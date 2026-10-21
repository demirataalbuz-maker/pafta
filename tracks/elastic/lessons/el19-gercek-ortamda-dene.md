---
id: el19
title: Gerçek Ortamda Dene · Elastic Laboratuvarı
summary: Aynı mapping, corpus ve sorguları ücretsiz yerel Elasticsearch/Kibana üzerinde karşılaştır.
---

::: anlat Yerel kurulum ve Basic lisansı
Pafta'nın Lucene tabanlı KQL/Lucene tezgahı ve sınırlı EQL yorumlayıcısı, Elasticsearch sunucusu değildir. Son adımda aynı sorguları gerçek ürüne taşı. Kendi bilgisayarında [resmî Windows Elasticsearch ZIP kurulumu](https://www.elastic.co/docs/deploy-manage/deploy/self-managed/install-elasticsearch-with-zip-on-windows) ve [aynı sürüm Kibana ZIP kurulumu](https://www.elastic.co/docs/deploy-manage/deploy/self-managed/install-kibana-on-windows) yönergelerini uygula. İndirilen arşivlerin yayımlanmış SHA-512 değerlerini denetle. Elasticsearch paketi kendi JDK'sını içerir.

Bu çalışma için ücretli abonelik veya Elastic Cloud gerekmez. Yeni, yerel kurulumda `config/elasticsearch.yml` içindeki `xpack.license.self_generated.type: basic` ücretsiz Basic lisansını seçer; bu zaten varsayılandır. Deneme lisansı açmak gerekmez. [Lisans ayarı](https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/license-settings) ve sürümünün özellik tablosunu kontrol et.

İlk Elasticsearch açılışında üretilen `elastic` parolasını ve Kibana enrollment token'ını kendi bilgisayarında sakla. Kibana'yı token ile eşleştir; token süresi dolarsa resmî yönergedeki `elasticsearch-create-enrollment-token -s kibana` aracını kullan. Yerel laboratuvarı `127.0.0.1` üzerinde tut: Elasticsearch `http.host` ve `transport.host` ayarları ile Kibana `server.host` değerini kontrol et. Otomatik üretilen TLS ve kimlik doğrulama ayarlarını koru. Kibana'da oturum açıp **Dev Tools → Console** bölümünü aç.
:::

::: anlat Aynı mapping ve aynı altı belge
Aşağıdaki istekler yalnız bu dersin yeni `pafta-el19` indeksini oluşturur. Önceden aynı isimde indeks varsa başka yeni ad seç ve bütün isteklerde onu kullan. `dynamic: strict` yanlış alan adını yakalar. Pafta'daki düz `event.category` alanı Elasticsearch'te `event` nesnesinin `category` alt alanıdır; iki gösterim aynı alan yoluna karşılık gelir.

```text
PUT pafta-el19
{
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "id": {"type": "keyword"},
      "@timestamp": {"type": "date"},
      "event": {"properties": {"category": {"type": "keyword"}}},
      "process": {"properties": {"name": {"type": "keyword"}}},
      "status": {"type": "integer", "coerce": false},
      "message": {"type": "text", "analyzer": "standard"}
    }
  }
}

POST pafta-el19/_bulk?refresh=true
{"index":{"_id":"a"}}
{"id":"a","@timestamp":"2026-01-01T00:00:00Z","event.category":"process","process.name":"cmd.exe","status":400,"message":"Login failed"}
{"index":{"_id":"b"}}
{"id":"b","@timestamp":"2026-01-01T00:00:01Z","event.category":"network","process.name":"cmd.exe","status":499,"message":"Login has failed"}
{"index":{"_id":"c"}}
{"id":"c","@timestamp":"2026-01-01T00:00:02Z","event.category":"process","process.name":"CMD.EXE","status":500,"message":"Login failed"}
{"index":{"_id":"d"}}
{"id":"d","@timestamp":"2026-01-01T00:00:03Z","event.category":"process","process.name":"cmd.exe","status":399,"message":"Failed login"}
{"index":{"_id":"e"}}
{"id":"e","@timestamp":"2026-01-01T00:00:04Z","event.category":"process","process.name":"powershell.exe","status":499,"message":"Login too many failed"}
{"index":{"_id":"f"}}
{"id":"f","@timestamp":"2026-01-01T00:00:05Z","event.category":"process","process.name":"CMD.EXE","status":499,"message":"login failed"}

```

Bulk yanıtında `errors: false` ve altı başarılı öğe gör. Ardından `GET pafta-el19/_count` sonucu 6 olmalı. Bir belge hatalıysa eşleştirmeye geçmeden mapping/girdi hatasını düzelt.
:::

::: anlat Üç dilde gerçek karşılaştırma
Kibana'da `pafta-el19` veri görünümünü oluştur, zaman alanı olarak `@timestamp` seç. Discover zaman seçicisini **2026-01-01T00:00:00Z dahil → 2026-01-01T00:00:06Z hariç** aralığına getir; aralık dışındaki kayıtların sorgudan bağımsız elendiğini unutma. KQL modunda şu sorguyu yaz:

```kibana norun
event.category: process AND process.name: cmd.exe AND status >= 400 AND status < 500
```

Yalnız `a` beklenir: keyword `cmd.exe`, `CMD.EXE` ile eşleşmez. Ardından aynı sorgu çubuğunu Lucene moduna geçir:

```lucene norun
message:"login failed"~1 AND status:[400 TO 500}
```

Kimlik kümesi `a,b,f` olur. Discover varsayılan sırasını Pafta'nın kaynak listesi sırasıyla karıştırma; kimlik kümesini karşılaştır. Console'da aynı Lucene sorgusu için JSON kaçışını kullan:

```text
POST pafta-el19/_search
{
  "size": 100,
  "sort": [{"@timestamp":"asc"},{"id":"asc"}],
  "query": {"query_string": {"query": "message:\"login failed\"~1 AND status:[400 TO 500}", "analyze_wildcard": false}}
}
```

EQL, Discover KQL kutusunda çalıştırılmaz. Console'da EQL API'sini kullan:

```text
POST pafta-el19/_eql/search
{
  "query": "process where process.name : \"cmd.exe\" and status >= 400 and status < 500",
  "timestamp_field": "@timestamp",
  "event_category_field": "event.category",
  "tiebreaker_field": "id",
  "size": 100
}
```

`hits.events` içinde zaman sırasıyla `a,f` beklenir. `:` harf farkını göz ardı eder; `== "cmd.exe"` yazınca yalnız `a` kalır. EL15–EL18 sequence sorgularını da kendi ders mapping/verisiyle aynı API'de dene; `hits.sequences` ile kimlik dizilerini karşılaştır.

Fark çıkarsa ürün/Lucene sürümünü, mapping ve analyzer'ı, zaman aralığını, tam sorguyu ve kimlikleri kaydet. Ürün sorgusunun kabul ettiği bir özellik Pafta'da açıkça reddedilebilir. Pafta sıralaması, skorlar, shard yapısı ve dağıtık yürütme için ürün garantisi vermez. Buradaki gerçek ortam işlemleri kullanıcı tarafından yapılır; Pafta yerel Elastic'i kendiliğinden kurmaz veya bu sayfada canlı bağlantı doğrulaması yapmaz.
:::

::: tahmin
Aynı altı belge aşağıdaki tezgah girdisinde. Status alt ucu 400 dahil, üst ucu 500 hariçtir. `message` standard analyzer kullanır. Sorgunun verdiği kimlikleri tezgahın kaynak listesi sırasıyla, her satıra bir tane yaz.

```meta
dil: lucene
timeout: 90
```

```stdin
{"dil":"lucene","mapping":{"id":{"type":"keyword"},"@timestamp":{"type":"date"},"event.category":{"type":"keyword"},"process.name":{"type":"keyword"},"status":{"type":"integer"},"message":{"type":"text"}},"documents":[{"id":"a","@timestamp":"2026-01-01T00:00:00Z","event.category":"process","process.name":"cmd.exe","status":400,"message":"Login failed"},{"id":"b","@timestamp":"2026-01-01T00:00:01Z","event.category":"network","process.name":"cmd.exe","status":499,"message":"Login has failed"},{"id":"c","@timestamp":"2026-01-01T00:00:02Z","event.category":"process","process.name":"CMD.EXE","status":500,"message":"Login failed"},{"id":"d","@timestamp":"2026-01-01T00:00:03Z","event.category":"process","process.name":"cmd.exe","status":399,"message":"Failed login"},{"id":"e","@timestamp":"2026-01-01T00:00:04Z","event.category":"process","process.name":"powershell.exe","status":499,"message":"Login too many failed"},{"id":"f","@timestamp":"2026-01-01T00:00:05Z","event.category":"process","process.name":"CMD.EXE","status":499,"message":"login failed"}],"context":{}}
```

```lucene
message:"login failed"~1 AND status:[400 TO 500}
```

???

Öbek `login failed` sıralı olarak bitişikse veya arada tek terim varsa geçer. `a` bitişik, `b` bir aralıklı, `f` bitişiktir. `c` üst uç 500, `d` 399, `e` ise iki aradaki terim nedeniyle elenir.

```text
a
b
f
```

:::

::: gorev KQL sözleşmesini gerçek ürüne taşı
Process kategorisinde, keyword process.name tam cmd.exe ve 400 dahil–500 hariç status iste. Harf farkını koru.

```meta
dil: kibana
timeout: 90
```

```stdin
{"dil":"kibana","mapping":{"id":{"type":"keyword"},"@timestamp":{"type":"date"},"event.category":{"type":"keyword"},"process.name":{"type":"keyword"},"status":{"type":"integer"},"message":{"type":"text"}},"documents":[{"id":"a","@timestamp":"2026-01-01T00:00:00Z","event.category":"process","process.name":"cmd.exe","status":400,"message":"Login failed"},{"id":"b","@timestamp":"2026-01-01T00:00:01Z","event.category":"network","process.name":"cmd.exe","status":499,"message":"Login has failed"},{"id":"c","@timestamp":"2026-01-01T00:00:02Z","event.category":"process","process.name":"CMD.EXE","status":500,"message":"Login failed"},{"id":"d","@timestamp":"2026-01-01T00:00:03Z","event.category":"process","process.name":"cmd.exe","status":399,"message":"Failed login"},{"id":"e","@timestamp":"2026-01-01T00:00:04Z","event.category":"process","process.name":"powershell.exe","status":499,"message":"Login too many failed"},{"id":"f","@timestamp":"2026-01-01T00:00:05Z","event.category":"process","process.name":"CMD.EXE","status":499,"message":"login failed"}],"context":{}}
```

```starter
status: *
```

```test
eq(eslesenler(), ["a"], "asıl kimlikler")
from copy import deepcopy
veri = deepcopy(korpus)
for d in veri["documents"]:
    d["id"] = "yeni_" + d["id"]
eq(eslesenler(veri), ["yeni_a"], "kimlikler ezberlenmez")
aday = [dict(korpus["documents"][0], id="alt", status=400), dict(korpus["documents"][0], id="alt_disi", status=399), dict(korpus["documents"][0], id="ust", status=499), dict(korpus["documents"][0], id="ust_disi", status=500), dict(korpus["documents"][0], id="kategori", **{"event.category":"network"}), dict(korpus["documents"][0], id="harf", **{"process.name":"CMD.EXE"}), dict(korpus["documents"][0], id="diger", **{"process.name":"powershell.exe"})]
eq(eslesenler(aday), ["alt","ust"], "iki aralık ucu ve tek koşul karşı örnekleri")

```

```solution
event.category: process AND process.name: cmd.exe AND status >= 400 AND status < 500
```

```hint
AND ile dört koşulu birleştir. Keyword harf duyarlıdır.
```

:::

::: gorev Lucene öbek ve aralık deneyi
message alanında login failed öbeğine en fazla bir konum hareketi tanı. Status 400 dahil–500 hariç olsun.

```meta
dil: lucene
timeout: 90
```

```stdin
{"dil":"lucene","mapping":{"id":{"type":"keyword"},"@timestamp":{"type":"date"},"event.category":{"type":"keyword"},"process.name":{"type":"keyword"},"status":{"type":"integer"},"message":{"type":"text"}},"documents":[{"id":"a","@timestamp":"2026-01-01T00:00:00Z","event.category":"process","process.name":"cmd.exe","status":400,"message":"Login failed"},{"id":"b","@timestamp":"2026-01-01T00:00:01Z","event.category":"network","process.name":"cmd.exe","status":499,"message":"Login has failed"},{"id":"c","@timestamp":"2026-01-01T00:00:02Z","event.category":"process","process.name":"CMD.EXE","status":500,"message":"Login failed"},{"id":"d","@timestamp":"2026-01-01T00:00:03Z","event.category":"process","process.name":"cmd.exe","status":399,"message":"Failed login"},{"id":"e","@timestamp":"2026-01-01T00:00:04Z","event.category":"process","process.name":"powershell.exe","status":499,"message":"Login too many failed"},{"id":"f","@timestamp":"2026-01-01T00:00:05Z","event.category":"process","process.name":"CMD.EXE","status":499,"message":"login failed"}],"context":{}}
```

```starter
status:[0 TO 999]
```

```test
eq(eslesenler(), ["a","b","f"], "asıl kimlikler")
from copy import deepcopy
veri = deepcopy(korpus)
for d in veri["documents"]:
    d["id"] = "yeni_" + d["id"]
eq(eslesenler(veri), ["yeni_a","yeni_b","yeni_f"], "kimlikler ezberlenmez")
aday = [dict(korpus["documents"][0], id="alt", status=400), dict(korpus["documents"][0], id="alt_disi", status=399), dict(korpus["documents"][0], id="ust", status=499), dict(korpus["documents"][0], id="ust_disi", status=500), dict(korpus["documents"][0], id="bir", message="login has failed"), dict(korpus["documents"][0], id="iki", message="login has now failed"), dict(korpus["documents"][0], id="ters", message="failed login"), dict(korpus["documents"][0], id="eksik", message="login succeeded")]
eq(eslesenler(aday), ["alt","ust","bir"], "slop 0/1/2, ters öbek, aralık sınırları")

```

```solution
message:"login failed"~1 AND status:[400 TO 500}
```

```hint
Öbeği çift tırnakla sınırla, ~1 ve [400 TO 500} kullan.
```

:::

::: gorev EQL olay seçimini karşılaştır
Process olaylarında process.name için cmd.exe harf duyarsız eşleşmesi ve 400 dahil–500 hariç status iste. Wildcard gerekli değildir.

```meta
dil: eql
timeout: 90
```

```stdin
{"dil":"eql","mapping":{"id":{"type":"keyword"},"@timestamp":{"type":"date"},"event.category":{"type":"keyword"},"process.name":{"type":"keyword"},"status":{"type":"integer"},"message":{"type":"text"}},"documents":[{"id":"a","@timestamp":"2026-01-01T00:00:00Z","event.category":"process","process.name":"cmd.exe","status":400,"message":"Login failed"},{"id":"b","@timestamp":"2026-01-01T00:00:01Z","event.category":"network","process.name":"cmd.exe","status":499,"message":"Login has failed"},{"id":"c","@timestamp":"2026-01-01T00:00:02Z","event.category":"process","process.name":"CMD.EXE","status":500,"message":"Login failed"},{"id":"d","@timestamp":"2026-01-01T00:00:03Z","event.category":"process","process.name":"cmd.exe","status":399,"message":"Failed login"},{"id":"e","@timestamp":"2026-01-01T00:00:04Z","event.category":"process","process.name":"powershell.exe","status":499,"message":"Login too many failed"},{"id":"f","@timestamp":"2026-01-01T00:00:05Z","event.category":"process","process.name":"CMD.EXE","status":499,"message":"login failed"}],"context":{}}
```

```starter
any where true
```

```test
eq(eslesenler(), ["a","f"], "asıl kimlikler")
from copy import deepcopy
veri = deepcopy(korpus)
for d in veri["documents"]:
    d["id"] = "yeni_" + d["id"]
eq(eslesenler(veri), ["yeni_a","yeni_f"], "kimlikler ezberlenmez")
aday = []
for i, (kimlik, status, name, category) in enumerate([("alt",400,"cmd.exe","process"),("alt_disi",399,"cmd.exe","process"),("ust",499,"CMD.EXE","process"),("ust_disi",500,"cmd.exe","process"),("kategori",400,"cmd.exe","network"),("diger",400,"powershell.exe","process")]):
    aday.append(dict(korpus["documents"][0], id=kimlik, status=status, **{"@timestamp":"2026-01-01T00:00:0%dZ" % i,"process.name":name,"event.category":category}))
eq(eslesenler(aday), ["alt","ust"], "harf, kategori ve iki sayısal uç")

```

```solution
process where process.name : "cmd.exe" and status >= 400 and status < 500
```

```hint
Kategori process, harf duyarsız eşleşme : ve iki sayısal karşılaştırma gerekir.
```

:::
