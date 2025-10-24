from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from apps.users.models import Group
from apps.users.permissions import IsTeacher
from .serializers import GroupCreateSerializer


class GroupCreateView(CreateAPIView):
    serializer_class = GroupCreateSerializer
    permission_classes = [IsAuthenticated, IsTeacher]
    
    def get_queryset(self):
        return Group.objects.filter(teacher=self.request.user)
