from django.contrib import admin
from .models import Owner

@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ("user", "govt_full_name", "status", "created_at")
    search_fields = ("govt_full_name", "user__username", "user__email")
