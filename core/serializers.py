from rest_framework import serializers
from .models import Level, Lesson, UserProgress
from django.contrib.auth import get_user_model

User = get_user_model()

class LevelSerializer(serializers.ModelSerializer):
    is_unlocked = serializers.SerializerMethodField()
    
    class Meta:
        model = Level
        fields = ['id', 'title', 'description', 'order_index', 'is_active', 'unlock_threshold', 'is_unlocked']
    
    def get_is_unlocked(self, obj)-> bool :
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_level_unlocked(request.user)
        return False

class LessonSerializer(serializers.ModelSerializer):
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'content', 'content_type', 
            'duration', 'order_index', 'video', 'user_progress'
        ]
    
    def get_user_progress(self, obj)-> int:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = UserProgress.objects.get(
                    user=request.user, 
                    lesson=obj
                )
                return UserProgressSerializer(progress).data
            except UserProgress.DoesNotExist:
                return None
        return None

class UserProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProgress
        fields = [
            'is_completed', 'completed_at', 
            'last_accessed', 'bookmarked' #, 'progress_percentage'
        ]
        read_only_fields = ['completed_at', 'last_accessed']

class UserLevelProgressSerializer(serializers.Serializer):
    level_id = serializers.IntegerField()
    completed = serializers.IntegerField()
    total = serializers.IntegerField()
    percentage = serializers.IntegerField()

class BookmarkSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'order_index']
