from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from api.bases.restaurants.models import Restaurant
from api.versioned.v1.restaurants.serializers import RestaurantSerializer, RestaurantCreateSerializer
from common.viewsets import MappingViewSetMixin
from rest_framework import viewsets
from rest_framework import status


class RestaurantViewSet(MappingViewSetMixin,
                     viewsets.ModelViewSet):

    permission_classes = [AllowAny, ]
    queryset = Restaurant.objects.all()
    lookup_field = 'title'
    serializer_action_map = {
        "create": RestaurantCreateSerializer
    }
    serializer_class = RestaurantSerializer
    def create(self, request, *args, **kwargs):
        created_cafes_count = 0
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'created': created_cafes_count}, status=status.HTTP_201_CREATED)