from django.db.models import Count, Q
from rest_framework.generics import ListAPIView

from apps.users.models import Group
from apps.users.permissions import IsTeacher
from .serializers import GroupListSerializer


class GroupListView(ListAPIView):
    serializer_class = GroupListSerializer
    permission_classes = [IsTeacher]
    
    def get_queryset(self):
        return Group.objects.filter(
            teacher=self.request.user,
            is_active=True
        ).select_related(
            'course',
            'course__subject'
        ).annotate(
            members_count=Count('members', filter=Q(members__is_active=True))
        ).order_by('-created_at')