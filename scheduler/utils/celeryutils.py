from celery.schedules import crontab, schedule
from datetime import timedelta


def create_cron_schedule(cron_dict):
    """
    Creates crontab object from dictionary

    :param cron_dict: format:
        {
            'minute': '*',
            'hour': '*',
            'day_of_week': '*',
            'day_of_month': '*',
            'month_of_year': '*'
        }
    :return: celery crontab instance
    """
    return crontab(minute=cron_dict.get('minute', '*'),
                   hour=cron_dict.get('hour', '*'),
                   day_of_week=cron_dict.get('day_of_week', '*'),
                   day_of_month=cron_dict.get('day_of_month', '*'),
                   month_of_year=cron_dict.get('month_of_year', '*'))


def create_interval_schedule(interval_dict):
    """
    Creates schedule object from dictionary

    :param interval_dict: format:
        {
            'minutes': '0',
            'hours': '0',
            'days': '0'
        }
    :return: celery schedule instance
    """
    return schedule(timedelta(minutes=interval_dict.get('minutes', 0),
                              hours=interval_dict.get('hours', 0),
                              days=interval_dict.get('days', 0)))
