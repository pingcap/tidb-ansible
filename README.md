# Ansible Playbook for TiDB

<span style="color: red; font-size:3em">  TIDB CAN NOT RUN BE WITH ROOT </span>

Requires Ansible 2.2

WIP

## Deploy  informations
1. install ansible and pip install the newest [ Jinja2 / MarkupSafe ]
3. modify inventory.ini
    * change val `ansible_user` with your deploy account (access sudo command).
    * if deploy with root
        * uncomment val `ansible_user`/`ansible_become_user`
        * comment val `ansible_become`
4. local prepare; if Internet is accessbile, ansible will download the latest tidb,
    * command: 
        ```
            ansible-playbook local_prepare.yml
        ```
5. modify kernel variables
    * command: 
    ```
        ansible-playbook bootstrap.yml
    ```
6. deploy 

    *if deploy with root,*
    *uncomment val `ansible_become` in inventory.ini file*

    * command: 
    ```
        ansible-playbook deploy.yml
    ```
7. start 
    * command:
    ```
        ansible-playbook start.yml
    ```
8. test
    * use mysql client 
    ```
        mysql -u root -h tidb_ip -P 4000
    ```
9. web http://grafana_servers:3000
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
