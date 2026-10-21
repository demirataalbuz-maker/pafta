---
id: pk14
title: BPF · Başlık ve Parçalanma
summary: IPv4 IHL, fragment offset ve eksik yakalanan baytları sabit ofset sanmadan oku.
---

::: anlat IPv4 başlığı her zaman 20 bayt değildir
`ip[0]` IPv4 başlığının ilk baytıdır. Üst dört bit sürüm, alt dört bit IHL'dir; IHL dört baytlık sözcük sayısını verir. `ip[0] & 0x0f > 5`, 20 bayttan uzun IPv4 başlığı ister. IHL=6 için başlık 24 bayttır. Ethernet'ten itibaren sabit TCP ofseti yazmak bu pakette kayar; `tcp[...]` erişimi IPv4 IHL'sini hesaba katar.

Bu örnekte `ip[...]` etiketsiz Ethernet IPv4 içindir. VLAN açılması bir sonraki derstedir; IPv6'nın ayrı başlık yapısı vardır. Kaynak: [pcap-filter paket veri erişimi](https://www.tcpdump.org/manpages/pcap-filter.7.html).

```bpf
ip[0] & 0x0f > 5
```

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"sinirlar"}
```
:::

::: anlat İlk fragment ile sonraki fragmenti ayır
`ip[6:2]`, IPv4 flags+fragment offset alanını iki bayt, ağ bayt sırasıyla okur. `0x1fff` maskesi 13 bit offset'i bırakır. Sıfır olmayan değer sonraki fragmenttir. MF biti tek başına sonraki fragment anlamına gelmez: offset=0, MF=1 ilk fragmenttir ve TCP başlığı taşıyabilir. Offset 8 baytlık birimdir; offset=1, yükün sekizinci baytından başlar.

BPF burada yeniden birleştirme yapmaz. Port erişimi sonraki IPv4 fragmentte yoktur. Ayrıca yakalanmamış bir baytı okumaya çalışan native BPF yükü o frame'in değerlendirmesini başarısız bitirir; bunu genel bir `not` ile güvenilirce tersine çevireceğini varsayma. Kayıt kesintisi, ağdaki gerçek başlığın yokluğu değildir. Kaynak: [Npcap fragment ve erişim kuralları](https://npcap.com/guide/wpcap/pcap-filter.html).

```bpf
ip[6:2] & 0x1fff != 0
```

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"sinirlar"}
```
:::

::: tahmin
`sinirlar` 50 frame içerir. Seçimi belirleyen başlık durumu bütün kayıt için şöyledir. Offset sütunu 8 baytlık birimdedir.

| Frame | Katman | Offset | MF |
|---|---|---:|---:|
| 27 | Etiketsiz IPv4 ilk fragment | 0 | 1 |
| 28 | Etiketsiz IPv4 sonraki fragment | 3 | 0 |
| 1–22, 32, 36–47, 49–50 | Diğer etiketsiz IPv4 | 0 | 0 |
| 29–31 | VLAN/QinQ içindeki IPv4; burada açılmıyor | 0 | 0 |
| 23–26, 33–35 | IPv6 | — | — |
| 48 | ARP | — | — |

50'nin yalnız ilk 36 baytı saklanmıştır; IPv4 flags/offset alanı bu sınırın içindedir. Maske hangi frame'i bırakır?

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"sinirlar"}
```

```bpf
ip[6:2] & 0x1fff != 0
```

???

Yalnız 28'in offset'i sıfır değildir. 27'de MF açık olsa da offset sıfırdır. IPv6 fragment başlığı aynı IPv4 alanı değildir; VLAN içi paketler de çıplak ip erişimiyle açılmaz.

```text
Paketler: 28
```
:::

::: gorev IPv4 seçenekli başlık
Etiketsiz Ethernet üzerindeki IPv4 paketlerinden IHL değeri 5'ten büyük olanları seç. IHL=5 dışarıda, IHL=6 ve 7 içeride olsun. IPv6, ARP ve VLAN içi IPv4 bu görevin kapsamında değil.

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
    eq(eslesenler(kayit=kayit),referans("ip[0] & 0x0f > 5",kayit=kayit,dil="bpf"),kayit+": native paket kümesi")
eq(eslesenler(kayit="sinirlar"),[32],"sabit corpus kimlikleri")
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

ham=pcap([frame(),frame(options=b"\x01"*4),frame(options=b"\x01"*8),frame(src="2001:db8::10",dst="2001:db8::20"),ethernet(arp(),0x0806),frame(options=b"\x01"*4,vlan=100)])
eq(eslesenler(kayit=ham),[2,3],"IHL 5/6/7 ve bağımsız katman karşı örnekleri")
```

```solution
ip[0] & 0x0f > 5
```

```hint
Alt dört bit için & 0x0f kullan; sürüm bitlerini IHL karşılaştırmasına katma.
```
:::

::: gorev Yalnız sonraki IPv4 fragmentler
Etiketsiz IPv4 fragment offset'i sıfır olmayan frame'leri seç. MF veya DF bitini offset sanma. İlk fragment (offset=0, MF=1) dışarıda; offset=1 dahil olsun. Port numarası arama ve yeniden birleştirme yapma.

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
    eq(eslesenler(kayit=kayit),referans("ip[6:2] & 0x1fff != 0",kayit=kayit,dil="bpf"),kayit+": native paket kümesi")
eq(eslesenler(kayit="sinirlar"),[28],"sabit corpus kimlikleri")
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

def parca(offset,flags):
    return ethernet(ipv4(b"X"*24,proto=6,flags=flags,frag_offset=offset))
ham=pcap([parca(0,0),parca(0,1),parca(1,0),parca(2,1),parca(0,2),parca(8191,0),frame(src="2001:db8::10",dst="2001:db8::20")])
eq(eslesenler(kayit=ham),[3,4,6],"offset 0/1/2/8191; MF ve DF bağımsız")
kesik=frame()
eq(eslesenler(kayit=pcap([(kesik[:20],len(kesik))])),[],"flags/offset baytları yakalanmamışsa eşleşme yok")
```

```solution
ip[6:2] & 0x1fff != 0
```

```hint
İki baytlık alanı oku, 0x1fff ile yalnız offset'i bırak ve sıfırla karşılaştır.
```
:::
