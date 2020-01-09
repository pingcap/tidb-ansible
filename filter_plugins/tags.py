#!/usr/bin/env python

import time
import copy
import json
import operator as py_operator
from distutils.version import LooseVersion, StrictVersion

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

def ansible_version_compare(d, version, operator, strict=False):
    op_map = {
        '==': 'eq', '=': 'eq', 'eq': 'eq',
        '<': 'lt', 'lt': 'lt',
        '<=': 'le', 'le': 'le',
        '>': 'gt', 'gt': 'gt',
        '>=': 'ge', 'ge': 'ge',
        '!=': 'ne', '<>': 'ne', 'ne': 'ne'
    }
    if strict:
        Version = StrictVersion
    else:
        Version = LooseVersion

    if operator in op_map:
        operator = op_map[operator]
    else:
        print 'Invalid operator type'
        raise

    try:
        method = getattr(py_operator, operator)
        return method(Version(str(d)), Version(str(version)))
    except Exception as e:
        print 'Version comparison: {}'.format(e)
        raise

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
            'ansible_version_compare': ansible_version_compare,
            'dictsort_by_value_type': dictsort_by_value_type,
            'tikv_server_labels_format': tikv_server_labels_format,
        }
