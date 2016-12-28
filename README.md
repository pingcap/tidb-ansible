# Ansible Playbook for TiDB

Requires Ansible 2.2

WIP

## Where to get binary

- http://download.pingcap.org/tidb-latest-linux-amd64.tar.gz
- http://download.pingcap.org/tidb-latest-linux-amd64-centos6.tar.gz
- http://download.pingcap.org/binlog-latest-linux-amd64.tar.gz
- http://download.pingcap.org/tidb-tools-latest-linux-amd64.tar.gz
- http://download.pingcap.org/sysbench-static-linux-amd64.tar.gz
- http://og66pdz33.bkt.clouddn.com/opbin.tar.gz

Above binaries will be automatically downloaded by:

    ansible-playbook local_prepare.yml

## Common Tasks

```
ansible all -m user -a 'name=tidb shell=/bin/bash groups=wheel append=yes'

ansible-playbook cluster.yml --list-hosts

ansible-playbook cluster.yml -k -K

ansible-playbook rolling_update.yml
```

## Special Tasks

Rolling update TiKV only:

    ansible-playbook rolling_update.yml --tags tikv
