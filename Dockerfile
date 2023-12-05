# Use a base image of Python
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the requirements files into the container and install dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy the application source code into the container
COPY . /app/

# Run Django migrations
RUN python manage.py migrate

# Expose the port on which the Django server will run (default is 8000)
EXPOSE 8000

# Initialize the Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
