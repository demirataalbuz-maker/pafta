---
id: p57
title: Araç Gibi Yazmak · argparse ve logging
summary: Komut satırı argümanları, yardım metni, alt komutlar; seviyeli loglama, biçim ve gizli veri süzgeci.
---

::: anlat argparse: komut satırı arayüzü
Gerçek bir güvenlik aracı `python tara.py hedef.txt --esik 5 --json` gibi çalışır. `sys.argv`'yi elle ayrıştırmak yerine `argparse` kullanılır; yardım metnini, tür dönüşümünü ve hata mesajlarını o üretir:

```python
import argparse

p = argparse.ArgumentParser(prog="logavci", description="Auth loglarında kaba kuvvet arar.")
p.add_argument("dosya", help="incelenecek log dosyası")                     #! konumsal, zorunlu
p.add_argument("-e", "--esik", type=int, default=5, help="alarm eşiği (varsayılan: 5)")
p.add_argument("-f", "--format", choices=["metin", "json"], default="metin")
p.add_argument("-v", "--ayrintili", action="store_true")                   #! bayrak: varsa True
p.add_argument("--hariç", nargs="*", default=[], metavar="IP")              #! 0+ değer → liste

a = p.parse_args(["auth.log", "-e", "10", "--hariç", "10.0.0.1", "10.0.0.2"])   #! test için liste ver
print(a.dosya, a.esik, a.format, a.ayrintili, a.hariç)
print(vars(a))
p.print_help()
```

`parse_args()` argümansız çağrılınca `sys.argv[1:]`'i okur. Tezgahta komut satırı olmadığı için denerken **listeyi kendin ver**: `p.parse_args(["auth.log", "-e", "10"])`. Görev testleri ise programına gerçek `sys.argv` geçirir.

| Seçenek | Anlamı |
|---|---|
| `type=int` | dönüştür; olmazsa güzel bir hata mesajıyla çık |
| `default=` | verilmezse bu değer |
| `required=True` | `--x` biçimindeki bir seçeneği zorunlu yap |
| `choices=[...]` | sadece bu değerler |
| `action="store_true"` | bayrak |
| `nargs="+"` / `"*"` / `"?"` | 1+ / 0+ / 0-1 değer |

Hatalı kullanımda argparse kullanımı yazdırıp **`SystemExit(2)`** ile çıkar. Alt komutlar için (`git commit`, `git push` gibi) `p.add_subparsers()` kullanılır.
:::

::: tahmin
Çıktı tek satır:

```python
import argparse
p = argparse.ArgumentParser()
p.add_argument("hedef")
p.add_argument("-p", "--port", type=int, default=22)
p.add_argument("-v", "--ayrintili", action="store_true")
a = p.parse_args(["web01", "-p", "8443"])
print(a.hedef, a.port + 1, a.ayrintili)
```

???

`web01 8444 False`. `type=int` metni sayıya çevirdi, bu yüzden toplama yapılabildi. `-v` verilmediği için bayrak `False`.
:::

::: anlat logging: print'in profesyonel hali
`print` hata ayıklama için iyidir ama bir araçta yetersizdir: seviye yok, zaman damgası yok, kapatılamaz, dosyaya ve ekrana aynı anda yazamaz. **`logging`** bunların hepsini yapar:

```python
import logging, sys

log = logging.getLogger("logavci")              #! isimli logger (modül başına bir tane)
log.setLevel(logging.DEBUG)
isleyici = logging.StreamHandler(sys.stdout)    #! nereye: ekran, dosya, ağ...
isleyici.setFormatter(logging.Formatter("%(levelname)-8s %(name)s: %(message)s"))
log.addHandler(isleyici)

log.debug("ayrıntı: %d satır okundu", 1200)     #! % biçimi: mesaj sadece gerekirse kurulur
log.info("tarama başladı")
log.warning("eşik aşıldı: %s", "203.0.113.9")
try:
    1 / 0
except ZeroDivisionError:
    log.exception("beklenmeyen hata")            #! ERROR + traceback otomatik
isleyici.setLevel(logging.WARNING)               #! bu işleyici artık sadece WARNING ve üstünü yazar
log.info("bu görünmez")
log.error("bu görünür")
```

Seviyeler: `DEBUG` < `INFO` < `WARNING` < `ERROR` < `CRITICAL`. Logger ve işleyicilerin her biri bir eşik süzgecidir. Küçük betiklerde `logging.basicConfig(level=logging.INFO, format="...")` tek satırda kurulum yapar.

> [!GÜVENLİK]
> Loglar saldırganların en sevdiği hazinelerden biridir, çünkü geliştiriciler oraya **parola, oturum belirteci, API anahtarı, kart numarası** yazar. İki kural: (1) gizli veriyi asla loglama ya da maskele, (2) kullanıcı girdisini loglarken satır sonlarını temizle; yoksa saldırgan sahte log satırları ekleyebilir (**log injection**, CWE-117). Log4Shell (2021) ise loglanan bir metnin kütüphane tarafından *yorumlanmasından* doğdu: log kütüphaneleri de girdiyi veri olarak görmeli.

> [!NOT]
> `log.info("kullanıcı %s", ad)` biçimini `log.info(f"kullanıcı {ad}")`'ye tercih et: seviye kapalıysa metin hiç kurulmaz ve log toplama araçları aynı şablondaki mesajları gruplayabilir.
:::

::: tahmin
İki satır:

```python
import logging, sys
log = logging.getLogger("pafta-tahmin")
h = logging.StreamHandler(sys.stdout)
h.setFormatter(logging.Formatter("%(levelname)s:%(message)s"))
log.addHandler(h)
log.setLevel(logging.WARNING)
log.info("bilgi")
log.warning("uyarı")
log.error("hata %d", 42)
```

???

`WARNING:uyarı`, sonra `ERROR:hata 42`. Logger seviyesi WARNING olduğu için INFO mesajı hiç işlenmez. `%d` yer tutucusu argümanla doldurulur.
:::

::: gorev Araç arayüzü
`ayristirici()` fonksiyonu bir log analiz aracı için `ArgumentParser` döndürsün:

- konumsal `dosya`
- `-e` / `--esik`: int, varsayılan 5
- `-f` / `--format`: `metin` ya da `json`, varsayılan `metin`
- `-s` / `--sessiz`: bayrak
- `--haric`: sıfır ya da daha fazla IP, varsayılan boş liste

```starter
import argparse

def ayristirici():
    pass
```

```test
need("ayristirici")
p = ayristirici()
a = p.parse_args(["auth.log"])
eq((a.dosya, a.esik, a.format, a.sessiz, a.haric), ("auth.log", 5, "metin", False, []), "varsayılanlar")
a = p.parse_args(["x.log", "-e", "12", "--format", "json", "-s", "--haric", "1.1.1.1", "8.8.8.8"])
eq((a.esik, a.format, a.sessiz, a.haric), (12, "json", True, ["1.1.1.1", "8.8.8.8"]), "tüm seçenekler")
raises(SystemExit, p.parse_args, ["x.log", "--format", "xml"], msg="geçersiz format → çıkış")
raises(SystemExit, p.parse_args, ["x.log", "-e", "çok"], msg="int olmayan eşik → çıkış")
raises(SystemExit, p.parse_args, [], msg="dosya eksik → çıkış")
```

```solution
import argparse

def ayristirici():
    p = argparse.ArgumentParser(prog="logavci")
    p.add_argument("dosya")
    p.add_argument("-e", "--esik", type=int, default=5)
    p.add_argument("-f", "--format", choices=["metin", "json"], default="metin")
    p.add_argument("-s", "--sessiz", action="store_true")
    p.add_argument("--haric", nargs="*", default=[])
    return p
```

```hint
Her seçenek için bir `add_argument`. Bayrak için `action="store_true"`, liste için `nargs="*"`.
```
:::

::: gorev Komut satırı hesaplayıcısı
Bir program yaz (fonksiyon değil, betik): komut satırından bir ya da daha fazla **sayı** alsın (`nargs="+"`, `type=float`) ve toplamlarını yazdırsın. `--ortalama` bayrağı verilirse toplam yerine ortalamayı yazdırsın. Sonuç `g` biçimiyle yazılsın (`f"{x:g}"`: 6.0 → `6`). Argparse'ı `if __name__ == "__main__":` içinde çalıştır.

Testler programı şu şekilde çağıracak: `kod.py 1 2 3` ve `kod.py 1 2 3 --ortalama`.

```starter
import argparse

```

```test
eq(run(argv=["1", "2", "3"]).strip(), "6", "1 2 3 → 6")
eq(run(argv=["1", "2", "3", "--ortalama"]).strip(), "2", "--ortalama → 2")
eq(run(argv=["0.5", "0.25"]).strip(), "0.75", "ondalıklı")
eq(run(argv=["--ortalama", "10", "5"]).strip(), "7.5", "bayrak önde de olabilir")
ok(calls("ArgumentParser") and calls("parse_args"), "argparse kullan")
```

```solution
import argparse

def main():
    p = argparse.ArgumentParser(description="Sayıları toplar.")
    p.add_argument("sayilar", nargs="+", type=float)
    p.add_argument("--ortalama", action="store_true")
    a = p.parse_args()
    sonuc = sum(a.sayilar) / len(a.sayilar) if a.ortalama else sum(a.sayilar)
    print(f"{sonuc:g}")

if __name__ == "__main__":
    main()
```

```hint
`p.parse_args()` argümansız çağrılınca `sys.argv[1:]`'i okur; testler oraya değer koyuyor.
```
:::

::: gorev Gizli veri süzgeci
`GizliFiltre` adında bir `logging.Filter` alt sınıfı yaz. `filter(self, kayit)` metodunda mesajdaki `parola=...`, `token=...` ve `apikey=...` değerlerini (boşluğa ya da `&`'e kadar) `***` ile değiştir; büyük-küçük harf fark etmesin. Sonra kaydın geçmesine izin ver (`True` döndür).

İpucu: argümanlı mesajlarda (`log.info("x %s", y)`) son metin `kayit.getMessage()` ile alınır; değiştirdikten sonra `kayit.msg`'ye yaz ve `kayit.args`'ı boşalt.

```starter
import logging, re

class GizliFiltre(logging.Filter):
    pass
```

```test
import logging, io
F = need("GizliFiltre", "sınıf")
tampon = io.StringIO()
log = logging.getLogger("pafta-test-gizli")
log.handlers.clear(); log.propagate = False; log.setLevel(logging.INFO)
h = logging.StreamHandler(tampon); h.setFormatter(logging.Formatter("%(message)s"))
log.addHandler(h); log.addFilter(F())
log.info("giriş: kullanici=ali parola=Gizli123! ip=10.0.0.5")
log.warning("istek /api?token=abc.def&sayfa=2")
log.info("ayar %s", "APIKEY=xyz789 mod=hizli")
log.info("normal satır")
eq(tampon.getvalue().splitlines(), [
    "giriş: kullanici=ali parola=*** ip=10.0.0.5",
    "istek /api?token=***&sayfa=2",
    "ayar APIKEY=*** mod=hizli",
    "normal satır",
], "gizli değerler maskelenmeli, diğerleri aynı kalmalı")
```

```solution
import logging, re

GIZLI = re.compile(r"(parola|token|apikey)=[^\s&]*", re.IGNORECASE)

class GizliFiltre(logging.Filter):
    def filter(self, kayit):
        kayit.msg = GIZLI.sub(lambda m: f"{m.group(1)}=***", kayit.getMessage())
        kayit.args = ()
        return True
```

```hint
Desen: `(parola|token|apikey)=[^\s&]*` ve `re.IGNORECASE`. Yerine koyarken anahtarın orijinal yazımını koru: `lambda m: f"{m.group(1)}=***"`.
```
:::
