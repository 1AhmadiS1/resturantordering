from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import TableView

router=DefaultRouter()
router.register("tables",TableView, basename="tables")
urlpatterns=router.urls