from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.users.models import Group, TeacherGlobalLimit


class GroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = [
            'name',
            'course',
            'max_member_count',
        ]

    def validate(self, attrs):
        teacher = self.context['request'].user
        course = attrs.get('course')

        # Check if teacher has remaining limit for this course
        try:
            teacher_limit = TeacherGlobalLimit.objects.get(
                teacher=teacher,
                course=course
            )
            if teacher_limit.remaining <= 0:
                raise ValidationError(
                    _("You do not have remaining limit for this course. Please purchase more.")
                )
        except TeacherGlobalLimit.DoesNotExist:
            raise ValidationError(
                _("You do not have access to this course. Please purchase the course first.")
            )

        return attrs

    def create(self, validated_data):
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)
