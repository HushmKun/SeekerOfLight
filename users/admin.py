from django.contrib import admin

from .models import User

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["get_full_name", "email", "date_joined", "country", "is_active"]
    list_display_links = ["get_full_name"]
