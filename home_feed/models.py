from django.db import models
from typing import TYPE_CHECKING
import secrets
import string

if TYPE_CHECKING:
    from django.db.models.manager import Manager

class ImageURL(models.Model):
    if TYPE_CHECKING:
        objects: "Manager"
    
    src = models.URLField(unique=True, max_length=500)
    alt = models.CharField(max_length=255, blank=True)
    origin = models.URLField(max_length=500)
    fallback_urls = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)  # type: ignore
    
    def __str__(self):
        return f"{self.alt}: {str(self.src)[:50]}..."
    class Meta:
        ordering = ['-id']
        verbose_name = "Image URL"
        verbose_name_plural = "Image URLs"


class APIKey(models.Model):
    if TYPE_CHECKING:
        objects: "Manager"
    
    name = models.CharField(max_length=100, help_text="Descriptive name for this API key")
    key = models.CharField(max_length=64, unique=True, editable=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_key():
        """Generate a secure API key"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(64))

    def __str__(self):
        return f"{self.name}: {self.key[:8]}..."

    class Meta:
        ordering = ['-created_at']
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"
