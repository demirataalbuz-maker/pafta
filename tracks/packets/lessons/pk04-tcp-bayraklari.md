---
id: pk04
title: TCP Bayrakları · Varlık ve Değer
summary: tcp.flags.syn alanının bulunması SYN değerinin 1 olduğu anlamına gelmez; ilk SYN ile SYN/ACK ayır.
---

::: anlat Boolean alan da sıfır olabilir
Görüntü filtresinde alan adını tek başına yazmak **varlığı** sınar. `tcp.flags.syn`, SYN bayrağının değeri sıfır olduğunda da TCP başlığında vardır. Yalnız SYN biti açık paket için `tcp.flags.syn == 1` yazılır.

```wireshark
tcp.flags.syn == 1
```

Bu alan boolean türündedir: filtrede `true` veya **sıfır dışındaki her sayı** doğru; `false` veya 0 yanlış anlamına gelir. Dolayısıyla `tcp.flags.syn == 2` ile `== 1` aynı sonucu verir; SYN bitinin sayısal maskesinin 2 olmasıyla karıştırma. Açıklık için `tcp.flags.syn == true` de yazabilirsin.

Bayraklar paket düzeyinde bilgidir. Bir SYN görmek bağlantının tamamlandığını; bir ACK görmek uygulama isteğinin başarılı olduğunu kanıtlamaz. El sıkışmasını ve uygulama yanıtlarını bağlam içinde incelemek gerekir. Kaynaklar: [Boolean değerler](https://www.wireshark.org/docs/man-pages/wireshark-filter.html), [Boolean alanların varlığı](https://www.wireshark.org/docs/wsug_html_chunked/ChWorkBuildDisplayFilterSection.html).

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```
:::

::: anlat SYN ile SYN/ACK farklı sorulardır
İlk bağlantı açma adayını görmek için SYN=1 ve ACK=0 istenebilir. Sunucunun SYN/ACK yanıtı SYN=1 olsa da ikinci koşulu sağlamaz. RST ile FIN de farklı kapanış işaretleridir; ikisini aynı anlamda yorumlamamalısın.

```wireshark
tcp.flags.syn == 1 and tcp.flags.ack == 0
```

Testler SYN, SYN/ACK, ACK, RST ve FIN/ACK başlıklarını ayrı örnekler olarak kullanır. UDP'de TCP bayrak alanı bulunmadığından pozitif bayrak karşılaştırmaları başarısızdır. Bu ders belirli bir tarama aracını veya saldırganı tanımaya çalışmaz; gözlenen başlık koşulunu doğru ifade eder. Kaynak: [TCP bayrak alanları](https://www.wireshark.org/docs/dfref/t/tcp.html).

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```
:::

::: tahmin
Aşağıdaki tablo seçili sentetik kaydın bu soru için gereken **bütün frame** alanlarını gösterir. Aynı alan değerleri bir satırda gruplandı; `—` o alanın bulunmadığı anlamına gelir. Hangi frame numaraları görünür? Sonuç kayıt sırasıyla, numaraları artarak yazılır.

| Frame numaraları | `tcp.flags.syn` | `tcp.flags.ack` |
| --- | --- | --- |
| 1, 2, 3, 4, 14, 16, 17, 18 | — | — |
| 5, 10, 15 | `True` | `False` |
| 6, 11 | `True` | `True` |
| 7, 8, 9, 12, 13, 19, 20, 21, 22, 23, 24 | `False` | `True` |

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```

```wireshark
tcp.flags.syn == 1 and tcp.flags.ack == 0
```

???

```text
Paketler: 5, 10, 15
```

SYN açık ve ACK kapalı olan başlıklar görünür. SYN/ACK, yalnız ACK ve TCP dışı paketler kalmaz.
:::

::: gorev İlk SYN adayları

TCP paketlerinde SYN=1 ve ACK=0 olanları göster. Yalnız alan varlığına bakma; SYN/ACK ve ACK paketlerini dışarıda bırak.

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
beklenenler = {'temel': [5, 10, 15], 'sinirlar': [1, 6, 12, 13, 29, 30, 32, 33], 'olay': [3, 18]}
for kayit, beklenen in beklenenler.items():
    eq(referans('tcp.flags.syn == 1 and tcp.flags.ack == 0', kayit=kayit, dil="wireshark"), beklenen, kayit + ": sabit kimliklerin native sağlaması")
    eq(eslesenler(kayit=kayit), beklenen, kayit + ": öğrenci filtresinin paket kümesi")

import packet_fixtures as pf
def tcp4(sport=40000, dport=80, payload=b"", src="10.0.0.10", dst="10.0.0.20", flags=0x18):
    segment = pf.tcp(sport, dport, payload, src=src, dst=dst, flags=flags)
    return pf.ethernet(pf.ipv4(segment, src, dst, 6))
def udp4(sport=53000, dport=53, payload=b"", src="10.0.0.10", dst="10.0.0.53"):
    segment = pf.udp(sport, dport, payload, src=src, dst=dst)
    return pf.ethernet(pf.ipv4(segment, src, dst, 17))

frames = [tcp4(sport=43000+i, flags=flags) for i, flags in enumerate((0, 2, 16, 18, 4, 1, 17, 3, 0xc2))]
frames += [udp4()]
eq(eslesenler(kayit=pf.pcap_bytes(frames)), [2, 8, 9], "SYN/ACK ayrımı ve başka bitlerle SYN")
```

```solution
tcp.flags.syn == 1 and tcp.flags.ack == 0
```

```hint
Her iki boolean alanı açıkça 1 veya 0 ile karşılaştır.
```

:::

::: gorev RST veya FIN

RST biti açık **veya** FIN biti açık TCP paketlerini göster. SYN ve sıradan ACK tek başına yeterli olmasın. Bayrakların diğer bitleri açık olabilir.

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
beklenenler = {'temel': [], 'sinirlar': [9, 10], 'olay': []}
for kayit, beklenen in beklenenler.items():
    eq(referans('tcp.flags.reset == 1 or tcp.flags.fin == 1', kayit=kayit, dil="wireshark"), beklenen, kayit + ": sabit kimliklerin native sağlaması")
    eq(eslesenler(kayit=kayit), beklenen, kayit + ": öğrenci filtresinin paket kümesi")

import packet_fixtures as pf
def tcp4(sport=40000, dport=80, payload=b"", src="10.0.0.10", dst="10.0.0.20", flags=0x18):
    segment = pf.tcp(sport, dport, payload, src=src, dst=dst, flags=flags)
    return pf.ethernet(pf.ipv4(segment, src, dst, 6))
def udp4(sport=53000, dport=53, payload=b"", src="10.0.0.10", dst="10.0.0.53"):
    segment = pf.udp(sport, dport, payload, src=src, dst=dst)
    return pf.ethernet(pf.ipv4(segment, src, dst, 17))

frames = [tcp4(sport=43000+i, flags=flags) for i, flags in enumerate((0, 2, 16, 18, 4, 1, 17, 3, 0xc2))]
frames += [udp4()]
eq(eslesenler(kayit=pf.pcap_bytes(frames)), [5, 6, 7, 8], "RST, FIN, FIN/ACK ve SYN/FIN ayrı tanıklar")
```

```solution
tcp.flags.reset == 1 or tcp.flags.fin == 1
```

```hint
Eşitlikler arasında or kullan; bütün flags baytını tek sayıya eşitlemek diğer bitleri yanlış dışlayabilir.
```

:::
