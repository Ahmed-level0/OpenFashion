from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Product
from .serializers import ProductSerializer


class ProductListAPIView(ListAPIView):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer

class ProductDetailAPIView(RetrieveAPIView):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    lookup_field = 'id'
