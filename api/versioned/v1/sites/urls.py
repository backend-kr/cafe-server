from django.urls import path, re_path, include
from .views import SitesViewSet

urlpatterns = [
    re_path('category', SitesViewSet.as_view({'get': 'list'}))
]

