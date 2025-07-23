import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import Level, Lesson, UserProgress 
import lorem

# Get the custom user model
User = get_user_model()

class Command(BaseCommand):
    """
    A Django management command to populate the database with initial data.
    
    This command clears existing data for User, Level, Lesson, and UserProgress models
    and then creates a new set of sample data. This is useful for development
    and testing purposes to ensure a consistent database state.
    
    Usage:
    python manage.py populate_db
    """
    help = 'Populates the database with initial data for levels, lessons, and users.'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        """
        Main logic for the management command.
        
        Wraps the entire data creation process in a single database transaction.
        If any part of the script fails, all changes will be rolled back.
        """
        self.stdout.write(self.style.WARNING('Clearing existing data...'))
        self._clear_data()
        
        self.stdout.write(self.style.SUCCESS('Creating new data...'))
        self._create_users()
        self._create_levels_and_lessons()
        self._create_user_progress()
        
        self.stdout.write(self.style.SUCCESS('Database populated successfully!'))

    def _clear_data(self):
        """
        Deletes all existing records from User, Level, and UserProgress models.
        Lesson records are deleted via cascading from Level.
        """
        User.objects.all().delete()
        Level.objects.all().delete()
        Lesson.objects.all().delete()
        UserProgress.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Data cleared.'))

    def _create_users(self):
        """
        Creates a set of sample users for the application.
        """
        self.users = [
            User.objects.create_superuser(email='HushmKun@outlook.com', password='password123', first_name="Hussein", last_name="Mukhtar", is_active=True),
            User.objects.create_user(email='alice@example.com', password='password123', first_name="Alice", last_name="Summers", is_active=True),
            User.objects.create_user(email='bob@example.com', password='password123',  first_name="Bob", last_name="Summers", is_active=True),
            User.objects.create_user(email='charlie@example.com', password='password123', first_name="Charlie", last_name="Summers", is_active=True)
        ]
        self.stdout.write(self.style.SUCCESS(f'Created {len(self.users)} users.'))

    def _create_levels_and_lessons(self):
        """
        Defines and creates the course structure including levels and their lessons.
        """
        # --- Level and Lesson Definitions ---
        
        # Level 1: Beginner
        level1 = Level.objects.create(
            title='Beginner',
            description='Start your journey with the fundamentals.',
            order_index=1,
            unlock_threshold=0
        )
        lessons_l1 = [
            {'title': 'Introduction to the Course', 'content':lorem.paragraph(), 'duration': 5, "order_index":1, 'content_type': 'text' },
            {'title': 'Setting Up Your Environment', 'content':lorem.paragraph(), 'duration': 15, "order_index":2, 'content_type': 'video' , 'video': 'http://example.com/video1'},
            {'title': 'Basic Concepts Part 1', 'content':lorem.paragraph(), 'duration': 10, "order_index":3, 'content_type': 'text' },
            {'title': 'Basic Concepts Part 2', 'content':lorem.paragraph(), 'duration': 12, "order_index":4, 'content_type': 'video' ,'video': 'http://example.com/video2'},
            {'title': 'Knowledge Check: Basics', 'content_type': 'quiz', 'duration': 8, "order_index" : 5, 'content':lorem.paragraph()}
        ]

        # Level 2: Intermediate
        level2 = Level.objects.create(
            title='Intermediate',
            description='Build on your foundational knowledge with more advanced topics.',
            order_index=2,
            unlock_threshold=3 # Requires 3 completed lessons from Beginner level
        )
        lessons_l2 = [
            {'title': 'Design Patterns', 'content':lorem.paragraph(), 'duration': 5, "order_index":1, 'content_type': 'text' },
            {'title': 'Software Development Life Cycles', 'content':lorem.paragraph(), 'duration': 15, "order_index":2, 'content_type': 'video' , 'video': 'http://example.com/video1'},
            {'title': 'How to think', 'content':lorem.paragraph(), 'duration': 10, "order_index":3, 'content_type': 'text' },
            {'title': 'Best Practices', 'content':lorem.paragraph(), 'duration': 12, "order_index":4, 'content_type': 'video' ,'video': 'http://example.com/video2'},
            {'title': 'Knowledge Check: Intermediate', 'content_type': 'quiz', 'duration': 8, 'content':lorem.paragraph(), "order_index" : 5}
        ]

        # Level 3: Advanced
        level3 = Level.objects.create(
            title='Advanced',
            description='Master the subject with expert-level insights and complex projects.',
            order_index=3,
            unlock_threshold=2 # Requires 2 completed lessons from Intermediate level
        )
        lessons_l3 = [
            {'title': 'Performance Optimization', 'content':lorem.paragraph(), 'duration': 10, "order_index":3, 'content_type': 'text' },
            {'title': 'Scaling Your Application', 'content':lorem.paragraph(), 'duration': 12, "order_index":4, 'content_type': 'video' ,'video': 'http://example.com/video2'},
            {'title': 'Final Project: Build a Full-Scale App', 'content':lorem.paragraph(), 'content_type': 'quiz', 'duration': 8, "order_index" : 5}
        ]

        # --- Lesson Creation in the Database ---
        
        self.stdout.write('Creating lessons for each level...')
        self.lessons = []

        for i, lesson_data in enumerate(lessons_l1, 1):
            lesson = Lesson.objects.create(
                level=level1,
                title=lesson_data['title'],
                content=lesson_data['content'],
                duration=lesson_data['duration'],
                order_index=i,
                content_type=lesson_data['content_type'],
                video=lesson_data.get('video')
            )
            self.lessons.append(lesson)

        for i, lesson_data in enumerate(lessons_l2, 1):
            lesson = Lesson.objects.create(
                level=level2,
                title=lesson_data['title'],
                content=lesson_data['content'],
                duration=lesson_data['duration'],
                order_index=i,
                content_type=lesson_data['content_type'],
                video=lesson_data.get('video')
            )
            self.lessons.append(lesson)
            
        for i, lesson_data in enumerate(lessons_l3, 1):
            lesson = Lesson.objects.create(
                level=level3,
                title=lesson_data['title'],
                content=lesson_data['content'],
                duration=lesson_data['duration'],
                order_index=i,
                content_type=lesson_data['content_type'],
                video=lesson_data.get('video')
            )
            self.lessons.append(lesson)

        self.stdout.write(self.style.SUCCESS('Levels and lessons created.'))
        
    def _create_user_progress(self):
        """
        Simulates user progress by creating UserProgress records.
        This function ensures that the progress data is realistic enough
        to test level unlocking logic.
        """
        progress_records = []

        # Hussein: A dedicated user who has completed many lessons
        hussein = User.objects.get(email='HushmKun@outlook.com')
        for i, lesson in enumerate(self.lessons):
            if i < 8: # Alice has completed the first 8 lessons
                progress_records.append(UserProgress(
                    user=hussein,
                    lesson=lesson,
                    is_completed=True,
                    completed_at=timezone.now()
                ))
            elif i == 8: # Currently on the 9th lesson
                progress_records.append(UserProgress(user=hussein, lesson=lesson, is_completed=False))

        # Alice: A dedicated user who has completed many lessons
        alice = User.objects.get(email='alice@example.com')
        for i, lesson in enumerate(self.lessons):
            if i < 8: # Alice has completed the first 8 lessons
                progress_records.append(UserProgress(
                    user=alice,
                    lesson=lesson,
                    is_completed=True,
                    completed_at=timezone.now()
                ))
            elif i == 8: # Currently on the 9th lesson
                progress_records.append(UserProgress(user=alice, lesson=lesson, is_completed=False))

        # Bob: A user who has completed the first level
        bob = User.objects.get(email='bob@example.com')
        for i, lesson in enumerate(self.lessons):
            if lesson.level.order_index == 1: # Completed all of level 1
                progress_records.append(UserProgress(
                    user=bob,
                    lesson=lesson,
                    is_completed=True,
                    completed_at=timezone.now()
                ))
            elif i == 5: # Started the first lesson of level 2
                 progress_records.append(UserProgress(user=bob, lesson=lesson, is_completed=False))


        # Charlie: A new user who has only completed a few lessons
        charlie = User.objects.get(email='charlie@example.com')
        for lesson in self.lessons[:2]: # Completed the first two lessons
            progress_records.append(UserProgress(
                user=charlie,
                lesson=lesson,
                is_completed=True,
                completed_at=timezone.now(),
                bookmarked=random.choice([True, False])
            ))
        # Bookmarked the third lesson but hasn't started
        progress_records.append(UserProgress(user=charlie, lesson=self.lessons[2], is_completed=False, bookmarked=True))


        UserProgress.objects.bulk_create(progress_records)
        self.stdout.write(self.style.SUCCESS(f'Created {len(progress_records)} user progress records.'))