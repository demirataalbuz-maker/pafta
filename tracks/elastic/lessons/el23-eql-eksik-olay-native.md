---
id: el23
title: EQL Dizileri: Ürünle Karşılaştır
summary: Anahtar, maxspan, until ve baştaki eksik olayı gerçek ürünle sınırla.
---

::: anlat Gerçek ürün üzerinde çalışma
Yerel alt kümenin açıkça reddettiği **baştaki eksik olay**, bu derste gerçek
Elasticsearch tarafından çalıştırılır. `![...]` bir başlatıcı olay üretmez;
olumlu olay etrafındaki `maxspan` penceresinde o koşula uyan olayın yokluğunu
ister. Bu, kurumda hiç process kaydı olmadığı anlamına gelmez: yalnız girilen
veri, alan eşlemesi, filtre ve zaman penceresi içinde yoktur.

`sequence by host.id` farklı makineleri karıştırmaz. `with maxspan=1m`
tam 60 saniyeyi kabul eder; 60001 ms kabul edilmez. `until` bekleyen olumlu
diziyi sonlandırır. İlk görevde until vardır; ikinci görevde yoktur ve eksik
start koşulunun yerini tutmaz. Verinin dosyadaki sırası yerine timestamp ve
tiebreaker kullanılır. Eşit tarihli olaylara belirsiz sıra bırakma.

Koşucu raw EQL yanıtındaki eksik aşamaları bir belge kimliği gibi yazmaz;
çıktı yalnız gerçek olumlu olay kimlikleridir. API yanıtında timeout, partial
veya running durumu varsa kesin sonuç gösterilmez. Önceki yerel EQL tahminlerini
aynı mapping/veriyle gerçek API'de ölçen kabul testi de teslimdedir.

Bu bölüm **gerçek Elasticsearch/Kibana 9.5.5, Basic lisansı** kullanır; önce
[yerel laboratuvar yönergesini](../README.md) uygula. Girdi kutusunda
`backend: elastic` görünür. Önceki Lucene/yerel EQL motoruna sessiz dönüş yoktur.
Her çalıştırma yeni bir geçici indeks kullanır, iş bitince onu siler. Girdideki
`documents` ders tanıklarıdır; sorgu veya pipeline kodu editörde yazılır.
Alan adı, tür, eksik alan ve zaman aralığı sözleşmenin parçasıdır.

Kaynaklar: [EQL syntax / missing events](https://www.elastic.co/docs/reference/query-languages/eql/eql-syntax), [EQL API](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-eql-search).
:::

::: tahmin Önce çıktıyı düşün
Eşit uçtaki n1 kalır mı; sonlandırılmış h5 dizisi ne olur?

```meta
dil: eql
timeout: 60
```

```eql
sequence by host.id with maxspan=1m
  [process where event.action == "start"]
  [network where destination.port == 443]
until [process where event.action == "end"]
```

```stdin
{"backend":"elastic","dil":"eql","mapping":{"@timestamp":"date","event.category":"keyword","event.action":"keyword","host.id":"keyword","destination.port":"long","event.sequence":"long"},"documents":[{"id":"s1","@timestamp":"2026-01-01T00:00:00.000Z","event.category":"process","event.action":"start","host.id":"h1","destination.port":0,"event.sequence":0},{"id":"n1","@timestamp":"2026-01-01T00:01:00.000Z","event.category":"network","event.action":"connect","host.id":"h1","destination.port":443,"event.sequence":60000},{"id":"n2","@timestamp":"2026-01-01T00:01:00.000Z","event.category":"network","event.action":"connect","host.id":"h2","destination.port":443,"event.sequence":60000},{"id":"s3","@timestamp":"2026-01-01T00:00:00.000Z","event.category":"process","event.action":"start","host.id":"h3","destination.port":0,"event.sequence":0},{"id":"n3","@timestamp":"2026-01-01T00:01:00.001Z","event.category":"network","event.action":"connect","host.id":"h3","destination.port":443,"event.sequence":60001},{"id":"n4","@timestamp":"2026-01-01T00:01:00.000Z","event.category":"network","event.action":"connect","host.id":"h4","destination.port":80,"event.sequence":60000},{"id":"s5","@timestamp":"2026-01-01T00:00:00.000Z","event.category":"process","event.action":"start","host.id":"h5","destination.port":0,"event.sequence":0},{"id":"end5","@timestamp":"2026-01-01T00:00:01.000Z","event.category":"process","event.action":"end","host.id":"h5","destination.port":0,"event.sequence":1000},{"id":"n5","@timestamp":"2026-01-01T00:00:02.000Z","event.category":"network","event.action":"connect","host.id":"h5","destination.port":443,"event.sequence":2000},{"id":"s6","@timestamp":"2026-01-01T00:00:00.000Z","event.category":"process","event.action":"start","host.id":"h6","destination.port":0,"event.sequence":0},{"id":"end6","@timestamp":"2026-01-01T00:00:01.000Z","event.category":"process","event.action":"END","host.id":"h6","destination.port":0,"event.sequence":1000},{"id":"n6","@timestamp":"2026-01-01T00:00:02.000Z","event.category":"network","event.action":"connect","host.id":"h6","destination.port":443,"event.sequence":2000},{"id":"s7","@timestamp":"2026-01-01T00:00:00.000Z","event.category":"process","event.action":"START","host.id":"h7","destination.port":0,"event.sequence":0},{"id":"n7","@timestamp":"2026-01-01T00:00:02.000Z","event.category":"network","event.action":"connect","host.id":"h7","destination.port":443,"event.sequence":2000}],"context":{"tiebreaker_field":"event.sequence"}}
```

???
Gerçek API ile doğrulanmış çıktı:

```text
s6 -> n6
s1 -> n1
```

:::

::: gorev Yerel sözleşmeyi üründe kanıtla
Aynı host altında start→443 bağlantısını en çok 1 dakika içinde ilişkilendir; end olayı bekleyen diziyi iptal etsin.

```meta
dil: eql
timeout: 60
```

```stdin
{"backend":"elastic","dil":"eql","mapping":{"@timestamp":"date","event.category":"keyword","event.action":"keyword","host.id":"keyword","destination.port":"long","event.sequence":"long"},"documents":[{"id":"s1","@timestamp":"2026-01-01T00:00:00.000Z","event.category":"process","event.action":"start","host.id":"h1","destination.port":0,"event.sequence":0},{"id":"n1","@timestamp":"2026-01-01T00:01:00.000Z","event.category":"network","event.action":"connect","host.id":"h1","destination.port":443,"event.sequence":60000},{"id":"n2","@timestamp":"2026-01-01T00:01:00.000Z","event.category":"network","event.action":"connect","host.id":"h2","destination.port":443,"event.sequence":60000},{"id":"s3","@timestamp":"2026-01-01T00:00:00.000Z","event.category":"process","event.action":"start","host.id":"h3","destination.port":0,"event.sequence":0},{"id":"n3","@timestamp":"2026-01-01T00:01:00.001Z","event.category":"network","event.action":"connect","host.id":"h3","destination.port":443,"event.sequence":60001},{"id":"n4","@timestamp":"2026-01-01T00:01:00.000Z","event.category":"network","event.action":"connect","host.id":"h4","destination.port":80,"event.sequence":60000},{"id":"s5","@timestamp":"2026-01-01T00:00:00.000Z","event.category":"process","event.action":"start","host.id":"h5","destination.port":0,"event.sequence":0},{"id":"end5","@timestamp":"2026-01-01T00:00:01.000Z","event.category":"process","event.action":"end","host.id":"h5","destination.port":0,"event.sequence":1000},{"id":"n5","@timestamp":"2026-01-01T00:00:02.000Z","event.category":"network","event.action":"connect","host.id":"h5","destination.port":443,"event.sequence":2000},{"id":"s6","@timestamp":"2026-01-01T00:00:00.000Z","event.category":"process","event.action":"start","host.id":"h6","destination.port":0,"event.sequence":0},{"id":"end6","@timestamp":"2026-01-01T00:00:01.000Z","event.category":"process","event.action":"END","host.id":"h6","destination.port":0,"event.sequence":1000},{"id":"n6","@timestamp":"2026-01-01T00:00:02.000Z","event.category":"network","event.action":"connect","host.id":"h6","destination.port":443,"event.sequence":2000},{"id":"s7","@timestamp":"2026-01-01T00:00:00.000Z","event.category":"process","event.action":"START","host.id":"h7","destination.port":0,"event.sequence":0},{"id":"n7","@timestamp":"2026-01-01T00:00:02.000Z","event.category":"network","event.action":"connect","host.id":"h7","destination.port":443,"event.sequence":2000}],"context":{"tiebreaker_field":"event.sequence"}}
```

```starter
sequence [process where true] [network where true]
```

```test
eq(eslesenler(),[['s6','n6'],['s1','n1']],'maxspan eşit uç, anahtar ve until')
aday=[]
for i,delta in enumerate([59999,60000,60001]):
    from datetime import datetime,timezone,timedelta
    a=dict(korpus['documents'][0],id='s'+str(i),**{'host.id':'x'+str(i)})
    ts=(datetime(2026,1,1,tzinfo=timezone.utc)+timedelta(milliseconds=delta)).isoformat(timespec='milliseconds').replace('+00:00','Z')
    b=dict(korpus['documents'][1],id='n'+str(i),**{'host.id':'x'+str(i),'@timestamp':ts})
    aday += [a,b]
eq(eslesenler(aday),[['s0','n0'],['s1','n1']],'bir milisaniye alt/eşit/üst gerçek backend')
```

```solution
sequence by host.id with maxspan=1m
  [process where event.action == "start"]
  [network where destination.port == 443]
until [process where event.action == "end"]
```

```hint
by host.id, maxspan=1m ve until process/end birlikte gerekir.
```

:::

::: gorev Baştaki eksik start
Host başına, önceki en çok 1 dakika içinde start olmadan gelen network/443 bağlantısını bul. Baştaki aşama eksik olay olsun.

```meta
dil: eql
timeout: 60
```

```stdin
{"backend":"elastic","dil":"eql","mapping":{"@timestamp":"date","event.category":"keyword","event.action":"keyword","host.id":"keyword","destination.port":"long","event.sequence":"long"},"documents":[{"id":"s1","@timestamp":"2026-01-01T00:00:00.000Z","event.category":"process","event.action":"start","host.id":"h1","destination.port":0,"event.sequence":0},{"id":"n1","@timestamp":"2026-01-01T00:01:00.000Z","event.category":"network","event.action":"connect","host.id":"h1","destination.port":443,"event.sequence":60000},{"id":"n2","@timestamp":"2026-01-01T00:01:00.000Z","event.category":"network","event.action":"connect","host.id":"h2","destination.port":443,"event.sequence":60000},{"id":"s3","@timestamp":"2026-01-01T00:00:00.000Z","event.category":"process","event.action":"start","host.id":"h3","destination.port":0,"event.sequence":0},{"id":"n3","@timestamp":"2026-01-01T00:01:00.001Z","event.category":"network","event.action":"connect","host.id":"h3","destination.port":443,"event.sequence":60001},{"id":"n4","@timestamp":"2026-01-01T00:01:00.000Z","event.category":"network","event.action":"connect","host.id":"h4","destination.port":80,"event.sequence":60000},{"id":"s5","@timestamp":"2026-01-01T00:00:00.000Z","event.category":"process","event.action":"start","host.id":"h5","destination.port":0,"event.sequence":0},{"id":"end5","@timestamp":"2026-01-01T00:00:01.000Z","event.category":"process","event.action":"end","host.id":"h5","destination.port":0,"event.sequence":1000},{"id":"n5","@timestamp":"2026-01-01T00:00:02.000Z","event.category":"network","event.action":"connect","host.id":"h5","destination.port":443,"event.sequence":2000},{"id":"s6","@timestamp":"2026-01-01T00:00:00.000Z","event.category":"process","event.action":"start","host.id":"h6","destination.port":0,"event.sequence":0},{"id":"end6","@timestamp":"2026-01-01T00:00:01.000Z","event.category":"process","event.action":"END","host.id":"h6","destination.port":0,"event.sequence":1000},{"id":"n6","@timestamp":"2026-01-01T00:00:02.000Z","event.category":"network","event.action":"connect","host.id":"h6","destination.port":443,"event.sequence":2000},{"id":"s7","@timestamp":"2026-01-01T00:00:00.000Z","event.category":"process","event.action":"START","host.id":"h7","destination.port":0,"event.sequence":0},{"id":"n7","@timestamp":"2026-01-01T00:00:02.000Z","event.category":"network","event.action":"connect","host.id":"h7","destination.port":443,"event.sequence":2000}],"context":{"tiebreaker_field":"event.sequence"}}
```

```starter
network where destination.port == 443
```

```test
eq(eslesenler(),[['n7'],['n2'],['n3']],'öncesinde pencere içinde start bulunmayan bağlantılar; until burada yok')
aday=[dict(korpus['documents'][1],id='yalniz',**{'host.id':'tek'})]
eq(eslesenler(aday),[['yalniz']],'gerçek baştaki eksik olay desteklenir')
aday.append(dict(korpus['documents'][0],id='baslangic',**{'host.id':'tek'}))
eq(eslesenler(aday),[],'tam 60 saniye önceki start eksik olay koşulunu bozar')
aday[0]['@timestamp']='2026-01-01T00:01:00.001Z'
eq(eslesenler(aday),[['yalniz']],'bir milisaniye dışarıdaki start pencereyi bozmaz')
```

```solution
sequence by host.id with maxspan=1m
  ![process where event.action == "start"]
  [network where destination.port == 443]
```

```hint
Gerçek EQL ![process where ...] aşamasını maxspan ile kullan.
```

:::
