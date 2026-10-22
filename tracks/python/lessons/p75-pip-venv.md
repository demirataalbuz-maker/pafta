---
id: p75
title: pip, venv ve Tekerlekler
summary: Sistem Python'u neden senin değil (PEP 668); temiz venv ve sistem paketlerini görmemesi; yerel bir paketten pip wheel ile tekerlek üretmek, ad ve sürüm normalleştirmesi; internetsiz --no-index kurulum, sürüm kısıtları ve PEP 440 eşitliği, requirements ve hash'li kilit dosyası.
backend: wsl
timeout: 180
---

::: anlat Sistem Python'u kimin?
Bu dersin bütün adımları gerçek bir Linux'ta (Kali, WSL) çalışır. Oradaki `/usr/bin/python3` **dağıtımındır**: paket yöneticisi `apt` onu ve kütüphanelerini kurar, güncel tutar, başka sistem araçları da ona dayanır. Üstüne `pip` ile bir şey yazmak dağıtımın kurduğu bir kütüphaneyi ezebilir ve sistemi bozabilir. Bu yüzden Debian tabanlı dağıtımlar sistem Python'unu **dışarıdan yönetilen** (PEP 668) olarak işaretler:

```python
import subprocess, sys

r = subprocess.run([sys.executable, "-m", "pip", "install", "--no-index", "pafta-demo"],
                   capture_output=True, text=True)
print(r.returncode)                                      #! 1: pip kurmayı reddetti
print(r.stderr.strip().splitlines()[0])                  #! error: externally-managed-environment
```

Çözüm sistem Python'unu zorlamak (`--break-system-packages`) değil, kendi **sanal ortamını** kurmaktır. `venv` bir klasörde Python'un küçük bir kopyasını ve **boş** bir paket alanı oluşturur:

```python
import subprocess, sys

subprocess.run([sys.executable, "-m", "venv", "--without-pip", "ortam"], check=True)
soru = "import sys; print(sys.prefix != sys.base_prefix)"
print(subprocess.run(["ortam/bin/python", "-c", soru], capture_output=True, text=True).stdout.strip())
```

| Komut ya da yol | Ne yapar |
|---|---|
| `python3 -m venv ortam` | `ortam/` içinde Python ve pip kurar |
| `--without-pip` | pip'i koymaz; çok daha hızlıdır, kurulum yapmayacaksan yeter |
| `--clear` | Klasör varsa içini silip baştan kurar |
| `--system-site-packages` | Sistem paketlerini de görür (temiz değildir) |
| `ortam/bin/python` | O ortamın yorumlayıcısı; Windows'ta `ortam\Scripts\python.exe` |
| `source ortam/bin/activate` | Yalnızca `PATH`'i değiştirir; betiklerde gerek yok, yorumlayıcıyı tam yoluyla çağır |

> [!TUZAK] "Temiz" ortam, sistemdeki paketleri görmez
> Sistem Python'unda `requests` kuruludur; yeni bir venv'de **yoktur**. Bir betik "bende çalışıyordu" deyip başka ortamda `ModuleNotFoundError` veriyorsa sebep çoğu zaman budur: geliştirirken sistem paketleri sessizce kullanılmıştır. Bağımlılığını gerçekten bilmenin yolu, betiği temiz bir venv'de denemektir.
:::

::: anlat Tekerlek: kurulmaya hazır paket
Bir paketi dağıtmanın biçimi **tekerlektir** (wheel): adı belli kurallara uyan bir zip dosyası. İçinde kod ve `.dist-info` klasöründe ad, sürüm ve dosya özetleri vardır. En küçük paket bir `pyproject.toml` ve bir modül klasöründen oluşur:

```text
kaynak/
  pyproject.toml
  pafta_demo/__init__.py
```

```toml
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "pafta-demo"
version = "1.0.0"

[tool.setuptools]
packages = ["pafta_demo"]
```

Tekerleği internetsiz üretmek için üç bayrak gerekir:

```bash norun
python3 -m pip wheel --no-index --no-build-isolation --no-deps -w dist ./kaynak
```

| Bayrak | Neden |
|---|---|
| `--no-index` | PyPI'a gitme |
| `--no-build-isolation` | Derleme için yeni bir ortam kurup `setuptools`'u **indirmeye** kalkma; kurulu olanı kullan |
| `--no-deps` | Bağımlılıkları da derlemeye çalışma |
| `-w dist` | Tekerleği `dist/` klasörüne yaz |

> [!TUZAK] `kaynak` ile `./kaynak` aynı şey değildir
> `pip wheel kaynak` yazarsan pip `kaynak` adında bir **paket** arar ve `Could not find a version that satisfies the requirement kaynak` der. Yerel bir klasörü göstermek için yolun `./` ile başlaması gerekir.

Tekerleğin adı beş parçadır ve iki şey **normalleştirilir**:

```text
pafta_demo-1.0.0-py3-none-any.whl
│          │     │   │    └─ platform: any = her işletim sistemi
│          │     │   └─ ABI: none = derlenmiş kod yok
│          │     └─ Python etiketi: py3
│          └─ sürüm (PEP 440 biçiminde)
└─ ad: küçük harf, - ve . yerine _
```

Bu derste ölçüldü: `name = "Pafta.Demo"`, `version = "01.2"` yazılan bir paketin tekerleği `pafta_demo-1.2-py3-none-any.whl` olur. pip için `Pafta.Demo`, `pafta_demo` ve `pafta-demo` **aynı projedir**.

Kurulum da internetsiz yapılır; `--find-links` pip'e tekerleklerin bulunduğu klasörü gösterir:

```bash norun
python3 -m venv --clear ortam
ortam/bin/python -m pip install --no-index --find-links dist pafta-demo
ortam/bin/python -m pip freeze          # pafta-demo==1.0.0
```
:::

::: anlat Sürüm kısıtları ve kilit dosyası
Bir projeyi başka makinede aynı biçimde kurabilmek için hangi sürümü istediğini yazarsın. pip kısıtı sağlayan **en yüksek** sürümü seçer. `dist/` içinde 1.0.0, 1.1.0 ve 1.2.0 varken:

| İstek | Seçilen | Neden |
|---|---|---|
| `pafta-demo` | 1.2.0 | kısıt yok, en yüksek |
| `pafta-demo==1.1.0` | 1.1.0 | tam eşitlik |
| `pafta-demo<1.1.0` | 1.0.0 | sınır **dahil değil** |
| `pafta-demo<=1.1.0` | 1.1.0 | sınır dahil |
| `pafta-demo>1.2.0` | — | hata: sağlayan sürüm yok |
| `pafta-demo==1.1` | 1.1.0 | PEP 440: eksik sıfırlar tamamlanır, `1.1 == 1.1.0` |
| `pafta-demo~=1.0` | 1.2.0 | "uyumlu sürüm": `>=1.0` ve `==1.*` |

Bu istekler alt alta bir `requirements.txt` dosyasına yazılır ve `pip install -r requirements.txt` ile kurulur. Kurulu ortamın tam fotoğrafını `pip freeze` verir; çıktısı yine `ad==sürüm` biçimindedir ve doğrudan bir requirements dosyası olarak kullanılabilir.

Sürüm sabitlemek "aynı sürüm" demektir, **aynı dosya** demek değildir. Birisi aynı ad ve sürümle değiştirilmiş bir paket koyarsa `==1.0.0` onu yine kurar. Bunu engellemek için satıra dosyanın SHA-256 özetini eklersin:

```text
pafta-demo==1.0.0 --hash=sha256:9c1d…e07a
```

Satırlardan birinde `--hash` varsa pip **hash denetimi kipine** geçer ve özeti tutmayan dosyayı kurmayı reddeder; bu derste ölçülen hata `THESE PACKAGES DO NOT MATCH THE HASHES FROM THE REQUIREMENTS FILE` ile başlar. `--require-hashes` bu kipi açıkça ister ve hash'i olmayan her satırı da reddeder.

> [!GÜVENLİK]
> Bir güvenlik betiğini ya da aracını başkasının makinesinde çalıştıracaksan bağımlılıklarını hash'li bir kilit dosyasıyla teslim et. Yazım hatasıyla seçilmiş benzer adlı paketler (`requets` gibi) ve ele geçirilmiş paket sürümleri gerçek tedarik zinciri saldırılarıdır; sürüm sabitleme onları durdurmaz, hash durdurur. Bu dersteki her kurulum `--no-index` ile yapılır ve internete çıkmaz.
:::

::: tahmin
Ne yazar?

```python
import subprocess, sys

subprocess.run([sys.executable, "-m", "venv", "--without-pip", "temiz"], check=True)
soru = "import sys, importlib.util as u; print(sys.prefix != sys.base_prefix, u.find_spec('requests') is not None)"
for python in (sys.executable, "temiz/bin/python"):
    print(subprocess.run([python, "-c", soru], capture_output=True, text=True).stdout.strip())
```

???

`False True` ve `True False`.

İlk satır sistem Python'udur: sanal ortam değildir (`sys.prefix` ile `sys.base_prefix` aynı) ve dağıtımın kurduğu `requests`'i görür. İkinci satır yeni venv'dir: `sys.prefix` venv klasörünü gösterir, `sys.base_prefix` ise hâlâ sistem Python'unu; bu fark "sanal ortamdayım" demektir. Ve temiz venv `requests`'i **görmez** — paket alanı boştur.
:::

::: gorev Tekerleği üret
Girdi kutusunun ilk satırında bir klasör adı var. O klasördeki paketten internetsiz bir tekerlek üret ve **yalnız** tekerleğin dosya adını yazdır. Tekerleği `dist/` klasörüne yaz; her çalıştırmada `dist/`'i önce boşalt, böylece yalnız bu çalıştırmanın tekerleği orada olur.

Klasör yoksa, paket değilse ya da girdi boşsa tek satır `HATA` yazdır.

Çalışma klasöründe üç klasör hazır: `kaynak` (`pafta-demo` 1.0.0), `ad_degisik` (`Pafta.Demo` 01.2) ve boş bir `bos`.

```stdin
kaynak
```

```setup
import pathlib

def paket(dizin, ad, surum):
    kok = pathlib.Path(dizin)
    (kok / "pafta_demo").mkdir(parents=True, exist_ok=True)
    (kok / "pyproject.toml").write_text(
        '[build-system]\nrequires = ["setuptools>=61"]\nbuild-backend = "setuptools.build_meta"\n\n'
        f'[project]\nname = "{ad}"\nversion = "{surum}"\n\n[tool.setuptools]\npackages = ["pafta_demo"]\n',
        encoding="utf-8")
    (kok / "pafta_demo" / "__init__.py").write_text(f'__version__ = "{surum}"\n', encoding="utf-8")

paket("kaynak", "pafta-demo", "1.0.0")
paket("ad_degisik", "Pafta.Demo", "01.2")
pathlib.Path("bos").mkdir(exist_ok=True)
```

```starter
import subprocess, sys

klasor = input().strip()
r = subprocess.run([sys.executable, "-m", "pip", "wheel", klasor], capture_output=True, text=True)
print(r.returncode)
```

```test
eq(out, "pafta_demo-1.0.0-py3-none-any.whl\n", "pafta-demo 1.0.0 tekerleği")
eq(run(stdin="ad_degisik\n"), "pafta_demo-1.2-py3-none-any.whl\n",
   "Pafta.Demo → pafta_demo, 01.2 → 1.2: ad ve sürüm normalleşir")
eq(run(stdin="bos\n"), "HATA\n", "pyproject.toml olmayan klasör paket değildir")
eq(run(stdin="yok\n"), "HATA\n", "olmayan klasör HATA")
eq(run(stdin="\n"), "HATA\n", "boş girdi HATA")
eq(run(stdin="kaynak\n"), "pafta_demo-1.0.0-py3-none-any.whl\n",
   "dist her çalıştırmada boşaltılır: önceki tekerlekler listeye karışmaz")
```

```solution
import pathlib, shutil, subprocess, sys

klasor = input().strip()
dist = pathlib.Path("dist")
shutil.rmtree(dist, ignore_errors=True)

if not klasor or not pathlib.Path(klasor).is_dir():
    print("HATA")
else:
    r = subprocess.run([sys.executable, "-m", "pip", "wheel", "--no-index", "--no-build-isolation",
                        "--no-deps", "-w", str(dist), "./" + klasor],
                       capture_output=True, text=True)
    tekerlekler = sorted(p.name for p in dist.glob("*.whl")) if r.returncode == 0 else []
    print(tekerlekler[0] if len(tekerlekler) == 1 else "HATA")
```

```hint
Klasörü `"./" + klasor` diye ver; çıplak ad bir paket adı sayılır. `--no-build-isolation` olmadan pip derleme için setuptools'u indirmeye kalkar ve internetsiz ortamda başarısız olur.
```

```hint
`shutil.rmtree(dist, ignore_errors=True)` klasör yoksa da hata vermez. Tekerleğin adını `dist.glob("*.whl")` ile bul.
```
:::

::: gorev Sürüm kısıtıyla temiz kurulum
`dist/` klasöründe `pafta-demo` paketinin üç tekerleği var: 1.0.0, 1.1.0 ve 1.2.0. Girdi kutusunun ilk satırı bir kurulum isteğidir (ör. `pafta-demo<1.1.0`).

Her çalıştırmada `ortam` adında **temiz** bir venv kur (`--clear`), isteği internetsiz kur ve ortamın `pip freeze` çıktısını yazdır. Kurulum başarısız olursa ya da girdi boşsa tek satır `HATA` yazdır. Sistem Python'una hiçbir şey kurma.

```stdin
pafta-demo==1.1.0
```

```setup
import pathlib, subprocess, sys

for surum in ("1.0.0", "1.1.0", "1.2.0"):
    kok = pathlib.Path("paket_" + surum)
    (kok / "pafta_demo").mkdir(parents=True, exist_ok=True)
    (kok / "pyproject.toml").write_text(
        '[build-system]\nrequires = ["setuptools>=61"]\nbuild-backend = "setuptools.build_meta"\n\n'
        f'[project]\nname = "pafta-demo"\nversion = "{surum}"\n\n[tool.setuptools]\npackages = ["pafta_demo"]\n',
        encoding="utf-8")
    (kok / "pafta_demo" / "__init__.py").write_text(f'__version__ = "{surum}"\n', encoding="utf-8")
    subprocess.run([sys.executable, "-m", "pip", "wheel", "--no-index", "--no-build-isolation", "--no-deps",
                    "-w", "dist", "./" + str(kok)], check=True, capture_output=True)
```

```starter
import subprocess, sys

istek = input().strip()
subprocess.run([sys.executable, "-m", "pip", "install", istek])
```

```test
import subprocess, sys
eq(out, "pafta-demo==1.1.0\n", "tam eşitlik")
eq(run(stdin="pafta-demo<1.1.0\n"), "pafta-demo==1.0.0\n", "< sınırı dahil etmez")
eq(run(stdin="pafta-demo<=1.1.0\n"), "pafta-demo==1.1.0\n", "<= sınırı dahil eder")
eq(run(stdin="pafta-demo>1.1.0\n"), "pafta-demo==1.2.0\n", "sınırın üstünde en yüksek sürüm")
eq(run(stdin="pafta-demo>1.2.0\n"), "HATA\n", "en yüksek sürümün de üstü: sağlayan yok")
eq(run(stdin="pafta-demo==1.1\n"), "pafta-demo==1.1.0\n", "PEP 440: 1.1 == 1.1.0")
eq(run(stdin="pafta-demo\n"), "pafta-demo==1.2.0\n", "kısıt yoksa en yüksek sürüm")
eq(run(stdin="\n"), "HATA\n", "boş girdi HATA")
sistem = subprocess.run([sys.executable, "-c", "import pafta_demo"], capture_output=True)
ok(sistem.returncode != 0, "sistem Python'u kirlenmemeli: pafta_demo yalnız venv'de olmalı")
```

```solution
import subprocess, sys

istek = input().strip()
if not istek:
    print("HATA")
else:
    subprocess.run([sys.executable, "-m", "venv", "--clear", "ortam"], check=True)
    python = "ortam/bin/python"
    r = subprocess.run([python, "-m", "pip", "install", "--no-index", "--find-links", "dist", istek],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("HATA")
    else:
        print(subprocess.run([python, "-m", "pip", "freeze"], capture_output=True, text=True).stdout, end="")
```

```hint
Kurulumu venv'in kendi yorumlayıcısıyla yap: `ortam/bin/python -m pip install ...`. `sys.executable` ile yaparsan sistem Python'una kurmaya çalışırsın ve PEP 668 seni durdurur.
```

```hint
`--clear` her çalıştırmada ortamı baştan kurar; yoksa bir önceki çalıştırmanın paketi ortamda kalır ve `pip freeze` yanlış sürümü gösterir.
```
:::

::: gorev Hash'li kilit dosyası
Girdi kutusunun ilk satırı bir tekerlek klasörünün adıdır. Klasörde **tam bir** `.whl` dosyası olmalı; yoksa ya da birden fazlaysa tek satır `HATA` yazdır.

Tek tekerlek varsa:

1. Dosyanın SHA-256 özetini hesapla ve sürümü dosya adından al (adın ikinci parçası).
2. `kilit.txt` dosyasına `pafta-demo==<sürüm> --hash=sha256:<özet>` satırını yaz ve **aynı satırı** yazdır.
3. Temiz bir `ortam` venv'i kur, `kilit.txt`'yi o klasörden internetsiz kur ve `pip freeze` çıktısını yazdır.

Çalışma klasöründe `dist` (bir tekerlek), `iki` (iki tekerlek) ve `bos` (tekerleksiz) hazır.

```stdin
dist
```

```setup
import pathlib, shutil, subprocess, sys

def tekerlek(surum, hedef, not_=""):
    kok = pathlib.Path("paket_" + surum + not_)
    (kok / "pafta_demo").mkdir(parents=True, exist_ok=True)
    (kok / "pyproject.toml").write_text(
        '[build-system]\nrequires = ["setuptools>=61"]\nbuild-backend = "setuptools.build_meta"\n\n'
        f'[project]\nname = "pafta-demo"\nversion = "{surum}"\n\n[tool.setuptools]\npackages = ["pafta_demo"]\n',
        encoding="utf-8")
    (kok / "pafta_demo" / "__init__.py").write_text(f'__version__ = "{surum}"\nNOT = "{not_}"\n', encoding="utf-8")
    subprocess.run([sys.executable, "-m", "pip", "wheel", "--no-index", "--no-build-isolation", "--no-deps",
                    "-w", hedef, "./" + str(kok)], check=True, capture_output=True)

tekerlek("1.0.0", "dist")
tekerlek("1.0.0", "iki")
tekerlek("1.1.0", "iki")
pathlib.Path("bos").mkdir(exist_ok=True)
tekerlek("1.0.0", "sahte", "_degistirilmis")     # aynı ad, aynı sürüm, farklı içerik
```

```starter
import pathlib

klasor = input().strip()
for whl in pathlib.Path(klasor).glob("*.whl"):
    print(whl.name)
```

```test
import hashlib, pathlib, subprocess, sys
satirlar = out.splitlines()
whl = next(pathlib.Path("dist").glob("*.whl"))
ozet = hashlib.sha256(whl.read_bytes()).hexdigest()
eq(len(satirlar), 2, "iki satır: kilit satırı ve pip freeze")
eq(satirlar[0] if satirlar else "", "pafta-demo==1.0.0 --hash=sha256:" + ozet, "kilit satırı dosyanın gerçek özetini taşır")
eq(satirlar[1] if len(satirlar) > 1 else "", "pafta-demo==1.0.0", "kilitli sürüm temiz ortama kuruldu")
eq(pathlib.Path("kilit.txt").read_text(encoding="utf-8").strip(), satirlar[0] if satirlar else "",
   "yazdırılan satır kilit.txt'de")
subprocess.run([sys.executable, "-m", "venv", "--clear", "deneme"], check=True)
sahte = subprocess.run(["deneme/bin/python", "-m", "pip", "install", "--no-index", "--find-links", "sahte",
                        "-r", "kilit.txt"], capture_output=True, text=True)
ok(sahte.returncode != 0, "kilit, aynı ad ve sürümlü ama değiştirilmiş tekerleği reddetmeli")
eq(run(stdin="iki\n"), "HATA\n", "birden fazla tekerlek: hangisinin kilitleneceği belirsiz")
eq(run(stdin="bos\n"), "HATA\n", "tekerlek yok")
eq(run(stdin="yok\n"), "HATA\n", "olmayan klasör")
eq(run(stdin="\n"), "HATA\n", "boş girdi")
```

```solution
import hashlib, pathlib, subprocess, sys

klasor = input().strip()
tekerlekler = sorted(pathlib.Path(klasor).glob("*.whl")) if klasor and pathlib.Path(klasor).is_dir() else []
if len(tekerlekler) != 1:
    print("HATA")
else:
    whl = tekerlekler[0]
    surum = whl.name.split("-")[1]
    ozet = hashlib.sha256(whl.read_bytes()).hexdigest()
    satir = f"pafta-demo=={surum} --hash=sha256:{ozet}"
    pathlib.Path("kilit.txt").write_text(satir + "\n", encoding="utf-8")
    print(satir)
    subprocess.run([sys.executable, "-m", "venv", "--clear", "ortam"], check=True)
    r = subprocess.run(["ortam/bin/python", "-m", "pip", "install", "--no-index", "--find-links", klasor,
                        "--require-hashes", "-r", "kilit.txt"], capture_output=True, text=True)
    if r.returncode != 0:
        print("HATA")
    else:
        print(subprocess.run(["ortam/bin/python", "-m", "pip", "freeze"], capture_output=True, text=True).stdout, end="")
```

```hint
`hashlib.sha256(yol.read_bytes()).hexdigest()` özeti 64 karakterlik onaltılık metin olarak verir. Sürüm, tekerlek adının `-` ile ayrılmış ikinci parçasıdır.
```

```hint
Klasör yoksa `glob` hata vermez ama boş döner; sayım yine 0 olur. `is_dir()` ile önce denetlemek okunurluğu artırır.
```
:::
