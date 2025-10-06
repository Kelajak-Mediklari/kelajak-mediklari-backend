from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .api_endpoints import auth, profile, dashboard

app_name = "users"


urlpatterns = [
    path("login/", auth.LoginView.as_view(), name="auth-login"),
    path("register/", auth.RegisterView.as_view(), name="auth-register"),
    path(
        "send-auth-verification-code/",
        auth.SendAuthVerificationCodeView.as_view(),
        name="auth-send-auth-verification-code",
    ),
    path(
        "send-forget-password-code/",
        auth.SendForgetPasswordCodeView.as_view(),
        name="auth-send-forget-password-code",
    ),
    path(
        "forget-password/",
        auth.ForgetPasswordView.as_view(),
        name="auth-forget-password",
    ),
    path("check-phone/", auth.CheckPhoneView.as_view(), name="auth-check-phone"),
    path("token-obtain-pair/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token-refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", profile.ProfileGetView.as_view(), name="profile-get"),
    path("profile/update/", profile.ProfileUpdateView.as_view(), name="profile-update"),
    path(
        "profile/send-code-change-phone/",
        profile.SendCodeForChangePhoneView.as_view(),
        name="profile-send-code-change-phone",
    ),
    path(
        "profile/change-phone/",
        profile.UserChangePhoneAPIView.as_view(),
        name="profile-change-phone",
    ),
    path("dashboard/", dashboard.UserDashboardView.as_view(), name="user-dashboard"),
]
