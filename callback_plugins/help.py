# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: help
    type: notification
    short_description: print help message
    version_added: historical
    description:
      - This plugin will print help message when tasks fail.
'''

from ansible.plugins.callback import CallbackBase
from ansible import constants as C
import os
import logging

FAIL_LOGFILE = os.path.dirname(C.DEFAULT_LOG_PATH) + "/fail.log"

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
        self.handler = logging.FileHandler(FAIL_LOGFILE)
        self.logger.addHandler(self.handler)

    def print_help_message(self):
        self._display.display("Ask for help:", color=C.COLOR_WARN)
        self._display.display("Contact us: sre@pingcap.com", color=C.COLOR_HIGHLIGHT)
        self._display.display("It seems that you encounter some problems. You can send an email to the above address, attached with the tidb-ansible/inventory.ini and tidb-ansible/log/ansible.log files and the error message, or new issue on https://github.com/pingcap/docs/issues. We'll try our best to help you deploy a TiDB cluster. Thanks. :-)", color=C.COLOR_WARN)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        if not ignore_errors:
            self.print_help_message()
            self.logger.error('[%s]: Ansible FAILED! => playbook: %s; %s; message: %s', result._host.name, self.playbook, result._task, self._dump_results(result._result))

    def v2_runner_on_unreachable(self, result):
        self.print_help_message()
        self.logger.error('[%s]: Ansible UNREACHABLE! => playbook: %s; %s; message: %s', result._host.name, self.playbook, result._task, self._dump_results(result._result))

    def v2_playbook_on_start(self, playbook):
        self.playbook = playbook._file_name
        open(FAIL_LOGFILE, 'w').close()

    def v2_playbook_on_stats(self, stats):
        count = -1
        for count, line in enumerate(open(FAIL_LOGFILE, 'r')):
            pass
        count += 1
        if count > 0:
            self._display.banner("ERROR MESSAGE SUMMARY")
            for count, line in enumerate(open(FAIL_LOGFILE, 'r')):
                self._display.display(line, color=C.COLOR_ERROR)
            self.print_help_message()
        else:
            self._display.display("Congrats! All goes well. :-)", color=C.COLOR_OK)
