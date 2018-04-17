#!/usr/bin/env python2

from __future__ import print_function, \
    unicode_literals

import os
import urllib2
import json
import tarfile
import shutil

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
            url = report_url + "api/report/" + dest['titles'][dashboard].lower() + "?apitoken=" + apikey
            filename = dest['titles'][dashboard] + ".pdf"

            print("Downloading: ", filename)
            f = urllib2.urlopen(url)
            data = f.read()
            with open(os.path.join(download_dir, filename), "wb") as pdf:
                pdf.write(data)

    tar_filename = download_dir + ".tar.gz"
    print("Compressing: ", tar_filename)
    make_tarfile(tar_filename, download_dir)

    print("Clean up download directory")
    shutil.rmtree(download_dir)
