from django.urls import path

from .api_endpoints import course

app_name = "course"

urlpatterns = [
    path("subjects/", course.SubjectListAPIView.as_view(), name="subjects"),
    path("list/", course.CourseListAPIView.as_view(), name="courses"),
]
