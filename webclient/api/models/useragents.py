import json
import os
import io

__useragents = list()
__dir__ = os.path.dirname(os.path.realpath(__file__))
__personality_dirpath = os.path.join(__dir__, './personalities/')


def create_list():
    for filename in os.listdir(__personality_dirpath):
        if filename.endswith('.json'):
            with io.open(os.path.join(__personality_dirpath, filename), encoding='utf8') as f:
                personality_file = json.load(f)
                name = filename.replace('.json', '')
                useragent = personality_file.get('userAgent', name)

                entry = {
                    'name': name,
                    'useragent': useragent
                }

                __useragents.append(entry)


def get_useragents():
    if not __useragents:
        create_list()

    return json.dumps(__useragents)
