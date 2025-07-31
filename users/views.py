from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.generics import (
    CreateAPIView, 
    UpdateAPIView,
    GenericAPIView
)

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from .serializers import EmailVerificationSerializer, PasswordResetConfirmSerializer

from .serializers import (
    PasswordChangeSerializer,
    PasswordResetSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
)

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import User

# Create your views here.


def uid_token(user: User) -> (str, str):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    return token, uid


class UserRegistrationView(CreateAPIView):
    """
    User registration view using CreateAPIView for conciseness.
    """
    # The queryset is often used for list views, but it's good practice
    # to include it for schema generation and other DRF features.
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        """
        Override the default create method to add custom logic:
        1.  Validate data.
        2.  Save the new user instance.
        3.  Send a confirmation email.
        4.  Return a custom success response.
        """
        serializer = self.get_serializer(data=request.data) # basedpyright: ignore

        # Let DRF's exception handling manage the 400 Bad Request response
        serializer.is_valid(raise_exception=True) 

        try:
            # The .save() method will now trigger the serializer's .create() method
            user = serializer.save()

            # --- Your custom logic begins here ---
            token, uid = uid_token(user)
            confirm_link = request.build_absolute_uri(
                reverse("confirm_email", kwargs={"uidb64": uid, "token": token})
            )

            user.email_user(
                subject="Email Activation Request",
                message=f"Hello, please use the following link to activate your account: {confirm_link}",
                fail_silently=False,
            )
            # --- Your custom logic ends here ---

            # Return your custom success response
            return Response(
                {
                    "message": "User registered successfully. Please check your email to activate your account.",
                    "email": user.email,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            print(e)
            # You should ideally log the exception `e` here
            # Note: Your original code had a bug here (no return statement).
            return Response(
                {"error": "A server error occurred, could not send confirmation email."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PasswordChangeView(UpdateAPIView):
    """
    An endpoint for changing password.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = PasswordChangeSerializer

    def get_object(self):
        """
        Overrides the default get_object() to return the current user.
        """
        return self.request.user

    def update(self, request, *args, **kwargs):
        """
        Overrides the default update method to provide a custom success message.
        """
        # The parent class's update method will perform the validation and save.
        # It calls get_object() and uses the serializer_class.
        super().update(request, *args, **kwargs)
        
        return Response(
            {"message": "Password changed successfully."},
            status=status.HTTP_200_OK
        )


class PasswordResetView(GenericAPIView):
    """
    An endpoint for initiating a password reset.
    """
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        # We pass the request to the serializer's context to build the reset link.
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # The '.save()' method now contains our email-sending logic.
        serializer.save()

        # The security principle of always returning a success message is maintained.
        return Response(
            {"message": "If an account with this email exists, a password reset link has been sent."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(GenericAPIView):
    """
    View for confirming a password reset.
    """
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, uidb64, token, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response(
                {"message": "Password has been reset successfully."},
                status=status.HTTP_200_OK,
            )
        
        return Response(
            {"error": "Reset link is invalid or has expired."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserProfileView(RetrieveUpdateAPIView):
    """
    An endpoint for the user to view and update their profile.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        """
        This method returns the user object that is associated with the current request.
        """
        return self.request.user


class EmailVerification(GenericAPIView):
    serializer_class = EmailVerificationSerializer

    def post(self, request, uidb64:str, token:str):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response(
                {"message": "Email has been verified successfully."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Verification link is invalid or has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LoginView(TokenObtainPairView):
    pass 


class RefreshView(TokenRefreshView):
    pass 
