---
id: pk02
title: Adresler · Yön ve Mantık Kapsamı
summary: ip.src, ip.dst ve ip.addr; iki yönü ve dışlama koşulunun bütün gruba uygulanmasını doğru yaz.
---

::: anlat Kaynak, hedef ve iki taraftan biri
`ip.src` IPv4 kaynağı, `ip.dst` hedefidir. `ip.addr` aynı pakette hem kaynak hem hedef alanı olarak bulunabilir. `ip.addr == 10.0.0.10` bunlardan en az biri eşitse paketi seçer. Tek yön isteği için `ip.src` kullanmalısın.

```wireshark
ip.src == 10.0.0.10
```

Bir IP adresi, o anda paketin yönünü gösterir; kullanıcının kimliği veya bağlantının başlatanı olduğuna dair tek başına kanıt değildir. NAT, tünel ve farklı yakalama noktaları adresleri değiştirebilir. Eğitim kayıtları bu ilk örneklerde açık IPv4 uçlar kullanır. Kaynak: [Görüntü filtresi karşılaştırmaları](https://www.wireshark.org/docs/wsug_html_chunked/ChWorkBuildDisplayFilterSection.html).

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```
:::

::: anlat Dışlamayı grubun dışına koy
Hem gidişi hem dönüşü görmek istiyorsan iki yönü `or` ile bağlayabilirsin. Bir dışlamanın bütün bu trafiğe uygulanması için dışlamayı parantezli grubun dışında `and` ile birleştir. `A or (B and C)`, `(A or B) and C` ile aynı değildir.

```wireshark
(ip.addr == 10.0.0.10) and not (ip.addr == 10.0.0.53)
```

Bu ifade .10 ile ilişkili trafiği seçer, iki ucundan biri .53 ise dışlar. Karşılaştırmada alan varlığı da önemlidir: `ip.dst != 10.0.0.53` IPv4 hedefi olmayan ARP/IPv6 çerçevelerini seçmez. `not (ip.dst == 10.0.0.53)` ise içteki eşitlik bu alan bulunmadığında başarısız olduğu için onları da seçer. Temel kayıttaki ARP 1–2 ve IPv6 14–15/18 bu iki ifadenin farkını gösterir.

Aynı fark taşıma alanında da vardır: `tcp.dstport != 80` UDP'yi dışarıda bırakır; `not (tcp.dstport == 80)` UDP'yi kapsar. Yalnız TCP içinde dışlama istiyorsan `tcp and not (tcp.dstport == 80)` yaz. Wireshark'ın çok değerli alanlarında güncel `!=`, bulunan değerlerin tamamının farklı olmasını ister. Kaynak: [Alan varlığı ve çoklu karşılaştırma](https://www.wireshark.org/docs/man-pages/wireshark-filter.html).

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```
:::

::: tahmin
Aşağıdaki tablo seçili sentetik kaydın bu soru için gereken **bütün frame** alanlarını gösterir. Aynı alan değerleri bir satırda gruplandı; `—` o alanın bulunmadığı anlamına gelir. Hangi frame numaraları görünür? Sonuç kayıt sırasıyla, numaraları artarak yazılır.

| Frame numaraları | `ip.src` | `ip.dst` |
| --- | --- | --- |
| 1, 2, 14, 15, 18 | — | — |
| 3 | `10.0.0.10` | `10.0.0.53` |
| 4 | `10.0.0.53` | `10.0.0.10` |
| 5, 7, 8, 10, 12, 13, 16, 17, 19, 21, 23 | `10.0.0.10` | `10.0.0.20` |
| 6, 9, 11, 20, 22, 24 | `10.0.0.20` | `10.0.0.10` |

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```

```wireshark
ip.addr == 10.0.0.10 and not (ip.addr == 10.0.0.53)
```

???

```text
Paketler: 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 19, 20, 21, 22, 23, 24
```

İstemci .10 iki yönden de kabul edilir, fakat DNS sunucusu .53 ile arasındaki paketler dışlanır. IPv4 dışındaki paketler pozitif adres koşulunu sağlamaz.
:::

::: gorev İstemciden çıkanlar

Yalnız IPv4 kaynak adresi 10.0.0.10 olan paketleri göster. Bu adrese gelen dönüş paketleri dahil olmasın.

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
beklenenler = {'temel': [3, 5, 7, 8, 10, 12, 13, 16, 17, 19, 21, 23], 'sinirlar': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 27, 28, 29, 30, 31, 32, 36, 37, 38, 39, 40, 41], 'olay': [1, 3, 5, 6, 8, 14, 16, 17, 21, 23]}
for kayit, beklenen in beklenenler.items():
    eq(referans('ip.src == 10.0.0.10', kayit=kayit, dil="wireshark"), beklenen, kayit + ": sabit kimliklerin native sağlaması")
    eq(eslesenler(kayit=kayit), beklenen, kayit + ": öğrenci filtresinin paket kümesi")
```

```solution
ip.src == 10.0.0.10
```

```hint
ip.addr iki yönü kapsar; görev tek yön istediğinden ip.src seç.
```

:::

::: gorev İki yön, bir uç dışarıda

10.0.0.10 adresini kaynak veya hedef olarak içeren IPv4 trafiği göster; diğer uçta 10.0.0.53 varsa iki yönde de dışla.

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
beklenenler = {'temel': [5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 19, 20, 21, 22, 23, 24], 'sinirlar': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 27, 28, 29, 30, 31, 32, 39, 40, 41, 42, 43, 44, 45, 46, 47], 'olay': [3, 4, 5, 6, 7, 8, 9, 14, 15, 16, 21, 22, 23, 24]}
for kayit, beklenen in beklenenler.items():
    eq(referans('ip.addr == 10.0.0.10 and not (ip.addr == 10.0.0.53)', kayit=kayit, dil="wireshark"), beklenen, kayit + ": sabit kimliklerin native sağlaması")
    eq(eslesenler(kayit=kayit), beklenen, kayit + ": öğrenci filtresinin paket kümesi")
```

```solution
ip.addr == 10.0.0.10 and not (ip.addr == 10.0.0.53)
```

```hint
Pozitif istemci koşuluyla not sunucu koşulunu and ile bağla.
```

:::
