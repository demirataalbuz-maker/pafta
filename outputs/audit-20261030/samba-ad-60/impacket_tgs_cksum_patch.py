# Heimdal KDC (Samba AD) rejects TGS-REQ authenticators without a keyed req-body
# checksum (KRB_AP_ERR_INAPP_CKSUM); Windows KDCs tolerate it. RFC 4120 5.5.1 / 7.5.1 key usage 6.
import impacket.krb5.kerberosv5 as k, re, sys
p = k.__file__
src = open(p, encoding='utf-8').read()
if 'PAFTA_TGS_CKSUM' in src:
    print('already patched'); sys.exit(0)
start = src.index('def getKerberosTGS(')
anchor = '    message = encoder.encode(tgsReq)\n'
i = src.index(anchor, start)
patch = '''    # PAFTA_TGS_CKSUM: keyed req-body checksum for Heimdal/Samba KDCs
    from impacket.krb5.crypto import _checksum_table
    def _pf_inner(b):
        # req-body is encoded with its explicit [4] context tag; checksum covers the inner KDC-REQ-BODY
        if b[0] != 0xa4: return b
        n = b[1]
        return b[2:] if n < 0x80 else b[2 + (n & 0x7f):]
    _ck = {18: 16, 17: 15, 23: -138}[cipher.enctype]
    authenticator['cksum'] = noValue
    authenticator['cksum']['cksumtype'] = _ck
    authenticator['cksum']['checksum'] = _checksum_table[_ck].checksum(sessionKey, 6, _pf_inner(encoder.encode(reqBody)))
    apReq['authenticator'] = noValue
    apReq['authenticator']['etype'] = cipher.enctype
    apReq['authenticator']['cipher'] = cipher.encrypt(sessionKey, 7, encoder.encode(authenticator), None)
    tgsReq['padata'][0]['padata-value'] = encoder.encode(apReq)
'''
open(p, 'w', encoding='utf-8').write(src[:i] + patch + src[i:])
print('patched', p)

# bloodhound.py sends a SPNEGO NegTokenInit but labels the SASL bind "GSSAPI";
# Samba parses GSSAPI as a raw krb5 token, so label it GSS-SPNEGO (what the blob is).
import bloodhound.ad.authentication as a
q = a.__file__; s = open(q, encoding='utf-8').read()
if 'sasl_mechanism=KERBEROS' in s:
    open(q, 'w', encoding='utf-8').write(s.replace('sasl_mechanism=KERBEROS', 'sasl_mechanism="GSS-SPNEGO"'))
    print('patched', q)

# Heimdal compares the authenticator realm with the ticket's realm case-sensitively
# ("Ticket/authenticator don't match"); Windows does not. Kerberos realms are upper case.
s = open(q, encoding='utf-8').read()
old = "authenticator['crealm'] = self.userdomain\n"
if old in s:
    open(q, 'w', encoding='utf-8').write(s.replace(old, "authenticator['crealm'] = self.userdomain.upper()\n"))
    print('patched crealm', q)
