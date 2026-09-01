"""
URL configuration for resturantorderingapi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from user.token_views import ThrottledTokenObtainPairView, ThrottledTokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from drf_spectacular.utils import extend_schema, extend_schema_view



urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema"
        ),
    ),
    path("api/token/",ThrottledTokenObtainPairView.as_view(), name="login"),
    path("api/token/refresh/", ThrottledTokenRefreshView.as_view(), name="refresh"),
    path("api/", include("user.urls")),
    path("api/", include("restaurant.urls")),
    path("api/", include("menu.urls")),
    path("api/", include("menuItem.urls")),
    path("api/", include("table.urls")),
    path("api/", include("order.urls")),
    path("api/", include("dashboard.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
