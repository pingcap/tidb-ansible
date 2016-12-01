# Ansible Playbook for TiDB

Requires Ansible 2.2

WIP

## Where to get binary

- http://download.pingcap.org/tidb-latest-linux-amd64.tar.gz
- http://download.pingcap.org/binlog-latest-linux-amd64.tar.gz
- http://download.pingcap.org/tidb-tools-latest-linux-amd64.tar.gz

Above binaries will be automatically downloaded by:

    ansible-playbook local_prepare.yml 

## Common Tasks

```
ansible-playbook cluster.yml --list-hosts

ansible-playbook cluster.yml -k -K

ansible-playbook rolling_update.yml
```

## Special Tasks

Rolling update TiKV only:

    ansible-playbook rolling_update.yml --tags tikv