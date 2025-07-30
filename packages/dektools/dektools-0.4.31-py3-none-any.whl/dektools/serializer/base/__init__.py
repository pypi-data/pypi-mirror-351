import os
import codecs
from io import BytesIO, StringIO, TextIOBase
from ...file import sure_parent_dir, normal_path

DEFAULT_VALUE = type('default_value', (), {})


class SerializerBase:
    _persist_str = True

    def __init__(self, encoding=None):
        self.encoding = encoding or "utf-8"

    def loads(self, s, encoding=None, **kwargs):
        if self._persist_str:
            if isinstance(s, (bytes, memoryview)):
                s = str(s, encoding or self.encoding)
        else:
            if isinstance(s, str):
                s = s.encode(encoding or self.encoding)
        return self.load(StringIO(s) if self._persist_str else BytesIO(s), **kwargs)

    def load(self, file, encoding=None, default=DEFAULT_VALUE, **kwargs):
        if not hasattr(file, 'read'):
            if not os.path.isfile(file) and default is not DEFAULT_VALUE:
                return default
            if self._persist_str:
                with codecs.open(file, encoding=encoding or self.encoding) as f:
                    return self._load_file(f, kwargs)
            else:
                with open(file, 'rb') as f:
                    return self._load_file(f, kwargs)
        else:
            if self._persist_str and not isinstance(file, TextIOBase):
                file = StringIO(file.read().decode(encoding or self.encoding))
            return self._load_file(file, kwargs)

    def _load_file(self, file, kwargs):
        raise NotImplementedError

    def dumps(self, obj):
        file = StringIO() if self._persist_str else BytesIO()
        self.dump(file, obj)
        return file.getvalue()

    def dump(self, file, obj, encoding=None, **kwargs):
        if not hasattr(file, 'write'):
            file = normal_path(file)
            sure_parent_dir(file)
            if self._persist_str:
                with codecs.open(file, 'w', encoding=encoding or self.encoding) as f:
                    self._dump_file(obj, f, kwargs)
            else:
                with open(file, 'wb') as f:
                    self._dump_file(obj, f, kwargs)
        else:
            self._dump_file(obj, file, kwargs)

    def _dump_file(self, obj, file, kwargs):
        raise NotImplementedError
