from bson import ObjectId
import datetime

from webapp.dbcontext import db, db_fs, fs

def get_location(task_id, location_id):
    """
    Returns location with coresponding code

    :param task_id: task ID
    :param location_id: Location ID
    """

    if not task_id or len(task_id) != 24:
        return None

    task = db.tasks.find_one({'_id': ObjectId(task_id)})

    if not task:
        return None

    analysis = db.analyses.find_one({'_id': ObjectId(task['analysis_id'])})

    if not analysis:
        return None

    location = db['locations'].find_one({'_id': ObjectId(location_id),
                                         'analysis_id': ObjectId(analysis['_id'])})

    location['url'] = db.urls.find_one({'_id': ObjectId(location['url_id'])})['url']

    code_id = location['content_id']
    file = None

    if code_id:
        file = db_fs['fs']['files'].find_one({'_id': ObjectId(code_id)})
        if file:
            file['uploadDate'] = file['uploadDate'].strftime("%B %d, %Y %I:%M %p")
            location['file'] = file
            location['code'] = fs.get(ObjectId(code_id)).read()

    return location


def get_behavior(task_id, behavior_id):
    """
    Returns behaviour with coresponding code

    :param task_id: task ID
    :param behavior_id: Behavior ID
    """

    if not task_id or len(task_id) != 24:
        return None

    task = db.tasks.find_one({'_id': ObjectId(task_id)})

    if not task:
        return None

    analysis = db.analyses.find_one({'_id': ObjectId(task['analysis_id'])})

    if not analysis:
        return None
    
    behavior = db['behaviors'].find_one({'_id': ObjectId(behavior_id), 
                                         'analysis_id': ObjectId(analysis['_id'])})
    code_id = behavior['snippet']
    code = None

    if code_id:
        code = db['codes'].find_one({'tag': str(code_id), 'analysis_id': ObjectId(analysis['_id'])})

    if code:
        behavior.update(code)
        
    return behavior


def get_task_geolocation(task_id):
    """
    Returns geolocation information of task with specified ID

    :param task_id: task ID
    """
    if not task_id or len(task_id) != 24:
        return None

    task = db.tasks.find_one({'_id': ObjectId(task_id)})

    if not task:
        return None

    geolocation = db.geolocation.find_one({'_id': ObjectId(task['geolocation_id'])})

    return geolocation


def get_task_subresource(resource_name, task_id=None):
    """
    Returns subresource of task with specified task_id

    :param task_id: task ID
    :param resource_name: resource name
    """
    if task_id is None:
        resource = db[resource_name].find()
        fixed_resource = append_url(resource)
        return fixed_resource

    if len(task_id) != 24:
        return None

    task = db.tasks.find_one({'_id': ObjectId(task_id)})

    if not task:
        return None

    analysis = db.analyses.find_one({'_id': ObjectId(task['analysis_id'])})

    if not analysis:
        return None

    if resource_name == 'options':
        resource = [analysis]
    else:
        resource = db[resource_name].find({'analysis_id': ObjectId(analysis['_id'])})

    fixed_resource = append_url(resource)

    return fixed_resource


def append_url(resource):
    """
    Replaces url_ids with actual urls

    :param resource: resource to fix
    """
    tmp_dict = list()

    for entry in resource:
        new_entry = dict(entry)

        if entry.get('url_id'):
            url = db.urls.find_one({'_id': ObjectId(entry['url_id'])})
            new_entry['url'] = url['url']

        if entry.get('source_id'):
            url = db.urls.find_one({'_id': ObjectId(entry['source_id'])})
            new_entry['source_url'] = url['url']

        if entry.get('destination_id'):
            url = db.urls.find_one({'_id': ObjectId(entry['destination_id'])})
            new_entry['destination_url'] = url['url']

        tmp_dict.append(new_entry)

    return tmp_dict
