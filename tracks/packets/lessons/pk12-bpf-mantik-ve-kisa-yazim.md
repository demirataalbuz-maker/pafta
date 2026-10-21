---
id: pk12
title: BPF · Mantık, Kısaltma ve Küçük Proje
summary: and/or eşit önceliğini, not kapsamını ve taşınan nitelikleri okuyup birleşik filtre yaz.
---

::: anlat AND ve OR eşit önceliklidir
BPF'de `not` en yüksek önceliktedir. `and` ile `or` eşit öncelikli, soldan birleşir: `tcp or udp and port 53`, `(tcp or udp) and port 53` anlamındadır. Başka dillerdeki AND>OR kuralı burada bütün TCP paketlerini yanlışlıkla bırakabilir.

Niyeti parantezle açık yaz. `not host A and host B`, `not (host A and host B)` değildir. Bir koşul eklerken hangi grubun daralacağını düşün. Kaynak: [Birleşim kuralları](https://www.tcpdump.org/manpages/pcap-filter.7.html).

```bpf
tcp or udp and port 53
```

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"sinirlar"}
```
:::

::: anlat Eksik nitelik önceki ifadeden taşınır
`tcp dst port 80 or 443`, ikinci sayıyı da `tcp dst port` ile yorumlar. Kısaltmayı başka bağlama taşırken niteliği kaybetmemek için açık tekrar kullanabilirsin.

Küçük projede önce kaynak seçip iki taşıma dalını birlikte daraltacağız. `src host A and (tcp dst port 80 or udp dst port 53)`, kaynağı iki dala da uygular. Parantezi kaldırmak son UDP dalını kaynak kısıtından kurtarır. Kaynak: [Npcap kısa yazım](https://npcap.com/guide/wpcap/pcap-filter.html).

```bpf
tcp dst port 80 or 443
```

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"temel"}
```
:::

::: tahmin
Tablo `temel` kaydındaki bütün TCP frame'lerini gösterir. Diğerleri ARP/UDP/SCTP/ICMP'dir. IPv6 frame 15 doğrudan TCP başlığı taşır; VLAN yoktur.

| Frame | Aile | Kaynak port | Hedef port |
|---|---|---|---|
| 5, 7, 8 | IPv4 | 40000 | 80 |
| 6, 9 | IPv4 | 80 | 40000 |
| 10, 12, 13 | IPv4 | 40001 | 443 |
| 11 | IPv4 | 443 | 40001 |
| 15 | IPv6 | 40002 | 443 |
| 19, 21, 23 | IPv4 | 41000,41001,41002 | 80 |
| 20, 22, 24 | IPv4 | 80 | 41000,41001,41002 |

İkinci sayı hangi nitelikleri alır?

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"temel"}
```

```bpf
tcp dst port 80 or 443
```

???

443 de TCP hedef portudur. Yanıtın kaynak portunun 80/443 olması yetmez; IPv6 doğrudan TCP frame 15 dahildir.

```text
Paketler: 5, 7, 8, 10, 12, 13, 15, 19, 21, 23
```
:::

::: gorev TCP veya UDP içinde port 53
TCP ya da UDP paketlerinden kaynak veya hedef portu tam 53 olanları seç. TCP 80 sırf TCP diye kalmasın; SCTP 53 dışarıda olsun. Bu, niteliksiz port 53'ten daha dar bir protokol kümesidir.

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
    eq(eslesenler(kayit=kayit),referans("(tcp or udp) and port 53",kayit=kayit,dil="bpf"),kayit+": native paket kümesi")
eq(eslesenler(kayit="sinirlar"),[4,14,15,36,37,38],"sabit corpus kimlikleri")
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

frames=[frame(dport=80),frame(dport=53),frame(proto=17,dport=53),frame(proto=17,dport=80),frame(proto=132,dport=53),
frame(sport=53,dport=45000),frame(proto=17,sport=53,dport=45001),frame(proto=17,dport=52),frame(proto=17,dport=54)]
eq(eslesenler(kayit=pcap(frames)),[2,3,6,7],"TCP80, SCTP53 ve iki port komşusu")
```

```solution
(tcp or udp) and port 53
```

```hint
Önce (tcp or udp), sonra iki yönlü port53 koşulu.
```
:::

::: gorev Kaynağa bağlı iki hizmet dalı
Kaynak protokol adresi 10.0.0.10 iken TCP hedef 80 veya UDP hedef 53 paketlerini seç. Kaynak koşulu iki dalı da daraltsın. Yanıt yönü, başka kaynak, TCP 53, UDP 80 ve ARP eşleşmesin.

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
    eq(eslesenler(kayit=kayit),referans("src host 10.0.0.10 and (tcp dst port 80 or udp dst port 53)",kayit=kayit,dil="bpf"),kayit+": native paket kümesi")
eq(eslesenler(kayit="temel"),[3,5,7,8,19,21,23],"sabit corpus kimlikleri")
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

frames=[frame(),frame(proto=17,dport=53),frame(src="10.0.0.11"),frame(src="10.0.0.11",proto=17,dport=53),
frame(src="10.0.0.20",dst="10.0.0.10",sport=80,dport=45000),frame(dport=53),frame(proto=17,dport=80),ethernet(arp(),0x0806)]
eq(eslesenler(kayit=pcap(frames)),[1,2],"her koşulu ayrı bozan adaylar")
```

```solution
src host 10.0.0.10 and (tcp dst port 80 or udp dst port 53)
```

```hint
Kaynak koşulundan sonra iki hizmeti parantez içinde or ile birleştir.
```
:::
