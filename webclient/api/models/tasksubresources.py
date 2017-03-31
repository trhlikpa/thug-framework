from bson import ObjectId

from webclient.dbcontext import db


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
