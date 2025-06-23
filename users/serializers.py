# In your_app/serializers.py

from django.contrib.auth import get_user_model
from rest_framework import serializers, validators

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    # We are writing this because we need to confirm password field in our Registratin Request
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password2']
        extra_kwargs = {
            'password': {
                'write_only': True, # Ensures password is not sent back in the response
                # 'validators': [validators.MinLengthValidator(8)] # Example validator
            }
        }

    def validate(self, attrs):
        """
        Check that the two password entries match.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        """
        Create and return a new `User` instance, given the validated data.
        """
        # We don't want to save password2 to the database
        validated_data.pop('password2')
        
        # Use the create_user method to handle password hashing
        user = User.objects.create_user(**validated_data)
        
        return user

class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password2 = serializers.CharField(required=True, style={'input_type': 'password'})

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({"new_password": "The two password fields didn't match."})
        return data

class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset e-mail.
    """
    email = serializers.EmailField(required=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming a password reset.
    """
    new_password = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({"new_password": "The two password fields didn't match."})
        return data

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile object.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'date_of_birth')
        read_only_fields = ('id', 'email')