from django.contrib import admin
from .models import QRLog

class QRLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at", "expires_at", "decoded_at")
    search_fields = ("user__username",)
    list_filter = ("created_at", "expires_at", "decoded_at")

admin.site.register(QRLog, QRLogAdmin)
