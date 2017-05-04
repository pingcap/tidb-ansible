# Ansible Playbook for TiDB
---
> **TIDB IS NOT RECOMMENDED TO RUN AS ROOT**
---

WIP

## Requirements
To use this guide you’ll need a working installation of Ansible version 2.2 or later and pip install the newest Jinja2 / MarkupSafe Python module.
([installation  reference](http://docs.ansible.com/ansible/intro_installation.html))

After the installation is complete, you can run the following command to check ansible version：
```
$ ansible --version
ansible 2.2.2.0
```
## Deploy  information
1.  modify inventory.ini
    * if deploying via normal user:
        * change variable `ansible_user` to your deploy account (access sudo command).
    * if deploying via root:
        * uncomment variable `ansible_user`/`ansible_become_user`
        * comment variable `ansible_become`
2.  local prepare: if the Internet is accessbile, ansible will download the latest tidb.
    ```
    ansible-playbook local_prepare.yml
    ```

3.  modify kernel parameters
    
    ```
    ansible-playbook bootstrap.yml
    ```
4.  deploy
    
    > If deploying via root, uncomment variable `ansible_become` in inventory.ini file.

        ansible-playbook deploy.yml

5.  start cluster

        ansible-playbook start.yml
   

6.  test
    
    use mysql client

        mysql -u root -h tidb_servers_ip -P 4000

7.  grafana monitoring platform:

    http://grafana_servers_ip:3000
   
    login(admin/admin)

## Where to get binary

- http://download.pingcap.org/tidb-latest-linux-amd64.tar.gz
- http://download.pingcap.org/tidb-latest-linux-amd64-centos6.tar.gz
- http://download.pingcap.org/tidb-binlog-latest-linux-amd64.tar.gz
- http://download.pingcap.org/tidb-tools-latest-linux-amd64.tar.gz
- http://download.pingcap.org/sysbench-static-linux-amd64.tar.gz
- http://download.pingcap.org/mydumper-linux-amd64.tar.gz
- http://og66pdz33.bkt.clouddn.com/opbin.tar.gz

Above binaries will be automatically downloaded by:

    ansible-playbook local_prepare.yml

## Common Tasks

```
ansible all -m user -a 'name=tidb shell=/bin/bash groups=wheel append=yes'

ansible-playbook deploy.yml --list-hosts

ansible-playbook deploy.yml -k -K

ansible-playbook rolling_update.yml
```

## Special Tasks

Rolling update TiKV only:

    ansible-playbook rolling_update.yml --tags tikv