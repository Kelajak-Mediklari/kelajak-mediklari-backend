from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import LessonPart


@receiver(post_save, sender=LessonPart)
def trigger_hls_conversion(sender, instance, created, **kwargs):
    """
    Signal to trigger HLS video conversion when a video is uploaded to a LessonPart.
    This will run in the background using Celery.
    """
    from .tasks import convert_video_to_hls

    # Check if video has changed (flag set by pre_save signal)
    video_changed = getattr(instance, "_video_changed", False)

    if video_changed and instance.video:
        # Trigger HLS conversion in background
        convert_video_to_hls.delay(instance.id)


@receiver(pre_save, sender=LessonPart)
def check_video_change(sender, instance, **kwargs):
    """
    Pre-save signal to check if video field has changed.
    Sets a flag on the instance to be used in post_save signal.
    """
    if instance.pk:
        try:
            old_instance = LessonPart.objects.get(pk=instance.pk)
            # Set a flag if video has changed
            instance._video_changed = old_instance.video != instance.video
        except LessonPart.DoesNotExist:
            instance._video_changed = False
    else:
        # New instance
        instance._video_changed = bool(instance.video)
