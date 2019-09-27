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
        tidb_port = var.get('tidb_port', 4000)
        tidb_status_port = var.get('tidb_status_port', 10080)
        deploy_dir = var['deploy_dir']

        if ip in tidb_servers:
            tidb_servers[ip].append([tidb_port, tidb_status_port, deploy_dir])
        else:
            tidb_servers[ip] = [[tidb_port, tidb_status_port, deploy_dir]]

    for tikv in tikv_nodes:
        var = vars.get_vars(host=inv.get_host(hostname=str(tikv)))
        ip = var['ansible_host'] if 'ansible_host' in var else var['inventory_hostname']
        tikv_port = var.get('tikv_port', 20160)
        tikv_status_port = var.get('tikv_status_port', 20180)
        deploy_dir = var['deploy_dir']

        if ip in tikv_servers:
            tikv_servers[ip].append([tikv_port, tikv_status_port, deploy_dir])
        else:
            tikv_servers[ip] = [[tikv_port, tikv_status_port, deploy_dir]]

    return [tidb_servers, tikv_servers]


def check_conflict(server_list):
    conflict_ip = []
    for ip, node_vars in server_list.iteritems():
        length = len(node_vars)
        if length > 1:
            port_list = [var[0] for var in node_vars]
            sts_port_list = [var[1] for var in node_vars]
            dir_list = [var[2] for var in node_vars]
            if len(set(port_list)) < length \
                    or len(set(sts_port_list)) < length \
                    or len(set(dir_list)) < length:
                conflict_ip.append(ip)
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

