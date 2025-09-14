from django.urls import path

from .api_endpoints import course

app_name = "course"

urlpatterns = [
    path("subjects/", course.SubjectListAPIView.as_view(), name="subjects"),
    path(
        "subjects/<int:subject_id>/courses/",
        course.CourseListAPIView.as_view(),
        name="courses",
    ),
    path(
        "<int:course_id>/lessons/", course.LessonsListAPIView.as_view(), name="lessons"
    ),
    path(
        "lessons/<int:lesson_id>/parts/",
        course.LessonPartListAPIView.as_view(),
        name="lesson-parts",
    ),
    path("roadmap/", course.RoadmapAPIView.as_view(), name="roadmap"),
]
