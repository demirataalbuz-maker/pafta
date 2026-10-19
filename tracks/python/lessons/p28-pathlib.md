---
id: p28
title: Yollar · pathlib ve os
summary: Path nesneleri, / işleci, klasör gezme, glob ve dizin aşma (path traversal) savunması.
---

::: anlat Yol bir metin değil, nesnedir
Dosya yollarını metin birleştirerek kurmak (`"loglar" + "\\" + ad`) hem çirkin hem platforma bağımlıdır: Windows `\`, Linux `/` kullanır. Modern Python'un cevabı **`pathlib.Path`**'tir:

```python
from pathlib import Path

p = Path("loglar") / "2026" / "auth.log.gz"   #! / işleci yolları birleştirir
print(p)                 #! işletim sistemine uygun ayraçla yazılır
print(p.name)            #! auth.log.gz — son parça
print(p.suffix)          #! .gz — son uzantı
print(p.suffixes)        #! ['.log', '.gz']
print(p.stem)            #! auth.log — son uzantısız ad
print(p.parent)          #! loglar/2026
print(p.parts)
print(p.with_suffix(".txt"))
print(Path.cwd())        #! çalışma klasörü
```

### Dosya sistemiyle konuşmak
```python
from pathlib import Path

klasor = Path("rapor") / "ekim"
klasor.mkdir(parents=True, exist_ok=True)     #! ara klasörleri de aç, varsa sorun etme
(klasor / "ozet.txt").write_text("3 alarm\n", encoding="utf-8")
(klasor / "ham.log").write_text("x\ny\n", encoding="utf-8")
print((klasor / "ozet.txt").read_text(encoding="utf-8").strip())

for oge in sorted(klasor.iterdir()):          #! klasör içeriği
    print(oge.name, oge.is_file(), oge.stat().st_size, "bayt")

print([p.name for p in Path(".").rglob("*.log")])   #! özyinelemeli arama
print(Path("yok.txt").exists())
```

| Yöntem | İş |
|---|---|
| `exists()` / `is_file()` / `is_dir()` | var mı, dosya mı, klasör mü |
| `iterdir()` | doğrudan içerik |
| `glob("*.log")` / `rglob("*.log")` | desenle arama; r = alt klasörler dahil |
| `read_text()` / `write_text()` | tek hamlede oku/yaz |
| `stat().st_size` / `.st_mtime` | boyut / değişiklik zamanı |
| `resolve()` | mutlak, `..`'ları çözülmüş gerçek yol |
| `unlink()` / `rmdir()` | dosya / boş klasör sil |

> [!NOT]
> Eski kodlarda `os.path.join`, `os.listdir`, `os.walk` görürsün. Hâlâ çalışırlar ve `os.environ` (ortam değişkenleri) gibi şeyler için `os` gerekir. Yeni kodda yol işleri için `pathlib` tercih edilir.
:::

::: tahmin
İki satır:

```python
from pathlib import Path
p = Path("loglar") / "2026" / "auth.log.gz"
print(p.name, p.suffix, p.stem, p.parent.name)
print(p.suffixes)
```

???

`auth.log.gz .gz auth.log 2026`, sonra `['.log', '.gz']`. `stem` sadece **son** uzantıyı atar. `parent.name` bir üst klasörün adıdır.
:::

::: anlat Dizin aşma: ../../ saldırısı
Kullanıcıdan dosya adı alıp belli bir klasörden servis eden her program şu soruyla yüzleşir: kullanıcı `../../etc/passwd` gönderirse ne olur?

```python
from pathlib import Path

kok = Path("dosyalar").resolve()
kok.mkdir(exist_ok=True)
(kok / "rapor.txt").write_text("gizli olmayan rapor", encoding="utf-8")

def oku_saf(istek):
    return kok / istek                       #! KÖTÜ: hiç kontrol yok

print(oku_saf("../../etc/passwd").resolve()) #! kökün DIŞINA çıktı!

def guvenli(istek):
    hedef = (kok / istek).resolve()          #! .. ve sembolik bağları çöz
    if not hedef.is_relative_to(kok):        #! hâlâ kökün içinde mi?
        raise PermissionError(f"kök dışı erişim: {istek}")
    return hedef

print(guvenli("rapor.txt").name)
try:
    guvenli("../../etc/passwd")
except PermissionError as e:
    print("engellendi:", e)
```

Doğru savunma **önce çöz, sonra kontrol et**tir: `resolve()` tüm `..`'ları ve sembolik bağları açar, `is_relative_to` sonucun kökün altında olup olmadığını söyler. "İstekte `..` geçiyor mu?" diye metin aramak yetmez: `..%2f`, mutlak yollar (`/etc/passwd`), Windows'ta `..\\` ve sembolik bağlar o kontrolü atlatır.

> [!GÜVENLİK]
> Path traversal (CWE-22) OWASP listelerinin daimi üyesidir. Zip arşivleri de aynı açığı taşır (**Zip Slip**): arşivin içindeki `../../.bashrc` adlı bir dosya, `extractall` ile hedef klasörün dışına yazılabilir. Arşiv açarken her üyenin hedef yolunu aynı kontrolden geçir. Python 3.12+ `tarfile` bunun için `filter="data"` parametresini sunar.
:::

::: tahmin
İki satır:

```python
from pathlib import Path
kok = Path("depo").resolve()
print((kok / "../../etc/passwd").resolve().is_relative_to(kok))
print((kok / "alt/../rapor.txt").resolve().is_relative_to(kok))
```

???

`False`, sonra `True`. İlki iki seviye yukarı çıkıp kökün dışına kaçar. İkincisi `alt/..` ile tekrar köke döner ve `depo/rapor.txt` olur: hâlâ içeride. `..` içermek tek başına kötü değildir; önemli olan **çözülmüş** sonucun nerede olduğudur.
:::

::: gorev Tüm log dosyaları
Çalışma klasöründe `sistem` adında iç içe bir klasör ağacı var. İçindeki **bütün `.log` dosyalarını** (alt klasörler dahil) bul. `sistem`'e göre göreli yollarını, `/` ayraçlı olarak (`as_posix()`), **alfabetik sırayla** her satıra bir tane yazdır.

```setup
from pathlib import Path
for yol in ["sistem/auth.log", "sistem/web/erisim.log", "sistem/web/eski/erisim.log.1",
            "sistem/web/eski/hata.log", "sistem/notlar.txt", "sistem/db/sorgu.log"]:
    p = Path(yol)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("x", encoding="utf-8")
```

```starter
from pathlib import Path

```

```test
eq(lines, ["auth.log", "db/sorgu.log", "web/erisim.log", "web/eski/hata.log"], "4 log dosyası, alfabetik")
ok(calls("rglob") or calls("walk") or calls("glob"), "rglob (ya da glob/os.walk) kullan")
```

```solution
from pathlib import Path

kok = Path("sistem")
for p in sorted(kok.rglob("*.log")):
    print(p.relative_to(kok).as_posix())
```

```hint
`Path("sistem").rglob("*.log")` alt klasörleri de tarar. `p.relative_to(kok).as_posix()` göreli yolu `/` ile verir.
```

```hint
Sıralamayı yollar üzerinde değil, metinler üzerinde yapmak daha güvenli: `sorted(...)` her ikisinde de burada aynı sonucu verir.
```
:::

::: gorev Güvenli yol çözücü
`guvenli_yol(kok, istek)` fonksiyonunu yaz. `kok` (bir `Path` ya da metin) ile kullanıcının istediği göreli yolu birleştirip **çözülmüş** `Path`'i döndürsün. Sonuç kökün dışına çıkıyorsa `PermissionError` yükseltsin.

```setup
from pathlib import Path
Path("site/genel").mkdir(parents=True, exist_ok=True)
Path("site/genel/index.html").write_text("ok", encoding="utf-8")
Path("gizli.txt").write_text("sır", encoding="utf-8")
```

```starter
from pathlib import Path

def guvenli_yol(kok, istek):
    return Path(kok) / istek
```

```test
from pathlib import Path
need("guvenli_yol")
kok = Path("site")
eq(guvenli_yol(kok, "genel/index.html"), (kok / "genel/index.html").resolve(), "normal istek çözülmüş yol döner")
eq(guvenli_yol("site", "genel/../genel/index.html"), (kok / "genel/index.html").resolve(), "içeride kalan .. serbest")
raises(PermissionError, guvenli_yol, kok, "../gizli.txt", msg="../gizli.txt → PermissionError")
raises(PermissionError, guvenli_yol, kok, "genel/../../gizli.txt", msg="genel/../../gizli.txt → PermissionError")
raises(PermissionError, guvenli_yol, kok, str(Path("gizli.txt").resolve()), msg="mutlak yol → PermissionError")
```

```solution
from pathlib import Path

def guvenli_yol(kok, istek):
    kok = Path(kok).resolve()
    hedef = (kok / istek).resolve()
    if not hedef.is_relative_to(kok):
        raise PermissionError(f"kök dışı erişim: {istek}")
    return hedef
```

```hint
Hem kökü hem hedefi `resolve()` et, sonra `hedef.is_relative_to(kok)`.
```

```hint
Mutlak bir yolla `/` yapılırsa sol taraf **tamamen yok sayılır**: `Path("site") / "C:/gizli.txt"` → `C:/gizli.txt`. Çözülmüş kontrol bunu da yakalar.
```
:::

::: gorev Uzantıya göre disk kullanımı
`veri` klasöründeki (alt klasörler dahil) **dosyaların** boyutlarını uzantılarına göre topla. Uzantıları alfabetik sırayla `uzantı: bayt` biçiminde yazdır. Uzantısız dosyalar için `(yok)` yaz.

```setup
from pathlib import Path
dosyalar = {"veri/a.log": 120, "veri/b.log": 30, "veri/alt/c.csv": 500, "veri/alt/d.LOG": 7,
            "veri/README": 10, "veri/alt/derin/e.csv": 1}
for yol, n in dosyalar.items():
    p = Path(yol)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"x" * n)
```

```starter
from pathlib import Path

```

```test
eq(lines, ["(yok): 10", ".LOG: 7", ".csv: 501", ".log: 150"], "uzantı başına toplam (büyük-küçük harf ayrı)")
```

```solution
from pathlib import Path

toplam = {}
for p in Path("veri").rglob("*"):
    if p.is_file():
        uz = p.suffix or "(yok)"
        toplam[uz] = toplam.get(uz, 0) + p.stat().st_size
for uz in sorted(toplam):
    print(f"{uz}: {toplam[uz]}")
```

```hint
`rglob("*")` her şeyi verir; `is_file()` ile klasörleri ele. `p.suffix` uzantıyı, `p.stat().st_size` boyutu verir.
```
:::
