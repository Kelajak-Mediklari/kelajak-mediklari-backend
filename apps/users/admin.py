from django.contrib import admin
from django.contrib.auth.hashers import identify_hasher, make_password

from apps.users.forms import GroupMemberInline
from apps.users.models import (
    Group,
    GroupMember,
    GroupMemberGrade,
    TeacherGlobalLimit,
    User,
    UserDevice, KMTeacher,
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
    readonly_fields = ("current_member_count", "group_end_date")
    ordering = ("created_at",)
    inlines = [GroupMemberInline]

    def get_queryset(self, request):
        """Filter groups to show only those belonging to the logged-in user"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(teacher=request.user)

    def get_readonly_fields(self, request, obj=None):
        """Make teacher field read-only for non-superusers"""
        readonly = list(self.readonly_fields)
        if not request.user.is_superuser:
            readonly.append('teacher')
        return readonly

    def get_form(self, request, obj=None, **kwargs):
        """Set teacher initial value so clean() can check limits"""
        form = super().get_form(request, obj, **kwargs)

        # Capture variables for closure
        is_new = not obj
        is_not_superuser = not request.user.is_superuser
        teacher_id = request.user.id if is_not_superuser else None

        # For new objects, set initial teacher value so it's available during clean()
        if is_new and is_not_superuser and 'teacher' in form.base_fields:
            form.base_fields['teacher'].initial = teacher_id

        # Also override clean to ensure teacher_id is set on instance
        original_clean = form.clean

        def clean_with_teacher(self):
            # Set teacher_id on instance if not set (for new objects)
            if is_new and is_not_superuser and teacher_id:
                if hasattr(self, 'instance') and self.instance:
                    if not getattr(self.instance, 'teacher_id', None):
                        self.instance.teacher_id = teacher_id
            return original_clean(self)

        form.clean = clean_with_teacher
        return form

    def save_model(self, request, obj, form, change):
        """Automatically set the teacher to the current user when creating a new group"""
        if not change:  # Only for new objects
            obj.teacher = request.user
        elif not request.user.is_superuser:
            # Ensure non-superusers can't change the teacher
            obj.teacher = request.user
        super().save_model(request, obj, form, change)


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

    def get_queryset(self, request):
        """Filter group members to show only those in groups belonging to the logged-in user"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(group__teacher=request.user)

    def get_form(self, request, obj=None, **kwargs):
        """Filter the group dropdown to show only groups belonging to the logged-in user"""
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            # Filter the group field queryset
            form.base_fields['group'].queryset = Group.objects.filter(teacher=request.user)
        return form


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

    def get_queryset(self, request):
        """Filter group member grades to show only those in groups belonging to the logged-in user"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(group_member__group__teacher=request.user)

    def get_form(self, request, obj=None, **kwargs):
        """Filter the group_member dropdown to show only members of groups belonging to the logged-in user"""
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            # Filter the group_member field queryset
            form.base_fields['group_member'].queryset = GroupMember.objects.filter(group__teacher=request.user)
        return form


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
    list_filter = ("course__subject", "created_at", "course")
    ordering = ("created_at",)


@admin.register(KMTeacher)
class KMTeacherAdmin(admin.ModelAdmin):
    list_display = ("km_id", "user", "user_full_name", "user_phone", "is_repetitor", "teacher_type")
    search_fields = ("km_id", "user__full_name", "user__phone")
    list_filter = ("user__role", "teacher_type")
    ordering = ("km_id",)

    readonly_fields = ("user_full_name", "user_phone")

    def user_full_name(self, obj):
        return obj.user.full_name

    user_full_name.short_description = "Full Name"

    def user_phone(self, obj):
        return obj.user.phone

    user_phone.short_description = "Phone Number"
