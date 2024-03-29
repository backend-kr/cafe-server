from django.urls import path, re_path, include
from common.routers import CustomSimpleRouter
from .views import CafeViewSet, CafeNearbyViewSet

router = CustomSimpleRouter(trailing_slash=False)
router.register('', CafeViewSet)

urlpatterns = [
    path('nearby', CafeNearbyViewSet.as_view({'post': 'nearby_cafes'})),
    path('search', CafeNearbyViewSet.as_view({'post': 'nearby_cafes'})),
]
urlpatterns += router.urls