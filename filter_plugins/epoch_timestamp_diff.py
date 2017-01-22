
import time
import copy

from ansible import errors

def epoch_time_diff(t):
    return int(int(t) - time.time())

def with_default_dicts(d, *args):
    ret = copy.deepcopy(d) or {}
    for arg in args:
        ret.update({k: with_default_dicts(ret[k], arg[k]) for k in arg if k in ret and isinstance(ret[k], (dict, type(None))) })
        ret.update({k: arg[k] for k in arg if k not in ret})
    return ret

class FilterModule(object):
    def filters(self):
        return {
            'epoch_time_diff': epoch_time_diff,
            'with_default_dicts': with_default_dicts
        }
