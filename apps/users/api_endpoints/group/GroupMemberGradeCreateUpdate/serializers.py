from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.users.models import GroupMemberGrade, GroupMember


class GroupMemberGradeCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMemberGrade
        fields = [
            'group_member',
            'lesson',
            'theoretical_ball',
            'practical_ball',
        ]
    
    def validate_theoretical_ball(self, value):
        if value < 0 or value > 100:
            raise ValidationError(_("Theoretical ball must be between 0 and 100."))
        return value
    
    def validate_practical_ball(self, value):
        if value < 0 or value > 100:
            raise ValidationError(_("Practical ball must be between 0 and 100."))
        return value
    
    def validate(self, attrs):
        group_member = attrs.get('group_member')
        lesson = attrs.get('lesson')
        
        # Check if group member belongs to teacher's group
        if not GroupMember.objects.filter(
            group__teacher=self.context['request'].user,
            id=group_member.id
        ).exists():
            raise ValidationError(_("You can only grade students from your own groups."))
        
        # Check if lesson belongs to the same course as the group
        if group_member.group.course != lesson.course:
            raise ValidationError(_("Lesson must belong to the same course as the group."))
        
        return attrs
    
    def create(self, validated_data):
        # Check if grade already exists for this group_member and lesson
        existing_grade = GroupMemberGrade.objects.filter(
            group_member=validated_data['group_member'],
            lesson=validated_data['lesson']
        ).first()
        
        if existing_grade:
            # Update existing grade
            existing_grade.theoretical_ball = validated_data['theoretical_ball']
            existing_grade.practical_ball = validated_data['practical_ball']
            existing_grade.save()
            return existing_grade
        else:
            # Create new grade
            return super().create(validated_data)
