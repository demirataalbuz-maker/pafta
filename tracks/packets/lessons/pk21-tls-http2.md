---
id: pk21
title: TLS ve HTTP/2 · Görünürlük ve Oturum Sırları
summary: ClientHello metadata'sıyla çözümlenmiş HTTP/2 verisini ayrı değerlendir.
---

::: anlat SNI görmek HTTP içeriğini görmek değildir
`tls-h2` kaydı Python ssl ile bellekte kurulmuş TLS 1.3 oturumundan üretilir. Uygulama ALPN ile h2 seçer; eğitim istekleri ve 200/201/202 yanıtları gerçek TLS kayıtları içinde şifrelenir. Ağ bağlantısı açılmaz. `tls.handshake.extensions_server_name` bu korpustaki açık ClientHello adını gösterir. Bu alan HTTP yolu veya yanıt kodunu göstermez; ECH kullanılan başka trafikte aynı görünürlüğü varsayma.

Girdi JSON'unda `anahtar` değeri `yok`, `yanlis` veya `tls-h2` olabilir. Sonuncusu yalnız bu eğitim oturumuna ait sırları geçici TShark profiline verir. Kullanıcının tarayıcı anahtarları okunmaz; dosya yolu verilmez. Doğru sırla HTTP/2 alanları çözülür; yanlış veya eksik sır HTTP/2 uygulama verisini açmaz. Port 443 tek başına TLS kanıtı değildir. HTTP/2 bir TCP segmentinde birden fazla frame taşıyabilir; aynı paket içinde iki alanın varlığı her zaman aynı HTTP/2 frame'ine ait olduklarını kanıtlamaz.

Kaynak: [Wireshark TLS çözümleme](https://wiki.wireshark.org/TLS/), [HTTP/2 alanları](https://www.wireshark.org/docs/dfref/h/http2.html).
```meta
dil: wireshark
```
```stdin
{"dil":"wireshark","kayit":"tls-h2","anahtar":"tls-h2"}
```
:::

::: tahmin
Doğru eğitim anahtarıyla HTTP/2 yanıt kodu 201 hangi pakettedir?
```wireshark
http2.headers.status == 201
```
```meta
dil: wireshark
```
```stdin
{"dil":"wireshark","kayit":"tls-h2","anahtar":"tls-h2"}
```
???
Paketler: 18
Doğru oturum sırrı ile HTTP/2 metadata'sı ayrıştırılır. Anahtar yoksa bu filtre boş sonuç verir; “sunucu 201 göndermedi” sonucu çıkarılmaz.
:::

::: gorev ClientHello adını bul
TLS SNI alanı tam `pafta.lab.test` olan paketleri seç. Sır dosyası olmadan da aynı ClientHello bulunabilsin; başka adlar eşleşmesin.
```starter
frame.number == 0
```
```meta
dil: wireshark
```
```stdin
{"dil":"wireshark","kayit":"tls-h2"}
```
```test
eq(eslesenler(),[4],"anahtarsız açık ClientHello")
eq(eslesenler(anahtar="tls-h2"),[4],"anahtar SNI seçimini değiştirmez")
eq(eslesenler("olay"),[],"portal.lab.test başka ad")
import packet_advanced_fixtures as af
eq(eslesenler(af.shifted_capture("tls-h2")),[5],"frame numarası sabit değil")
```
```solution
tls.handshake.extensions_server_name == "pafta.lab.test"
```
```hint
http.host yerine ClientHello içindeki TLS alanını kullan.
```
:::

::: gorev Çözümlenmiş yanıt kodu ve yokluk
HTTP/2 yanıt kodu tam **201** olan paketleri seç. 200 ve 202 dahil olmasın. Aynı kural doğru anahtarla çalışsın; anahtarsız/yanlış anahtarlı görünümde uygulama alanı görünmesin.
```starter
frame.number == 0
```
```meta
dil: wireshark
```
```stdin
{"dil":"wireshark","kayit":"tls-h2","anahtar":"tls-h2"}
```
```test
eq(eslesenler(),[18],"200/201/202 yanıt komşuları")
eq(eslesenler(anahtar="yok"),[],"sırlar yok")
eq(eslesenler(anahtar="yanlis"),[],"yanlış sırlar")
import packet_advanced_fixtures as af
eq(eslesenler(af.shifted_capture("tls-h2")),[19],"frame sırası kaydı")
eq(eslesenler("temel"),[],"HTTP/1 yanıtı HTTP/2 değildir")
```
```solution
http2.headers.status == 201
```
```hint
Bu alan sayısaldır; 201'i tırnak içine alma.
```
:::
