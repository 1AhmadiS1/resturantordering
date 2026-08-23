from rest_framework.throttling import UserRateThrottle


class WriteScopedRateThrottle(UserRateThrottle):
    scope = "writes"

    def allow_request(self, request, view):
        if request.method in ["POST", "PATCH", "PUT", "DELETE"]:
            return super().allow_request(request, view)
        return True