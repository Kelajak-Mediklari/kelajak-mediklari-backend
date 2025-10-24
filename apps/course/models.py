from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField

from apps.common.models import BaseModel
from apps.course.choices import LessonPartType, QuestionType, TestType

User = get_user_model()


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


class Roadmap(BaseModel):
    image = models.ImageField(_("Image"), upload_to="roadmaps/", null=True, blank=True)
    is_active = models.BooleanField(_("Is Active"), default=True)
    subject = models.ForeignKey(
        "course.Subject",
        on_delete=models.CASCADE,
        related_name="roadmaps",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.subject.title

    class Meta:
        verbose_name = _("Roadmap")
        verbose_name_plural = _("Roadmaps")


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
    duration_months = models.IntegerField(_("Duration Months"), default=0)
    price = models.DecimalField(
        _("Price"), max_digits=10, decimal_places=2, null=True, blank=True
    )

    is_unlimited = models.BooleanField(_("Is Unlimited"), default=False)
    is_main_course = models.BooleanField(_("Is Main Course"), default=False)
    is_active = models.BooleanField(_("Is Active"), default=True)
    is_can_pay_with_coin = models.BooleanField(_("Is Can Pay With Coin"), default=False)
    is_can_pay_with_referral = models.BooleanField(_("Is Can Pay With Referral"), default=False)

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
    order = models.PositiveIntegerField(_("Order"), default=1)
    theoretical_pass_ball = models.IntegerField(_("Theoretical Pass Ball"), default=0)
    practical_pass_ball = models.IntegerField(_("Practical Pass Ball"), default=0)
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
    questions_count = models.IntegerField(
        _("Questions Count"),
        default=10,
        help_text="Number of random questions to show to user",
    )
    attached_files = models.ManyToManyField(
        "course.File", related_name="tests", blank=True
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
    content = HTMLField(null=True, blank=True)
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
    instructions = models.TextField(
        _("Instructions"),
        help_text="Special instructions for matching questions or other question types",
        blank=True,
        null=True,
    )
    order = models.IntegerField(_("Order"), default=1)

    # True/False question field
    correct_answer = models.BooleanField(_("Correct Answer"), null=True, blank=True)

    # Book test questions field - JSON array of all questions and answers
    book_questions = models.JSONField(
        _("Book Questions"),
        null=True,
        blank=True,
        default=list,
        help_text="JSON array of book test questions with their answers. Example: [{'questions_count': 10, 'questions': [{'expected_answer': 'A', 'question_number': 1}, {'expected_answer': 'B', 'question_number': 2}]}]",
    )

    # Regular test question fields
    regular_question_type = models.CharField(
        _("Regular Question Type"),
        max_length=50,
        choices=QuestionType.choices,
        null=True,
        blank=True,
        default=QuestionType.TEXT_CHOICE,
    )
    video_url = models.URLField(_("Video URL"), null=True, blank=True)
    question_image = models.ImageField(
        _("Question Image"), upload_to="questions/images/", null=True, blank=True
    )

    is_active = models.BooleanField(_("Is Active"), default=True)

    def __str__(self):
        return f"{self.test.title} - {self.question_text[:50]}..."

    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
        ordering = ["order"]


class MatchingPair(BaseModel):
    question = models.ForeignKey(
        "course.Question",
        on_delete=models.CASCADE,
        related_name="matching_pairs",
        null=True,
        blank=True,
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


# Answer choices for Regular Test Questions
class AnswerChoice(BaseModel):
    question = models.ForeignKey(
        "course.Question",
        on_delete=models.CASCADE,
        related_name="choices",
        null=True,
        blank=True,
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
        unique_together = ["question", "choice_label"]


# User Progress Tracking Models


class UserCourse(BaseModel):
    """Track user's progress in a specific course"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_courses",
        verbose_name=_("User"),
    )
    course = models.ForeignKey(
        "course.Course",
        on_delete=models.CASCADE,
        related_name="user_courses",
        verbose_name=_("Course"),
    )
    progress_percent = models.DecimalField(
        _("Progress Percentage"),
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text=_("Progress percentage from 0.00 to 100.00"),
    )
    is_completed = models.BooleanField(_("Is Completed"), default=False)
    start_date = models.DateTimeField(_("Start Date"), auto_now_add=True)
    finish_date = models.DateTimeField(_("Finish Date"), null=True, blank=True)
    is_expired = models.BooleanField(_("Is Expired"), default=False)

    # Additional tracking fields
    coins_earned = models.IntegerField(_("Coins Earned"), default=0)
    points_earned = models.IntegerField(_("Points Earned"), default=0)

    class Meta:
        verbose_name = _("User Course")
        verbose_name_plural = _("User Courses")
        unique_together = ["user", "course"]
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.user} - {self.course.title} ({self.progress_percent}%)"

    def clean(self):
        """Validate progress percentage"""
        if self.progress_percent < 0 or self.progress_percent > 100:
            raise ValidationError(_("Progress percentage must be between 0 and 100"))

    def update_progress(self):
        """Calculate and update course progress based on completed lessons"""
        total_lessons = self.course.lessons.filter(is_active=True).count()
        if total_lessons == 0:
            self.progress_percent = 0
        else:
            completed_lessons = self.user_lessons.filter(is_completed=True).count()
            self.progress_percent = round((completed_lessons / total_lessons) * 100, 2)

        # Mark course as completed if 100% progress
        if self.progress_percent >= 100 and not self.is_completed:
            self.is_completed = True
            self.finish_date = timezone.now()

        self.save()
        return self.progress_percent

    def sync_user_balance(self):
        """Sync user's actual coin and point balance with course earnings"""
        # Calculate total earned from all completed lesson parts
        total_coins = 0
        total_points = 0

        for user_lesson in self.user_lessons.filter(is_completed=True):
            for user_lesson_part in user_lesson.user_lesson_parts.filter(is_completed=True):
                total_coins += user_lesson_part.lesson_part.award_coin
                total_points += user_lesson_part.lesson_part.award_point

        # Update the user's balance
        current_user_coins = self.user.coin
        current_user_points = self.user.point

        # Calculate difference and update
        coin_diff = total_coins - current_user_coins
        point_diff = total_points - current_user_points

        if coin_diff != 0:
            self.user.add_coins(coin_diff)
        if point_diff != 0:
            self.user.add_points(point_diff)

        # Update course totals
        self.coins_earned = total_coins
        self.points_earned = total_points
        self.save(update_fields=['coins_earned', 'points_earned'])

    def get_next_lesson(self):
        """Get the next uncompleted lesson in the course"""
        completed_lesson_ids = self.user_lessons.filter(is_completed=True).values_list(
            "lesson_id", flat=True
        )

        return (
            self.course.lessons.filter(is_active=True)
            .exclude(id__in=completed_lesson_ids)
            .first()
        )

    @classmethod
    def get_total_earnings_for_user(cls, user):
        """Get total coins and points earned by a user across all courses"""
        from django.db.models import Sum

        total_earnings = cls.objects.filter(
            user=user,
            is_completed=True
        ).aggregate(
            total_coins=Sum('coins_earned'),
            total_points=Sum('points_earned')
        )

        return {
            'total_coins': total_earnings['total_coins'] or 0,
            'total_points': total_earnings['total_points'] or 0
        }


class UserLesson(BaseModel):
    """Track user's progress in a specific lesson"""

    user_course = models.ForeignKey(
        "course.UserCourse",
        on_delete=models.CASCADE,
        related_name="user_lessons",
        verbose_name=_("User Course"),
    )
    lesson = models.ForeignKey(
        "course.Lesson",
        on_delete=models.CASCADE,
        related_name="user_lessons",
        verbose_name=_("Lesson"),
    )
    is_completed = models.BooleanField(_("Is Completed"), default=False)
    completion_date = models.DateTimeField(_("Completion Date"), null=True, blank=True)
    start_date = models.DateTimeField(_("Start Date"), auto_now_add=True)

    # Progress tracking
    progress_percent = models.DecimalField(
        _("Progress Percentage"), max_digits=5, decimal_places=2, default=0.00
    )

    class Meta:
        verbose_name = _("User Lesson")
        verbose_name_plural = _("User Lessons")
        unique_together = ["user_course", "lesson"]
        ordering = ["lesson__id"]

    def __str__(self):
        return f"{self.user_course.user} - {self.lesson.title}"

    def clean(self):
        """Validate that lesson belongs to the same course"""
        if self.lesson.course != self.user_course.course:
            raise ValidationError(
                _("Lesson must belong to the same course as user course")
            )

    def update_progress(self):
        """Calculate and update lesson progress based on completed parts"""
        total_parts = self.lesson.parts.filter(is_active=True).count()
        if total_parts == 0:
            self.progress_percent = 100  # No parts means lesson is complete
        else:
            completed_parts = self.user_lesson_parts.filter(is_completed=True).count()
            self.progress_percent = round((completed_parts / total_parts) * 100, 2)

        # Mark lesson as completed if 100% progress
        if self.progress_percent >= 100 and not self.is_completed:
            self.is_completed = True
            self.completion_date = timezone.now()

            # Update course progress
            self.user_course.update_progress()

        self.save()
        return self.progress_percent

    def get_next_part(self):
        """Get the next uncompleted lesson part"""
        completed_part_ids = self.user_lesson_parts.filter(
            is_completed=True
        ).values_list("lesson_part_id", flat=True)

        return (
            self.lesson.parts.filter(is_active=True)
            .exclude(id__in=completed_part_ids)
            .order_by("order")
            .first()
        )


class UserLessonPart(BaseModel):
    """Track user's progress in a specific lesson part"""

    user_lesson = models.ForeignKey(
        "course.UserLesson",
        on_delete=models.CASCADE,
        related_name="user_lesson_parts",
        verbose_name=_("User Lesson"),
    )
    lesson_part = models.ForeignKey(
        "course.LessonPart",
        on_delete=models.CASCADE,
        related_name="user_lesson_parts",
        verbose_name=_("Lesson Part"),
    )
    is_completed = models.BooleanField(_("Is Completed"), default=False)
    completion_date = models.DateTimeField(_("Completion Date"), null=True, blank=True)
    start_date = models.DateTimeField(_("Start Date"), auto_now_add=True)

    class Meta:
        verbose_name = _("User Lesson Part")
        verbose_name_plural = _("User Lesson Parts")
        unique_together = ["user_lesson", "lesson_part"]
        ordering = ["lesson_part__order"]

    def __str__(self):
        return f"{self.user_lesson.user_course.user} - {self.lesson_part.title}"

    def clean(self):
        """Validate that lesson part belongs to the same lesson"""
        if self.lesson_part.lesson != self.user_lesson.lesson:
            raise ValidationError(
                _("Lesson part must belong to the same lesson as user lesson")
            )

    def mark_completed(self):
        """Mark this lesson part as completed and update related progress"""
        if not self.is_completed:
            self.is_completed = True
            self.completion_date = timezone.now()

            # Award coins and points to user course
            user_course = self.user_lesson.user_course
            user_course.coins_earned += self.lesson_part.award_coin
            user_course.points_earned += self.lesson_part.award_point
            user_course.save()

            # Update user's actual coin and point balance (always, even if 0)
            user = user_course.user
            user.add_coins(self.lesson_part.award_coin)
            user.add_points(self.lesson_part.award_point)

            self.save()

            # Update lesson progress
            self.user_lesson.update_progress()


class UserTest(BaseModel):
    """Track user's test attempts and results"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_tests",
        verbose_name=_("User"),
    )
    test = models.ForeignKey(
        "course.Test",
        on_delete=models.CASCADE,
        related_name="user_tests",
        verbose_name=_("Test"),
    )
    start_date = models.DateTimeField(_("Start Date"), auto_now_add=True)
    finish_date = models.DateTimeField(_("Finish Date"), null=True, blank=True)
    is_passed = models.BooleanField(_("Is Passed"), default=False)

    # Score tracking
    total_questions = models.IntegerField(_("Total Questions"), default=0)
    correct_answers = models.IntegerField(_("Correct Answers"), default=0)

    # Test attempt tracking
    attempt_number = models.IntegerField(_("Attempt Number"), default=1)

    # Status tracking
    is_submitted = models.BooleanField(_("Is Submitted"), default=False)
    is_in_progress = models.BooleanField(_("Is In Progress"), default=True)

    class Meta:
        verbose_name = _("User Test")
        verbose_name_plural = _("User Tests")
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.user} - {self.test.title} - Attempt {self.attempt_number}"

    def calculate_score(self):
        """Calculate test score based on user answers"""
        if self.total_questions == 0:
            score_percent = 0
        else:
            score_percent = round(
                (self.correct_answers / self.total_questions) * 100, 2
            )

        # Determine if test is passed (assuming 70% is passing)
        self.is_passed = score_percent >= 70

        self.save()
        return score_percent

    def submit_test(self):
        """Submit the test and calculate final results"""
        if not self.is_submitted:
            self.is_submitted = True
            self.is_in_progress = False
            self.finish_date = timezone.now()

            # Count correct answers
            self.correct_answers = self.user_answers.filter(is_correct=True).count()
            self.total_questions = self.user_answers.count()

            # Calculate final score
            self.calculate_score()

            self.save()


class UserAnswer(BaseModel):
    """Track user's answers to test questions"""

    user_test = models.ForeignKey(
        "course.UserTest",
        on_delete=models.CASCADE,
        related_name="user_answers",
        verbose_name=_("User Test"),
    )
    question = models.ForeignKey(
        "course.Question",
        on_delete=models.CASCADE,
        related_name="user_answers",
        verbose_name=_("Question"),
    )

    # Different answer types
    selected_choice = models.ForeignKey(
        "course.AnswerChoice",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Selected Choice"),
        help_text=_("For multiple choice questions"),
    )
    boolean_answer = models.BooleanField(
        _("Boolean Answer"),
        null=True,
        blank=True,
        help_text=_("For true/false questions"),
    )
    text_answer = models.TextField(
        _("Text Answer"), null=True, blank=True, help_text=_("For open-ended questions")
    )

    # For matching questions - JSON field to store matching pairs
    matching_answer = models.JSONField(
        _("Matching Answer"),
        null=True,
        blank=True,
        help_text=_("JSON object storing matching pairs for matching questions"),
    )

    # For book test questions
    book_answer = models.JSONField(
        _("Book Answer"),
        null=True,
        blank=True,
        help_text=_("JSON array of answers for book test questions"),
    )

    # Answer metadata
    is_correct = models.BooleanField(_("Is Correct"), default=False)
    answered_at = models.DateTimeField(_("Answered At"), null=True, blank=True)

    class Meta:
        verbose_name = _("User Answer")
        verbose_name_plural = _("User Answers")
        unique_together = ["user_test", "question"]
        ordering = ["question__order"]

    def __str__(self):
        return f"{self.user_test.user} - {self.question.question_text[:50]}..."

    def clean(self):
        """Validate that question belongs to the same test"""
        if self.question.test != self.user_test.test:
            raise ValidationError(
                _("Question must belong to the same test as user test")
            )

    def save(self, *args, **kwargs):
        """Auto-check correctness when saving"""
        skip_check = kwargs.pop("skip_correctness_check", False)
        if not skip_check:
            self.check_correctness()
        super().save(*args, **kwargs)

    def check_correctness(self):
        """Check if the answer is correct based on question type"""
        if self.question.test.type == TestType.TRUE_FALSE:
            self.is_correct = self.boolean_answer == self.question.correct_answer

        elif self.question.test.type == TestType.REGULAR_TEST:
            if self.selected_choice:
                self.is_correct = self.selected_choice.is_correct
            else:
                self.is_correct = False

        elif self.question.test.type == TestType.MATCHING:
            # For matching questions, check if all pairs are correctly matched
            if self.matching_answer and self.question.matching_pairs.exists():
                correct_pairs = {
                    pair.left_item: pair.right_item
                    for pair in self.question.matching_pairs.all()
                }
                self.is_correct = self.matching_answer == correct_pairs
            else:
                self.is_correct = False

        elif self.question.test.type == TestType.BOOK_TEST:
            # For book test, check against book_questions field
            if self.book_answer and self.question.book_questions:
                # Handle new book_questions structure
                if (
                        isinstance(self.question.book_questions, list)
                        and len(self.question.book_questions) > 0
                ):
                    # New structure: [{'questions_count': 10, 'questions': [...]}]
                    book_data = self.question.book_questions[0]
                    if isinstance(book_data, dict) and "questions" in book_data:
                        questions_list = book_data["questions"]
                        correct_count = 0
                        total_questions = len(questions_list)

                        for i, book_question in enumerate(questions_list):
                            if i < len(self.book_answer):
                                user_answer = self.book_answer[i]
                                expected_answer = book_question.get("expected_answer")
                                if user_answer == expected_answer:
                                    correct_count += 1

                        # Consider correct if at least 70% of book questions are correct
                        self.is_correct = (
                            (correct_count / total_questions) >= 0.7
                            if total_questions > 0
                            else False
                        )
                    else:
                        # Fallback for old structure: direct array of questions
                        correct_count = 0
                        total_questions = len(self.question.book_questions)

                        for i, book_question in enumerate(self.question.book_questions):
                            if i < len(self.book_answer):
                                user_answer = self.book_answer[i]
                                expected_answer = book_question.get("expected_answer")
                                if user_answer == expected_answer:
                                    correct_count += 1

                        # Consider correct if at least 70% of book questions are correct
                        self.is_correct = (
                            (correct_count / total_questions) >= 0.7
                            if total_questions > 0
                            else False
                        )
                else:
                    self.is_correct = False
            else:
                self.is_correct = False
