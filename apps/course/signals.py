from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserLessonPart


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
            user_course.save(update_fields=['coins_earned', 'points_earned'])
