from .models import Product
from .serializers import ProductSerializer
from rest_framework.viewsets import ModelViewSet
from .permissions import IsAdminOrReadOnly

class ProductViewset(ModelViewSet):
    """
    A viewset for viewing and editing product instances.
    """
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Product.objects.select_related('category').all()

    