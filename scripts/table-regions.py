#!/usr/bin/env python
#!coding:utf-8

import argparse
import subprocess
import json

def main():
    args = parse_args()
    httpAPI = "http://{}:{}/tables/{}/{}/regions".format(args.host, args.port, args.database, args.table)

    webContent = subprocess.check_output(["curl", "-sl", httpAPI])
    region_info = json.loads(webContent)

    table_region_leaders = parse_regions(region_info["record_regions"])
    table_region_peers = parse_region_peers(region_info["record_regions"])
    indices_region_leaders = []
    indices_region_peers = []
    for index_info in region_info["indices"]:
        index_name = index_info["name"]
        index_region_leaders = parse_regions(index_info["regions"])
        indices_region_leaders.append({"name": index_name, "leader": index_region_leaders})
        index_region_peers = parse_region_peers(index_info["regions"])
        indices_region_peers.append({"name": index_name, "peers": index_region_peers})
    # print record
    print("[RECORD - {}.{}] - Leaders Distribution:".format(args.database, args.table))
    print_leaders(table_region_leaders)
    print("[RECORD - {}.{}] - Peers Distribution:".format(args.database, args.table))
    print_peers(table_region_peers)
    # print indices
    for index_region_info in indices_region_leaders:
        print("[INDEX - {}] - Leaders Distribution:".format(index_region_info["name"]))
        print_leaders(index_region_info["leader"])
    for index_region_info in indices_region_peers:
        print("[INDEX - {}] - Peers Distribution:".format(index_region_info["name"]))
        print_peers(index_region_info["peers"])


def parse_args():
    parser = argparse.ArgumentParser(description="Show leader distribution of a TiDB table.")
    parser.add_argument("--host", dest="host", help="tidb-server address, default: 127.0.0.1", default="127.0.0.1")
    parser.add_argument("--port", dest="port", help="tidb-server status port, default: 10080", default="10080")
    parser.add_argument("database", help="database name")
    parser.add_argument("table",    help="table name")
    args = parser.parse_args()
    return args

def parse_regions(regions):
    info = {}
    for region in regions:
        if region["leader"]["store_id"] != None:
            store_id = region["leader"]["store_id"]
            info[store_id] = 1 + info.get(store_id, 0)
    return info

def parse_region_peers(regions):
    info = {}
    for region in regions:
        for peer in region["peers"]:
            if peer["store_id"] != None:
                store_id = peer["store_id"]
                info[store_id] = 1 + info.get(store_id, 0)
    return info

def print_leaders(info, indent = "  "):
    total_leaders = 0
    for store_id, num_leaders in info.items():
        total_leaders += num_leaders
    print("{}total leader count: {}".format(indent, total_leaders))
    for store_id, num_leaders in info.items():
        print("{}store: {}, num_leaders: {}, percentage: {}%".format(indent, store_id, num_leaders,format((num_leaders*100.0)/total_leaders,'.2f')))

def print_peers(info, indent = "  "):
    total_peers = 0
    for store_id, num_peers in info.items():
        total_peers += num_peers
    print("{}total peers count: {}".format(indent, total_peers))
    for store_id, num_peers in info.items():
        print("{}store: {}, num_peers: {}, percentage: {}%".format(indent, store_id, num_peers, format((num_peers*100.0)/total_peers,'.2f')))


if __name__ == "__main__":
    main()
