# Ansible-TiDB 部署指南
v0.0.1 by wangshuyu [项目地址](https://github.com/pingcap/tidb-ansible)

## 概述
Ansilbe 是一个集群部署工具。部署的主机可以是本地或者远程虚拟机，也可以是远程物理机。
一个完整的TiDB集群包括TiKV，PD，TiDB以及负载均衡模块、集群监控模块、数据备份（同步）模块。

由于TiDB集群天然的复杂性（此处应有一坨图），导致了部署成了难题。本 Ansible-TiDB 工具为集群的快速部署、
监控模块的快速配置提供了可能，并对实际上线过程中的滚动升级提供有限支持。

## 前置条件
- 部署目标机器若干
  - 建议4台及以上，TiKV建议至少3实例，且与TiDB、PD模块不同机共存
    - 若用于实验目的，单机也可以部署多模块
  - Linux 操作系统，x86_64架构（amd64），内核版本建议 3.10 以上
  - 机器之间网络互通，防火墙、iptables等可以在部署验证时关闭，后期开启
  - 机器的时间、时区设置正确，有 NTP 服务可以同步正确时间
  - 部署账户具有 sudo 权限，或直接通过 root 用户部署
  - python 2.6 或 python 2.7
  - ifconfig 可正常执行（CentOS 下 net-tools）
  - 建议至少有一台开放外网访问，用于安装监控工具、报警工具
- 部署中控机一台
  - python 2.6 或 python 2.7，安装有 ansible 2.2 版本
    - 也可使用 docker 镜像: ``williamyeh/ansible:ubuntu16.04``
  - 可通过 ssh 登录目标机器
  - 可以访问外网（不需要翻墙）
  - 可以是部署目标机器中的某一台

## 准备工作

确定好前置条件满足后，就可以分配机器资源了，原则上应按照：
[TiDB 部署建议](https://github.com/pingcap/docs-cn/blob/master/op-guide/recommendation.md)
分配机器和对应模块。

### 下载 Playbook

登录中控机器（也可使用个人笔记本，macOS 操作系统亦可）。下载本 Playbook。

```bash
git clone https://github.com/pingcap/tidb-ansible.git
cd tidb-ansible # where the magic happens
```

> 建议使用 git 下载，用分支管理集群的部署配置。


### 安装 Ansible 2.2

按照 [官方手册](http://docs.ansible.com/ansible/intro_installation.html) 安装最新版本。

安装完成后，需要执行 ``ansible --version`` 确认 Ansible 版本为 2.2 及以上。

以下是简单说明：

#### Ubuntu

通过 PPA 源安装。

```shell
sudo add-apt-repository ppa:ansible/ansible
sudo apt-get update
sudo apt-get install ansible
```

#### macOS

通过 Homebrew 安装。安装 Homebrew 请参考 [官方主页](http://brew.sh/)。

```
brew update
brew install ansible
```

#### Windows

无环境。暂未测试。请自己折腾。

#### Docker

根据自己的平台，安装并配置 Docker。

```bash
docker run -v `pwd`:/playbook --rm -it williamyeh/ansible:ubuntu16.04 /bin/bash
cd /playbook #  
```

> 注意以上目录将当前工作目录挂载为容器中 ``/playbook``。

### 编制 Ansible Inventory 文件

Ansible 使用 Inventory 文件描述部署目标服务器。例子请参考 ``inventory.ini.sample`` 文件。

当通过 root 用户 ssh 部署时（一般为 CentOS），需要填写 ``[all:vars]``：

```ini
[all:vars]
# ssh via root:
ansible_user = root
ansible_become = true
ansible_become_user = tidb
```

表示通过 root 用户登录，部署到 tidb 用户。

当通过 tidb 用户（举个栗子）ssh 登录部署时，只需提供：

```
[all:vars]
ansible_user = tidb
```

> 当不需要部署监控时，``[monitoring_servers]``, ``[monitored_servers:children]`` 留空即可。

inventory 文件修改完成后，保存，并确认 ``ansible.cfg`` 的 inventory 指向该文件。

### 自定义模块部署配置

本 Playbook 默认将模块部署在 ``/home/用户名/deploy`` 目录下。

相关配置请在 ``group_vas`` 目录下修改。包括端口号，数据目录等。

模块核心配置暂时不推荐非专家修改。:)

## 部署前检查

### 检查机器可访问性

定义好服务列表后，需要检查确保登录用户、sudo 权限正常。

以下命令假定和目标机器的信任已建好。若需要帐号密码登录，请加上 ``-k -K`` 参数。

```bash
# 检查所有机器列表
ansible all --list-hosts 

# 检查机器权限
ansible all -m ping

# 检查当前用户
ansible all -m shell 'whoami'
# 检查 sudo 是否正常
ansible all -m -b shell 'whoami'
```

> 一般情况下，sudo 都需要输入密码，所以密码登录比较保险。（修改 /etc/sudoers 也可）

以上命令确认正常后。即可继续。

### 检查部署列表

```bash
ansible-playbook cluster.yml --list-hosts
```

查看输出确认以上部署安排是否符合预期。

## 开始部署

### 获取最新 binary

```bash
ansible-playbook local_prepare.yml
```

以上命令会自动下载最新的 TiDB 集群 binary 到中控机 downloads 目录，为之后部署做准备。

若有手工野版本需要上线，在此时修改并替换 downloads 目录中对应的文件。

### 开始真正部署

以下命令择一执行：

```bash
ansible-playbook cluster.yml

# 需要用户名密码时
ansible-playbook cluster.yml -k -K

# 需要提高并发度时（10并发: forks）
ansible-playbook cluster.yml -k -K -f 10

# 需要查看详细输出时
ansible-playbook -v cluster.yml -k -K -f 10

# 觉得以上输出不够详细时
ansible-playbook -vv cluster.yml -k -K -f 10

# 觉得以上输出不够详细时
ansible-playbook -vvv cluster.yml -k -K -f 10

# 觉得以上输出不够详细时
ansible-playbook -vvvv cluster.yml -k -K -f 10

# 觉得以上输出不够详细时
echo sucks
```

### 启动服务

部署成功后，可以到目标机器检查确认。随后启动服务。

```bash
ansible-playbook restart_all.yml
```

等待一段时间后，检查集群是否成功启动：

```bash
ansible all -m shell -a 'ps aux | grep supervise'

# 或 pstree 检查线程数是否符合预期

ansible all -m shell -a 'pstree 用户名'
```

然后就可以用 ``mysql -u root -h TiDB主机IP -P 端口(默认4000)`` 尝试连接。


## 滚动升级

TODO

## Trouble Shooting 

TODO

## 存在问题

TODO




