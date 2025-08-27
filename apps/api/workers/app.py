import os
from celery import Celery

# Broker and backend default to redis service in docker-compose
broker = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
backend = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

celery_app = Celery("raincheck_workers", broker=broker, backend=backend)
celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
)

@celery_app.task
def ping():
    return "pong"
