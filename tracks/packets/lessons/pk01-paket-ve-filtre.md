---
id: pk01
title: Wireshark · İlk Görüntü Filtren
summary: Frame, protokol ve alanı ayır; yazdığın filtreyi gerçek TShark ile çevrimdışı kayıtta çalıştır.
---

::: anlat Kaydı açmak ile ağdan toplamak farklı işler
Paket kaydı, gözlenen çerçevelerin sıralı bir örneğidir. Bir `frame.number` kaydın içindeki sıradır; internette geçerli bir paket kimliği değildir. Aynı trafiği başka kayda taşırsan numaralar değişebilir. Pafta bu yolda yalnız üretilmiş eğitim kayıtlarını okur; canlı ağ arayüzünden veri toplamaz.

Filtre metnini sağdaki tezgâha yaz. Girdi JSON'u dilin `wireshark`, kaydın `temel` olduğunu seçer. Çalıştır, gerçek `tshark -Y` motoruyla eşleşen frame numaralarını verir. Bu, Python ile protokol tahmini yapan bir alıştırma değildir.

```wireshark
ip
```

`ip` IPv4 katmanının varlığını arar; IPv6 için ayrı `ipv6` alanı vardır. Protokolün bulunması, paketin zararlı ya da başarılı olduğunu söylemez. Kaynak: [TShark görüntü filtresi](https://www.wireshark.org/docs/man-pages/tshark.html).

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```
:::

::: anlat Görüntü filtresi kaydı küçültmez
Görüntü filtresi ekranda hangi paketlerin listeleneceğini seçer. Mevcut kayıttan diğer paketleri silmez. Yakalama filtresi ise toplama aşamasında nelerin alınacağını sınırlar ve başka bir dildir; bu yolun ikinci yarısında BPF yazacağız. `tcp.port == 80` bir görüntü filtresidir; BPF metni diye kullanılamaz.

```wireshark
ip or ipv6
```

Bu ifade iki IP ailesini birleştirir; ARP gibi IP katmanı olmayan çerçeveler kalmaz. JSON'daki `kayit` alanı başka bir sentetik kayıtla değiştirildiğinde aynı filtre yeni kayıt üzerinde tekrar değerlendirilir. Testler bir cevabı ezberlemeyi değil, farklı kayıtlarda doğru protokol kümesini seçmeyi sınar. Kaynak: [Alan/protokol varlığı ve mantık](https://www.wireshark.org/docs/man-pages/wireshark-filter.html).

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```
:::

::: tahmin
Aşağıdaki tablo seçili sentetik kaydın bu soru için gereken **bütün frame** alanlarını gösterir. Aynı alan değerleri bir satırda gruplandı; `—` o alanın bulunmadığı anlamına gelir. Hangi frame numaraları görünür? Sonuç kayıt sırasıyla, numaraları artarak yazılır.

| Frame numaraları | `ip.version` | `ipv6.version` | `arp.opcode` |
| --- | --- | --- | --- |
| 1 | — | — | `1` |
| 2 | — | — | `2` |
| 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 19, 20, 21, 22, 23, 24 | `4` | — | — |
| 14, 15, 18 | `6` | `6` | — |

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```

```wireshark
ip
```

???

```text
Paketler: 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 19, 20, 21, 22, 23, 24
```

IPv4 katmanı görülen paketler kalır. IPv6 ve ARP paketleri bu ifadeyi sağlamaz. Tam frame listesi, seçili temel kaydının gerçek çözümlemesinden gelir.
:::

::: gorev Yalnız IPv4

Seçili kayıtta yalnız IPv4 katmanı içeren paketleri göster. Protokolü olmayan paketler ve IPv6 dışarıda kalmalı. Filtreyi frame numaralarıyla sınırlama; temel, sinirlar ve olay kayıtlarında çalışsın.

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
beklenenler = {'temel': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 19, 20, 21, 22, 23, 24], 'sinirlar': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 27, 28, 29, 30, 31, 32, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50], 'olay': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 20, 21, 22, 23, 24, 25]}
for kayit, beklenen in beklenenler.items():
    eq(referans('ip', kayit=kayit, dil="wireshark"), beklenen, kayit + ": sabit kimliklerin native sağlaması")
    eq(eslesenler(kayit=kayit), beklenen, kayit + ": öğrenci filtresinin paket kümesi")
```

```solution
ip
```

```hint
Bir protokol adını tek başına yazmak o protokolün varlığını sınar.
```

:::

::: gorev İki IP ailesi

IPv4 veya IPv6 içeren bütün paketleri göster; ARP gibi IP dışı çerçeveleri seçme. İki aileden yalnız birine sınırlama getirme.

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
beklenenler = {'temel': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24], 'sinirlar': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50], 'olay': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25]}
for kayit, beklenen in beklenenler.items():
    eq(referans('ip or ipv6', kayit=kayit, dil="wireshark"), beklenen, kayit + ": sabit kimliklerin native sağlaması")
    eq(eslesenler(kayit=kayit), beklenen, kayit + ": öğrenci filtresinin paket kümesi")
```

```solution
ip or ipv6
```

```hint
İki protokol varlığı arasında or kullan.
```

:::
