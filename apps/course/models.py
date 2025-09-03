from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel
from apps.course.choices import LessonPartType


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

    # Video type
    video_url = models.URLField(_("Video URL"), null=True, blank=True)

    is_active = models.BooleanField(_("Is Active"), default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Lesson Part")
        verbose_name_plural = _("Lesson Parts")
        ordering = ["order"]
