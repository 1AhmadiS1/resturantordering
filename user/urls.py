from django.urls import path
from rest_framework.routers import DefaultRouter

from user.views import UserViewSet,ChangePasswordView


router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
urlpatterns=[
    path("change-password/",ChangePasswordView.as_view(),name="change-password")
]
urlpatterns += router.urls
