## Setup

By default vagrant will launch 1 master, 3 nodes. And each VM allocate 1GB memory, so make sure your host machine has enough memory.

Write following to `../inventory/hosts`:

```conf
[masters]
kube-master

[nodes]
kube-node1
kube-node2
kube-node3

[etcd]
kube-master
```

Just run `vagrant up` in this directory and the cluster will get up and running.

ssh into kube-master by `vagrant ssh kube-master`, configure bashrc

```bash
$ echo 'export PATH=/opt/bin:$PATH' >> ~/.bashrc
$ echo 'source <(kubectl completion bash)' >> ~/.bashrc
$ source ~/.bashrc
```

then enjoy exploring your cluster with kubectl.

If you'd like to access kubernetes cluster from web browser, you can install nginx, apache or haproxy. Take nginx for example, install nginx on master and copy this to `/etc/nginx/sites-enabled/k8s` and restart nginx

```
server {
    listen 80;
	server_name kube-cluster.local;
	location / {
	    proxy_pass http://127.0.0.1:8080;
	}
}
```

write `127.0.0.1 kube-cluster.local` to host machine's `/etc/hosts`, now open http://kube-cluster.local:38080/ui with your browser and there you go.
