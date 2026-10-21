---
id: pk10
title: BPF · Protokol, Adres ve Yön
summary: Görüntü filtresinden BPF diline geç; protokolü, adresi ve kaynak/hedef yönünü ayır.
---

::: anlat Aynı paket, farklı filtre dili
Tezgâhın dili artık `bpf`: ifade gerçek libpcap 1.10.6 ile Ethernet kaydına uygulanır. Wireshark'taki IPv4 kaynak sorusu `ip.src == 10.0.0.10`, BPF'de `ip and src host 10.0.0.10` ile ifade edilir. Aşağıdaki niteliksiz `src host` ise ARP'yi de kapsar. `src` kaynak, `dst` hedef alanını ister. Yön yazılmazsa kaynak **veya** hedef yeterlidir. PCAP değerlendirmesi arayüz açmaz ve paket göndermez.

Bir adresi doğru yönde görmek, kullanıcı kimliği veya saldırı niyeti kanıtı değildir. Ethernet MAC adresi ile IP adresi farklı alanlardır. Bu yol sayısal adres ve port kullanır; isim çözümlemesi yapmaz. Kaynak: [pcap-filter](https://www.tcpdump.org/manpages/pcap-filter.7.html).

```bpf
src host 10.0.0.10
```

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"temel"}
```
:::

::: anlat Host filtresi ARP'yi de kapsayabilir
Niteliksiz IPv4 host koşulu ARP/RARP gönderici ve hedef protokol adreslerini de denetler. Yalnız IPv4 veri paketlerini istiyorsan `ip` ekle. `ip6` ayrı IPv6 ailesidir; `arp` bir protokol seçicisidir. ARP protokol adresi, Ethernet MAC alanı değildir.

`src and dst host A`, iki uç alanının da A olmasını ister; varsayılan `src or dst` ile aynı değildir. Testte ters yön, komşu adres ve ARP örneği bulunur. Kaynak: [Npcap nitelikler](https://npcap.com/guide/wpcap/pcap-filter.html).

```bpf
ip and host 10.0.0.10
```

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"temel"}
```
:::

::: tahmin
`temel` kaydında 24 frame var. Tablo bütün ARP'leri gösterir; diğer 22 frame IPv4 veya IPv6 taşır. Adresler ARP protokol adresleridir.

| Frame | Tür | Kaynak | Hedef |
|---|---|---|---|
| 1 | ARP istek | 10.0.0.10 | 10.0.0.20 |
| 2 | ARP yanıt | 10.0.0.20 | 10.0.0.10 |

Kaynak yönü hangisini bırakır?

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"temel"}
```

```bpf
arp and src host 10.0.0.10
```

???

Yalnız 1 seçilir. Yanıtın hedefindeki .10 kaynak koşulunu sağlamaz; diğer frame'lerde ARP katmanı yoktur.

```text
Paketler: 1
```
:::

::: gorev Kaynağı katmanlar arasında izle
Kaynak protokol adresi tam `10.0.0.10` olan paketleri seç. IPv4 veri ve ARP/RARP gönderici adresleri dahil; yalnız hedefte .10 bulunması yeterli değil. VLAN açma istenmiyor; native Ethernet host davranışını kullan.

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"temel"}
```

```starter
ip
```

```test
for kayit in ("temel","sinirlar","olay"):
    eq(eslesenler(kayit=kayit),referans("src host 10.0.0.10",kayit=kayit,dil="bpf"),kayit+": native paket kümesi")
eq(eslesenler(kayit="temel"),[1,3,5,7,8,10,12,13,16,17,19,21,23],"sabit corpus kimlikleri")
from packet_fixtures import ethernet, ipv4, ipv6, tcp, udp, sctp, arp, icmp_echo, pcap
import ipaddress
def frame(src="10.0.0.10", dst="10.0.0.20", proto=6, sport=40000, dport=80, flags=2, boy=None, vlan=None, vlans=(), options=b"", mac="02:00:00:00:00:10"):
    v=ipaddress.ip_address(src).version
    ek=4*(len(vlans) if vlans else int(vlan is not None))
    taban=14+ek+(20+len(options) if v==4 else 40)+(20 if proto==6 else 8 if proto==17 else 32)
    veri=b"" if boy is None else b"X"*max(0,boy-taban)
    seg=tcp(sport,dport,veri,src=src,dst=dst,flags=flags) if proto==6 else udp(sport,dport,veri,src=src,dst=dst) if proto==17 else sctp(sport,dport)
    ag=ipv4(seg,src,dst,proto,options=options) if v==4 else ipv6(seg,src,dst,proto)
    return ethernet(ag,0x0800 if v==4 else 0x86dd,src=mac,vlan=vlan,vlans=vlans)

frames=[frame(),frame(src="10.0.0.20",dst="10.0.0.10"),frame(src="10.0.0.11"),
ethernet(arp("10.0.0.10","10.0.0.20"),0x0806),ethernet(arp("10.0.0.20","10.0.0.10"),0x0806),
frame(src="2001:db8::10",dst="2001:db8::20")]
eq(eslesenler(kayit=pcap(frames)),[1,4],"kaynak, ters yön, komşu, ARP ve IPv6")
```

```solution
src host 10.0.0.10
```

```hint
src host kullan; ip eklemek istenen ARP kümesini daraltır.
```
:::

::: gorev İki yönde IPv4 uç eşleşmesi
Kaynak veya hedef IPv4 adresi `10.0.0.10` olan veri paketlerini seç. ARP/RARP ve IPv6 elensin; yalnız kaynak yönüyle sınırlama. VLAN katmanı açılmıyor.

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"temel"}
```

```starter
ip
```

```test
for kayit in ("temel","sinirlar","olay"):
    eq(eslesenler(kayit=kayit),referans("ip and host 10.0.0.10",kayit=kayit,dil="bpf"),kayit+": native paket kümesi")
eq(eslesenler(kayit="olay"),[1,2,3,4,5,6,7,8,9,14,15,16,17,21,22,23,24],"sabit corpus kimlikleri")
from packet_fixtures import ethernet, ipv4, ipv6, tcp, udp, sctp, arp, icmp_echo, pcap
import ipaddress
def frame(src="10.0.0.10", dst="10.0.0.20", proto=6, sport=40000, dport=80, flags=2, boy=None, vlan=None, vlans=(), options=b"", mac="02:00:00:00:00:10"):
    v=ipaddress.ip_address(src).version
    ek=4*(len(vlans) if vlans else int(vlan is not None))
    taban=14+ek+(20+len(options) if v==4 else 40)+(20 if proto==6 else 8 if proto==17 else 32)
    veri=b"" if boy is None else b"X"*max(0,boy-taban)
    seg=tcp(sport,dport,veri,src=src,dst=dst,flags=flags) if proto==6 else udp(sport,dport,veri,src=src,dst=dst) if proto==17 else sctp(sport,dport)
    ag=ipv4(seg,src,dst,proto,options=options) if v==4 else ipv6(seg,src,dst,proto)
    return ethernet(ag,0x0800 if v==4 else 0x86dd,src=mac,vlan=vlan,vlans=vlans)

frames=[frame(),frame(src="10.0.0.20",dst="10.0.0.10"),frame(src="10.0.0.11"),
ethernet(arp(),0x0806),frame(src="2001:db8::10",dst="2001:db8::20")]
eq(eslesenler(kayit=pcap(frames)),[1,2],"iki yön dahil, ARP ve IPv6 hariç")
```

```solution
ip and host 10.0.0.10
```

```hint
ip ile aileyi sınırla; yönsüz host iki uçtan birini kabul eder.
```
:::
