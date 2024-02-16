# Use a base image of Ubuntu
FROM ubuntu:20.04

ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install necessary dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip redis-server postgresql postgresql-contrib tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER postgres

#define database in postgres 
RUN /etc/init.d/postgresql start \
    && psql --command "CREATE DATABASE core;" \
    && psql --command "CREATE USER postgres WITH PASSWORD 'ADMIN';" \
    && psql --command "GRANT ALL PRIVILEGES ON DATABASE core TO postgres;"

USER root
RUN sed -i 's/bind 127.0.0.1/bind 0.0.0.0/' /etc/redis/redis.conf

# Set the working directory in the container
WORKDIR /app

# Copy the requirements files into the container and install dependencies
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt

# Install ping 
RUN apt-get install -y iputils-ping

# Copy the application source code into the container
COPY . /app/

# Expose the port on which the Django server will run (default is 8000)
EXPOSE 8000

COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD [ "/start.sh" ]
