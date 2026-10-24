---
id: el27
title: Proje · Çok Değer ve Eksik Ölçüm
summary: Null, boş metin, çok değerli grup ve gerçek rapor sözleşmesini birleştir.
---

::: anlat Gerçek ürün üzerinde çalışma
Tek bir belge `tags: [red, blue]` ile iki gruba katkı yapabilir. Bu nedenle
grup sayımlarını toplayıp kaynak belge sayısı sandığında çift sayarsın.
`COUNT(*)` satır/katkıyı, `COUNT(bytes)` null olmayan ölçümü sayar; sıfır gerçek
bir ölçümdür. Boş dizi ve eksik alan indekste değer üretmeyebilir. Bu görevde
null grubu açık sıralamayla görünür yap; rastgele sonuç sırası bekleme.

İkinci rapor `COALESCE` ile kullanıcı yokluğunu `bilinmiyor` yapar. Boş metin
null değildir; bilinmeyen kullanıcı sayısını büyütmek için sessizce eşitleme.
Veri toplama aşamasında alan türünü ve yokluk anlamını kararlaştırmak raporun
doğruluğunu belirler. Çalışan sorgu güvenilir rapor demek değildir: payda,
ölçüm eksiği ve çok değerli katkıyı açıklayabilmelisin.

Teslim kaydında kaynak dosya/üretici, ingest pipeline, mapping, sorgu, ürün
sürümü ve zaman aralığını birlikte sakla. EL20'nin gerçek süreç gözlemi ile
buradaki sentetik sınır korpusunu aynı kaynak türü diye sunma. Bu son projede
iki raporu gerçek ES|QL motoru çalıştırır; Python yalnız test beklentilerini
karşılaştırır, toplama işlemini kendisi yapmaz.

Bu bölüm **gerçek Elasticsearch/Kibana 9.5.5, Basic lisansı** kullanır; önce
[yerel laboratuvar yönergesini](../README.md) uygula. Girdi kutusunda
`backend: elastic` görünür. Önceki Lucene/yerel EQL motoruna sessiz dönüş yoktur.
Her çalıştırma yeni bir geçici indeks kullanır, iş bitince onu siler. Girdideki
`documents` ders tanıklarıdır; sorgu veya pipeline kodu editörde yazılır.
Alan adı, tür, eksik alan ve zaman aralığı sözleşmenin parçasıdır.

Kaynaklar: [STATS / multivalued grouping](https://www.elastic.co/docs/reference/query-languages/esql/commands/stats-by), [COUNT](https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/aggregation-functions), [COALESCE](https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/conditional-functions-and-expressions).
:::

::: tahmin Önce çıktıyı düşün
Tek a belgesi iki gruba giderse sayımların toplamı belge sayısına eşit mi?

```meta
dil: esql
timeout: 60
```

```esql
FROM pafta | STATS satir = COUNT(*), olcum = COUNT(bytes), toplam = SUM(bytes) BY tags | SORT tags ASC NULLS FIRST | KEEP tags, satir, olcum, toplam
```

```stdin
{"backend":"elastic","dil":"esql","mapping":{"@timestamp":"date","status":"long","user.name":"keyword","bytes":"long","tags":"keyword"},"documents":[{"id":"a","user.name":"alice","bytes":10,"tags":["red","blue"]},{"id":"b","user.name":"bob","tags":["blue"]},{"id":"c","bytes":0},{"id":"d","user.name":"alice","bytes":20,"tags":["red"]},{"id":"e","user.name":null,"bytes":null,"tags":[]}]}
```

???
Gerçek API ile doğrulanmış çıktı:

```text
{"columns":["tags","satir","olcum","toplam"],"values":[[null,2,1,0],["blue",2,1,10],["red",2,2,30]]}
```

:::

::: gorev Etiket başına katkıyı raporla
tags başına satir=COUNT(*), olcum=COUNT(bytes), toplam=SUM(bytes) üret. tags artan, null önce; yalnız tags,satir,olcum,toplam döndür.

```meta
dil: esql
timeout: 60
```

```stdin
{"backend":"elastic","dil":"esql","mapping":{"@timestamp":"date","status":"long","user.name":"keyword","bytes":"long","tags":"keyword"},"documents":[{"id":"a","user.name":"alice","bytes":10,"tags":["red","blue"]},{"id":"b","user.name":"bob","tags":["blue"]},{"id":"c","bytes":0},{"id":"d","user.name":"alice","bytes":20,"tags":["red"]},{"id":"e","user.name":null,"bytes":null,"tags":[]}]}
```

```starter
FROM pafta | STATS satir = COUNT(*)
```

```test
eq(sonuc(),{'columns':['tags','satir','olcum','toplam'],'values':[[None,2,1,0],['blue',2,1,10],['red',2,2,30]]}, 'çok değerli grup, null ve iki sayım')
aday=[dict(d) for d in korpus['documents']]
aday[0]['bytes']=11
eq(sonuc(aday)['values'], [[None,2,1,0],['blue',2,1,11],['red',2,2,31]], 'bir belge iki grubu etkiler')
eq(sonuc([])['values'], [], 'BY ile boş veri grup üretmez')
ters=[{'id':str(i),'tags':[n],'bytes':i} for i,n in enumerate(['z','a','m'])]
eq(sonuc(ters)['values'], [['a',1,1,1],['m',1,1,2],['z',1,1,0]], 'SORT kaldırılırsa girdi sırası yanlış kalır')
```

```solution
FROM pafta | STATS satir = COUNT(*), olcum = COUNT(bytes), toplam = SUM(bytes) BY tags | SORT tags ASC NULLS FIRST | KEEP tags, satir, olcum, toplam
```

```hint
Çok değerli gruplamayı ürüne bırak; SORT tags ASC NULLS FIRST açık olsun.
```

:::

::: gorev Kullanıcı yokluğunu koruyarak özetle
kisi=COALESCE(user.name,"bilinmiyor") üret; kisi başına adet=COUNT(*) ve olcum=COUNT(bytes). kisi artan sırada; yalnız kisi,adet,olcum.

```meta
dil: esql
timeout: 60
```

```stdin
{"backend":"elastic","dil":"esql","mapping":{"@timestamp":"date","status":"long","user.name":"keyword","bytes":"long","tags":"keyword"},"documents":[{"id":"a","user.name":"alice","bytes":10,"tags":["red","blue"]},{"id":"b","user.name":"bob","tags":["blue"]},{"id":"c","bytes":0},{"id":"d","user.name":"alice","bytes":20,"tags":["red"]},{"id":"e","user.name":null,"bytes":null,"tags":[]}]}
```

```starter
FROM pafta | STATS adet = COUNT(*)
```

```test
eq(sonuc(),{'columns':['kisi','adet','olcum'],'values':[['alice',2,2],['bilinmiyor',2,1],['bob',1,0]]}, 'null ve eksik aynı yedek gruba; ölçüm sayısı ayrı')
aday=[dict(d) for d in korpus['documents']]
aday[2]['user.name']=''; aday[4]['user.name']='svc'
eq(sonuc(aday)['values'], [['',1,1],['alice',2,2],['bob',1,0],['svc',1,0]], 'boş metin null değildir, coalesce onu değiştirmez')
```

```solution
FROM pafta | EVAL kisi = COALESCE(user.name, "bilinmiyor") | STATS adet = COUNT(*), olcum = COUNT(bytes) BY kisi | SORT kisi | KEEP kisi, adet, olcum
```

```hint
Boş metni null sanma; COUNT(bytes) ölçüm eksikliğini gösterir.
```

:::
