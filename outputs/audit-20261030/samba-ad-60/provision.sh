#!/bin/bash
set -euo pipefail
A=$(python3 -c "import json;print(json.load(open('/lab/lab-secret.json'))['admin'])")
U=$(python3 -c "import json;print(json.load(open('/lab/lab-secret.json'))['user'])")
if [ ! -f /var/lib/samba/private/sam.ldb ]; then
  samba-tool domain provision --realm=PAFTA.TEST --domain=PAFTA --server-role=dc \
    --dns-backend=SAMBA_INTERNAL --adminpass="$A" --host-name=dc1 \
    --option="dns forwarder = 127.0.0.1" --option="ldap server require strong auth = no" >/tmp/prov.log
  cp /var/lib/samba/private/krb5.conf /etc/krb5.conf
fi
