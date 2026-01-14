# Maintenance App

Django-based maintenance application with Celery task queue and PostgreSQL database.

## Prerequisites

- Docker
- Docker Compose
- Git

## Installation

1. Clone the repository:
   obs: to clone e private repo you must have a token generated, use settings on github and developer > generate a token, it could me all types

```bash
git clone https://github.com/lfontini/maintenance_app.git
cd maintenance_app
```

1. Create a `.env` file in the project root with the following variables:
```env
# Database
POSTGRES_DB=maintenance_db
POSTGRES_USER=maintenance
POSTGRES_PASSWORD=maintenance
POSTGRES_HOST=db
POSTGRES_PORT=5432                     # port inside container (inter-container communication)
POSTGRES_EXTERNAL_PORT=5434            # port mapped to host

# Django
DJANGO_SECRET_KEY=1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
DJANGO_DEBUG=True

# Redis
REDIS_PORT=6379                        # port inside container
REDIS_EXTERNAL_PORT=6381               # port mapped to host
```

3. Build and start the containers:
```bash
docker-compose up --build
```

The application will be available at `http://localhost:8000`

## Services

- **web**: Django application (port 8000)
- **db**: PostgreSQL database (host port 5434 → container port 5432)
- **redis**: Redis cache (host port 6381 → container port 6379)
- **celery**: Celery worker for background tasks
- **celery-beat**: Celery beat scheduler

## Stopping the Application

```bash
docker-compose down
```

To remove volumes as well:
```bash
docker-compose down -v
```


## Logs

```bash
docker-compose logs -f 
or
docker-compose logs 
```