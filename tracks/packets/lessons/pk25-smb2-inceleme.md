---
id: pk25
title: SMB2 · Komut, Yön ve Durum
summary: SMB2 istek/yanıtını, NTSTATUS değerini ve şifreli zarf sınırını incele.
---

::: anlat Protokol alanından kanıta
`smb-lab` eğitim korpusu SMB2 Negotiate ve Tree Connect istek/yanıtları içerir. `smb2.cmd` komutu, `smb2.flags.response` yönü, `smb2.nt_status` yanıt durumunu gösterir. Komut 3 hem istek hem yanıtta bulunur; yalnız komut numarası istek seçmeye yetmez. Message ID (`smb2.msg_id`) eşleştirmede yararlıdır, tek başına bütün bağlantılarda global kimlik değildir.

Son frame gerçek AES-CCM ile şifrelenmiş SMB3 Transform zarfıdır. Başlık metadata'sı görünürken iç SMB2 komutu görünmez. Üretici Scapy kodlayıcısı ve sabit eğitim anahtarı kullanır; bir Windows sunucusuna bağlanılmaz. Bu pasif bayt örnekleri gerçek bir domaine giriş veya doğrulanmış SMB oturumu kurulduğunu iddia etmez. Negotiate içindeki imzalama/şifreleme yeteneği de sonraki her paketin doğrulandığını kanıtlamaz.

Kaynak: [SMB2 alanları](https://www.wireshark.org/docs/dfref/s/smb2.html).
```meta
dil: wireshark
```
```stdin
{"dil": "wireshark", "kayit": "smb-lab"}
```
:::

::: tahmin
Bu filtre seçili korpusta hangi frame numaralarını döndürür?
```wireshark
smb2.nt_status == 0xc0000022
```
```meta
dil: wireshark
```
```stdin
{"dil": "wireshark", "kayit": "smb-lab"}
```
???
Paketler: 9
Bu örnekte ACCESS_DENIED durumlu yanıt seçilir; başarılı yanıt ve farklı hata hariçtir.
:::

::: gorev Tree Connect isteklerini seç
Komut 3 olup yanıt bayrağı kapalı olan SMB2 frame'lerini seç.
```starter
frame.number == 0
```
```meta
dil: wireshark
```
```stdin
{"dil": "wireshark", "kayit": "smb-lab"}
```
```test
eq(eslesenler(),[6,8,10],"komut 3 istek; Negotiate ve yanıtlar hariç")
import packet_advanced_fixtures as af
eq(eslesenler(af.shifted_capture("smb-lab")),[7,9,11],"frame başlangıcı değişti")
eq(eslesenler("temel"),[],"TCP tek başına SMB2 değildir")
eq(referans("smb2.header.transform.flags.encrypted"),[12],"şifreli zarf tanığı")
ok(12 not in eslesenler(),"şifreli iç komut görünmez")
```
```solution
smb2.cmd == 3 and smb2.flags.response == 0
```
```hint
Alanı ve istenen tam değeri birlikte kullan; frame numarası sabitleme.
```
:::

::: gorev Belirli NTSTATUS yanıtı
NTSTATUS değeri tam 0xc0000022 olan yanıtları seç; başarı 0 ve LOGON_FAILURE 0xc000006d dahil olmasın.
```starter
frame.number == 0
```
```meta
dil: wireshark
```
```stdin
{"dil": "wireshark", "kayit": "smb-lab"}
```
```test
eq(eslesenler(),[9],"başarı ve başka hata farklı")
import packet_advanced_fixtures as af
eq(eslesenler(af.shifted_capture("smb-lab")),[10],"frame ezberi değil")
eq(eslesenler("ldap-lab"),[],"başka protokol hata alanı")
```
```solution
smb2.nt_status == 0xc0000022
```
```hint
Alanı ve istenen tam değeri birlikte kullan; frame numarası sabitleme.
```
:::
