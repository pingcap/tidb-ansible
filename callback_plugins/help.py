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

import os
import io
import logging
import yaml

from ansible.plugins.callback import CallbackBase, strip_internal_keys
from ansible.parsing.yaml.dumper import AnsibleDumper
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

    def _format_results(self, result, indent=None, sort_keys=True, keep_invocation=False):
        # All result keys stating with _ansible_ are internal, so remove them from the result before we output anything.
        abridged_result = strip_internal_keys(result._result)

        # remove invocation unless specifically wanting it
        if not keep_invocation and self._display.verbosity < 3 and 'invocation' in abridged_result:
            del abridged_result['invocation']

        # remove diff information from screen output
        if self._display.verbosity < 3 and 'diff' in abridged_result:
            del abridged_result['diff']

        if 'access_control_allow_headers' in abridged_result:
            del abridged_result['access_control_allow_headers']

        if 'access_control_allow_methods' in abridged_result:
            del abridged_result['access_control_allow_methods']

        if 'access_control_allow_origin' in abridged_result:
            del abridged_result['access_control_allow_origin']

        if 'x_content_type_options' in abridged_result:
            del abridged_result['x_content_type_options']

        # remove exception from screen output
        if 'exception' in abridged_result:
            del abridged_result['exception']

        dumped = ''

        dumpd_tile = '[' + str(result._host.name) + ']: Ansible Failed! ==>\n  '
        # put changed and skipped into a header line
        if 'changed' in abridged_result:
            dumped += 'changed=' + str(abridged_result['changed']).lower() + ' '
            del abridged_result['changed']

        if 'skipped' in abridged_result:
            dumped += 'skipped=' + str(abridged_result['skipped']).lower() + ' '
            del abridged_result['skipped']

        # if we already have stdout, we don't need stdout_lines
        if 'stdout' in abridged_result and 'stdout_lines' in abridged_result:
            abridged_result['stdout_lines'] = '<omitted>'

        if abridged_result:
            dumped += '\n'
            dumped += yaml.dump(abridged_result, width=1000, Dumper=AnsibleDumper, default_flow_style=False)

        # indent by a couple of spaces
        dumped = '\n  '.join(dumped.split('\n')).rstrip()
        return dumpd_tile + dumped + '\n'

    def print_help_message(self):
        self._display.display("Ask TiDB User Group for help:", color=C.COLOR_WARN)
        self._display.display(
            "It seems that you have encountered some problem. Please describe your operation steps and provide error information as much as possible on https://asktug.com (in Chinese) or https://stackoverflow.com/questions/tagged/tidb (in English). We will do our best to help solve your problem. Thanks. :-)",
            color=C.COLOR_WARN)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        if not ignore_errors:
            messages = self._format_results(result)
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

