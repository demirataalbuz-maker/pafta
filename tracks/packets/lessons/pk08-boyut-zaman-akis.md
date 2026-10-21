---
id: pk08
title: Boyut, Zaman ve TCP Akışı
summary: frame.len, frame.time_relative ve tcp.stream farklı boyutlardır; eşiklerle bağlamı daralt.
---

::: anlat Çerçeve boyutu ile uygulama verisi farklıdır
`frame.len` kayıt bilgisindeki çerçevenin özgün uzunluğudur. TCP yük boyutu `tcp.len` ile aynı şey değildir; Ethernet/IP/TCP başlıkları ve başka katmanlar fark yaratır. Yakalama kısaltılmışsa `frame.cap_len` yakalanan kısmı gösterebilir. Bu yüzden “64 bayt veri” derken hangi alanın ölçüldüğünü açıkça belirt.

```wireshark
frame.len >= 64 and frame.len <= 128
```

Bu filtre bütün protokollerde boyut sorar. TCP'ye sınırlamak istiyorsan ayrıca tcp koşulu ekle. Kayıtlarımızda 63/64/65 ve 127/128/129 bayt komşuları eşitlik sınırlarını sınamak için bulunur. Kaynak: [Frame alanları](https://www.wireshark.org/docs/dfref/f/frame.html).

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "sinirlar"}
```
:::

::: anlat Göreli zaman ve akış numarası yereldir
`frame.time_relative`, kaydın başlangıcına göre saniye farkıdır; mutlak UTC saat değildir. `tcp.stream`, TShark'ın bu kayıtta verdiği TCP akış indeksidir; başka kayda ait aynı indeks aynı uçları temsil etmeyebilir. Bu iki değeri global kimlik gibi saklama.

```wireshark
tcp.stream == 0
```

Bir akışa odaklanmak önceki/sonraki paketleri anlamak için yararlı olabilir; fakat segment kaybı, yeniden iletim ve dissector durumunun varlığını da hesaba katmalısın. Bu dersin görevi akış 0 paketlerini seçmek ve boyut eşiğini ayrı okumaktır; tam oturum çıkarıcı yazdırmaz. Göreli zaman penceresinin sınırlarını proje dersinde ayrıca kullanacağız. Kaynaklar: [TCP stream](https://www.wireshark.org/docs/dfref/t/tcp.html), [Frame zaman alanları](https://www.wireshark.org/docs/dfref/f/frame.html).

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "sinirlar"}
```
:::

::: tahmin
Aşağıdaki tablo seçili sentetik kaydın bu soru için gereken **bütün frame** alanlarını gösterir. Aynı alan değerleri bir satırda gruplandı; `—` o alanın bulunmadığı anlamına gelir. Hangi frame numaraları görünür? Sonuç kayıt sırasıyla, numaraları artarak yazılır.

| Frame numaraları | `frame.len` |
| --- | --- |
| 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 27, 28, 29, 30, 32, 48, 49 | `60` |
| 4 | `73` |
| 15 | `89` |
| 16 | `66` |
| 17 | `63` |
| 18, 50 | `64` |
| 19 | `65` |
| 20 | `127` |
| 21 | `128` |
| 22 | `129` |
| 23, 24, 25, 26 | `62` |
| 31 | `80` |
| 33 | `82` |
| 34 | `86` |
| 35 | `70` |
| 36, 37 | `75` |
| 38 | `74` |
| 39 | `146` |
| 40 | `147` |
| 41 | `145` |
| 42 | `149` |
| 43 | `150` |
| 44 | `154` |
| 45 | `152` |
| 46 | `159` |
| 47 | `153` |

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "sinirlar"}
```

```wireshark
frame.len >= 64 and frame.len <= 128
```

???

```text
Paketler: 4, 15, 16, 18, 19, 20, 21, 31, 33, 34, 35, 36, 37, 38, 50
```

Frame uzunluğu tam 64 ve 128 dahil aralıktadır; başlıklar da bu ölçüye dahildir. Bir alt ve üst komşu olan 63 ile 129 kalmaz.
:::

::: gorev Kapalı boyut aralığı

Protokole bakmadan frame.len 64–128 bayt aralığındaki paketleri göster; iki uç dahil. 63 ve 129 dışarıda kalsın. tcp.len ile değiştirme.

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "sinirlar"}
```

```starter
frame.number < 0
```

```test
beklenenler = {'temel': [3, 4, 14, 15, 16, 18], 'sinirlar': [4, 15, 16, 18, 19, 20, 21, 31, 33, 34, 35, 36, 37, 38, 50], 'olay': [1, 2, 10, 11, 17, 18, 20, 25]}
for kayit, beklenen in beklenenler.items():
    eq(referans('frame.len >= 64 and frame.len <= 128', kayit=kayit, dil="wireshark"), beklenen, kayit + ": sabit kimliklerin native sağlaması")
    eq(eslesenler(kayit=kayit), beklenen, kayit + ": öğrenci filtresinin paket kümesi")

import packet_fixtures as pf
def tcp4(sport=40000, dport=80, payload=b"", src="10.0.0.10", dst="10.0.0.20", flags=0x18):
    segment = pf.tcp(sport, dport, payload, src=src, dst=dst, flags=flags)
    return pf.ethernet(pf.ipv4(segment, src, dst, 6))
def udp4(sport=53000, dport=53, payload=b"", src="10.0.0.10", dst="10.0.0.53"):
    segment = pf.udp(sport, dport, payload, src=src, dst=dst)
    return pf.ethernet(pf.ipv4(segment, src, dst, 17))

frames = []
for size in (63, 64, 65, 127, 128, 129):
    data = udp4(dport=9000, payload=b"L"*(size-42))
    frames += [(data, size)]
frames += [(frames[1][0][:36], 64), (frames[5][0][:64], 129)]
eq(eslesenler(kayit=pf.pcap_bytes(frames)), [2, 3, 4, 5, 7], "63/64/65 ve 127/128/129; len ile cap_len ayrımı")
```

```solution
frame.len >= 64 and frame.len <= 128
```

```hint
Ölçü field adı frame.len; iki sayısal şartı and ile bağla.
```

:::

::: gorev Bir TCP akışı

Seçili kayıtta TCP akış indeksi tam 0 olan paketleri göster. Başka TCP akışları ve UDP/ARP dahil olmasın. Bu indeksin yalnız o kayda ait olduğunu unutma.

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
beklenenler = {'temel': [5, 6, 7, 8, 9], 'sinirlar': [1], 'olay': [3, 4, 5]}
for kayit, beklenen in beklenenler.items():
    eq(referans('tcp.stream == 0', kayit=kayit, dil="wireshark"), beklenen, kayit + ": sabit kimliklerin native sağlaması")
    eq(eslesenler(kayit=kayit), beklenen, kayit + ": öğrenci filtresinin paket kümesi")
```

```solution
tcp.stream == 0
```

```hint
tcp.stream alanının eşitliği aynı zamanda alan varlığını da gerektirir.
```

:::
