---
id: pk19
title: PCAPNG · Arayüz, Zaman ve Kesilmiş Kayıt
summary: Bir kayıtta birden fazla arayüzü ve farklı zaman çözünürlüklerini ayırt et.
---

::: anlat Dosya biçimi ile link-layer farklı şeylerdir
PCAPNG, section ve interface bloklarıyla birden fazla arayüzü tek dosyada tutabilir. `frame.interface_id` section içindeki arayüz kimliğidir; başka kayıtta aynı kimlik aynı ağ kartı anlamına gelmez. `arayuzler` eğitim kaydında Ethernet=0, RAW IP=1, Linux SLL=2, SLL2=3 arayüzleri vardır. Her birinde hedef portları 79/80/81 olan üç TCP paketi bulunur; son Ethernet paketi kasıtlı kesilmiştir.

Zaman birimi arayüzün `if_tsresol` seçeneğine bağlıdır. Aynı tamsayı her arayüzde aynı süre değildir. Tezgâh PCAPNG içindeki ondalık/ikilik çözünürlüğü ve zaman ofsetini tam kesirle saklar; frame sırasını zamana göre yeniden dizmez. Çıktıdaki `capture_interfaces` bunu gösterir. TShark görüntü filtresini özgün kayıt üzerinde değerlendirir.

Destek: classic PCAP 2.4 ve PCAPNG 1.0 Enhanced Packet Block; Ethernet, RAW, SLL ve SLL2. Eski Packet Block/Simple Packet Block açık hatayla reddedilir. Bütün PCAPNG uzantılarını desteklediğimiz varsayılmamalı.

Kaynak: [PCAPNG biçim taslağı](https://www.ietf.org/archive/id/draft-ietf-opsawg-pcapng-05.html), [TShark](https://www.wireshark.org/docs/man-pages/tshark.html).
```meta
dil: wireshark
```
```stdin
{"dil":"wireshark","kayit":"arayuzler"}
```
:::

::: tahmin
İkinci arayüzdeki port 80 paketini seçince hangi frame gelir?
```wireshark
frame.interface_id == 1 and tcp.dstport == 80
```
```meta
dil: wireshark
```
```stdin
{"dil":"wireshark","kayit":"arayuzler"}
```
???
Paketler: 5
Arayüz 1 RAW IP'dir; üç paketinden ortadaki hedef port 80'dir.
:::

::: gorev Arayüz ve port birlikte
Arayüz kimliği 1 ve TCP hedef portu 80 olan paketleri seç. Frame numarasını sabitleme; test kaydının sırası da değişir.
```starter
frame.number == 0
```
```meta
dil: wireshark
```
```stdin
{"dil":"wireshark","kayit":"arayuzler"}
```
```test
eq(eslesenler(), [5], "dört arayüzde 79/80/81 komşuları")
import packet_advanced_fixtures as af
from capture_formats import parse_capture
fs=parse_capture(af.mixed_capture())
interfaces=((1,65535,6),(101,65535,9),(113,65535,138),(276,65535,6))
scales=(10**6,10**9,1024,10**6)
rev=af.pcapng([(f.interface,int(f.timestamp*scales[f.interface]),f.data,f.wirelen) for f in reversed(fs)],interfaces)
eq(eslesenler(rev), [9], "frame sırası değişti")
```
```solution
frame.interface_id == 1 and tcp.dstport == 80
```
```hint
frame.interface_id ve tcp.dstport koşullarını and ile birleştir.
```
:::

::: gorev Kesilmiş paketi bul
Yakalanan bayt sayısı özgün hat uzunluğundan **küçük** olan paketleri seç. Eşit uzunlukta olanlar dahil olmasın.
```starter
frame.number == 0
```
```meta
dil: wireshark
```
```stdin
{"dil":"wireshark","kayit":"arayuzler"}
```
```test
eq(eslesenler(),[13],"kasıtlı snaplen kaybı")
import packet_advanced_fixtures as af
raw=af.pcapng([(0,0,b'x'*63,64),(0,1,b'x'*64,64),(0,2,b'x'*64,65)])
eq(eslesenler(raw),[1,3],"eşitlik ve iki kesilmiş komşu")
```
```solution
frame.cap_len < frame.len
```
```hint
İki frame alanını karşılaştır; tcp.len uygulama/taşıma katmanındaki farklı ölçüdür.
```
:::
