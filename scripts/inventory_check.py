# coding: utf-8


import sys
from ansible.vars.manager import VariableManager
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager


def parse_inventory(inventory):
    loader = DataLoader()
    inv = InventoryManager(loader=loader, sources=[inventory])
    vars = VariableManager(loader=loader, inventory=inv)
    all_groups = inv.get_groups_dict()
    tidb_nodes = all_groups['tidb_servers']
    tikv_nodes = all_groups['tikv_servers']
    tidb_servers = {}
    tikv_servers = {}
    for tidb in tidb_nodes:
        var = vars.get_vars(host=inv.get_host(hostname=str(tidb)))
        ip = var['ansible_host'] if 'ansible_host' in var else var['inventory_hostname']
        tidb_port = var['tidb_port'] \
            if 'tidb_port' in var else 4000
        tidb_status_port = var['tidb_status_port'] \
            if 'tidb_status_port' in var else 10080
        deploy_dir = var['deploy_dir']

        if ip in tidb_servers:
            tidb_servers[ip].append([tidb_port, tidb_status_port, deploy_dir])
        else:
            tidb_servers[ip] = [[tidb_port, tidb_status_port, deploy_dir]]

    for tikv in tikv_nodes:
        var = vars.get_vars(host=inv.get_host(hostname=str(tikv)))
        ip = var['ansible_host'] if 'ansible_host' in var else var['inventory_hostname']
        tikv_port = var['tikv_port'] \
            if 'tikv_port' in var else 4000
        tikv_status_port = var['tikv_status_port'] \
            if 'tikv_status_port' in var else 10080
        deploy_dir = var['deploy_dir']

        if ip in tikv_servers:
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
            for index_i in range(length - 1):
                for index_j in range(index_i + 1, length):
                    for node_var in nodes[index_i]:
                        if node_var in nodes[index_j]:
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
        print('\n    TiDB port or deployment directory conflicts on {} machine.'
              .format(','.join(tidb_conf_conflict)))

    if tikv_conf_conflict and not tidb_conf_conflict:
        print('\n    TiKV port or deployment directory conflicts on {} machine.'
              .format(','.join(tikv_conf_conflict)))
    elif tikv_conf_conflict and tidb_conf_conflict:
        print('    TiKV port or deployment directory conflicts on {} machine.'
              .format(','.join(tikv_conf_conflict)))

    if tidb_conf_conflict or tikv_conf_conflict:
        print('    Please recheck the port, status_port, deploy_dir or other configuration in inventory.ini.')
    else:
        print('Check ok.')

