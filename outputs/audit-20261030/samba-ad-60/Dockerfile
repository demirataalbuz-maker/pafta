FROM debian:trixie-slim
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      samba samba-ad-dc samba-ad-provision samba-dsdb-modules samba-vfs-modules winbind krb5-user ldb-tools python3-ldap3 python3-pip python3-venv ca-certificates dnsutils \
 && python3 -m venv /opt/bh && /opt/bh/bin/pip install --no-cache-dir bloodhound-ce==1.9.1 \
 && rm -rf /var/lib/apt/lists/* /etc/samba/smb.conf
CMD ["samba","-i","--debug-stdout"]
