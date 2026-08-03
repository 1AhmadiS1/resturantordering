from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from user.models import User
from user.permissions import RolePermission
from user.serializer import UserSerializer

@extend_schema_view(
    list=extend_schema(tags=['Users']),
    retrieve=extend_schema(tags=['Users'])
    ,create=extend_schema(tags=['Users'])
    ,update=extend_schema(tags=['Users'])
    ,partial_update=extend_schema(tags=['Users'])
    ,destroy=extend_schema(tags=['Users'])
)
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, RolePermission]

    def get_queryset(self):
        user = self.request.user

        if user.role == User.RoleChoices.PLATFORM_ADMIN:
            return User.objects.all()

        if user.role == User.RoleChoices.OWNER:
            return User.objects.filter(role__in=[
                User.RoleChoices.OWNER,
                User.RoleChoices.WAITER,
                User.RoleChoices.CHEF,
            ])

        return User.objects.none()
