from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProductViewset
from cart.views import CartViewset

router = DefaultRouter()
router.register(r'products', ProductViewset, basename='product')
router.register(r'cart', CartViewset, basename='cart')

urlpatterns = router.urls