# In your_app/serializers.py

from django.contrib.auth import get_user_model
from rest_framework import serializers
from django_countries.serializer_fields import CountryField

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    # We are writing this because we need to confirm password field in our Registratin Request
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "password2", "first_name", "last_name"]
        extra_kwargs = {
            "password": {
                "write_only": True,  # Ensures password is not sent back in the response
                # 'validators': [validators.MinLengthValidator(8)] # Example validator
            }
        }

    def validate(self, attrs):
        """
        Check that the two password entries match.
        """
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        """
        Create and return a new `User` instance, given the validated data.
        """
        validated_data.pop("password2")

        # Use the create_user method to handle password hashing
        user = User.objects.create_user(**validated_data)

        return user


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """

    old_password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )
    new_password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )
    new_password2 = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        return value

    def validate(self, data):
        if data["new_password"] != data["new_password2"]:
            raise serializers.ValidationError(
                {"new_password": "The two password fields didn't match."}
            )
        return data
    
    def update(self, instance, validated_data):
        # The 'instance' here is the user object provided by the view's get_object() method.
        
        # 1. Check the old password
        if not instance.check_password(validated_data.get("old_password")):
            # Raising a ValidationError will be automatically handled by DRF 
            # and result in a 400 Bad Request response.
            raise serializers.ValidationError({"old_password": "Wrong password."})

        # 2. Set the new password
        # The set_password method handles hashing.
        instance.set_password(validated_data.get("new_password"))
        instance.save()
        
        return instance


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset e-mail.
    """

    email = serializers.EmailField(required=True)

    def save(self):
        # The 'validated_data' is available here after '.is_valid()' is called.
        email = self.validated_data['email']
        
        # The 'request' is passed from the view to the serializer's context.
        request = self.context.get('request')

        try:
            user = User.objects.get(email=email)

            token, uid = uid_token(user)

            reset_link = request.build_absolute_uri(
                reverse("reset_password_confirm", kwargs={"uidb64": uid, "token": token})
            )

            user.send_mail(
                subject="Password Reset Request",
                message=f"Hello, please use the following link to reset your password: {reset_link}",
                fail_silently=False,
            )
        except User.DoesNotExist:
            pass


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming a password reset.
    """

    new_password = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

    def validate_new_password(self, value):
        if len(value) < 8 : 
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        return value

    def validate(self, data):
        if data["new_password"] != data["new_password2"]:
            raise serializers.ValidationError(
                {"new_password": "The two password fields didn't match."}
            )
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile object.
    """

    country = CountryField()

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "date_of_birth", "country")
        read_only_fields = ("id", "email")


class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        return data
