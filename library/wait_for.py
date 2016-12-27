#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2012, Jeroen Hoekx <jeroen@hoekx.be>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

import binascii
import datetime
import math
import re
import select
import socket
import sys
import time

from ansible.module_utils._text import to_native

HAS_PSUTIL = False
try:
    import psutil
    HAS_PSUTIL = True
    # just because we can import it on Linux doesn't mean we will use it
except ImportError:
    pass

ANSIBLE_METADATA = {'status': ['stableinterface'],
                    'supported_by': 'core',
                    'version': '1.0'}

DOCUMENTATION = '''
---
module: wait_for
short_description: Waits for a condition before continuing.
description:
     - You can wait for a set amount of time C(timeout), this is the default if nothing is specified.
     - Waiting for a port to become available is useful for when services
       are not immediately available after their init scripts return
       which is true of certain Java application servers. It is also
       useful when starting guests with the M(virt) module and
       needing to pause until they are ready.
     - This module can also be used to wait for a regex match a string to be present in a file.
     - In 1.6 and later, this module can also be used to wait for a file to be available or
       absent on the filesystem.
     - In 1.8 and later, this module can also be used to wait for active
       connections to be closed before continuing, useful if a node
       is being rotated out of a load balancer pool.
version_added: "0.7"
options:
  host:
    description:
      - A resolvable hostname or IP address to wait for
    required: false
    default: "127.0.0.1"
  timeout:
    description:
      - maximum number of seconds to wait for
    required: false
    default: 300
  connect_timeout:
    description:
      - maximum number of seconds to wait for a connection to happen before closing and retrying
    required: false
    default: 5
  delay:
    description:
      - number of seconds to wait before starting to poll
    required: false
    default: 0
  port:
    description:
      - port number to poll
    required: false
    default: null
  state:
    description:
      - either C(present), C(started), or C(stopped), C(absent), or C(drained)
      - When checking a port C(started) will ensure the port is open, C(stopped) will check that it is closed, C(drained) will check for active connections
      - When checking for a file or a search string C(present) or C(started) will ensure that the file or string is present before continuing, C(absent) will check that file is absent or removed
    choices: [ "present", "started", "stopped", "absent", "drained" ]
    required: False
    default: "started"
  path:
    version_added: "1.4"
    required: false
    default: null
    description:
      - path to a file on the filesytem that must exist before continuing
  search_regex:
    version_added: "1.4"
    required: false
    default: null
    description:
      - Can be used to match a string in either a file or a socket connection. Defaults to a multiline regex.
  exclude_hosts:
    version_added: "1.8"
    required: false
    default: null
    description:
      - list of hosts or IPs to ignore when looking for active TCP connections for C(drained) state
  sleep:
    version_added: "2.3"
    required: false
    default: 1
    description:
      - Number of seconds to sleep between checks, before 2.3 this was hardcoded to 1 second.
notes:
  - The ability to use search_regex with a port connection was added in 1.7.
requirements: []
author:
    - "Jeroen Hoekx (@jhoekx)"
    - "John Jarvis (@jarv)"
    - "Andrii Radyk (@AnderEnder)"
'''

EXAMPLES = '''

# wait 300 seconds for port 8000 to become open on the host, don't start checking for 10 seconds
- wait_for:
    port: 8000
    delay: 10

# wait 300 seconds for port 8000 of any IP to close active connections, don't start checking for 10 seconds
- wait_for:
    host: 0.0.0.0
    port: 8000
    delay: 10
    state: drained

# wait 300 seconds for port 8000 of any IP to close active connections, ignoring connections for specified hosts
- wait_for:
    host: 0.0.0.0
    port: 8000
    state: drained
    exclude_hosts: 10.2.1.2,10.2.1.3

# wait until the file /tmp/foo is present before continuing
- wait_for:
    path: /tmp/foo

# wait until the string "completed" is in the file /tmp/foo before continuing
- wait_for:
    path: /tmp/foo
    search_regex: completed

# wait until the lock file is removed
- wait_for:
    path: /var/lock/file.lock
    state: absent

# wait until the process is finished and pid was destroyed
- wait_for:
    path: /proc/3466/status
    state: absent

# wait 300 seconds for port 22 to become open and contain "OpenSSH", don't assume the inventory_hostname is resolvable
# and don't start checking for 10 seconds
- local_action: wait_for
    port: 22
    host: "{{ ansible_ssh_host | default(inventory_hostname) }}"
    search_regex: OpenSSH
    delay: 10
'''

class TCPConnectionInfo(object):
    """
    This is a generic TCP Connection Info strategy class that relies
    on the psutil module, which is not ideal for targets, but necessary
    for cross platform support.

    A subclass may wish to override some or all of these methods.
      - _get_exclude_ips()
      - get_active_connections()

    All subclasses MUST define platform and distribution (which may be None).
    """
    platform = 'Generic'
    distribution = None

    match_all_ips = {
        socket.AF_INET: '0.0.0.0',
        socket.AF_INET6: '::',
    }
    ipv4_mapped_ipv6_address = {
        'prefix': '::ffff',
        'match_all': '::ffff:0.0.0.0'
    }
    connection_states = {
        '01': 'ESTABLISHED',
        '02': 'SYN_SENT',
        '03': 'SYN_RECV',
        '04': 'FIN_WAIT1',
        '05': 'FIN_WAIT2',
        '06': 'TIME_WAIT',
    }

    def __new__(cls, *args, **kwargs):
        return load_platform_subclass(TCPConnectionInfo, args, kwargs)

    def __init__(self, module):
        self.module = module
        self.ips = _convert_host_to_ip(module.params['host'])
        self.port = int(self.module.params['port'])
        self.exclude_ips = self._get_exclude_ips()
        if not HAS_PSUTIL:
            module.fail_json(msg="psutil module required for wait_for")

    def _get_exclude_ips(self):
        exclude_hosts = self.module.params['exclude_hosts']
        exclude_ips = []
        if exclude_hosts is not None:
            for host in exclude_hosts:
                exclude_ips.extend(_convert_host_to_ip(host))
        return exclude_ips

    def get_active_connections_count(self):
        active_connections = 0
        for p in psutil.process_iter():
            connections = p.get_connections(kind='inet')
            for conn in connections:
                if conn.status not in self.connection_states.values():
                    continue
                (local_ip, local_port) = conn.local_address
                if self.port != local_port:
                    continue
                (remote_ip, remote_port) = conn.remote_address
                if (conn.family, remote_ip) in self.exclude_ips:
                    continue
                if any((
                    (conn.family, local_ip) in self.ips,
                    (conn.family, self.match_all_ips[conn.family]) in self.ips,
                    local_ip.startswith(self.ipv4_mapped_ipv6_address['prefix']) and
                        (conn.family, self.ipv4_mapped_ipv6_address['match_all']) in self.ips,
                )):
                    active_connections += 1
        return active_connections


# ===========================================
# Subclass: Linux

class LinuxTCPConnectionInfo(TCPConnectionInfo):
    """
    This is a TCP Connection Info evaluation strategy class
    that utilizes information from Linux's procfs. While less universal,
    does allow Linux targets to not require an additional library.
    """
    platform = 'Linux'
    distribution = None

    source_file = {
        socket.AF_INET: '/proc/net/tcp',
        socket.AF_INET6: '/proc/net/tcp6'
    }
    match_all_ips = {
        socket.AF_INET: '00000000',
        socket.AF_INET6: '00000000000000000000000000000000',
    }
    ipv4_mapped_ipv6_address = {
        'prefix': '0000000000000000FFFF0000',
        'match_all': '0000000000000000FFFF000000000000'
    }
    local_address_field = 1
    remote_address_field = 2
    connection_state_field = 3

    def __init__(self, module):
        self.module = module
        self.ips = _convert_host_to_hex(module.params['host'])
        self.port = "%0.4X" % int(module.params['port'])
        self.exclude_ips = self._get_exclude_ips()

    def _get_exclude_ips(self):
        exclude_hosts = self.module.params['exclude_hosts']
        exclude_ips = []
        if exclude_hosts is not None:
            for host in exclude_hosts:
                exclude_ips.extend(_convert_host_to_hex(host))
        return exclude_ips

    def get_active_connections_count(self):
        active_connections = 0
        for family in self.source_file.keys():
            f = open(self.source_file[family])
            for tcp_connection in f.readlines():
                tcp_connection = tcp_connection.strip().split()
                if tcp_connection[self.local_address_field] == 'local_address':
                    continue
                if tcp_connection[self.connection_state_field] not in self.connection_states:
                    continue
                (local_ip, local_port) = tcp_connection[self.local_address_field].split(':')
                if self.port != local_port:
                    continue
                (remote_ip, remote_port) = tcp_connection[self.remote_address_field].split(':')
                if (family, remote_ip) in self.exclude_ips:
                    continue
                if any((
                    (family, local_ip) in self.ips,
                    (family, self.match_all_ips[family]) in self.ips,
                    local_ip.startswith(self.ipv4_mapped_ipv6_address['prefix']) and
                        (family, self.ipv4_mapped_ipv6_address['match_all']) in self.ips,
                )):
                    active_connections += 1
            f.close()
        return active_connections


def _convert_host_to_ip(host):
    """
    Perform forward DNS resolution on host, IP will give the same IP

    Args:
        host: String with either hostname, IPv4, or IPv6 address

    Returns:
        List of tuples containing address family and IP
    """
    addrinfo = socket.getaddrinfo(host, 80, 0, 0, socket.SOL_TCP)
    ips = []
    for family, socktype, proto, canonname, sockaddr in addrinfo:
        ip = sockaddr[0]
        ips.append((family, ip))
        if family == socket.AF_INET:
            ips.append((socket.AF_INET6, "::ffff:" + ip))
    return ips

def _convert_host_to_hex(host):
    """
    Convert the provided host to the format in /proc/net/tcp*

    /proc/net/tcp uses little-endian four byte hex for ipv4
    /proc/net/tcp6 uses little-endian per 4B word for ipv6

    Args:
        host: String with either hostname, IPv4, or IPv6 address

    Returns:
        List of tuples containing address family and the
        little-endian converted host
    """
    ips = []
    if host is not None:
        for family, ip in _convert_host_to_ip(host):
            hexip_nf = binascii.b2a_hex(socket.inet_pton(family, ip))
            hexip_hf = ""
            for i in range(0, len(hexip_nf), 8):
                ipgroup_nf = hexip_nf[i:i+8]
                ipgroup_hf = socket.ntohl(int(ipgroup_nf, base=16))
                hexip_hf = "%s%08X" % (hexip_hf, ipgroup_hf)
            ips.append((family, hexip_hf))
    return ips

def _create_connection(host, port, connect_timeout):
    """
    Connect to a 2-tuple (host, port) and return
    the socket object.

    Args:
        2-tuple (host, port) and connection timeout
    Returns:
        Socket object
    """
    if sys.version_info < (2, 6):
        (family, _) = (_convert_host_to_ip(host))[0]
        connect_socket = socket.socket(family, socket.SOCK_STREAM)
        connect_socket.settimeout(connect_timeout)
        connect_socket.connect( (host, port) )
    else:
        connect_socket = socket.create_connection( (host, port), connect_timeout)
    return connect_socket

def _timedelta_total_seconds(timedelta):
    return (
        timedelta.microseconds + 0.0 +
        (timedelta.seconds + timedelta.days * 24 * 3600) * 10 ** 6) / 10 ** 6

def main():

    module = AnsibleModule(
        argument_spec = dict(
            host=dict(default='127.0.0.1'),
            timeout=dict(default=300, type='int'),
            connect_timeout=dict(default=5, type='int'),
            delay=dict(default=0, type='int'),
            port=dict(default=None, type='int'),
            path=dict(default=None, type='path'),
            search_regex=dict(default=None),
            send=dict(default=None, type='str'),
            state=dict(default='started', choices=['started', 'stopped', 'present', 'absent', 'drained']),
            exclude_hosts=dict(default=None, type='list'),
            sleep=dict(default=1, type='int')
        ),
    )

    params = module.params

    host = params['host']
    timeout = params['timeout']
    connect_timeout = params['connect_timeout']
    delay = params['delay']
    port = params['port']
    state = params['state']
    path = params['path']
    search_regex = params['search_regex']
    send = params['send']
    if search_regex is not None:
        compiled_search_re = re.compile(search_regex, re.MULTILINE)
    else:
        compiled_search_re = None

    if port and path:
        module.fail_json(msg="port and path parameter can not both be passed to wait_for")
    if path and state == 'stopped':
        module.fail_json(msg="state=stopped should only be used for checking a port in the wait_for module")
    if path and state == 'drained':
        module.fail_json(msg="state=drained should only be used for checking a port in the wait_for module")
    if params['exclude_hosts'] is not None and state != 'drained':
        module.fail_json(msg="exclude_hosts should only be with state=drained")
    if path and send is not None:
        module.fail_json(msg="send can only be used with port check mode")

    start = datetime.datetime.now()

    if delay:
        time.sleep(delay)

    if not port and not path and state != 'drained':
        time.sleep(timeout)
    elif state in [ 'stopped', 'absent' ]:
        ### first wait for the stop condition
        end = start + datetime.timedelta(seconds=timeout)

        while datetime.datetime.now() < end:
            if path:
                try:
                    f = open(path)
                    f.close()
                except IOError:
                    break
            elif port:
                try:
                    s = _create_connection(host, port, connect_timeout)
                    s.shutdown(socket.SHUT_RDWR)
                    s.close()
                except:
                    break
            # Conditions not yet met, wait and try again
            time.sleep(params['sleep'])
        else:
            elapsed = datetime.datetime.now() - start
            if port:
                module.fail_json(msg="Timeout when waiting for %s:%s to stop." % (host, port), elapsed=elapsed.seconds)
            elif path:
                module.fail_json(msg="Timeout when waiting for %s to be absent." % (path), elapsed=elapsed.seconds)

    elif state in ['started', 'present']:
        ### wait for start condition
        end = start + datetime.timedelta(seconds=timeout)
        while datetime.datetime.now() < end:
            if path:
                try:
                    os.stat(path)
                except OSError:
                    e = get_exception()
                    # If anything except file not present, throw an error
                    if e.errno != 2:
                        elapsed = datetime.datetime.now() - start
                        module.fail_json(msg="Failed to stat %s, %s" % (path, e.strerror), elapsed=elapsed.seconds)
                    # file doesn't exist yet, so continue
                else:
                    # File exists.  Are there additional things to check?
                    if not compiled_search_re:
                        # nope, succeed!
                        break
                    try:
                        f = open(path)
                        try:
                            if re.search(compiled_search_re, f.read()):
                                # String found, success!
                                break
                        finally:
                            f.close()
                    except IOError:
                        pass
            elif port:
                alt_connect_timeout = math.ceil(_timedelta_total_seconds(end - datetime.datetime.now()))
                try:
                    s = _create_connection(host, port, min(connect_timeout, alt_connect_timeout))
                    if send is not None:
                        s.send(send)
                except:
                    # Failed to connect by connect_timeout. wait and try again
                    pass
                else:
                    # Connected -- are there additional conditions?
                    if compiled_search_re:
                        data = ''
                        matched = False
                        while datetime.datetime.now() < end:
                            max_timeout = math.ceil(_timedelta_total_seconds(end - datetime.datetime.now()))
                            (readable, w, e) = select.select([s], [], [], max_timeout)
                            if not readable:
                                # No new data.  Probably means our timeout
                                # expired
                                continue
                            response = s.recv(1024)
                            if not response:
                                # Server shutdown
                                break
                            data += to_native(response, errors='surrogate_or_strict')
                            if re.search(compiled_search_re, data):
                                matched = True
                                break

                        # Shutdown the client socket
                        s.shutdown(socket.SHUT_RDWR)
                        s.close()
                        if matched:
                            # Found our string, success!
                            break
                    else:
                        # Connection established, success!
                        s.shutdown(socket.SHUT_RDWR)
                        s.close()
                        break

            # Conditions not yet met, wait and try again
            time.sleep(params['sleep'])

        else:   # while-else
            # Timeout expired
            elapsed = datetime.datetime.now() - start
            if port:
                if search_regex:
                    module.fail_json(msg="Timeout when waiting for search string %s in %s:%s" % (search_regex, host, port), elapsed=elapsed.seconds)
                else:
                    module.fail_json(msg="Timeout when waiting for %s:%s" % (host, port), elapsed=elapsed.seconds)
            elif path:
                if search_regex:
                    module.fail_json(msg="Timeout when waiting for search string %s in %s" % (search_regex, path), elapsed=elapsed.seconds)
                else:
                    module.fail_json(msg="Timeout when waiting for file %s" % (path), elapsed=elapsed.seconds)

    elif state == 'drained':
        ### wait until all active connections are gone
        end = start + datetime.timedelta(seconds=timeout)
        tcpconns = TCPConnectionInfo(module)
        while datetime.datetime.now() < end:
            try:
                if tcpconns.get_active_connections_count() == 0:
                    break
            except IOError:
                pass
            # Conditions not yet met, wait and try again
            time.sleep(params['sleep'])
        else:
            elapsed = datetime.datetime.now() - start
            module.fail_json(msg="Timeout when waiting for %s:%s to drain" % (host, port), elapsed=elapsed.seconds)

    elapsed = datetime.datetime.now() - start
    module.exit_json(state=state, port=port, search_regex=search_regex, path=path, elapsed=elapsed.seconds)

# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
