from rest_framework.throttling import UserRateThrottle


class CustomUserThrottle(UserRateThrottle):
    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            return

        return self.cache_format % {"scope": self.scope, "ident": ident}
