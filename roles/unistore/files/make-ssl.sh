#!/bin/bash

# Author: Smana smainklh@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -o errexit
set -o pipefail

usage()
{
    cat << EOF
Create self signed certificates

Usage : $(basename $0) [-d <ssldir>]
      -h | --help         : Show this message
      -d | --ssldir       : Directory where the certificates will be located

      Environmental variables HOSTS and CN should be set to generate keys
      for each host.
EOF
}

# Options parsing
while (($#)); do
    case "$1" in
        -h | --help)   usage;   exit 0;;
        -d | --ssldir) SSLDIR="${2}"; shift 2;;
        *)
            usage
            echo "ERROR : Unknown option"
            exit 3
        ;;
    esac
done

if [ -z ${SSLDIR} ]; then
    echo "ERROR: the directory where the certificates will be located is missing. option -d"
    exit 1
fi

tmpdir=$(mktemp -d /tmp/tidb_cacert.XXXXXX)
trap 'rm -rf "${tmpdir}"' EXIT
cd "${tmpdir}"

mkdir -p "${SSLDIR}"

if [ -e "$SSLDIR/ca-config.json" ]; then
    # Reuse existing CA
    cp $SSLDIR/{ca-config.json,ca-csr.json} .
else
    echo "ERROR: ca-config.json and ca-csr.json is missing in $SSLDIR."
    exit 1
fi

# Root CA
if [ -e "$SSLDIR/ca-key.pem" ]; then
    # Reuse existing CA
    cp $SSLDIR/{ca.pem,ca-key.pem} .
else
    cfssl gencert -initca ca-csr.json | cfssljson -bare ca - > /dev/null 2>&1
fi

# client cert
if [ ! -e "$SSLDIR/client-key.pem" ]; then
    echo '{"CN":"client","hosts":[""],"key":{"algo":"rsa","size":2048}}' | cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=client -hostname="" - | cfssljson -bare client > /dev/null 2>&1
fi

gen_key_and_cert() {
    local host=$1
    local cn=$2
    local name=$3
    echo "{\"CN\":\"${cn}\",\"hosts\":[\"\"],\"key\":{\"algo\":\"rsa\",\"size\":2048}}" | cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=server -hostname="${host},127.0.0.1" - | cfssljson -bare ${name} > /dev/null 2>&1
}

# Nodes
if [ -n "$HOSTS" ]; then
    for host in $HOSTS; do
        gen_key_and_cert "${host}" "${CN}" "${CN}-${host}"
    done
fi

# Install certs
mv *.pem ${SSLDIR}/
