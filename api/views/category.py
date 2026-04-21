from rest_framework import mixins, viewsets

from api.models import Category
from api.serializers import CategorySerializer


class CategoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Category.objects.all().order_by("created_at")
    serializer_class = CategorySerializer
