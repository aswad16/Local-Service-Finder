from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import hashlib
import hmac
import random
import string
import os


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('provider', 'Service Provider'),
        ('admin', 'Administrator'),
    ]

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hi', 'Hindi'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=20, blank=True)
    phone_country_code = models.CharField(max_length=10, blank=True, default='+91')
    whatsapp_no = models.CharField(max_length=20, blank=True, help_text="WhatsApp number for contact")
    whatsapp_country_code = models.CharField(max_length=10, blank=True, default='+91')
    preferred_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # OTP fields — code stored as salted HMAC hash, not plain text
    otp_hash = models.CharField(max_length=64, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    otp_purpose = models.CharField(max_length=20, blank=True)

    # Legacy plain-text field kept for migration compatibility — not used
    otp_code = models.CharField(max_length=6, blank=True)

    class Meta:
        db_table = 'users_customuser'

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_provider(self):
        return self.role == 'provider'

    @property
    def is_customer(self):
        return self.role == 'customer'

    @property
    def is_admin_user(self):
        return self.role == 'admin' or self.is_staff

    def _hash_otp(self, code):
        """Return HMAC-SHA256 hex of code using SECRET_KEY as the key."""
        secret = settings.SECRET_KEY.encode()
        return hmac.new(secret, code.encode(), hashlib.sha256).hexdigest()

    def generate_otp(self, purpose='phone_verify'):
        """
        Generate a 6-digit OTP. Enforces a per-user cooldown to prevent
        SMS flooding. Returns the plain OTP (caller must send it; we do not
        store it in plain text).
        """
        cooldown = getattr(settings, 'OTP_COOLDOWN_SECONDS', 60)
        if self.otp_created_at:
            elapsed = (timezone.now() - self.otp_created_at).total_seconds()
            if elapsed < cooldown:
                remaining = int(cooldown - elapsed)
                raise ValueError(
                    f"Please wait {remaining} seconds before requesting a new OTP."
                )

        code = ''.join(random.choices(string.digits, k=6))
        self.otp_hash = self._hash_otp(code)
        self.otp_code = ''          # never store plain text
        self.otp_created_at = timezone.now()
        self.otp_purpose = purpose
        self.save(update_fields=['otp_hash', 'otp_code', 'otp_created_at', 'otp_purpose'])
        return code

    def verify_otp(self, code, purpose='phone_verify'):
        """Constant-time comparison against stored hash."""
        if not self.otp_hash or not self.otp_created_at:
            return False
        if self.otp_purpose != purpose:
            return False
        expiry_minutes = getattr(settings, 'OTP_EXPIRY_MINUTES', 10)
        if timezone.now() > self.otp_created_at + timedelta(minutes=expiry_minutes):
            return False
        return hmac.compare_digest(self.otp_hash, self._hash_otp(code))

    def clear_otp(self):
        self.otp_hash = ''
        self.otp_code = ''
        self.otp_created_at = None
        self.otp_purpose = ''
        self.save(update_fields=['otp_hash', 'otp_code', 'otp_created_at', 'otp_purpose'])
