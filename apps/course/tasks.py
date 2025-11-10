import logging
import subprocess
from pathlib import Path

from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import LessonPart, UserCourse

logger = logging.getLogger(__name__)


@shared_task
def check_expired_courses():
    """
    Cron job to check for expired courses and update them
    Runs every hour to check if any course finish_date has passed
    """
    current_time = timezone.now()

    with transaction.atomic():
        # Find all UserCourses that have finish_date in the past and are not already marked as expired
        expired_courses = UserCourse.objects.filter(
            finish_date__lt=current_time, is_expired=False, finish_date__isnull=False
        )

        # Update expired courses
        updated_count = expired_courses.update(is_expired=True, finish_date=None)

        return f"Updated {updated_count} expired courses"


@shared_task(bind=True, max_retries=3)
def convert_video_to_hls(self, lesson_part_id):
    """
    Convert uploaded video to HLS format

    Args:
        lesson_part_id: ID of the LessonPart to process

    Returns:
        str: Success message with HLS URL
    """
    try:
        lesson_part = LessonPart.objects.get(id=lesson_part_id)

        if not lesson_part.video:
            logger.error(f"No video file found for LessonPart {lesson_part_id}")
            lesson_part.hls_processing_status = "failed"
            lesson_part.save(update_fields=["hls_processing_status"])
            return f"Failed: No video file for LessonPart {lesson_part_id}"

        # Update status to processing
        lesson_part.hls_processing_status = "processing"
        lesson_part.save(update_fields=["hls_processing_status"])

        # Get the video file path
        video_path = lesson_part.video.path

        # Create HLS output directory
        video_filename = Path(video_path).stem
        hls_dir = (
            Path(settings.MEDIA_ROOT) / "hls_videos" / f"lesson_part_{lesson_part_id}"
        )
        hls_dir.mkdir(parents=True, exist_ok=True)

        # Output file paths
        playlist_path = hls_dir / "playlist.m3u8"
        segment_pattern = str(hls_dir / "segment_%03d.ts")

        # FFmpeg command to convert video to HLS
        # Using adaptive bitrate with multiple quality levels
        ffmpeg_cmd = [
            "ffmpeg",
            "-i",
            video_path,
            "-c:v",
            "libx264",  # Video codec
            "-c:a",
            "aac",  # Audio codec
            "-strict",
            "-2",
            "-hls_time",
            "10",  # Segment duration in seconds
            "-hls_list_size",
            "0",  # Include all segments in playlist
            "-hls_segment_filename",
            segment_pattern,
            "-f",
            "hls",
            str(playlist_path),
        ]

        logger.info(f"Starting HLS conversion for LessonPart {lesson_part_id}")
        logger.info(f"FFmpeg command: {' '.join(ffmpeg_cmd)}")

        # Run FFmpeg
        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            timeout=3600,  # 1 hour timeout
        )

        if result.returncode != 0:
            error_msg = result.stderr.decode("utf-8")
            logger.error(f"FFmpeg error for LessonPart {lesson_part_id}: {error_msg}")
            lesson_part.hls_processing_status = "failed"
            lesson_part.save(update_fields=["hls_processing_status"])
            return f"Failed: FFmpeg error - {error_msg[:200]}"

        # Generate the HLS URL (relative to MEDIA_URL)
        relative_playlist_path = (
            f"hls_videos/lesson_part_{lesson_part_id}/playlist.m3u8"
        )
        hls_url = f"{settings.MEDIA_URL}{relative_playlist_path}"

        # Update lesson part with HLS URL
        lesson_part.hls_video_url = hls_url
        lesson_part.hls_processing_status = "completed"
        lesson_part.save(update_fields=["hls_video_url", "hls_processing_status"])

        logger.info(
            f"Successfully converted video to HLS for LessonPart {lesson_part_id}"
        )
        logger.info(f"HLS URL: {hls_url}")

        return f"Success: HLS conversion completed for LessonPart {lesson_part_id}"

    except LessonPart.DoesNotExist:
        logger.error(f"LessonPart {lesson_part_id} does not exist")
        return f"Failed: LessonPart {lesson_part_id} not found"

    except subprocess.TimeoutExpired:
        logger.error(f"FFmpeg timeout for LessonPart {lesson_part_id}")
        try:
            lesson_part = LessonPart.objects.get(id=lesson_part_id)
            lesson_part.hls_processing_status = "failed"
            lesson_part.save(update_fields=["hls_processing_status"])
        except Exception:
            pass
        # Retry the task
        raise self.retry(exc=subprocess.TimeoutExpired, countdown=300)

    except Exception as e:
        logger.exception(
            f"Unexpected error converting video for LessonPart {lesson_part_id}"
        )
        try:
            lesson_part = LessonPart.objects.get(id=lesson_part_id)
            lesson_part.hls_processing_status = "failed"
            lesson_part.save(update_fields=["hls_processing_status"])
        except Exception:
            pass

        # Retry the task
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))

        return f"Failed: {str(e)}"
