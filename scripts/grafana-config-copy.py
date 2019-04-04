#!/usr/bin/env python2

from __future__ import print_function, \
    unicode_literals

import urllib
import urllib2
import base64
import json
# from pprint import pprint

try:
    input = raw_input
except:
    pass

############################################################
################## CONFIGURATION ###########################
############################################################

# use a viewer key
dests = [
]

if not dests:
    with open("./dests.json") as fp:
        dests = json.load(fp)

method = dests[0]['method']

if method == "pull":
    src = dict(
        dashboards={"node": 'node.json',
                    "pd"  : 'pd.json',
                    "tidb": 'tidb.json',
                    "tikv": 'tikv_pull.json',
                    "tikv_suammry": 'tikv_pull_summary.json',
                    "tikv_details": 'tikv_pull_details.json',
                    "tikv_trouble_shot": 'tikv_pull_trouble_shot.json',
                    "binlog": "binlog.json",
                    "overview": 'overview.json',
                    "disk_performance": 'disk_performance.json',
                    "blackbox_exporter": "blackbox_exporter.json",
                    "kafka_overview": "kafka.json",
                    "lightning": "lightning.json"})
else:
    src = dict(
        dashboards={"node": 'node.json',
                    "pd"  : 'pd.json',
                    "tidb": 'tidb.json',
                    "tikv": 'tikv_push.json',
                    "tikv_suammry": 'tikv_pull_summary.json',
                    "tikv_details": 'tikv_pull_details.json',
                    "tikv_touble_shot": 'tikv_pull_trouble_shot.json',
                    "binlog": "binlog.json",
                    "overview": 'overview.json',
                    "disk_performance": 'disk_performance.json',
                    "blackbox_exporter": "blackbox_exporter.json",
                    "kafka_overview": "kafka.json",
                    "lightning": "lightning.json"})

############################################################
################## CONFIGURATION ENDS ######################
############################################################

def export_dashboard(api_url, api_key, dashboard_name):
    req = urllib2.Request(api_url + 'api/dashboards/db/' + dashboard_name,
                          headers={'Authorization': "Bearer {}".format(api_key)})

    resp = urllib2.urlopen(req)
    data = json.load(resp)
    return data['dashboard']


def fill_dashboard_with_dest_config(dashboard, dest, type_='node'):
    dashboard['title'] = dest['titles'][type_]
    dashboard['id'] = None
    # pprint(dashboard)
    for row in dashboard['rows']:
        for panel in row['panels']:
            panel['datasource'] = dest['datasource']

    if 'templating' in dashboard:
        for templating in dashboard['templating']['list']:
            if templating['type'] == 'query':
                templating['current'] = {}
                templating['options'] = []
            templating['datasource'] = dest['datasource']

    if 'annotations' in dashboard:
        for annotation in dashboard['annotations']['list']:
            annotation['datasource'] = dest['datasource']

    if 'links' in dashboard:
        for link in dashboard['links']:
            if 'title' in link and link['title'] == 'Report':
                link['icon'] = "doc"
                link['includeVars'] = True
                link['keepTime'] = True
                link['targetBlank'] = True
                link['tooltip'] = "Open a pdf report for the current dashboard"
                link['type'] = "link"
                link['url'] = "{0}api/report/{1}?apitoken={2}".format(dest['report_url'], dest['titles'][type_].lower(), dest['apikey'])

    return dashboard

def import_dashboard(api_url, api_key, dashboard):
    payload = {'dashboard': dashboard,
               'overwrite': True}
    headers = {'Authorization': "Bearer {}".format(api_key),
               'Content-Type': 'application/json'}
    req = urllib2.Request(api_url + 'api/dashboards/db',
                          headers=headers,
                          data=json.dumps(payload))
    try:
        resp = urllib2.urlopen(req)
        data = json.load(resp)
        return data
    except urllib2.HTTPError, error:
        data = json.load(error)
        return data

def import_dashboard_via_user_pass(api_url, user, password, dashboard):
    payload = {'dashboard': dashboard,
               'overwrite': True}
    auth_string = base64.b64encode('%s:%s' % (user, password))
    headers = {'Authorization': "Basic {}".format(auth_string),
               'Content-Type': 'application/json'}
    req = urllib2.Request(api_url + 'api/dashboards/db',
                          headers=headers,
                          data=json.dumps(payload))
    try:
        resp = urllib2.urlopen(req)
        data = json.load(resp)
        return data
    except urllib2.URLError, error:
        return error.reason

if __name__ == '__main__':
    for type_ in src['dashboards']:
        print("[load] from <{}>:{}".format(
          src['dashboards'][type_], type_))

        dashboard = json.load(open(src['dashboards'][type_]))

        for dest in dests:
            dashboard = fill_dashboard_with_dest_config(dashboard, dest, type_)
            print("[import] <{}> to [{}]".format(
                dashboard['title'], dest['name']), end='\t............. ')
            if 'user' in dest:
                ret = import_dashboard_via_user_pass(dest['url'], dest['user'], dest['password'], dashboard)
            else:
                ret = import_dashboard(dest['url'], dest['key'], dashboard)

            if isinstance(ret,dict):
                if ret['status'] != 'success':
                    print('ERROR: ', ret)
                    raise RuntimeError
                else:
                    print(ret['status'])
            else:
                print('ERROR: ', ret)
                raise RuntimeError
