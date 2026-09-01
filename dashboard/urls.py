from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import DashboardView

urlpatterns=[
    path('dashboard/',DashboardView.as_view(),name='dashboard')
]