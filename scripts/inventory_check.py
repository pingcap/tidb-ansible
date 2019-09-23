# coding: utf-8


import re
import sys


def parse_inventory(inventory):
    tidb_servers = {}
    tikv_servers = {}

    with open(inventory, 'r') as f:
        inventory = f.readlines()

    group = ''
    for line in inventory:
        line = line.strip()
        if re.match(r'\[\w+_\w+\]', line):
            if 'tidb_servers' in line:
                group = 'tidb_servers'
            elif 'tikv_servers' in line:
                group = 'tikv_servers'
            else:
                group = ''
        elif group == 'tidb_servers':
            if not len(line) or line.startswith('#'):
                continue
            ip = re.search(r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?'
                           r'[0-9][0-9]?)\.){3}(?:25[0-5]|'
                           r'2[0-4][0-9]|[01]?[0-9][0-9]?)',
                           line).group()
            dbport = re.search(r'tidb_port=(\d+)', line)
            tidb_port = 4000 if not dbport else dbport.group(1)
            dbstsport = re.search(r'tidb_staus_port=(\d+)', line)
            tidb_status_port = 10080 if not dbstsport else dbstsport.group(1)
            deploydir = re.search(r'deploy_dir=([^ ]*)', line)
            deploy_dir = '/home/tidb/deploy' if not deploydir else deploydir.group(1)
            if tidb_servers.has_key(ip):
                tidb_servers[ip].append([tidb_port, tidb_status_port, deploy_dir])
            else:
                tidb_servers[ip] = [[tidb_port, tidb_status_port, deploy_dir]]
        elif group == 'tikv_servers':
            if not len(line) or line.startswith('#'):
                continue
            ip = re.search(r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?'
                           r'[0-9][0-9]?)\.){3}(?:25[0-5]|'
                           r'2[0-4][0-9]|[01]?[0-9][0-9]?)',
                           line).group()
            kvport = re.search(r'tikv_port=(\d+)', line)
            tikv_port = 20160 if not kvport else kvport.group(1)
            kvstsport = re.search(r'tikv_staus_port=(\d+)', line)
            tikv_status_port = 20180 if not kvstsport else kvstsport.group(1)
            deploydir = re.search(r'deploy_dir=([^ ]*)', line)
            deploy_dir = '/home/tidb/deploy' if not deploydir else deploydir.group(1)
            if tikv_servers.has_key(ip):
                tikv_servers[ip].append([tikv_port, tikv_status_port, deploy_dir])
            else:
                tikv_servers[ip] = [[tikv_port, tikv_status_port, deploy_dir]]
    return [tidb_servers, tikv_servers]


def check_conflict(server_list):
    conflict_ip = []
    isContinue = False
    for ip, nodes in server_list.iteritems():
        length = len(nodes)
        if length > 1:
            for i in range(length - 1):
                for j in range(i + 1, length):
                    for k in nodes[i]:
                        if k in nodes[j]:
                            isContinue = True
                            conflict_ip.append(ip)
                            break
                    if isContinue:
                        break
                if isContinue:
                    break
            if isContinue:
                continue
    return conflict_ip


if __name__ == '__main__':
    tidb_servers, tikv_servers = parse_inventory(sys.argv[1])
    tidb_conf_conflict = check_conflict(tidb_servers)
    tikv_conf_conflict = check_conflict(tikv_servers)
    if tidb_conf_conflict:
        if tikv_conf_conflict:
            print('''
    TiDB port or deployment directory conflicts on {} machine.
    TiKV port or deployment directory conflicts on {} machine.
    Please recheck the port, status_port, deploy_dir or other configuration in inventory.ini.'''
                  .format(','.join(tidb_conf_conflict), ','.join(tikv_conf_conflict)))
        else:
            print('''
    TiDB port or deployment directory conflicts on {} machine.
    Please recheck the port, status_port, deploy_dir or other configuration in inventory.ini.'''
                  .format(','.join(tidb_conf_conflict)))
    else:
        if tikv_conf_conflict:
            print('''
    TiKV port or deployment directory conflicts on {} machine.
    Please recheck the port, status_port, deploy_dir or other configuration in inventory.ini.'''
                  .format(','.join(tikv_conf_conflict)))
        else:
            print('Check ok.')
