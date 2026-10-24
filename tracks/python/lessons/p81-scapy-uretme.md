---
id: p81
title: Scapy · Paket Üretmek ve Doğrulamak
summary: Scapy ile katman katman paket kurmak; hesaplanan alanların (chksum, len) serileştirmeye kadar None kalması, bytes(p)'nin nesneyi değiştirmemesi, bir alanı elle verince otomatik hesabın kapanması; varsayılan alanlar ve proto'nun yükten türemesi; wrpcap ile zaman damgalı kayıt yazmak, geri okumak; sağlamayı Scapy'de yeniden hesaplayarak doğrulamak ve TShark'ın sağlamayı varsayılanda doğrulamadığını (status 2), tercih açılınca iyi/kötü (1/0) ayırdığını görmek.
backend: wsl
timeout: 90
---

::: anlat Paketi kurmak: ne yazarsın, ne hesaplanır
P80'de bir kaydı okudun. Şimdi paketi **kendin kuracaksın**: bir protokolü anlamak, bir aracı test etmek ya da bir kaydı yeniden üretmek için. Bu ders de Kali'nin kurulu Scapy'siyle gerçek Linux'ta çalışır; paketleri ağa göndermeyip dosyaya yazıp geri okuyacağız, böylece sonuç belirlidir.

Paket katmanların `/` ile yığılmasıdır. Her katmanın **varsayılan** alanları vardır; yalnız değiştireceğini yazarsın:

```python
from scapy.all import Ether, IP, TCP
print("IP:", IP().ttl, IP().version, IP().proto)     # 64 4 0
print("TCP:", TCP().dport, int(TCP().flags))          # 80 2  (flags=2 => SYN)
```

Bir alanı vermezsen Scapy ya sabit bir varsayılan (TTL 64) ya da **kuruluşta hesaplanan** bir değer koyar. İki alan paketi serileştirene (`bytes(p)`, `wrpcap`) kadar **boş** durur:

```python
from scapy.all import IP, TCP
p = IP(src="10.0.0.5", dst="10.0.0.9") / TCP(sport=1234, dport=80, flags="S")
print(p[IP].chksum, p[TCP].chksum, p[IP].len)         # None None None
ham = bytes(p)                                         # burada hesaplanır
print(p[IP].chksum)                                   # None — NESNE değişmedi
print(IP(ham)[IP].chksum, IP(ham)[IP].len)            # 0x66c2 40 — baytlarda var
```

İki ayrıntı her gün karşına çıkar:

- **`bytes(p)` nesneyi değiştirmez.** Sağlama ve uzunluk yalnız üretilen baytların içine yazılır; `p`'nin alanları `None` kalır. Hesaplanmış değeri görmek için baytları geri çözümlersin (`IP(bytes(p))`).
- **Bir alanı elle verirsen otomatik hesap kapanır.** `IP(chksum=0x1234)` yazarsan Scapy onu olduğu gibi bırakır, yeniden hesaplamaz — bilerek **bozuk** bir paket üretmenin yolu budur.

```python
from scapy.all import IP, TCP
p = IP(src="10.0.0.5", dst="10.0.0.9", chksum=0x1234) / TCP(sport=1, dport=2)
b = bytes(p)
print(hex(b[10] * 256 + b[11]))                       # 0x1234 — korundu, hesaplanmadı
```

`proto` da kuruluşta yükten türer: `IP()/TCP()` serileştirilince `proto` 6, `IP()/UDP()` için 17 olur. Elle `IP(proto=...)` verirsen o değer korunur.
:::

::: anlat Kaydı yazmak ve sağlamayı doğrulamak
`wrpcap(yol, paketler)` bir paket listesini PCAP dosyasına yazar. Zaman damgasını `p.time` ile sen verirsin; vermezsen yazıldığı an konur ve dosya her çalıştırmada değişir, bu yüzden testlerde hep elle ver.

```python
from scapy.all import Ether, IP, TCP, wrpcap, rdpcap
M = dict(src="02:00:00:00:00:01", dst="02:00:00:00:00:02")
paketler = []
for i, dport in enumerate((80, 443)):
    p = Ether(**M) / IP(src="10.0.0.5", dst="10.0.0.9") / TCP(sport=40000 + i, dport=dport, flags="S")
    p.time = 1792400000 + i
    paketler.append(p)
wrpcap("uretilen.pcap", paketler)
for p in rdpcap("uretilen.pcap"):
    print(p[TCP].dport, p[IP].len, hex(p[IP].chksum))   # geri okununca hesaplanmış alanlar var
```

Ürettiğin paketin sağlaması doğru mu? İki tanık var ve ikisi de tuzaklı.

**Scapy ile yeniden hesaplamak** kesin yoldur: sağlamayı sil, baytları yeniden kur, saklanan değerle karşılaştır.

```python
from scapy.all import IP, TCP
ham = bytes(IP(src="10.0.0.5", dst="10.0.0.9") / TCP(sport=1, dport=80))
p = IP(ham)                                            # geri çözülmüş: sağlama dolu
saklanan = p[IP].chksum
q = p.copy(); del q[IP].chksum                         # sil → yeniden hesaplanır
yeniden = IP(bytes(q[IP]))[IP].chksum
print(saklanan == yeniden)                             # True: sağlama tutuyor
```

**TShark varsayılanda sağlamayı doğrulamaz.** Canlı kayıtlarda ağ kartı sağlamayı kendisi hesapladığı için ("checksum offload") kayıttaki değer çoğu zaman yanlıştır; TShark bu yüzden sağlamayı **doğrulamadan** geçer. Bu derste ölçüldü: `ip.checksum.status` varsayılanda hem doğru hem bozuk pakette **2** (doğrulanmadı) gelir. Doğrulamayı açman gerekir:

| TShark çağrısı | Doğru paket | Bozuk paket |
|---|---|---|
| varsayılan | `ip.checksum.status` = 2 | 2 (ikisi de "doğrulanmadı") |
| `-o ip.check_checksum:TRUE` | 1 (Good) | 0 (Bad) |

> [!TUZAK] "Yeşil tik" sağlamanın doğru olduğunu söylemez
> Bir kayıtta bütün sağlamalar "doğrulanmadı" görünüyorsa paketler bozuk demek değildir; büyük olasılıkla kartın offload'u yüzünden doğrulama kapalıdır. Tersi de olur: sen bilerek bozuk sağlamayla paket üretirsen, doğrulama açık olmayan bir TShark bunu fark etmez. Ürettiğin paketi doğrularken sağlamayı ya Scapy'de yeniden hesapla ya da TShark'ta doğrulamayı açıkça aç.
:::

::: tahmin Hesaplanan alan ne zaman dolu?
```python
from scapy.all import IP, TCP, bytes_encode
p = IP(src="10.0.0.1", dst="10.0.0.2") / TCP(dport=80, flags="S")
a = (p[IP].len, p[IP].chksum)
ham = bytes(p)
b = (p[IP].len, p[IP].chksum)
c = (IP(ham)[IP].len, IP(ham)[IP].proto)
print(a)
print(b)
print(c)
```

???

```text
(None, None)
(None, None)
(40, 6)
```

Kuruluşta `len` ve `chksum` boştur: ikisi de serileştirmede hesaplanır. `bytes(p)` baytları üretir ama **nesneyi değiştirmez**, bu yüzden `b` yine `(None, None)`. Değerleri ancak baytları geri çözümleyince görürsün: `len` 40 (20 IP + 20 TCP, yük yok), `proto` 6 — çünkü `proto` da kuruluşta yükten (TCP) türedi. Bir paketi kurduktan sonra "alanları neden None?" diye şaşırma: üretilmiş baytlara bak, nesneye değil.
:::

::: gorev Belirtime göre paket üret
`uret(yol, satirlar)` yaz. Her `satir` bir `(src, dst, sport, dport, bayrak)` demetidir; her biri için `Ether / IP / TCP` paketi kur (MAC adresleri `02:00:00:00:00:01` → `02:00:00:00:00:02`, bayrak `TCP(flags=...)`'a verilir), `p.time`'ı `1792400000`'dan başlayıp birer saniye artır, hepsini `yol`'a `wrpcap` ile yaz. Dönüş: her paket için geri okunan `(dport, ip_len, bayrak_str)` listesi; `bayrak_str` `str(p[TCP].flags)` (ör. `"S"`, `"PA"`).

- `satirlar` boşsa yalnız dosya başlığı olan bir kayıt yaz ve `[]` döndür.
- Sağlamaları elle verme; Scapy hesaplasın.

```setup
from scapy.all import rdpcap
```

```starter
from scapy.all import Ether, IP, TCP, wrpcap

def uret(yol, satirlar):
    M = dict(src="02:00:00:00:00:01", dst="02:00:00:00:00:02")
    paketler = []
    for src, dst, sport, dport, bayrak in satirlar:
        p = Ether(**M) / IP(src=src, dst=dst) / TCP(sport=sport, dport=dport, flags=bayrak)
        paketler.append(p)
    wrpcap(yol, paketler)
    return [(p[TCP].dport, p[IP].len, str(p[TCP].flags)) for p in rdpcap(yol)]
```

```test
import subprocess
from scapy.all import rdpcap, IP, TCP
f = need("uret")
SATIR = [("10.0.0.5", "10.0.0.9", 51544, 80, "S"), ("10.0.0.5", "10.0.0.9", 51545, 443, "PA")]
eq(f("u.pcap", SATIR), [(80, 40, "S"), (443, 40, "PA")], "iki paket: dport, hesaplanan ip.len (40), bayrak metni")
paketler = rdpcap("u.pcap")
eq([float(p.time) for p in paketler], [1792400000.0, 1792400001.0], "zaman damgaları birer saniye artar")
ok(all(p[IP].chksum is not None for p in paketler), "geri okununca sağlama hesaplanmış")
# Scapy ile yeniden hesap: üretilen sağlamalar doğru olmalı
for p in paketler:
    q = p.copy(); del q[IP].chksum
    eq(p[IP].chksum, IP(bytes(q[IP]))[IP].chksum, "üretilen IP sağlaması geçerli")
# TShark: doğrulama açıkken hepsi iyi (1)
t = subprocess.run(["tshark", "-r", "u.pcap", "-o", "ip.check_checksum:TRUE", "-o", "tcp.check_checksum:TRUE",
                    "-T", "fields", "-e", "tcp.dstport", "-e", "ip.checksum.status", "-e", "tcp.checksum.status"],
                   capture_output=True, text=True)
eq(t.stdout.split(), ["80", "1", "1", "443", "1", "1"], "TShark doğrulama açıkken port doğru ve sağlamalar iyi (1)")
# varsayılanda doğrulanmaz (2)
t2 = subprocess.run(["tshark", "-r", "u.pcap", "-T", "fields", "-e", "ip.checksum.status"], capture_output=True, text=True)
eq(t2.stdout.split(), ["2", "2"], "varsayılan TShark sağlamayı doğrulamaz: status 2")
eq(f("bos.pcap", []), [], "boş belirtim: yalnız dosya başlığı")
eq(len(rdpcap("bos.pcap")), 0, "boş kayıt okunur")
```

```solution
from scapy.all import Ether, IP, TCP, wrpcap, rdpcap

def uret(yol, satirlar):
    M = dict(src="02:00:00:00:00:01", dst="02:00:00:00:00:02")
    paketler = []
    for i, (src, dst, sport, dport, bayrak) in enumerate(satirlar):
        p = Ether(**M) / IP(src=src, dst=dst) / TCP(sport=sport, dport=dport, flags=bayrak)
        p.time = 1792400000 + i
        paketler.append(p)
    wrpcap(yol, paketler)
    return [(p[TCP].dport, p[IP].len, str(p[TCP].flags)) for p in rdpcap(yol)]
```

```hint
Zaman damgası için `enumerate(satirlar)` ile `p.time = 1792400000 + i`. Sağlama/uzunluk kuruluşta None'dur; `wrpcap` yazarken hesaplar, `rdpcap` ile geri okuyunca dolu gelir — dönüşü geri okunan paketlerden üret.
```

```hint
`str(p[TCP].flags)` bayrağı `"S"`, `"PA"` gibi harflerle verir; `int(...)` sayı ister. Hiç satır yoksa `wrpcap(yol, [])` yalnız dosya başlığını yazar.
```
:::

::: gorev Bozuk sağlamayı bul
`bozuk_saglama(yol)` yaz: bir PCAP'teki paketlerden **IP sağlaması yanlış** olanların numaralarını (1'den, artan) döndür. Saklanan sağlamayı Scapy'de yeniden hesaplayıp karşılaştır; TShark'ın varsayılan "doğrulanmadı" durumuna güvenme. IP katmanı olmayan paketleri atla (numara saymaya devam et). Dosya yoksa `FileNotFoundError`, PCAP değilse `ValueError`.

Hazırlık `s.pcap`'i üretir: iki doğru paket, IP sağlaması elle bozulmuş bir paket, bir ARP (IP yok) ve TCP sağlaması bozuk ama IP'si doğru bir paket (bu sonuncusu listeye **girmez**, yalnız IP sağlamasına bakılır).

```setup
from scapy.all import Ether, IP, TCP, ARP, wrpcap
M = dict(src="02:00:00:00:00:01", dst="02:00:00:00:00:02")
def tcp(sport, **ip):
    return Ether(**M) / IP(src="10.0.0.5", dst="10.0.0.9", **ip) / TCP(sport=sport, dport=80, flags="S")
p1 = tcp(1)
p2 = tcp(2)
p3 = tcp(3, chksum=0x1111)
p4 = Ether(**M) / ARP(psrc="10.0.0.1", pdst="10.0.0.5", hwsrc=M["src"])
p5 = Ether(**M) / IP(src="10.0.0.5", dst="10.0.0.9") / TCP(sport=5, dport=80, flags="S", chksum=0x2222)
for i, p in enumerate((p1, p2, p3, p4, p5)):
    p.time = 1792400000 + i
wrpcap("s.pcap", [p1, p2, p3, p4, p5])
```

```starter
from scapy.all import rdpcap, IP

def bozuk_saglama(yol):
    kotu = []
    for no, p in enumerate(rdpcap(yol), 1):
        if p.haslayer(IP) and p[IP].chksum != 0:
            kotu.append(no)
    return kotu
```

```test
import subprocess
from scapy.all import Ether, IP, TCP, wrpcap
f = need("bozuk_saglama")
eq(f("s.pcap"), [3], "yalnız 3. paketin IP sağlaması yanlış; ARP atlanır, bozuk TCP sağlaması IP'yi etkilemez")
# TShark doğrulama açıkken aynı sonucu vermeli (ip.checksum.status == 0 olanlar)
t = subprocess.run(["tshark", "-r", "s.pcap", "-o", "ip.check_checksum:TRUE", "-T", "fields",
                    "-e", "frame.number", "-e", "ip.checksum.status"], capture_output=True, text=True)
kotu_tshark = [int(r.split("\t")[0]) for r in t.stdout.splitlines() if r.split("\t")[1:] == ["0"]]
eq(kotu_tshark, [3], "TShark da (doğrulama açıkken) yalnız 3'ü bozuk sayar")
M = dict(src="02:00:00:00:00:01", dst="02:00:00:00:00:02")
temiz = [Ether(**M) / IP(src="10.0.0.1", dst="10.0.0.2") / TCP(sport=i, dport=80) for i in (1, 2)]
for i, p in enumerate(temiz):
    p.time = 1792400100 + i
wrpcap("temiz.pcap", temiz)
eq(f("temiz.pcap"), [], "hepsi doğru")
wrpcap("bos.pcap", [])
eq(f("bos.pcap"), [], "boş kayıt")
open("metin.pcap", "w").write("pcap değil")
raises(ValueError, f, "metin.pcap", msg="PCAP olmayan dosya")
raises(FileNotFoundError, f, "yok.pcap", msg="olmayan dosya")
```

```solution
from scapy.all import rdpcap, IP
from scapy.error import Scapy_Exception

def bozuk_saglama(yol):
    try:
        paketler = rdpcap(yol)
    except Scapy_Exception as e:
        raise ValueError(f"PCAP değil: {e}")
    kotu = []
    for no, p in enumerate(paketler, 1):
        if not p.haslayer(IP):
            continue
        saklanan = p[IP].chksum
        q = p.copy(); del q[IP].chksum
        if saklanan != IP(bytes(q[IP]))[IP].chksum:
            kotu.append(no)
    return kotu
```

```hint
Saklanan sağlama `p[IP].chksum`. Doğrusu için kopyala, sil, yeniden kur: `q = p.copy(); del q[IP].chksum; dogru = IP(bytes(q[IP]))[IP].chksum`. İkisi farklıysa paket bozuktur.
```

```hint
`q[IP]` yerine bütün `q`'yu yeniden kurma: Ethernet başlığıyla birlikte baytlayıp IP'yi tekrar bulman gerekir. `bytes(q[IP])` yalnız IP katmanından aşağısını baytlar, `IP(...)` ile geri çözümlersin. ARP gibi IP'siz paketleri `haslayer(IP)` ile ele.
```
:::
