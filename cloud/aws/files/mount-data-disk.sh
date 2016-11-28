#!/bin/bash

sudo mkdir -p /data
if [ -e '/mnt/lost+found' ]; then
    echo "Unmount /dev/xvdb from /mnt"
    sudo umount /mnt
fi

if [ -e /dev/xvdb ]; then
    sudo mount /dev/svdb /data
else
    echo "No such device: /dev/xvdb"
    exit 0
fi

if [ $? != 0 ]; then
    sudo mkfs -t ext4 /dev/xvdb
    sudo mount /dev/xvdb /data
    if [ $? != 0 ]; then
	echo "Mount device /dev/xvdb error"
	exit 1
    fi
fi

echo "Make /dev/xvdb auto mount at /data"
echo "/dev/xvdb    /data    ext4    defaults,nofail    0    2" | sudo tee -a /etc/fstab
