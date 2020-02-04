#!/usr/bin/env python2

from __future__ import print_function, \
    unicode_literals

import urllib
import urllib2
import base64
import json
import argparse

ComponentToRegister = ('alertmanager', 'tidb', 'grafana')


def parse_opts():
    """
    parse_opts parse the input of involved components and pd address.
    """
    parser = argparse.ArgumentParser(description="Parse output.")
    # pd is involved because we need to send http request
    involve = ComponentToRegister + ('pd', )
    for target in involve:
        parser.add_argument("--{}_port".format(target),
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
        data = json.load(error)
        return data


def request_topo(comp, topo, etcd_target):
    """
    Sending request to etcd v3, and leave:
    under {pd_target}:
    write: /topo/{comp}: {topo}

    comp: str for component name, which will be like "tidb"
    topo: str for topology address, like "127.0.0.1:4000"
    pd_target: the place to send etcd request, like "127.0.0.1:2379"
    """
    if topo is None:
        # if topo is None, do nothing
        return
    return etcd_write(etcd_target, comp, topo)


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
    # pd_address = concat_to_address(args.pd_host, args.pd_port)
    # tidb_address = concat_to_address(args.tidb_host, args.tidb_port)
    # alertmanager_address = concat_to_address(args.alertmanager_host,
    #                                          args.alertmanager_port)
    # grafana_address = concat_to_address(args.grafana_host, args.grafana_port)
    pd_address = args.pd
    pd_address_zero = pd_address.split(',')[0]

    tidb_address = args.tidb
    alertmanager_address = args.alertmanager
    grafana_address = args.grafana

    mapping = {
        'tidb': tidb_address,
        'alertmanager': alertmanager_address,
        'grafana': grafana_address,
    }

    for comp in ComponentToRegister:
        request_topo(comp, mapping[comp], pd_address_zero)
