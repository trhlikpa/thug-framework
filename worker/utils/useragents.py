import io
import os
import json
import thug


def get_useragent_string(useragent):
    if thug.__configuration_path__ is None:
        return None

    personalities_path = os.path.join(thug.__configuration_path__, "personalities")

    if useragent is None:
        return None

    filename = useragent + '.json'
    path = os.path.join(personalities_path, filename)

    if not os.path.isfile(path):
        return None

    with io.open(os.path.join(path), encoding='utf8') as f:
        personality_file = json.load(f)
        personality = personality_file.get('userAgent')
        return personality
