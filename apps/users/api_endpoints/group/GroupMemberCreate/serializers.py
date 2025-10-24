from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.users.models import GroupMember, Group


class GroupMemberCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMember
        fields = [
            'group',
            'user',
        ]
    
    def validate(self, attrs):
        group = attrs.get('group')
        user = attrs.get('user')
        
        # Check if group has available space
        if group.current_member_count >= group.max_member_count:
            raise ValidationError(
                _("This group is full. No more members can be added.")
            )
        
        # Check if user is already a member of this group
        if GroupMember.objects.filter(group=group, user=user, is_active=True).exists():
            raise ValidationError(
                _("This user is already a member of this group.")
            )
        
        return attrs
    
    def create(self, validated_data):
        group = validated_data['group']
        # Increment current member count
        group.current_member_count += 1
        group.save(update_fields=['current_member_count'])
        
        return super().create(validated_data)
