# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://vagrantcloud.com/search.
  config.vm.box_check_update = false
  config.vm.box = "centos/7"
  config.vm.hostname = "ansible"
  config.vm.network "private_network", ip: "172.17.8.102"
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "4096"
    vb.cpus = 2
    vb.name = config.vm.hostname
  end
  config.vm.synced_folder ".", "/vagrant", type: "rsync",
    rsync__verbose: true,
    rsync__auto: true,
    rsync__exclude: ['.git*', 'node_modules*','*.log','*.box','Vagrantfile']
    config.trigger.after :up do |t|
      t.info = "rsync auto"
      t.run = {inline: "vagrant rsync-auto"}
    end
  config.vm.provision "shell", inline: <<-SHELL

## setup tsinghua yum source

sudo sed -e "/mirrorlist/d" -e "s/#baseurl/baseurl/g" -e "s/mirror\.centos\.org/mirrors\.tuna\.tsinghua\.edu\.cn/g" -i /etc/yum.repos.d/CentOS-Base.repo

sudo yum makecache

sudo yum install -y epel-release

## install deppend's yum package
sudo yum install -y python36 python36-devel python36-pip

## setup tsinghua pip source
sudo -u vagrant mkdir /home/vagrant/.pip
cat << EOF | sudo -u vagrant tee  /home/vagrant/.pip/pip.conf
[global]
timeout = 6000
index-url = https://pypi.tuna.tsinghua.edu.cn/simple

[install]
use-mirrors = true
mirrors = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host=pypi.tuna.tsinghua.edu.cn
EOF

sudo -u vagrant python3.6 -m venv /home/vagrant/venv
echo 'source /home/vagrant/venv/bin/activate' >> /home/vagrant/.bash_profile
sudo -u vagrant /home/vagrant/venv/bin/pip install -U pywinrm ansible
  SHELL
end


