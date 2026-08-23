from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

@extend_schema_view(
    post=extend_schema(
        tags=["Authentication"],
        summary="Log in",
        description=(
            "Submit email and password to receive JWT access and refresh tokens. "
            "Use the access token in Swagger's Authorize button as: Bearer <token>."
        ),
    )
)


class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

@extend_schema_view(
    post=extend_schema(
        tags=["Authentication"],
        summary="Refresh an access token",
        description="Submit a valid refresh token to receive a new access token.",
    )
)

class ThrottledTokenRefreshView(TokenRefreshView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "token_refresh"