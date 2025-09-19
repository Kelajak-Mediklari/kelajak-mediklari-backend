import random
import time

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from apps.common.models import BaseModel
from apps.users.managers import SoftDeleteUserManager


class User(AbstractUser, BaseModel):
    class Gender(models.TextChoices):
        MALE = "MALE", _("Male")
        FEMALE = "FEMALE", _("Female")

    full_name = models.CharField(
        verbose_name=_("Full name"), max_length=255, null=True, blank=True
    )
    username = models.CharField(
        _("Username"), max_length=150, unique=True, null=True, blank=True
    )
    password = models.CharField(_("Password"), max_length=128, null=True, blank=True)
    email = models.EmailField(_("Email"), unique=True, null=True, blank=True)
    phone = PhoneNumberField(unique=True, verbose_name=_("Phone"))
    avatar = models.ImageField(
        verbose_name=_("Avatar"), upload_to="users/%Y/%m/", blank=True, null=True
    )
    grade = models.CharField(_("Grade"), max_length=255, null=True, blank=True)
    birth_date = models.DateField(_("Birth date"), null=True, blank=True)
    region = models.ForeignKey(
        "common.Region",
        on_delete=models.SET_NULL,
        verbose_name=_("Region"),
        null=True,
        blank=True,
    )
    district = models.ForeignKey(
        "common.District",
        on_delete=models.SET_NULL,
        verbose_name=_("District"),
        null=True,
        blank=True,
    )
    address_index = models.CharField(_("Address index"), max_length=255, null=True, blank=True)
    gender = models.CharField(_("Gender"), max_length=255, null=True, blank=True, choices=Gender.choices)
    is_deleted = models.BooleanField(_("Is deleted"), default=False)

    objects = SoftDeleteUserManager()
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []  # type: ignore

    def __str__(self):
        if self.phone:
            return str(self.phone)
        if self.email:
            return self.email
        if self.username:
            return self.username

        return str(self.id)

    def prepare_to_delete(self):
        self.is_deleted = True
        for x in ["email", "full_name"]:
            if getattr(self, x):
                setattr(self, x, f"DELETED_{self.id}_{getattr(self, x)}")
        self.save()

    @classmethod
    def generate_username(cls, full_name):
        """
        Generate a unique username from a full name.
        Converts spaces to underscores, makes lowercase, and adds random numbers if needed for uniqueness.
        """
        if not full_name:
            return None

        # Replace spaces with underscores and make lowercase
        base_username = full_name.replace(" ", "_").lower()

        # Remove any non-alphanumeric or underscore characters
        import re

        base_username = re.sub(r"[^\w]", "", base_username)

        # Truncate to stay within the max_length limit
        base_username = base_username[:140]  # Leave room for numbers

        # Check if the username already exists
        username = base_username

        if cls.objects.filter(username=username).exists():
            # If username exists, append a random number and try again
            max_attempts = 100  # Prevent infinite loops

            for _ in range(max_attempts):
                # Generate a random 4-digit number
                random_suffix = random.randint(1000, 9999)
                username = f"{base_username}{random_suffix}"

                # Ensure we don't exceed max_length even with random numbers
                if len(username) > 150:
                    username = f"{base_username[:140 - 4]}{random_suffix}"

                if not cls.objects.filter(username=username).exists():
                    break

            # If we still couldn't find a unique username after max attempts
            # Use timestamp for guaranteed uniqueness
            if cls.objects.filter(username=username).exists():
                timestamp = int(time.time())
                username = f"{base_username[:140 - 10]}{timestamp}"

        return username

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")


class UserDevice(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_("User"), related_name="devices"
    )
    device_id = models.CharField(max_length=256, verbose_name=_("Device id"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is active"))

    def __str__(self):
        return f"{self.user.phone} - {self.device_id}"

    class Meta:
        verbose_name = _("User device")
        verbose_name_plural = _("User devices")
