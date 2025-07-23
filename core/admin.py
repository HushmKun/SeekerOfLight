from django.contrib import admin
from .models import Level, Lesson, UserProgress

# Register your models here.


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "order_index", "is_active")
    # list_editable = ("order_index", "is_active")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "level", "order_index", "content_type", "duration")
    list_filter = ("level", "content_type")
    search_fields = ("title", "content")


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "lesson", "is_completed", "last_accessed")
    list_filter = ("is_completed", "lesson__level")
    search_fields = ("user__username", "lesson__title")
    ordering = ('user', 'lesson__level', 'lesson')