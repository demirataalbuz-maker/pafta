set -e
U=$(python3 -c "import json;print(json.load(open('/lab/lab-secret.json'))['user'])")
B="DC=pafta,DC=test"
samba-tool ou list | grep -q PaftaLab || samba-tool ou add "OU=PaftaLab,$B" >/dev/null
for u in svc_sql ali.kaya mehmet.yilmaz pf_s4u_user; do
  samba-tool user show $u >/dev/null 2>&1 || samba-tool user add $u "$U" --userou=OU=PaftaLab >/dev/null
done
samba-tool group show SOC-Analistleri >/dev/null 2>&1 || samba-tool group add SOC-Analistleri --groupou=OU=PaftaLab >/dev/null
samba-tool group addmembers SOC-Analistleri ali.kaya,mehmet.yilmaz >/dev/null 2>&1 || true
G=$(samba-tool group show SOC-Analistleri --attributes=objectSid | awk '/objectSid/{print $2}')
M=$(samba-tool user show mehmet.yilmaz --attributes=objectSid | awk '/objectSid/{print $2}')
D="CN=svc_sql,OU=PaftaLab,$B"
samba-tool dsacl get --objectdn="$D" | grep -q "$G" || samba-tool dsacl set --objectdn="$D" --sddl="(A;;WD;;;$G)" >/dev/null
samba-tool dsacl get --objectdn="$D" | grep -q "(D;;WD;;;$M)" || samba-tool dsacl set --objectdn="$D" --sddl="(D;;WD;;;$M)" >/dev/null
echo "group=$G mehmet=$M"
samba-tool dsacl get --objectdn="$D" | sed 's/.*D:/D:/' | tr ')' '\n' | grep -n -E "WD|^D:" | head
