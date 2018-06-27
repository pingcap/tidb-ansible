#!/usr/bin/env python

from __future__ import print_function, \
    unicode_literals

import os
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

if __name__ == '__main__':

    if not os.path.isdir(download_dir):
        os.makedirs(download_dir)

    for dest in dests:
        report_url = dest['report_url']
        apikey = dest['apikey']

        for dashboard in dest['titles']:
            url = "{0}api/report/{1}?apitoken={2}".format(report_url, dest['titles'][dashboard].lower(), apikey)
            filename = "{0}.pdf".format(dest['titles'][dashboard])

            print("Downloading: ", filename)
            f = urlreq.urlopen(url)
            data = f.read()
            with open(os.path.join(download_dir, filename), "wb") as pdf:
                pdf.write(data)

    tar_filename = "{0}.tar.gz".format(download_dir)
    print("Compressing: ", tar_filename)
    make_tarfile(tar_filename, download_dir)

    print("Clean up download directory")
    shutil.rmtree(download_dir)
