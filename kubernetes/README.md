# TiDB on Kubernetes with Ansible

This playbook and set of roles set up a Kubernetes cluster onto machines. And deploy TiDB cluster on kubernetes cluster.

This project uses lots of code from [kubernetes-contrib](https://github.com/kubernetes/contrib/tree/master/ansible). Many thanks to original authors!

## Requirements

* ansible 2.0 or higher and python-netaddr on control machine

* IP address or hostname of master/nodes. In a private network, these IP address must be internal or they may not communicate with each other by the public IP address

* All machines (master/node) must have docker, socat, python-yaml installed.

* Download tidb-kube-binaries.tar.gz from [here](http://download.pingcap.net/tidb-kube-binaries.tar.gz). This tarball contains docker images from gcr.io and DockerHub and etcd/flannel binary release and easy-rsa

*Note:* Currently only ubuntu trusty is tested, other OS maybe also works but not promised, and they will be tested very soon.


## Setup

### Configure inventory

Write host information in `inventory/hosts`

```
[masters]
192.168.199.100

[etcd]
192.168.199.100

[nodes]
192.168.199.101
192.168.199.102
192.168.199.103
```

### Configure Cluster options

Look through all of the options in `inventory/group_vars/all.yml` and
set the variables to reflect your needs.

## Get kubernetes up and running

To bring up kubernetes cluster, just run `ansible-playbook deploy-cluster.yml`. After kubernetes is up, ssh into master machine, configure bashrc

```bash
echo 'export PATH=/opt/bin:$PATH' >> ~/.bashrc
echo 'source <(kubectl completion bash)' >> ~/.bashrc
source ~/.bashrc
```

After that you can access your kubernetes cluster.

```bash
kubectl cluster-info
kubectl get svc --all-namespaces
kubectl get po --all-namespaces -o wide
```

If you see some errors or crashes when listing all pods, just delete and recreate them. This is somehow not very pleasant currently, I'm sorry.

You can also view your cluster from your web browser by http://192.168.199.100:8080/ui

TiDB can be access from any nodes IP with port `30004`, for example `mysql -h 192.168.199.102 -P 30004 -u root -D test`

We don't provide any higher level load balancer, you can choose whatever you like.

### Addons

By default, the Ansible playbook deploys Kubernetes addons as well. Addons consist of:

* DNS (kubedns)
* cluster monitoring (Grafana, Prometheus, node-exporter, pushgateway, alertmanager)
* cluster logging (Kibana, ElasticSearch, Fluentd)
* Kube UI (Kubernetes-dashboard)

### Network

This deployment uses flannel to get an overlay network
