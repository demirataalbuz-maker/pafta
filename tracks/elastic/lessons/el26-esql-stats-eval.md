---
id: el26
title: ES|QL: Filtre, EVAL ve STATS
summary: Sorgu dilini değiştirmeden taklit etmek yerine gerçek _query API’sini kullan.
---

::: anlat Gerçek ürün üzerinde çalışma
Kibana KQL bir filtre dilidir; `STATS` ekleyerek ES|QL'e dönüşmez. ES|QL
ayrı bir boru hattıdır ve bu derste doğrudan Elasticsearch `_query` API'sine
gider. `FROM pafta` bu tezgahın tek ad bağlamasıdır: her çalıştırmanın rastgele
geçici indeksine çevrilir. API anahtarının okuma yetkisi de yalnız o indekstir.
Diğer indeksleri, uzak cluster'ı veya haricî veri kaynağını kullanma.

`WHERE` önce satırları seçer, `STATS ... BY` gruplar, `EVAL` yeni sütun üretir.
`COUNT(*)` satırları sayar; `SUM(bytes)` sayısal alanı toplar. `bytes / 1024.0`
ondalıklı dönüşüm ister; tam sayı bölen farklı tür davranışı doğurabilir.
`SORT` olmadan sonuç sırasını sözleşme sanma. `KEEP` sütun sırasını açıklar.
Koşucu gerçek sütun adları/değerlerini gösterir; JSON yalnız taşıma biçimidir.

ES|QL'in çıktı satırı sınırı işlenen belge sayısı sınırı değildir. Büyük
sonuçlarda LIMIT/pagination ve sorgu planını ayrıca değerlendirmelisin; bu
tezgah en çok 100 belgeli öğretim korpusu kullanır. Kısmi API sonucu sessizce
tam rapor sayılmaz. Bu ders olay tanıkları sentetiktir; üretim kapasite testi değildir.

Bu bölüm **gerçek Elasticsearch/Kibana 9.5.5, Basic lisansı** kullanır; önce
[yerel laboratuvar yönergesini](../README.md) uygula. Girdi kutusunda
`backend: elastic` görünür. Önceki Lucene/yerel EQL motoruna sessiz dönüş yoktur.
Her çalıştırma yeni bir geçici indeks kullanır, iş bitince onu siler. Girdideki
`documents` ders tanıklarıdır; sorgu veya pipeline kodu editörde yazılır.
Alan adı, tür, eksik alan ve zaman aralığı sözleşmenin parçasıdır.

Kaynaklar: [STATS](https://www.elastic.co/docs/reference/query-languages/esql/commands/stats-by), [ES|QL API](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-esql-query), [Limitations](https://www.elastic.co/docs/reference/query-languages/esql/limitations).
:::

::: tahmin Önce çıktıyı düşün
399/400/499/500 sınırları sayım ve toplamı nasıl etkiler?

```meta
dil: esql
timeout: 60
```

```esql
FROM pafta | WHERE status >= 400 AND status < 500 | STATS adet = COUNT(*), toplam = SUM(bytes) BY user.name | SORT user.name | KEEP user.name, adet, toplam
```

```stdin
{"backend":"elastic","dil":"esql","mapping":{"@timestamp":"date","status":"long","user.name":"keyword","bytes":"long","tags":"keyword"},"documents":[{"id":"a","@timestamp":"2026-01-01T00:00:00Z","status":399,"user.name":"alice","bytes":10},{"id":"b","@timestamp":"2026-01-01T00:00:01Z","status":400,"user.name":"alice","bytes":20},{"id":"c","@timestamp":"2026-01-01T00:00:02Z","status":499,"user.name":"alice","bytes":30},{"id":"d","@timestamp":"2026-01-01T00:00:03Z","status":500,"user.name":"bob","bytes":40},{"id":"e","@timestamp":"2026-01-01T00:00:04Z","status":401,"user.name":"bob","bytes":50}]}
```

???
Gerçek API ile doğrulanmış çıktı:

```text
{"columns":["user.name","adet","toplam"],"values":[["alice",2,50],["bob",1,50]]}
```

:::

::: gorev Kullanıcı başına hata trafiği
status [400,500) satırlarını filtrele. user.name başına adet=COUNT(*) ve toplam=SUM(bytes) üret; kullanıcıya göre sırala ve yalnız user.name, adet, toplam sütunlarını bu sırada döndür.

```meta
dil: esql
timeout: 60
```

```stdin
{"backend":"elastic","dil":"esql","mapping":{"@timestamp":"date","status":"long","user.name":"keyword","bytes":"long","tags":"keyword"},"documents":[{"id":"a","@timestamp":"2026-01-01T00:00:00Z","status":399,"user.name":"alice","bytes":10},{"id":"b","@timestamp":"2026-01-01T00:00:01Z","status":400,"user.name":"alice","bytes":20},{"id":"c","@timestamp":"2026-01-01T00:00:02Z","status":499,"user.name":"alice","bytes":30},{"id":"d","@timestamp":"2026-01-01T00:00:03Z","status":500,"user.name":"bob","bytes":40},{"id":"e","@timestamp":"2026-01-01T00:00:04Z","status":401,"user.name":"bob","bytes":50}]}
```

```starter
FROM pafta | STATS adet = COUNT(*)
```

```test
eq(sonuc(),{'columns':['user.name','adet','toplam'],'values':[['alice',2,50],['bob',1,50]]}, 'gruplar ve iki uç')
aday=[dict(d,bytes=d['bytes']*2,**{'user.name':'x_'+d['user.name']}) for d in korpus['documents']]
eq(sonuc(aday),{'columns':['user.name','adet','toplam'],'values':[['x_alice',2,100],['x_bob',1,100]]}, 'veriden gerçek toplam ve grup')
eksik=dict(korpus['documents'][1],id='olcum_yok'); eksik.pop('bytes')
eq(sonuc(korpus['documents']+[eksik])['values'], [['alice',3,50],['bob',1,50]], 'COUNT(*) ölçüm yokluğunu atmaz')
ters=[dict(d,**{'user.name':'z_alice' if d['user.name']=='alice' else 'a_bob'}) for d in korpus['documents']]
eq(sonuc(ters)['values'], [['a_bob',1,50],['z_alice',2,50]], 'kaynak sırası sonuç sırası değildir')
```

```solution
FROM pafta | WHERE status >= 400 AND status < 500 | STATS adet = COUNT(*), toplam = SUM(bytes) BY user.name | SORT user.name | KEEP user.name, adet, toplam
```

```hint
WHERE agregasyondan önce; SORT ve KEEP sonucu belirgin yapar.
```

:::

::: gorev KiB raporu ve boş girdi
bytes değerinden kib=bytes/1024.0 üret. Aynı status filtresiyle BY kullanmadan adet=COUNT(*) ve toplam_kib=SUM(kib) döndür; sütun sırası adet, toplam_kib.

```meta
dil: esql
timeout: 60
```

```stdin
{"backend":"elastic","dil":"esql","mapping":{"@timestamp":"date","status":"long","user.name":"keyword","bytes":"long","tags":"keyword"},"documents":[{"id":"a","@timestamp":"2026-01-01T00:00:00Z","status":399,"user.name":"alice","bytes":10},{"id":"b","@timestamp":"2026-01-01T00:00:01Z","status":400,"user.name":"alice","bytes":20},{"id":"c","@timestamp":"2026-01-01T00:00:02Z","status":499,"user.name":"alice","bytes":30},{"id":"d","@timestamp":"2026-01-01T00:00:03Z","status":500,"user.name":"bob","bytes":40},{"id":"e","@timestamp":"2026-01-01T00:00:04Z","status":401,"user.name":"bob","bytes":50}]}
```

```starter
FROM pafta | STATS adet = COUNT(*)
```

```test
eq(sonuc(),{'columns':['adet','toplam_kib'],'values':[[3,100/1024.0]]}, 'EVAL ondalıklı bölme ve STATS')
aday=[dict(d,bytes=1024) for d in korpus['documents']]
eq(sonuc(aday),{'columns':['adet','toplam_kib'],'values':[[3,3.0]]}, 'sabit çıktı ve tamsayı bölmesi olmaz')
eksik=dict(korpus['documents'][1],id='olcum_yok'); eksik.pop('bytes')
eq(sonuc(korpus['documents']+[eksik])['values'], [[4,100/1024.0]], 'eksik ölçüm satırı sayılır')
eq(sonuc([]),{'columns':['adet','toplam_kib'],'values':[[0,None]]}, 'BY yok, boş veride tek satır ve null toplam')
```

```solution
FROM pafta | EVAL kib = bytes / 1024.0 | WHERE status >= 400 AND status < 500 | STATS adet = COUNT(*), toplam_kib = SUM(kib) | KEEP adet, toplam_kib
```

```hint
Ondalıklı bölen, BY olmadan STATS ve açık KEEP kullan.
```

:::
