#!/usr/bin/env python2

from __future__ import print_function, \
    unicode_literals

import urllib
import urllib2
import base64
import json
import argparse

ComponentToRegister = ('alertmanager', 'grafana', 'pd', 'prometheus')


def parse_opts():
    """
    parse_opts parse the input of involved components and pd address.
    """
    parser = argparse.ArgumentParser(description="Parse output.")
    # pd is involved because we need to send http request
    for target in ComponentToRegister:
        parser.add_argument("--{}".format(target),
                            help="the address list of {}".format(target))
    args, unknown = parser.parse_known_args()
    return args


def etcd_write(etcd_url, key, value):
    encoded_key = base64.b64encode(key)
    encoded_value = base64.b64encode(value)
    data = json.dumps({
        "key": encoded_key,
        "value": encoded_value,
    })
    req = urllib2.Request('http://' + etcd_url + '/v3/kv/put',
                          data=data,
                          headers={'Content-Type': 'application/json'})
    try:
        resp = urllib2.urlopen(req)
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


def request_topo(comp, topo, etcd_target):
    """
    Sending request to etcd v3, and leave:
    under {pd_target}:
    write: /topology/{comp}: {ip: ip, address: address}

    comp: str for component name, which will be like "tidb"
    topo: str for topology address, like "127.0.0.1:4000"
    pd_target: the place to send etcd request, like "127.0.0.1:2379"
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
    etcd_write(etcd_target, "/topology/" + comp, message)


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
        request_topo(comp, mapping[comp], pd_address_zero)
