# no 60 — Samba AD DC canlı kanıtı (30.10.2026)

Kapsam: no 60 (AD13–AD15) için "AD15 gerçek DC kabulü yok" eksiğine **Windows dışı** bir canlı DC ile yaklaşım. Bu bir Windows `AccessCheck` kabulü **değildir**; denetçi kararı bekler.

## Ortam

- Samba AD DC 4.22.11 (Debian trixie `samba-ad-dc`), Docker konteyneri `pafta-samba-dc`, ağ `pafta-samba` 172.30.88.0/24, etki alanı `pafta.test`, DC `dc1`.
- Nesneler AD15 ile aynı: `OU=PaftaLab` altında `svc_sql`, `ali.kaya`, `mehmet.yilmaz`, `pf_s4u_user`; `SOC-Analistleri` (ali + mehmet). `svc_sql` DACL'i: `SOC-Analistleri` WriteDacl allow, `mehmet.yilmaz` WriteDacl deny (Samba kanonik sırada deny'ı öne koydu).
- Parolalar `%LOCALAPPDATA%/Pafta/labs/samba/lab-secret.json` içinde, Git dışında; bu klasördeki dosyalarda parola yok.
- Lab ayarı: `ldap server require strong auth = no` eklendi (Samba varsayılanı imzasız SASL'i reddeder).

## 1. Canlı BloodHound CE toplaması

`bloodhound-ce-python` 1.9.1, **normal kullanıcı** `ali.kaya` ile Kerberos üzerinden: 8 kullanıcı, 43 grup, 2 GPO, 2 OU, 20 container, 1 bilgisayar. Çıktı: `20261030090341_bloodhound.zip`.

Grafikte: `ALI.KAYA` ve `MEHMET.YILMAZ` → MemberOf → `SOC-ANALISTLERI` → WriteDacl (explicit) → `SVC_SQL`.

**Öğretici bulgu:** BloodHound deny ACE'lerini toplamaz. Grafik Mehmet için de WriteDacl yolu gösterir; gerçek DC ise reddeder (aşağıda). AD13–AD15'in "grafik yolu ≠ etkili hak" noktasının canlı örneği.

Toplayıcı Samba/Heimdal ile kutudan çıktığı gibi çalışmadı; üç istemci tarafı uyumluluk yaması gerekti (`impacket_tgs_cksum_patch.py`, yalnız toplayıcı konteynerinde, veri değiştirmez):
1. impacket TGS-REQ authenticator'üne anahtarlı req-body checksum'ı (RFC 4120, key usage 6). Heimdal yoksa `KRB_AP_ERR_INAPP_CKSUM` döner; Windows KDC tolere eder.
2. bloodhound.py SASL mekanizma etiketi `GSSAPI` → `GSS-SPNEGO` (gönderilen blob zaten SPNEGO).
3. Authenticator realm'i büyük harf (Heimdal "Ticket/authenticator don't match").
NTLM yolu kullanılamaz: ldap3 NTLM'i Microsoft'a özgü Sicily bind'idir, Samba desteklemez.

## 2. Canlı WriteDacl izin/ret (DC'nin kendi denetimi)

Her kullanıcı LDAPS ile kendi kimliğiyle bağlanır ve `svc_sql`'in mevcut DACL'ini (SD flags = DACL) geri yazmayı dener. Kararı Samba DC'nin erişim denetimi verir (`success` / `insufficientAccessRights`). Sonra ACL değiştirilip tekrar sorulur ve geri alınır.

| adım | ali.kaya | mehmet.yilmaz | pf_s4u_user |
|---|---|---|---|
| başlangıç (grup allow + mehmet deny) | izin | ret | ret |
| mehmet deny kaldırıldı | izin | izin | ret |
| pf_s4u_user allow eklendi | izin | izin | izin |
| geri alındı | izin | ret | ret |

Beklenen = gözlenen (`writedacl-evidence.json`, `eslesme: true`). Başlangıç satırı AD15'in beklediği `izin / ret / ret` ile aynı. Son durumda DACL başlangıçla aynı (deny önde, grup allow arkada).

## Sınırlar

- Windows `LogonUser` + `AccessCheck(WRITE_DAC)` değil; Samba'nın DSDB erişim denetimidir. AD15'in PowerShell dersi Samba'da çalışmaz; ayrı bir Python/LDAP varyantı yazılmadı.
- WriteDacl testi DACL'i aynı değerle geri yazar; DC izin kontrolünü yine yapar, ama yazma "değişiklik" içermez.
- BloodHound CE arayüzüne/API'sine yükleme bu çalışmada yapılmadı (yalnız toplayıcı çıktısı incelendi).
- Samba ≠ Windows AD; S4U (no 61) ve AD CS (no 62) için kullanılamaz.
- `docs/denetim/puanlar.json` değiştirilmedi; not denetçinindir. Commit yok.

## Yeniden üretme

`Dockerfile` → `pafta-samba-dc:4`; `provision.sh` (domain), `seed.sh` (nesneler + ACE), toplayıcı konteynerde `impacket_tgs_cksum_patch.py` sonra `bloodhound-ce-python ... --auth-method kerberos`, DC içinde `wdtest.py`. Hash'ler `SHA256SUMS`.
