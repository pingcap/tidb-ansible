#!/usr/bin/env python2

from __future__ import print_function, \
    unicode_literals

import httplib
import ssl
import sys
import urllib2
import base64
import json
import argparse
import socket

ComponentToRegister = ('alertmanager', 'grafana', 'pd', 'prometheus')


class HTTPSClientAuthConnection(httplib.HTTPSConnection):
    def __init__(self, host, key_file=None, cert_file=None, ca_certs=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        httplib.HTTPSConnection.__init__(self, host, key_file=key_file, cert_file=cert_file, timeout=timeout)
        self.ca_certs = ca_certs

    def connect(self):
        httplib.HTTPConnection.connect(self)
        self.sock = ssl.wrap_socket(self.sock, self.key_file, self.cert_file, ca_certs=self.ca_certs)


class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    def __init__(self, key_file, cert_file, ca_certs):
        urllib2.HTTPSHandler.__init__(self)
        self.key_file = key_file
        self.cert_file = cert_file
        self.ca_certs = ca_certs

    def https_open(self, url):
        return self.do_open(HTTPSClientAuthConnection, url, key_file=self.key_file, cert_file=self.cert_file, ca_certs=self.ca_certs)


def req_with_context(url, key_file, cert_file, ca_certs):
    """
    Python2 added context to HTTPSHandler
    """
    context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH, cafile=ca_certs)
    context.load_cert_chain(certfile=cert_file, keyfile=key_file)
    opener = urllib2.build_opener(urllib2.HTTPSHandler(context=context))
    return opener.open(url)


def req_without_context(url, key_file, cert_file, ca_certs):
    """
    Used for python before 2.7.9
    """
    opener = urllib2.build_opener(HTTPSClientAuthHandler(ca_certs=ca_certs, key_file=key_file, cert_file=cert_file))
    return opener.open(url)


def http_request(url, key_file, cert_file, ca_certs):
    if not key_file:
        return urllib2.urlopen(url)
    if sys.version_info.minor < 9:
        req_func = req_without_context
    else:
        req_func = req_with_context
    return req_func(url, key_file, cert_file, ca_certs)


def parse_opts():
    """
    parse_opts parse the input of involved components and pd address.
    """
    parser = argparse.ArgumentParser(description="Parse output.")
    # pd is involved because we need to send http request
    for target in ComponentToRegister:
        parser.add_argument("--{}".format(target),
                            help="the address list of {}".format(target))
    for ssl_arg in ("key_file", "cert_file", "cacert_file"):
        parser.add_argument("--{}".format(ssl_arg),
                            help="path of the ".format(ssl_arg))

    args, unknown = parser.parse_known_args()
    return args


def etcd_write(etcd_url, key, value, key_file, cert_file, cacert_file):
    encoded_key = base64.b64encode(key)
    encoded_value = base64.b64encode(value)
    data = json.dumps({
        "key": encoded_key,
        "value": encoded_value,
    })
    scheme = "https" if key_file else "http"
    req = urllib2.Request(scheme + '://' + etcd_url + '/v3/kv/put',
                          data=data,
                          headers={'Content-Type': 'application/json'})
    try:
        resp = http_request(req, key_file, cert_file, cacert_file)
        data = json.load(resp)
        return data
    except urllib2.HTTPError as error:
        raise error


def parse_address(con):
    """
    con: str for argument like "127.0.0.1:2379/deploy"
    return: Tuple[str, str] like ("127.0.0.1:2379", "/deploy")
    """
    pos = con.find('/')
    return (con[:pos], con[pos:])


def request_topo(comp, topo, etcd_target, key_file, cert_file, cacert_file):
    """
    Sending request to etcd v3, and leave:
    under {pd_target}:
    write: /topology/{comp}: {ip: ip, address: address}

    comp: str for component name, which will be like "tidb"
    topo: str for topology address, like "127.0.0.1:4000"
    pd_target: the place to send etcd request, like "127.0.0.1:2379"
    key_file: TSL key file
    cert_file: TSL cert file
    cacert_file: TSL ca file
    """
    if topo is None:
        # if topo is None, do nothing
        return
    if ',' in topo:
        topo = topo.split(',')[0]
    ip, add = parse_address(topo)
    ip, port = ip.split(':')

    message = json.dumps({
        'ip': ip,
        'binary_path': add,
        'port': int(port),
    })
    etcd_write(etcd_target, "/topology/" + comp, message, key_file, cert_file, cacert_file)


def concat_to_address(ip, port):
    """
    ip: str for address to concat, like "127.0.0.1"
    port: str for port, like "2379"

    return: str like "127.0.0.1:2379"
        return None if ip or port is None
    """
    if ip is None or port is None:
        return None
    return ip.strip() + ":" + port.strip()


if __name__ == '__main__':
    args = parse_opts()
    print(args)

    # parse from args
    pd_address = args.pd
    pd_address_zero, _ = parse_address(pd_address.split(',')[0])

    alertmanager_address = args.alertmanager
    grafana_address = args.grafana
    prometheus_address = args.prometheus

    mapping = {
        'alertmanager': alertmanager_address,
        'grafana': grafana_address,
        'prometheus': prometheus_address,
    }

    for comp in ComponentToRegister:
        if comp == 'pd':
            continue
        request_topo(comp, mapping[comp], pd_address_zero, args.key_file, args.cert_file, args.cacert_file)
