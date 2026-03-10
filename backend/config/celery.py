import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('interview_brush_up')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'daily-recommendation': {
        'task': 'apps.recommend.tasks.generate_daily_recommendations',
        'schedule': crontab(hour=0, minute=0),
    },
    'calculate-similarities': {
        'task': 'apps.recommend.tasks.calculate_similarities',
        'schedule': crontab(hour=0, minute=30),
    },
}
















