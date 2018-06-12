#!/bin/bash

#export ANS_HOME=/home/pingcap/tidb-ansible
PDIP=172.16.10.12:2379

# get command.
obj=$1

case "$obj" in
        "stores")
                echo "######### Get the information of tikv stores . #########"
                curl -s http://$PDIP/pd/api/v1/$obj | egrep '(id|address|state_name|capacity|available|leader_count|region_count)' | awk '{if(NR%7!=0)ORS="\t"; else ORS="\n"}1' | sed 's/[ ][ ]*/  /g' | sed 's/"//g' | sort -k 2 -t ‘:’
                ;;
        "members")
                echo "######### Get the information of pd member leader. #########"
                curl -s http://$PDIP/pd/api/v1/leader | egrep '(name|member_id|http)' | awk '{if(NR%4!=0)ORS="\t"; else ORS="\n"}1' |  sed 's/[ ][ ]*/  /g' | sed 's/"//g' | sort -k 2 -t ‘:’
                echo
                echo "######### Get the information of pd member . #########"
                curl -s  http://$PDIP/pd/api/v1/$obj | egrep '(name|member_id|http)' | awk '{if(NR%4!=0)ORS="\t"; else ORS="\n"}1' |  sed 's/[ ][ ]*/  /g' | sed 's/"//g' | sort -k 2 -t ‘:’
                ;;
        "regions")
                echo "######### Get the information of regions . #########"
                curl -s http://$PDIP/pd/api/v1/$obj | egrep '(id|store_id)' | awk '{if(NR%7!=0)ORS="\t"; else ORS="\n"}1' |  sed 's/[ ][ ]*/  /g' | sed 's/"//g' | sort -k 2 -t ‘:’
                ;;
        "config")
                echo "######### Get the information of config . #########"
                curl -s http://$PDIP/pd/api/v1/$obj
                ;;
        "labels")
                echo "######### Get the information of labels . #########"
                curl -s  http://$PDIP/pd/api/v1/labels/stores | egrep '(id|address|state_name|value)' | awk '{if(NR%4!=0)ORS="\t"; else ORS="\n"}1' | sed 's/[ ][ ]*/  /g' | sed 's/"//g' | sort -k 2 -t ‘:’
                ;;
        *)
                #其它输入
                echo "Usage: $0 stores|members|regions|config|labels"
                ;;
esac
