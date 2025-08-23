from django.contrib import admin

from apps.users.models import User, UserDevice


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "phone",
        "email",
        "username",
        "full_name",
        "created_at",
    )
    search_fields = ("phone", "full_name", "email", "username")
    ordering = ("created_at",)


@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ("user", "device_id", "created_at")
    search_fields = ("user__phone", "user__full_name", "user__email", "user__username")
    ordering = ("created_at",)