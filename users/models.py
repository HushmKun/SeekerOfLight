from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from .managers import UserManager

# Create your models here.


class User(AbstractBaseUser, PermissionsMixin):
    """
    A custom User model for Django projects that uses email as the unique identifier.

    This model substitutes the default Django User model to enable authentication
    using an email address and password. It inherits from `AbstractBaseUser` for
    core user implementation and `PermissionsMixin` to handle permissions.

    The `UserManager` is responsible for object creation, providing helper methods
    like `create_user` and `create_superuser`.

    Key characteristics:
    - Authentication is managed via the `email` field.
    - `username` is not a field on this model.
    - `first_name` and `last_name` are nessecary.
    - `date_of_birth` and `phone_number` are optional.

    Attributes:
        email (EmailField): The user's unique email address. Serves as the USERNAME_FIELD.
        first_name (CharField): The user's first name.
        last_name (CharField): The user's last name.
        date_joined (DateTimeField): The timestamp when the user account was created.
        is_active (BooleanField): Designates whether the user can log in.
        is_staff (BooleanField): Designates whether the user can access the admin site.
        avatar (ImageField): An optional profile picture for the user.
        date_of_birth (DateField): The date when the user was born.
        phone_number (CharField): The user's phone number.
    """

    first_name = models.CharField(_("first name"), max_length=30)
    last_name = models.CharField(_("last name"), max_length=30)
    email = models.EmailField(_("email address"), unique=True)
    date_joined = models.DateTimeField(_("date joined"), auto_now_add=True)
    is_active = models.BooleanField(_("active"), default=False)
    is_staff = models.BooleanField(_("staff"), default=False)
    # avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    date_of_birth = models.DateField(_("date of birth"), null=True, blank=True)
    country = CountryField(null=True)
    # phone_number = models.CharField(_("phone number"), max_length=15, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "date_of_birth"]

    class Meta:
        db_table = "user"
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        # send_mail(subject, message, from_email, [self.email], **kwargs)
        print(message)
