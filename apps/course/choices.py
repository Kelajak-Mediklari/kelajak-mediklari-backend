from django.db import models
from django.utils.translation import gettext_lazy as _


class LessonPartType(models.TextChoices):
    VIDEO = "video", _("Video")
    THEORY = "theory", _("Theory")
    MATCHING = "matching", _("Matching")
    TRUE_FALSE = "true_false", _("True False")
    BOOK_TEST = "book_test", _("Book Test")
    TEST = "test", _("Test")
    ASSIGNMENT = "assignment", _("Assignment")
