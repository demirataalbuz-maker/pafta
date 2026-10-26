---
id: bt02
title: Aynı Soruyu Kusto ve SPL ile Sormak
summary: Kanıt penceresini iki sorgu dilinde yeniden üret; eşit uç, hesap, cihaz ve kaynak filtresini koru.
---

::: anlat Aramayı olay iddialarına bağla
İlk soru: **ws01 üzerinde alice için auth kaynağındaki başarısız girişlerin hangileri ilk 120 saniye içinde?** Bu pencerede iki uç da dahil. Beklenen kanıtlar a-start, a-mid, a-edge. Önceki saniye a-before ve sonraki saniye a-after; başka host/hesap ve başarılı giriş kontrol grubudur. Bu eşikler ürün varsayılanı veya saldırı kanıtı değil, açık soru sözleşmesidir.

`v.sorgu('kql',metin,rows)` ya da `v.sorgu('spl',metin,rows)` her çağrıda yeni bellek tablosu kurar. `rows` verilmezse paket kullanılır. Tablo adı olaylar; sütunlar id,ts,source,host,user,event,outcome,src,Image,CommandLine. KQL `olaylar | where ... | project id`, SPL `sourcetype=olaylar | where ... | table id` biçimindedir. SPL index alanı yerel backend'de ops'tur; gerçek index bilgisi değildir. Zaman kıyası burada göreli ts üzerindedir, _time veya TimeGenerated sanma.

KQL `==` karşılaştırmasını bilinçli kullan; bu görev küçük harfe normalize edilmiş host/user varsayar. Üretim aramasında alan eşlemesi, NULL, harf durumu ve zaman aralığını ayrıca ürün üzerinde doğrula. İki yerel sorgunun uyuşması gerçek Sentinel/Splunk eşdeğerliği kanıtı değildir. [Kusto where](https://learn.microsoft.com/en-us/kusto/query/where-operator), [SPL where](https://help.splunk.com/en/splunk-enterprise/search/spl-search-reference/9.4/search-commands/where).
:::

::: tahmin
```python
import vaka_lab as v
rows=v.sorgu('kql','olaylar | where source == "auth" and ts == 120 | project id')
print([r['id'] for r in rows])
```

???
`['a-edge']`. 120 dahil uçtur; bu sorgu henüz başarısız girişlerin tamamını seçmez.
:::

::: gorev Kusto inceleme sorgusu
`kusto()` istenen soruyu cevaplayan KQL metnini döndürsün. Sonuçta yalnız id sütunu bulunsun. Sıra zorunlu değil; fazladan kayıt veya tekrar olmasın. Veride id değişse de koşul doğru kalmalı.

```starter
def kusto():
    return 'olaylar | project id'
```

```test
import vaka_lab as v
def check(rows):
    got=v.sorgu('kql',kusto(),rows)
    wanted=sorted(r['id'] for r in rows if r['source']=='auth' and r['host']=='ws01' and r['user']=='alice' and r['outcome']=='failure' and 0<=r['ts']<=120)
    eq(sorted(r['id'] for r in got),wanted,'kayıt kümesi ve sınırlar')
    ok(all(set(r)=={'id'} for r in got),'yalnız id')
rows=v.yukle();rows += [dict(rows[0],id='non-auth',ts=60,source='proxy'),dict(rows[0],id='success-in-window',ts=60,outcome='success')];check(rows)
check([dict(r,id='yeni-'+r['id']) for r in rows])
check([dict(rows[0],id='first',ts=0),dict(rows[0],id='last',ts=120),dict(rows[0],id='out',ts=121)])
check([])
```

```solution
def kusto():
    return 'olaylar | where source == "auth" and host == "ws01" and user == "alice" and outcome == "failure" and ts >= 0 and ts <= 120 | project id'
```

```hint
source, host, user, outcome ve iki zaman sınırı ayrı koşullardır. id listesini sorguya gömme.
```
:::

::: gorev Aynı soruyu SPL ile yeniden üret
`spl()` SPL metni döndürsün; bt02'nin aynı kaynak/cihaz/hesap/sonuç ve kapalı zaman penceresini yalnız id ile cevaplasın. KQL metnini SPL diye verme.

```starter
def spl():
    return 'sourcetype=olaylar | table id'
```

```test
import vaka_lab as v
rows=v.yukle();rows += [dict(rows[0],id='non-auth',ts=60,source='proxy'),dict(rows[0],id='success-in-window',ts=60,outcome='success')]
for corpus in (rows,[],[dict(r,id='z-'+r['id']) for r in rows]):
    got=v.sorgu('spl',spl(),corpus)
    expected=sorted(r['id'] for r in corpus if r['source']=='auth' and r['host']=='ws01' and r['user']=='alice' and r['outcome']=='failure' and 0<=r['ts']<=120)
    eq(sorted(r['id'] for r in got),expected,'SPL aynı soruyu cevaplar')
    ok(all(set(r)=={'id'} for r in got),'yalnız id')
```

```solution
def spl():
    return 'sourcetype=olaylar | where source="auth" AND host="ws01" AND user="alice" AND outcome="failure" AND ts>=0 AND ts<=120 | table id'
```

```hint
where koşulunun AND bağlarını koru; komşu saniyeler ve diğer hesaplar kontrol örneğidir.
```
:::
