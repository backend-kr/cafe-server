from django.urls import path, re_path, include
from common.routers import CustomSimpleRouter
from .views import CafeViewSet, CafeNearbyViewSet, CafeSearchViewSet

router = CustomSimpleRouter(trailing_slash=False)
router.register(r'', CafeViewSet)

urlpatterns = [
    path('nearby/', CafeNearbyViewSet.as_view({'post': 'nearby_cafes'})),
    path('search/', CafeSearchViewSet.as_view({'post': 'searh_cafes'})),
]
urlpatterns += router.urls