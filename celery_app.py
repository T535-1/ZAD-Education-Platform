
import os
from celery import Celery

# --- Celery Configuration ---

# The REDIS_URL is the connection string for your Redis server.
# This will be passed in as an environment variable in a Docker environment.
# Example: "redis://localhost:6379/0"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create the Celery app instance
# The first argument is the name of the current module.
# The 'broker' is the message broker (Redis) that Celery uses to send and receive messages.
# The 'backend' is where Celery stores the results of tasks.
celery_app = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['core.tasks'] # List of modules to import when the worker starts.
)

# --- Celery App Settings ---
celery_app.conf.update(
    task_track_started=True,
    result_expires=3600, # How long to keep task results (in seconds)
    broker_connection_retry_on_startup=True,
)

# To run a Celery worker for this app, you would use the command:
# celery -A core.celery_app.celery_app worker --loglevel=info
