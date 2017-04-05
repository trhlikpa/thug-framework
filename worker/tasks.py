from datetime import datetime
from dateutil import parser
from bson import ObjectId
from worker.dbcontext import db
from worker.celeryapp import celery
from worker.crawler.tasks import crawl
from worker.analyzer.tasks import analyze
from celery.signals import after_task_publish
from ast import literal_eval as make_tuple

celery.autodiscover_tasks(['worker.crawler, worker.analyzer'])


@celery.task(bind=True)
def execute_job(self, data):
    """

    :param self: celery task object
    :param data: job document
    :return: job ID
    """
    submit_time = datetime.utcnow().isoformat()

    job_id = self.request.id
    crawl_id = ObjectId()

    data['_id'] = ObjectId(job_id)
    data['_crawl_id'] = crawl_id
    data['submit_time'] = submit_time

    # id fix for sake of consistency
    if data['schedule_id']:
        data['schedule_id'] = ObjectId(data['schedule_id'])

    db.jobs.insert_one(data)

    eta = None

    if data['eta']:
        eta = parser.parse(data['eta'])

    signatures = []

    # serializing analyze task
    thug_signature = analyze.signature(time_limit=data['thug_time_limit'], eta=eta)
    signatures.append(thug_signature)

    if data['type'] == 'singleurl':
        for sig in signatures:
            task_id = str(ObjectId())
            sig.apply_async(args=[job_id, data['url'], data['submitter_id']], task_id=task_id)
    else:
        crawl.apply_async(args=[job_id, signatures], task_id=str(crawl_id),
                          time_limit=data['crawler_time_limit'], eta=eta)

    return job_id


@after_task_publish.connect(sender='worker.analyzer.tasks.analyze')
def thug_sent_handler(headers=None, body=None, **kwargs):
    """
    Fires when task is published to a worker
    """
    submit_time = datetime.utcnow().isoformat()

    info = headers if 'task' in headers else body

    # parse args
    job_id = ObjectId(make_tuple(info['argsrepr'])[0])
    url = make_tuple(info['argsrepr'])[1]
    submitter_id = make_tuple(info['argsrepr'])[2]

    after_publish_data = {
        '_id': ObjectId(info['id']),
        '_state': 'PENDING',
        '_error': None,
        'url': url,
        'submitter_id': submitter_id,
        'submit_time': submit_time,
        'start_time': None,
        'end_time': None,
        'job_id': job_id,
        'analysis_id': None,
        'geolocation_id': None,
        'classification': None
    }

    db.tasks.insert_one(after_publish_data)
    db.jobs.update_one({'_id': job_id}, {'$push': {'tasks': ObjectId(info['id'])}})


def revoke_job(job_id):
    """
    Revokes job and deletes related database documents

    :param job_id: job ID
    :return: True if successful, False otherwise
    """
    execute_job.AsyncResult(job_id).revoke()
    job = db.jobs.find_one({'_id': ObjectId(job_id)})

    if not job:
        return False

    crawl_id = job['_crawl_id']
    task_ids = job['tasks']

    crawl.AsyncResult(str(crawl_id)).revoke()

    for task_id in task_ids:
        revoke_task(str(task_id))

    job_rm = db.jobs.delete_one({'_id': ObjectId(job_id)})

    if job_rm.deleted_count > 0:
        return True

    return False


def revoke_task(task_id):
    """
    Revokes task and deletes related database documents

    :param task_id: task ID
    :return: True if successful, False otherwise
    """
    analyze.AsyncResult(task_id).revoke()
    task = db.tasks.find_one({'_id': ObjectId(task_id)})

    if not task:
        return False

    job_id = task['job_id']
    analysis_id = task['analysis_id']

    db.jobs.update_one({'_id': job_id}, {'$pull': {'tasks': ObjectId(task_id)}})

    db.connections.delete_many({'analysis_id': analysis_id})
    db.locations.delete_many({'analysis_id': analysis_id})
    db.samples.delete_many({'analysis_id': analysis_id})
    db.exploits.delete_many({'analysis_id': analysis_id})
    db.classifiers.delete_many({'analysis_id': analysis_id})
    db.codes.delete_many({'analysis_id': analysis_id})
    db.behaviors.delete_many({'analysis_id': analysis_id})
    db.certificates.delete_many({'analysis_id': analysis_id})
    db.graphs.delete_many({'analysis_id': analysis_id})
    db.virustotal.delete_many({'analysis_id': analysis_id})
    db.honeyagent.delete_many({'analysis_id': analysis_id})
    db.androguard.delete_many({'analysis_id': analysis_id})
    db.peepdf.delete_many({'analysis_id': analysis_id})

    db.analyses.delete_one({'_id': analysis_id})

    task_rm = db.tasks.delete_one({'_id': ObjectId(task_id)})

    if task_rm.deleted_count > 0:
        return True

    return False
