from .models import Cart, CartItem
from .permissions import IsOwnerOrReadOnly
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.db import transaction
from orders.models import Order, OrderItem

class CartViewset(ModelViewSet):
    """
    A viewset for viewing and editing cart instances.
    """
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated ,IsOwnerOrReadOnly]
    
    def get_queryset(self):
        (cart, created) = Cart.objects.get_or_create(user=self.request.user)
        return Cart.objects.filter(id=cart.id)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        user = self.request.user        
        user_id = self.request.user.id

        (cart, created) = Cart.objects.get_or_create(user_id=user_id)
        product = get_object_or_404(Product, id=request.data.get('product_id'))

        if request.data['quantity'] <= 0:
            return Response({'error': 'Quantity must be greater than 0'}, status=status.HTTP_400_BAD_REQUEST)

        if CartItem.objects.filter(cart=cart, product=product).exists():
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.quantity += request.data['quantity']
            cart_item.save()
            return Response(CartItemSerializer(cart_item).data)
    
        cart_item = CartItem.objects.create(cart=cart, product=product, quantity=request.data['quantity'])
        return Response(CartItemSerializer(cart_item).data) 
    
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        user = self.request.user        
        user_id = self.request.user.id

        (cart, created) = Cart.objects.get_or_create(user_id=user_id)

        try:
            cart_item = CartItem.objects.get(cart=cart, product=request.data['product_id'])
            cart_item.delete()
            return Response({'message': 'Item removed successfully'}, status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def update_item(self, request):
        user = self.request.user
        user_id = self.request.user.id

        (cart, created) = Cart.objects.get_or_create(user_id=user_id)
        product = get_object_or_404(Product, id=request.data.get('product_id'))

        if request.data['quantity'] <= 0:
            return Response({'error': 'Quantity must be greater than 0'}, status=status.HTTP_400_BAD_REQUEST)

        if CartItem.objects.filter(cart=cart, product=product).exists():
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.quantity = request.data['quantity']
            cart_item.save()
            return Response(CartItemSerializer(cart_item).data)
        else:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
        
            
    # Safe checkout
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        user = self.request.user
        user_id = self.request.user.id

        (cart, created) = Cart.objects.get_or_create(user_id=user_id)

        if cart.items.count() == 0:
            return Response({"error": "Cart is empty"}, status=400)

        phone = request.data.get('phone')
        address = request.data.get('address')
        # payment_method = request.data.get('payment_method', 'online')

        if not phone or not address:
            return Response({"error": "Phone and address required"}, status=400)

        # shipping_fee = 50 if city in ['cairo', 'giza'] else 80
        # cod_fee = float(cart.total_price) * 0.10 if payment_method == 'cod' else 0

        # Compute discount safely
        # discount_amount = 0
        # if cart.coupon and cart.coupon.is_valid:
        #     items_total = sum(item.total_price for item in cart.items.select_related('product'))
        #     if cart.coupon.discount_type == 'percentage':
        #         discount_amount = items_total * cart.coupon.discount / 100
        #     else:
        #         discount_amount = min(cart.coupon.discount, items_total)

        # Start atomic transaction for order creation & stock deduction
        with transaction.atomic():
            # Lock all products involved to prevent race conditions
            products = Product.objects.filter(id__in=cart.items.values_list('product_id', flat=True)).select_for_update()

            # Verify stock
            for item in cart.items.select_related('product'):
                if item.quantity > item.product.stock:
                    return Response(
                        {"error": f"Not enough stock for {item.product.name}. Only {item.product.stock} left"},
                        status=409
                    )

            # Create order
            order = Order.objects.create(
                user=request.user,
                total_price=float(cart.get_total_price()),
                total_quantity=cart.get_total_quantity(),
                # shipping_fee=shipping_fee,
                # coupon=cart.coupon,
                # discount_amount=discount_amount,
                phone=phone,
                address=address,
                status='pending'
            )

            # Create order items
            for item in cart.items.select_related('product'):
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            # Deduct stock immediately for COD
            # if order.status == 'cod':
            #     for item in order.items.select_related('product'):
            #         item.product.stock = F('stock') - item.quantity
            #         item.product.save()

            # Update coupon usage count safely
            # if cart.coupon:
            #     coupon = Coupon.objects.select_for_update().get(id=cart.coupon.id)
            #     coupon.usage_count = F('usage_count') + 1
            #     coupon.save()

            cart.items.all().delete()
            cart.save()

        message = "Order created. Payment required." if order.status == 'pending' else "Order placed successfully"
        return Response({
            "order_id": order.id,
            "message": message,
            "status": order.status
        }, status=201)