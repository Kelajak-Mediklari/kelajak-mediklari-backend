from rest_framework import serializers

from apps.users.models import GroupMemberGrade
from apps.course.models import Lesson


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
        
        # Use prefetched group members from view
        group_members = getattr(self.context.get('view'), 'group_members', [])
        if not group_members:
            group_members = group.members.filter(is_active=True).select_related('user')
        
        # Use pre-built grades dictionary from view
        grades_dict = getattr(self.context.get('view'), 'grades_dict', {})
        
        students_data = []
        
        for member in group_members:
            # Get grade from pre-built dictionary
            grade_key = f"{obj.id}_{member.id}"
            grade = grades_dict.get(grade_key)
            
            student_data = {
                'student_id': member.user.id,
                'student_name': member.user.full_name,
                'student_username': member.user.username,
                'student_avatar': member.user.avatar.url if member.user.avatar else None,
                'theoretical_ball': grade.theoretical_ball if grade else 0,
                'practical_ball': grade.practical_ball if grade else 0,
            }
            students_data.append(student_data)
        
        return students_data
