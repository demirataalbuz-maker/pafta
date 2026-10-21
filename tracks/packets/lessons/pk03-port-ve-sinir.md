---
id: pk03
title: Portlar · Yön, Kümeler ve Sınırlar
summary: TCP ile UDP portunu ayrı tut; srcport/dstport ve dahil sayısal aralığı native motorla sına.
---

::: anlat Port numarası uygulama ispatı değildir
TCP ve UDP ayrı taşıma protokolleridir. `tcp.port` hem kaynak hem hedef port alanı için değerlendirilebilir; `tcp.dstport` yalnız hedefi sınar. 443 numarası çoğu ortamda HTTPS için kullanılsa da bu numaraya eşleşen her paketin HTTP veya TLS çözümleneceği garanti değildir.

```wireshark
tcp.port in {80, 443}
```

`in` bir değer kümesidir; aynı şartı iki eşitliği `or` ile bağlayarak da yazabilirsin. Burada IP adresini değil port alanını karşılaştırıyoruz. UDP/53 isteği TCP/53 veya SCTP/53 ile aynı küme değildir. Kaynak: [Küme üyeliği](https://www.wireshark.org/docs/man-pages/wireshark-filter.html).

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```
:::

::: anlat Aralık uçlarını ayrı düşün
`tcp.dstport >= 80 and tcp.dstport <= 81` tam 80 ve 81'i içerir. 79 ile 82 komşularıdır ve kalmaz. Port alanının varlığı örtük olarak aranır; UDP paketi bu TCP karşılaştırmalarını sağlamaz.

```wireshark
tcp.dstport >= 80 and tcp.dstport <= 81
```

Aynı kapalı aralık `tcp.dstport in {80..81}` biçiminde de yazılabilir; `..` uçları dahil eder. Bir port aralığı gidiş ve dönüşte aynı davranmaz: sunucu yanıtının kaynak portu 80 olabilir ama hedefi istemcinin geçici portudur. Görev testi bunu ayrıca ayırır. Bu sınır örnekleri gerçek paket başlıklarına yazılmıştır. Kaynaklar: [Aralık üyeliği](https://www.wireshark.org/docs/man-pages/wireshark-filter.html), [TCP alanları](https://www.wireshark.org/docs/dfref/t/tcp.html).

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```
:::

::: tahmin
Aşağıdaki tablo seçili sentetik kaydın bu soru için gereken **bütün frame** alanlarını gösterir. Aynı alan değerleri bir satırda gruplandı; `—` o alanın bulunmadığı anlamına gelir. Hangi frame numaraları görünür? Sonuç kayıt sırasıyla, numaraları artarak yazılır.

| Frame numaraları | `tcp.srcport` | `tcp.dstport` |
| --- | --- | --- |
| 1, 2, 3, 4, 14, 16, 17, 18 | — | — |
| 5, 7, 8 | `40000` | `80` |
| 6, 9 | `80` | `40000` |
| 10, 12, 13 | `40001` | `443` |
| 11 | `443` | `40001` |
| 15 | `40002` | `443` |
| 19 | `41000` | `80` |
| 20 | `80` | `41000` |
| 21 | `41001` | `80` |
| 22 | `80` | `41001` |
| 23 | `41002` | `80` |
| 24 | `80` | `41002` |

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```

```wireshark
tcp.dstport >= 80 and tcp.dstport <= 81
```

???

```text
Paketler: 5, 7, 8, 19, 21, 23
```

Yalnız TCP hedef portu 80 veya 81 olan paketler seçilir. Kaynak portu bu aralıkta olup hedefi başka port olan dönüşler, UDP eşdeğerleri ve aralığın dış komşuları elenir.
:::

::: gorev TCP hedef aralığı

Yalnız TCP hedef portu 80–81 aralığında olan paketleri göster; her iki sınır dahil. 79 ve 82, UDP eşdeğerleri ve sadece kaynak portu 80 olan yanıtlar elensin.

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
beklenenler = {'temel': [5, 7, 8, 19, 21, 23], 'sinirlar': [7, 8, 28, 29, 30, 32, 39, 40, 41], 'olay': [3, 5, 6, 8, 12, 14, 21, 23]}
for kayit, beklenen in beklenenler.items():
    eq(referans('tcp.dstport >= 80 and tcp.dstport <= 81', kayit=kayit, dil="wireshark"), beklenen, kayit + ": sabit kimliklerin native sağlaması")
    eq(eslesenler(kayit=kayit), beklenen, kayit + ": öğrenci filtresinin paket kümesi")

import packet_fixtures as pf
def tcp4(sport=40000, dport=80, payload=b"", src="10.0.0.10", dst="10.0.0.20", flags=0x18):
    segment = pf.tcp(sport, dport, payload, src=src, dst=dst, flags=flags)
    return pf.ethernet(pf.ipv4(segment, src, dst, 6))
def udp4(sport=53000, dport=53, payload=b"", src="10.0.0.10", dst="10.0.0.53"):
    segment = pf.udp(sport, dport, payload, src=src, dst=dst)
    return pf.ethernet(pf.ipv4(segment, src, dst, 17))

frames = [tcp4(dport=p) for p in (79, 80, 81, 82)]
frames += [tcp4(sport=80, dport=9000), udp4(dport=80), udp4(dport=81)]
frames += [pf.ethernet(pf.ipv4(pf.sctp(40000, 80), proto=132))]
v6 = pf.tcp(40000, 80, src="2001:db8::10", dst="2001:db8::20")
frames += [pf.ethernet(pf.ipv6(v6), 0x86dd)]
eq(eslesenler(kayit=pf.pcap_bytes(frames)), [2, 3, 9], "79/80/81/82, yön ve taşıma protokolü")
```

```solution
tcp.dstport >= 80 and tcp.dstport <= 81
```

```hint
Hedef alanında iki sayısal karşılaştırmayı and ile birleştir.
```

:::

::: gorev UDP DNS iki yönde

UDP kaynak veya hedef portu tam 53 olan paketleri göster. TCP/53, SCTP/53 ve UDP 52/54 dışarıda kalsın. DNS çözümlenmesi şart değil; görev taşıma portunu soruyor.

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
beklenenler = {'temel': [3, 4, 14], 'sinirlar': [4, 15, 31, 36, 37, 38], 'olay': [1, 2, 10, 11, 25]}
for kayit, beklenen in beklenenler.items():
    eq(referans('udp.port == 53', kayit=kayit, dil="wireshark"), beklenen, kayit + ": sabit kimliklerin native sağlaması")
    eq(eslesenler(kayit=kayit), beklenen, kayit + ": öğrenci filtresinin paket kümesi")

import packet_fixtures as pf
def tcp4(sport=40000, dport=80, payload=b"", src="10.0.0.10", dst="10.0.0.20", flags=0x18):
    segment = pf.tcp(sport, dport, payload, src=src, dst=dst, flags=flags)
    return pf.ethernet(pf.ipv4(segment, src, dst, 6))
def udp4(sport=53000, dport=53, payload=b"", src="10.0.0.10", dst="10.0.0.53"):
    segment = pf.udp(sport, dport, payload, src=src, dst=dst)
    return pf.ethernet(pf.ipv4(segment, src, dst, 17))

frames = [udp4(dport=p) for p in (52, 53, 54)]
frames += [udp4(sport=p, dport=9000) for p in (52, 53, 54)]
frames += [tcp4(dport=53), pf.ethernet(pf.ipv4(pf.sctp(40000, 53), proto=132))]
v6 = pf.udp(53000, 53, src="2001:db8::10", dst="2001:db8::53")
frames += [pf.ethernet(pf.ipv6(v6, dst="2001:db8::53", next_header=17), 0x86dd)]
eq(eslesenler(kayit=pf.pcap_bytes(frames)), [2, 5, 9], "UDP iki yön; 52/53/54; IPv6 dahil")
```

```solution
udp.port == 53
```

```hint
Taşıma protokolüne ait birleşik port alanını kullan.
```

:::
