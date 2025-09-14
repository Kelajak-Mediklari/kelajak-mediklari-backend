from django.db import models
from django.utils.translation import gettext_lazy as _
from ckeditor_uploader.fields import RichTextUploadingField


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        abstract = True


class VersionHistory(BaseModel):
    version = models.CharField(_("Version"), max_length=64)
    required = models.BooleanField(_("Required"), default=True)

    class Meta:
        verbose_name = _("Version history")
        verbose_name_plural = _("Version histories")

    def __str__(self):
        return self.version


class FrontendTranslation(BaseModel):
    key = models.CharField(_("Key"), max_length=255, unique=True)
    text = models.CharField(_("Text"), max_length=1024)

    class Meta:
        verbose_name = _("Frontend translation")
        verbose_name_plural = _("Frontend translations")

    def __str__(self):
        return str(self.key)


class UsefulLinkCategory(BaseModel):
    title = models.CharField(_("Title"), max_length=255)
    slug = models.SlugField(_("Slug"), unique=True, blank=True)

    class Meta:
        verbose_name = _("Useful link category")
        verbose_name_plural = _("Useful link categories")

    def __str__(self):
        return self.title


class UsefulLinkSubject(BaseModel):
    title = models.CharField(_("Title"), max_length=255)
    slug = models.SlugField(_("Slug"), unique=True, blank=True)

    class Meta:
        verbose_name = _("Useful link subject")
        verbose_name_plural = _("Useful link subjects")

    def __str__(self):
        return self.title


class UsefulLinkFile(BaseModel):
    file = models.FileField(_("File"), upload_to="useful_links/", null=True, blank=True)
    is_active = models.BooleanField(_("Is Active"), default=True)

    class Meta:
        verbose_name = _("Useful link file")
        verbose_name_plural = _("Useful link files")

    def __str__(self):
        return self.file.name


class UsefulLink(BaseModel):
    title = models.CharField(_("Title"), max_length=255)
    slug = models.SlugField(_("Slug"), unique=True, blank=True)
    description = RichTextUploadingField(_("Description"))
    category = models.ForeignKey(UsefulLinkCategory, on_delete=models.CASCADE, related_name="links")
    subject = models.ForeignKey(UsefulLinkSubject, on_delete=models.CASCADE, related_name="links")
    cover_image = models.ImageField(_("Cover Image"), upload_to="useful_links/", null=True, blank=True)
    video_url = models.URLField(_("Video URL"), null=True, blank=True)
    video_file = models.FileField(_("Video File"), upload_to="useful_links/", null=True, blank=True)
    is_active = models.BooleanField(_("Is Active"), default=True)
    files = models.ManyToManyField(UsefulLinkFile, related_name="links", blank=True, null=True)

    class Meta:
        verbose_name = _("Useful link")
        verbose_name_plural = _("Useful links")

    def __str__(self):
        return self.title
