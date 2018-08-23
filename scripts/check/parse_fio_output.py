#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import argparse

def parse_opts():
    parser = argparse.ArgumentParser(description="Parse fio output.")
    parser.add_argument("--read-iops", action="store_true", default=False,
                        help="fio read IOPS.")
    parser.add_argument("--read-lat", action="store_true", default=False,
                        help="fio read average latency. (ns)")
    parser.add_argument("--write-iops", action="store_true", default=False,
                        help="fio write IOPS.")
    parser.add_argument("--write-lat", action="store_true", default=False,
                        help="fio write average latency. (ns)")
    parser.add_argument("--target", action="store", default=None,
                                    help="file path of fio JSON output.")
    parser.add_argument("--summary", action="store_true", default=False,
                        help="fio output summary.")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_opts()

    if not args.target:
        print("Please add `--target` flag to specify file path of fio JSON output.")
        sys.exit(1)
    else:
        output_file = args.target
 
    with open(output_file) as fp:
        result = json.load(fp)

    jobname = result['jobs'][0]['jobname']
    rw = result['global options']['rw']
    result_read = result['jobs'][0]['read']
    result_write = result['jobs'][0]['write']

    read_lag_ns = result_read['lat_ns']
    write_lag_ns = result_write['lat_ns']
    read_clag_ns = result_read['clat_ns']['percentile']
    write_clag_ns = result_write['clat_ns']['percentile']

    read_iops = int(result_read['iops'])
    read_lag_ns_min = int(read_lag_ns['min'])
    read_lag_ns_avg = int(read_lag_ns['mean'])
    read_lag_ns_max = int(read_lag_ns['max'])
    read_clag_ns_95 = int(read_clag_ns['95.000000'])
    read_clag_ns_99 = int(read_clag_ns['99.000000'])

    write_iops = int(result_write['iops'])
    write_lag_ns_min = int(write_lag_ns['min'])
    write_lag_ns_avg = int(write_lag_ns['mean'])
    write_lag_ns_max = int(write_lag_ns['max'])
    write_clag_ns_95 = int(write_clag_ns['95.000000'])
    write_clag_ns_99 = int(write_clag_ns['99.000000'])

    read_summary = "read: IOPS={}\nlat (ns): min={}, max={}, avg={}\nclat percentiles (ns): 95.00th={}, 99.00th={}".format(read_iops, read_lag_ns_min, read_lag_ns_max, read_lag_ns_avg, read_clag_ns_95, read_clag_ns_99)

    write_summary = "write: IOPS={}\nlat (ns): min={}, max={}, avg={}\nclat percentiles (ns): 95.00th={}, 99.00th={}".format(write_iops, write_lag_ns_min, write_lag_ns_max, write_lag_ns_avg, write_clag_ns_95, write_clag_ns_99)

    if args.read_iops:
        print(read_iops)
        sys.exit()

    if args.read_lat:
        print(read_lag_ns_avg)
        sys.exit()

    if args.write_iops:
        print(write_iops)
        sys.exit()

    if args.write_lat:
        print(write_lag_ns_avg)
        sys.exit()

    if args.summary:
        print("jobname: {}".format(jobname))
        if rw in ("read","randread","readwrite","rw","randrw"):
            print(read_summary)
        if rw in ("write","randwrite","readwrite","rw","randrw","trimwrite"):
            print(write_summary)
        sys.exit()
