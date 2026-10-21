---
id: pk11
title: BPF · Ağlar ve Port Aralıkları
summary: CIDR kapsamını ve portrange uçlarını gerçek başlıklarda sına; yönü ve taşıma protokolünü koru.
---

::: anlat CIDR metin öneki değildir
`net A/P`, ilk P adres bitini karşılaştırır. IPv4 /24 içinde .0 ve .255 filtre açısından yer alır; adresin uç cihaza atanabilirliği sorulmuyor. IPv6 /126 dört adres kapsar. Ağın dış komşularını da denemek yanlış maskeyi yakalar.

Kaynak ağı için `src net` yaz. Tarihsel CIDR'siz kısaltmalar yerine bu yolda açık önek kullanıyoruz. IPv4 /32 ve IPv6 /128 tek adresi seçer. Hedefin ağda olması kaynak koşulunu sağlamaz. Kaynak: [pcap-filter net](https://www.tcpdump.org/manpages/pcap-filter.7.html).

```bpf
src net 192.0.2.0/24
```

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"sinirlar"}
```
:::

::: anlat Port aralığında iki uç dahil
`tcp dst portrange 79-81`, TCP hedef 79/80/81'i kapsar. 78 ve 82 dış komşulardır; kaynak 80 ve geçici hedefli yanıt seçilmez. TCP niteliği aynı numaralı UDP/SCTP'yi dışlar. Native libpcap ters verilen aralık uçlarını da sıralar; açık küçük-büyük yazım daha okunaklıdır.

Port numarası uygulama protokolü ispatı değildir. IPv4 port erişimi ilk fragmentte veya parçalanmamış pakette yapılabilir; sonraki fragment port başlığını taşımaz. Kaynak: [Native port üretimi](https://raw.githubusercontent.com/the-tcpdump-group/libpcap/libpcap-1.10.6/gencode.c).

```bpf
tcp dst portrange 79-81
```

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"sinirlar"}
```
:::

::: tahmin
Aşağıdaki frame'lerin dışında bütün IPv4 kaynakları 10.0.0.10/.20/.53/.99'dur. ARP kaynağı 10.0.0.10; kalan frame'ler IPv6'dır. Tablo ağla ilgili bütün adayları gösterir.

| Frame | Kaynak IPv4 |
|---|---|
| 17 | 192.0.2.0 |
| 18 | 192.0.2.255 |
| 19 | 192.0.1.255 |
| 20 | 192.0.3.0 |
| 21 | 192.0.2.1 |
| 22 | 192.0.2.254 |
| 49 | 192.0.2.10 |

/24 sınırı hangilerini içerir?

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"sinirlar"}
```

```bpf
src net 192.0.2.0/24
```

???

192.0.2.0–192.0.2.255 dahildir; 19 ve 20 dış komşulardır. Kaynak yönü hedef adresinden bağımsız sınanır.

```text
Paketler: 17, 18, 21, 22, 49
```
:::

::: gorev İki kaynak ağını birleştir
Kaynağı IPv4 `192.0.2.0/24` veya IPv6 `2001:db8:1::/126` içinde olanları seç. Hedefin ağda olması yetmesin. İki ağın ilk/son adresleri dahil, dış komşuları hariç olsun.

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
    eq(eslesenler(kayit=kayit),referans("src net 192.0.2.0/24 or src net 2001:db8:1::/126",kayit=kayit,dil="bpf"),kayit+": native paket kümesi")
eq(eslesenler(kayit="sinirlar"),[17,18,21,22,24,25,49],"sabit corpus kimlikleri")
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

frames=[frame(src=s,dst="198.51.100.20",proto=17) for s in ("192.0.1.255","192.0.2.0","192.0.2.1","192.0.2.255","192.0.3.0")]
frames += [frame(src=s,dst="2001:db8:ffff::20",proto=17) for s in ("2001:db8:0:ffff:ffff:ffff:ffff:ffff","2001:db8:1::","2001:db8:1::1","2001:db8:1::2","2001:db8:1::3","2001:db8:1::4")]
frames.append(frame(src="198.51.100.20",dst="192.0.2.10",proto=17))
eq(eslesenler(kayit=pcap(frames)),[2,3,4,7,8,9,10],"CIDR uçları ve ters yön")
```

```solution
src net 192.0.2.0/24 or src net 2001:db8:1::/126
```

```hint
İki src net koşulunu or ile bağla; IPv6 /126'yı genişletme.
```
:::

::: gorev TCP hedef aralığını kapat
Yalnız TCP hedef portu 79–81 dahil aralığında olanları seç. Kaynak portu, UDP/SCTP eşdeğeri, 78 ve 82 yeterli olmasın. Port 0/65535 aralık dışı; IPv4 seçenekli başlık da doğru port ofsetiyle değerlendirilsin.

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
    eq(eslesenler(kayit=kayit),referans("tcp dst portrange 79-81",kayit=kayit,dil="bpf"),kayit+": native paket kümesi")
eq(eslesenler(kayit="sinirlar"),[6,7,8,27,32,39,40,41],"sabit corpus kimlikleri")
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

frames=[frame(dport=p) for p in (0,1,78,79,80,81,82,65534,65535)]
frames += [frame(proto=17,dport=80),frame(proto=132,dport=80),frame(sport=80,dport=45000),frame(dport=80,options=b"\x01\x01\0\0")]
eq(eslesenler(kayit=pcap(frames)),[4,5,6,13],"iki dahil uç ve bağımsız protokol/yön")
```

```solution
tcp dst portrange 79-81
```

```hint
tcp dst portrange primitive'i üç niteliği birlikte taşır.
```
:::
