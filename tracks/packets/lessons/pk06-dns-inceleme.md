---
id: pk06
title: DNS · Soru, Yanıt ve Ad Alanları
summary: Porttan çözümlenmiş DNS alanına geç; query/response, A/AAAA ve tam ad eşleşmesini ayır.
---

::: anlat UDP/53 ile DNS aynı ifade değildir
Taşıma portu bir aday gösterir; `dns` alanı ise çözümleyicinin pakette DNS yapısı gördüğünü söyler. DNS TCP üzerinde de taşınabilir. Şifreli DNS trafiğinde açık DNS alanları bulunmayabilir; port filtresi bu içeriği kendiliğinden açmaz.

```wireshark
dns.flags.response == 0
```

`dns.flags.response` soru için 0, yanıt için 1 olur. `dns.qry.name` sorulan addır; yanıtta soru bölümü tekrar bulunduğunda bu alan da bulunabilir. Bu nedenle yalnız ada bakmak soru/yanıt ayrımını yapmaz. Kaynak: [DNS alan başvurusu](https://www.wireshark.org/docs/dfref/d/dns.html).

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```
:::

::: anlat Tam ad, parça ve regex
`dns.qry.name == "portal.lab.test"` tam metin eşitliğidir. `contains "lab.test"` başka adların içindeki parçayı da yakalayabilir. Ad alanı içinde kalmak istiyorsan sınırı tarif etmelisin. `matches` PCRE2 regex kullanır ve varsayılan olarak harf duyarsızdır; `contains` ile aynı harf davranışına sahip olduğunu varsayma.

```wireshark
dns.flags.response == 0 and dns.qry.name == "portal.lab.test" and dns.qry.type == 1
```

Örneğin `dns.qry.name contains "lab.test"`, `portal.lab.test` yanında `notlab.test` adını da kabul eder. `dns.qry.name matches r"(^|\.)lab\.test$"` ise noktayla ayrılan `lab.test` son ekini veya bu adın kendisini ister; `notlab.test` elenir. Regex içindeki `\.` gerçek noktadır, sondaki `$` adın bitişini sabitler; `r"..."` Wireshark ham metin gösterimidir. Harf farkı da anlamlıdır: `Portal.Lab.Test`, bu `contains` ifadesinden geçmezken varsayılan harf duyarsız `matches` ifadesinden geçer. Bu örnek ad, olay kaydının 25. frame'indedir.

Tür 1 A, tür 28 AAAA sorusudur; bu **sayısal** tür alanında 2, 1'e eşit değildir. Buna karşılık `dns.flags.response` boolean olduğundan `== 1`, `== true` ve sıfır dışındaki sayıyla eşitlik aynı doğru değeri ister. Her görevde soru bayrağı, ad ve tür gerektiğinde ayrı ayrı sınanır. Görevler `.test` eğitim adlarını kullanır. Kaynaklar: [DNS alanları](https://www.wireshark.org/docs/dfref/d/dns.html), [contains ve matches](https://www.wireshark.org/docs/man-pages/wireshark-filter.html).

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```
:::

::: tahmin
Aşağıdaki tablo seçili sentetik kaydın bu soru için gereken **bütün frame** alanlarını gösterir. Aynı alan değerleri bir satırda gruplandı; `—` o alanın bulunmadığı anlamına gelir. Hangi frame numaraları görünür? Sonuç kayıt sırasıyla, numaraları artarak yazılır.

| Frame numaraları | `dns.flags.response` | `dns.qry.name` | `dns.qry.type` |
| --- | --- | --- | --- |
| 1, 2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24 | — | — | — |
| 3 | `False` | `portal.lab.test` | `1` |
| 4 | `True` | `portal.lab.test` | `1` |
| 14 | `False` | `portal.lab.test` | `28` |

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```

```wireshark
dns.flags.response == 0 and dns.qry.name == "portal.lab.test" and dns.qry.type == 1
```

???

```text
Paketler: 3
```

portal.lab.test için A soruları görünür. Yanıt paketi aynı soru adını taşısa da response=0 koşulundan geçmez; AAAA ve başka adlar da elenir.
:::

::: gorev Belirli A sorusu

Yalnız soru bayrağı 0, soru adı tam portal.lab.test ve soru türü A (1) olan DNS paketlerini göster. Yanıtlar, AAAA ve başka adlar elensin.

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
beklenenler = {'temel': [3], 'sinirlar': [36], 'olay': [1, 17]}
for kayit, beklenen in beklenenler.items():
    eq(referans('dns.flags.response == 0 and dns.qry.name == "portal.lab.test" and dns.qry.type == 1', kayit=kayit, dil="wireshark"), beklenen, kayit + ": sabit kimliklerin native sağlaması")
    eq(eslesenler(kayit=kayit), beklenen, kayit + ": öğrenci filtresinin paket kümesi")

import packet_fixtures as pf
def tcp4(sport=40000, dport=80, payload=b"", src="10.0.0.10", dst="10.0.0.20", flags=0x18):
    segment = pf.tcp(sport, dport, payload, src=src, dst=dst, flags=flags)
    return pf.ethernet(pf.ipv4(segment, src, dst, 6))
def udp4(sport=53000, dport=53, payload=b"", src="10.0.0.10", dst="10.0.0.53"):
    segment = pf.udp(sport, dport, payload, src=src, dst=dst)
    return pf.ethernet(pf.ipv4(segment, src, dst, 17))

frames = []
cases = [(False, "portal.lab.test", 1), (True, "portal.lab.test", 1),
         (False, "portal.lab.test", 28), (True, "portal.lab.test", 28),
         (False, "other.lab.test", 1), (True, "portal.lab.test", 0),
         (True, "portal.lab.test", 2), (True, "portal.lab.test", 27),
         (True, "portal.lab.test", 29), (False, "portal.lab.test", 0),
         (False, "portal.lab.test", 2), (False, "Portal.Lab.Test", 1)]
for i, (response, name, qtype) in enumerate(cases):
    payload = bytearray(pf.dns_query(name, qtype, 0x3000+i))
    if response:
        payload[2:4] = b"\x81\x80"  # Geçerli, soru bölümü bulunan boş yanıt.
    frames += [udp4(sport=54000+i, payload=bytes(payload))]
eq(eslesenler(kayit=pf.pcap_bytes(frames)), [1], "Soru/yanıt, tam ad, tür 0/1/2 ve AAAA")
```

```solution
dns.flags.response == 0 and dns.qry.name == "portal.lab.test" and dns.qry.type == 1
```

```hint
Üç koşulun tamamını and ile iste.
```

:::

::: gorev Yanıtlardaki iki tür

Yalnız DNS yanıtlarından soru türü A (1) veya AAAA (28) olanları göster. Ad kısıtı koyma; sorgu paketleri ve diğer soru türleri elensin.

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
beklenenler = {'temel': [4], 'sinirlar': [15], 'olay': [2, 11]}
for kayit, beklenen in beklenenler.items():
    eq(referans('dns.flags.response == 1 and dns.qry.type in {1, 28}', kayit=kayit, dil="wireshark"), beklenen, kayit + ": sabit kimliklerin native sağlaması")
    eq(eslesenler(kayit=kayit), beklenen, kayit + ": öğrenci filtresinin paket kümesi")

import packet_fixtures as pf
def tcp4(sport=40000, dport=80, payload=b"", src="10.0.0.10", dst="10.0.0.20", flags=0x18):
    segment = pf.tcp(sport, dport, payload, src=src, dst=dst, flags=flags)
    return pf.ethernet(pf.ipv4(segment, src, dst, 6))
def udp4(sport=53000, dport=53, payload=b"", src="10.0.0.10", dst="10.0.0.53"):
    segment = pf.udp(sport, dport, payload, src=src, dst=dst)
    return pf.ethernet(pf.ipv4(segment, src, dst, 17))

frames = []
cases = [(False, "portal.lab.test", 1), (True, "portal.lab.test", 1),
         (False, "portal.lab.test", 28), (True, "portal.lab.test", 28),
         (False, "other.lab.test", 1), (True, "portal.lab.test", 0),
         (True, "portal.lab.test", 2), (True, "portal.lab.test", 27),
         (True, "portal.lab.test", 29), (False, "portal.lab.test", 0),
         (False, "portal.lab.test", 2), (False, "Portal.Lab.Test", 1)]
for i, (response, name, qtype) in enumerate(cases):
    payload = bytearray(pf.dns_query(name, qtype, 0x3000+i))
    if response:
        payload[2:4] = b"\x81\x80"  # Geçerli, soru bölümü bulunan boş yanıt.
    frames += [udp4(sport=54000+i, payload=bytes(payload))]
eq(eslesenler(kayit=pf.pcap_bytes(frames)), [2, 4], "A ve AAAA yanıtları; 0/2 ve 27/29 dışarıda")
```

```solution
dns.flags.response == 1 and dns.qry.type in {1, 28}
```

```hint
Yanıt bayrağı ile tür kümesini birleştir; tür alanı dns.qry.type.
```

:::
