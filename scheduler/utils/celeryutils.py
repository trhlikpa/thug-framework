from celery.schedules import crontab, schedule
from datetime import timedelta


def create_cron_schedule(cron_dict):
    return crontab(minute=cron_dict.get('minute', '*'),
                   hour=cron_dict.get('hour', '*'),
                   day_of_week=cron_dict.get('day_of_week', '*'),
                   day_of_month=cron_dict.get('day_of_month', '*'),
                   month_of_year=cron_dict.get('month_of_year', '*'))


def create_interval_schedule(interval_dict):
    return schedule(timedelta(minutes=interval_dict.get('minutes', 0),
                              hours=interval_dict.get('hours', 0),
                              days=interval_dict.get('days', 0)))
