#!/usr/bin/env bash
set -eu
org=kclhi-ca
org_name=kclhi

openssl genpkey -algorithm RSA -out $org_name.key -pkeyopt rsa_keygen_bits:4096
openssl req -x509 -key $org_name.key -days 365 -out $org_name.crt \
    -subj "/CN=$org/O=$org"
