from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from apps.users.models import GroupMember
from apps.users.permissions import IsTeacher
from .serializers import GroupMemberCreateSerializer


class GroupMemberCreateView(CreateAPIView):
    serializer_class = GroupMemberCreateSerializer
    permission_classes = [IsAuthenticated, IsTeacher]
    
    def get_queryset(self):
        return GroupMember.objects.filter(
            group__teacher=self.request.user
        )
