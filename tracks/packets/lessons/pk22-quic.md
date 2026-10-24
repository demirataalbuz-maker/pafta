---
id: pk22
title: QUIC · Initial ile Stream Verisini Ayırmak
summary: QUIC paket türleri ve doğru oturum sırlarıyla açılan stream yükü.
---

::: anlat UDP/443, QUIC ve HTTP/3 aynı hüküm değildir
`quic-lab`, kurulu aioquic ile bellekte üretilmiş gerçek QUIC oturumudur; UDP paket baytları korpusa yazılmıştır, ağa gönderilmemiştir. QUIC sürümü, bağlantı kimlikleri ve Initial el sıkışması bazı metadata'yı sağlar. Initial koruması bağlantı başlangıç bilgisinden çözümlenebilir; bunun görülmesi sonraki 1-RTT stream verisinin açıldığı anlamına gelmez.

Bu örnekte ALPN `pafta-lab` ve stream yükü `PAFTA-QUIC-LAB`dır. **HTTP/3 oturumu değildir.** UDP/443'ten veya QUIC varlığından HTTP/3 sonucu çıkarma. `anahtar:"quic-lab"` ilgili eğitim sırlarını verir; `yok` ve `yanlis` durumlarında stream yükü görünmez. Bir UDP datagramında birden fazla QUIC paketi bulunabilir; `quic.long.packet_type` aynı frame'de birden fazla değere sahip olabilir.

Kaynak: [Wireshark QUIC alanları](https://www.wireshark.org/docs/dfref/q/quic.html), [RFC 9001 Initial sırları](https://www.rfc-editor.org/rfc/rfc9001.html#section-5.2).
```meta
dil: wireshark
```
```stdin
{"dil":"wireshark","kayit":"quic-lab","anahtar":"quic-lab"}
```
:::

::: tahmin
Anahtarsız görünümde QUIC Initial türü (0) içeren datagramlar hangileridir?
```wireshark
quic.long.packet_type == 0
```
```meta
dil: wireshark
```
```stdin
{"dil":"wireshark","kayit":"quic-lab"}
```
???
Paketler: 1, 2, 4
Initial metadata'sını ayırt etmek için uygulama stream sırlarına ihtiyaç yoktur. Frame 4'ün tekrar Initial içermesi onu ayrı bir bağlantı kanıtı yapmaz.
:::

::: gorev Initial datagramlarını ayır
QUIC long-header paket türü 0 olan paketleri içeren frame'leri seç. Her UDP paketi veya her QUIC paketi dahil olmasın.
```starter
frame.number == 0
```
```meta
dil: wireshark
```
```stdin
{"dil":"wireshark","kayit":"quic-lab"}
```
```test
eq(eslesenler(),[1,2,4],"Initial ile Handshake/short header farklı")
eq(eslesenler(anahtar="quic-lab"),[1,2,4],"sırlar paket türünü değiştirmez")
eq(eslesenler("temel"),[],"sıradan UDP/443 yeterli değil")
import packet_advanced_fixtures as af
eq(eslesenler(af.shifted_capture("quic-lab")),[2,3,5],"frame numarası ezberlenmez")
```
```solution
quic.long.packet_type == 0
```
```hint
quic.version yerine long.packet_type alanını kullan.
```
:::

::: gorev Gerçek stream yükünü doğrula
QUIC stream verisi tam ASCII `PAFTA-QUIC-LAB` baytları olan paketi seç. Başlık metadata'sı veya başka UDP yükü yeterli olmasın.
```starter
frame.number == 0
```
```meta
dil: wireshark
```
```stdin
{"dil":"wireshark","kayit":"quic-lab","anahtar":"quic-lab"}
```
```test
eq(eslesenler(),[8],"doğru sırlarla gerçek stream verisi")
eq(eslesenler(anahtar="yok"),[],"stream sırları yok")
eq(eslesenler(anahtar="yanlis"),[],"stream sırları yanlış")
eq(eslesenler("tls-h2"),[],"TLS/TCP aynı protokol değil")
import packet_advanced_fixtures as af
eq(eslesenler(af.shifted_capture("quic-lab")),[9],"başka başlangıç frame'i")
```
```solution
quic.stream_data == 50:41:46:54:41:2d:51:55:49:43:2d:4c:41:42
```
```hint
quic.stream_data bir bayt alanıdır; iki noktayla ayrılmış hex baytlarıyla tam eşitlik kur.
```
:::
