from django.urls import path
from .views import *

urlpatterns = [
    # Level endpoints
    path('levels/', LevelListView.as_view(), name='level-list'),
    path('levels/<int:id>/', LevelDetailView.as_view(), name='level-detail'),
    path('levels/<int:id>/lessons/', LevelLessonsView.as_view(), name='level-lessons'),
    
    # Lesson endpoints
    path('lessons/<int:id>/', LessonDetailView.as_view(), name='lesson-detail'),
    
    # Progress tracking
    path('progress/<int:lesson_id>/', UserProgressView.as_view(), 
         name='progress-update'),
    path('progress/summary/', UserProgressSummaryView.as_view(), 
         name='progress-summary'),
    path('progress/next/', NextLessonView.as_view(), 
         name='next-lesson'),
    
    # Additional utility endpoints
    path('bookmarks/', BookmarkedLessonsView.as_view(), 
         name='bookmarked-lessons'),
]