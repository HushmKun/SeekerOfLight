from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Level(models.Model):
    title = models.CharField(
        max_length=100, help_text="Level title (e.g. 'Beginner', 'Intermediate')"
    )
    description = models.TextField(
        blank=True, null=True, help_text="Brief overview of what this level covers"
    )
    order_index = models.PositiveIntegerField(
        unique=True, help_text="Order position (1-based index)"
    )
    is_active = models.BooleanField(
        default=True, help_text="Is this level publicly accessible?"
    )
    unlock_threshold = models.PositiveIntegerField(
        default=0,
        help_text="Minimum completed lessons from previous level to unlock"
    )
    class Meta:
        db_table = "level"
        ordering = ["order_index"]
        verbose_name = "Course Level"
        verbose_name_plural = "Course Levels"

    def __str__(self):
        return f"{self.order_index}. {self.title}"

    def clean(self):
        # Prevent order_index = 0
        if self.order_index < 1:
            raise ValidationError({"order_index": _("Order index must start at 1")})

    def is_level_unlocked(self, user):
        """
        Determine if this level is unlocked for a given user
        based on progress in previous levels
        """
        if self.order_index == 1:
            return True
        
        # Get the previous level
        try:
            prev_level = Level.objects.get(order_index=self.order_index - 1)
        except Level.DoesNotExist:
            return True
        
        # Check if user has met the unlock threshold
        completed_in_prev = UserProgress.objects.filter(
            user=user,
            lesson__level=prev_level,
            is_completed=True
        ).count()
        
        return completed_in_prev >= self.unlock_threshold

class Lesson(models.Model):
    CONTENT_TYPE_CHOICES = [
        ("text", "Text Content"),
        ("video", "Video Lesson"),
        ("quiz", "Interactive Quiz"),
    ]

    level = models.ForeignKey(
        Level,
        on_delete=models.CASCADE,
        related_name="lessons",
        help_text="Parent level for this lesson",
    )
    title = models.CharField(max_length=100, help_text="Lesson title")
    content = models.TextField(help_text="Main content (HTML/text or file reference)")
    duration = models.PositiveIntegerField(
        blank=True, null=True, help_text="Estimated completion time (minutes)"
    )
    order_index = models.PositiveIntegerField(
        help_text="Order within level (1-based index)"
    )
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        default="text",
        help_text="Type of lesson content",
    )
    video = models.URLField(max_length=250, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["level__order_index", "order_index"]
        unique_together = [("level", "order_index")]
        verbose_name = "Course Lesson"
        verbose_name_plural = "Course Lessons"

    def __str__(self):
        return f"{self.level.title} - {self.title}"

    def clean(self):
        # Validate order_index per level
        if self.order_index < 1:
            raise ValidationError({"order_index": _("Order index must start at 1")})

        # Check for duplicate ordering in same level
        if (
            Lesson.objects.filter(level=self.level, order_index=self.order_index)
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError(
                {"order_index": _("This order position already exists in this level")}
            )

class UserProgress(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    bookmarked = models.BooleanField(default=False)

    class Meta:
        unique_together = [("user", "lesson")]
        verbose_name_plural = "User Progress Records"

    def __str__(self):
        status = "Completed" if self.is_completed else "In Progress"
        return f"{self.user.email} - {self.lesson.title} ({status})"
