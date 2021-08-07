from attrdict import AttrDict
import yaml

def load_config() -> AttrDict:
    file_name = 'Config.yaml'
    with open(file_name) as config_file:
        data = yaml.safe_load(config_file)
    return AttrDict(data)