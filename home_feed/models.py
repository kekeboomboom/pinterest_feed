from django.db import models
from typing import TYPE_CHECKING

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
