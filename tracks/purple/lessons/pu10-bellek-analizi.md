---
id: pu10
title: Bellek Analizi · Süreç, Ağ ve Enjeksiyon İzleri
summary: Volatility 3 ve MemProcFS dışa aktarımlarındaki farklı alan adlarını normalize etmek; iki kaynaktaki yinelenen kayıtları kaynak kökeniyle birleştirmek; PID yeniden kullanımını süreç ve bağlantı zamanıyla ayırmak; RWX, özel ve dosyasız bellek bölgelerini süreç ve ağ kanıtıyla ilişkilendirmek; sahipsiz PID'yi kaybetmeden yanlış süreç adı uydurmamak. Python ve küçük sentetik CSV/JSON fixture'ları; gerçek araçlar yalnız açık onaylı, yerel imajlı opt-in bağdaştırıcıyla.
---

::: anlat İmaj değil, kanıt tabloları
Bellek incelemesinde **Volatility 3** ve **MemProcFS**, aynı imajın farklı görünümlerini verebilir. Bu derste imajın kendisi yoktur; iki aracın çıktılarına benzeyen, elle yazılmış küçük CSV/JSON dosyaları vardır. Amaç üç tabloyu güvenli biçimde birleştirmektir:

| Kanıt | Volatility 3 örneği | MemProcFS örneği | Ortak soru |
|---|---|---|---|
| Süreç | `windows.pslist.PsList` | `process_list()` | Hangi PID, hangi süreç, ne zaman? |
| Ağ | `windows.netscan.NetScan` | `vmm.maps.net()` | Bağlantı hangi sürece ait? |
| Bellek bölgesi | `windows.malfind.Malfind` | `process.maps.vad()` | Olağan dışı yürütülebilir/yazılabilir bölge var mı? |

Alan adları aynı değildir: `PID`/`pid`, `ImageFileName`/`name`, `ForeignAddr`/`dst-ip`, `Start VPN`/`start`. Zamanlar da `+00:00`, `Z` ya da `UTC` ile yazılabilir. Önce bunları tek sözlük biçimine çeviririz. Aynı kanıt iki araçta görülürse iki olay saymayız; `kaynaklar` alanında iki aracın adını da saklarız.

> [!TUZAK] PID tek başına kimlik değildir
> Bir süreç kapandıktan sonra PID'si yeniden kullanılabilir. Bağlantının zamanı, aday sürecin başlangıç ve varsa bitiş zamanıyla uyumlu olmalıdır. Süreç bulunamazsa `surec: None` yaz; kanıtı silme veya başka bir sürece bağlama. Gerçek çıktıda zaman yoksa bu, kesin eşleşme değil, sınırlılık olarak raporlanmalıdır.

> [!GÜVENLİK] Aday, hüküm değildir
> **RWX + özel + dosyasız** bir bölge inceleme önceliğidir; JIT derleyicileri ve başka meşru yazılımlar da böyle bölgeler oluşturabilir. Dış bağlantı da tek başına zararlı kanıtı değildir. Bu dersin çıktısı `nedenler` içeren bir öncelik listesidir; “kesin enjeksiyon” ya da “zararlı” etiketi değildir.

Gerçek araçlar varsayılan olarak **kapalıdır**. `sandbox/memory_lab.py` yalnız açık onay ve kullanıcının sağladığı yerel imajla çalışır. Volatility 3 için `vol.py`, MemProcFS için önceden kurulmuş `memprocfs` Python modülü gerekir; ders paket kurmaz, imaj indirmez, canlı sisteme bağlanmaz veya bellek baytlarını dökmez. Araç/imaj yoksa sonuç açıkça `atlandi`, gerçek yol kapalıysa `gereksinim-yok` olur; ikisi de başarılı analiz demek değildir.

```python norun
# Örnek gerçek kullanım; bu paftada otomatik çalıştırılmaz.
python sandbox/memory_lab.py volatility --onay --ikili /yol/vol.py --imaj /yol/imaj.raw --cikti /yol/export
python sandbox/memory_lab.py memprocfs --onay --imaj /yol/imaj.raw --cikti /yol/export
```
:::

::: tahmin
Aşağıdaki üç korumadan hangileri bu dersin ilk bellek süzgecinden geçer? Bölgelerin üçü de özel ve dosyasız olsun.

```python
korumalar = ["PAGE_EXECUTE_READWRITE", "rwx", "r-x"]
for k in korumalar:
    aday = k == "PAGE_EXECUTE_READWRITE" or k == "rwx"
    print(k, aday)
```

???

**İlk ikisi geçer; `r-x` geçmez.**

```
PAGE_EXECUTE_READWRITE True
rwx True
r-x False
```

İki araç aynı anlamı farklı yazabilir. Ancak bu yalnız koruma süzgecidir: özel olmayan ya da dosya destekli bölge daha sonra elenir; kalan bölge de otomatik olarak zararlı sayılmaz.
:::

::: gorev 1 · Süreçleri normalize et ve kökeni koru
`surecler()` fonksiyonunu yaz. `bellek/volatility_pslist.csv` ve `bellek/memprocfs_processes.json` dosyalarını okuyup her benzersiz süreç için şu sözlüğü döndür:

```text
{"pid": int, "ppid": int, "ad": küçük harf, "baslangic": "YYYY-AA-GG SS:DD:ss",
 "bitis": aynı biçim veya "", "kaynaklar": ["memprocfs", "volatility"] alt kümesi}
```

- CSV satırına `volatility`, JSON satırına `memprocfs` kökenini ver.
- Aynı kimlik iki araçta varsa tek satır üret ve iki kökeni birleştir.
- Aynı PID'nin farklı zamandaki süreçlerini birleştirme.
- `(pid, baslangic, ad)` ile artan sırala. Boş bitiş `""` kalsın; `***` ve `N/A` boş sayılır.

Hazırlık, `oku`, `alan`, `sayi`, `metin` ve `zaman` yardımcılarını verir.

```starter
from memory_lab import satirlari_oku as oku, alan, sayi, metin, zaman, evet


def surecler():
    rows = oku("bellek/volatility_pslist.csv")
    return [{"pid": sayi(r["PID"]), "ad": r["ImageFileName"]} for r in rows]
```

```test
need("surecler")
ps = surecler()
eq(len(ps), 5, "dört ortak kayıt tekil; eski PID örneği ayrı: beş süreç")
eq([(p["pid"], p["ad"]) for p in ps], [(4, "system"), (512, "services.exe"), (900, "svchost.exe"),
                                      (4242, "eski.exe"), (4242, "rundll32.exe")], "PID yeniden kullanımı birleştirilmedi")
yeni = next(p for p in ps if p["ad"] == "rundll32.exe")
eq(yeni, {"pid": 4242, "ppid": 900, "ad": "rundll32.exe", "baslangic": "2026-10-19 09:02:00",
          "bitis": "", "kaynaklar": ["memprocfs", "volatility"]}, "alan adları, UTC yazımı ve iki köken")
eski = next(p for p in ps if p["ad"] == "eski.exe")
eq((eski["baslangic"], eski["bitis"], eski["kaynaklar"]),
   ("2026-10-19 07:00:00", "2026-10-19 07:30:00", ["volatility"]), "bitiş zamanı korunur")
ok(all(isinstance(p["pid"], int) and isinstance(p["ppid"], int) for p in ps), "PID ve PPID sayı")
```

```solution
from memory_lab import satirlari_oku as oku, alan, sayi, metin, zaman, evet


def surecler():
    kaynakli = [("volatility", "bellek/volatility_pslist.csv"),
                ("memprocfs", "bellek/memprocfs_processes.json")]
    birlesik = {}
    for kaynak, yol in kaynakli:
        for r in oku(yol):
            p = {"pid": sayi(alan(r, "PID", "pid")),
                 "ppid": sayi(alan(r, "PPID", "ppid", varsayilan="0")),
                 "ad": alan(r, "ImageFileName", "name").lower(),
                 "baslangic": zaman(alan(r, "CreateTime", "time-create-str")),
                 "bitis": zaman(alan(r, "ExitTime", "time-exit-str"))}
            anahtar = (p["pid"], p["ppid"], p["ad"], p["baslangic"], p["bitis"])
            if anahtar not in birlesik:
                birlesik[anahtar] = dict(p, kaynaklar=set())
            birlesik[anahtar]["kaynaklar"].add(kaynak)
    sonuc = []
    for p in birlesik.values():
        p["kaynaklar"] = sorted(p["kaynaklar"])
        sonuc.append(p)
    return sorted(sonuc, key=lambda p: (p["pid"], p["baslangic"], p["ad"]))


for p in surecler():
    print(p)
```

```hint
Önce her satırı ortak sözlüğe çevir, sonra `(pid, ppid, ad, baslangic, bitis)` anahtarlı bir sözlükte topla. Kökenleri küme olarak tutup dönüşte `sorted` ile listeye çevir.
```

```setup
import os, runpy, sys
_s = os.path.dirname(next(m.__file__ for m in list(sys.modules.values())
                          if getattr(m, "__file__", None) and os.path.basename(m.__file__) == "py_harness.py"))
sys.path.insert(0, _s)
import memory_lab as ml
ml.hazirla("bellek")
```
:::

::: gorev 2 · Bağlantıyı doğru süreç örneğine bağla
Görev 1'deki `surecler()` fonksiyonunu da kopyala. `baglantilar(ps)` fonksiyonu iki ağ dosyasını okusun; yinelenen kayıtları tekleştirip şu alanları döndürsün:

```text
{"pid": int, "protokol": str, "yerel_ip": str, "yerel_port": int,
 "uzak_ip": str, "uzak_port": int, "durum": büyük harf, "zaman": UTC metni,
 "surec": süreç adı veya None, "eslesme": "pid+zaman" veya "yok",
 "kaynaklar": sıralı köken listesi}
```

Bir süreç ancak `baslangic <= bağlantı zamanı` ve bitiş boş ya da `bağlantı zamanı <= bitis` ise adaydır. Tam bir aday varsa onu kullan; sıfır ya da birden çok adayda `surec=None`, `eslesme="yok"` yap. `(zaman, pid, uzak_port)` ile sırala.

```starter
from memory_lab import satirlari_oku as oku, alan, sayi, metin, zaman, evet


def baglantilar(ps):
    sonuc = []
    for r in oku("bellek/volatility_netscan.csv"):
        pid = sayi(r["PID"])
        ad = next((p["ad"] for p in ps if p["pid"] == pid), "bilinmiyor")
        sonuc.append({"pid": pid, "surec": ad, "uzak_ip": r["ForeignAddr"]})
    return sonuc
```

```test
need("baglantilar"); need("surecler")
ps = surecler(); cs = baglantilar(ps)
eq(len(cs), 4, "iki araçtaki iki yinelenen bağlantı tekil; eski ve sahipsiz kayıtlar korunur")
aktif = next(c for c in cs if c["pid"] == 4242 and c["zaman"] == "2026-10-19 09:04:00")
eq((aktif["surec"], aktif["eslesme"], aktif["kaynaklar"]),
   ("rundll32.exe", "pid+zaman", ["memprocfs", "volatility"]), "yeni süreç ve iki köken")
eq((aktif["protokol"], aktif["yerel_ip"], aktif["yerel_port"], aktif["uzak_ip"], aktif["uzak_port"], aktif["durum"]),
   ("TCPv4", "10.20.0.15", 51510, "198.51.100.24", 8443, "ESTABLISHED"), "uçlar ve sayısal portlar")
eski = next(c for c in cs if c["zaman"] == "2026-10-19 07:15:00")
eq((eski["surec"], eski["eslesme"]), ("eski.exe", "pid+zaman"), "07:15, 09:02'de başlayan rundll32'ye bağlanmaz")
sahipsiz = next(c for c in cs if c["pid"] == 9999)
ok(sahipsiz["surec"] is None and sahipsiz["eslesme"] == "yok", "sahipsiz PID'ye isim uydurma")
eq([c["zaman"] for c in cs], sorted(c["zaman"] for c in cs), "artan zaman")
```

```solution
from memory_lab import satirlari_oku as oku, alan, sayi, metin, zaman, evet


def surecler():
    kaynakli = [("volatility", "bellek/volatility_pslist.csv"),
                ("memprocfs", "bellek/memprocfs_processes.json")]
    birlesik = {}
    for kaynak, yol in kaynakli:
        for r in oku(yol):
            p = {"pid": sayi(alan(r, "PID", "pid")),
                 "ppid": sayi(alan(r, "PPID", "ppid", varsayilan="0")),
                 "ad": alan(r, "ImageFileName", "name").lower(),
                 "baslangic": zaman(alan(r, "CreateTime", "time-create-str")),
                 "bitis": zaman(alan(r, "ExitTime", "time-exit-str"))}
            anahtar = (p["pid"], p["ppid"], p["ad"], p["baslangic"], p["bitis"])
            if anahtar not in birlesik:
                birlesik[anahtar] = dict(p, kaynaklar=set())
            birlesik[anahtar]["kaynaklar"].add(kaynak)
    sonuc = []
    for p in birlesik.values():
        p["kaynaklar"] = sorted(p["kaynaklar"])
        sonuc.append(p)
    return sorted(sonuc, key=lambda p: (p["pid"], p["baslangic"], p["ad"]))


def baglantilar(ps):
    kaynakli = [("volatility", "bellek/volatility_netscan.csv"),
                ("memprocfs", "bellek/memprocfs_net.json")]
    birlesik = {}
    for kaynak, yol in kaynakli:
        for r in oku(yol):
            c = {"pid": sayi(alan(r, "PID", "pid")),
                 "protokol": alan(r, "Proto", "protocol", varsayilan="TCPv" + str(alan(r, "ver", varsayilan=""))),
                 "yerel_ip": alan(r, "LocalAddr", "src-ip"),
                 "yerel_port": sayi(alan(r, "LocalPort", "src-port")),
                 "uzak_ip": alan(r, "ForeignAddr", "dst-ip"),
                 "uzak_port": sayi(alan(r, "ForeignPort", "dst-port")),
                 "durum": alan(r, "State", "state-str").upper(),
                 "zaman": zaman(alan(r, "Created", "time-str"))}
            anahtar = tuple(c.items())
            if anahtar not in birlesik:
                birlesik[anahtar] = dict(c, kaynaklar=set())
            birlesik[anahtar]["kaynaklar"].add(kaynak)
    sonuc = []
    for c in birlesik.values():
        aday = [p for p in ps if p["pid"] == c["pid"] and p["baslangic"] <= c["zaman"]
                and (not p["bitis"] or c["zaman"] <= p["bitis"])]
        c["surec"] = aday[0]["ad"] if len(aday) == 1 else None
        c["eslesme"] = "pid+zaman" if len(aday) == 1 else "yok"
        c["kaynaklar"] = sorted(c["kaynaklar"])
        sonuc.append(c)
    return sorted(sonuc, key=lambda c: (c["zaman"], c["pid"], c["uzak_port"]))


for c in baglantilar(surecler()):
    print(c)
```

```hint
Ağ kayıtlarını da tüm normalize alanlardan oluşan bir anahtarla birleştir. Süreç adını `next(...)` ile ilk PID eşleşmesinden alma; zaman koşulunu sağlayan adayların listesini çıkar ve yalnız `len(aday) == 1` ise ad ver.
```

```setup
import os, runpy, sys
_s = os.path.dirname(next(m.__file__ for m in list(sys.modules.values())
                          if getattr(m, "__file__", None) and os.path.basename(m.__file__) == "py_harness.py"))
sys.path.insert(0, _s)
import memory_lab as ml
ml.hazirla("bellek")
```
:::

::: gorev 3 · Bellek ve ağ gerekçelerini birleştir
Önceki iki görevin fonksiyonlarını kopyala. `bulgular(ps, cs)` iki bellek dosyasını normalize etsin ve yalnız **RWX + özel + dosyasız** bölgeleri döndürsün:

```text
{"pid": int, "adres": int, "zaman": UTC metni, "surec": ad veya None,
 "kaynaklar": sıralı köken listesi, "nedenler": [...]}
```

Her adayda `rwx-ozel-dosyasiz` gerekçesi bulunur. Aynı süreç örneğine zaman uyumlu bağlanmış, bölge zamanından önceki ve `ESTABLISHED` bir bağlantının uzak ucu gerçek bir uç ise (`0.0.0.0`, `::`, boş veya port 0 değil) `dis-ag-baglantisi` gerekçesini ekle. PID'si süreçte olmayan bölgeyi de `surec=None` ile koru. `(pid, adres)` ile sırala.

```starter
from memory_lab import satirlari_oku as oku, alan, sayi, metin, zaman, evet


def bulgular(ps, cs):
    sonuc = []
    for r in oku("bellek/volatility_malfind.csv"):
        if "READWRITE" in r["Protection"]:
            sonuc.append({"pid": sayi(r["PID"]), "adres": sayi(r["Start VPN"]),
                          "surec": next(p["ad"] for p in ps if p["pid"] == sayi(r["PID"])),
                          "nedenler": ["zararli"]})
    return sonuc
```

```test
need("bulgular"); need("surecler"); need("baglantilar")
ps = surecler(); cs = baglantilar(ps); bs = bulgular(ps, cs)
eq([(b["pid"], b["adres"]) for b in bs], [(900, 0x600000), (4242, 0x500000), (9999, 0x900000)],
   "RWX+özel+dosyasız üç aday; r-x, paylaşılan ve dosya destekli bölgeler yok")
ana = next(b for b in bs if b["pid"] == 4242)
eq((ana["surec"], ana["nedenler"], ana["kaynaklar"]),
   ("rundll32.exe", ["rwx-ozel-dosyasiz", "dis-ag-baglantisi"], ["memprocfs", "volatility"]),
   "iki bellek kaynağı ve zaman uyumlu dış bağlantı")
benign = next(b for b in bs if b["pid"] == 900)
eq((benign["surec"], benign["nedenler"]), ("svchost.exe", ["rwx-ozel-dosyasiz"]),
   "yanlış-pozitif kontrolü: RWX aday kalır ama dinleyen soket dış bağlantı gerekçesi değildir")
sahipsiz = next(b for b in bs if b["pid"] == 9999)
ok(sahipsiz["surec"] is None and sahipsiz["nedenler"] == ["rwx-ozel-dosyasiz"],
   "yanlış-negatif kontrolü: sahipsiz bellek kanıtı kaybolmaz, isim/ağ uydurulmaz")
ok(all("zararli" not in b["nedenler"] for b in bs), "bulgu gerekçedir, zararlı hükmü değil")
```

```solution
from memory_lab import satirlari_oku as oku, alan, sayi, metin, zaman, evet


def surecler():
    kaynakli = [("volatility", "bellek/volatility_pslist.csv"),
                ("memprocfs", "bellek/memprocfs_processes.json")]
    birlesik = {}
    for kaynak, yol in kaynakli:
        for r in oku(yol):
            p = {"pid": sayi(alan(r, "PID", "pid")),
                 "ppid": sayi(alan(r, "PPID", "ppid", varsayilan="0")),
                 "ad": alan(r, "ImageFileName", "name").lower(),
                 "baslangic": zaman(alan(r, "CreateTime", "time-create-str")),
                 "bitis": zaman(alan(r, "ExitTime", "time-exit-str"))}
            anahtar = (p["pid"], p["ppid"], p["ad"], p["baslangic"], p["bitis"])
            if anahtar not in birlesik:
                birlesik[anahtar] = dict(p, kaynaklar=set())
            birlesik[anahtar]["kaynaklar"].add(kaynak)
    sonuc = []
    for p in birlesik.values():
        p["kaynaklar"] = sorted(p["kaynaklar"])
        sonuc.append(p)
    return sorted(sonuc, key=lambda p: (p["pid"], p["baslangic"], p["ad"]))


def baglantilar(ps):
    kaynakli = [("volatility", "bellek/volatility_netscan.csv"),
                ("memprocfs", "bellek/memprocfs_net.json")]
    birlesik = {}
    for kaynak, yol in kaynakli:
        for r in oku(yol):
            c = {"pid": sayi(alan(r, "PID", "pid")),
                 "protokol": alan(r, "Proto", "protocol", varsayilan="TCPv" + str(alan(r, "ver", varsayilan=""))),
                 "yerel_ip": alan(r, "LocalAddr", "src-ip"),
                 "yerel_port": sayi(alan(r, "LocalPort", "src-port")),
                 "uzak_ip": alan(r, "ForeignAddr", "dst-ip"),
                 "uzak_port": sayi(alan(r, "ForeignPort", "dst-port")),
                 "durum": alan(r, "State", "state-str").upper(),
                 "zaman": zaman(alan(r, "Created", "time-str"))}
            anahtar = tuple(c.items())
            if anahtar not in birlesik:
                birlesik[anahtar] = dict(c, kaynaklar=set())
            birlesik[anahtar]["kaynaklar"].add(kaynak)
    sonuc = []
    for c in birlesik.values():
        aday = [p for p in ps if p["pid"] == c["pid"] and p["baslangic"] <= c["zaman"]
                and (not p["bitis"] or c["zaman"] <= p["bitis"])]
        c["surec"] = aday[0]["ad"] if len(aday) == 1 else None
        c["eslesme"] = "pid+zaman" if len(aday) == 1 else "yok"
        c["kaynaklar"] = sorted(c["kaynaklar"])
        sonuc.append(c)
    return sorted(sonuc, key=lambda c: (c["zaman"], c["pid"], c["uzak_port"]))


def bulgular(ps, cs):
    kaynakli = [("volatility", "bellek/volatility_malfind.csv"),
                ("memprocfs", "bellek/memprocfs_vads.json")]
    birlesik = {}
    for kaynak, yol in kaynakli:
        for r in oku(yol):
            koruma = alan(r, "Protection", "protection").upper()
            rwx = koruma == "PAGE_EXECUTE_READWRITE" or set(koruma) <= set("RWX-") and all(x in koruma for x in "RWX")
            ozel = evet(alan(r, "PrivateMemory", "private", varsayilan="False"))
            dosya = alan(r, "File", "file")
            if not (rwx and ozel and not dosya):
                continue
            b = {"pid": sayi(alan(r, "PID", "pid")),
                 "adres": sayi(alan(r, "Start VPN", "start")),
                 "zaman": zaman(alan(r, "Created", "time-str")),
                 "koruma": koruma, "etiket": alan(r, "Tag", "tag")}
            anahtar = (b["pid"], b["adres"], b["zaman"])
            if anahtar not in birlesik:
                birlesik[anahtar] = dict(b, kaynaklar=set())
            birlesik[anahtar]["kaynaklar"].add(kaynak)
    sonuc = []
    for b in birlesik.values():
        aday = [p for p in ps if p["pid"] == b["pid"] and p["baslangic"] <= b["zaman"]
                and (not p["bitis"] or b["zaman"] <= p["bitis"])]
        ad = aday[0]["ad"] if len(aday) == 1 else None
        dis_ag = any(c["pid"] == b["pid"] and c["surec"] == ad and ad is not None
                     and c["zaman"] <= b["zaman"] and c["durum"] == "ESTABLISHED"
                     and c["uzak_ip"] not in ("", "0.0.0.0", "::") and c["uzak_port"] for c in cs)
        b["surec"] = ad
        b["nedenler"] = ["rwx-ozel-dosyasiz"] + (["dis-ag-baglantisi"] if dis_ag else [])
        b["kaynaklar"] = sorted(b["kaynaklar"])
        b.pop("koruma")
        b.pop("etiket")
        sonuc.append(b)
    return sorted(sonuc, key=lambda b: (b["pid"], b["adres"]))


for b in bulgular(surecler(), baglantilar(surecler())):
    print(b)
```

```hint
Önce `PrivateMemory/private` ve `File/file` alanlarını da normalize et; yalnız korumaya bakma. Volatility'nin `PAGE_EXECUTE_READWRITE` ve MemProcFS'nin `rwx` yazımını ayrı tanı. Ağ gerekçesini `surec`, `zaman`, `durum`, uzak IP ve port birlikte uyumluyken ekle.
```

```setup
import os, runpy, sys
_s = os.path.dirname(next(m.__file__ for m in list(sys.modules.values())
                          if getattr(m, "__file__", None) and os.path.basename(m.__file__) == "py_harness.py"))
sys.path.insert(0, _s)
import memory_lab as ml
ml.hazirla("bellek")
```
:::
