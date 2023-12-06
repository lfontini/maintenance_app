# Use a base image of Ubuntu
FROM ubuntu:20.04

# Install necessary dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip

# Set the working directory in the container
WORKDIR /app

# Copy the requirements files into the container and install dependencies
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt
# Installlping 
RUN apt-get install -y iputils-ping

# Copy the application source code into the container
COPY . /app/

# Run Django migrations
RUN python3 manage.py migrate

# Expose the port on which the Django server will run (default is 8000)
EXPOSE 8000

# Initialize the Django server
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
