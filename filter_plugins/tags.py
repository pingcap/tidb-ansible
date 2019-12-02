#!/usr/bin/env python

import time
import copy
import json

def epoch_time_diff(t):
    return int(int(t) - time.time())

def with_default_dicts(d, *args):
    ret = copy.deepcopy(d) or {}
    for arg in args:
        if arg:
            ret.update([(k, with_default_dicts(ret[k], arg[k]))
                        for k in arg if k in ret and isinstance(ret[k], (dict, type(None)))])
            ret.update([(k, arg[k]) for k in arg if k not in ret])
    return ret

def update_default_dicts(d):
    ret = copy.deepcopy(d) or {}
    if ret:
        ret.update([(k, update_default_dicts(ret[k])) for k in ret if isinstance(ret[k], (dict, type(None)))])
    return ret

def dictsort_by_value_type(d):
    vals = list(d.items())
    return sorted(vals, key=lambda p: (isinstance(p[1], dict), p[0], p[1]))

def tikv_server_labels_format(label_str):
    label_str = str(label_str or '')
    labels = set()
    for tag in set(filter(None, map(lambda s: s.strip(), label_str.split(',')))):
        k = tag.split('=', 1)[0].strip()
        v = tag.split('=', 1)[1].strip()
        assert k, "empty label key"
        assert v, "empty label value"
        labels.add((k, v))

    return "{ %s }" % (', '.join(["%s = %s" % (k, json.dumps(v)) for (k,v) in labels]))

class FilterModule(object):
    def filters(self):
        return {
            'epoch_time_diff': epoch_time_diff,
            'with_default_dicts': with_default_dicts,
            'update_default_dicts': update_default_dicts,
            'dictsort_by_value_type': dictsort_by_value_type,
            'tikv_server_labels_format': tikv_server_labels_format,
        }
