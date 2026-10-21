---
id: pk18
title: BPF · Proje: Sınır ve Dil Seçimi
summary: Bir seçim sözleşmesini çok koşullu filtreye çevir; IPv6 uzantısında BPF ile görüntü filtresinin kapsamını karşılaştır.
---

::: anlat Sözleşmeyi alanlara böl ve her koşulu sınırla
Proje filtresi etiketsiz IPv4 ister: kaynak `10.0.0.0/24`, TCP hedef portu 79..81, SYN açık/ACK kapalı, hat uzunluğu en fazla 128. Her koşul ayrı bir anlam taşır. Port aralığı kapalıdır; SYN+FIN kabul edilir; 128 dahil, 129 dışarıdadır. Bir koşulu kaldırınca diğerlerini sağlayan yanlış paketler sızabilir.

Böyle bir filtre yalnız başlık seçimi yapar. SYN gözlemi bağlantının kurulduğunu veya isteğin kötü niyetli olduğunu kanıtlamaz. Testler üç sentetik kayda ek olarak her koşulu tek başına bozan paketler üretir; sabit frame numaralarını ezberlemek yeterli değildir.

```bpf
ip and src net 10.0.0.0/24 and tcp dst portrange 79-81 and tcp[tcpflags] & (tcp-syn|tcp-ack) == tcp-syn and less 128
```

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"temel"}
```
:::

::: anlat Aynı görünen soru iki dilde aynı kapsamda olmayabilir
Doğrudan IPv6/TCP başlığında `ip6 and tcp dst port 443` BPF ifadesi ile `ipv6 and tcp.dstport == 443` görüntü filtresi aynı paketi seçebilir. IPv6 Hop-by-Hop uzantısı eklenince TShark TCP'ye kadar çözümleyebilir; bu native BPF port erişimi o uzantıyı izlemez. Önceki `ip6 protochain 6` zincirde TCP numarasını arasa da hedef port 443 koşulunun yerine geçmez.

Dolayısıyla bir dilden diğerine yalnız alan adını değiştirerek genel eşdeğerlik iddia etme. Hangi katmanı çözdüğünü, fragment ve etiket sınırını belirt. Bu yol yerel Ethernet PCAP üzerinde filtre yazmayı öğretir; canlı yakalama veya bütün protokol incelemelerini tamamlamış sayılmaz. Kaynaklar: [pcap-filter](https://www.tcpdump.org/manpages/pcap-filter.7.html), [Wireshark görüntü filtreleri](https://www.wireshark.org/docs/man-pages/wireshark-filter.html).

```bpf
ip6 and tcp dst port 443
```

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"temel"}
```
:::

::: tahmin
`temel` kaydındaki bütün IPv6 frame'leri aşağıda; kalan 21 frame IPv4 veya ARP'dir. Bu üç IPv6 frame uzantı başlığı taşımaz.

| Frame | IPv6 taşıma | Kaynak → hedef port |
|---|---|---|
| 14 | UDP | 53001 → 53 |
| 15 | TCP | 40002 → 443 |
| 18 | ICMPv6 | port yok |

BPF filtresi hangisini seçer?

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"temel"}
```

```bpf
ip6 and tcp dst port 443
```

???

Yalnız 15 doğrudan IPv6/TCP hedef portu 443 taşır. 14'te taşıma UDP, 18'de port alanı yoktur. Bu sonuç uzantılı bütün IPv6 TCP paketlerini kapsadığı anlamına gelmez.

```text
Paketler: 15
```
:::

::: gorev Sınırlarıyla SYN seçim projesi
Etiketsiz IPv4 üzerinde şu koşulların **hepsini** uygula: kaynak `10.0.0.0/24`; TCP hedef portu 79..81 dahil; SYN açık ve ACK kapalı; hat uzunluğu en fazla 128. Diğer TCP bayrakları serbesttir. Kaynak .0 ve .255 dahildir; komşu ağlar, UDP, IPv6 ve VLAN açılması kapsam dışıdır.

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
    eq(eslesenler(kayit=kayit),referans("ip and src net 10.0.0.0/24 and tcp dst portrange 79-81 and tcp[tcpflags] & (tcp-syn|tcp-ack) == tcp-syn and less 128",kayit=kayit,dil="bpf"),kayit+": native paket kümesi")
eq(eslesenler(kayit="sinirlar"),[6,32],"sabit corpus kimlikleri")
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

iyi=dict(src="10.0.0.10",dst="198.51.100.80",dport=80,flags=2,boy=128)
aday=[frame(**iyi)]
for alan,degerler in (("src",("9.255.255.255","10.0.0.0","10.0.0.255","10.0.1.0")),("dport",(78,79,81,82)),("flags",(0,1,3,4,16,18,19)),("boy",(127,129)),("proto",(17,))):
    for deger in degerler:
        ayar=dict(iyi); ayar[alan]=deger; aday.append(frame(**ayar))
aday.append(frame(src="2001:db8::10",dst="2001:db8::20",dport=80,flags=2,boy=128))
aday.append(frame(**iyi,vlan=100))
aday.append(frame(**iyi,options=b"\x01"*4))
ham=pcap(aday)
eq(eslesenler(kayit=ham),[1,3,4,7,8,12,17,22],"tek koşullu karşı örnekler; iki port ucu, SYN+FIN, boy 128 ve IHL6")
```

```solution
ip and src net 10.0.0.0/24 and tcp dst portrange 79-81 and tcp[tcpflags] & (tcp-syn|tcp-ack) == tcp-syn and less 128
```

```hint
Koşulları and ile birleştir. Bayrak maskesini SYN|ACK ile kur, port aralığı ve less 128 eşitliği içerir.
```
:::

::: gorev IPv6 port sorusunun dürüst kapsamı
Native BPF ile doğrudan IPv6 başlığından sonra TCP hedef portu 443 taşıyan frame'leri seç. UDP 443, IPv4/TCP 443 ve hedef 444 dışarıda olsun. Uzantı arkasındaki TCP'yi kapsama iddiası yok: bu görevin port erişimi doğrudan başlık kapsamındadır. Test aynı özel kaydı Wireshark görüntü filtresiyle de karşılaştırıp kapsam farkını gösterir.

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
    eq(eslesenler(kayit=kayit),referans("ip6 and tcp dst port 443",kayit=kayit,dil="bpf"),kayit+": native paket kümesi")
eq(eslesenler(kayit="temel"),[15],"sabit corpus kimlikleri")
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

s="2001:db8::10"; d="2001:db8::20"
seg=tcp(41000,443,src=s,dst=d)
hbh=ethernet(ipv6(bytes([6,0])+b"\0"*6+seg,s,d,0),0x86dd)
ham=pcap([frame(src=s,dst=d,dport=443),frame(src=s,dst=d,dport=443,proto=17),frame(dport=443),frame(src=s,dst=d,dport=444),hbh])
eq(eslesenler(kayit=ham),[1],"doğrudan IPv6 TCP ve bağımsız taşıma/aile/port karşı örnekleri")
eq(referans("ipv6 and tcp.dstport == 443",kayit=ham,dil="wireshark"),[1,5],"TShark uzantı arkasındaki TCP'yi de çözümler")
```

```solution
ip6 and tcp dst port 443
```

```hint
ip6 and tcp dst port 443. protochain 6 portu doğrulamaz; başka bir sözleşmedir.
```
:::
