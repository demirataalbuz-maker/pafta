# Elastic / Kibana — sorgu yazma yolu

27 ders, altı rütbe. Öğrenci Kibana KQL, Lucene query string ve Elastic EQL **yazar**. Her tahmin aynı sorgu motorunda hesaplanır; sabit `gercek` cevabı veya sorguya özel gizli Python eşleştirme modeli yoktur. Microsoft **KQL (Kusto)** ayrı bir yoldur.

## Çalıştırma

JDK 17+ gerekir; bu bilgisayardaki Android Studio JBR 21 kullanılabilir. Özel JDK için `PAFTA_JAVA` veya `JAVA_HOME` ayarlanabilir.

```text
python tools/install_elastic_runtime.py
python tools/validate.py --yol elastic
```

Kurucu, beş Apache Lucene **9.12.3** JAR'ını resmî Maven deposundan `.deps/elastic-lucene` içine indirip sabit SHA-512 değerlerini doğrular. İlk çalıştırmada depodaki Java bağdaştırıcısı derlenir. Windows JVM'sinin emoji içeren sınıf yolu sorunu için doğrulanmış dosyalar geçici ASCII önbelleğe kopyalanır. JDK/JAR eksikse açıklayıcı hata verilir; başka bir sorgu motoruna sessiz geçilmez. Öğrenci sorgusu komut satırı veya Python kodu olarak çalıştırılmaz.

KQL bir sözdizimi ağacına ayrılır; yapraklar, Boolean gruplar ve nested alt belge sorguları **gerçek Lucene indeksinde** değerlendirilir. Lucene yolu doğrudan gerçek Classic QueryParser, token konumları, fuzzy aramaları ve regex otomatalarını kullanır. EQL, Elastic kaynakları ve belgelerindeki davranışa göre yazılmış **sınırlı yerel bir yorumlayıcıdır**. Bunlar temel motorlardır. EL20–EL27 ayrıca gerçek Elasticsearch/Kibana 9.5.5 API laboratuvarını kullanır. EL13–EL18 tahminlerinin altısı aynı mapping/veriyle gerçek EQL API’siyle karşılaştırılmıştır; bütün yerel dilin her sorguda birebir eşdeğer olduğu iddia edilmez.

## Temel motor corpus sözleşmesi (EL01–EL19)

Girdi kutusu JSON alır. Tam bir örnek `corpora/temel.json` dosyasındadır:

```json
{
  "dil": "kibana",
  "mapping": {"user.name": {"type": "keyword"}, "message": {"type": "text"}},
  "documents": [{"id": "a", "user.name": "alice", "message": "Login failed"}],
  "context": {}
}
```

- Her belgede benzersiz, boş olmayan metin `id` bulunur. Bu çıktı kimliğidir; sorgulamak için ayrıca mapping'e alınmalıdır. Mapping dışı kaynak alanları kendiliğinden indekslenmez.
- Alan türleri: `keyword`, `text`, `integer`, `long`, `double`, `boolean`, `date`; KQL için ayrıca `nested`. Genel JSON nesneleri mapped düz alan yollarına açılır; nested nesne listeleri çocuk kapsamını korur.
- Belgelerde tür dönüştürme/coerce yoktur. Tarihler saat dilimli ISO-8601, en çok milisaniye hassasiyetindedir. Lucene/KQL kaynak tarihlerinde tamsayı epoch_millis de kabul edilir; EQL tarihleri zonlu ISO metin ister. Kısmi tarih, tarih matematiği ve sayısal tarih sorgu metinleri açık hata verir.
- `text` yalnız `standard` analyzer, `keyword` isteğe bağlı `normalizer: lowercase`, `ignore_above` ve `null_value` destekler. Metin dizilerinin konum aralığı 100'dür. EQL özel mapping seçeneklerini, text/nested sorgularını, çok değerli sorgu alanlarını ve negatif double sıfırı (-0.0) reddeder. maxspan birimleri ms/s/m/h/d ile sınırlıdır.
- KQL/Lucene sonuçları varsayılan olarak corpus listesinin sırasındadır; bu Elasticsearch'ün skor/shard sırası değildir. `context.sort` skaler alanlarda `[["alan","asc"],["id","desc"]]` biçimini kabul eder, eksikleri sona koyar; dizi alanı sıralaması hata verir.
- `context.time_filter`, mapped date alanında `{"field":"@timestamp","gte":"...","lt":"..."}` gibi açık uçlar alır ve sorgudan önce uygulanır. EQL daima `timestamp_field` ve `tiebreaker_field` ile sıralanır; `context.sort` kabul etmez. Varsayılan `event.id` mapped değilse yerel `id` eşitlik kırıcıdır. Gerçek EQL API'sinde eşdeğer karşılaştırma için mapped `id` alanını açıkça seç. Aynı timestamp+tiebreaker çifti açık hata verir.

## Temel motor desteği ve ürün farkları (EL01–EL19)

| Dil | Desteklenen çekirdek | Açıkça reddedilen / farklı sabit seçenek |
|---|---|---|
| Kibana KQL | Alan/değer, keyword harf duyarlılığı, text analizli varsayılan OR, tırnaklı öbek, AND/OR/NOT, değer grubu, `*` varlık/joker, literal `?`, kaçış, sayısal/tarih aralığı, aynı nested çocuk | Alansız arama, alan adı jokeri, text içinde boşluklu karma joker, özel analyzer, tarih matematiği. Başta joker sabit olarak açık; Kibana'da bu ayara bağlıdır. Boş sorgu Pafta arayüzünde açık hata verir. |
| Lucene | Gerçek Classic QueryParser, varsayılan OR, açık alanlar, saf NOT, exists, öbek/slop, fuzzy, whole-term regex, joker/kaçış, türlenmiş açık/kapalı aralık | Alan adı jokeri/default field, nested sorgusu, boost/skor seçenekleri, özel analyzer/tarih matematiği. Lucene sürümü 9.12.3'tür; Elasticsearch'ün bundled Lucene sürümü farklı olabilir. `analyze_wildcard=false`, başta joker açık, text position gap=100 sabit seçimlerdir. |
| Elastic EQL | Skaler olay koşulu, null/optional alan, `==` ile `:` farkı, in/in~, like/like~, sequence, common/per-stage by, dahil maxspan, until, ortada eksik olay | Functions, aritmetik, regex, pipes, runs, sample/join, ilk/son eksik olay, text/nested/dizi sorgusu, özel mapping seçenekleri. Harf duyarsız işlemler yalnız ASCII değerlerde; Unicode duyarsız eşleşme açık hata. Açık timestamp/tie sırası gerekir. Sabit-sabit, keyword sıralama ve karışık tamsayı/double karşılaştırmaları; double veya farklı mapping türlerinden join anahtarları reddedilir. |

Mapped olmayan alan sorguları ve `index:false` alan sorguları açık hata verir. Gerçek Elastic unmapped alanı bazen boş sonuç olarak kabul eder; bazı `index:false` türleri doc_values ile sorgulanabilir. Bu yerel tezgah bunları taklit etmez. KQL'de yalnız `*` jokerken Lucene ve EQL'de `?` de jokerdir. EQL'de string kaçışı, wildcard kaçışı değildir; literal yıldız için `==` gerekir. Temel motorun sonuç tabloları belge/dizi üyeliğini öğretir; skor, shard, aggregations, ingest, gerçek saat ilerlemesi ve dağıtık yürütme sunmaz. Aşağıdaki gerçek API bölümü bundan ayrıdır.

## Gerçek API laboratuvarı (EL20–EL27)

Resmi imajlar, sürüm **9.5.5** ve SHA-256 digest ile sabitlenir.
Docker Desktop açık olmalı. İlk indirme açık kurulum eylemidir:

```text
python tools/elastic_lab_setup.py --pull --start
python tools/elastic_lab_setup.py --start
python tools/elastic_lab_setup.py --stop
```

`--start` indirme yapmaz. Ders çalıştırmak konteyner başlatmaz. Her konteynerin
2 GiB bellek sınırı vardır. Başka laboratuvarlar da açıksa Docker'a buna göre
bellek ayır. İmajlar/data volume yerel diskte kalır; restart policy `no`dur.
Elasticsearch `127.0.0.1:19200`, Kibana `127.0.0.1:15601`; `elastic` parolası
Git dışında `.deps/elastic-lab/password` içinde üretilir. Basic lisans gerçekten
sorgulanarak doğrulanır; trial/abonelik ve Elastic Agent kurulumu yoktur.

Bu öğretim kurulumunda HTTP yalnız localhost'a yayımlanır; konteyner ağında
TLS yoktur. EL19'un güvenli gerçek dağıtım TLS yönergesinin yerine geçmez.
İnternete/LAN'a yayımlama. Yönetim işlemleri laboratuvar admin hesabını kullanır;
ES|QL sorgusuna ayrıca yalnız kendi indeksini okuyabilen kısa ömürlü anahtar
verilir. Bunu üretimde kullanılacak bir en az yetki dağıtımı olarak sunmuyoruz.

Yeni girdi biçimi:

```json
{"backend":"elastic","dil":"esql","mapping":{"n":"long"},"documents":[{"id":"a","n":1}],"context":{}}
```

- `dil`: `ingest`, `eql`, `esql`, `rule`. Backend açıkça seçilir; fallback yoktur.
- Mapping düz ECS yollarından gerçek `properties` nesnelerine çevrilir.
  Strict mapping ve sayısal `coerce:false` kullanılır. Kaynak `_source` bazen
  düz noktalı anahtar, bazen ingest'in oluşturduğu iç içe nesnedir; `alan(doc,yol)`
  test yardımcısı iki gösterimi okur, tür veya eşleşme taklit etmez.
- Girdi en çok 1 MiB / 100 belge, kod 16 KiB; API yanıtı 4 MiB ile sınırlı.
  Ağ/API hatası, hatalı bulk öğesi ve kısmi EQL/ES|QL sonucu görünür kalır.
- Ingest kodu gerçek pipeline JSON'udur. `_simulate` ve gerçek `_bulk` ayrı
  ölçülür. Simülasyon başarısı mapping başarısı sayılmaz. Script/pipeline çağrısı,
  dinamik alan adları ve `_index` gibi metadata yazımı bu tezgaha açılmaz;
  desteklenmeyen işlemci açık hatadır. Kullanılan işlemciler kaynaktaki allowlist'tedir.
- EQL gerçek `_eql/search` kullanır; baştaki eksik olay, işlevler ve sequence
  gerçek ürün tarafından değerlendirilir. EQL çıktı satırında yalnız olumlu
  kaynak olay kimlikleri yazılır. Async/kısmi yanıt kesin sonuç sayılmaz.
- ES|QL gerçek `_query` kullanır. `FROM pafta` yalnız işin rastgele indeksine
  bağlanır. Sonuç sütun ve değerleri API'den gelir; toplama Python'da yapılmaz.
- Security kodu query/eql/threshold create-rule JSON alanlarıdır. Rastgele
  indeks ve rule id tezgahça bağlanır, kural devre dışı kaydedilir, tek gerçek
  preview yürütülür. `context.timeframe_end` sabit referans andır. Preview
  belgeleri 9.5.5'in preview indeksinden okunur; operational alarm sayılmaz.
  `exceptions` hazırlığı gerçek exception listesi/öğesi oluşturup kurala bağlar.
- `sonuc(veri=None)`, `eslesenler`, `referans`, `korpus` ve `alan` test yardımcıları
  yeniden gerçek API çağırır; kaynak metni kontrol ederek başarı verilmez.
- Her normal tamamlanma/hata sonunda yalnız o işin indeks/pipeline/kuralı
  silinir; ES|QL anahtarı iptal edilir. İşlem zorla öldürülürse `finally`
  çalışmayabilir: konteynerde kalan `pafta-elastic-*` indekslerini ve Pafta adlı
  geçici kuralları yalnız kendi laboratuvarında kontrol et. Konteyner volume'unu
  silmek bütün bu laboratuvar verisini kaybettirir; varsayılan durdurma silmez.

EL20 korpusu gerçek, zararsız alt süreç gözleminden alınan NDJSON'dur;
üretici `tools/capture_elastic_telemetry.py`, köken/özet `captures/README.md` ve
`captures/manifest.json` içindedir. Diğer ileri ders korpusları sınır değerleri
için sentetik tanıklardır. Sysmon/Agent verisi oldukları iddia edilmez.

Kendi EL24 kuralını `kuralim.json` dosyasına kaydedip gerçek zamanlayıcıya ver:

```text
python tools/elastic_rule_live.py --task 1 --code-file kuralim.json
```

Task 2 EQL içindir. Araç olay tarihlerini açıkça yeniden bazlar; interval 1m,
lookback now-10m kullanır. Query/type/language öğrenci kodundan gelir. Gerçek
Task Manager yürütmesi ve operational alarm indeksi ölçülür, yalnız o işin
kural/alarmları temizlenir. Bu canlı gösterim, sabit tarihli preview sınır
testlerinin yerine geçmez. Canlı pencerede EL24'ün `d` olayı da eşleşebilir;
on dakikalık pencere iki dakikalık pencereyle aynı değildir.

## Ders sırası ve denetim

EL01–EL06 KQL; EL07–EL12 Lucene; EL13–EL18 EQL; EL19 aynı mapping ve sorgularla gerçek Windows Elasticsearch/Kibana kurulumu. EL20–EL21 gerçek NDJSON/ingest ve mapping; EL22–EL23 native EQL; EL24–EL25 Security kuralı, eşik/istisna; EL26–EL27 ES|QL raporları. Her derste tahmin ve kod yazma görevleri vardır. Testler eşit sınır, komşu değer, eksik alan, harf, joker ve dizi karşı örneklerini içerir; üyelik karşılaştırması çözüm metnini ezberlemeyi gerektirmez.

```text
python tools/test_elastic_common.py
python tools/test_elastic_kql.py
python tools/test_elastic_lucene.py
python tools/test_elastic_eql.py
python tools/test_elastic_curriculum.py
python tools/test_elastic_integration.py
python tools/audit_elastic_mutations.py
python tools/audit_elastic_native.py
python tools/test_elastic_lab.py
python tools/test_elastic_lab.py --scheduled
node --test tools/test_elastic_ui.mjs
```

Mutasyon aracı AND/OR, NOT, eşit aralık uçları, slop/fuzzy ve maxspan değişikliklerini dener. Geçen bir mutasyon otomatik olarak yanlış çözüm sayılmaz: eşdeğer olup olmadığı incelenir ve gerçek hataysa yeni karşı örnek eklenir. Test sayıları ve sonuçlar teslim raporundadır.

## Resmî kaynaklar

21 Ekim 2026'da başvurulan kaynaklar:

- [Kibana KQL](https://www.elastic.co/docs/reference/query-languages/kql) ve [Kibana is.ts kaynak kodu](https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-es-query/src/kuery/functions/is.ts).
- [Elasticsearch query_string](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-query-string-query) ve [Apache Lucene 9.12.3 QueryParser](https://lucene.apache.org/core/9_12_3/queryparser/org/apache/lucene/queryparser/classic/package-summary.html).
- [Elastic EQL](https://www.elastic.co/docs/reference/query-languages/eql/eql-syntax), [SequenceMatcher](https://github.com/elastic/elasticsearch/blob/v9.2.0/x-pack/plugin/eql/src/main/java/org/elasticsearch/xpack/eql/execution/sequence/SequenceMatcher.java) ve [Ordinal](https://github.com/elastic/elasticsearch/blob/v9.2.0/x-pack/plugin/eql/src/main/java/org/elasticsearch/xpack/eql/execution/search/Ordinal.java).
- [Elasticsearch Windows ZIP](https://www.elastic.co/docs/deploy-manage/deploy/self-managed/install-elasticsearch-with-zip-on-windows), [Kibana Windows](https://www.elastic.co/docs/deploy-manage/deploy/self-managed/install-kibana-on-windows), [Basic lisans ayarı](https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/license-settings).
