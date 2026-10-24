---
id: pk23
title: TCP · Segment, Yeniden İletim ve Kayıp
summary: Tek frame ile tamamlanan uygulama mesajını ayır; TCP analysis etiketini kanıtla birlikte yorumla.
---

::: anlat Paket sırası uygulama mesajı değildir
`tcp-tam` kaydındaki HTTP isteği iki TCP segmentine ayrılmıştır. HTTP yanıtı da iki segmenttir; gövde `PAFTA-TCP-LAB` toplam 13 bayttır. `http.request` son istek segmentinde, `http.response` son yanıt segmentinde görünür. İlk segmentte HTTP alanı bulunmaması mesajın hiç gönderilmediğini kanıtlamaz.

`tcp-tekrar` aynı yanıt segmentini tekrar içerir; `tcp-kayip` son gövde baytlarını içermez; `tcp-sirasiz` yanıtın ortasını sonundan sonra taşır. Bunlar ağdan alınan kullanıcı trafiği değil, doğru sequence/ack ve checksum alanlarıyla üretilmiş eğitim kayıtlarıdır. TShark'ın `tcp.analysis.*` etiketleri kaydın bağlamına ve tercihlere bağlı analist ipuçlarıdır. Sırasız üretilen korpusta geç gelen segment bu sürümde retransmission etiketi alır; yalnız etiketten gerçek ağda yeniden gönderim kanıtı çıkarma. Sequence numarası, zaman, eksik bölüm ve Follow Stream birlikte incelenir.

Kaynak: [TCP analysis](https://www.wireshark.org/docs/wsug_html_chunked/ChAdvTCPAnalysis.html), [yeniden birleştirme](https://www.wireshark.org/docs/wsug_html_chunked/ChAdvReassemblySection.html).
```meta
dil: wireshark
```
```stdin
{"dil":"wireshark","kayit":"tcp-tekrar"}
```
:::

::: tahmin
Kasıtlı tekrarlı kayıtta analysis etiketi hangi frame'i seçer?
```wireshark
tcp.analysis.retransmission
```
```meta
dil: wireshark
```
```stdin
{"dil":"wireshark","kayit":"tcp-tekrar"}
```
???
Paketler: 8
Korpusta son paket önce gönderilmiş yanıt segmentinin aynısıdır. Etiket bu kayıttaki sıra ve zaman bağlamında hesaplanır.
:::

::: gorev Native yeniden iletim etiketi
TShark'ın `tcp.analysis.retransmission` alanıyla işaretlediği frame'leri seç; her TCP segmenti dahil olmasın.
```starter
frame.number == 0
```
```meta
dil: wireshark
```
```stdin
{"dil":"wireshark","kayit":"tcp-tekrar"}
```
```test
eq(eslesenler(),[8],"kasıtlı tekrar")
eq(eslesenler("tcp-tam"),[],"tam ve tekrarsız")
eq(eslesenler("tcp-kayip"),[],"son segment yokluğu yeniden gönderim değildir")
import packet_advanced_fixtures as af
eq(eslesenler(af.shifted_capture("tcp-tekrar")),[9],"frame numarası değişti")
```
```solution
tcp.analysis.retransmission
```
```hint
tcp.flags veya tcp.len yerine analysis alanının varlığını sorgula.
```
:::

::: gorev Yeniden birleştirilmiş istek yolu
Yalnız HTTP **isteği** olup istek yolu tam `/download` olan frame'i seç. Yolun yalnız tek segmentte görünmesini bekleme. TShark ilişkili yanıt paketine de istek URI'sini ekleyebilir; `http.request` şartını ayrıca kullan.
```starter
frame.number == 0
```
```meta
dil: wireshark
```
```stdin
{"dil":"wireshark","kayit":"tcp-tam"}
```
```test
eq(eslesenler(),[5],"iki segmentli istek son segmentte çözülür")
eq(eslesenler("tcp-kayip"),[5],"yanıt eksik olsa da istek tam")
eq(eslesenler("olay"),[],"başka HTTP yolları")
import packet_advanced_fixtures as af
eq(eslesenler(af.shifted_capture("tcp-tam")),[6],"başka frame başlangıcı")
```
```solution
http.request and http.request.uri == "/download"
```
```hint
tcp contains ile tek frame yükünü aramak yerine HTTP ayrıştırıcısının alanını sorgula.
```
:::
