import io
from flask import json
from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler

with io.open('../config.json', encoding='utf8') as f:
    config = json.load(f)

scheduler = BackgroundScheduler(timezone=utc)
scheduler.add_jobstore(url=config['MONGODB_URL'], collection='schedules')
