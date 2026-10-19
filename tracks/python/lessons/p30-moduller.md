---
id: p30
title: Modüller ve Paketler
summary: import nasıl çalışır; sys.path, sys.modules önbelleği, __name__ koruması ve paketler.
---

::: anlat Her .py dosyası bir modüldür
Bir Python dosyası **modüldür**; içindeki fonksiyonlar, sınıflar ve değişkenler başka dosyalardan `import` ile kullanılabilir. Standart kütüphane yüzlerce hazır modülle gelir ("pilleri dahil" felsefesi):

```python
import math                        #! modülü al, math.x ile eriş
print(math.sqrt(144))

from math import pi, floor         #! belirli isimleri doğrudan al
print(floor(pi * 100) / 100)

import datetime as dt              #! takma adla al
print(dt.date(2026, 10, 19).isoformat())

from collections import Counter as Sayac
print(Sayac("aab"))
```

> [!TUZAK]
> `from modul import *` yazma. Modüldeki tüm isimleri senin isim alanına döker; hangi ismin nereden geldiğini kaybedersin ve kendi değişkenlerini sessizce ezebilirsin. Ayrıca dosyalarına **standart kütüphane modüllerinin adını verme**: `random.py`, `json.py`, `socket.py` diye bir dosyan varsa `import random` seninkini yükler ve her şey tuhaf biçimde bozulur.

### import gerçekte ne yapar?
1. `sys.modules` sözlüğüne bakar: modül **zaten yüklendiyse** onu döndürür.
2. Yoksa `sys.path` listesindeki klasörlerde `isim.py` dosyasını (ya da `isim/` paketini) arar.
3. Bulduğu dosyayı **baştan sona bir kez çalıştırır**, oluşan isim alanını bir modül nesnesine koyar ve `sys.modules`'e kaydeder.

```python
import sys
print(sys.path[:3])                 #! arama sırası
print("math" in sys.modules)
print(type(sys), sys.__name__)     #! modül de bir nesnedir
```

> [!NOT]
> Normalde çalıştırdığın betiğin klasörü otomatik olarak `sys.path`'in başındadır. Tezgah güvenlik için **izole kipte** (`python -I`) çalışır ve betik klasörünü eklemez. Bu yüzden aşağıdaki örneklerde kendi modülümüzü bulması için `sys.path.insert(0, ".")` yazıyoruz. Sen de böylece `sys.path`'in nasıl çalıştığını elinle görmüş oluyorsun.

> [!GÜVENLİK]
> `sys.path` arama sırası bir saldırı yüzeyidir. Yazılabilir bir klasöre `json.py` ya da `requests.py` bırakan bir saldırgan, o klasörde çalışan her Python betiğine kod enjekte eder. Bu *module/DLL hijacking*'in Python versiyonudur. `-I` bayrağının var olma sebebi budur ve güvenilmeyen klasörlerde betik çalıştırırken kullanılır. Benzer şekilde PyPI'da popüler paketlere benzeyen adlarla yayınlanan kötü paketler (*typosquatting*: `reqeusts`) tedarik zinciri saldırılarının klasiğidir.
:::

::: tahmin
Çıktı tek satır:

```python
import math as m
from math import sqrt, pi
print(m.sqrt(16) == sqrt(16), round(pi, 2))
```

???

`True 3.14`. `m.sqrt` ve `sqrt` aynı fonksiyon nesnesidir; sadece iki farklı yoldan erişiliyor.
:::

::: anlat __name__ koruması ve paketler
Her modülün bir `__name__`'i vardır. Dosya **doğrudan çalıştırıldığında** bu değer `"__main__"`, **import edildiğinde** ise modülün adıdır. Bu sayede bir dosya hem kütüphane hem program olabilir:

```python
import sys
from pathlib import Path

Path("tarayici.py").write_text('''
def kontrol(ip):
    return ip.count(".") == 3

if __name__ == "__main__":          # sadece doğrudan çalıştırılınca
    print("komut satırı aracı çalışıyor")
print("modül yüklendi, __name__ =", __name__)
''', encoding="utf-8")

sys.path.insert(0, ".")
import tarayici                      #! import → __main__ bloğu ÇALIŞMAZ
print(tarayici.kontrol("10.0.0.1"))
```

`if __name__ == "__main__":` bloğunu her betiğine koy: import edildiğinde istenmeyen kod (tarama, dosya silme, sunucu başlatma) çalışmasın.

### Paketler
Klasör = **paket**. İçinde `__init__.py` olan bir klasör, modülleri gruplar: `import guvenlik.tespit`. `__init__.py` paket ilk import edildiğinde çalışır; boş olabilir.

```text
guvenlik/
├── __init__.py
├── tespit.py        →  from guvenlik.tespit import kural_uygula
└── ag/
    ├── __init__.py
    └── soket.py     →  from guvenlik.ag import soket
```

Paket içinden kardeş modüle **göreli import** yapılabilir: `from . import tespit`, `from ..ag import soket`.

> [!DERİN]
> Modüller **tekildir** (singleton): aynı modülü 50 yerde import etsen de bir kez çalışır, herkes aynı nesneyi paylaşır. Bu yüzden modül düzeyindeki bir değişken, uygulama genelinde paylaşılan bir duruma dönüşür. Kodu değiştirdikten sonra yeniden yüklemek için `importlib.reload(modul)` vardır. İsimle dinamik yüklemek için `importlib.import_module("json")` kullanılır; eklenti sistemleri bunun üstüne kurulur.
:::

::: tahmin
İki satır:

```python
import sys
from pathlib import Path
Path("arac.py").write_text('print("yükleniyor", __name__)\nX = 1\n', encoding="utf-8")
sys.path.insert(0, ".")
import arac
import arac
print(arac.X, "arac" in sys.modules)
```

???

`yükleniyor arac`, sonra `1 True`. Modül sadece **ilk** import'ta çalışır; ikinci `import arac` `sys.modules`'teki hazır nesneyi döndürür, dosyayı yeniden çalıştırmaz. İçeriden bakınca `__name__` dosyanın adıdır, `"__main__"` değildir.
:::

::: gorev İlk modülün
Kodunla çalışma klasörüne `yardimci.py` adında bir dosya yaz. İçinde `kare(x)` fonksiyonu olsun ve `x * x` döndürsün. Sonra `sys.path`'i ayarla, modülü import et ve `yardimci.kare(7)` sonucunu yazdır.

```starter
import sys
from pathlib import Path

# 1) yardimci.py dosyasını yaz
# 2) sys.path ayarı
# 3) import et ve kare(7) yazdır
```

```test
from pathlib import Path
eq(out.strip(), "49", "yardimci.kare(7) → 49")
ok(Path("yardimci.py").exists() and "def kare" in Path("yardimci.py").read_text(encoding="utf-8"), "yardimci.py içinde def kare olmalı")
ok(uses("import") and "import yardimci" in src or "from yardimci" in src, "modülü import et")
```

```solution
import sys
from pathlib import Path

Path("yardimci.py").write_text("def kare(x):\n    return x * x\n", encoding="utf-8")
sys.path.insert(0, ".")
import yardimci
print(yardimci.kare(7))
```

```hint
`Path("yardimci.py").write_text("def kare(x):\n    return x * x\n", encoding="utf-8")`
```
:::

::: gorev Ana program koruması
Bir `topla(a, b)` fonksiyonu tanımla. Dosya **doğrudan çalıştırıldığında** `topla(2, 3)` sonucunu yazdırsın; **import edildiğinde** hiçbir şey yazdırmasın. Testler kodunu bir de modül gibi yükleyecek.

```starter
def topla(a, b):
    return a + b

print(topla(2, 3))
```

```test
eq(out, "5\n", "doğrudan çalışınca 5 yazmalı")
ns = {"__name__": "kodum"}
_, yazilan = capture(exec, src, ns)
eq(yazilan, "", "import edilince hiçbir şey yazmamalı")
ok(ns.get("topla") and ns["topla"](10, 5) == 15, "import edilince topla kullanılabilir olmalı")
```

```solution
def topla(a, b):
    return a + b

if __name__ == "__main__":
    print(topla(2, 3))
```

```hint
`if __name__ == "__main__":` bloğunun içine al.
```
:::

::: gorev Eklenti yükleyici
Girdide boşlukla ayrılmış modül adları var. Her birini `importlib.import_module` ile **isimle** yüklemeyi dene ve sırayla şunu yazdır:

- yüklendiyse: `ad: tamam`
- modül yoksa: `ad: bulunamadı` (`ModuleNotFoundError` yakala)

```starter
import importlib
adlar = input().split()

```

```stdin
json yok_boyle_bir_modul math
```

```test
eq(run("json yok_boyle_bir_modul math").strip().splitlines(), ["json: tamam", "yok_boyle_bir_modul: bulunamadı", "math: tamam"], "örnek")
eq(run("hashlib").strip(), "hashlib: tamam", "hashlib")
ok(calls("import_module"), "importlib.import_module kullan")
ok(uses("try"), "ModuleNotFoundError yakala")
```

```solution
import importlib
adlar = input().split()
for ad in adlar:
    try:
        importlib.import_module(ad)
        print(f"{ad}: tamam")
    except ModuleNotFoundError:
        print(f"{ad}: bulunamadı")
```

```hint
`importlib.import_module(ad)` metinden modül yükler. Bulamazsa `ModuleNotFoundError` yükseltir.
```
:::
