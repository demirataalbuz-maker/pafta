import json, ssl, ldap3, datetime
from ldap3.protocol.microsoft import security_descriptor_control
S = json.load(open('/lab/lab-secret.json'))
DN = 'CN=svc_sql,OU=PaftaLab,DC=pafta,DC=test'
DACL = security_descriptor_control(sdflags=0x04)
tls = ldap3.Tls(validate=ssl.CERT_NONE)  # lab DC uses Samba's auto-generated self-signed cert
srv = ldap3.Server('dc1.pafta.test', port=636, use_ssl=True, tls=tls)
def conn(user, pw):
    c = ldap3.Connection(srv, user=user + '@pafta.test', password=pw)
    assert c.bind(), (user, c.result)
    return c
adm = conn('Administrator', S['admin'])
def sd():
    adm.search(DN, '(objectClass=*)', ldap3.BASE, attributes=['nTSecurityDescriptor'], controls=DACL)
    return adm.entries[0]['nTSecurityDescriptor'].raw_values[0]
def write_dacl(user):
    c = conn(user, S['user'])
    c.modify(DN, {'nTSecurityDescriptor': [(ldap3.MODIFY_REPLACE, [sd()])]}, controls=DACL)
    r = c.result; c.unbind()
    return {'kullanici': user, 'ldap_result': r['result'], 'description': r['description'], 'karar': 'izin' if r['result'] == 0 else 'ret'}
def sddl_deny_present():
    import subprocess
    out = subprocess.run(['samba-tool', 'dsacl', 'get', '--objectdn=' + DN, '-H', 'ldap://dc1.pafta.test', '-U', 'Administrator', '--password=' + S['admin']], capture_output=True, text=True).stdout
    return out
import subprocess
def dsacl(op, sddl):
    r = subprocess.run(['samba-tool', 'dsacl', op, '--objectdn=' + DN, '--sddl=' + sddl], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
def sid(name):
    return subprocess.run(['samba-tool', 'user', 'show', name, '--attributes=objectSid'], capture_output=True, text=True).stdout.split('objectSid: ')[1].split()[0]
M, P = sid('mehmet.yilmaz'), sid('pf_s4u_user')
USERS = ('ali.kaya', 'mehmet.yilmaz', 'pf_s4u_user')
ev = {'zaman': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'nesne': DN, 'adimlar': []}
def step(label):
    ev['adimlar'].append({'durum': label, 'sonuclar': [write_dacl(u) for u in USERS]})
step('baslangic: SOC-Analistleri WriteDacl allow + mehmet.yilmaz deny')
dsacl('delete', '(D;;WD;;;%s)' % M); step('mehmet deny kaldirildi')
dsacl('set', '(A;;WD;;;%s)' % P); step('pf_s4u_user icin WriteDacl allow eklendi')
dsacl('delete', '(A;;WD;;;%s)' % P); dsacl('set', '(D;;WD;;;%s)' % M); step('geri alindi (baslangic ile ayni olmali)')
ev['beklenen'] = [['izin','ret','ret'], ['izin','izin','ret'], ['izin','izin','izin'], ['izin','ret','ret']]
ev['gozlenen'] = [[r['karar'] for r in a['sonuclar']] for a in ev['adimlar']]
ev['eslesme'] = ev['beklenen'] == ev['gozlenen']
json.dump(ev, open('/out/writedacl-evidence.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps({'gozlenen': ev['gozlenen'], 'eslesme': ev['eslesme']}, ensure_ascii=False))
