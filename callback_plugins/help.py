# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: help
    type: notification
    short_description: oneline help message
    version_added: historical
    description:
      - This plugin will print help message when tasks fail.
'''

from ansible.plugins.callback import CallbackBase
from ansible import constants as C
import os

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'help'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):

        super(CallbackModule, self).__init__()

        if not os.path.exists(os.path.dirname(C.DEFAULT_LOG_PATH)):
            os.makedirs(os.path.dirname(C.DEFAULT_LOG_PATH))
    def print_help_message(self):
        self._display.display("Ask for help:", color=C.COLOR_WARN)
        self._display.display("sre@pingcap.com", color=C.COLOR_HIGHLIGHT)
        self._display.display("Send an email to the above address, attached with the tidb-ansible/inventory.ini and tidb-ansible/log/ansible.log files and the error message.", color=C.COLOR_WARN)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.print_help_message()

    def v2_runner_on_unreachable(self, result):
        self.print_help_message()
