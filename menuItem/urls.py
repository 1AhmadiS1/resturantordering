# pyrefly: ignore [missing-import]
from menuItem.views import MenuItemViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("menuitems", MenuItemViewSet, basename="menuitems")
urlpatterns = router.urls
