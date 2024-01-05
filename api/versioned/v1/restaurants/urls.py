from common.routers import CustomSimpleRouter
from .views import RestaurantViewSet

router = CustomSimpleRouter(trailing_slash=False)
router.register('', RestaurantViewSet)

urlpatterns = [
]
urlpatterns += router.urls