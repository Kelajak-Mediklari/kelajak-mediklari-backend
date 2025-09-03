from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import BaseModel
from django.utils.text import slugify


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
    slug = models.SlugField(_("Slug"), unique=True, blank=True)
    cover = models.ImageField(_("Cover"), upload_to="courses/", null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="courses")
    learning_outcomes = models.JSONField(null=True, blank=True, default=list)

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