from django.db import models
from django.utils.translation import gettext_lazy as _


class LessonPartType(models.TextChoices):
    VIDEO = "video", _("Video")
    THEORY = "theory", _("Theory")
    MATCHING = "matching", _("Matching")
    TRUE_FALSE = "true_false", _("True False")
    BOOK_TEST = "book_test", _("Book Test")
    REGULAR_TEST = "regular_test", _("Regular Test")
    ASSIGNMENT = "assignment", _("Assignment")


class TestType(models.TextChoices):
    TRUE_FALSE = "true_false", _("True False")
    MATCHING = "matching", _("Matching")
    BOOK_TEST = "book_test", _("Book Test")
    REGULAR_TEST = "regular_test", _("Regular Test")


class QuestionType(models.TextChoices):
    TEXT_CHOICE = "text_choice", _("Text Choice")  # A, B, C, D options
    IMAGE_CHOICE = "image_choice", _("Image Choice")  # Image options
    VIDEO_CHOICE = "video_choice", _("Video Choice")  # Video with A, B, C, D options