from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Level, Lesson, UserProgress
from .serializers import (
    BookmarkSerializer,
    LevelSerializer, 
    LessonSerializer, 
    UserProgressSerializer,
    UserLevelProgressSerializer
)
from django.contrib.auth import get_user_model

User = get_user_model()

class LevelListView(generics.ListAPIView):
    """List active levels with unlock status"""
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = LevelSerializer
    queryset = Level.objects.filter(is_active=True).order_by('order_index')
    
    def get_serializer_context(self):
        return {'request': self.request}

class LevelDetailView(generics.RetrieveAPIView):
    """Retrieve single level details"""
    serializer_class = LevelSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        return Level.objects.filter(is_active=True)
    
    def get_serializer_context(self):
        return {'request': self.request}

class LevelLessonsView(generics.ListAPIView):
    """List lessons for a specific level"""
    serializer_class = LessonSerializer
    
    def get_queryset(self):
        level_id = self.kwargs['id']
        return Lesson.objects.filter(
            level__id=level_id
        ).order_by('order_index')
    
    def get_serializer_context(self):
        return {'request': self.request}

class LessonDetailView(generics.RetrieveAPIView):
    """Retrieve lesson details with user progress"""
    serializer_class = LessonSerializer
    lookup_field = 'id'
    queryset = Lesson.objects.all()
    
    def get_serializer_context(self):
        return {'request': self.request}

class UserProgressView(generics.UpdateAPIView, generics.CreateAPIView):
    """Create or update user progress for a lesson"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProgressSerializer
    lookup_field = 'lesson_id'

    def get_object(self):
        lesson_id = self.kwargs['lesson_id']
        user = self.request.user
        
        obj, created = UserProgress.objects.get_or_create(
            user=user,
            lesson_id=lesson_id
        )
        return obj
    
    def perform_update(self, serializer):
        # Automatically set completion timestamp
        if serializer.validated_data.get('is_completed', False):
            serializer.save(completed_at=timezone.now())
        else:
            serializer.save()
    
    def create(self, request, *args, **kwargs):
        # Use update logic since we're upserting
        return self.update(request, *args, **kwargs)

class UserProgressSummaryView(generics.ListAPIView):
    """Get user's progress summary across all levels"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserLevelProgressSerializer
    
    def get_queryset(self):
        user = self.request.user
        levels = Level.objects.filter(is_active=True)
        progress_data = []
        
        for level in levels:
            total_lessons = level.lessons.count()
            completed = UserProgress.objects.filter(
                user=user,
                lesson__level=level,
                is_completed=True
            ).count()
            percentage = int((completed / total_lessons) * 100) if total_lessons else 0
            
            progress_data.append({
                'level_id': level.id,
                'completed': completed,
                'total': total_lessons,
                'percentage': percentage
            })
        
        return progress_data
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class NextLessonView(generics.RetrieveAPIView):
    """Get user's next recommended lesson"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LevelSerializer
    def get(self, request, *args, **kwargs):
        user = request.user
        next_lesson = self.get_next_lesson(user)
        
        if not next_lesson:
            return Response(
                {"detail": "All lessons completed"}, 
                status=status.HTTP_204_NO_CONTENT
            )
            
        serializer = LessonSerializer(next_lesson, context={'request': request})
        return Response(serializer.data)
    
    def get_next_lesson(self, user):
        # 1. Check last accessed incomplete lesson
        last_accessed = UserProgress.objects.filter(
            user=user,
            is_completed=False
        ).order_by('-last_accessed').first()
        
        if last_accessed:
            return last_accessed.lesson
        
        # 2. Find first uncompleted lesson in first unlocked level
        for level in Level.objects.filter(is_active=True).order_by('order_index'):
            if not level.is_level_unlocked(user):
                continue
                
            lesson = level.lessons.exclude(
                userprogress__user=user,
                userprogress__is_completed=True
            ).order_by('order_index').first()
            
            if lesson:
                return lesson
        
        return None

class BookmarkedLessonsView(generics.ListAPIView):
    serializer_class = BookmarkSerializer
    
    def get_queryset(self):
        bookmarked_lessons = Lesson.objects.filter(
                userprogress__user=self.request.user,
                userprogress__bookmarked=True
            ).order_by('level__order_index', 'order_index')
        return bookmarked_lessons

    def get_serializer_context(self):
        return {'request': self.request}
