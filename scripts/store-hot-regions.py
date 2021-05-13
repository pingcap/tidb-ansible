#!/usr/bin/env python
#!coding:utf-8

from __future__ import print_function

import argparse
import subprocess
import json

class StoreStatistics(object):
    @classmethod
    def from_store_meta(cls, meta):
        res = cls()
        res.store_id = int(meta["store"]["id"])
        res.address = meta["store"].get("address", "")
        def is_tiflash_store(m):
            labels = m["store"].get("labels", [])
            for pair in labels:
                if pair.get("key", "") == "engine" and pair.get("value", "") == "tiflash":
                    return True
            return False
        res.is_tiflash_store = is_tiflash_store(meta)
        res.region_count = meta["status"].get("region_count", -1)
        res.leader_count = meta["status"].get("leader_count", -1)
        return res
    
    def __init__(self):
        self.store_id = -1
        self.address = ""
        self.is_tiflash_store = False
        self.region_count = -1
        self.leader_count = -1
    
    def is_tiflash(self):
        return self.is_tiflash_store

    def type(self):
        return "TiFlash" if self.is_tiflash_store else "TiKV"
    
    def __str__(self):
        return "Region {{ id: {:7d} type: {:7s} address: {:16s} region_count: {} leader_count: {} }}".format(
            self.store_id, self.type(), self.address, self.region_count, self.leader_count
        )

    def __repr__(self):
        return str({
            "id": self.store_id, "address": self.address, "type": self.type(),
            "region_count": self.region_count, "leader_count": self.region_count,
        })


class StoreHotStatistics(object):
    @classmethod
    def from_store_info(cls, store_id, obj):
        res = cls()
        res.store_id = int(store_id)
        for region in obj["statistics"]:
            res.total_flow_bytes += region['flow_bytes']
            res.total_flow_keys += region['flow_keys']
            res.hot_write_region_ids.append(int(region['region_id']))
        return res
 
    def __init__(self):
        self.store_id = 0
        self.total_flow_bytes = 0
        self.total_flow_keys = 0
        self.hot_write_region_ids = []

    def num_regions(self):
        return len(self.hot_write_region_ids)
    
    def __str__(self):
        return "HotWrite {{ flow_bytes: {:.2f} flow_keys: {:.2f} hot_region_count: {} }}".format(
            self.total_flow_bytes, self.total_flow_keys, self.num_regions()
        )

    def __repr__(self):
        return str({
            "id": self.store_id, "num_regions": self.num_regions(), 
            "flow_bytes": self.total_flow_bytes, "flow_keys" : self.total_flow_keys
        })

def collectStores(args):
    stores = {}

    httpAPI = "http://{}:{}/pd/api/v1/stores".format(args.host, args.port)
    webContent = subprocess.check_output(["curl", "-sl", httpAPI])
    store_infos = json.loads(webContent)
    for s in store_infos["stores"]:
        store = StoreStatistics.from_store_meta(s)
        stores[store.store_id] = store
    return stores

def collectHotWriteStores(args):
    stores = {}

    httpAPI = "http://{}:{}/pd/api/v1/hotspot/regions/write".format(args.host, args.port)
    webContent = subprocess.check_output(["curl", "-sl", httpAPI])
    region_infos = json.loads(webContent)

    as_leader = region_infos["as_leader"]
    for store_id in as_leader:
        store = StoreHotStatistics.from_store_info(store_id, as_leader[store_id])
        if store.num_regions() != 0:
            store_id = int(store_id)
            stores[store_id] = {"leader": store}

    as_peers = region_infos["as_peer"]
    for store_id in as_peers:
        store = StoreHotStatistics.from_store_info(store_id, as_peers[store_id])
        if store.num_regions() != 0:
            update_info = {"peer": store}
            store_id = int(store_id)
            if store_id in stores:
                stores[store_id].update(update_info)
            else:
                stores[store_id] = update_info
    return stores


def main():
    args = parse_args()

    stores = collectStores(args)
    stores_hot_write = collectHotWriteStores(args)

    print("Hot write: ")
    for store_id in stores:
        # Ignore TiKV stores if --tiflash-only is set
        if not stores[store_id].is_tiflash() and args.tiflash_only:
            continue
        print("{}".format(stores[store_id]))
        ident = ' ' * 4
        if store_id in stores_hot_write:
            for k in stores_hot_write[store_id]:
                print(ident + "Role: {:6s} {}".format(k, stores_hot_write[store_id][k]))
        else:
            print(ident + "[No hot write regions for this store]")


def parse_args():
    parser = argparse.ArgumentParser(description="Show hot regions distribution of all stores (including TiFlash stores).")
    parser.add_argument("--host", dest="host", help="pd address, default: 127.0.0.1", default="127.0.0.1")
    parser.add_argument("--port", dest="port", help="pd client port, default: 2379", default="2379")
    parser.add_argument("--tiflash-only", dest="tiflash_only", help="only show the hot regions of TiFlash stores.", action='store_true', default=False)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main()

