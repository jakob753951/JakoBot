from attrdict import AttrDict
import json

def load_config(file_name: str = 'Config.json') -> AttrDict:
    with open(file_name) as config_file:
        data = json.load(config_file)
    return AttrDict(data)