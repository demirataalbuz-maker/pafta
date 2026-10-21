---
id: pk09
title: Proje · Kapsamlı Paket İncelemesi
summary: Adres, protokol, uygulama ve zaman koşullarını tek filtrede birleştir; her koşulun ayrı yakın karşı örneğini sınar.
---

::: anlat İnceleme sorusunu önce sınırla
Araştırma sorusu “istemci .10 hangi paketleri üretti?” kadar geniş olabilir; ancak bir rapor için alt sorular gerekir. Bu projede kaynak, hedef, protokol ve zaman penceresiyle belirli bir küme oluşturacağız. Bu seçimin kendisi bir olayın zararlı olduğunu veya isteğin sunucuda başarıyla işlendiğini kanıtlamaz.

```wireshark
ip.src == 10.0.0.10 and (dns.flags.response == 0 or http.request)
```

Parantez kaynak kısıtını hem DNS hem HTTP dalına uygular. DNS ve HTTP alanları birbiriyle aynı pakette bulunmak zorunda değildir; bu yüzden dallar or ile bağlanır. Aralarına and koymak iki ayrı uygulama protokolünü aynı paketten istemek olur. Kaynak: [Mantık ifadeleri](https://www.wireshark.org/docs/man-pages/wireshark-filter.html).

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```
:::

::: anlat Boş sonuçta filtreyi ve veriyi ayır
Doğru bir filtre, seçili kayıtta hiç eşleşme üretmeyebilir. Sözdizimi hatası ise ayrı bir sonuçtur ve native motorun hata mesajı gösterilir. Boş sonuçta “trafik hiç olmadı” demeden kayıt süresini, yakalama noktasını, eksik/kısaltılmış paketleri ve çözümlenen alanları kontrol et.

```wireshark
ip.src == 10.0.0.10 and (dns.flags.response == 0 or http.request) and frame.time_relative >= 2 and frame.time_relative <= 4
```

Burada 2 ve 4 saniye dahildir; kaynak yönü de bilinçli seçilmiştir. Yeni bir kayıtta frame numaraları ve göreli sıfır noktası değişebilir. Bu yüzden testler farklı içerik ve sıralamaya sahip sentetik kayıtlar üzerinde aynı filtreyi çalıştırır; tek bir frame listesini ezberlemeye dayanmaz. Kaynaklar: [TShark çevrimdışı okuma](https://www.wireshark.org/docs/man-pages/tshark.html), [Frame zaman alanları](https://www.wireshark.org/docs/dfref/f/frame.html).

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```
:::

::: tahmin
Aşağıdaki tablo seçili sentetik kaydın bu soru için gereken **bütün frame** alanlarını gösterir. Aynı alan değerleri bir satırda gruplandı; `—` o alanın bulunmadığı anlamına gelir. Hangi frame numaraları görünür? Sonuç kayıt sırasıyla, numaraları artarak yazılır.

| Frame numaraları | `ip.src` | `dns.flags.response` | `http.request` |
| --- | --- | --- | --- |
| 1, 2, 15, 18 | — | — | — |
| 3 | `10.0.0.10` | `False` | — |
| 4 | `10.0.0.53` | `True` | — |
| 5, 7, 10, 12, 13, 16, 17 | `10.0.0.10` | — | — |
| 6, 9, 11, 20, 22, 24 | `10.0.0.20` | — | — |
| 8, 19, 21, 23 | `10.0.0.10` | — | `True` |
| 14 | — | `False` | — |

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```

```wireshark
ip.src == 10.0.0.10 and (dns.flags.response == 0 or http.request)
```

???

```text
Paketler: 3, 8, 19, 21, 23
```

Kaynağı .10 olan DNS soruları veya HTTP istekleri seçilir. Sunucu yanıtları ve başka kaynaktan aynı uygulama trafiği, doğru parantez kapsamı sayesinde elenir.
:::

::: gorev İstemcinin iki uygulama dalı

IPv4 kaynağı 10.0.0.10 olan paketler içinde DNS sorusu (response=0) veya çözümlenmiş HTTP isteği olanları göster. Kaynak koşulu iki dala da uygulanmalı; DNS yanıtları ve HTTP yanıtları elensin.

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```

```starter
frame.number < 0
```

```test
beklenenler = {'temel': [3, 8, 19, 21, 23], 'sinirlar': [4, 31, 36, 37, 38, 39, 40, 41], 'olay': [1, 6, 8, 14, 17, 21, 23]}
for kayit, beklenen in beklenenler.items():
    eq(referans('ip.src == 10.0.0.10 and (dns.flags.response == 0 or http.request)', kayit=kayit, dil="wireshark"), beklenen, kayit + ": sabit kimliklerin native sağlaması")
    eq(eslesenler(kayit=kayit), beklenen, kayit + ": öğrenci filtresinin paket kümesi")

import packet_fixtures as pf
def tcp4(sport=40000, dport=80, payload=b"", src="10.0.0.10", dst="10.0.0.20", flags=0x18):
    segment = pf.tcp(sport, dport, payload, src=src, dst=dst, flags=flags)
    return pf.ethernet(pf.ipv4(segment, src, dst, 6))
def udp4(sport=53000, dport=53, payload=b"", src="10.0.0.10", dst="10.0.0.53"):
    segment = pf.udp(sport, dport, payload, src=src, dst=dst)
    return pf.ethernet(pf.ipv4(segment, src, dst, 17))

def question(src="10.0.0.10", response=False):
    data = bytearray(pf.dns_query())
    if response:
        data[2:4] = b"\x81\x80"
    return udp4(payload=bytes(data), src=src)
def request(sport, src="10.0.0.10"):
    return tcp4(sport=sport, src=src, payload=pf.http_request())
def response(sport):
    return tcp4(sport=80, dport=sport, payload=pf.http_response(401))
v6data = pf.udp(53000, 53, pf.dns_query(), src="2001:db8::10", dst="2001:db8::53")
v6dns = pf.ethernet(pf.ipv6(v6data, dst="2001:db8::53", next_header=17), 0x86dd)
# 0.25 saniyelik adımlar: frame 9/13/17, tam 2/3/4 saniyedir.
frames = [pf.ethernet(pf.arp(), 0x0806), tcp4(), udp4(dport=9000), question("10.0.0.11"),
          question(), request(57001), v6dns, question(response=True),
          question(), question("10.0.0.11"), question(response=True), request(57002, "10.0.0.11"),
          request(57003), response(57004), tcp4(sport=57005), udp4(dport=9000),
          question(), question(response=True), request(57006, "10.0.0.11"),
          tcp4(sport=57007, dport=443, payload=pf.tls_client_hello()), request(57008)]
capture = pf.pcap_bytes(frames, step_us=250000)
eq(eslesenler(kayit=capture), [5, 6, 9, 13, 17, 21], "İki uygulama dalı; yanlış kaynak, yanıt ve boş taşıma")
```

```solution
ip.src == 10.0.0.10 and (dns.flags.response == 0 or http.request)
```

```hint
Kaynağı and ile dışarıda tut; iki uygulama dalını parantez içinde or ile bağla.
```

:::

::: gorev Zamanı da daralt

Önceki uygulama/kaynak koşullarını koru ve yalnız frame.time_relative 2–4 saniye aralığındaki paketleri göster; iki uç dahil. Yalnız zaman filtresi yazmak veya kaynak şartını dallardan birine uygulamak yeterli değil.

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```

```starter
frame.number < 0
```

```test
beklenenler = {'temel': [3], 'sinirlar': [4], 'olay': []}
for kayit, beklenen in beklenenler.items():
    eq(referans('ip.src == 10.0.0.10 and (dns.flags.response == 0 or http.request) and frame.time_relative >= 2 and frame.time_relative <= 4', kayit=kayit, dil="wireshark"), beklenen, kayit + ": sabit kimliklerin native sağlaması")
    eq(eslesenler(kayit=kayit), beklenen, kayit + ": öğrenci filtresinin paket kümesi")

import packet_fixtures as pf
def tcp4(sport=40000, dport=80, payload=b"", src="10.0.0.10", dst="10.0.0.20", flags=0x18):
    segment = pf.tcp(sport, dport, payload, src=src, dst=dst, flags=flags)
    return pf.ethernet(pf.ipv4(segment, src, dst, 6))
def udp4(sport=53000, dport=53, payload=b"", src="10.0.0.10", dst="10.0.0.53"):
    segment = pf.udp(sport, dport, payload, src=src, dst=dst)
    return pf.ethernet(pf.ipv4(segment, src, dst, 17))

def question(src="10.0.0.10", response=False):
    data = bytearray(pf.dns_query())
    if response:
        data[2:4] = b"\x81\x80"
    return udp4(payload=bytes(data), src=src)
def request(sport, src="10.0.0.10"):
    return tcp4(sport=sport, src=src, payload=pf.http_request())
def response(sport):
    return tcp4(sport=80, dport=sport, payload=pf.http_response(401))
v6data = pf.udp(53000, 53, pf.dns_query(), src="2001:db8::10", dst="2001:db8::53")
v6dns = pf.ethernet(pf.ipv6(v6data, dst="2001:db8::53", next_header=17), 0x86dd)
# 0.25 saniyelik adımlar: frame 9/13/17, tam 2/3/4 saniyedir.
frames = [pf.ethernet(pf.arp(), 0x0806), tcp4(), udp4(dport=9000), question("10.0.0.11"),
          question(), request(57001), v6dns, question(response=True),
          question(), question("10.0.0.11"), question(response=True), request(57002, "10.0.0.11"),
          request(57003), response(57004), tcp4(sport=57005), udp4(dport=9000),
          question(), question(response=True), request(57006, "10.0.0.11"),
          tcp4(sport=57007, dport=443, payload=pf.tls_client_hello()), request(57008)]
capture = pf.pcap_bytes(frames, step_us=250000)
eq(eslesenler(kayit=capture), [9, 13, 17], "Tam 2/3/4 saniye; 1 ve 5 dışarıda, içerideki karşı örnekler")
```

```solution
ip.src == 10.0.0.10 and (dns.flags.response == 0 or http.request) and frame.time_relative >= 2 and frame.time_relative <= 4
```

```hint
Önceki filtreyi parantez kapsamını bozmadan zamanın iki karşılaştırmasıyla and kullanarak daralt.
```

:::
