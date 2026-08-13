from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user.permissions import ChangePasswordPermission
from user.serializer import ChangePasswordSerializer
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
            return User.objects.filter(restaurant__owner=user).exclude(role=User.RoleChoices.OWNER).exclude(role=User.RoleChoices.PLATFORM_ADMIN)
        return User.objects.none()

@extend_schema(
  tags=["Users"]

)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated,ChangePasswordPermission]
    def put(self,request):
        serializer=ChangePasswordSerializer(
            instance=request.user,
            data=request.data,
            context={"request":request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail":"Password changed successfully."},
            status=status.HTTP_200_OK,
        )

        
            
        
