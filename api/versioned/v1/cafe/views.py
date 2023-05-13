from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from api.bases.cafe.models import Cafe
from api.versioned.v1.cafe.serializers import CafeSerializer, PointSerializer
from common.viewsets import MappingViewSetMixin
from rest_framework import viewsets
from rest_framework import status
import math

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
    serializer_class = CafeSerializer



class CafeNearbyViewSet(MappingViewSetMixin,
                     viewsets.GenericViewSet):

    permission_classes = [AllowAny, ]
    queryset = Cafe.objects.all()
    serializer_class = PointSerializer

    def nearby_cafes(self, request, *args, **kwargs):
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        if latitude is None or longitude is None:
            return Response({"error": "위도와 경도를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        user_location = (float(latitude), float(longitude))
        queryset = list(Cafe.objects.all())
        nearby_cafes = []

        for cafe in queryset:
            cafe.distance = haversine(user_location[0], user_location[1], float(cafe.latitude), float(cafe.longitude))

            if cafe.distance <= 1:  # 5km 이내인 경우에만 추가
                nearby_cafes.append(cafe)

        nearby_cafes.sort(key=lambda cafe: cafe.distance)

        serializer = CafeSerializer(nearby_cafes, many=True)
        serialized_data = serializer.data

        for i, cafe in enumerate(nearby_cafes):
            serialized_data[i]['distance'] = round(cafe.distance * 1000, 3) # 킬로미터를 미터로 변환

        return Response(serializer.data, status=status.HTTP_200_OK)
