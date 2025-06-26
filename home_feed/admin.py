from django.contrib import admin
from .models import ImageURL, APIKey

@admin.register(ImageURL)
class ImageURLAdmin(admin.ModelAdmin):
    list_display = ('alt', 'src', 'origin', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('alt', 'src', 'origin')
    readonly_fields = ('src', 'origin', 'fallback_urls')


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'key_preview', 'is_active', 'created_at', 'last_used')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('key', 'created_at', 'last_used')
    fieldsets = (
        (None, {
            'fields': ('name', 'is_active')
        }),
        ('Key Information', {
            'fields': ('key', 'created_at', 'last_used'),
            'classes': ('collapse',)
        }),
    )

    def key_preview(self, obj):
        return f"{obj.key[:8]}..." if obj.key else "Not generated"
    key_preview.short_description = "API Key Preview"
