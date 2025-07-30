from .base import SerializerBase


class Dyna(SerializerBase):

    def _dump_file(self, obj, file, kwargs):
        prefix = kwargs.get('prefix')
        if prefix:
            obj = {f'{prefix}_{k}': v for k, v in obj.items()}
        file.write('\n'.join(f'{k}="{repr(v)}"' for k, v in obj.items()))


dyna = Dyna()
