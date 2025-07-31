# Use the official Python runtime image
FROM astral/uv:python3.13-alpine
 
# Create the app directory
RUN mkdir /app
 
# Set the working directory inside the container
WORKDIR /app
 
# Set environment variables 
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
#Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1 
 
# Copy the Django project  and install dependencies
COPY uv.lock pyproject.toml  /app/
 
# run this command to install all dependencies 
RUN uv sync 
 
# Copy the Django project to the container
COPY . /app/
 
# Expose the Django port
EXPOSE 8000
 
COPY docker-entrypoint.sh /docker-entrypoint.sh

RUN chmod +x docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["uv", "run", "main.py"]
