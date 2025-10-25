from rest_framework import serializers

from apps.users.models import GroupMemberGrade
from apps.course.models import Lesson


class StudentGradeSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    student_name = serializers.CharField()
    student_username = serializers.CharField()
    student_avatar = serializers.ImageField()
    theoretical_ball = serializers.IntegerField()
    practical_ball = serializers.IntegerField()


class GroupMemberGradeListSerializer(serializers.ModelSerializer):
    lesson_id = serializers.IntegerField(source='id')
    lesson_title = serializers.CharField(source='title')
    lesson_slug = serializers.CharField(source='slug')
    students = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'lesson_id',
            'lesson_title',
            'lesson_slug',
            'theoretical_pass_ball',
            'practical_pass_ball',
            'students'
        ]

    def get_students(self, obj):
        # Get all group members for this lesson's group
        group = self.context.get('group')
        if not group:
            return []

        members = group.members.filter(is_active=True).prefetch_related('user')
        students_data = []

        for member in members:
            # Get grade for this lesson and member
            grade = obj.lesson_group_member_grades.filter(
                group_member=member
            ).first()

            student_data = {
                'student_id': member.user.id,
                'student_name': member.user.full_name,
                'student_username': member.user.username,
                'student_avatar': member.user.avatar,
                'theoretical_ball': grade.theoretical_ball if grade else 0,
                'practical_ball': grade.practical_ball if grade else 0,
            }
            students_data.append(student_data)

        return students_data
