
# pyrefly: ignore [missing-import]
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import MenuModelViewSet

router=DefaultRouter()
router.register('menu',MenuModelViewSet,basename='menu')

urlpatterns=router.urls


