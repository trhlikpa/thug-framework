import io
import os
import json

__dir__ = os.path.dirname(os.path.realpath(__file__))
__deafult_filepath = os.path.join(__dir__, './personalities/default.json')


def get_useragent_string(useragent):
    if useragent is None:
        filepath = __deafult_filepath
    else:
        filename = './personalities/' + useragent + '.json'
        filepath = os.path.join(__dir__, filename)
        if not os.path.isfile(filepath):
            filepath = __deafult_filepath

    with io.open(os.path.join(filepath), encoding='utf8') as f:
        personality_file = json.load(f)
        personality = personality_file.get('userAgent', None)
        return personality
