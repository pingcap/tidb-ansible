#!/usr/bin/env python
# !coding:utf-8

import argparse
import subprocess
import json
import os


def main():
    args = parse_args()
    region_info = get_json("http://{}:{}/tables/{}/{}/regions".format(args.host, args.port, args.database, args.table))
    region_set = set(map(lambda region: region["region_id"], region_info["record_regions"]))
    all_regions = get_json("http://{}:{}/pd/api/v1/regions".format(args.pd_host, args.pd_port))
    table_regions = filter(lambda region: region["id"] in region_set, all_regions["regions"])
    table_regions = map(lambda region: (region["id"], int(region["approximate_size"])), table_regions)
    table_regions = sorted(table_regions, key=lambda region: region[0])
    try:
        draw(table_regions)
    except:
        pass

    table_regions = sorted(table_regions, key=lambda region: region[1])
    max_region_size = table_regions[-1][1] + 1
    steps = []
    if args.group:
        for i in range(0, args.group+1):
            steps.append(int(i * max_region_size / args.group))
    else:
        steps = [0, 2, 20, 96, max_region_size]
    output_simple(table_regions, steps)


def parse_args():
    parser = argparse.ArgumentParser(description="Show leader distribution of a TiDB table.")
    parser.add_argument("--host", dest="host", help="tidb-server address, default: 127.0.0.1", default="127.0.0.1")
    parser.add_argument("--port", dest="port", help="tidb-server status port, default: 10080", default="10080")
    parser.add_argument("--pd_host", dest="pd_host", help="pd-server address, default: 127.0.0.1", default="127.0.0.1")
    parser.add_argument("--pd_port", dest="pd_port", help="pd-server status port, default: 2379", default="2379")
    parser.add_argument("--group", dest="group", help="the result group num, default: 0 (split by default mode)",
                        type=int, required=False, default=0)
    parser.add_argument("database", help="database name")
    parser.add_argument("table", help="table name")
    args = parser.parse_args()
    return args


def draw(table_regions):
    import matplotlib.pyplot as plt
    ax = plt.gca()
    ax.set_xlabel('region order')
    ax.set_ylabel('approximate_size')
    x_list, y_list = [], []
    for i, (_, region_size) in enumerate(table_regions):
        x_list.append(i)
        y_list.append(region_size)

    plt.scatter(x_list, y_list, color="r", alpha=0.5, s=5)
    plt.show()
    plt.savefig(os.path.join("result.png"))


def get_json(url):
    web_content = subprocess.check_output(["curl", "-sl", url])
    json.loads(web_content)
    return json.loads(web_content)


def output_simple(table_regions, steps):
    counts = [0]
    i = 1
    for region in table_regions:
        if region[1] < steps[i]:
            counts[-1] += 1
        else:
            counts.append(0)
            i += 1
    print("Region size(MB)\tRegion num")
    for i, count in enumerate(counts):
        print("{}\t~\t{}\t\t{}".format(steps[i], steps[i + 1], count))


if __name__ == "__main__":
    main()
