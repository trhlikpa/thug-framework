import dateutil.parser
from datetime import datetime, timedelta
from webapp.dbcontext import db
from bson import ObjectId


def normalize_task_states():
    """
    Normalizes tasks that exceeded time limit and still have 'STARTED' state

    Happens when:
        - os kills celery task

        - task exceeds hard time limit

        - task is lost
    """
    tasks = db.tasks.find({'_state': 'STARTED'})

    for entry in tasks:
        job = db.jobs.find_one({'_id': entry['job_id']})

        thug_time_limit = job['thug_time_limit'] or 600

        start_time = dateutil.parser.parse(entry['start_time'])
        now_time = datetime.utcnow()
        limit_time = start_time + timedelta(seconds=thug_time_limit)

        if now_time > limit_time:
            entry['_state'] = 'FAILURE'
            entry['classification'] = 'SUSPICIOUS'
            entry['end_time'] = str(now_time.isoformat())
            entry['_error'] = 'Thug was killed by worker. Possibly exceeded thug hard limit.'
            key = entry['_id']
            entry.pop('_id', None)
            db.tasks.update_one({'_id': ObjectId(key)}, {'$set': entry})


def normalize_job_states():
    """
    Normalizes and classifies jobs
    """
    jobs = db.jobs.find({'_state': 'STARTED'})

    normalize_task_states()

    for entry in jobs:
        crawler_time_limit = entry['crawler_time_limit'] or 600

        if not entry['crawler_end_time'] and entry['crawler_start_time']:
            start_time = dateutil.parser.parse(entry['crawler_start_time'])
            now_time = datetime.utcnow()
            limit_time = start_time + timedelta(seconds=crawler_time_limit)

            # Normalizes state when crawling task was killed or lost
            if now_time > limit_time:
                entry['_state'] = 'FAILURE'
                entry['crawler_end_time'] = str(now_time.isoformat())
                entry['end_time'] = str(now_time.isoformat())
                entry['_error'] = 'Crawler was killed by worker. Possibly exceeded crawler hard limit.'
                key = entry['_id']
                entry.pop('_id', None)
                db.jobs.update_one({'_id': ObjectId(key)}, {'$set': entry})
                continue

        tasks = entry['tasks']

        if len(tasks) < 1:
            continue

        state = 'SUCCESSFUL'
        classification = 'CLEAR'
        max_end_time = entry['crawler_end_time']

        # Classifies job after every task finishes
        for task_id in tasks:
            task = db.tasks.find_one({'_id': task_id})

            if task['_state'] not in ['SUCCESSFUL', 'FAILURE']:
                state = 'STARTED'
                break

            if task['classification'] in ['MALICIOUS', 'SUSPICIOUS'] and not classification == 'MALICIOUS':
                classification = task['classification']

            if task['end_time'] > max_end_time:
                max_end_time = task['end_time']

        if state == 'SUCCESSFUL':
            entry['_state'] = state
            entry['classification'] = classification
            entry['end_time'] = max_end_time
            key = entry['_id']
            entry.pop('_id', None)
            db.jobs.update_one({'_id': ObjectId(key)}, {'$set': entry})
