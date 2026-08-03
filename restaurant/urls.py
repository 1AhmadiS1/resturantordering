from django.urls import path
from .views import RestaurantView
from rest_framework.routers import DefaultRouter

router=DefaultRouter()
router.register('restaurants',RestaurantView,basename='restaurants')
urlpatterns=router.urls