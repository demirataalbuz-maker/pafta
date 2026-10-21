---
id: pk07
title: HTTP · İstek, Yanıt ve Görünürlük
summary: Çözümlenmiş istek alanını porttan ayır; host/URI/metot ve durum kodu sınırlarını native sına.
---

::: anlat HTTP alanı gerçekten görülüyor mu?
`http.request` çözümleyicinin bir HTTP isteği gördüğünü belirtir. Host, URI ve metot alanları ayrı koşullardır. Port 80'deki her TCP segmenti tam bir istek değildir; bazı alanlar yeniden birleştirme tamamlandığında başka bir frame üzerinde görünebilir. Pafta'nın küçük kayıtları bu ilk görevlerde açık ve çözümlenebilir istekler içerir.

```wireshark
http.request and http.request.method == "GET"
```

TLS ile korunan uygulama verisinde bu açık HTTP/1 alanlarının her kayıtta bulunmasını bekleme. SNI veya sertifika verisi varsa ayrı TLS alanlarıyla incelenir; şifreli uygulama içeriği port filtresiyle çözülemez. Bu ders şifre çözme işlemi yapmaz. Kaynak: [HTTP alanları](https://www.wireshark.org/docs/dfref/h/http.html).

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```
:::

::: anlat İstek alanı yanıt alanı değildir
`http.host` çoğunlukla istek tarafındadır. Bir yanıtın durum kodunu filtrelerken host alanının o pakette de bulunduğunu varsaymak hatalı biçimde sonuçları boşaltabilir. İstek-yanıt ilişkisi için akış ve frame bağlantıları ayrıca incelenir.

```wireshark
http.response.code >= 400 and http.response.code <= 499
```

Bu örnek 400 ve 499'u dahil eder; 399 ile 500 dışarıdadır. `>=` yerine `>` yazmak tam 400'ü kaçırır. Uygulama seviyesindeki 4xx yanıt da tek başına saldırı kanıtı değildir; kullanıcının olağan hatalı isteği olabilir. Testler host, yol ve durum koşullarını bozabilen yakın örnekler içerir. Kaynak: [HTTP response alanı](https://www.wireshark.org/docs/dfref/h/http.html).

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```
:::

::: tahmin
Aşağıdaki tablo seçili sentetik kaydın bu soru için gereken **bütün frame** alanlarını gösterir. Aynı alan değerleri bir satırda gruplandı; `—` o alanın bulunmadığı anlamına gelir. Hangi frame numaraları görünür? Sonuç kayıt sırasıyla, numaraları artarak yazılır.

| Frame numaraları | `http.response.code` |
| --- | --- |
| 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 23 | — |
| 9 | `200` |
| 20 | `401` |
| 22 | `400` |
| 24 | `402` |

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```

```wireshark
http.response.code >= 400 and http.response.code <= 499
```

???

```text
Paketler: 20, 22, 24
```

HTTP yanıt kodu 400–499 aralığında olan frame'ler görünür. İstekler bu alanı taşımadığından kalmaz; 500 ve üstü de dışarıdadır.
:::

::: gorev Host ve yönetim yolu

Yalnız çözümlenmiş HTTP GET isteklerinde host tam portal.lab.test ve URI tam /admin olan paketleri göster. Başka host, /health, başka metot ve yanıt paketleri elensin.

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
beklenenler = {'temel': [19], 'sinirlar': [39], 'olay': [6]}
for kayit, beklenen in beklenenler.items():
    eq(referans('http.request and http.request.method == "GET" and http.host == "portal.lab.test" and http.request.uri == "/admin"', kayit=kayit, dil="wireshark"), beklenen, kayit + ": sabit kimliklerin native sağlaması")
    eq(eslesenler(kayit=kayit), beklenen, kayit + ": öğrenci filtresinin paket kümesi")

import packet_fixtures as pf
def tcp4(sport=40000, dport=80, payload=b"", src="10.0.0.10", dst="10.0.0.20", flags=0x18):
    segment = pf.tcp(sport, dport, payload, src=src, dst=dst, flags=flags)
    return pf.ethernet(pf.ipv4(segment, src, dst, 6))
def udp4(sport=53000, dport=53, payload=b"", src="10.0.0.10", dst="10.0.0.53"):
    segment = pf.udp(sport, dport, payload, src=src, dst=dst)
    return pf.ethernet(pf.ipv4(segment, src, dst, 17))

cases = [("/admin", "portal.lab.test", "GET"), ("/admin", "portal.lab.test", "POST"),
         ("/admin", "other.lab.test", "GET"), ("/health", "portal.lab.test", "GET"),
         ("/administration", "portal.lab.test", "GET"), ("/admin?x=1", "portal.lab.test", "GET")]
frames = [tcp4(sport=55000+i, payload=pf.http_request(uri, host, method))
          for i, (uri, host, method) in enumerate(cases)]
frames += [tcp4(sport=80, dport=55999, payload=pf.http_response(401), src="10.0.0.20", dst="10.0.0.10")]
frames += [tcp4(sport=55998, dport=443, payload=pf.tls_client_hello())]
eq(eslesenler(kayit=pf.pcap_bytes(frames)), [1], "Her istek koşulunu tek başına bozan yakın örnekler")
```

```solution
http.request and http.request.method == "GET" and http.host == "portal.lab.test" and http.request.uri == "/admin"
```

```hint
İstek varlığına ek olarak metot, host ve URI eşitliklerinin tamamını iste.
```

:::

::: gorev Dar yanıt aralığı

Yalnız HTTP yanıt kodu 400–401 aralığındaki paketleri göster; iki uç dahil. 399/402 komşuları ve alanı bulunmayan paketler dışarıda kalsın.

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
beklenenler = {'temel': [20, 22], 'sinirlar': [42, 43], 'olay': [7, 13, 24]}
for kayit, beklenen in beklenenler.items():
    eq(referans('http.response.code >= 400 and http.response.code <= 401', kayit=kayit, dil="wireshark"), beklenen, kayit + ": sabit kimliklerin native sağlaması")
    eq(eslesenler(kayit=kayit), beklenen, kayit + ": öğrenci filtresinin paket kümesi")

import packet_fixtures as pf
def tcp4(sport=40000, dport=80, payload=b"", src="10.0.0.10", dst="10.0.0.20", flags=0x18):
    segment = pf.tcp(sport, dport, payload, src=src, dst=dst, flags=flags)
    return pf.ethernet(pf.ipv4(segment, src, dst, 6))
def udp4(sport=53000, dport=53, payload=b"", src="10.0.0.10", dst="10.0.0.53"):
    segment = pf.udp(sport, dport, payload, src=src, dst=dst)
    return pf.ethernet(pf.ipv4(segment, src, dst, 17))

frames = [tcp4(sport=80, dport=56000+i, payload=pf.http_response(status),
               src="10.0.0.20", dst="10.0.0.10")
          for i, status in enumerate((399, 400, 401, 402, 499, 500, 501))]
frames += [tcp4(sport=56998, payload=pf.http_request()), tcp4(sport=56999, flags=2)]
eq(eslesenler(kayit=pf.pcap_bytes(frames)), [2, 3], "399/400/401/402 komşuları ve alanın yokluğu")
```

```solution
http.response.code >= 400 and http.response.code <= 401
```

```hint
Durum kodu sayısaldır; kapalı aralığı iki karşılaştırmayla kur.
```

:::
