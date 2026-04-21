from django.db import models
from django.conf import settings
from products.models import Product

# Create your models here.
class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name= 'cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user}"
    
    def get_total_price(self):
        """Sum of (price × quantity) for all items."""
        return sum([item.get_total_price() for item in self.items.all()])

    def get_total_quantity(self):
        """Total number of individual units in the cart."""
        return sum([item.quantity for item in self.items.all()])

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.IntegerField(default=1)


    def __str__(self):
        return f"{self.cart} - {self.product}"

    def get_total_price(self):
        return self.product.price * self.quantity