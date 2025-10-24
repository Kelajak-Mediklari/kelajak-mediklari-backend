from rest_framework import serializers

from apps.users.models import GroupMember, GroupMemberGrade
from apps.course.models import Lesson


class StudentGradeSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    student_name = serializers.CharField()
    student_username = serializers.CharField()
    student_avatar = serializers.ImageField()
    theoretical_ball = serializers.IntegerField()
    practical_ball = serializers.IntegerField()


class LessonGradeSerializer(serializers.Serializer):
    lesson_id = serializers.IntegerField()
    lesson_title = serializers.CharField()
    lesson_slug = serializers.CharField()
    theoretical_pass_ball = serializers.IntegerField()
    practical_pass_ball = serializers.IntegerField()
    students = StudentGradeSerializer(many=True)
