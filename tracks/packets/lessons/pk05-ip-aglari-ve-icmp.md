---
id: pk05
title: IP Aileleri · Ağlar ve ICMP
summary: IPv4/IPv6 CIDR üyeliğini ve ICMP sürümlerini doğru alanlarla yaz; ağ sınırlarını dahil et.
---

::: anlat CIDR adres aralığıdır
CIDR son eki ağdaki adres bitlerini belirtir. `192.0.2.0/24`, 192.0.2.0 ile 192.0.2.255 arasını kapsar. Bu filtrede ağ ve yayın adreslerinin paketlerde görünmesini otomatik yasaklamıyoruz; görev bir adres üyeliği sorusudur, işletim sisteminin kullanılabilir host hesabı değildir.

```wireshark
ip.addr == 192.0.2.0/24
```

`ip.addr` iki yöndeki adresleri sınar. Kaynağın ağda olmasını istiyorsan `ip.src` yaz. Tünellenmiş paketlerde birden çok IP katmanı olabileceğinden gerçek incelemede hangi katmanın alanına baktığını da denetle. Bu eğitim aralık görevlerinin başlıkları basittir. Kaynak: [IPv4 ve IPv6 alan türleri](https://www.wireshark.org/docs/wsug_html_chunked/ChWorkBuildDisplayFilterSection.html).

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```
:::

::: anlat IPv6 ve ICMP alanları ayrıdır
`ipv6.addr == 2001:db8:1::/126`, IPv6 ağının ilk dört adresini kabul eder. IPv4 alanı bu pakette kendiliğinden ortaya çıkmaz. ICMPv4 için `icmp`, ICMPv6 için `icmpv6` protokol alanları vardır; biri diğerinin tümünü kapsayan ortak ad değildir.

```wireshark
icmp or icmpv6
```

ICMP yalnız ping değildir; hata ve kontrol mesajları da taşır. IPv6 komşuluk keşfi de ICMPv6 üzerindedir. Dolayısıyla yalnız echo istiyorsan ayrıca doğru type alanını okumak gerekir. Bu derste görev bütün iki ICMP protokol kümesini ister. Ağ örnekleri belgeleme için ayrılmış adres alanlarıdır. Kaynak: [Filtre alanları ve protokol varlığı](https://www.wireshark.org/docs/man-pages/wireshark-filter.html).

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```
:::

::: tahmin
Aşağıdaki tablo seçili sentetik kaydın bu soru için gereken **bütün frame** alanlarını gösterir. Aynı alan değerleri bir satırda gruplandı; `—` o alanın bulunmadığı anlamına gelir. Hangi frame numaraları görünür? Sonuç kayıt sırasıyla, numaraları artarak yazılır.

| Frame numaraları | `icmp.type` | `icmpv6.type` |
| --- | --- | --- |
| 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24 | — | — |
| 17 | `8` | — |
| 18 | — | `128` |

```meta
dil: wireshark
```

```stdin
{"dil": "wireshark", "kayit": "temel"}
```

```wireshark
icmp or icmpv6
```

???

```text
Paketler: 17, 18
```

ICMPv4 ve ICMPv6 çözümlenen paketler görünür. Sıradan TCP/UDP ile ARP bu protokol filtresini sağlamaz.
:::

::: gorev İki belgeleme ağı

Kaynak veya hedefi IPv4 192.0.2.0/24 ağına ya da IPv6 2001:db8:1::/126 ağına ait paketleri göster. İki ağın ilk/son adresi dahil; dış komşuları dışarıda.

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
beklenenler = {'temel': [], 'sinirlar': [17, 18, 21, 22, 24, 25, 49], 'olay': []}
for kayit, beklenen in beklenenler.items():
    eq(referans('ip.addr == 192.0.2.0/24 or ipv6.addr == 2001:db8:1::/126', kayit=kayit, dil="wireshark"), beklenen, kayit + ": sabit kimliklerin native sağlaması")
    eq(eslesenler(kayit=kayit), beklenen, kayit + ": öğrenci filtresinin paket kümesi")

import packet_fixtures as pf
def tcp4(sport=40000, dport=80, payload=b"", src="10.0.0.10", dst="10.0.0.20", flags=0x18):
    segment = pf.tcp(sport, dport, payload, src=src, dst=dst, flags=flags)
    return pf.ethernet(pf.ipv4(segment, src, dst, 6))
def udp4(sport=53000, dport=53, payload=b"", src="10.0.0.10", dst="10.0.0.53"):
    segment = pf.udp(sport, dport, payload, src=src, dst=dst)
    return pf.ethernet(pf.ipv4(segment, src, dst, 17))

frames = []
outside = "198.51.100.20"
for address in ("192.0.2.0", "192.0.2.255"):
    frames += [udp4(src=outside, dst=address), udp4(src=address, dst=outside)]
for address in ("192.0.1.255", "192.0.3.0"):
    frames += [udp4(src=outside, dst=address)]
outside6 = "2001:db8:ffff::20"
for address in ("2001:db8:1::", "2001:db8:1::3"):
    for source, target in ((outside6, address), (address, outside6)):
        segment = pf.udp(53000, 9000, src=source, dst=target)
        frames += [pf.ethernet(pf.ipv6(segment, source, target, 17), 0x86dd)]
for address in ("2001:db8:0:ffff:ffff:ffff:ffff:ffff", "2001:db8:1::4"):
    segment = pf.udp(53000, 9000, src=outside6, dst=address)
    frames += [pf.ethernet(pf.ipv6(segment, outside6, address, 17), 0x86dd)]
eq(eslesenler(kayit=pf.pcap_bytes(frames)), [1, 2, 3, 4, 7, 8, 9, 10], "CIDR ilk/son/dış komşu; kaynak ve hedef")
```

```solution
ip.addr == 192.0.2.0/24 or ipv6.addr == 2001:db8:1::/126
```

```hint
IP ailelerinin alanları farklıdır; iki CIDR karşılaştırmasını or ile bağla.
```

:::

::: gorev İki ICMP ailesi

Bütün ICMPv4 ve ICMPv6 paketlerini göster. Yalnız bir protokol ailesini seçme; TCP/UDP veya ARP ekleme.

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
beklenenler = {'temel': [17, 18], 'sinirlar': [49], 'olay': []}
for kayit, beklenen in beklenenler.items():
    eq(referans('icmp or icmpv6', kayit=kayit, dil="wireshark"), beklenen, kayit + ": sabit kimliklerin native sağlaması")
    eq(eslesenler(kayit=kayit), beklenen, kayit + ": öğrenci filtresinin paket kümesi")
```

```solution
icmp or icmpv6
```

```hint
icmpv6 ayrı protokol alanıdır.
```

:::
