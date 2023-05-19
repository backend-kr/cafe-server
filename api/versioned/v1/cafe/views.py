from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from api.bases.cafe.models import Cafe
from api.versioned.v1.cafe.serializers import CafeSerializer, PointSerializer
from common.viewsets import MappingViewSetMixin
from rest_framework import viewsets
from rest_framework import status
import math
import json
from django.core.cache import caches



def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # 지구의 반지름 (킬로미터)

    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    a = math.sin(dLat / 2) * math.sin(dLat / 2) + \
        math.sin(dLon / 2) * math.sin(dLon / 2) * math.cos(lat1) * math.cos(lat2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance

class CafeViewSet(MappingViewSetMixin,
                     viewsets.ModelViewSet):

    permission_classes = [AllowAny, ]
    queryset = Cafe.objects.all()
    lookup_field = 'title'
    serializer_class = CafeSerializer


class CafeNearbyViewSet(MappingViewSetMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    queryset = Cafe.objects.all()
    serializer_class = PointSerializer

    def nearby_cafes(self, request, *args, **kwargs):
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        if latitude is None or longitude is None:
            return Response({"error": "위도와 경도를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        latitude_rounded = round(float(latitude), 4)
        longitude_rounded = round(float(longitude), 4)

        user_location = (latitude_rounded, longitude_rounded)
        # 위도 경도를 하나의 그룹으로 캐싱
        nearby_cafes_json = caches['replica'].get(f'cafes_near_{user_location}')

        if nearby_cafes_json is None:
            queryset = list(Cafe.objects.all())
            nearby_cafes = []

            for cafe in queryset:
                cafe.distance = haversine(user_location[0], user_location[1], float(cafe.latitude), float(cafe.longitude))

                if cafe.distance <= 1:
                    serializer = CafeSerializer(cafe)
                    serialized_cafe = serializer.data
                    serialized_cafe['distance'] = cafe.distance
                    nearby_cafes.append(serialized_cafe)

            nearby_cafes.sort(key=lambda cafe: cafe['distance'])
            nearby_cafes_json = json.dumps(nearby_cafes)
            caches['default'].set(f'cafes_near_{user_location}', nearby_cafes_json)
        else:
            nearby_cafes = json.loads(nearby_cafes_json)

        for i, cafe in enumerate(nearby_cafes):
            cafe['distance'] = round(cafe['distance'] * 1000, 3)  # 킬로미터를 미터로 변환

        return Response(nearby_cafes, status=status.HTTP_200_OK)


class CafeSearchViewSet(MappingViewSetMixin,
                     viewsets.GenericViewSet):

    permission_classes = [AllowAny, ]
    queryset = Cafe.objects.all()
    serializer_class = PointSerializer

    def searh_cafes(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)
