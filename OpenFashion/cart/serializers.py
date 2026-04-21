from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import Cart, CartItem
from products.serializers import ProductSerializer
from products.models import Product


class CartItemSerializer(ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True        # for creating/updating cart items
    )
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.get_total_price()


class CartSerializer(ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'created_at', 'items', 'total_price', 'total_quantity']

    def get_total_price(self, obj):
        return obj.get_total_price()
    
    def get_total_quantity(self, obj):
        return obj.get_total_quantity()