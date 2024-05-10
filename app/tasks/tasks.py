import asyncio
from datetime import datetime, timedelta

from celery import Celery
from celery.schedules import crontab
from sqlalchemy import desc

from app.db.postgres import async_session
from app.model.notification import Notification
from app.model.quizzes import Quiz, Result
from app.model.user import User
from app.сore.config import settings
from sqlalchemy.future import select

celery = Celery('tasks', broker=settings.REDIS_URL)


async def send_notifications():
    async with async_session() as session:
        query = select(User)
        result = await session.execute(query)
        users = result.scalars()

        for user in users:
            subquery = (
                select(Result.created_at, Quiz.frequency_days, Quiz.name)
                .join(Quiz)
                .where(Result.user_uuid == user.uuid)
                .order_by(Result.quiz_uuid, desc(Result.created_at))
                .distinct(Result.quiz_uuid)
            ).subquery()

            results = await session.execute(select(subquery))

            for result in results.mappings():
                last_attempt = result["created_at"]
                quiz_frequency_days = result['frequency_days']

                min_time = quiz_frequency_days * 24 * 60 * 60

                time_since_last_attempt = datetime.utcnow() - last_attempt.replace(tzinfo=None)

                if time_since_last_attempt > timedelta(seconds=min_time):
                    notification_text = f"You have to take the quiz '{result['name']}'!"
                    await create_notification(session, user.uuid, notification_text)


async def create_notification(session, user_uuid, text):
    notification = Notification(
        user_uuid=user_uuid,
        text=text,
        status='sent'
    )
    session.add(notification)
    await session.commit()


@celery.task
def make_notifications():
    asyncio.run(send_notifications())


celery.conf.beat_schedule = {
    'send-notifications-every-minute': {
        'task': 'app.tasks.tasks.make_notifications',
        'schedule': crontab(minute='*'),
    },
}
