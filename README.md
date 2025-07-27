# Seeker of Light 🌟

![Project Banner](https://dummyimage.com/800x200/000/35f50a&text=Spiritual+Learning+Platform)

> A structured learning platform for spiritual growth and personal development

## Overview
Seeker of Light is a Django-based learning platform that guides users through structured content levels. Users progress through lessons, track their advancement, and unlock new levels as they gain wisdom. The platform features secure authentication, progress tracking, and a RESTful API for seamless integration.

## Key Features ✨
- **Structured Learning Paths**: Organized levels with unlock thresholds
- **Multi-format Lessons**: Text, video, and interactive quizzes
- **Progress Tracking**: Bookmarking and completion metrics
- **Personalized Recommendations**: Next lesson suggestions
- **Secure Authentication**: JWT & session-based auth with email verification
- **Comprehensive API**: Full OpenAPI 3.0 documentation
- **Responsive Design**: Ready for web and mobile clients

## Technology Stack 💻
**Backend**
- Python 3.10+
- Django 5.2
- Django REST Framework
- PostgreSQL (Production), SQLite (Development)
- JWT Authentication
- drf-spectacular (API docs)

**Frontend** *(Coming Soon)*
- Flutter

## Project Structure 🗂️
```
seeker-of-light/
├── SeekerOfLight/ # Main project config
│ ├── settings.py # Environment-aware config
│ ├── urls.py # API endpoints
│ └── ...
├── core/ # Learning content app
│ ├── models.py # Levels, Lessons, Progress
│ ├── serializers.py # API data formatting
│ ├── views.py # Lesson/Level logic
│ └── ...
├── users/ # Authentication app
│ ├── models.py # Custom User model
│ ├── serializers.py # Auth/form handling
│ ├── views.py # Registration/auth flows
│ └── ...
├── .env.sample # Environment template
├── pyproject.toml # Dependency management
└── ...
```


## Getting Started 🚀

### Prerequisites
- Python 3.10+
- PostgreSQL (for production)
- Redis (optional for caching)

### Installation
```bash
# Clone repository
git clone https://github.com/your-org/seeker-of-light.git
cd seeker-of-light

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.sample .env
nano .env  # Configure your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## Configuration ⚙️
Create .env file with these core settings:

```ini
# Database
DEBUG=True
POSTGRES_DB=seeker
POSTGRES_USER=admin
POSTGRES_PASSWORD=securepassword
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Security
SECRET_KEY=your_django_secret
ALLOWED_HOSTS=localhost,127.0.0.1
```

## API Documentation 📖
Interactive API docs are available at: http://localhost:8000/

### Key Endpoints 🔑

### Authentication & Users
- `POST /accounts/register/` - Register new user (requires email, password, name)
- `POST /accounts/login/` - Obtain JWT access/refresh tokens
- `POST /accounts/refresh/` - Refresh access token using refresh token
- `POST /accounts/confirm_email/{uidb64}/{token}/` - Verify email address
- `PUT /accounts/change_password/` - Change password (authenticated)
- `GET/PUT /accounts/profile/` - View/update user profile
- `POST /accounts/reset_password/` - Initiate password reset
- `POST /accounts/reset_password/confirm/{uidb64}/{token}` - Confirm password reset

### Content & Learning
- `GET /content/levels/` - List all active levels with unlock status
- `GET /content/levels/{id}/` - Get details of a specific level
- `GET /content/levels/{id}/lessons/` - List lessons within a level
- `GET /content/lessons/{id}/` - Get lesson details with user progress
- `GET /content/bookmarks/` - List bookmarked lessons
- `POST/PUT /content/progress/{lesson_id}/` - Create/update lesson progress
- `GET /content/progress/next/` - Get next recommended lesson
- `GET /content/progress/summary/` - Get progress summary across all levels

## Contributing 🤝
We welcome contributions! Please follow these steps:

- Fork the repository

- Create your feature branch (git checkout -b feature/amazing-feature)

- Commit your changes (git commit -m 'Add amazing feature')

- Push to the branch (git push origin feature/amazing-feature)

- Open a pull request

## License 📄
This project is licensed under the MIT License - see the LICENSE.md file for details.

## Seek Wisdom. Embrace Light. ✨

```text

This README includes:
1. Eye-catching header with placeholder banner
2. Clear project description and features
3. Technology stack breakdown
4. Visual project structure
5. Step-by-step installation guide
6. Configuration instructions
7. API documentation section with sample endpoint
8. Contribution guidelines
9. License information

For a complete version, you'd want to:
1. Replace placeholder images with actual screenshots
2. Add real deployment instructions
3. Include environment setup for production
4. Add badges (build status, coverage, etc.)
5. Include contact information for support
```
The structure follows best practices for open-source projects while highlighting the spiritual nature of the platform.