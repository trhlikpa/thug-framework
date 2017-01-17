import re
import math
import json
from bson import json_util


def parse_url_parameters(args):
    sort = args.get('sort', None)

    if sort is None:
        sort = '_id|1'

    r = re.compile('\w+\|\w+')

    if not r.match(sort):
        sort = '_id|1'

    sortargs = sort.split('|')

    if len(sortargs) != 2:
        sortargs[0] = '_id'
        sortargs[1] = '1'

    if sortargs[1] == 'desc':
        sortargs[1] = '-1'
    else:
        sortargs[1] = '1'

    pagesize = args.get('per_page', None)
    page = args.get('page', None)

    if page is None or page == 0:
        page = 1

    if pagesize is None or pagesize == 0:
        pagesize = 10

    filter_arg = args.get('filter', None)

    if filter_arg is None or filter_arg == '':
        filter_arg = None

    return page, pagesize, sortargs, filter_arg


def get_paged_documents(collection, page, pagesize, sort, filter_fields=None, collums=None):

    if pagesize < 0:
        query = collection.find({}, collums is None if {} else collums)
    else:
        query = collection.find(filter_fields is None if {} else filter_fields, collums is None if {} else collums) \
            .skip(pagesize * (page - 1)) \
            .limit(pagesize).sort(sort[0], int(sort[1]))

    pagesize = abs(pagesize)

    total = collection.count(filter_fields is None if {} else filter_fields)
    count = query.count()
    from_t = (pagesize * (page - 1) + 1)
    to_t = (pagesize * (page - 1) + min(pagesize, count))
    last = math.ceil(total / pagesize)

    if from_t > total:
        from_t = None

    if to_t > total:
        if from_t is None:
            to_t = None
        else:
            to_t = total

    links = {
        'total': total,
        'per_page': pagesize,
        'current_page': page,
        'last_page': last,
        'from': from_t,
        'to': to_t
    }

    json_string = json_util.dumps({'data': query}, default=json_util.default)

    d = json.loads(json_string)
    d.update(links)

    return d
