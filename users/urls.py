from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    EmailVerification,
    PasswordChangeView,
    UserRegistrationView,
    PasswordResetView,
    PasswordResetConfirmView,
    UserProfileView,
)


def empty():
    pass


urlpatterns = [
    path("register/", view=UserRegistrationView.as_view(), name="register"),
    path(
        "confirm_email/<uidb64>/<token>/",
        view=EmailVerification.as_view(),
        name="confirm_email",
    ),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("change_password/", view=PasswordChangeView.as_view(), name="change_password"),
    path("reset_password/", view=PasswordResetView.as_view(), name="reset_password"),
    path(
        "reset_password/confirm/<uidb64>/<token>",
        view=PasswordResetConfirmView.as_view(),
        name="reset_password_confirm",
    ),
    path("current_user/", view=UserProfileView.as_view(), name="profile"),
]
