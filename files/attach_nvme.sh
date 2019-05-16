#!/bin/bash -ex

mkfs -t ext4 /dev/nvme0n1
sudo -u ec2-user mkdir -p /home/ec2-user/deploy
mount -o noatime,nodelalloc /dev/nvme0n1 /home/ec2-user/deploy
echo /dev/nvme0n1  /home/ec2-user/deploy ext4 defaults,nofail,noatime,nodelalloc 0 2 >> /etc/fstab
