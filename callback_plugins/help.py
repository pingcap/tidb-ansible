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
import logging
import socket

HELP_FILE = os.path.dirname(C.DEFAULT_LOG_PATH) + "/fail.log"

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'help'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):

        super(CallbackModule, self).__init__()

        if not os.path.exists(os.path.dirname(C.DEFAULT_LOG_PATH)):
            os.makedirs(os.path.dirname(C.DEFAULT_LOG_PATH))

        self.logger = logging.getLogger('fail')
        self.logger.setLevel(logging.DEBUG)
        self.handler = logging.FileHandler(HELP_FILE)
        self.logger.addHandler(self.handler)
        self.hostname = socket.gethostname()

    def print_help_message(self):
        self._display.display("Ask for help:", color=C.COLOR_WARN)
        self._display.display("sre@pingcap.com", color=C.COLOR_HIGHLIGHT)
        self._display.display("Send an email to the above address, attached with the tidb-ansible/inventory.ini and tidb-ansible/log/ansible.log files and the error message.", color=C.COLOR_WARN)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.print_help_message()
        data = {
            'status': "FAILED",
            'host': self.hostname,
            'ansible_type': "task",
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.name,
            'ansible_task': result._task,
            'ansible_result': self._dump_results(result._result)
        }
        self.logger.error("ansible failed", extra=data)

    def v2_runner_on_unreachable(self, result):
        self.print_help_message()
        data = {
            'status': "UNREACHABLE",
            'host': self.hostname,
            'ansible_type': "task",
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.name,
            'ansible_task': result._task,
            'ansible_result': self._dump_results(result._result)
        }
        self.logger.error("ansible unreachable", extra=data)

    def v2_playbook_on_start(self, playbook):
        self._display.banner("START")
        open(HELP_FILE, 'w').close()

    def v2_playbook_on_stats(self, stats):
        self._display.banner("END")
        count = -1
        for count, line in enumerate(open(HELP_FILE, 'r')):
            pass
        count += 1
        if count > 0:
            for count, line in enumerate(open(HELP_FILE, 'r')):
                self._display.display(line, color=C.COLOR_ERROR)
        self.print_help_message()
