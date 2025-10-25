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
        self.group = Group.objects.filter(
            id=group_id,
            teacher=self.request.user,
            is_active=True
        ).select_related('course').first()

        if not self.group:
            return Group.objects.none()

        # Return lessons with prefetched related data
        return self.group.course.lessons.filter(is_active=True).prefetch_related(
            Prefetch(
                'lesson_group_member_grades',
                queryset=GroupMemberGrade.objects.filter(
                    group_member__group=self.group,
                    group_member__is_active=True
                ).select_related('group_member__user')
            )
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['group'] = self.group
        return context
