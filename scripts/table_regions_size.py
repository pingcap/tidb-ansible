#!/usr/bin/env python
# !coding:utf-8

import argparse
import subprocess
import json
import os
from enum import Enum


class Resource(Enum):
    KEY = 1
    SIZE = 2


def count(table_region_set, all_regions, resource, group, to_draw):
    table_regions = filter(lambda region: region["id"] in table_region_set, all_regions["regions"])
    table_regions = map(lambda region: (region["id"], int(region[get_resource_key(resource)])), table_regions)
    table_regions = sorted(table_regions, key=lambda region: region[0])
    if to_draw:
        try:
            draw(table_regions, resource)
        except:
            print("need to install matplotlib")

    table_regions = sorted(table_regions, key=lambda region: region[1])

    output(table_regions, generate_steps(resource, group=group, max_value=table_regions[-1][1] + 1), resource)


def main():
    args = parse_args()
    region_info = get_json("http://{}:{}/tables/{}/{}/regions".format(args.host, args.port, args.database, args.table))
    table_region_set = set(map(lambda region: region["region_id"], region_info["record_regions"]))
    all_regions = get_json("http://{}:{}/pd/api/v1/regions".format(args.pd_host, args.pd_port))
    count(table_region_set, all_regions, Resource.KEY, args.group, args.draw)
    count(table_region_set, all_regions, Resource.SIZE, args.group, args.draw)


def generate_steps(resource, group, max_value):
    steps = []
    if group:
        for i in range(0, group + 1):
            steps.append(int(i * max_value / group))
    else:
        if resource == Resource.SIZE:
            steps = [0, 2, 20, 96, max_value]
        else:
            steps = [0, 20000, 200000, 960000, max_value]
    return steps


def format_steps(steps):
    result = []
    for step in steps:
        if step >= 1000:
            result.append("{}k".format(int(step / 1000)))
        else:
            result.append("{}".format(step))
    return result


def get_resource_key(resource):
    if resource == Resource.KEY:
        return 'approximate_keys'
    else:
        return 'approximate_size'


def parse_args():
    parser = argparse.ArgumentParser(description="Show region size and keys distribution of a TiDB table.")
    parser.add_argument("--host", dest="host", help="tidb-server address, default: 127.0.0.1", default="127.0.0.1")
    parser.add_argument("-d", dest="draw", help="whether to draw pictures, default: False", default=False, action='store_true')
    parser.add_argument("--port", dest="port", help="tidb-server status port, default: 10080", default="10080")
    parser.add_argument("--pd_host", dest="pd_host", help="pd-server address, default: 127.0.0.1", default="127.0.0.1")
    parser.add_argument("--pd_port", dest="pd_port", help="pd-server status port, default: 2379", default="2379")
    parser.add_argument("--group", dest="group", help="the result group num, default: 0 (split by default mode)",
                        type=int, required=False, default=0)
    parser.add_argument("database", help="database name")
    parser.add_argument("table", help="table name")
    args = parser.parse_args()
    return args


def draw(table_regions, resource):
    import matplotlib.pyplot as plt
    label = get_resource_key(resource)
    ax = plt.gca()
    ax.set_xlabel('region_order')
    ax.set_ylabel(label)
    x_list, y_list = [], []
    for i, (_, region_size) in enumerate(table_regions):
        x_list.append(i)
        y_list.append(region_size)

    plt.scatter(x_list, y_list, color="r", alpha=0.5, s=5)
    plt.savefig(os.path.join("result_{}.png".format(label)))
    plt.show()


def get_json(url):
    web_content = subprocess.check_output(["curl", "-sl", url])
    json.loads(web_content)
    return json.loads(web_content)


def output(table_regions, steps, resource):
    counts = [0]
    i = 1
    for region in table_regions:
        if region[1] < steps[i]:
            counts[-1] += 1
        else:
            counts.append(0)
            i += 1

    output_steps = format_steps(steps)
    print("Region {}\t\t\tRegion num".format(get_resource_key(resource)).replace("approximate_", ""))
    for i, count in enumerate(counts):
        output_range = "{} ~ {}".format(output_steps[i], output_steps[i + 1]).ljust(16)
        print("{}\t{}".format(output_range, count))
    print("")


if __name__ == "__main__":
    main()
