---
id: p66
title: Bytecode, dis ve AST
summary: Kaynaktan bytecode'a yolculuk; kod nesneleri, yığın makinesi, sabit katlama ve ast ile statik analiz.
---

::: anlat Kaynak → AST → bytecode → sanal makine
P01'de bir söz vermiştik. Python kodunu çalıştırırken şu adımlar olur:

1. **Ayrıştırma**: metin, bir **soyut sözdizimi ağacına** (AST) çevrilir
2. **Derleme**: AST, **bytecode** komutlarına derlenir ve bir **kod nesnesine** konur (`.pyc` dosyaları bunun diske yazılmış halidir)
3. **Yürütme**: CPython'un sanal makinesi (`ceval.c` içindeki dev bir döngü) komutları tek tek çalıştırır

Bu bir **yığın makinesidir**: komutlar değerleri bir yığına iter ve oradan çeker.

```python
import dis

def toplam_karesi(a, b):
    c = a + b
    return c * c

dis.dis(toplam_karesi)
```

Çıktıyı oku: `LOAD_FAST a` → yığına a'yı it, `LOAD_FAST b` → b'yi it, `BINARY_OP +` → ikisini çek, topla, sonucu it, `STORE_FAST c` → çek ve c'ye yaz... Tezgahtaki **Bytecode** sekmesi bu çıktının aynısını gösterir.

### Kod nesnesi
Her fonksiyonun derlenmiş hali `__code__` niteliğindedir:

```python
def f(a, b=2):
    c = a + b
    return c * 2

k = f.__code__
print(k.co_name, k.co_argcount, k.co_varnames)   #! ad, argüman sayısı, yerel isimler
print(k.co_consts, k.co_names)                    #! sabitler, global/nitelik isimleri
print(k.co_filename, k.co_firstlineno)
print(len(k.co_code), "bayt bytecode")
```

`compile()` ile istediğin metni kod nesnesine çevirebilir, `exec`/`eval` ile çalıştırabilirsin: `exec(compile("x = 1 + 2", "<metin>", "exec"))`. Tezgah kodunu tam olarak böyle çalıştırır.

> [!DERİN]
> Neden **yerel değişkenler globallerden hızlıdır?** Yereller derleme anında bilinir ve bir dizideki sabit konuma yerleşir: `LOAD_FAST` doğrudan indekse erişir. Globaller ise her erişimde bir sözlükte aranır (`LOAD_GLOBAL`), bulunamazsa yerleşikler sözlüğüne bakılır. Python 3.11'in "özelleştirici yorumlayıcısı" sık çalışan komutları türüne göre uyarlanmış hızlı sürümlerle (`LOAD_GLOBAL_BUILTIN` gibi) değiştirir. `dis.dis(f, adaptive=True)` ile birkaç çağrıdan sonra bunu görebilirsin.
:::

::: tahmin
Çıktı tek satır:

```python
def f(a, b):
    c = a + b
    return c * 2

k = f.__code__
print(k.co_argcount, k.co_varnames, k.co_name)
```

???

`2 ('a', 'b', 'c') f`. `co_varnames` önce argümanları, sonra diğer yerel değişkenleri sırayla listeler.
:::

::: anlat Derleyici optimizasyonları ve ast
Derleyici bazı işleri **derleme anında** yapar. En bilineni **sabit katlamadır** (constant folding):

```python
def gun_saniye():
    return 24 * 60 * 60                  #! çarpma çalışma anında yapılmaz

print(gun_saniye.__code__.co_consts)     #! 86400 hazır sabit olarak duruyor
import dis
dis.dis(gun_saniye)                      #! tek bir LOAD_CONST 86400
```

### ast: kodu veri olarak işlemek
`ast` modülü kaynak kodu bir ağaç olarak verir. Kodu **çalıştırmadan** analiz etmenin temelidir. Linter'lar, biçimlendiriciler ve güvenlik tarayıcıları (Bandit, Semgrep) böyle çalışır:

```python
import ast

kaynak = '''
import os
def temizle(yol):
    os.system("rm -rf " + yol)
    return eval(input())
'''
agac = ast.parse(kaynak)
print(ast.dump(agac.body[1].body[0], indent=1)[:300])

class CagriBulucu(ast.NodeVisitor):
    def visit_Call(self, dugum):                      #! her Call düğümünde çağrılır
        hedef = ast.unparse(dugum.func)
        print(f"satır {dugum.lineno}: {hedef}(...)")
        self.generic_visit(dugum)                     #! alt düğümlere de in

CagriBulucu().visit(agac)
```

> [!GÜVENLİK]
> **Statik uygulama güvenlik testi** (SAST), kodu çalıştırmadan riskli kalıpları bulur: `eval`, `exec`, `pickle.loads`, `shell=True`, sabit yazılmış parolalar, zayıf özet fonksiyonları... Bunların hepsi AST üzerinde birer desen aramasıdır. Bu paftanın ikinci görevinde kendi küçük SAST aracını yazacaksın. Pafta'nın görev testleri de senin kodunda `uses("for")` gibi kontrolleri aynı yöntemle yapıyor.
:::

::: tahmin
Çıktı tek satır:

```python
def g():
    return 24 * 60 * 60

k = g.__code__.co_consts
print(86400 in k, 24 in k)
```

???

`True False`. Derleyici `24 * 60 * 60` ifadesini derleme anında hesaplayıp sadece sonucu sabit olarak saklar; 24, 60 gibi ara sabitler kod nesnesinde hiç yer almaz.
:::

::: gorev Komut istatistiği
`komut_sayimi(fonk)` fonksiyonu, verilen fonksiyonun bytecode'undaki her komut adının (`opname`) kaç kez geçtiğini bir sözlük olarak döndürsün. `dis.get_instructions` kullan.

```starter
import dis

def komut_sayimi(fonk):
    pass
```

```test
import dis
from collections import Counter
need("komut_sayimi")
def ornek(liste):
    toplam = 0
    for x in liste:
        if x > 0:
            toplam += x
    return toplam
s = komut_sayimi(ornek)
eq(s, dict(Counter(i.opname for i in dis.get_instructions(ornek))), "tüm komutların sayımı")
ok(s.get("RETURN_VALUE", 0) >= 1, "en az bir RETURN_VALUE")
ok(isinstance(s, dict), "sözlük döndürmeli")
ok(calls("get_instructions"), "dis.get_instructions kullan")
```

```solution
import dis

def komut_sayimi(fonk):
    sayim = {}
    for komut in dis.get_instructions(fonk):
        sayim[komut.opname] = sayim.get(komut.opname, 0) + 1
    return sayim
```

```hint
`for komut in dis.get_instructions(fonk):` her `komut`'un `opname` niteliği var.
```
:::

::: gorev Mini SAST
`riskli_cagrilar(kaynak)` fonksiyonu Python kaynak metnini **çalıştırmadan** `ast` ile tarasın ve riskli çağrıları `(satır, açıklama)` demetleri olarak satır sırasıyla döndürsün:

| Çağrı | Açıklama |
|---|---|
| `eval(...)` / `exec(...)` | `"eval"` / `"exec"` |
| `os.system(...)` | `"os.system"` |
| `pickle.loads(...)` / `pickle.load(...)` | `"pickle.loads"` / `"pickle.load"` |
| herhangi bir çağrıda `shell=True` anahtar argümanı | `"shell=True"` |

```starter
import ast

def riskli_cagrilar(kaynak):
    pass
```

```test
need("riskli_cagrilar")
kod = '''import os, pickle, subprocess
def f(x, veri):
    y = eval(x)
    os.system("ls " + x)
    subprocess.run(["ls"], shell=False)
    subprocess.run("ls " + x, shell=True)
    obj = pickle.loads(veri)
    print("eval kelimesi metinde geçse sorun yok")
    exec(compile(x, "s", "exec"))
'''
eq(riskli_cagrilar(kod), [(3, "eval"), (4, "os.system"), (6, "shell=True"), (7, "pickle.loads"), (9, "exec")], "riskli çağrılar")
eq(riskli_cagrilar("print('temiz kod')"), [], "temiz kod → []")
ok(not calls("exec") and not calls("eval"), "kodu çalıştırma, sadece ast ile analiz et")
```

```solution
import ast

RISKLI = {"eval", "exec", "os.system", "pickle.loads", "pickle.load"}

def riskli_cagrilar(kaynak):
    bulgular = []
    for dugum in ast.walk(ast.parse(kaynak)):
        if not isinstance(dugum, ast.Call):
            continue
        ad = ast.unparse(dugum.func)
        if ad in RISKLI:
            bulgular.append((dugum.lineno, ad))
        for kw in dugum.keywords:
            if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                bulgular.append((dugum.lineno, "shell=True"))
    return sorted(bulgular)
```

```hint
`ast.walk(ast.parse(kaynak))` bütün düğümleri gezer. Çağrılar `ast.Call`; çağrılan şeyin metni için `ast.unparse(dugum.func)`.
```

```hint
Anahtar argümanlar `dugum.keywords` listesinde: her birinin `arg` (ad) ve `value` (bir AST düğümü, burada `ast.Constant`) niteliği var.
```
:::

::: gorev Kullanılan globaller
`kullanilan_globaller(fonk)` fonksiyonu, verilen fonksiyonun bytecode'unda `LOAD_GLOBAL` ile okunan isimleri **alfabetik ve tekrarsız** bir liste olarak döndürsün. Yerel değişkenler ve argümanlar listede olmamalı.

```starter
import dis

def kullanilan_globaller(fonk):
    pass
```

```test
need("kullanilan_globaller")
ESIK = 5
def analiz(olaylar):
    sayac = len(olaylar)
    sonuc = sorted(o for o in olaylar if o > ESIK)
    print(sayac)
    return max(sonuc, default=None)
eq(kullanilan_globaller(analiz), ["ESIK", "len", "max", "print", "sorted"], "analiz'in globalleri")
eq(kullanilan_globaller(lambda x: x + 1), [], "global yok")
```

```solution
import dis

def kullanilan_globaller(fonk):
    adlar = set()
    kodlar = [fonk.__code__]
    while kodlar:
        kod = kodlar.pop()
        for komut in dis.get_instructions(kod):
            if komut.opname == "LOAD_GLOBAL":
                adlar.add(komut.argval)
        kodlar.extend(c for c in kod.co_consts if hasattr(c, "co_code"))
    return sorted(adlar)
```

```hint
`komut.opname == "LOAD_GLOBAL"` olanların `argval` değeri ismin kendisidir.
```

```hint
Dikkat: üreteç ifadesi (`o for o in ...`) ayrı bir **iç kod nesnesidir** ve `co_consts` içinde durur. `ESIK` oradan okunuyor; iç kod nesnelerini de tara.
```
:::
