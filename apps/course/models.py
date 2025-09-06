from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel
from apps.course.choices import LessonPartType, QuestionType, TestType


class Roadmap(BaseModel):
    image = models.ImageField(_("Image"), upload_to="roadmaps/", null=True, blank=True)
    is_active = models.BooleanField(_("Is Active"), default=True)

    def __str__(self):
        return self.image.name

    class Meta:
        verbose_name = _("Roadmap")
        verbose_name_plural = _("Roadmaps")


class Gallery(BaseModel):
    image = models.ImageField(_("Image"), upload_to="galleries/", null=True, blank=True)

    def __str__(self):
        return self.image.name

    class Meta:
        verbose_name = _("Gallery")
        verbose_name_plural = _("Galleries")


class File(BaseModel):
    file = models.FileField(_("File"), upload_to="files/", null=True, blank=True)

    def __str__(self):
        return self.file.name

    class Meta:
        verbose_name = _("File")
        verbose_name_plural = _("Files")


class Subject(BaseModel):
    title = models.CharField(_("Title"), max_length=255)
    slug = models.SlugField(_("Slug"), unique=True, blank=True)
    icon = models.FileField(_("Icon"), upload_to="subjects/", null=True, blank=True)
    is_active = models.BooleanField(_("Is Active"), default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Subject")
        verbose_name_plural = _("Subjects")

    def __str__(self):
        return self.title


class Course(BaseModel):
    title = models.CharField(_("Title"), max_length=255)
    description = models.TextField(_("Description"), null=True, blank=True)
    slug = models.SlugField(_("Slug"), unique=True, blank=True)
    cover = models.ImageField(_("Cover"), upload_to="courses/", null=True, blank=True)
    subject = models.ForeignKey(
        "course.Subject", on_delete=models.CASCADE, related_name="courses"
    )
    learning_outcomes = models.JSONField(null=True, blank=True, default=list)
    duration = models.CharField(_("Duration"), max_length=255, null=True, blank=True)

    is_unlimited = models.BooleanField(_("Is Unlimited"), default=False)
    is_main_course = models.BooleanField(_("Is Main Course"), default=False)
    is_active = models.BooleanField(_("Is Active"), default=True)

    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Lesson(BaseModel):
    title = models.CharField(_("Title"), max_length=255)
    slug = models.SlugField(_("Slug"), unique=True, blank=True)
    course = models.ForeignKey(
        "course.Course", on_delete=models.CASCADE, related_name="lessons"
    )
    is_active = models.BooleanField(_("Is Active"), default=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Lesson")
        verbose_name_plural = _("Lessons")


class Test(BaseModel):
    title = models.CharField(_("Title"), max_length=255)
    description = models.TextField(_("Description"), null=True, blank=True)
    type = models.CharField(_("Type"), max_length=255, choices=TestType.choices)
    slug = models.SlugField(_("Slug"), unique=True, blank=True)
    test_duration = models.IntegerField(
        _("Test Duration"), default=10, null=True, blank=True, help_text="in minutes"
    )
    is_active = models.BooleanField(_("Is Active"), default=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Test")
        verbose_name_plural = _("Tests")


class LessonPart(BaseModel):
    lesson = models.ForeignKey(
        "course.Lesson", on_delete=models.CASCADE, related_name="parts"
    )
    title = models.CharField(_("Title"), max_length=255)
    description = models.TextField(_("Description"), null=True, blank=True)
    type = models.CharField(_("Type"), max_length=255, choices=LessonPartType.choices)
    order = models.IntegerField(_("Order"), default=1)
    award_coin = models.IntegerField(_("Award Coin"), default=0)
    award_point = models.IntegerField(_("Award Point"), default=0)
    galleries = models.ManyToManyField(
        "course.Gallery", related_name="lesson_parts", blank=True
    )
    attached_files = models.ManyToManyField(
        "course.File", related_name="lesson_parts", blank=True
    )

    # Video related
    video_url = models.URLField(_("Video URL"), null=True, blank=True)

    # Test related
    test = models.ForeignKey(
        "course.Test",
        on_delete=models.CASCADE,
        related_name="lesson_parts",
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(_("Is Active"), default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Lesson Part")
        verbose_name_plural = _("Lesson Parts")
        ordering = ["order"]


# Base Question Model for all test types
class Question(BaseModel):
    test = models.ForeignKey(
        "course.Test", on_delete=models.CASCADE, related_name="questions"
    )
    question_text = models.TextField(_("Question Text"))
    order = models.IntegerField(_("Order"), default=1)
    points = models.IntegerField(_("Points"), default=1)
    is_active = models.BooleanField(_("Is Active"), default=True)

    def __str__(self):
        return f"{self.test.title} - {self.question_text[:50]}..."

    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
        ordering = ["order"]


# True/False Questions
class TrueFalseQuestion(BaseModel):
    question = models.OneToOneField(
        "course.Question", on_delete=models.CASCADE, related_name="true_false_question"
    )
    correct_answer = models.BooleanField(_("Correct Answer"))

    def __str__(self):
        return f"True/False: {self.question.question_text[:50]}..."

    class Meta:
        verbose_name = _("True False Question")
        verbose_name_plural = _("True False Questions")


# Matching Questions
class MatchingQuestion(BaseModel):
    question = models.OneToOneField(
        "course.Question", on_delete=models.CASCADE, related_name="matching_question"
    )
    instructions = models.TextField(
        _("Instructions"),
        default="Match the items on the left with the correct items on the right.",
        blank=True,
    )

    def __str__(self):
        return f"Matching: {self.question.question_text[:50]}..."

    class Meta:
        verbose_name = _("Matching Question")
        verbose_name_plural = _("Matching Questions")


class MatchingPair(BaseModel):
    matching_question = models.ForeignKey(
        "course.MatchingQuestion", on_delete=models.CASCADE, related_name="pairs"
    )
    left_item = models.TextField(_("Left Item"))  # Question side
    right_item = models.TextField(_("Right Item"))  # Answer side
    order = models.IntegerField(_("Order"), default=1)

    def __str__(self):
        return f"{self.left_item[:30]} -> {self.right_item[:30]}"

    class Meta:
        verbose_name = _("Matching Pair")
        verbose_name_plural = _("Matching Pairs")
        ordering = ["order"]


# Book Test Questions
class BookTestQuestion(BaseModel):
    question = models.OneToOneField(
        "course.Question", on_delete=models.CASCADE, related_name="book_test_question"
    )
    book_page = models.IntegerField(_("Book Page"), help_text="Page number in the book")
    question_number = models.IntegerField(
        _("Question Number"), help_text="Question number on the page"
    )
    expected_answer = models.TextField(
        _("Expected Answer"),
        help_text="Expected answer for reference (optional)",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Book Test Page {self.book_page} Q{self.question_number}: {self.question.question_text[:50]}..."

    class Meta:
        verbose_name = _("Book Test Question")
        verbose_name_plural = _("Book Test Questions")
        ordering = ["book_page", "question_number"]


# Regular Test Questions (with multiple choice options)
class RegularTestQuestion(BaseModel):
    question = models.OneToOneField(
        "course.Question",
        on_delete=models.CASCADE,
        related_name="regular_test_question",
    )
    question_type = models.CharField(
        _("Question Type"),
        max_length=50,
        choices=QuestionType.choices,
        default=QuestionType.TEXT_CHOICE,
    )
    # For video questions
    video_url = models.URLField(_("Video URL"), null=True, blank=True)
    # For questions with additional media
    question_image = models.ImageField(
        _("Question Image"), upload_to="questions/images/", null=True, blank=True
    )

    def __str__(self):
        return f"Regular: {self.question.question_text[:50]}..."

    class Meta:
        verbose_name = _("Regular Test Question")
        verbose_name_plural = _("Regular Test Questions")


# Answer choices for Regular Test Questions
class AnswerChoice(BaseModel):
    regular_question = models.ForeignKey(
        "course.RegularTestQuestion", on_delete=models.CASCADE, related_name="choices"
    )
    choice_text = models.TextField(_("Choice Text"), null=True, blank=True)
    choice_image = models.ImageField(
        _("Choice Image"), upload_to="questions/choices/", null=True, blank=True
    )
    choice_label = models.CharField(
        _("Choice Label"), max_length=5, help_text="A, B, C, D, etc."
    )
    is_correct = models.BooleanField(_("Is Correct"), default=False)
    order = models.IntegerField(_("Order"), default=1)

    def __str__(self):
        choice_display = (
            self.choice_text
            if self.choice_text
            else f"Image: {self.choice_image.name if self.choice_image else 'No image'}"
        )
        return f"{self.choice_label}: {choice_display[:30]}..."

    class Meta:
        verbose_name = _("Answer Choice")
        verbose_name_plural = _("Answer Choices")
        ordering = ["order"]
        unique_together = ["regular_question", "choice_label"]
