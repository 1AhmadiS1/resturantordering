from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user.permissions import ChangePasswordPermission
from user.serializer import ChangePasswordResponseSerializer, ChangePasswordSerializer
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from user.models import User
from user.permissions import RolePermission
from user.serializer import ResetUserPasswordSerializer, UserCreateSerializer, UserSerializer

@extend_schema_view(
    list=extend_schema(
        tags=["Users"],
        summary="List manageable users",
        description=(
            "Platform admins see all users. Owners see only waiters and chefs assigned "
            "to their restaurants."
        ),
    ),
    retrieve=extend_schema(
        tags=["Users"],
        summary="Get a user",
        description="Return one user that the authenticated admin or owner is allowed to manage.",
    ),
    create=extend_schema(
        tags=["Users"],
        summary="Create a user",
        description=(
            "Platform admins may create any role. Owners may create only waiter or chef "
            "accounts assigned to one of their own restaurants."
        ),
        responses={201: UserSerializer},
    ),
    update=extend_schema(
        tags=["Users"],
        summary="Replace a user",
        description="Passwords cannot be changed here; use the change-password endpoint.",
    ),
    partial_update=extend_schema(
        tags=["Users"],
        summary="Update a user",
        description=(
            "Update allowed profile, role, or restaurant fields. Owner scope is enforced "
            "again after the update values are combined with the existing user."
        ),
    ),
    destroy=extend_schema(
        tags=["Users"],
        summary="Delete a user",
        description="Owners may delete only their own waiter or chef accounts; platform admins may delete any user.",
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, RolePermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["role", "restaurant"]
    search_fields = ["email", "first_name", "last_name"]
    ordering_fields = ["id", "email", "role"]
    ordering = ["role"]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action == "reset_password":
            return ResetUserPasswordSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user

        if user.role == User.RoleChoices.PLATFORM_ADMIN:
            return User.objects.select_related("restaurant").all().order_by("role")

        if user.role == User.RoleChoices.OWNER:
            return User.objects.select_related("restaurant").filter(
                restaurant__owner=user,
                role__in=[User.RoleChoices.WAITER, User.RoleChoices.CHEF],
            ).order_by("role")
        return User.objects.none()

    @extend_schema(
        tags=["Users"],
        summary="Reset a user's password",
        description=(
            "Platform admins may reset any user's password. Owners may reset passwords "
            "only for waiter or chef accounts assigned to their own restaurant."
        ),
        request=ResetUserPasswordSerializer,
        responses={200: ChangePasswordResponseSerializer},
    )
    @action(detail=True, methods=["post"], url_path="reset-password")
    def reset_password(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(
            instance=user,
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password reset successfully."},
            status=status.HTTP_200_OK,
        )

@extend_schema(
    tags=["Authentication"],
    summary="Change your password",
    description=(
        "Change the authenticated user's password after verifying the old password. "
        "All roles may change their own password."
    ),
    request=ChangePasswordSerializer,
    responses={200: ChangePasswordResponseSerializer},
)

class ChangePasswordView(APIView):
    serializer_class = ChangePasswordSerializer
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


@extend_schema(
    tags=["Authentication"],
    summary="Get the current user",
    description=(
        "Return the authenticated user's profile. Frontend clients use this endpoint "
        "after login to load the user's role and restaurant assignment."
    ),
    responses={200: UserSerializer},
)
class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

        
            
        
