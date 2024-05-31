from celery import Celery
from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import sessionmaker
import datetime
from src.config import settings
from celery.schedules import crontab
from src.models.friends_model import Invite

celery_app = Celery("tasks", broker="redis://localhost:6379/0")

# will ne changed


engine = create_engine(settings.db_settings.sync_url)
Session = sessionmaker(bind=engine)


@celery_app.task
def print_message():
    with Session() as ses:
        stmt = (
            delete(Invite)
            .where(Invite.expire_at != None)
            .where(datetime.datetime.utcnow() > Invite.expire_at)
        )
        ses.execute(stmt)
        ses.commit()


celery_app.conf.beat_schedule = {
    "run-every-thirty-seconds": {
        "task": "src.services.tasks.print_message",
        "schedule": 30.0,
    }
}
