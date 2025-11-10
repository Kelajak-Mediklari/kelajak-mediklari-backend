from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import LessonPart, UserLessonPart


@receiver(post_save, sender=UserLessonPart)
def update_user_coins_points_on_completion(sender, instance, created, **kwargs):
    """
    Signal to automatically update user's coins and points when a lesson part is completed.
    This ensures that even if mark_completed() is not called explicitly, the user still gets rewards.
    """
    # Only process if the lesson part was just marked as completed
    if not created and instance.is_completed:
        # Check if this is the first time it's being marked as completed
        # by checking if completion_date was just set
        if instance.completion_date:
            # Get the user course to access the user
            user_course = instance.user_lesson.user_course
            user = user_course.user

            # Award coins and points (always, even if 0)
            user.add_coins(instance.lesson_part.award_coin)
            user.add_points(instance.lesson_part.award_point)

            # Update user course totals as well
            user_course.coins_earned += instance.lesson_part.award_coin
            user_course.points_earned += instance.lesson_part.award_point
            user_course.save(update_fields=["coins_earned", "points_earned"])


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
