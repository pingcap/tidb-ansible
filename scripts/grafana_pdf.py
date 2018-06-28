#!/usr/bin/env python

from __future__ import print_function, \
    unicode_literals

import argparse
import os
import time
import json
import tarfile
import shutil

try:
    # For Python 2
    import urllib2 as urlreq
    from urllib2 import HTTPError, URLError
except ImportError:
    # For Python 3
    import urllib.request as urlreq
    from urllib.error import HTTPError, URLError

dests = []
download_dir = "grafana_pdf"

if not dests:
    with open("./dests.json") as fp:
        dests = json.load(fp)


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def read_url(url):
    try:
        f = urlreq.urlopen(url)
        return f.read()
    except HTTPError as e:
        print("HTTP Error: %s" % e.getcode())
        return e.read()
    except URLError as e:
        print("Reading URL %s error: %s" % (url, e))
        return None


def parse_opts():
    parser = argparse.ArgumentParser(
        description="Export Grafana charts to PDF")
    parser.add_argument("-t", "--time", action="store", default=None,
                        help="Relative time to now, supported format is like: 2h, 4h. If not set, assume 3h by default.")
    parser.add_argument("--time-from", action="store", default=None,
                        help="Start timestamp of time range, format: '%%Y-%%m-%%d %%H:%%M:%%S'.")
    parser.add_argument("--time-to", action="store", default=None,
                        help="End timestamp of time range, format: '%%Y-%%m-%%d %%H:%%M:%%S'.")
    return parser.parse_args()


def parse_timestamp(time_string):
    format_guess = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H",
        "%Y-%m-%d",
        "%m-%d",
        "%H:%M:%S",
        "%H:%M",
        "%H"
    ]
    for time_format in format_guess:
        try:
            # Grafana API's timestamp is in ms
            return time.mktime(time.strptime(time_string, time_format)) * 1000
        except ValueError:
            pass
    raise ValueError(
        "time data '%s' does not match any supported format." % time_string)


if __name__ == '__main__':
    args = parse_opts()
    if not os.path.isdir(download_dir):
        os.makedirs(download_dir)

    if args.time:
        time_args = "&from=now-{0}&to=now".format(args.time)
    elif args.time_from:
        start_time = int(parse_timestamp(args.time_from))
        end_time = "now"
        if args.time_to:
            end_time = int(parse_timestamp(args.time_to))
        time_args = "&from={0}&to={1}".format(start_time, end_time)
    else:
        time_args = "&from=now-3h&to=now"

    for dest in dests:
        report_url = dest['report_url']
        apikey = dest['apikey']

        for dashboard in dest['titles']:
            url = "{0}api/report/{1}?apitoken={2}{3}".format(
                report_url, dest['titles'][dashboard].lower(), apikey, time_args)
            filename = "{0}.pdf".format(dest['titles'][dashboard])

            print("Downloading: ", filename)
            data = read_url(url)
            with open(os.path.join(download_dir, filename), "wb") as pdf:
                pdf.write(data)

    tar_filename = "{0}.tar.gz".format(download_dir)
    print("Compressing: ", tar_filename)
    make_tarfile(tar_filename, download_dir)

    print("Clean up download directory")
    shutil.rmtree(download_dir)
