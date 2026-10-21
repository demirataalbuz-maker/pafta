# Elastic / Kibana — sorgu yazma yolu

19 ders, altı rütbe. Öğrenci Kibana KQL, Lucene query string ve Elastic EQL **yazar**. Her tahmin aynı sorgu motorunda hesaplanır; sabit `gercek` cevabı veya sorguya özel gizli Python eşleştirme modeli yoktur. Microsoft **KQL (Kusto)** ayrı bir yoldur.

## Çalıştırma

JDK 17+ gerekir; bu bilgisayardaki Android Studio JBR 21 kullanılabilir. Özel JDK için `PAFTA_JAVA` veya `JAVA_HOME` ayarlanabilir.

```text
python tools/install_elastic_runtime.py
python tools/validate.py --yol elastic
```

Kurucu, beş Apache Lucene **9.12.3** JAR'ını resmî Maven deposundan `.deps/elastic-lucene` içine indirip sabit SHA-512 değerlerini doğrular. İlk çalıştırmada depodaki Java bağdaştırıcısı derlenir. Windows JVM'sinin emoji içeren sınıf yolu sorunu için doğrulanmış dosyalar geçici ASCII önbelleğe kopyalanır. JDK/JAR eksikse açıklayıcı hata verilir; başka bir sorgu motoruna sessiz geçilmez. Öğrenci sorgusu komut satırı veya Python kodu olarak çalıştırılmaz.

KQL bir sözdizimi ağacına ayrılır; yapraklar, Boolean gruplar ve nested alt belge sorguları **gerçek Lucene indeksinde** değerlendirilir. Lucene yolu doğrudan gerçek Classic QueryParser, token konumları, fuzzy aramaları ve regex otomatalarını kullanır. EQL, Elastic kaynakları ve belgelerindeki davranışa göre yazılmış **sınırlı yerel bir yorumlayıcıdır**. Hiçbiri Elasticsearch/Kibana sunucusu değildir. Bu teslimde gerçek Elasticsearch sunucusunda karşılaştırmalı çalıştırma yapılmadı. EL19 bunu öğrencinin kendi ücretsiz yerel ürün kurulumunda yapmasını sağlar.

## Corpus sözleşmesi

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

## Destek ve ürün farkları

| Dil | Desteklenen çekirdek | Açıkça reddedilen / farklı sabit seçenek |
|---|---|---|
| Kibana KQL | Alan/değer, keyword harf duyarlılığı, text analizli varsayılan OR, tırnaklı öbek, AND/OR/NOT, değer grubu, `*` varlık/joker, literal `?`, kaçış, sayısal/tarih aralığı, aynı nested çocuk | Alansız arama, alan adı jokeri, text içinde boşluklu karma joker, özel analyzer, tarih matematiği. Başta joker sabit olarak açık; Kibana'da bu ayara bağlıdır. Boş sorgu Pafta arayüzünde açık hata verir. |
| Lucene | Gerçek Classic QueryParser, varsayılan OR, açık alanlar, saf NOT, exists, öbek/slop, fuzzy, whole-term regex, joker/kaçış, türlenmiş açık/kapalı aralık | Alan adı jokeri/default field, nested sorgusu, boost/skor seçenekleri, özel analyzer/tarih matematiği. Lucene sürümü 9.12.3'tür; Elasticsearch'ün bundled Lucene sürümü farklı olabilir. `analyze_wildcard=false`, başta joker açık, text position gap=100 sabit seçimlerdir. |
| Elastic EQL | Skaler olay koşulu, null/optional alan, `==` ile `:` farkı, in/in~, like/like~, sequence, common/per-stage by, dahil maxspan, until, ortada eksik olay | Functions, aritmetik, regex, pipes, runs, sample/join, ilk/son eksik olay, text/nested/dizi sorgusu, özel mapping seçenekleri. Harf duyarsız işlemler yalnız ASCII değerlerde; Unicode duyarsız eşleşme açık hata. Açık timestamp/tie sırası gerekir. Sabit-sabit, keyword sıralama ve karışık tamsayı/double karşılaştırmaları; double veya farklı mapping türlerinden join anahtarları reddedilir. |

Mapped olmayan alan sorguları ve `index:false` alan sorguları açık hata verir. Gerçek Elastic unmapped alanı bazen boş sonuç olarak kabul eder; bazı `index:false` türleri doc_values ile sorgulanabilir. Bu yerel tezgah bunları taklit etmez. KQL'de yalnız `*` jokerken Lucene ve EQL'de `?` de jokerdir. EQL'de string kaçışı, wildcard kaçışı değildir; literal yıldız için `==` gerekir. Sonuç tabloları belge/dizi üyeliğini öğretir; skor, shard, aggregations, ingest, gerçek saat ilerlemesi ve dağıtık yürütme yoktur.

## Ders sırası ve denetim

EL01–EL06 KQL; EL07–EL12 Lucene; EL13–EL18 EQL; EL19 aynı mapping ve sorgularla gerçek Windows Elasticsearch/Kibana kurulumu. Her derste tahmin ve sorgu yazma görevleri vardır. Testler eşit sınır, komşu değer, eksik alan, harf, joker ve dizi karşı örneklerini içerir; üyelik karşılaştırması çözüm metnini ezberlemeyi gerektirmez.

```text
python tools/test_elastic_common.py
python tools/test_elastic_kql.py
python tools/test_elastic_lucene.py
python tools/test_elastic_eql.py
python tools/test_elastic_curriculum.py
python tools/test_elastic_integration.py
python tools/audit_elastic_mutations.py
node --test tools/test_elastic_ui.mjs
```

Mutasyon aracı AND/OR, NOT, eşit aralık uçları, slop/fuzzy ve maxspan değişikliklerini dener. Geçen bir mutasyon otomatik olarak yanlış çözüm sayılmaz: eşdeğer olup olmadığı incelenir ve gerçek hataysa yeni karşı örnek eklenir. Test sayıları ve sonuçlar teslim raporundadır.

## Resmî kaynaklar

21 Ekim 2026'da başvurulan kaynaklar:

- [Kibana KQL](https://www.elastic.co/docs/reference/query-languages/kql) ve [Kibana is.ts kaynak kodu](https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-es-query/src/kuery/functions/is.ts).
- [Elasticsearch query_string](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-query-string-query) ve [Apache Lucene 9.12.3 QueryParser](https://lucene.apache.org/core/9_12_3/queryparser/org/apache/lucene/queryparser/classic/package-summary.html).
- [Elastic EQL](https://www.elastic.co/docs/reference/query-languages/eql/eql-syntax), [SequenceMatcher](https://github.com/elastic/elasticsearch/blob/v9.2.0/x-pack/plugin/eql/src/main/java/org/elasticsearch/xpack/eql/execution/sequence/SequenceMatcher.java) ve [Ordinal](https://github.com/elastic/elasticsearch/blob/v9.2.0/x-pack/plugin/eql/src/main/java/org/elasticsearch/xpack/eql/execution/search/Ordinal.java).
- [Elasticsearch Windows ZIP](https://www.elastic.co/docs/deploy-manage/deploy/self-managed/install-elasticsearch-with-zip-on-windows), [Kibana Windows](https://www.elastic.co/docs/deploy-manage/deploy/self-managed/install-kibana-on-windows), [Basic lisans ayarı](https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/license-settings).
