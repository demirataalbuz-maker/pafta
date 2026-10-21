---
id: pk17
title: BPF · Çevrimdışı İnceleme
summary: tcpdump dosya seçeneklerini oku; istek ve dönüş yönünü kanıt sınırlarıyla filtrele.
---

::: anlat Komut satırı ile filtre alanı farklı yerlerdir
Bir dosyayı çevrimdışı inceleyen örnek komut `tcpdump -nn -r olay.pcap -c 3 "tcp dst port 80"` biçimindedir. `-r` dosyayı okur; canlı arayüz açmaz. `-n` adres adlarını, `-nn` ayrıca servis adlarını sayısal tutar. `-c 3` en fazla üç **eşleşen** paketten sonra durur; PCAP'teki ilk üç frame'i seçmek değildir. Kabuk tırnakları argümanı bir arada tutar; editöre yalnız içteki BPF ifadesini yazarsın.

`tcpdump -nn -r olay.pcap -w secilen.pcap "tcp port 80"` seçilen paketleri PCAP dosyasına yazar; `-w` metin raporu üretmez. Bu komutlar açıklama içindir, tezgâh dosya yazmaz ve tcpdump çalıştırmaz: aynı BPF ifadesini native libpcap ile mevcut sentetik kayda uygular. Kaynak: [tcpdump man sayfası](https://www.tcpdump.org/manpages/tcpdump.1.html).

```bpf
tcp dst port 80
```

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"olay"}
```
:::

::: anlat Önce yönü sınırla, sonra yorumu yap
Bir inceleme sorusunu küçük alanlara ayır: istemci kaynak adresi, sunucu hedef adresi, protokol ve hedef port. Dönüş yönünde adresler ile port yönü yer değiştirir. Geniş bir sunucu ağı seçmek, yalnız bir sunucu seçmekten farklı sonuç verir.

`tcp src port 80` HTTP yanıtı olduğunu, 401/500 durumunu veya başarılı oturum açmayı kanıtlamaz; yalnız başlıktaki sayıyı seçer. HTTP alanı gerekirse Wireshark görüntü filtresi veya uygulama çözümlemesi ayrı aşamadır. TCP SYN ve ACK de bu port filtresine girebilir. Kaynaklar: [pcap-filter yön nitelikleri](https://www.tcpdump.org/manpages/pcap-filter.7.html), [TShark okuma ve görüntü filtresi](https://www.wireshark.org/docs/man-pages/tshark.html).

```bpf
src net 198.51.100.0/24 and tcp src port 80
```

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"olay"}
```
:::

::: tahmin
`olay` kaydındaki kaynak portu 80 olan bütün TCP frame'leri aşağıda. Kalan 18 frame kaynak portu 80 olan TCP değildir. Alt ağın tamamı seçildiğinde ikinci sunucuyu da düşün.

| Frame | IPv4 kaynak | Hedef | TCP kaynak → hedef |
|---|---|---|---|
| 4 | 198.51.100.80 | 10.0.0.10 | 80 → 40100 |
| 7 | 198.51.100.80 | 10.0.0.10 | 80 → 40101 |
| 9 | 198.51.100.80 | 10.0.0.10 | 80 → 40102 |
| 13 | 198.51.100.81 | 10.0.0.11 | 80 → 40103 |
| 15 | 198.51.100.80 | 10.0.0.10 | 80 → 40104 |
| 22 | 198.51.100.80 | 10.0.0.10 | 80 → 40107 |
| 24 | 198.51.100.80 | 10.0.0.10 | 80 → 40108 |

Filtrenin tam çıktısı nedir?

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"olay"}
```

```bpf
src net 198.51.100.0/24 and tcp src port 80
```

???

Listelenen yedi frame'in kaynağı /24 içinde, taşıması TCP ve kaynak portu 80'dir. 13 farklı istemciye dönse de hedef adres koşulu yazılmadığından seçilir. Bu kümeden HTTP durum kodu çıkarılamaz.

```text
Paketler: 4, 7, 9, 13, 15, 22, 24
```
:::

::: gorev Tek istemciden tek web portuna
Yalnız IPv4 kaynak `10.0.0.10`, hedef `198.51.100.80` ve TCP hedef portu 80 olan frame'leri seç. Bağlantı kurulumu da dahil; HTTP yükü veya durum kodu şartı yok. Aynı porttaki başka kaynak/hedef ve UDP dışarıda olsun.

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"olay"}
```

```starter
ip
```

```test
for kayit in ("temel","sinirlar","olay"):
    eq(eslesenler(kayit=kayit),referans("src host 10.0.0.10 and dst host 198.51.100.80 and tcp dst port 80",kayit=kayit,dil="bpf"),kayit+": native paket kümesi")
eq(eslesenler(kayit="olay"),[3,5,6,8,14,21,23],"sabit corpus kimlikleri")
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

ham=pcap([frame(src="10.0.0.10",dst="198.51.100.80",dport=80),frame(src="10.0.0.11",dst="198.51.100.80",dport=80),frame(src="10.0.0.10",dst="198.51.100.81",dport=80),frame(src="10.0.0.10",dst="198.51.100.80",dport=79),frame(src="10.0.0.10",dst="198.51.100.80",dport=81),frame(src="10.0.0.10",dst="198.51.100.80",dport=80,proto=17),frame(src="198.51.100.80",dst="10.0.0.10",sport=80,dport=41000)])
eq(eslesenler(kayit=ham),[1],"kaynak, hedef, port ve taşıma koşullarını tek tek bozan tanıklar")
```

```solution
src host 10.0.0.10 and dst host 198.51.100.80 and tcp dst port 80
```

```hint
İki host koşulunun yönlerini yaz, sonra tcp dst port 80 ile and üzerinden birleştir.
```
:::

::: gorev Sunucu ağından istemciye dönüş
IPv4 kaynak ağı `198.51.100.0/24`, hedef host `10.0.0.10` ve TCP kaynak portu 80 olanları seç. /24 içindeki .0 ve .255 dahil; bitişik ağlar dışarıda. Farklı istemci, UDP ve hedef portu 80 olan ters yön yetmez.

```meta
dil: bpf
```

```stdin
{"dil":"bpf","kayit":"olay"}
```

```starter
ip
```

```test
for kayit in ("temel","sinirlar","olay"):
    eq(eslesenler(kayit=kayit),referans("src net 198.51.100.0/24 and dst host 10.0.0.10 and tcp src port 80",kayit=kayit,dil="bpf"),kayit+": native paket kümesi")
eq(eslesenler(kayit="olay"),[4,7,9,15,22,24],"sabit corpus kimlikleri")
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

adresler=("198.51.99.255","198.51.100.0","198.51.100.80","198.51.100.255","198.51.101.0")
ham=pcap([frame(src=s,dst="10.0.0.10",sport=80,dport=41000) for s in adresler]+[frame(src="198.51.100.80",dst="10.0.0.11",sport=80,dport=41000),frame(src="198.51.100.80",dst="10.0.0.10",sport=80,dport=41000,proto=17),frame(src="198.51.100.80",dst="10.0.0.10",sport=79,dport=41000),frame(src="198.51.100.80",dst="10.0.0.10",sport=81,dport=41000),frame(src="198.51.100.80",dst="10.0.0.10",sport=41000,dport=80)])
eq(eslesenler(kayit=ham),[2,3,4],"ağ iki ucu ve komşuları; hedef, protokol ve port yönü")
```

```solution
src net 198.51.100.0/24 and dst host 10.0.0.10 and tcp src port 80
```

```hint
src net, dst host ve tcp src port ayrı sorular; hepsi and ile gerekli.
```
:::
