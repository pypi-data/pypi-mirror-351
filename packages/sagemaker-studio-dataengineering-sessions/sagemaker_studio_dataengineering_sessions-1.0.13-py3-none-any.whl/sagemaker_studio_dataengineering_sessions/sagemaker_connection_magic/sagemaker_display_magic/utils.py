import re
import json


def get_canonical_class_name(obj):
    return re.findall(r"'(.*?)'", str(type(obj)))[0]

class JSONWithCommentsDecoder(json.JSONDecoder):
    def __init__(self, **kw):
        super().__init__(**kw)

    def decode(self, s: str):
        s = '\n'.join(l if not l.lstrip().startswith('//') else '' for l in s.split('\n'))
        return super().decode(s)

