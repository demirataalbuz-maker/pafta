---
id: pk15
title: BPF · VLAN ve IPv6 Zinciri
summary: VLAN'ın derleme ofsetini değiştirmesini ve IPv6 uzantılarında protochain farkını gözlemle.
---

::: anlat vlan yalnız bir etiket karşılaştırması değildir
Ethernet etiketi dört bayt ekler. BPF'de her `vlan` anahtar sözcüğü, ifadenin kendisinden sonraki çözümleme ofsetini dört bayt ilerletir. `vlan 100 and ip` bir etiketi açar; `vlan 100 and vlan 200 and ip` iki katmanı sırayla açar. Çıplak `ip` etiketi kendiliğinden atlamaz.

Bu yan etki nedeniyle VLAN'ı sıradan, yerel bir boolean test gibi `or` dalları arasında taşıma; parantez ofset değişikliğini geri almaz. Bu derste doğrusal tek/çift etiket zincirleri kullanılır. Dış ve iç etiket sırası anlamlıdır. Kaynak: [pcap-filter vlan](https://www.tcpdump.org/manpages/pcap-filter.7.html).

```bpf
vlan 100 and vlan 200 and ip
```

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"sinirlar"}
```
:::

::: anlat IPv6 next-header ile protokol zinciri
`ip6 proto 6` IPv6'nın doğrudan next-header alanını denetler; `ip6 protochain 6` uzantı başlıklarını izleyerek TCP protokol numarasını arar. Bu, TCP yükünün tamamını yakaladığını veya fragmentleri birleştirdiğini söylemez. Sonraki IPv6 fragment, zincirde 6 taşısa da TCP port başlığını içermeyebilir.

Buna karşılık bu native BPF port sözdizimi IPv6 uzantılarını otomatik izleyen genel bir TCP çözücüsü değildir. `ip6 and tcp dst port 443` ile `ip6 protochain 6` aynı soru değildir. Wireshark görüntü filtresiyle sonuç farkını son projede ayrıca göreceğiz. Kaynak: [Npcap protochain](https://npcap.com/guide/wpcap/pcap-filter.html).

```bpf
ip6 protochain 6
```

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"sinirlar"}
```
:::

::: tahmin
`sinirlar` içindeki bütün etiketli frame'ler bunlardır; kalan 47 frame etiketsizdir. Etiketler dıştan içe yazıldı.

| Frame | Dış etiket | İç etiket | En iç ağ/yük |
|---|---:|---:|---|
| 29 | 100 | yok | IPv4 / TCP hedef 80 |
| 30 | 101 | yok | IPv4 / TCP hedef 80 |
| 31 | 100 | 200 | IPv4 / UDP hedef 53 |

İki `vlan` adımı hangi frame'in IPv4 katmanına ulaşır?

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"sinirlar"}
```

```bpf
vlan 100 and vlan 200 and ip
```

???

31 iki etiketi istenen sırayla taşır. 29'un ikinci etiketi yoktur; 30 daha ilk VLAN kimliğinde elenir. Etiketsiz paketler ilk koşulu sağlayamaz.

```text
Paketler: 31
```
:::

::: gorev Tek etiketli web portu
Dış VLAN kimliği 100 olan ve tam bu tek etiketten sonra IPv4/TCP hedef portu 80 taşıyan frame'leri seç. Etiketsiz, VLAN 101, hedef 81, UDP 80, IPv6 ve araya ikinci etiket giren paketler dışarıda olsun.

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
    eq(eslesenler(kayit=kayit),referans("vlan 100 and ip and tcp dst port 80",kayit=kayit,dil="bpf"),kayit+": native paket kümesi")
eq(eslesenler(kayit="sinirlar"),[29],"sabit corpus kimlikleri")
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

ham=pcap([frame(),frame(vlan=99),frame(vlan=100),frame(vlan=101),frame(vlan=100,proto=17),frame(vlan=100,dport=81),frame(vlan=100,src="2001:db8::10",dst="2001:db8::20"),frame(vlans=(100,200))])
eq(eslesenler(kayit=ham),[3],"etiket 99/100/101; protokol, port ve etiket derinliği ayrı ayrı")
```

```solution
vlan 100 and ip and tcp dst port 80
```

```hint
Önce vlan 100, sonra bu ofsette ip ve tcp dst port 80. İkinci VLAN'ı açma.
```
:::

::: gorev TCP numarasını IPv6 zincirinde ara
IPv6 protokol zincirinde TCP numarası 6 bulunan frame'leri seç. Doğrudan TCP, Hop-by-Hop sonrası TCP ve TCP numarası taşıyan fragment başlığı dahil; doğrudan UDP ve IPv4 dışarıda olsun. Port veya TCP bayrağı aranmıyor.

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
    eq(eslesenler(kayit=kayit),referans("ip6 protochain 6",kayit=kayit,dil="bpf"),kayit+": native paket kümesi")
eq(eslesenler(kayit="sinirlar"),[33,34,35],"sabit corpus kimlikleri")
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

import struct
s="2001:db8::10"; d="2001:db8::20"
seg=tcp(41000,443,src=s,dst=d)
hbh=ethernet(ipv6(bytes([6,0])+b"\0"*6+seg,s,d,0),0x86dd)
ilk=ethernet(ipv6(bytes([6,0])+struct.pack("!HI",1,77)+seg+b"ABCD",s,d,44),0x86dd)
son=ethernet(ipv6(bytes([6,0])+struct.pack("!HI",8,77)+b"X"*16,s,d,44),0x86dd)
ham=pcap([frame(src=s,dst=d,dport=443),hbh,ilk,son,frame(src=s,dst=d,proto=17,dport=443),frame(dport=443)])
eq(eslesenler(kayit=ham),[1,2,3,4],"doğrudan/uzantı/iki fragment; TCP başlığı varlığı iddia edilmez")
```

```solution
ip6 protochain 6
```

```hint
proto yerine protochain kullan; soru portu değil zincirdeki protokol numarasını soruyor.
```
:::
