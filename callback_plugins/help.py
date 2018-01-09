# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: help
    type: notification
    short_description: oneline help message output
    version_added: historical
    description:
      - This plugin will print help message when tasks fail.
'''

from ansible.plugins.callback import CallbackBase

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'help'
    CALLBACK_NEEDS_WHITELIST = True

    def runner_on_failed(self, host, res, ignore_errors=False):
        self._display.warning("Ask for help!!!")
