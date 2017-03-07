import re
import math
import json
from bson import json_util


def parse_url_parameters(args):
    sort = args.get('sort')

    if not sort:
        sort = '_id|1'

    sort_regex = re.compile('\w+\|\w+')

    if not sort_regex.match(sort):
        sort = '_id|1'

    sort_args = sort.split('|')

    if len(sort_args) != 2:
        sort_args[0] = '_id'
        sort_args[1] = '1'

    if sort_args[1] == 'desc':
        sort_args[1] = '-1'
    else:
        sort_args[1] = '1'

    pagesize = args.get('per_page')
    page = args.get('page')

    if not page:
        page = 1

    if not pagesize:
        pagesize = 10

    filter_args = None
    filter_string = args.get('filter')

    if filter_string:
        filter_regex = re.compile('(\w+(\|\w+)+)(\|\|(\w+(\|\w+)+))*')

        if filter_regex.match(filter_string):
            tmp_list = sort.split('||')

            for entry in tmp_list:
                args_list = entry.split('|')

                if len(args_list) < 2:
                    continue

                filter_arg = {
                    'field': args_list[0],
                    'values': args_list[1:]
                }

                if filter_arg['field'] == 'all':
                    return page, pagesize, sort_args, [filter_arg]

                filter_args.append(filter_arg)

    return page, pagesize, sort_args, filter_args


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
    last = math.ceil(float(total or 1) / pagesize)

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
