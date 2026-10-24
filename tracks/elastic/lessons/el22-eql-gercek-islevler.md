---
id: el22
title: Gerçek EQL İşlevleri
summary: endsWith~ ve between~ sorgularını doğrudan Elasticsearch EQL API’sinde çalıştır.
---

::: anlat Gerçek ürün üzerinde çalışma
EL13–EL18'in yerel alt kümesi bütün EQL dili değildir. Burada aynı görünümlü
editörün girdisi `backend: elastic` olduğu için `_eql/search` kullanılır.
`endsWith` son eki, `between` iki ayırıcı arasındaki metni işler. İşlev adına
eklenen `~` işlevin metin eşleştirmesini harf duyarsız yapar; işlevin döndürdüğü
metnin sonraki `==` karşılaştırmasını kendiliğinden harf duyarsız yapmaz.

Ayırıcılar bulunamazsa boş sonuç ile alanın bulunmadığı `null` durumu aynı
şey değildir; eşitlik koşulunu yazarken bunu düşün. `between` dosyanın güvenilir
olduğunu veya gerçek bir dosya yolu olduğunu kanıtlamaz. Özellikle `.exe.bak`
tanığında ayırıcıyla parça çıkarılabilir ama gerçek son ek `.exe` değildir.
Sayı karşılaştırmaları, kategori ve metin işlevlerini birlikte test et.
API'nin sözdizimi/tür hatası öğrenciye açıkça döner; yerel yorumlayıcıda başka
bir sorguyla yaklaşık sonuç üretilmez.

Bu bölüm **gerçek Elasticsearch/Kibana 9.5.5, Basic lisansı** kullanır; önce
[yerel laboratuvar yönergesini](../README.md) uygula. Girdi kutusunda
`backend: elastic` görünür. Önceki Lucene/yerel EQL motoruna sessiz dönüş yoktur.
Her çalıştırma yeni bir geçici indeks kullanır, iş bitince onu siler. Girdideki
`documents` ders tanıklarıdır; sorgu veya pipeline kodu editörde yazılır.
Alan adı, tür, eksik alan ve zaman aralığı sözleşmenin parçasıdır.

Kaynaklar: [EQL function reference](https://www.elastic.co/docs/reference/query-languages/eql/eql-function-ref), [EQL search API](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-eql-search).
:::

::: tahmin Önce çıktıyı düşün
Son ekin harf farkı ve 500 sınırı sonucu nasıl değiştirir?

```meta
dil: eql
timeout: 60
```

```eql
process where endsWith~(process.name, ".exe") and status >= 400 and status < 500
```

```stdin
{"backend":"elastic","dil":"eql","mapping":{"@timestamp":"date","event.category":"keyword","process.name":"keyword","status":"long","file.path":"keyword"},"documents":[{"id":"a","@timestamp":"2026-01-01T00:00:00Z","event.category":"process","process.name":"CMD.EXE","status":400},{"id":"b","@timestamp":"2026-01-01T00:00:00Z","event.category":"process","process.name":"cmd.exe","status":500},{"id":"c","@timestamp":"2026-01-01T00:00:00Z","event.category":"process","process.name":"cmd.exe.bak","status":499},{"id":"d","@timestamp":"2026-01-01T00:00:00Z","event.category":"process","process.name":"agent.ExE","status":499},{"id":"e","@timestamp":"2026-01-01T00:00:00Z","event.category":"process","status":499}],"context":{"tiebreaker_field":"id"}}
```

???
Gerçek API ile doğrulanmış çıktı:

```text
a
d
```

:::

::: gorev Süreç son eki ve aralık
process kategorisinde .exe ile harf duyarsız biten process.name ve 400 dahil, 500 hariç status iste.

```meta
dil: eql
timeout: 60
```

```stdin
{"backend":"elastic","dil":"eql","mapping":{"@timestamp":"date","event.category":"keyword","process.name":"keyword","status":"long","file.path":"keyword"},"documents":[{"id":"a","@timestamp":"2026-01-01T00:00:00Z","event.category":"process","process.name":"CMD.EXE","status":400},{"id":"b","@timestamp":"2026-01-01T00:00:00Z","event.category":"process","process.name":"cmd.exe","status":500},{"id":"c","@timestamp":"2026-01-01T00:00:00Z","event.category":"process","process.name":"cmd.exe.bak","status":499},{"id":"d","@timestamp":"2026-01-01T00:00:00Z","event.category":"process","process.name":"agent.ExE","status":499},{"id":"e","@timestamp":"2026-01-01T00:00:00Z","event.category":"process","status":499}],"context":{"tiebreaker_field":"id"}}
```

```starter
any where true
```

```test
eq(eslesenler(),['a','d'],'gerçek endsWith~ ve [400,500)')
aday=[]
for i,(name,n,cat) in enumerate([('p.exe',399,'process'),('p.exe',400,'process'),('p.EXE',499,'process'),('p.exe',500,'process'),('p.exe.bak',400,'process'),('p.exe',400,'network')]):
    aday.append({'id':str(i),'@timestamp':'2026-01-01T00:00:00Z','process.name':name,'status':n,'event.category':cat})
eq(eslesenler(aday),['1','2'],'harf, son ek, iki uç, kategori karşı örnekleri')
```

```solution
process where endsWith~(process.name, ".exe") and status >= 400 and status < 500
```

```hint
endsWith~ yanında iki karşılaştırma ve process kategorisi gerekir.
```

:::

::: gorev Ayırıcı ile gerçek son eki ayır
file.path içinde /bin/ ile .exe ayırıcılarını harf duyarsız bul; çıkarılan değer tam küçük harf cmd olsun. Yol ayrıca harf duyarsız .exe ile bitsin; kategori process.

```meta
dil: eql
timeout: 60
```

```stdin
{"backend":"elastic","dil":"eql","mapping":{"@timestamp":"date","event.category":"keyword","process.name":"keyword","status":"long","file.path":"keyword"},"documents":[{"id":"a","@timestamp":"2026-01-01T00:00:00Z","event.category":"process","file.path":"/BIN/cmd.EXE"},{"id":"b","@timestamp":"2026-01-01T00:00:00Z","event.category":"process","file.path":"/bin/cmd.exe"},{"id":"c","@timestamp":"2026-01-01T00:00:00Z","event.category":"process","file.path":"/BIN/cmd.EXE.bak"},{"id":"d","@timestamp":"2026-01-01T00:00:00Z","event.category":"process","file.path":"/BIN/agent.EXE"},{"id":"e","@timestamp":"2026-01-01T00:00:00Z","event.category":"process"}],"context":{"tiebreaker_field":"id"}}
```

```starter
process where true
```

```test
eq(eslesenler(),['a','b'],'between~ ayırıcıları harf duyarsız; son ek ayrı koşul')
aday=[dict(korpus['documents'][0],id=str(i),**{'file.path':p}) for i,p in enumerate(['/BIN/cmd.EXE','/bin/CMD.exe','/BIN/cmd.EXE.bak','/BIN/cmd2.EXE','cmd.exe','/sbin/cmd.exe'])]
eq(eslesenler(aday),['0'],'çıkarılan değer karşılaştırması harf duyarlı; yanlış dizin ve son ek elenir')
```

```solution
process where between~(file.path, "/bin/", ".exe") == "cmd" and endsWith~(file.path, ".exe")
```

```hint
between~(...) == "cmd" çıkarılan değerin harfini korur.
```

:::
