import io
import json
import os
import datetime
from bson import ObjectId
from worker.celeryapp import celery
from worker.utils.netutils import hostname_to_ip
from worker.dbcontext import db


@celery.task()
def analyze(self, input_data):
    from thugapi import Thug
    from worker.utils.geolocation import query_info

    oid = str(self.request.id)

    db.tasks.update_one({'_id': ObjectId(oid)}, {'$set': {
        '_state': 'STARTED', 'start_time': datetime.datetime.utcnow().isoformat()}}, upsert=True)

    output_data = dict()
    output_data['_state'] = 'FAILURE'

    try:
        ip = hostname_to_ip(input_data['url'])
        geoloc_data = query_info(ip)
        output_data['geolocation'] = geoloc_data.__dict__
    except Exception as error:
        geoloc_data = dict(error=error.message)
        output_data['geolocation'] = geoloc_data

    try:
        thug = Thug(input_data)
        log_path = thug.analyze()
        json_path = os.path.join(log_path, 'analysis/json/analysis.json')

        with io.open(json_path) as result:
            thug_data = json.load(result)
            output_data['_state'] = 'SUCCESS'
            output_data.update(thug_data)
    except Exception as error:
        output_data['_state'] = 'FAILURE'
        output_data['error'] = error.message
    finally:
        output_data['end_time'] = datetime.datetime.utcnow().isoformat()
        db.tasks.update_one({'_id': ObjectId(oid)}, {'$set': output_data})
