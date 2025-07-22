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


from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from .serializers import PasswordResetConfirmSerializer

from .serializers import (PasswordChangeSerializer, PasswordResetSerializer,
                          UserRegistrationSerializer, UserProfileSerializer)

from .models import (User)

# Create your views here.

def uid_token(user:User) -> (str, str):

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    return token , uid
    
class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()

                token, uid = uid_token(user)
                    
                reset_link = request.build_absolute_uri(
                    reverse(
                        "confirm_email", 
                        kwargs= {
                            'uidb64': uid, 
                            'token':token
                            }
                        )
                    )

                user.email_user(
                    subject='Email Activation Request',
                    message=f'Hello, please use the following link to activate your account: {reset_link}',
                    from_email='noreply@yourapi.com',
                    fail_silently=False
                )
                    
                return Response({
                    "message": "User registered successfully.",
                    "user_id": user.id,
                    "email": user.email
                }, status=status.HTTP_201_CREATED)
            except:
                Response({"error":"Server Failure"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordChangeView(APIView):
    """
    An endpoint for changing password.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            # Check old password
            if not user.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            
            # set_password hashes the password
            user.set_password(serializer.data.get("new_password"))
            user.save()

            return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                
                # Generate token
                token, uid = uid_token(user)
                
                # Construct reset link
                reset_link = request.build_absolute_uri(
                    reverse(
                        "reset_password_confirm", 
                        kwargs= {
                            'uidb64': uid, 
                            'token':token
                            }
                        )
                    )
                
                # Send email
                send_mail(
                    subject='Password Reset Request',
                    message=f'Hello, please use the following link to reset your password: {reset_link}',
                    from_email='noreply@yourapi.com',
                    recipient_list=[email],
                    fail_silently=False
                )

                # Always return a success response to prevent user enumeration attacks
                return Response({"message": "If an account with this email exists, a password reset link has been sent."}, status=status.HTTP_200_OK)

            except User.DoesNotExist:
                # Still return a generic success message
                return Response({"message": "If an account with this email exists, a password reset link has been sent."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None

            if user is not None and default_token_generator.check_token(user, token):
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Reset link is invalid or has expired."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

class EmailVerification(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "Email has been verified successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Verification link is invalid or has expired."}, status=status.HTTP_400_BAD_REQUEST)

    