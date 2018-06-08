#!/bin/bash

export LANG=en_US.UTF-8
export TZ="Asia/Shanghai"

NODE_LIST="t001 t002 t003 t004"
NODE_LIST_TIKV="t002 t003 t004"
NODE_LIST_TIDB="t001"
NODE_LIST_PD="t001 t002 t003"

# breakpoint resume for scp
function rscp() {
  if [ -z "$1" -o -z "$2" ] ; then
    echo "Usage: rscp src target"
  else
    while true ; do
      rsync -v -P -e "ssh " $1 $2
      if [ $? -eq 0 ] ; then
        break
      else
        sleep 1; echo try again at $(date)...
      fi
    done
  fi
}
alias rscp=rscp

function cls_cp() {
  SELF="`hostname`"

  if [ -z "$NODE_LIST" ]; then
    echo
    echo Error: NODE_LIST environment variable must be set in .bash_profile
    exit 1
  fi

  if [[ $1 = '--tikv' ]]; then
     shift
     HOST_LIST=$NODE_LIST_TIKV
  elif [[ $1 = '--tidb' ]]; then
     shift
     HOST_LIST=$NODE_LIST_TIDB
  elif [[ $1 = '--pd' ]]; then
     shift
     HOST_LIST=$NODE_LIST_PD
  else
     HOST_LIST=$NODE_LIST
  fi

  if [[ "$1" = '--background' ]]; then
    shift
    for i in $HOST_LIST; do
      if [ ! "$i" = "$SELF" ]; then
        if [ "$1" = "-r" ]; then
          scp $sshauth -oStrictHostKeyChecking=no -r $2 $i:$3 &
        else
          scp $sshauth -oStrictHostKeyChecking=no $1 $i:$2 &
        fi
      fi
    done
    wait
  else
    for i in $HOST_LIST; do
      if [ ! "$i" = "$SELF" ]; then
        if [ "$1" = "-r" ]; then
          scp $sshauth -oStrictHostKeyChecking=no -r $2 $i:$3
        else
          scp $sshauth -oStrictHostKeyChecking=no $1 $i:$2
        fi
      fi
    done
  fi
}
alias cls_cp=cls_cp

function cls_run() {
  if [ -z "$NODE_LIST" ]; then
    echo
    echo Error: NODE_LIST environment variable must be set in .bash_profile
    exit 1
  fi

  if [[ $1 = '--tikv' ]]; then
     shift
     HOST_LIST=$NODE_LIST_TIKV
  elif [[ $1 = '--tidb' ]]; then
     shift
     HOST_LIST=$NODE_LIST_TIDB
  elif [[ $1 = '--pd' ]]; then
     shift
     HOST_LIST=$NODE_LIST_PD
  else
     HOST_LIST=$NODE_LIST
  fi

  if [[ $1 = '--background' ]]; then
    shift
    for i in $HOST_LIST; do
      ssh $sshauth -oStrictHostKeyChecking=no -n $i "$@" &
    done
    wait
  else
    for i in $HOST_LIST; do
      ssh $sshauth -oStrictHostKeyChecking=no $i "$@"
    done
  fi
}
alias cls_run=cls_run

export TERM=linux
