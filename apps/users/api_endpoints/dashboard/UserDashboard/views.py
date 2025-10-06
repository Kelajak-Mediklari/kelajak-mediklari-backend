from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Sum, Q
from datetime import datetime, timedelta
from django.utils import timezone

from apps.course.models import UserCourse, UserLessonPart
from .serializers import UserDashboardSerializer, LastCourseSerializer, ReadingTempoDataSerializer


class UserDashboardView(GenericAPIView):
    """User dashboard with last courses and reading tempo"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserDashboardSerializer

    def get(self, request, *args, **kwargs):
        """Get user dashboard data with optimized queries"""
        user = request.user
        
        # Get all dashboard data in optimized queries
        dashboard_data = self.get_dashboard_data(user)
        
        serializer = self.get_serializer(dashboard_data)
        return Response(serializer.data)

    def get_dashboard_data(self, user):
        """Get all dashboard data with optimized queries"""
        from django.db.models import Count, Sum, F, FloatField, Q
        
        # Single query for user courses with progress
        user_courses = UserCourse.objects.filter(
            user=user,
            course__is_active=True
        ).select_related('course').prefetch_related(
            'course__lessons',
            'user_lessons'
        ).annotate(
            total_lessons=Count('course__lessons', filter=Q(course__lessons__is_active=True)),
            completed_lessons=Count('user_lessons', filter=Q(user_lessons__is_completed=True))
        ).order_by('-updated_at')[:2]
        
        # Get last courses data
        last_courses_data = []
        for user_course in user_courses:
            if user_course.total_lessons > 0:
                progress_percent = round((user_course.completed_lessons / user_course.total_lessons) * 100, 2)
            else:
                progress_percent = 0.00
            
            last_courses_data.append({
                'id': user_course.course.id,
                'title': user_course.course.title,
                'cover': user_course.course.cover,
                'progress_percent': progress_percent,
                'last_accessed': user_course.updated_at
            })
        
        # Get reading tempo data for last 30 days
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=29)
        
        daily_points = UserLessonPart.objects.filter(
            user_lesson__user_course__user=user,
            is_completed=True,
            completion_date__date__gte=start_date,
            completion_date__date__lte=end_date
        ).select_related('lesson_part').extra(
            select={'date': 'DATE(course_userlessonpart.completion_date)'}
        ).values('date').annotate(
            study_hours=Sum(F('lesson_part__award_point') / 10.0, output_field=FloatField())
        ).order_by('date')
        
        # Create date dictionary and fill missing dates
        date_dict = {item['date']: round(item['study_hours'] or 0, 1) for item in daily_points}
        
        reading_tempo_data = []
        current_date = start_date
        while current_date <= end_date:
            reading_tempo_data.append({
                'date': current_date,
                'study_hours': date_dict.get(current_date, 0.0)
            })
            current_date += timedelta(days=1)
        
        return {
            'last_courses': last_courses_data,
            'reading_tempo': reading_tempo_data
        }


__all__ = ["UserDashboardView"]
