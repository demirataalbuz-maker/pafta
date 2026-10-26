---
id: yr24
title: Toplu Tarama · Korpus, Hata ve Maliyet
summary: Aynı kural paketini dosya kümesinde işletmek; temiz dosyayı hatadan ayırmak ve tekrar üretilebilir maliyet kaydı tutmak.
---

::: anlat Derle bir kez, tara çok kez
Gerçek dosya kümesi taramasında kuralları her dosyada tekrar derlemek gereksiz maliyettir. Dosyaları bir kez listele, aynı Rules nesnesini kullan, namespace ve kural adını birlikte tut. `rules.match(filepath=...)` dosyayı tarar; `data=...` açık baytları tarar. Bu ders dosyaları geçici çalışma klasöründe oluşturur ve baytlarını API'ye verir; bütün diski taramaz ve süreç belleği okumaz.

`scan_set` her açık ad/bayt girdisini gerçek libyara ile tarar. En çok 32 örnek, örnek başına 1 MiB ve tarama başına 1–5 saniye sınırı vardır. Timeout ayrı `status='timeout'`, `matches=None` döner. Temiz dosya `status='ok', matches=[]` olur. Dosya okuma/derleme hatasını temiz diye raporlama. Namespace çiftleri korunur. Bu bir dizin dolaşma/antivirüs servisi değildir; alt dizin, symlink, izin ve büyük dosya politikası üretimde ayrıca tasarlanır.

YARA timeout saniye cinsinden yerel tarama sınırıdır; hassas süre garantisi değildir. `perf_counter_ns()` ölçümü libyara çağrısı ve Python rapor maliyetini kapsar; derleme süresi ayrı ölçülmelidir. Tek ölçümle “bu kural her makinede hızlıdır” denmez. Uyarı derlemede oluşabilir: `error_on_warning=True` uyarıyı hataya çevirir; Rules.warnings inceleme kanıtıdır. Pafta süreyi başarı ölçütü yapmaz; hatalı mikro-benchmark hızlı makinede geçip yavaşta kalmamalıdır.

[API timeout, warnings ve match](https://yara.readthedocs.io/en/stable/yarapython.html), [CLI seçenekleri ve farkları](https://yara.readthedocs.io/en/stable/commandline.html). Bu ders CLI kurmaz; Python API sınırlarını öğretir.
:::

::: tahmin Temiz dosya da rapora girer
```python
from yara_lab import compile_bundle, scan_set
r=compile_bundle({'p':'rule X {strings: $x="PF" condition:$x}'})
rows=scan_set(r, {'b.bin':b'clean', 'a.bin':b'PF'})
print([(v['file'],v['status'],v['matches']) for v in rows])
```
???
`[('a.bin', 'ok', [('p', 'X')]), ('b.bin', 'ok', [])]`. Temiz dosya kaybolmaz; süre alanını tahmin etmiyoruz.
```meta
motor: python
dil: python
timeout: 45
```
:::

::: gorev Geçici dosya kümesini gerçek motorla tara
`tara(rules, yollar)` verilen dosyaları okuyup `scan_set` sonucunu döndürsün. Rapor adı basename; aynı basename varsa `ValueError`, dosya yoksa okuma hatası aynen yükselsin. Sadece verilen yolları oku.

```starter
def tara(rules, yollar):
    return []
```

```test
from pathlib import Path
from yara_lab import compile_bundle
import tempfile
r=compile_bundle({'a':'rule X {condition:filesize<=4}', 'b':'rule X {strings:$x="PF" condition:$x}'})
with tempfile.TemporaryDirectory(dir='.') as folder:
    root=Path(folder)
    for name,data in [('empty',b''),('four',b'PFxx'),('five',b'PFxxx'),('clean',b'abcde')]:
        (root/name).write_bytes(data)
    rows=tara(r,[str(p) for p in root.iterdir()])
    eq([(x['file'],x['status'],x['matches'],x['bytes']) for x in rows], [('clean','ok',[],5),('empty','ok',[('a','X')],0),('five','ok',[('b','X')],5),('four','ok',[('a','X'),('b','X')],4)],'boş/tam eşik/eşik üstü/temiz korpus')
    ok(all(type(x['elapsed_ns']) is int and x['elapsed_ns']>=0 for x in rows),'ölçülen süre negatif olamaz')
    (root/'four').write_bytes(b'zzzzz')
    eq(tara(r,[str(root/'four')])[0]['matches'], [], 'her çağrıda güncel dosya okunur')
    raises(FileNotFoundError,lambda:tara(r,[str(root/'missing')]),msg='okuma hatası temiz dosya değildir')
    (root/'sub').mkdir();(root/'sub'/'four').write_bytes(b'PF')
    raises(ValueError,lambda:tara(r,[str(root/'four'),str(root/'sub'/'four')]),msg='aynı basename raporu ezmesin')
eq(tara(r,[]), [], 'boş korpus')
```

```solution
from pathlib import Path
from yara_lab import scan_set

def tara(rules, yollar):
    samples = {Path(p).name: Path(p).read_bytes() for p in yollar}
    if len(samples) != len(yollar):
        raise ValueError("Aynı rapor adına iki dosya")
    return scan_set(rules, samples)

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

::: gorev Maliyeti ve eksik taramayı ayrı raporla
`ozet(rows)` scanned/matched/timeouts/bytes/elapsed_ns alanlarını döndürsün. matched eşleşen **dosya** sayısıdır; timeout temiz değildir. Yapay timeout tanığı rapor ayrımını sınar, libyara'nın bu küçük korpusta mutlaka timeout ürettiği iddia edilmez.

```starter
def ozet(rows):
    return {}
```

```test
rows=[{'status':'ok','matches':[('a','X'),('b','X')],'bytes':4,'elapsed_ns':10},{'status':'ok','matches':[],'bytes':5,'elapsed_ns':0},{'status':'timeout','matches':None,'bytes':9,'elapsed_ns':20}]
eq(ozet(rows), {'scanned':3,'matched':1,'timeouts':1,'bytes':18,'elapsed_ns':30},'eşleşen kural sayısı değil dosya sayısı')
eq(ozet([]), {'scanned':0,'matched':0,'timeouts':0,'bytes':0,'elapsed_ns':0},'boş korpus')
from yara_lab import compile_bundle,scan_set
actual=scan_set(compile_bundle({'n':'rule X {condition:filesize==0}'}),{'empty':b'', 'other':b'x'})
o=ozet(actual)
eq((o['scanned'],o['matched'],o['timeouts'],o['bytes']), (2,1,0,1),'gerçek korpustan özet')
eq(o['elapsed_ns'],sum(r['elapsed_ns'] for r in actual),'ölçümü rapordan topla')
```

```solution
def ozet(rows):
    return {"scanned":len(rows), "matched":sum(r["status"]=="ok" and bool(r["matches"]) for r in rows), "timeouts":sum(r["status"]=="timeout" for r in rows), "bytes":sum(r["bytes"] for r in rows), "elapsed_ns":sum(r["elapsed_ns"] for r in rows)}
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
