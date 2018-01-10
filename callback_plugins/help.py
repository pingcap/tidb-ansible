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

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'help'
    CALLBACK_NEEDS_WHITELIST = True

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self._display.warning("Ask for help: Send an email to sre@pingcap.com, attached with the tidb-ansible/inventory.ini and tidb-ansible/log/ansible.log files and the error message.")

    def v2_runner_on_unreachable(self, result):
        self._display.warning("Ask for help: Send an email to sre@pingcap.com, attached with the tidb-ansible/inventory.ini and tidb-ansible/log/ansible.log files and the error message.")
