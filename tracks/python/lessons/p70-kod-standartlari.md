---
id: p70
title: Kod Standartları · PEP 8, 20, 257
summary: Python'un yazım kılavuzu PEP 8 (girinti, satır uzunluğu, adlandırma, boşluklar, içe aktarma sırası, None ve tür karşılaştırmaları), Python'un ilkeleri PEP 20, docstring kuralları PEP 257 ve docstring biçimleri, inspect.getdoc, linter ve biçimlendiriciler.
---

::: anlat PEP 8: herkesin okuyabildiği Python
Kod bir kez yazılır, defalarca okunur. **PEP 8**, Python topluluğunun ortak yazım kılavuzudur: bir projeyi açtığında adların, boşlukların ve düzenin tanıdık gelmesi bu sayededir. Sınavlarda (PCPP1) ve kod incelemelerinde ilk bakılan şeydir.

| Konu | Kural | Örnek |
|---|---|---|
| Girinti | 4 boşluk, sekme yok | |
| Satır uzunluğu | en fazla 79 karakter (yorum ve docstring 72) | uzun ifadeyi parantez içinde böl |
| Fonksiyon, değişken, modül | `kucuk_harf_alt_cizgi` | `def kullanici_bul():` |
| Sınıf | `BuyukHarfleBirlesik` | `class GunlukOkuyucu:` |
| Sabit | `BUYUK_HARF` | `ZAMAN_ASIMI = 30` |
| İç kullanım | başta tek alt çizgi | `_onbellek` |
| Boş satır | üst düzey tanımlar arasında 2, metotlar arasında 1 | |
| İçe aktarma | dosyanın başında, satır başına bir modül; sıra: standart kütüphane, üçüncü parti, yerel; grupların arasında boş satır | |

### Boşluklar
```python norun
# Doğru
x = y + 1
liste = [1, 2, 3]
sozluk["anahtar"] = deger(a, b=2)       # anahtar kelimeli argümanda = çevresinde boşluk yok

# Yanlış
x=y+1
liste = [ 1,2 ,3 ]
sozluk ["anahtar"] = deger (a, b = 2)
```

### Karşılaştırmalar
| Yerine | Yaz | Neden |
|---|---|---|
| `x == None` | `x is None` | `None` tektir; `==` sınıfın `__eq__`'ine bağlıdır |
| `if len(liste) == 0:` | `if not liste:` | boş koleksiyonlar yanlışımsıdır |
| `type(x) == list` | `isinstance(x, list)` | alt sınıfları da kabul eder |
| `if bayrak == True:` | `if bayrak:` | |
| `except:` | `except ValueError:` | çıplak `except` `KeyboardInterrupt`'ı bile yutar |

```python
deger = None
if deger is None:
    print("değer yok")
print(isinstance(True, int), type(True) == int)   # bool, int'in alt sınıfıdır
```

### PEP 20: Python'un ilkeleri
Yorumlayıcıda `import this` yazınca Tim Peters'ın yazdığı 19 ilke ekrana gelir. Hepsini ezberlemen gerekmez; özü şudur: **açık olan örtük olandan, basit olan karmaşıktan, okunabilirlik zekâ gösterisinden iyidir**; hatalar sessizce geçmemeli; bir işi yapmanın tercihen tek ve belli bir yolu olmalı. PEP 8'in kurallarının çoğu bu ilkelerin uygulamasıdır.

> [!İPUCU]
> Kuralları elle denetleme. **Linter**'lar (`flake8`, `pycodestyle`, `ruff`, `pylint`) kuralı çiğneyen satırı kod numarasıyla gösterir: `E501 line too long`, `E711 comparison to None`. **Biçimlendiriciler** (`black`, `ruff format`) kodu kendiliğinden düzeltir. Bir projede hangisinin kullanıldığı genellikle `pyproject.toml`'da yazar. PEP 8'in kendisi de şunu söyler: tutarsızlık bir projenin kendi kuralıyla çelişiyorsa projeninki kazanır.
:::

::: anlat PEP 257: docstring
**Docstring**, modülün, sınıfın ya da fonksiyonun **ilk ifadesi** olan metindir. Yorumdan farkı, çalışma anında erişilebilmesidir: `fonksiyon.__doc__`, `help(fonksiyon)` ve belgeleme araçları onu okur.

```python
def ortalama(sayilar):
    """Sayıların aritmetik ortalamasını döndür.

    Boş bir dizi verilirse ValueError fırlatır. Sonuç her zaman float'tır.
    """
    if not sayilar:
        raise ValueError("boş dizi")
    return sum(sayilar) / len(sayilar)

print(ortalama.__doc__.splitlines()[0])
```

PEP 257'nin kuralları:

1. Her zaman **üç çift tırnak**: `"""..."""`.
2. **Tek satırlık** docstring tırnaklarla aynı satırda biter ve bir **cümle** olarak noktayla biter: `"""İki sayıyı topla."""`.
3. **Çok satırlı** docstring'de ilk satır kısa bir **özet**tir; ardından **bir boş satır**, sonra ayrıntılar gelir.
4. Özet, bir **emir** gibi yazılır ("Döndür", "Hesapla"); "Bu fonksiyon ... döndürür" diye değil.
5. Fonksiyonun imzasını tekrarlama; ne yaptığını, neyi döndürdüğünü ve hangi istisnaları fırlattığını anlat.

### Docstring biçimleri
Parametreleri ve dönüşü açıklamak için üç yaygın biçim var; bir projede hangisi seçildiyse o kullanılır:

```text
Google                 NumPy                    reST (Sphinx)
Args:                  Parameters               :param sayilar: ...
    sayilar: ...       ----------               :returns: ...
Returns:               sayilar : list           :raises ValueError: ...
    ...                Returns
Raises:                -------
    ValueError: ...
```

Tür bilgisini docstring yerine tip ipuçlarıyla (P47) vermek bugün daha yaygındır; docstring ise **anlamı** anlatır.

> [!NOT]
> `__doc__` metni kaynaktaki girintiyi de taşır. Satırlarına bakarken `inspect.getdoc(nesne)` ya da `inspect.cleandoc(metin)` kullan: ortak girintiyi ve baştaki, sondaki boş satırları temizler. (Python 3.13'ten itibaren derleyici girintiyi kendisi de siler; `cleandoc` iki sürümde de aynı sonucu verir.)
:::

::: tahmin
Üç satır yazar:

```python
import inspect

def topla(a, b):
    """İki sayıyı topla."""
    return a + b

class Sunucu:
    """Bir sunucuyu temsil eder.

    Ayrıntılar burada.
    """

print(topla.__doc__)
print(inspect.cleandoc(Sunucu.__doc__).splitlines()[0])
print(len(inspect.cleandoc(Sunucu.__doc__).splitlines()))
```

???

`İki sayıyı topla.`, `Bir sunucuyu temsil eder.`, `3`. Docstring bir fonksiyonun ya da sınıfın ilk ifadesidir ve `__doc__` ile okunur. `cleandoc` girintiyi ve sondaki boş satırı temizler; geriye özet, boş satır ve ayrıntı satırı kalır.
:::

::: gorev PEP 8'e uydur
Aşağıdaki kod çalışıyor ama PEP 8'i birçok yerde çiğniyor. Davranışını (çıktısını) değiştirmeden düzelt:

- fonksiyon adları ve değişkenler `kucuk_harf_alt_cizgi`, sınıf adı `BuyukHarfleBirlesik`, sabit `BUYUK_HARF`
- `None` ile karşılaştırma `is` / `is not` ile, tür denetimi `isinstance` ile
- 4 boşluk girinti, satırlar en fazla 79 karakter

```starter
esik=80
class sunucuListesi:
  def __init__(self,Sunucular):
    self.Sunucular=Sunucular
  def YuksekOlanlar(self):
    Sonuc=[]
    for s in self.Sunucular:
      if s.get("cpu")!=None and type(s["cpu"])==int and s["cpu"]>esik: Sonuc.append(s["ad"])
    return Sonuc
print(sunucuListesi([{"ad":"db01","cpu":91},{"ad":"web01","cpu":72},{"ad":"cache01","cpu":None}]).YuksekOlanlar())
```

```test
import ast, re
eq(out, "['db01']\n", "çıktı aynı kalmalı")
agac = ast.parse(src)
ok(all(len(s) <= 79 for s in src.splitlines()), "satırlar en fazla 79 karakter")
ok("\t" not in src and all((len(s) - len(s.lstrip(" "))) % 4 == 0 for s in src.splitlines() if s.strip()), "girinti 4 boşluğun katı")
siniflar = [n.name for n in ast.walk(agac) if isinstance(n, ast.ClassDef)]
ok(siniflar and all(re.fullmatch(r"[A-Z][A-Za-z0-9]*", a) for a in siniflar), "sınıf adı BuyukHarfleBirlesik")
fonksiyonlar = [n.name for n in ast.walk(agac) if isinstance(n, ast.FunctionDef)]
ok(all(re.fullmatch(r"_{0,2}[a-z][a-z0-9_]*_{0,2}", a) for a in fonksiyonlar), "fonksiyon adları kucuk_harf_alt_cizgi")
sabitler = [h.id for n in agac.body if isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant)
            for h in n.targets if isinstance(h, ast.Name)]
ok(bool(sabitler) and all(re.fullmatch(r"[A-Z][A-Z0-9_]*", a) for a in sabitler), "eşik sabiti BUYUK_HARF")
none_esit = any(isinstance(n, ast.Compare) and any(isinstance(o, (ast.Eq, ast.NotEq)) for o in n.ops)
                and any(isinstance(c, ast.Constant) and c.value is None for c in n.comparators) for n in ast.walk(agac))
ok(not none_esit, "None ile == / != karşılaştırma yok")
ok(not calls("type"), "tür denetimi isinstance ile")
ok(calls("isinstance"), "isinstance kullan")
```

```solution
ESIK = 80


class SunucuListesi:
    def __init__(self, sunucular):
        self.sunucular = sunucular

    def yuksek_olanlar(self):
        sonuc = []
        for s in self.sunucular:
            cpu = s.get("cpu")
            if cpu is not None and isinstance(cpu, int) and cpu > ESIK:
                sonuc.append(s["ad"])
        return sonuc


liste = SunucuListesi([
    {"ad": "db01", "cpu": 91},
    {"ad": "web01", "cpu": 72},
    {"ad": "cache01", "cpu": None},
])
print(liste.yuksek_olanlar())
```

```hint
Adlar: `ESIK`, `SunucuListesi`, `sunucular`, `yuksek_olanlar`, `sonuc`. `!= None` yerine `is not None`, `type(x) == int` yerine `isinstance(x, int)`.
```

```hint
Uzun son satırı böl: listeyi parantez içinde satırlara yay ya da önce bir değişkene ata. Tek satırlık `if ...: ...` yerine gövdeyi alt satıra yaz.
```
:::

::: gorev PEP 257 docstring
`ortalama(sayilar)` fonksiyonunu yaz: sayıların ortalamasını döndürsün, boş dizide `ValueError` fırlatsın. Fonksiyona PEP 257'ye uygun **çok satırlı** bir docstring yaz: ilk satır noktayla biten kısa bir özet, ardından bir boş satır, ardından boş dizideki davranışı anlatan en az bir ayrıntı satırı (içinde `ValueError` geçsin).

```starter
def ortalama(sayilar):
    # ortalamayı hesaplar
    return sum(sayilar) / len(sayilar)
```

```test
import inspect
need("ortalama")
eq(ortalama([2, 4, 9]), 5.0, "ortalama")
raises(ValueError, ortalama, [], msg="boş dizide ValueError")
belge = inspect.getdoc(ortalama)
ok(belge is not None, "docstring olmalı")
satirlar = (belge or "").splitlines()
ok(len(satirlar) >= 3, "çok satırlı: özet, boş satır, ayrıntı")
ok(bool(satirlar) and satirlar[0].endswith("."), "özet satırı noktayla biter")
ok(len(satirlar) >= 2 and satirlar[1] == "", "özetten sonra bir boş satır")
ok("ValueError" in (belge or ""), "ayrıntıda ValueError anlatılmalı")
ok('"""' in src, "üç çift tırnak kullan")
```

```solution
def ortalama(sayilar):
    """Sayıların aritmetik ortalamasını döndür.

    Boş bir dizi verilirse ValueError fırlatır.
    """
    if not sayilar:
        raise ValueError("boş dizi")
    return sum(sayilar) / len(sayilar)
```

```hint
Yorum (`#`) çalışma anında görülmez; docstring fonksiyon gövdesinin **ilk ifadesi** olan üç tırnaklı metindir.
```

```hint
Biçim: `"""Özet cümlesi.` satırı, bir boş satır, sonra ayrıntı satırı ve kapanış `"""`.
```
:::

::: gorev Kendi mini linter'ın
`denetle(kaynak)` fonksiyonunu yaz: bir Python kaynak metnini satır satır incelesin ve bulduğu sorunları `(satir_no, kod)` çiftleri olarak, satır numarasına sonra koda göre sıralı bir liste halinde döndürsün. Satır numaraları 1'den başlar. Kurallar (gerçek linter kodlarıyla):

| Kod | Kural |
|---|---|
| `E501` | satır 79 karakterden uzun |
| `W191` | girintide sekme var |
| `W291` | satır sonunda boşluk var |
| `E711` | `== None` ya da `!= None` |

```starter
def denetle(kaynak):
    return []
```

```test
need("denetle")
ornek = "x = 1\nif x == None:  \n\tprint(x)\n" + "y = '" + "a" * 80 + "'\n" + "z = x is None\n"
eq(denetle(ornek), [(2, "E711"), (2, "W291"), (3, "W191"), (4, "E501")], "dört sorun")
eq(denetle("temiz = True\n"), [], "temiz kod")
eq(denetle("a != None\n"), [(1, "E711")], "!= None")
eq(denetle("a" * 79 + "\n"), [], "tam 79 karakter: E501 yok")
eq(denetle("a" * 80 + "\n"), [(1, "E501")], "80 karakter: E501")
```

```solution
import re


def denetle(kaynak):
    sorunlar = []
    for no, satir in enumerate(kaynak.splitlines(), 1):
        if len(satir) > 79:
            sorunlar.append((no, "E501"))
        girinti = satir[: len(satir) - len(satir.lstrip())]
        if "\t" in girinti:
            sorunlar.append((no, "W191"))
        if satir != satir.rstrip():
            sorunlar.append((no, "W291"))
        if re.search(r"[!=]=\s*None\b", satir):
            sorunlar.append((no, "E711"))
    return sorted(sorunlar)
```

```hint
`enumerate(kaynak.splitlines(), 1)` satırları 1'den numaralar. Girinti, satırın baştaki boşluk kısmıdır: `satir[:len(satir) - len(satir.lstrip())]`.
```

```hint
Sondaki boşluk: `satir != satir.rstrip()`. `E711` için bir regex: `[!=]=\s*None\b`. En sonda `sorted(...)`.
```
:::
