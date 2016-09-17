import re

__last_page = None


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

    pagesize = args.get('per_page', None)
    page = args.get('page', None)

    return page, pagesize, sortargs


def get_documents(collection, args, collums=dict):
    page, pagesize, sort = parse_url_parameters(args)
    links = None

    if page is None or pagesize is None:
        query = collection.find({}, collums).sort(sort[0], int(sort[1]))
    else:
        query = collection.find({}, collums).skip(pagesize * (page - 1)).limit(pagesize)\
                                            .sort(sort[0], int(sort[1]))
        links = {
            'pagination': {
                'total': collection.count(),
                'per_page': pagesize,
                'current_page': page,
                'last_page': __last_page,
                'from': (pagesize * (page - 1) + 1),
                'to': (pagesize * (page - 1) + pagesize)
            }
        }
        global __last_page
        __last_page = page

    return query, links
