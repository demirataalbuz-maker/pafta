---
id: p80
title: Scapy · PCAP'i Katman Katman Okumak
summary: Kurulu Scapy ile bir paket kaydını Python'dan açmak: rdpcap ve PcapReader, katman yığını, haslayer ve alan okuma; başlık alanı ile çözülmüş katman farkı; snaplen kırpması (caplen/wirelen) ile yarıda kesilmiş dosyayı ayırmak ve sonucu TShark'la karşılaştırmak.
backend: wsl
timeout: 90
---

::: anlat Bir kayıt dosyası, Python'dan
Paket yolunda kayıtları Wireshark ve TShark filtreleriyle okudun. Bir kaydı **kendi kuralınla** işlemek gerektiğinde (her akıştan bir alan çıkarmak, bozuk kayıtları ayıklamak, bir rapor üretmek) Python'da **Scapy** kullanılır. Bu iki ders Kali'nin sistem Python'undaki kurulu Scapy ile gerçek Linux'ta çalışır; TShark da aynı makinededir.

```python
import subprocess, sys
import scapy
print(sys.version.split()[0], scapy.__version__)
print(subprocess.run(["tshark", "--version"], capture_output=True, text=True).stdout.splitlines()[0])
```

Scapy'de bir paket **katmanların yığınıdır**: `Ether / IP / TCP / Raw`. Her katman bir nesnedir ve alanları adla okunur:

| Yazım | Ne verir |
|---|---|
| `rdpcap("k.pcap")` | bütün kaydı belleğe bir liste olarak okur |
| `PcapReader("k.pcap")` | kaydı paket paket akıtır; büyük dosyada bellek dostu |
| `p.haslayer(TCP)` | o katman çözüldü mü (sayı döner: 0 ya da konumu) |
| `p[IP].src`, `p[TCP].dport` | alan değeri |
| `p.getlayer(TCP)` | katman nesnesi ya da `None` |
| `len(p)` | dosyada **saklanan** bayt sayısı |
| `p.wirelen` | paketin hattaki **gerçek** uzunluğu |
| `p.time` | zaman damgası (saniye; `float()` ile sayıya çevrilir) |

```python
from scapy.all import Ether, IP, TCP, UDP, Raw, wrpcap, rdpcap
M = dict(src="02:00:00:00:00:01", dst="02:00:00:00:00:02")
istek = Ether(**M) / IP(src="10.0.0.5", dst="10.0.0.9") / TCP(sport=51544, dport=80, flags="PA") / Raw(b"GET / HTTP/1.1\r\nHost: pafta.test\r\n\r\n")
dns = Ether(**M) / IP(src="10.0.0.5", dst="10.0.0.53") / UDP(sport=5353, dport=53)
istek.time, dns.time = 1792400000, 1792400001
wrpcap("ornek.pcap", [istek, dns])
for no, p in enumerate(rdpcap("ornek.pcap"), 1):
    print(no, p.summary(), len(p), p.haslayer(TCP), p[IP].proto)
```

Örneklerde MAC ve IP adreslerini **hep açıkça** veriyoruz. Verilmezse Scapy bulunduğu makinenin yönlendirme tablosuna bakıp bir kaynak adresi seçer, MAC için ağa sormaya çalışır ve uyarı basar: sonuç makineden makineye değişir.
:::

::: anlat Başlık ne diyor, Scapy neyi çözdü
`haslayer(TCP)` ile `p[IP].proto == 6` aynı soru değildir. İlki "Scapy TCP başlığını **çözebildi** mi?", ikincisi "IP başlığı bir sonraki katmanın TCP **olduğunu söylüyor** mu?" diye sorar. Normal pakette ikisi aynı yanıtı verir. Kırpılmış bir pakette ayrılırlar: IP başlığı TCP der, ama TCP başlığının baytları dosyada yoktur; Scapy kalan baytları `Raw` diye bırakır.

Bir paketin dosyada eksik saklanmasının **iki ayrı nedeni** vardır ve incelemede ikisini karıştırmamak gerekir:

| Durum | Ne olmuştur | PCAP kaydında | Scapy'de |
|---|---|---|---|
| **snaplen kırpması** | kayıt aracı her paketin yalnız ilk N baytını bilerek sakladı (`tcpdump -s 96`) | `caplen < wirelen`, veri caplen kadar tam | `len(p) < p.wirelen` |
| **yarıda kesilmiş dosya** | dosya yazılırken kopyalama, disk dolması ya da çökme | kaydın başlığı N bayt der, dosyada daha azı vardır | **uyarı yok**: kısa paket sessizce gelir |

İkincisi daha tehlikelidir: Scapy'nin `rdpcap`'i dosyanın sonundaki eksik kaydı hiçbir şey söylemeden kısa bir paket olarak verir. Bunu görmek için kaydın kendi başlığını okuyan `RawPcapReader` kullanılır: her kayıt için `(ham_bayt, meta)` verir, `meta.caplen` başlığın söylediği saklanan uzunluk, `meta.wirelen` hattaki uzunluktur. `len(ham) < meta.caplen` ise dosya o kaydın ortasında bitmiştir. TShark aynı dosyada açıkça hata verir ve 0 dışı kodla çıkar:

```python
import subprocess
from scapy.all import Ether, IP, TCP, wrpcap
M = dict(src="02:00:00:00:00:01", dst="02:00:00:00:00:02")
p = Ether(**M) / IP(src="10.0.0.5", dst="10.0.0.9") / TCP(sport=40000, dport=80)
p.time = 1792400000
wrpcap("kesik.pcap", [p, p])
veri = open("kesik.pcap", "rb").read()
open("kesik.pcap", "wb").write(veri[:-20])
t = subprocess.run(["tshark", "-r", "kesik.pcap", "-T", "fields", "-e", "frame.number", "-e", "frame.cap_len"],
                   capture_output=True, text=True)
print(t.returncode, t.stdout.split(), t.stderr.strip())
```

Bozuk bir dosyanın (PCAP olmayan bir şeyin) `rdpcap`'i ise `Scapy_Exception: Not a supported capture file` verir; olmayan dosya `FileNotFoundError`. Kendi aracında bunları ayırt edilebilir hatalara çevir: "dosya yok", "PCAP değil" ve "PCAP ama son kaydı eksik" üç ayrı rapordur.

Kaynak: [Scapy, PCAP okuma ve yazma](https://scapy.readthedocs.io/en/latest/usage.html#reading-pcap-files), [libpcap dosya biçimi: kayıt başlığı, incl_len ve orig_len](https://www.tcpdump.org/manpages/pcap-savefile.5.txt).
:::

::: tahmin Kesik dosyada Scapy ne görür?
```python
from scapy.all import Ether, IP, TCP, wrpcap, rdpcap, RawPcapReader
M = dict(src="02:00:00:00:00:01", dst="02:00:00:00:00:02")
p = Ether(**M) / IP(src="10.0.0.5", dst="10.0.0.9") / TCP(sport=40000, dport=80)
p.time = 1792400000
wrpcap("t.pcap", [p, p])
veri = open("t.pcap", "rb").read()
open("t.pcap", "wb").write(veri[:-20])
paketler = rdpcap("t.pcap")
print(len(paketler), [len(x) for x in paketler])
print(paketler[1].haslayer(TCP), paketler[1].wirelen)
for ham, meta in RawPcapReader("t.pcap"):
    print(len(ham), meta.caplen)
```

???

```text
2 [54, 34]
0 54
54 54
34 54
```

Her paket 54 bayttır (14 Ethernet + 20 IP + 20 TCP). Son 20 baytı silmek ikinci kaydın TCP başlığını götürür. `rdpcap` yine iki paket verir; ikincisi 34 bayttır, IP katmanı çözülür ama TCP çözülemez: `haslayer` **0** döner (`False` değil, bir sayı). `wirelen` 54 kalır çünkü kayıt başlığında yazandır. `RawPcapReader` ise asıl kanıtı gösterir: başlık 54 bayt saklandığını söylüyor, dosyada 34 bayt var.
:::

::: gorev Kayıttan IPv4 özeti
`ozet(yol)` yaz: PCAP dosyasındaki **IPv4** paketleri için birer tuple içeren bir liste döndür:

`(no, kaynak, hedef, proto, sport, dport, saklanan, hattaki)`

- `no`: paketin dosyadaki sırası, 1'den başlar; IPv4 olmayan paketler listeye girmez ama numara saymaya devam eder.
- `proto`: IP başlığının söylediği protokol: 6 ise `"TCP"`, 17 ise `"UDP"`, başka her şey `"diğer"`.
- `sport`, `dport`: taşıma katmanı **çözülebildiyse** portlar, çözülemediyse (kırpılmış başlık ya da başka protokol) `None`.
- `saklanan`: dosyada saklanan bayt sayısı; `hattaki`: paketin gerçek uzunluğu.
- Dosya yoksa `FileNotFoundError`, PCAP değilse `ValueError`. Yalnız dosya başlığı olan boş kayıt `[]` verir.

Hazırlık klasörde `kayit.pcap`'i üretir: TCP isteği, DNS sorgusu, ARP, ICMP ve TCP başlığının ortasından kırpılmış (snaplen 40) bir paket.

```setup
from scapy.all import Ether, IP, TCP, UDP, ICMP, ARP, Raw, wrpcap
M = dict(src="02:00:00:00:00:01", dst="02:00:00:00:00:02")
p1 = Ether(**M) / IP(src="10.0.0.5", dst="10.0.0.9") / TCP(sport=51544, dport=80, flags="PA") / Raw(b"GET / HTTP/1.1\r\n\r\n")
p2 = Ether(**M) / IP(src="10.0.0.5", dst="10.0.0.53") / UDP(sport=5353, dport=53) / Raw(b"\x00" * 12)
p3 = Ether(**M) / ARP(psrc="10.0.0.1", pdst="10.0.0.5", hwsrc=M["src"])
p4 = Ether(**M) / IP(src="10.0.0.9", dst="10.0.0.5") / ICMP()
ham = bytes(Ether(**M) / IP(src="10.0.0.7", dst="10.0.0.9") / TCP(sport=40000, dport=443, flags="S"))
p5 = Ether(ham[:40]); p5.wirelen = len(ham)
for i, p in enumerate((p1, p2, p3, p4, p5)):
    p.time = 1792400000 + i
wrpcap("kayit.pcap", [p1, p2, p3, p4, p5])
```

```starter
from scapy.all import rdpcap, IP, TCP, UDP

def ozet(yol):
    sonuc = []
    for no, p in enumerate(rdpcap(yol)):
        if p.haslayer(TCP):
            sonuc.append((no, p[IP].src, p[IP].dst, "TCP", p[TCP].sport, p[TCP].dport, len(p), len(p)))
    return sonuc
```

```test
import subprocess
from scapy.all import Ether, IP, IPv6, UDP, wrpcap
f = need("ozet")
eq(f("kayit.pcap"), [
    (1, "10.0.0.5", "10.0.0.9", "TCP", 51544, 80, 72, 72),
    (2, "10.0.0.5", "10.0.0.53", "UDP", 5353, 53, 54, 54),
    (4, "10.0.0.9", "10.0.0.5", "diğer", None, None, 42, 42),
    (5, "10.0.0.7", "10.0.0.9", "TCP", None, None, 40, 54),
], "beş paketten dördü IPv4; ARP sayılır ama listeye girmez; kırpılmış TCP'nin portu yok")
t = subprocess.run(["tshark", "-r", "kayit.pcap", "-T", "fields", "-e", "frame.number", "-e", "frame.cap_len", "-e", "frame.len", "-e", "ip.proto"],
                   capture_output=True, text=True)
tshark = [s.split("\t") for s in t.stdout.split("\n") if s and s.split("\t")[3]]
eq([(r[0], r[1], r[2], r[3]) for r in tshark], [(str(x[0]), str(x[6]), str(x[7]), {"TCP": "6", "UDP": "17"}.get(x[3], "1")) for x in f("kayit.pcap")],
   "numara, saklanan, hattaki ve protokol TShark ile aynı")
M = dict(src="02:00:00:00:00:01", dst="02:00:00:00:00:02")
v6 = Ether(**M) / IPv6(src="fd00::1", dst="fd00::2") / UDP(sport=1, dport=2)
v4 = Ether(**M) / IP(src="10.0.0.1", dst="10.0.0.2") / UDP(sport=65535, dport=1)
v6.time = v4.time = 1792400100
wrpcap("v6.pcap", [v6, v4])
eq(f("v6.pcap"), [(2, "10.0.0.1", "10.0.0.2", "UDP", 65535, 1, 42, 42)], "IPv6 listeye girmez, numara yine sayılır; port sınırı 65535")
wrpcap("bos.pcap", [])
eq(f("bos.pcap"), [], "yalnız dosya başlığı olan kayıt")
open("metin.pcap", "w").write("bu bir paket kaydı değil")
raises(ValueError, f, "metin.pcap", msg="PCAP olmayan dosya")
raises(FileNotFoundError, f, "olmayan.pcap", msg="olmayan dosya")
```

```solution
from scapy.all import rdpcap, IP, TCP, UDP
from scapy.error import Scapy_Exception

def ozet(yol):
    try:
        paketler = rdpcap(yol)
    except Scapy_Exception as e:
        raise ValueError(f"PCAP değil: {e}")
    sonuc = []
    for no, p in enumerate(paketler, 1):
        if not p.haslayer(IP):
            continue
        proto = {6: "TCP", 17: "UDP"}.get(p[IP].proto, "diğer")
        katman = {"TCP": TCP, "UDP": UDP}.get(proto)
        if katman is not None and p.haslayer(katman):
            sport, dport = p[katman].sport, p[katman].dport
        else:
            sport = dport = None
        sonuc.append((no, p[IP].src, p[IP].dst, proto, sport, dport, len(p), p.wirelen))
    return sonuc
```

```hint
Numara için `enumerate(..., 1)`. Protokolü `haslayer`'dan değil `p[IP].proto`'dan al; portları ise ancak `haslayer(TCP)` ya da `haslayer(UDP)` doğruysa oku.
```

```hint
`rdpcap` PCAP olmayan dosyada `scapy.error.Scapy_Exception` yükseltir; onu yakalayıp `ValueError`'a çevir. Saklanan `len(p)`, hattaki `p.wirelen`.
```
:::

::: gorev Kırpılmış mı, kesik mi?
`butunluk(yol)` yaz; bir PCAP dosyasının kayıtlarını denetleyip `(kayit_sayisi, kirpik, kesik)` döndür:

- `kayit_sayisi`: dosyadaki kayıt sayısı (kesik kayıt da sayılır).
- `kirpik`: **snaplen** yüzünden bilerek kısa saklanmış kayıtların numaraları: kayıt başlığında saklanan uzunluk hattakinden küçük, ama veri o uzunlukta tam.
- `kesik`: dosya **yarıda bittiği** için verisi kayıt başlığının söylediğinden kısa olan kayıtların numaraları.
- Numaralar 1'den başlar, listeler artan sıradadır. Bir kayıt hem kırpık hem kesik olabilir.
- Dosya yoksa `FileNotFoundError`, PCAP değilse `ValueError`.

Kayıt başlığındaki uzunlukları `RawPcapReader` verir.

```setup
from scapy.all import Ether, IP, TCP, Raw, wrpcap
M = dict(src="02:00:00:00:00:01", dst="02:00:00:00:00:02")
def paket(n):
    p = Ether(**M) / IP(src="10.0.0.5", dst="10.0.0.9") / TCP(sport=40000 + n, dport=80) / Raw(b"x" * 46)
    p.time = 1792400000 + n
    return p
def kirpik(p, n):
    ham = bytes(p); k = Ether(ham[:n]); k.wirelen = len(ham); k.time = p.time
    return k
wrpcap("temiz.pcap", [paket(1), paket(2), paket(3)])
wrpcap("snaplen.pcap", [kirpik(paket(1), 64), paket(2), kirpik(paket(3), 34)])
wrpcap("kesik.pcap", [paket(1), paket(2), paket(3)])
veri = open("kesik.pcap", "rb").read()
open("kesik.pcap", "wb").write(veri[:-30])
wrpcap("ikisi.pcap", [paket(1), kirpik(paket(2), 80)])
veri = open("ikisi.pcap", "rb").read()
open("ikisi.pcap", "wb").write(veri[:-6])
```

```starter
from scapy.all import rdpcap

def butunluk(yol):
    paketler = rdpcap(yol)
    kirpik = [i for i, p in enumerate(paketler, 1) if len(p) < p.wirelen]
    return len(paketler), kirpik, []
```

```test
import subprocess
from scapy.all import Ether, IP, wrpcap
f = need("butunluk")
eq(f("temiz.pcap"), (3, [], []), "temiz kayıt")
eq(f("snaplen.pcap"), (3, [1, 3], []), "snaplen ile kırpılmış 1 ve 3 kesik değildir")
eq(f("kesik.pcap"), (3, [], [3]), "son kaydı yarıda kalan dosya")
eq(f("ikisi.pcap"), (2, [2], [2]), "hem kırpık hem kesik kayıt")
t = subprocess.run(["tshark", "-r", "kesik.pcap", "-T", "fields", "-e", "frame.number"], capture_output=True, text=True)
ok(t.returncode != 0 and "cut short" in t.stderr, "TShark da kesik dosyayı reddediyor (ölçüm)", got=(t.returncode, t.stderr.strip()))
t = subprocess.run(["tshark", "-r", "snaplen.pcap", "-T", "fields", "-e", "frame.cap_len", "-e", "frame.len"], capture_output=True, text=True)
eq((t.returncode, t.stdout.split()), (0, ["64", "100", "100", "100", "34", "100"]), "TShark snaplen kaydını hata saymadan okur")
M = dict(src="02:00:00:00:00:01", dst="02:00:00:00:00:02")
tam = Ether(**M) / IP(src="10.0.0.1", dst="10.0.0.2"); tam.time = 1792400200
ham = bytes(tam); bir = Ether(ham[:-1]); bir.wirelen = len(ham); bir.time = 1792400201
wrpcap("sinir.pcap", [tam, bir])
eq(f("sinir.pcap"), (2, [2], []), "saklanan = hattaki kırpık değil; bir bayt eksiği bile kırpık")
wrpcap("bos.pcap", [])
eq(f("bos.pcap"), (0, [], []), "boş kayıt")
open("metin.pcap", "w").write("pcap değil")
raises(ValueError, f, "metin.pcap", msg="PCAP olmayan dosya")
raises(FileNotFoundError, f, "olmayan.pcap", msg="olmayan dosya")
```

```solution
from scapy.all import RawPcapReader
from scapy.error import Scapy_Exception

def butunluk(yol):
    try:
        okuyucu = RawPcapReader(yol)
    except Scapy_Exception as e:
        raise ValueError(f"PCAP değil: {e}")
    sayi, kirpik, kesik = 0, [], []
    with okuyucu:
        for no, (ham, meta) in enumerate(okuyucu, 1):
            sayi = no
            if meta.caplen < meta.wirelen:
                kirpik.append(no)
            if len(ham) < meta.caplen:
                kesik.append(no)
    return sayi, kirpik, kesik
```

```hint
`for ham, meta in RawPcapReader(yol)`: `meta.caplen` başlığın söylediği saklanan uzunluk, `meta.wirelen` hattaki uzunluk, `len(ham)` dosyadan gerçekten okunan bayt.
```

```hint
Kırpık: `meta.caplen < meta.wirelen`. Kesik: `len(ham) < meta.caplen`. İkisi bağımsızdır; ikisini ayrı ayrı denetle.
```
:::
