#!/usr/bin/python
# -*- coding: utf-8 -*-

import binascii
import datetime
import math
import re
import select
import socket
import sys
import time
import os

from ansible.module_utils._text import to_native

def main():
    module = AnsibleModule(
        argument_spec = dict(
            pid=dict(default=None, type='int'),
            pid_file=dict(default=None, type='path'),
            timeout=dict(default=300, type='int'),
            delay=dict(default=0, type='int'),
            thread_name_regex=dict(default=None, type='str'),
            thread_num=dict(default=1, type='int'),
            state=dict(default='present', choices=['present', 'absent']),
            sleep=dict(default=1, type='int')
        ),
    )

    params = module.params

    pid = params['pid']
    pid_file = params['pid_file']
    timeout = params['timeout']
    delay = params['delay']
    thread_name_regex = params['thread_name_regex']
    thread_num = params['thread_num']
    state = params['state']
    sleep = params['sleep']
    if thread_name_regex is not None:
        compiled_search_re = re.compile(thread_name_regex, re.MULTILINE)
    else:
        compiled_search_re = None

    if pid and pid_file:
        module.fail_json(msg="pid and pid_file parameter can not both be passed to wait_for_pid")

    start = datetime.datetime.now()

    if delay:
        time.sleep(delay)

    if not pid and not pid_file:
        time.sleep(timeout)
    elif state == 'absent':
        ### first wait for the stop condition
        end = start + datetime.timedelta(seconds=timeout)

        while datetime.datetime.now() < end:
            try:
                if pid_file:
                    f = open(pid_file)
                    pid = f.read().strip()
                    f.close()
                f = open("/proc/%s/comm' %s pid")
                f.close()
            except IOError:
                break
            except:
                break
            # Conditions not yet met, wait and try again
            time.sleep(params['sleep'])
        else:
            elapsed = datetime.datetime.now() - start
            if pid_file:
                module.fail_json(msg="Timeout when waiting for PID:%s to stop." % (pid_file), elapsed=elapsed.seconds)
            elif pid:
                module.fail_json(msg="Timeout when waiting for PID:%s to be absent." % (pid), elapsed=elapsed.seconds)

    elif state ==  'present':
        ### wait for start condition
        end = start + datetime.timedelta(seconds=timeout)
        while datetime.datetime.now() < end:
            try:
                if pid_file:
                    f = open(pid_file)
                    pid = f.read().strip()
                    f.close()
                f = open('/proc/%s/comm' % pid)
                f.close()
            except (OSError, IOError):
                e = get_exception()
                # If anything except file not present, throw an error
                if e.errno != 2:
                    elapsed = datetime.datetime.now() - start
                    module.fail_json(msg="Failed to stat %s, %s" % (path, e.strerror), elapsed=elapsed.seconds)
            # file doesn't exist yet, so continue
            else:
                # process exists.  Are there additional things to check?
                if not compiled_search_re:
                    # nope, succeed!
                    break
                try:
                    matches = 0
                    for thread in os.listdir('/proc/%s/task' % pid):
                        f = open('/proc/%s/task/%s/comm' % (pid, thread))
                        try:
                            if re.search(compiled_search_re, f.read()):
                                matches += 1
                        finally:
                            f.close()
                    if matches >= thread_num:
                        # found, success!
                        break
                except (OSError, IOError):
                    pass

            # Conditions not yet met, wait and try again
            time.sleep(params['sleep'])

        else:   # while-else
            # Timeout expired
            elapsed = datetime.datetime.now() - start
            if pid_file:
                module.fail_json(msg="Timeout when waiting for PID:%s to stop." % (pid_file), elapsed=elapsed.seconds)
            elif pid:
                module.fail_json(msg="Timeout when waiting for PID:%s to be absent." % (pid), elapsed=elapsed.seconds)

    elapsed = datetime.datetime.now() - start
    module.exit_json(state=state, pid=pid, thread_name_regex=thread_name_regex, pid_file=pid_file, elapsed=elapsed.seconds)

# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
