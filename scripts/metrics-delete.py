#!/usr/bin/env python2

from __future__ import print_function, \
    unicode_literals, division

import urllib
import urllib2
import json
from pprint import pprint
from urlparse import urljoin
import time
import re
import calendar
import os

SECOND = 1
MINUTE = 60 * SECOND
HOUR   = 60 * MINUTE
DAY    = 24 * HOUR

PROMETHEUS_URL = "http://127.0.0.1:9090/"
PUSHGATEWAY_URL = "http://127.0.0.1:9091/"
TIMEOUT = 5 * MINUTE
if os.getenv('PROMETHEUS_URL'):
    PROMETHEUS_URL = os.getenv('PROMETHEUS_URL')
if os.getenv('PUSHGATEWAY_URL'):
    PUSHGATEWAY_URL = os.getenv('PUSHGATEWAY_URL')
if os.getenv('TIMEOUT'):
    TIMEOUT = os.getenv('TIMEOUT')

current_ts = time.time()

def query_metadata():
    url = urljoin(PROMETHEUS_URL, '/api/v1/series?match[]=up')
    print(url)
    resp = urllib2.urlopen(url)

    payload = json.load(resp)
    pprint(payload)


def query_all_series():
    url = urljoin(PROMETHEUS_URL, r'/api/v1/query?query={instance=~"[\\S].*"}')
    print(url)
    resp = urllib2.urlopen(url)

    payload = json.load(resp)
    pprint(payload)

    for item in payload['data']['result']:
        name = item['metric']['__name__']
        value_ts = item['value'][0]
        if value_ts - current_ts > 2:
            print(name, time.ctime(value_ts))


def delete_series_by_job_instance(job, instance):
    url = urljoin(PROMETHEUS_URL,
                  r'/api/v1/series?match[]={job="%s",instance="%s"}' %  (job, instance))
    req = urllib2.Request(url)
    req.get_method = lambda : 'DELETE'
    resp = urllib2.urlopen(req)
    payload = json.load(resp)
    pprint(payload)
    return True


def query_out_dated_job_from_pushgateway(timeout):
    html = urllib2.urlopen(PUSHGATEWAY_URL).read()
    pattern = re.compile(
        r'<span class="caret"></span>\s+'
        '<span class="label label-warning">job="(.*?)"</span>\s+'
        '<span class="label label-primary">instance="(.*?)"</span>\s+'
        '.*?last pushed: (.*?)\s+</h4>',
        re.DOTALL
    )
    ret = []
    for job, instance, last_update in pattern.findall(html):
        last_update = last_update.replace('&#43;', '+')
        last_update = last_update.replace('&#45;', '-')
        tz_offset = 0
        # parse TZ offset into seconds
        if not last_update.endswith('+0000 UTC'):
            offset = int(last_update.split()[-2], 10)
            tz_offset += offset % 100 * MINUTE
            tz_offset += offset // 100 * HOUR
        last_update = time.strptime(last_update.split('.')[0], "%Y-%m-%d %H:%M:%S")
        # local
        # update_ts = time.mktime(last_update)
        # gmt
        update_ts = calendar.timegm(last_update) - tz_offset
        diff = abs(current_ts - update_ts)
        print("%s@%s is %s seconds behind." % (job, instance, int(diff)))
        if diff > timeout:
            print("  MARKED as OUTDATED!")
            ret.append((job, instance))
    return ret


def delete_job_from_pushgateway(job, instance):
    url = urljoin(PUSHGATEWAY_URL, '/metrics/job/%s/instance/%s' % (job, instance))
    req = urllib2.Request(url)
    req.get_method = lambda : 'DELETE'

    resp = urllib2.urlopen(req)
    resp.read()


if __name__ == '__main__':
    #query_metadata()
    #query_all_series()
    print('prometheus url: {}'.format(PROMETHEUS_URL))
    print('pushgateway url: {}'.format(PUSHGATEWAY_URL))
    for job, instance in query_out_dated_job_from_pushgateway(timeout=TIMEOUT):
        print("deleting", job, instance)
        delete_job_from_pushgateway(job, instance)
        delete_series_by_job_instance(job, instance)
