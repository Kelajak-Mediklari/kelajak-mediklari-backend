from django.contrib import admin
from django.contrib.auth.hashers import identify_hasher, make_password

from apps.users.models import (
    Group,
    GroupMember,
    GroupMemberGrade,
    TeacherGlobalLimit,
    User,
    UserDevice,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "phone",
        "email",
        "username",
        "full_name",
        "role",
        "created_at",
    )
    search_fields = ("phone", "full_name", "email", "username")
    list_filter = ("role", "is_active", "is_deleted")
    ordering = ("created_at",)

    def save_model(self, request, obj, form, change):
        """
        Ensure that passwords entered via the admin UI are hashed before saving.

        If the password value already looks like a hashed password (Django can
        identify the hasher), we leave it as-is. Otherwise we hash it.
        """
        password = form.cleaned_data.get("password")

        if password and (not obj.pk or password != obj.password):
            try:
                identify_hasher(password)
                hashed_password = password
            except ValueError:
                hashed_password = make_password(password)

            obj.password = hashed_password

        super().save_model(request, obj, form, change)


@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ("user", "device_id", "is_active", "created_at")
    search_fields = ("user__phone", "user__full_name", "user__email", "user__username")
    list_filter = ("is_active", "created_at")
    ordering = ("created_at",)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "teacher",
        "course",
        "current_member_count",
        "max_member_count",
        "is_active",
        "group_end_date",
        "created_at",
    )
    search_fields = ("name", "teacher__full_name", "teacher__username", "course__title")
    list_filter = ("is_active", "course__subject", "created_at")
    readonly_fields = ("current_member_count",)
    ordering = ("created_at",)


@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = (
        "group",
        "user",
        "is_active",
        "created_at",
    )
    search_fields = ("group__name", "user__full_name", "user__username", "user__phone")
    list_filter = ("is_active", "group__course", "created_at")
    ordering = ("created_at",)


@admin.register(GroupMemberGrade)
class GroupMemberGradeAdmin(admin.ModelAdmin):
    list_display = (
        "group_member",
        "lesson",
        "theoretical_ball",
        "practical_ball",
        "created_at",
    )
    search_fields = (
        "group_member__user__full_name",
        "group_member__user__username",
        "lesson__title",
        "group_member__group__name"
    )
    list_filter = ("lesson__course", "created_at")
    ordering = ("created_at",)


@admin.register(TeacherGlobalLimit)
class TeacherGlobalLimitAdmin(admin.ModelAdmin):
    list_display = (
        "teacher",
        "course",
        "limit",
        "used",
        "remaining",
        "created_at",
    )
    search_fields = (
        "teacher__full_name",
        "teacher__username",
        "course__title"
    )
    list_filter = ("course__subject", "created_at")
    ordering = ("created_at",)
