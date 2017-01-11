
import time

from ansible import errors

def epoch_time_diff(t):
    return int(int(t) - time.time())


class FilterModule(object):
    def filters(self):
        return {
            'epoch_time_diff' : epoch_time_diff

#            'escape_domain2': lambda content: content.replace('\\', '%5c')
        }
