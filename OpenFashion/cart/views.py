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
    
    def check_out(self, request):
        user = self.request.user
        user_id = self.request.user.id

        (cart, created) = Cart.objects.get_or_create(user_id=user_id)
        
            
