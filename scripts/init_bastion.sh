#!/bin/bash -ex

user=${1:-ec2-user}

tag=${2:-v3.0.0-rc.1}

### change workspace
cd /home/${user}

chmod 600 /home/${user}/.ssh/{aws.key,config}
sudo yum -y install python-pip git
if [[ ! -e tidb-ansible ]]
then
	git clone -b $tag https://github.com/pingcap/tidb-ansible.git
fi
sudo pip install -r ./tidb-ansible/requirements.txt
