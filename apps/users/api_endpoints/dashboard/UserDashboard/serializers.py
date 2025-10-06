from rest_framework import serializers
from apps.course.models import UserCourse, UserLessonPart
from django.db.models import Sum
from datetime import datetime, timedelta


class LastCourseSerializer(serializers.Serializer):
    """Serializer for last watched courses with progress"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    cover = serializers.ImageField()
    progress_percent = serializers.DecimalField(max_digits=5, decimal_places=2)
    last_accessed = serializers.DateTimeField()


class ReadingTempoDataSerializer(serializers.Serializer):
    """Serializer for reading tempo chart data"""
    date = serializers.DateField()
    study_hours = serializers.FloatField()


class UserDashboardSerializer(serializers.Serializer):
    """Main dashboard serializer"""
    last_courses = LastCourseSerializer(many=True)
    reading_tempo = ReadingTempoDataSerializer(many=True)
