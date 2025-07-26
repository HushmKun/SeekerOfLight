from django.urls import path

from .views import (
    EmailVerification,
    PasswordChangeView,
    UserRegistrationView,
    PasswordResetView,
    PasswordResetConfirmView,
    UserProfileView,
    LoginView,
    RefreshView
)

urlpatterns = [
    path("register/", view=UserRegistrationView.as_view(), name="register"),
    path(
        "confirm_email/<str:uidb64>/<str:token>/",
        view=EmailVerification.as_view(),
        name="confirm_email",
    ),
    path("login/", LoginView.as_view(), name="token_obtain_pair"),
    path("refresh/", RefreshView.as_view(), name="token_refresh"),
    path("change_password/", view=PasswordChangeView.as_view(), name="change_password"),
    path("reset_password/", view=PasswordResetView.as_view(), name="reset_password"),
    path(
        "reset_password/confirm/<str:uidb64>/<str:token>",
        view=PasswordResetConfirmView.as_view(),
        name="reset_password_confirm",
    ),
    path("profile/", view=UserProfileView.as_view(), name="profile"),
]
