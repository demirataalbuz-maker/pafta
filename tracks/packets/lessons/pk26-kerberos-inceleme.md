---
id: pk26
title: Kerberos · İstek ve Ön Kimlik Doğrulama Hatası
summary: AS-REQ, istemci adı ve 23/24/25 hata komşularını ayırt et.
---

::: anlat Protokol alanından kanıta
`kerberos-lab` gerçek Kerberos ASN.1 kodlamasıyla oluşturulmuş pasif örneklerden oluşur: LAB.TEST realm'inde alice ve bob AS-REQ mesajları; hata 23, 24 ve 25. Bir KDC'ye gönderim yoktur; parola veya gerçek bilet toplanmaz. `kerberos.msg_type == 10` AS-REQ, 30 KRB-ERROR mesajını seçer. `kerberos.CNameString` istemci adı alanıdır; yalnız bu alanı kullanınca aynı adı taşıyan hata mesajları da seçilebilir.

RFC 4120'da 23 KDC_ERR_KEY_EXPIRED, 24 KDC_ERR_PREAUTH_FAILED, 25 KDC_ERR_PREAUTH_REQUIRED olarak tanımlanır. PREAUTH_REQUIRED, istemciden ek ön kimlik doğrulama istendiğini bildirir; tek başına yanlış parola veya saldırı kanıtı sayılmaz. Hata kodu, istek/yanıt sırası, kullanıcı ve servis bağlamı birlikte değerlendirilir. Şifrelenmiş bilet içeriğinin bu alanlarla açıldığı varsayılmaz.

Kaynak: [Kerberos alanları](https://www.wireshark.org/docs/dfref/k/kerberos.html), [RFC 4120](https://www.rfc-editor.org/rfc/rfc4120.html).
```meta
dil: wireshark
```
```stdin
{"dil": "wireshark", "kayit": "kerberos-lab"}
```
:::

::: tahmin
Bu filtre seçili korpusta hangi frame numaralarını döndürür?
```wireshark
kerberos.error_code == 24
```
```meta
dil: wireshark
```
```stdin
{"dil": "wireshark", "kayit": "kerberos-lab"}
```
???
Paketler: 3
23 ve 25 farklı hata türleridir; yalnız 24 seçilir.
:::

::: gorev Alice AS-REQ mesajı
Mesaj türü AS-REQ (10) ve istemci adı tam alice olan frame'i seç. Bob isteği ve alice hata mesajları hariç olsun.
```starter
frame.number == 0
```
```meta
dil: wireshark
```
```stdin
{"dil": "wireshark", "kayit": "kerberos-lab"}
```
```test
eq(eslesenler(),[1],"bob AS-REQ ve alice hataları hariç")
import packet_advanced_fixtures as af
eq(eslesenler(af.shifted_capture("kerberos-lab")),[2],"frame sırası değişti")
eq(eslesenler("smb-lab"),[],"başka protokol")
```
```solution
kerberos.msg_type == 10 and kerberos.CNameString == "alice"
```
```hint
Alanı ve istenen tam değeri birlikte kullan; frame numarası sabitleme.
```
:::

::: gorev PREAUTH_FAILED durumunu ayır
Kerberos error_code değeri tam 24 olan mesajları seç; 23 ve 25 dahil olmasın.
```starter
frame.number == 0
```
```meta
dil: wireshark
```
```stdin
{"dil": "wireshark", "kayit": "kerberos-lab"}
```
```test
eq(eslesenler(),[3],"23/24/25 hata komşuları")
import packet_advanced_fixtures as af
eq(eslesenler(af.shifted_capture("kerberos-lab")),[4],"sabit frame yok")
eq(eslesenler("ldap-lab"),[],"LDAP koduyla karıştırma")
```
```solution
kerberos.error_code == 24
```
```hint
Alanı ve istenen tam değeri birlikte kullan; frame numarası sabitleme.
```
:::
