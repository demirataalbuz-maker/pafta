---
id: pk27
title: LDAP · Bind Yanıtı ve Arama Kökü
summary: LDAP paket alanlarını LDAP filtre dilinden ve Kerberos hata numaralarından ayır.
---

::: anlat Protokol alanından kanıta
`ldap-lab` korpusu LDAP BER mesajları içerir: anonim BindRequest ve örnek BindResponse sonuçları 0/48/49/50; iki farklı baseObject ile SearchRequest ve SearchResultDone. Bunlar durum alanlarını öğretmek için üretilmiş bağımsız tel-biçimi tanıklarıdır; bir sunucunun aynı anonim isteklere gerçekten bu cevapların hepsini verdiği veya bir AD oturumu açıldığı iddia edilmez.

Bind yanıtında doğru TShark alanı `ldap.bindResponse_resultCode`dur. SearchResultDone için kullanılan `ldap.resultCode` ile alan adını karıştırma. RFC 4511'de 48 inappropriateAuthentication, 49 invalidCredentials, 50 insufficientAccessRights'tır. 49 görmek hangi gerçek parolanın denendiğini tek başına söylemez. `ldap.baseObject` arama kökünü gösterir. Paket görüntü filtresi `ldap.baseObject == "DC=lab,DC=test"` ile dizin sorgusu `(objectClass=person)` farklı dillerdir.

LDAPS/StartTLS veya SASL koruması bulunan başka kayıtta aynı açık alanların görüneceği varsayılmaz. Pakette alanın yokluğu olayın gerçekleşmediği kanıtı değildir; bu korpus açık LDAP mesajlarını öğretir.

Kaynak: [LDAP alanları](https://www.wireshark.org/docs/dfref/l/ldap.html), [RFC 4511](https://www.rfc-editor.org/rfc/rfc4511.html).
```meta
dil: wireshark
```
```stdin
{"dil": "wireshark", "kayit": "ldap-lab"}
```
:::

::: tahmin
Bu filtre seçili korpusta hangi frame numaralarını döndürür?
```wireshark
ldap.bindResponse_resultCode == 49
```
```meta
dil: wireshark
```
```stdin
{"dil": "wireshark", "kayit": "ldap-lab"}
```
???
Paketler: 9
Bind sonucu 49 olan mesaj seçilir; SearchResultDone alanı başka bir alan adıdır.
:::

::: gorev Bind hatası 49
Yalnız BindResponse sonuç kodu 49 olan frame'leri seç. 0, 48 ve 50 dahil olmasın.
```starter
frame.number == 0
```
```meta
dil: wireshark
```
```stdin
{"dil": "wireshark", "kayit": "ldap-lab"}
```
```test
eq(eslesenler(),[9],"0/48/49/50 sonuç tanıkları")
import packet_advanced_fixtures as af
eq(eslesenler(af.shifted_capture("ldap-lab")),[10],"frame numarası sabit değil")
eq(eslesenler("kerberos-lab"),[],"Kerberos hata alanı değildir")
```
```solution
ldap.bindResponse_resultCode == 49
```
```hint
Alanı ve istenen tam değeri birlikte kullan; frame numarası sabitleme.
```
:::

::: gorev Arama kökünü doğrula
Arama baseObject alanı tam DC=lab,DC=test olan frame'i seç. DC=other,DC=test dahil olmasın.
```starter
frame.number == 0
```
```meta
dil: wireshark
```
```stdin
{"dil": "wireshark", "kayit": "ldap-lab"}
```
```test
eq(eslesenler(),[12],"iki farklı arama kökü")
import packet_advanced_fixtures as af
eq(eslesenler(af.shifted_capture("ldap-lab")),[13],"sıra değişti")
eq(eslesenler("temel"),[],"başka protokol")
```
```solution
ldap.baseObject == "DC=lab,DC=test"
```
```hint
Alanı ve istenen tam değeri birlikte kullan; frame numarası sabitleme.
```
:::
