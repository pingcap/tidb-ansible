# Ansible Playbook for TiDB

Requires Ansible 2.2

WIP

## Where to get binary

- http://download.pingcap.org/tidb-latest-linux-amd64.tar.gz
- http://download.pingcap.org/binlog-latest-linux-amd64.tar.gz
- http://download.pingcap.org/tidb-tools-latest-linux-amd64.tar.gz


## Common Tasks

```
ansible-playbook cluster.yml --list-hosts

ansible all -m user -a 'name=tidb shell=/bin/bash groups=wheel append=yes'

ansible all -m setup

ansible-playbook cluster.yml -k -K
```
