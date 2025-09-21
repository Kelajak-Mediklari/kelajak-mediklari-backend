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
    path(
        "lessons/parts/<int:id>/",
        course.LessonPartDetailAPIView.as_view(),
        name="lesson-part-detail",
    ),
    path(
        "tests/<int:id>/",
        course.TestDetailAPIView.as_view(),
        name="test-detail",
    ),
    path(
        "tests/<int:test_id>/start/",
        course.TestStartAPIView.as_view(),
        name="test-start",
    ),
    path(
        "tests/<int:test_id>/questions/",
        course.TestQuestionsAPIView.as_view(),
        name="test-questions",
    ),
    path(
        "tests/<int:test_id>/answers/<int:answer_id>/",
        course.SubmitAnswerAPIView.as_view(),
        name="submit-answer",
    ),
    path(
        "tests/<int:test_id>/finish/",
        course.FinishTestAPIView.as_view(),
        name="finish-test",
    ),
    path(
        "subjects/<int:subject_id>/roadmap/",
        course.RoadmapAPIView.as_view(),
        name="roadmap",
    ),
    # USER RELATED APIS
    path("user-courses/", course.UserCoursesListAPIView.as_view(), name="user-courses"),
    path(
        "user-lesson/create/",
        course.UserLessonCreateAPIView.as_view(),
        name="user-lesson-create",
    ),
    path(
        "user-lesson-part/create/",
        course.UserLessonPartCreateAPIView.as_view(),
        name="user-lesson-part-create",
    ),
]
