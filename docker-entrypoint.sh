#!/bin/sh

# Wait for PostgreSQL using netcat
until nc -z -v -w5 $POSTGRES_HOST 5432; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

# Collect static files
echo "Collect static files"
uv run manage.py collectstatic --noinput

# Apply database migrations
# echo "Checking database for new migrations"
# uv run manage.py makemigrations 

# Apply database migrations
echo "Apply database migrations"
uv run manage.py migrate 

# Populate Database
# echo "Populating database"
# uv run manage.py populate_db 

# Run Server
if [ $GUNICORN -eq 0 ]; then 
    # Start Debug Server
    echo "Starting Development server"
    uv run manage.py runserver 0.0.0.0:8000
fi

if [ $GUNICORN -eq 1 ]; then 
    # Start Debug Server
    echo "Starting Production server"
    uv run -m gunicorn SeekerOfLight.wsgi:application --bind 0.0.0.0:8000
fi