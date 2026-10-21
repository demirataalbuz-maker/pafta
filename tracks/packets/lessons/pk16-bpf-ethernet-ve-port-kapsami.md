---
id: pk16
title: BPF · Ethernet ve Port Kapsamı
summary: MAC adresi ile ARP protokol adresini, genel port ile yalnız TCP portunu karıştırma.
---

::: anlat Ethernet alanı ile ağ adresi aynı kimlik değildir
`ether src` Ethernet kaynak MAC alanını seçer. `src host` ağ/protokol adresine bakar; ARP içinde bunlar farklı alanlardır. Bir MAC'ten hem IPv4 hem ARP gelebilir. MAC koşuluna `ether proto 0x0806` eklendiğinde yalnız Ethernet türü ARP olanlar kalır. Burada sayısal EtherType kullanılır; bu sayı IP protokol numarası değildir.

MAC gözlemi tek başına cihazın kimliğini doğrulamaz. VLAN etiketli frame'in dış EtherType'ı da içteki IP türünden farklıdır. Bu derste MAC+ARP görevi etiketsiz ARP'yi ister. Kaynak: [pcap-filter ether](https://www.tcpdump.org/manpages/pcap-filter.7.html).

```bpf
ether src 02:00:00:00:00:10 and ether proto 0x0806
```

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"temel"}
```
:::

::: anlat Genel port TCP, UDP ve SCTP'yi kapsar
`port 53` yazınca yalnız DNS veya yalnız UDP istemiş olmazsın. Native BPF genel port koşulu TCP, UDP ve SCTP kaynak veya hedef portuna bakar. `tcp port 53` ise TCP ile sınırlar. Başlıkta 53 bulunması, yükün gerçekten DNS olduğunu kanıtlamaz.

Önceki sınırlar sürer: çıplak port koşulu VLAN'ı kendiliğinden açmaz; IPv4 sonraki fragmentinde taşıma başlığı yoktur, IPv6 uzantı zinciri de genel port erişimiyle otomatik çözülmez. Testlerde SCTP ve IPv6 doğrudan başlık tanıkları bulunur. Kaynak: [Npcap port ve portrange](https://npcap.com/guide/wpcap/pcap-filter.html).

```bpf
port 53
```

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"sinirlar"}
```
:::

::: tahmin
Aşağıdaki tablo `sinirlar` kaydında kaynak veya hedef 53 olabilecek bütün frame'leri listeler. Kalan 42 frame'de erişilebilen bir TCP/UDP/SCTP portu 53 değildir. Bütün satırlarda IPv4 taşıma başlığı ilk fragmentte bulunur.

| Frame | Dış katman | Taşıma | Kaynak port | Hedef port |
|---|---|---|---:|---:|
| 4 | Etiketsiz IPv4 | UDP | 42003 | 53 |
| 14 | Etiketsiz IPv4 | TCP | 53 | 44000 |
| 15 | Etiketsiz IPv4 | UDP | 53 | 44001 |
| 16 | Etiketsiz IPv4 | SCTP | 44002 | 53 |
| 31 | QinQ 100/200 içi IPv4 | UDP | 48002 | 53 |
| 36, 37, 38 | Etiketsiz IPv4 | UDP | 49035, 49036, 49037 | 53 |

Genel port filtresi SCTP'yi ve etiketli satırı nasıl ele alır?

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"sinirlar"}
```

```bpf
port 53
```

???

TCP, UDP ve SCTP içindeki 53 seçilir. 31'in VLAN katmanları açılmadığı için çıplak port filtresi o UDP başlığına ulaşmaz. Filtre DNS yükünün doğru olduğunu sınamıyor.

```text
Paketler: 4, 14, 15, 16, 36, 37, 38
```
:::

::: gorev Belirli MAC'ten gelen ARP
Ethernet kaynak MAC'i tam `02:00:00:00:00:10` ve dış EtherType'ı ARP (`0x0806`) olan frame'leri seç. Aynı MAC'ten gelen IP, başka MAC'ten ARP veya MAC'in yalnız hedefte bulunduğu ARP seçilmesin.

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
    eq(eslesenler(kayit=kayit),referans("ether src 02:00:00:00:00:10 and ether proto 0x0806",kayit=kayit,dil="bpf"),kayit+": native paket kümesi")
eq(eslesenler(kayit="temel"),[1],"sabit corpus kimlikleri")
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

mac="02:00:00:00:00:10"; diger="02:00:00:00:00:99"
ham=pcap([ethernet(arp(),0x0806,src=mac),frame(mac=mac),frame(mac=mac,src="2001:db8::10",dst="2001:db8::20"),ethernet(arp(),0x0806,src=diger),ethernet(arp(),0x0806,src=diger,dst=mac),ethernet(arp(),0x0806,src=mac,vlan=100)])
eq(eslesenler(kayit=ham),[1],"kaynak MAC ve dış EtherType koşulları birbirinden bağımsız")
```

```solution
ether src 02:00:00:00:00:10 and ether proto 0x0806
```

```hint
ether src MAC and ether proto 0x0806; IP host koşulunu MAC yerine koyma.
```
:::

::: gorev Her üç taşıma protokolünde port 53
Native BPF'nin genel port sözleşmesiyle kaynak **veya** hedef portu 53 olan paketleri seç: TCP, UDP ve SCTP dahil. Doğrudan IPv6 başlıkları da kapsansın. Port 52/54 dışarıda; VLAN açma ve uygulama yükü çözümleme yok.

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
    eq(eslesenler(kayit=kayit),referans("port 53",kayit=kayit,dil="bpf"),kayit+": native paket kümesi")
eq(eslesenler(kayit="sinirlar"),[4,14,15,16,36,37,38],"sabit corpus kimlikleri")
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

ham=pcap([frame(proto=p,dport=53) for p in (6,17,132)]+[frame(proto=p,sport=53,dport=41000) for p in (6,17,132)]+[frame(proto=p,dport=q) for p in (6,17,132) for q in (52,54)]+[frame(src="2001:db8::10",dst="2001:db8::20",proto=p,dport=53) for p in (6,17,132)]+[frame(proto=17,dport=53,vlan=100)])
eq(eslesenler(kayit=ham),[1,2,3,4,5,6,13,14,15],"TCP/UDP/SCTP iki yön; komşu portlar ve IPv6")
```

```solution
port 53
```

```hint
Protokol niteleyicisi eklemeden port 53 kullan; src/dst yazılmazsa iki yön kabul edilir.
```
:::
