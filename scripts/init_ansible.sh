#!/bin/bash -ex

list_tidb=$1
list_tikv=$2
list_pd=$3
list_monitor=$4
time=`date +"%Y%M%d%H%M%S"`

cp /home/ec2-user/tidb-ansible/inventory.ini /home/ec2-user/tidb-ansible/inventory.ini-$time
sed -ri '/^[0-9.]+/d' /home/ec2-user/tidb-ansible/inventory.ini

for tidb in `echo ${list_tidb} | sed 's/,/ /g'`
do
	sed -i "/\[tidb_servers\]/a$tidb" /home/ec2-user/tidb-ansible/inventory.ini
	sed -i "/\[monitored_servers\]/a$tidb" /home/ec2-user/tidb-ansible/inventory.ini
done

for tikv in `echo ${list_tikv} | sed 's/,/ /g'`
do
	sed -i "/\[tikv_servers\]/a$tikv" /home/ec2-user/tidb-ansible/inventory.ini
	sed -i "/\[monitored_servers\]/a$tikv" /home/ec2-user/tidb-ansible/inventory.ini
done

for pd in `echo ${list_pd} | sed 's/,/ /g'`
do
	sed -i "/\[pd_servers\]/a$pd" /home/ec2-user/tidb-ansible/inventory.ini
	sed -i "/\[monitored_servers\]/a$pd" /home/ec2-user/tidb-ansible/inventory.ini
done

for monitor in `echo ${list_monitor} | sed 's/,/ /g'`
do
	sed -i "/\[monitoring_servers\]/a$monitor" /home/ec2-user/tidb-ansible/inventory.ini
	sed -i "/\[grafana_servers\]/a$monitor" /home/ec2-user/tidb-ansible/inventory.ini
	sed -i "/\[monitored_servers\]/a$monitor" /home/ec2-user/tidb-ansible/inventory.ini
done

sed -i 's/\/home\/tidb\/deploy/\/home\/ec2-user\/deploy/' /home/ec2-user/tidb-ansible/inventory.ini
sed -i 's/ansible_user = tidb/ansible_user = ec2-user/' /home/ec2-user/tidb-ansible/inventory.ini
sed -i 's/enable_ntpd = True/enable_ntpd = False/' /home/ec2-user/tidb-ansible/inventory.ini
sed -i 's/dev_mode: False/dev_mode: True/' /home/ec2-user/tidb-ansible/group_vars/all.yml
