from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.bases.cafe.models import Cafe
from api.bases.restaurants.models import Restaurant
from api.versioned.v1.cafe.filters import SiteFilterSet
from api.versioned.v1.cafe.serializers import CafeSerializer
from api.versioned.v1.restaurants.serializers import RestaurantSerializer
from common.filters import MappingDjangoFilterBackend
from common.viewsets import MappingViewSetMixin
from rest_framework import viewsets

class SitesViewSet(MappingViewSetMixin,
                  viewsets.GenericViewSet,
                   MappingDjangoFilterBackend):

    filterset_class = SiteFilterSet
    permission_classes = [AllowAny, ]
    queryset_map = {
        '0': Cafe.objects.all(),
        '1': Restaurant.objects.all(),
        '2': None
    }
    serializer_class = CafeSerializer
    serializer_map = {
        '0': CafeSerializer,
        '1': RestaurantSerializer,
        '2': None
    }
    def list(self, request, *args, **kwargs):
        query_params = request.query_params
        filter_value = query_params.get('category', "0")
        queryset = self.queryset_map.get(filter_value)
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)

        serializer = self.serializer_map.get(filter_value)
        serializer = serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
