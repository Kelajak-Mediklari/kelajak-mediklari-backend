from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Prefetch

from apps.users.models import Group, GroupMemberGrade, GroupMember
from apps.users.permissions import IsTeacher
from .serializers import GroupMemberGradeListSerializer


class GroupMemberGradePagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 50


class GroupMemberGradeListView(ListAPIView):
    serializer_class = GroupMemberGradeListSerializer
    permission_classes = [IsAuthenticated, IsTeacher]
    pagination_class = GroupMemberGradePagination
    
    def get_queryset(self):
        group_id = self.kwargs.get('pk')
        group = Group.objects.filter(
            id=group_id,
            teacher=self.request.user,
            is_active=True
        ).select_related('course').first()
        
        if not group:
            return Group.objects.none()
        
        # Get all lessons for this group's course
        lessons = group.course.lessons.filter(is_active=True)
        
        # Get all students for the group
        members = group.members.filter(is_active=True).prefetch_related('user')
        
        # Prefetch all grades for these lessons and students
        grades_prefetch = Prefetch(
            'group_member_grades',
            queryset=GroupMemberGrade.objects.filter(
                lesson__in=lessons,
                group_member__in=members
            ).select_related('lesson')
        )
        
        # Apply prefetch to members
        members = members.prefetch_related(grades_prefetch)
        
        # Build lesson data with students
        lesson_data_list = []
        for lesson in lessons:
            lesson_data = {
                'lesson_id': lesson.id,
                'lesson_title': lesson.title,
                'lesson_slug': lesson.slug,
                'theoretical_pass_ball': lesson.theoretical_pass_ball,
                'practical_pass_ball': lesson.practical_pass_ball,
                'students': []
            }
            
            # Add students with their grades
            for member in members:
                grade = member.group_member_grades.filter(lesson=lesson).first()
                student_data = {
                    'student_id': member.user.id,
                    'student_name': member.user.full_name,
                    'student_username': member.user.username,
                    'student_avatar': member.user.avatar,
                    'theoretical_ball': grade.theoretical_ball if grade else 0,
                    'practical_ball': grade.practical_ball if grade else 0,
                }
                lesson_data['students'].append(student_data)
            
            lesson_data_list.append(lesson_data)
        
        return lesson_data_list
