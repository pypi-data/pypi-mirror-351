from collections import OrderedDict
from .base import SerializerBase

try:
    from dynaconf.loaders.env_loader import load_from_env
except ImportError as e:
    if "'gitignore_parser'" in e.args[0]:
        pass
    else:
        raise


class Dyna(SerializerBase):

    def _dump_file(self, obj, file, kwargs):
        prefix = kwargs.get('prefix')
        if prefix:
            obj = {f'{prefix}_{k}': v for k, v in obj.items()}
        obj = data_to_dyna(obj)
        file.write('\n'.join(f'{k}="{v}"' for k, v in obj.items()))


dyna = Dyna()


def data_to_dyna(data):
    return {k: repr(v) for k, v in data.items()}


def load_dyna(data=None, prefix=None, **kwargs):
    data = data or OrderedDict()
    kwargs = {**dict(key=None, prefix=prefix or False, silent=True), **kwargs}
    load_from_env(data, **kwargs)
    return data
