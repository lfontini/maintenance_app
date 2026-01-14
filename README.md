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

## Development Workflow

### Making Changes Locally and Pushing to Repository

1. Make your changes in the local repository

2. Check the status of your changes:
```bash
git status
```

3. Add the files you want to commit:
```bash
git add .
# or for specific files
git add path/to/file
```

4. Commit your changes:
```bash
git commit -m "Description of your changes"
```

5. Push to the remote repository:
```bash
git push origin main
```

### Updating the Server with Latest Changes

On the server, pull the latest changes from the repository:

```bash
# Navigate to the project directory
cd maintenance_app

# Pull the latest changes
git pull origin main

# Rebuild and restart containers to apply changes
docker-compose down
docker-compose up --build -d
```

**Note**: The `-d` flag runs containers in detached mode (background)

### Troubleshooting: Unfinished Merge

If you encounter the error `You have not concluded your merge (MERGE_HEAD exists)`, follow these steps:

#### Step 1: Check the current status
```bash
git status
```

#### Step 2: Choose your approach

**Option A - Keep BOTH local and remote changes (recommended):**

If there are NO conflicts:
```bash
# Add all changes
git add .

# Commit the merge
git commit -m "Merge remote changes"

# Pull again to ensure you're up to date
git pull origin main

# Rebuild containers
docker-compose down
docker-compose up --build -d
```

If there ARE conflicts:
```bash
# Check which files have conflicts
git status

# Open each conflicting file and resolve the conflicts manually
# Look for markers like <<<<<<< HEAD, =======, and >>>>>>>

# After resolving conflicts, add the files
git add .

# Commit the merge
git commit -m "Resolved merge conflicts"

# Pull again to ensure you're up to date
git pull origin main

# Rebuild containers
docker-compose down
docker-compose up --build -d
```

**Option B - Discard ALL local changes (⚠️ use with caution):**
```bash
# Abort the current merge
git merge --abort

# Discard all local changes and match remote exactly
git reset --hard origin/main

# Pull the latest changes
git pull origin main

# Rebuild containers
docker-compose down
docker-compose up --build -d
```

**Option C - Save local changes for later (stash):**
```bash
# Abort the current merge
git merge --abort

# Save your local changes
git stash

# Pull the latest changes
git pull origin main

# Reapply your local changes (may cause conflicts)
git stash pop

# If conflicts occur, resolve them and commit
git add .
git commit -m "Applied stashed changes after pull"

# Rebuild containers
docker-compose down
docker-compose up --build -d
```