#!/usr/bin/env python
#!coding:utf-8

import argparse
import subprocess
import json
from collections import Iterable

# sql: select count(s.region_id) cnt, s.index_name, p.store_id from INFORMATION_SCHEMA.TIKV_REGION_STATUS s join INFORMATION_SCHEMA.tikv_region_peers p on s.region_id = p.region_id where s.table_name = 'table_name' and p.is_leader = 1 group by index_name, p.store_id order by index_name,cnt desc;

def main():
    args = parse_args()
    httpAPI = "http://{}:{}/tables/{}/{}/regions".format(args.host, args.port, args.database, args.table)

    webContent = subprocess.check_output(["curl", "-sl", httpAPI])
    region_infos = json.loads(webContent)
    if not isinstance(region_infos, list): # without partition
        region_infos = [region_infos]
        
    # store_id -> num of regions
    table_region_leaders = {}
    # store_id -> StoreRegionPeers
    table_region_peers = {}
    # name -> region leader
    indices_region_leaders = {}
    # name -> region peers
    indices_region_peers = {}
    for region_info in region_infos:
        table_region_leaders = merge(table_region_leaders, parse_regions(region_info["record_regions"]))
        table_region_peers = merge_peers(table_region_peers, parse_region_peers(region_info["record_regions"]))
        if not args.hide_indices:
            for index_info in region_info["indices"]:
                index_name = index_info["name"]
                index_region_leaders = parse_regions(index_info["regions"])
                indices_region_leaders[index_name] = merge(index_region_leaders, indices_region_leaders.get(index_name, {}))
                index_region_peers = parse_region_peers(index_info["regions"])
                indices_region_peers[index_name] = merge_peers(index_region_peers, indices_region_peers.get(index_name, {}))
    # print record
    print("[RECORD - {}.{}] - Leaders Distribution:".format(args.database, args.table))
    print_leaders(table_region_leaders)
    print("[RECORD - {}.{}] - Peers Distribution:".format(args.database, args.table))
    print_peers(table_region_peers)
    # print indices
    if not args.hide_indices:
        print("")
        for index_name, index_region_info in indices_region_leaders.items():
            print("[INDEX - {}] - Leaders Distribution:".format(index_name))
            print_leaders(index_region_info)
        print("")
        for index_name, index_region_info in indices_region_peers.items():
            print("[INDEX - {}] - Peers Distribution:".format(index_name))
            print_peers(index_region_info)


def parse_args():
    parser = argparse.ArgumentParser(description="Show leader distribution of a TiDB table.")
    parser.add_argument("--host", dest="host", help="tidb-server address, default: 127.0.0.1", default="127.0.0.1")
    parser.add_argument("--port", dest="port", help="tidb-server status port, default: 10080", default="10080")
    parser.add_argument("database", help="database name")
    parser.add_argument("table",    help="table name")
    parser.add_argument("--hide-indices", dest="hide_indices", help="whether collect distribution of indices regions", action='store_true', default=False)
    args = parser.parse_args()
    return args

def merge(dist1, dist2):
    for k in dist2:
        dist1[k] = dist2[k] + dist1.get(k, 0)
    return dist1

def parse_regions(regions):
    info = {}
    for region in regions:
        if region["leader"]["store_id"] != None:
            store_id = region["leader"]["store_id"]
            info[store_id] = 1 + info.get(store_id, 0)
    return info

class StoreRegionPeers:
    def __init__(self):
        # num of regions in normal role (Leader or Follower)
        self.num_normal = 0
        # num of region in Learner role
        self.num_learners = 0

    def add(self, peer):
        if peer.get("is_learner", False) == True:
            self.num_learners += 1
        else:
            self.num_normal += 1

    def merge(self, rhs):
        self.num_normal += rhs.num_normal
        self.num_learners += rhs.num_learners
        return self
    
    def num(self):
        return self.num_normal + self.num_learners
    
    def __str__(self):
        return str({"normal": self.num_normal, "learner": self.num_learners})
    def __repr__(self):
        return str(self)

def merge_peers(dist1, dist2):
    for k in dist2:
        if k in dist1:
            dist1[k] = dist2[k].merge(dist1[k])
        else:
            dist1[k] = dist2[k]
    return dist1

def parse_region_peers(regions):
    info = {}
    for region in regions:
        for peer in region["peers"]:
            if peer["store_id"] != None:
                store_id = peer["store_id"]
                if store_id not in info:
                    info[store_id] = StoreRegionPeers()
                info[store_id].add(peer)
    return info

def print_leaders(info, indent = "  "):
    total_leaders = 0
    for store_id, num_leaders in info.items():
        total_leaders += num_leaders
    print("{}total leader count: {}".format(indent, total_leaders))
    for store_id, num_leaders in info.items():
        print("{}store: {:6d}, num_leaders: {:6d}, percentage: {:.2f}%".format(indent, store_id, num_leaders,(num_leaders*100.0)/total_leaders))

def print_peers(info, indent = "  "):
    total_peers = 0
    for store_id, peers in info.items():
        total_peers += peers.num()
    print("{}total peers count: {}".format(indent, total_peers))
    for store_id, peers in info.items():
        num_peers = peers.num()
        print("{}store: {:6d}, num_peers(num_learners): {:6d}({:6d}), percentage: {:.2f}%".format(indent, store_id, num_peers, peers.num_learners, (num_peers*100.0)/total_peers))


if __name__ == "__main__":
    main()

