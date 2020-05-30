import json
import jsonpickle

def to_json_recursively(obj, fname, suffix=''):
    s = json.dumps( json.loads( jsonpickle.encode(obj)), indent=4 )

    with open(fname + suffix, 'w') as f:
        f.write( s )

def from_json_recursively(fname, suffix=''):
    with open(fname + suffix, 'r') as f:
        read_obj = jsonpickle.decode(f.read())
    return read_obj

