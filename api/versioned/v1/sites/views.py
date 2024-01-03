from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.bases.cafe.models import Cafe
from api.versioned.v1.cafe.filters import SiteFilterSet
from api.versioned.v1.cafe.serializers import CafeSerializer
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
        '1': None,
        '2': None
    }
    serializer_class = CafeSerializer
    def list(self, request, *args, **kwargs):
        query_params = request.query_params
        filter_value = query_params.get('category', None)
        queryset = self.queryset_map.get(filter_value)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
