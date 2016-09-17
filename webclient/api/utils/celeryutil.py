import datetime
import dateutil.parser
from bson import ObjectId
from crawler.tasks import execute_job
from worker.tasks import analyze_url


def normalize_state(collection, time_limit):
    collection.find({'_state': 'STARTED'}, {'_id': 1, 'start_time': 1, '_state': 1})

    for entry in collection:
        if 'start_time' in entry:
            start_time = dateutil.parser.parse(entry['start_time'])
            now_time = datetime.datetime.utcnow()
            limit_time = start_time + datetime.timedelta(seconds=time_limit)
            if now_time > limit_time:
                if collection.name == 'tasks':
                    info = analyze_url.AsyncResult(entry['_id']).info
                elif collection.name == 'jobs':
                    info = execute_job.AsyncResult(entry['_id']).info
                else:
                    return
                entry['_state'] = 'FAILURE'
                entry['error'] = str(info)
                key = entry['_id']
                entry.pop('_id', None)
                collection.update_one({'_id': ObjectId(key)}, {'$set': entry})
