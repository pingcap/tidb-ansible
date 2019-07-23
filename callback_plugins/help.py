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

import locale
import os
import sys
import io
import logging

from ansible.plugins.callback import CallbackBase, strip_internal_keys
from ansible.module_utils._text import to_bytes, to_text
from ansible.utils.color import stringc
from ansible import constants as C

FAIL_LOGFILE = os.path.dirname(C.DEFAULT_LOG_PATH) + "/fail.log"


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'help'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):

        self._play = None
        self._last_task_banner = None
        self._last_task_name = None
        self._task_type_cache = {}
        super(CallbackModule, self).__init__()

        if not os.path.exists(os.path.dirname(C.DEFAULT_LOG_PATH)):
            os.makedirs(os.path.dirname(C.DEFAULT_LOG_PATH))

        self.logger = logging.getLogger('fail')
        self.logger.setLevel(logging.DEBUG)
        self.handler = logging.FileHandler(FAIL_LOGFILE)
        self.logger.addHandler(self.handler)

    def format_results(self, result):
        messages = '[' + str(result._host.name) + ']: Ansible Failed! => changed=' + \
                   str(result._result['changed']) + '\n'
        for k, v in result._result.iteritems():
            if isinstance(v, list):
                messages += '  ' + str(k) + ':' + '\n'
                for key, value in v[0].iteritems():
                    if 'ansible' not in key and key != 'invocation':
                        messages += '    - ' + str(key) + ': ' + str(value) + '\n'
            elif k != 'changed' and 'ansible' not in k and k != 'invocation' and k != 'exception':
                messages += '  ' + str(k) + ': ' + str(v) + '\n'
        return messages

    def print_help_message(self):
        self._display.display("Ask for help:", color=C.COLOR_WARN)
        self._display.display("Contact us: support@pingcap.com", color=C.COLOR_HIGHLIGHT)
        self._display.display(
            "It seems that you encounter some problems. You can send an email to the above email address, attached with the tidb-ansible/inventory.ini and tidb-ansible/log/ansible.log files and the error message, or new issue on https://github.com/pingcap/tidb-ansible/issues. We'll try our best to help you deploy a TiDB cluster. Thanks. :-)",
            color=C.COLOR_WARN)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        if not ignore_errors:
            messages = self.format_results(result)
            self.logger.error(messages)

    def v2_runner_on_unreachable(self, result):
        # self.print_help_message()
        self.logger.error('[%s]: Ansible UNREACHABLE! =>  changed=%s\n  playbook: %s\n  %s\n  stderr: %s\n',
                          result._host.name, result._result['changed'],
                          self.playbook, result._task, result._result['msg'])

    def v2_playbook_on_start(self, playbook):
        self.playbook = playbook._file_name
        open(FAIL_LOGFILE, 'w').close()

    def v2_playbook_on_stats(self, stats):
        if os.path.isfile(FAIL_LOGFILE):
            count = -1
            with open(FAIL_LOGFILE, 'r') as f:
                for count, line in enumerate(f):
                    pass
                count += 1

            if count > 0:
                self._display.banner("ERROR MESSAGE SUMMARY")
                with io.open(FAIL_LOGFILE, 'r', encoding="utf-8") as f:
                    for _, line in enumerate(f):
                        self._display.display(line.strip('\n'), color=C.COLOR_ERROR)
                    self.print_help_message()
            else:
                self._display.display("Congrats! All goes well. :-)", color=C.COLOR_OK)

