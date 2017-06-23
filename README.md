# Ansible Playbook for TiDB
> **TIDB IS NOT RECOMMENDED TO RUN AS ROOT**

# Introductioon
Ansible is simple IT automation tool. [TiDB-Ansible](https://github.com/pingcap/tidb-ansible) is a deployment cluster tool based on `Ansible playbook`. By using it, you can deploy a TiDB cluster(PD, TiDB, TiKv and monitor tools) quick and easily.
 
# What this Playbook can do
* cluster topology is set through a configuration file `inventory.ini`. Operation and maintenance work can be easily done.
1. bootstrap machine.
2. deploy binary to desination machine
3. rolling update
4. cleanup data
5. cleanip enviorment
6. configure minotor package

# Prepare Machine
## Some target machine:
# Tutorial

[简体中文](https://github.com/pingcap/docs-cn/blob/master/op-guide/ansible-deployment.md)

## Requirements
To use this guide you’ll need a working installation of Ansible version 2.2 or later and `pip install Jinja2==2.7.2 MarkupSafe==0.11`.

Simple guide for installing ansinle in different OS
1. Ubuntu install ansible via PPA:
  sudo add-apt-repository ppa:ansible/ansible
  sudo apt-get update
  sudo apt-get install ansible

2. CentOS install ansible via PPA:
  yum install epel-release
  yum update
  yum install ansible

3. macOS install ansible via Homebrew:
  brew update
  brew install ansible

4. Docker:
  docker run -v `pwd`:/playbook --rm -it williamyeh/ansible:ubuntu16.04 /bin/bash
  cd /playbook # 
  above command will mount current directory to container's `/playbook`.

If above does not help, you can find more information in ([installation  reference](http://docs.ansible.com/ansible/intro_installation.html)).

After the installation is complete, you can run the following command to check ansible version：
```
$ ansible --version
ansible 2.2.2.0
```

## Deploy  information
1.  modify ansible.cgf
    * if you want to supply a differnt location of your key:
        * uncomment ssh_args and supply path of your key after  `-i`.
2.  modify inventory.ini
    * if deploying via normal user:
        * change variable `ansible_user` to your deploy account (access sudo command).
    * if deploying via root:
        * uncomment variable `ansible_user`/`ansible_become_user`
        * comment variable `ansible_become`
3.  local prepare: if the Internet is accessbile, ansible will download the latest tidb.
    ```
    ansible-playbook local_prepare.yml
    ```

4.  modify kernel parameters
    
    ```
    ansible-playbook bootstrap.yml
    ```
5.  deploy
    
    > If deploying via root, uncomment variable `ansible_become` in inventory.ini file.

        ansible-playbook deploy.yml

6.  start cluster

        ansible-playbook start.yml
   

7.  test
    
    use mysql client

        mysql -u root -h tidb_servers_ip -P 4000

8.  grafana monitoring platform:

    http://grafana_servers_ip:3000
   
    login(admin/admin)

If your run into trouble, be sure you try 3 first and then 4, 5.

- http://download.pingcap.org/tidb-latest-linux-amd64.tar.gz
- http://download.pingcap.org/tidb-latest-linux-amd64-centos6.tar.gz
- http://download.pingcap.org/tidb-binlog-latest-linux-amd64.tar.gz
- http://download.pingcap.org/tidb-tools-latest-linux-amd64.tar.gz
- http://download.pingcap.org/sysbench-static-linux-amd64.tar.gz
- http://download.pingcap.org/mydumper-linux-amd64.tar.gz
- http://download.pingcap.org/opbin.tar.gz

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
