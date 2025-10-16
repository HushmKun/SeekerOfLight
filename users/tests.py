from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch
from datetime import date

User = get_user_model()


class UserRegistrationViewTests(APITestCase):
    """Test suite for UserRegistrationView"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.valid_payload = {
            'email': 'testuser@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }

    @patch('users.models.User.email_user')
    def test_successful_registration(self, mock_email):
        """Test successful user registration"""
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user_id', response.data)
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'], self.valid_payload['email'])
        
        # Verify user was created
        user = User.objects.get(email=self.valid_payload['email'])
        self.assertIsNotNone(user)
        self.assertFalse(user.is_active)  # User should not be active until email is verified
        
        # Verify email was sent
        mock_email.assert_called_once()

    def test_registration_with_mismatched_passwords(self):
        """Test registration fails with mismatched passwords"""
        invalid_payload = self.valid_payload.copy()
        invalid_payload['password2'] = 'differentpass'
        
        response = self.client.post(self.register_url, invalid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_with_existing_email(self):
        """Test registration fails with already registered email"""
        # Create a user first
        User.objects.create_user(
            email=self.valid_payload['email'],
            password=self.valid_payload['password'],
            first_name='Existing',
            last_name='User'
        )
        
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_with_missing_fields(self):
        """Test registration fails with missing required fields"""
        invalid_payload = {'email': 'test@example.com'}
        
        response = self.client.post(self.register_url, invalid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('users.models.User.email_user', side_effect=Exception('Email service error'))
    def test_registration_email_failure(self, mock_email):
        """Test registration handles email sending failure gracefully"""
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)


class EmailVerificationViewTests(APITestCase):
    """Test suite for EmailVerification view"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.user.is_active = False
        self.user.save()
        
        self.token = default_token_generator.make_token(self.user)
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))

    def test_successful_email_verification(self):
        """Test successful email verification"""
        url = reverse('confirm_email', kwargs={'uidb64': self.uid, 'token': self.token})
        response = self.client.post(url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Verify user is now active
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_email_verification_with_invalid_token(self):
        """Test email verification fails with invalid token"""
        url = reverse('confirm_email', kwargs={'uidb64': self.uid, 'token': 'invalid-token'})
        response = self.client.post(url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
        # Verify user is still inactive
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_email_verification_with_invalid_uid(self):
        """Test email verification fails with invalid UID"""
        url = reverse('confirm_email', kwargs={'uidb64': 'invalid-uid', 'token': self.token})
        response = self.client.post(url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class LoginViewTests(APITestCase):
    """Test suite for LoginView (JWT token obtain)"""

    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('token_obtain_pair')
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.user.is_active = True
        self.user.save()

    def test_successful_login(self):
        """Test successful login with valid credentials"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_invalid_credentials(self):
        """Test login fails with invalid credentials"""
        payload = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_inactive_user(self):
        """Test login fails with inactive user"""
        self.user.is_active = False
        self.user.save()
        
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_nonexistent_user(self):
        """Test login fails with nonexistent user"""
        payload = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RefreshViewTests(APITestCase):
    """Test suite for RefreshView (JWT token refresh)"""

    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.user.is_active = True
        self.user.save()
        
        # Get tokens
        login_response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'testpass123'
        }, format='json')
        self.refresh_token = login_response.data['refresh']

    def test_successful_token_refresh(self):
        """Test successful token refresh"""
        payload = {'refresh': self.refresh_token}
        response = self.client.post(self.refresh_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_refresh_with_invalid_token(self):
        """Test token refresh fails with invalid token"""
        payload = {'refresh': 'invalid-token'}
        response = self.client.post(self.refresh_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PasswordChangeViewTests(APITestCase):
    """Test suite for PasswordChangeView"""

    def setUp(self):
        self.client = APIClient()
        self.password_change_url = reverse('change_password')
        self.user = User.objects.create_user(
            email='test@example.com',
            password='oldpassword123',
            first_name='Test',
            last_name='User'
        )
        self.user.is_active = True
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def test_successful_password_change(self):
        """Test successful password change"""
        payload = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'new_password2': 'newpassword123'
        }
        response = self.client.put(self.password_change_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_password_change_with_wrong_old_password(self):
        """Test password change fails with wrong old password"""
        payload = {
            'old_password': 'wrongpassword',
            'new_password': 'newpassword123',
            'new_password2': 'newpassword123'
        }
        response = self.client.put(self.password_change_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_change_with_mismatched_new_passwords(self):
        """Test password change fails with mismatched new passwords"""
        payload = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'new_password2': 'differentpassword'
        }
        response = self.client.put(self.password_change_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_change_with_short_password(self):
        """Test password change fails with password less than 8 characters"""
        payload = {
            'old_password': 'oldpassword123',
            'new_password': 'short',
            'new_password2': 'short'
        }
        response = self.client.put(self.password_change_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_change_requires_authentication(self):
        """Test password change requires authentication"""
        self.client.force_authenticate(user=None)
        payload = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'new_password2': 'newpassword123'
        }
        response = self.client.put(self.password_change_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PasswordResetViewTests(APITestCase):
    """Test suite for PasswordResetView"""

    def setUp(self):
        self.client = APIClient()
        self.password_reset_url = reverse('reset_password')
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.user.is_active = True
        self.user.save()

    @patch('users.models.User.email_user')
    def test_successful_password_reset_request(self, mock_email_user):
        """Test successful password reset request"""
        payload = {'email': 'test@example.com'}
        response = self.client.post(self.password_reset_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        # Verify email was sent
        mock_email_user.assert_called_once()

    def test_password_reset_with_nonexistent_email(self):
        """Test password reset with nonexistent email (should still return success)"""
        payload = {'email': 'nonexistent@example.com'}
        response = self.client.post(self.password_reset_url, payload, format='json')
        
        # Should return success for security reasons (don't reveal if email exists)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_password_reset_with_invalid_email(self):
        """Test password reset with invalid email format"""
        payload = {'email': 'invalid-email'}
        response = self.client.post(self.password_reset_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmViewTests(APITestCase):
    """Test suite for PasswordResetConfirmView"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='oldpassword123',
            first_name='Test',
            last_name='User'
        )
        self.user.is_active = True
        self.user.save()
        
        self.token = default_token_generator.make_token(self.user)
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))

    def test_successful_password_reset_confirm(self):
        """Test successful password reset confirmation"""
        url = reverse('reset_password_confirm', kwargs={'uidb64': self.uid, 'token': self.token})
        payload = {
            'new_password': 'newpassword123',
            'new_password2': 'newpassword123'
        }
        response = self.client.post(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_password_reset_confirm_with_invalid_token(self):
        """Test password reset confirmation fails with invalid token"""
        url = reverse('reset_password_confirm', kwargs={'uidb64': self.uid, 'token': 'invalid-token'})
        payload = {
            'new_password': 'newpassword123',
            'new_password2': 'newpassword123'
        }
        response = self.client.post(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_password_reset_confirm_with_mismatched_passwords(self):
        """Test password reset confirmation fails with mismatched passwords"""
        url = reverse('reset_password_confirm', kwargs={'uidb64': self.uid, 'token': self.token})
        payload = {
            'new_password': 'newpassword123',
            'new_password2': 'differentpassword'
        }
        response = self.client.post(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_with_short_password(self):
        """Test password reset confirmation fails with short password"""
        url = reverse('reset_password_confirm', kwargs={'uidb64': self.uid, 'token': self.token})
        payload = {
            'new_password': 'short',
            'new_password2': 'short'
        }
        response = self.client.post(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_with_invalid_uid(self):
        """Test password reset confirmation fails with invalid UID"""
        url = reverse('reset_password_confirm', kwargs={'uidb64': 'invalid-uid', 'token': self.token})
        payload = {
            'new_password': 'newpassword123',
            'new_password2': 'newpassword123'
        }
        response = self.client.post(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class UserProfileViewTests(APITestCase):
    """Test suite for UserProfileView"""

    def setUp(self):
        self.client = APIClient()
        self.profile_url = reverse('profile')
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            date_of_birth=date(1990, 1, 1)
        )
        self.user.is_active = True
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def test_get_user_profile(self):
        """Test retrieving user profile"""
        response = self.client.get(self.profile_url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['first_name'], 'Test')
        self.assertEqual(response.data['last_name'], 'User')
        self.assertIn('date_of_birth', response.data)

    def test_update_user_profile(self):
        """Test updating user profile"""
        payload = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'date_of_birth': '1995-05-15',
            'country': 'US'
        }
        response = self.client.put(self.profile_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify profile was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
        self.assertEqual(str(self.user.country), 'US')

    def test_partial_update_user_profile(self):
        """Test partially updating user profile"""
        payload = {'first_name': 'PartialUpdate'}
        response = self.client.patch(self.profile_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify only first_name was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'PartialUpdate')
        self.assertEqual(self.user.last_name, 'User')  # Should remain unchanged

    def test_user_profile_requires_authentication(self):
        """Test user profile requires authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.profile_url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_email_field_is_read_only(self):
        """Test that email field cannot be updated"""
        payload = {
            'email': 'newemail@example.com',
            'first_name': 'Test'
        }
        response = self.client.put(self.profile_url, payload, format='json')
        
        # Should succeed but email should not be changed
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'test@example.com')  # Should remain unchanged
