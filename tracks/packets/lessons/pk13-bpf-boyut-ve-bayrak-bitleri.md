---
id: pk13
title: BPF · Boyut ve Bayrak Bitleri
summary: Hat uzunluğunun kapalı sınırlarını ve TCP bayrak maskelerinin gerçekten ne istediğini ayır.
---

::: anlat len, yakalanan bayt sayısı değildir
`less 64`, `len <= 64`; `greater 128`, `len >= 128` demektir. İki uç da dahildir. BPF bu karşılaştırmada PCAP kaydının özgün hat uzunluğunu kullanır. `caplen` yalnız dosyada saklanan bayttır; snapshot kesintisinde daha küçük olabilir. Bu kayıtlarda uzunluk Ethernet frame boyudur; FCS baytları eklenmemiştir.

Boyut koşulu bir uygulama protokolünü tanımaz. Kısa bir paket otomatik olarak SYN, uzun bir paket HTTP değildir. Testler 63/64/65 ve 127/128/129 değerlerini, ayrıca aynı uzunlukta kısaltılmış kaydı ayrı tutar. Kaynak: [pcap-filter uzunluk işleçleri](https://www.tcpdump.org/manpages/pcap-filter.7.html).

```bpf
less 64 or greater 128
```

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"temel"}
```
:::

::: anlat Bir biti istemek, bütün bayrağı eşitlemek değildir
`tcp[tcpflags]` TCP başlığının bayrak baytını okur. SYN=2, ACK=16; `&` maskesi yalnız istenen bitleri bırakır. `(SYN|ACK)` maskesinin sonucunu SYN'e eşitlemek, SYN açık ve ACK kapalı demektir. FIN veya başka bir bit bu maskede yoktur: SYN+FIN de geçer. Yalnız saf SYN istenseydi bütün baytın `tcp-syn` değerine eşitliği farklı bir sözleşme olurdu.

Bu libpcap sözdizimindeki `tcp[...]` taşıma katmanı bayt erişimi IPv4 içindir; IPv6 SYN'lerini kapsadığı varsayılmaz. Sonraki ders IP başlığı, fragment ve değişken başlık uzunluğunu ele alır. Kaynak: [Npcap aritmetik erişimler](https://npcap.com/guide/wpcap/pcap-filter.html).

```bpf
tcp[tcpflags] & (tcp-syn|tcp-ack) == tcp-syn
```

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"temel"}
```
:::

::: tahmin
`temel` kaydının bütün frame uzunlukları aşağıda gruplandı. Bu tabloda caplen=hat uzunluğu; her numara tam bir kez bulunur.

| Frame | Hat uzunluğu |
|---|---:|
| 1, 2, 5, 6, 7, 10, 11, 12, 17 | 60 |
| 3 | 75 |
| 4 | 91 |
| 8 | 147 |
| 9 | 140 |
| 13 | 154 |
| 14 | 95 |
| 15 | 74 |
| 16 | 66 |
| 18 | 67 |
| 19 | 146 |
| 20 | 150 |
| 21 | 146 |
| 22 | 149 |
| 23 | 148 |
| 24 | 154 |

`less` sınırı dahil olunca hangileri kalır?

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"temel"}
```

```bpf
less 64
```

???

Bu kayıtta 64 baytlık frame yok; 60 baytlık dokuz frame seçilir. 66 bayt bile 64'ten büyük olduğu için dışarıda kalır. Görevde tam 64 ve 128 bayt tanıkları da bulunur.

```text
Paketler: 1, 2, 5, 6, 7, 10, 11, 12, 17
```
:::

::: gorev İki kapalı boyut aralığı
Hat uzunluğu en fazla 64 **veya** en az 128 bayt olan frame'leri seç. Aradaki 65..127 aralığı dışarıda kalsın. Yakalanan bayt sayısına göre karar verme; kısaltılmış kayıtların özgün uzunluğu geçerlidir.

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
    eq(eslesenler(kayit=kayit),referans("less 64 or greater 128",kayit=kayit,dil="bpf"),kayit+": native paket kümesi")
eq(eslesenler(kayit="sinirlar"),[1,2,3,5,6,7,8,9,10,11,12,13,14,17,18,21,22,23,24,25,26,27,28,29,30,32,39,40,41,42,43,44,45,46,47,48,49,50],"sabit corpus kimlikleri")
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

tam=[frame(boy=n) for n in (63,64,65,127,128,129)]
kesik=frame(boy=129)
ham=pcap(tam+[(kesik[:36],64),(kesik[:36],65),(kesik[:36],127),(kesik[:36],128)])
eq(eslesenler(kayit=ham),[1,2,5,6,7,10],"iki eşik ve caplen yerine wirelen")
```

```solution
less 64 or greater 128
```

```hint
less ve greater ikisi de eşitliği içerir; iki küme or ile birleşir.
```
:::

::: gorev SYN var, ACK yok
IPv4 TCP bayraklarında SYN açık ve ACK kapalı olanları seç. Diğer bayrak bitlerini serbest bırak: SYN+FIN kabul edilir; SYN+ACK edilmez. IPv6 ve sonraki IPv4 fragmentler için TCP bayrak erişimi istenmiyor.

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
    eq(eslesenler(kayit=kayit),referans("tcp[tcpflags] & (tcp-syn|tcp-ack) == tcp-syn",kayit=kayit,dil="bpf"),kayit+": native paket kümesi")
eq(eslesenler(kayit="temel"),[5,10],"sabit corpus kimlikleri")
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

bayraklar=(0,1,2,3,4,16,18,19)
ham=pcap([frame(flags=f) for f in bayraklar]+[frame(src="2001:db8::10",dst="2001:db8::20",flags=2),frame(proto=17)])
eq(eslesenler(kayit=ham),[3,4],"SYN tek başına ve SYN+FIN; ACK bitli olanlar dışarı")
```

```solution
tcp[tcpflags] & (tcp-syn|tcp-ack) == tcp-syn
```

```hint
SYN ve ACK maskesinin sonucu yalnız SYN olmalı. Bütün baytı 2'ye eşitlemek SYN+FIN'i kaybeder.
```
:::
