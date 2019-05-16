#!/bin/bash -ex

mkfs -t ext4 /dev/xvdg
sudo -u ec2-user mkdir -p /home/ec2-user/deploy
mount -o noatime,nodelalloc /dev/xvdg /home/ec2-user/deploy
echo /dev/xvdg  /home/ec2-user/deploy ext4 defaults,nofail,noatime 0 2 >> /etc/fstab
