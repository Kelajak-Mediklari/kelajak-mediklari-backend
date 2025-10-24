from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from apps.users.models import GroupMemberGrade
from apps.users.permissions import IsTeacher
from .serializers import GroupMemberGradeCreateUpdateSerializer


class GroupMemberGradeCreateView(CreateAPIView):
    serializer_class = GroupMemberGradeCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsTeacher]
    
    def get_queryset(self):
        return GroupMemberGrade.objects.filter(
            group_member__group__teacher=self.request.user
        )


class GroupMemberGradeUpdateView(UpdateAPIView):
    serializer_class = GroupMemberGradeCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsTeacher]
    
    def get_queryset(self):
        return GroupMemberGrade.objects.filter(
            group_member__group__teacher=self.request.user
        )


__all__ = ["GroupMemberGradeCreateView", "GroupMemberGradeUpdateView"]
