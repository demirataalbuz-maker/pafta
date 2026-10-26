---
id: yr23
title: Kural Paketi · Externals, Include ve Namespace
summary: Gerçek yara-python ile çevresel değerleri bağlamak, ders içi include çözmek ve aynı adlı kuralları namespace ile ayırmak.
---

::: anlat Bir kuraldan pakete
`yara.compile(sources={namespace: kaynak}, externals={...})` birden çok kaynak derler. Aynı adlı iki kural farklı namespace'lerde bulunabilir; yalnız `m.rule` raporlamak bunları birbirine karıştırır. Aynı namespace içindeki iki aynı ad ise derleme hatasıdır. `global` kurallar namespace kapsamında ele alınır; bütün pakete tek bir genel koşul diye düşünme.

Dış değişken önce derleme sırasında türüyle tanımlanır. `rules.match(externals=...)` tarama çağrısındaki değeri değiştirebilir; tanımsız sembol kendi kendine oluşmaz. Derleme varsayılanı sonraki çağrılarda kaybolmaz. Dosya adı/uzantı otomatik external değildir: çağıran kod sağlamalıdır.

Bu ders Python API yazar; kural metni yine gerçek libyara'da derlenir. `yara_lab.compile_bundle` yalnız verilen kaynak sözlüğündeki include adlarını döndüren gerçek `include_callback` kullanır; host dosyasına geri düşmez. Varsayılan YARA tezgahı `includes=False` olarak kalır. `includes={'ortak.yar': '...'}` verilirse yalnız bu sanal dosya açılır; mutlak/üst dizin yolları reddedilir. Include izni, rastgele diski okuma izni değildir.

[Resmî API: sources, externals, include_callback, warnings](https://yara.readthedocs.io/en/stable/yarapython.html). Dış değişkenler bool/int/str ile sınırlandırılmış örneklerdir; tam dağıtım sistemi veya CLI taklidi değildir.
:::

::: tahmin Aynı ad, iki namespace
```python
from yara_lab import compile_bundle, scan_bytes
r = compile_bundle({'sol': 'rule Isaret {condition: limit >= 4}', 'sag': 'rule Isaret {condition: limit > 4}'}, {'limit': 4})
print(sorted((m.namespace, m.rule) for m in scan_bytes(r, b'')))
print(sorted((m.namespace, m.rule) for m in scan_bytes(r, b'', {'limit': 5})))
```
???
`[('sol', 'Isaret')]` ve `[('sag', 'Isaret'), ('sol', 'Isaret')]`. Eşik 4 ilk koşula dahildir, ikinciye dahil değildir.
```meta
motor: python
dil: python
timeout: 45
```
:::

::: gorev İki kaynağı gerçek derleyiciye bağla
`paket(kaynaklar, dosyalar, limit)` derlenmiş Rules döndürsün. External adı `limit`; include metinleri `dosyalar` sözlüğünde. Derleme hatalarını yutma. Testler kuralı sonradan gerçek veride tarar.

```starter
from yara_lab import compile_bundle, scan_bytes

def paket(kaynaklar, dosyalar, limit):
    return compile_bundle(kaynaklar, {"limit": 0})
```

```test
import yara
sources={'a': 'include "ortak.yar"\nrule A {condition: Yardim and filesize <= limit}', 'b':'rule A {condition: filesize > limit}'}
files={'ortak.yar':'private rule Yardim {strings: $x="PF" condition: $x at 0}'}
r=paket(sources, files, 4)
def names(data, external=None):
    return sorted((m.namespace,m.rule) for m in scan_bytes(r,data,external))
eq(names(b'PF'), [('a','A')], 'include kuralı ve küçük dosya')
eq(names(b'PFxx'), [('a','A')], 'kapalı eşik 4')
eq(names(b'PFxxx'), [('b','A')], 'eşik üstü 5')
eq(names(b'xxPF'), [], 'include içindeki konum koşulu')
eq(names(b'PFxx', {'limit':3}), [('b','A')], 'çağrıdaki external geçersiz kılma')
eq(names(b'PFxx'), [('a','A')], 'derleme varsayılanı korunur')
raises(Exception, lambda: paket({'a':'rule A {condition: bilinmeyen}'}, {}, 4), msg='tanımsız external')
raises(Exception, lambda: paket({'a':'include "eksik.yar"'}, files, 4), msg='eksik include')
raises(Exception, lambda: paket({'a':'rule A {condition:true} rule A {condition:true}'}, {}, 4), msg='aynı namespace çakışması')
raises(Exception, lambda: paket({'a':'include "../gizli.yar"'}, {'../gizli.yar':'rule X {condition:true}'}, 4), msg='üst dizin yolu reddedilir')
```

```solution
from yara_lab import compile_bundle, scan_bytes

def paket(kaynaklar, dosyalar, limit):
    return compile_bundle(kaynaklar, {'limit': limit}, dosyalar)

```

```hint
Gerçek API sonucunu işle; örnek adlarına göre sonuç sabitleme.
```

```meta
motor: python
dil: python
timeout: 45
```
:::

::: gorev Kimliği kaybetmeden raporla
`kimlikler(eslesmeler)` gerçek Match nesnelerinden `(namespace, rule)` çiftlerini tekrarsız ve sıralı döndürsün.

```starter
def kimlikler(eslesmeler):
    return sorted({m.rule for m in eslesmeler})
```

```test
from yara_lab import compile_bundle, scan_bytes
r=compile_bundle({'bir':'rule A {condition:true} rule B {condition:true}', 'iki':'rule A {condition:true}'})
m=scan_bytes(r,b'')
eq(kimlikler(m), [('bir','A'),('bir','B'),('iki','A')], 'aynı ad ayrı namespace')
eq(kimlikler(m+m), [('bir','A'),('bir','B'),('iki','A')], 'tekrarları kaldır')
eq(kimlikler([]), [], 'boş eşleşme')
eq(kimlikler(list(reversed(m))), [('bir','A'),('bir','B'),('iki','A')], 'girdi sırasına bağlı değil')
```

```solution
def kimlikler(eslesmeler):
    return sorted({(m.namespace, m.rule) for m in eslesmeler})
```

```hint
Gerçek API sonucunu işle; örnek adlarına göre sonuç sabitleme.
```

```meta
motor: python
dil: python
timeout: 45
```
:::
