from __future__ import print_function, \
    unicode_literals

import urllib2
import base64
import json
import argparse

Components = ('tidb', 'pd')


def parse_opts():
    """
    parse_opts parse the input of involved components and pd address.
    """
    parser = argparse.ArgumentParser(description="Parse output.")
    # pd is involved because we need to send http request
    for target in Components:
        parser.add_argument("--{}".format(target),
                            help="the address list of {}".format(target))
    args, unknown = parser.parse_known_args()
    return args


def etcd_delete(etcd_url, key):
    encoded_key = base64.b64encode(key)
    data = json.dumps({
        "key": encoded_key,
    })
    req = urllib2.Request('http://' + etcd_url + '/v3/kv/deleterange',
                          data=data,
                          headers={'Content-Type': 'application/json'})
    try:
        resp = urllib2.urlopen(req)
        data = json.load(resp)
        return data
    except urllib2.HTTPError as error:
        raise error


def delete_tidb_topo(tidb_list, pd_address):
    try:
        for tidb in tidb_list.split(','):
            # tidb is ip:port
            etcd_delete(pd_address, '/topology/tidb/' + tidb + '/info')
            etcd_delete(pd_address, '/topology/tidb/' + tidb + '/ttl')
        return False
    except:
        return True


if __name__ == '__main__':
    args = parse_opts()

    pd_address = args.pd
    pd_address_zero = pd_address.split(',')[0]

    tidb_list = args.tidb

    for pd in pd_address.split(','):
        if delete_tidb_topo(tidb_list, pd):
            return
