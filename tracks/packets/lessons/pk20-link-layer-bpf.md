---
id: pk20
title: BPF · Ethernet Dışında Doğru Başlangıç
summary: RAW IP ve Linux cooked kayıtlarında gerçek DLT ile filtre derlemek.
---

::: anlat Ethernet ofsetini her kayda uygulama
`tcp dst port 80` ifadesinin bayt kodu link-layer türüne göre derlenir. RAW IP başında Ethernet başlığı yoktur; Linux SLL/SLL2 başlıkları da Ethernet değildir. Tezgâh her arayüzün gerçek DLT'siyle ayrı libpcap programı derler, sonra özgün frame sırasını koruyarak sonuçları birleştirir. RAW için dosyadaki LINKTYPE_RAW=101 ile libpcap DLT_RAW=12 eşleştirilir; sayılar körlemesine aynı kabul edilmez.

`ether` gibi bazı işlemler her DLT'de anlamlı değildir. Native derleyici bir arayüzde filtreyi desteklemiyorsa tüm işlem açık hata verir; o arayüz sessizce dışlanmaz. `len` özgün hat uzunluğudur, yakalanan bayt sayısı değildir. Kesilmiş pakette port alanı okunamayabilir; uzunluğu yine test edilebilir.

Kaynak: [libpcap filtreleri](https://npcap.com/guide/wpcap/pcap-filter.html), [pcap_open_dead](https://npcap.com/guide/wpcap/pcap_open_dead.html).
```meta
dil: bpf
```
```stdin
{"dil":"bpf","kayit":"arayuzler"}
```
:::

::: tahmin
Aynı port filtresi dört link-layer üzerinde ne seçer?
```bpf
tcp dst port 80
```
```meta
dil: bpf
```
```stdin
{"dil":"bpf","kayit":"arayuzler"}
```
???
Paketler: 2, 5, 8, 11
Her arayüzde port 80 olan tam paket seçilir; kesilmiş son pakette TCP portları yoktur.
:::

::: gorev Dört link-layer üzerinde hedef port
TCP hedef portu tam 80 olan paketleri seç. Kaynak portun 80 olması yeterli olmasın.
```starter
tcp dst port 0
```
```meta
dil: bpf
```
```stdin
{"dil":"bpf","kayit":"arayuzler"}
```
```test
eq(eslesenler(),[2,5,8,11],"dört arayüz ve komşu portlar")
import packet_advanced_fixtures as af
import packet_fixtures as pf
packets=[]
for src,dst in ((80,81),(81,80),(80,80),(81,79)):
    b=pf.ipv4(pf.tcp(src,dst),pf.CLIENT,pf.SERVER,6)
    packets.append((0,0,b,len(b)))
eq(eslesenler(af.pcapng(packets,((101,65535,6),))),[2,3],"kaynak/hedef ve RAW")
```
```solution
tcp dst port 80
```
```hint
Filtre dilinde noktalı alan adı yerine dst port nitelendiricisini kullan.
```
:::

::: gorev Kapsayıcı hat uzunluğu sınırı
Özgün hat uzunluğu **en az 128** bayt olan paketleri seç. Yakalanan bayt miktarı karar vermesin.
```starter
len < 0
```
```meta
dil: bpf
```
```stdin
{"dil":"bpf","kayit":"arayuzler"}
```
```test
eq(eslesenler(),[13],"30 bayt yakalandı ama hat uzunluğu 128")
import packet_advanced_fixtures as af
raw=af.pcapng([(0,i,b'x'*64,n) for i,n in enumerate((127,128,129))])
eq(eslesenler(raw),[2,3],"127/128/129 sınır komşuları")
```
```solution
len >= 128
```
```hint
>= eşikteki 128 baytı da kabul eder.
```
:::
