# Elastic / Kibana — okuma yolu

Bu yol, SOC incelemelerinde karşılaşılan **Kibana KQL**, **Lucene query string** ve **Elastic EQL** sorgularını okumak içindir. Microsoft'un ayrı **KQL (Kusto)** yoluyla dil, ders kimliği veya ilerleme paylaşmaz. 18 ders harita sırasında `el01`–`el18` kimliklerini kullanır; altı rütbenin her birinde üç ders vardır.

## Çalıştırma sözleşmesi

Pafta bu yolda Elasticsearch veya Kibana başlatmaz; bir Elastic sorgu çeviricisi de içermez. Yerel bir Elastic kurulumu ve yeni Python bağımlılığı gerekmez.

- `kibana`, `lucene` ve `eql` kod blokları sözdizimi vurgulanmış **okuma örnekleridir**. Sorgu için Çalıştır düğmesi gösterilmez.
- Her derste verilen mapping, kayıtlar, zaman aralığı ve sıralama altında bir tahmin vardır. Yanıt `gercek` bloğunda yazılıdır; sunucu bunu tahmin gönderilmeden ön yüze açmaz.
- Her tahminin gizli `test` bloğu, aynı sabit örnek verinin sonucunu bağımsız Python ifadeleriyle hesaplar. Bu bir sorgu ayrıştırıcısı veya gerçek Elastic doğrulaması değildir; ders yazarının yanıtını, tanımlanmış küçük veri üzerinde çapraz denetler.
- Tezgah **Python** çalıştırır. Görevler açıkça sınırlanmış veri yorumlama, istek kurma veya yanıt okuma alıştırmalarıdır. Genel KQL/Lucene/EQL yorumlayıcısı yazdırılmaz.
- EQL görevlerindeki aday çiftler/diziler önceden verilmişse yalnızca bu adayların koşulları sınanır. Bütün bir olay akışında gerçek EQL durum makinesinin hangi diziyi seçeceği bu küçük fonksiyonlardan çıkarılmaz.

Gerçek ortamda aynı metnin sonucunu mapping, analyzer/normalizer, veri görünümü, zaman alanı, sorgu modu, alanların indekslenmesi ve ürün sürümü belirler. Dersin varsayımlarını değiştirmek için yerel tahmin yanıtı düzenlenmez; sorgu ilgili Elastic ortamında yeniden denenir. Sıra soruda ayrıca belirtilir: Python'da veya örnek listesindeki sıra, arama motorunun varsayılan sonuç sırası sayılmaz.

## Öğrenme sırası

| Dersler | Odak |
|---|---|
| el01–el03 | Discover bağlamı; Kibana KQL, keyword/text ayrımı, mantıksal filtreler |
| el04–el06 | Sayı/zaman sınırları, wildcard/varlık, nested bağlamı ve KQL inceleme projesi |
| el07–el09 | Lucene mantığı, dahil/hariç aralık uçları, wildcard ve indekslenmiş alanlar |
| el10–el12 | Analyzer/phrase, fuzzy ve Lucene regex sınırları; istek/yanıt inceleme projesi |
| el13–el15 | Elastic EQL olay kategorileri, karşılaştırmalar ve sıra/anahtar ilişkileri |
| el16–el18 | maxspan, until, eksik olaylar ve EQL tespit/regresyon projesi |

## Denetim

Proje kökünden:

```text
python tools/validate.py --yol elastic
python tools/test_elastic_curriculum.py
python tools/test_elastic_integration.py
python tools/audit_elastic_mutations.py
node --test tools/test_elastic_ui.mjs
```

Genel doğrulayıcı görev çözümlerini/başlangıçlarını ve çalıştırılabilir Python örneklerini denetler. Müfredat testi ayrıca 18 tahminin sabit yanıtını Python modeliyle karşılaştırır; API testi geçici ilerleme klasörü kullanır. Mutasyon denetimi her çözümde `<`/`<=`, `>`/`>=` ve `and`/`or` değişikliklerini tek tek dener; her bozuk çözümün `fail` vermesini ister. Node testi sorgu bloklarının okuma etiketi taşımasını, Python düğmelerini ve HTML kaçışını denetler; görsel tarayıcı testi değildir. Bu raporların hiçbiri sorguların gerçek bir Elasticsearch sunucusunda çalıştırıldığı anlamına gelmez.

## Resmi dayanaklar

21 Ekim 2026 tarihinde başvurulan kaynaklar:

- [Kibana KQL](https://www.elastic.co/docs/reference/query-languages/kql): Kusto'dan ayrı filtre dili; alan türleri, wildcard ve nested söz dizimi.
- [Kibana'da Lucene seçimi](https://www.elastic.co/docs/explore-analyze/query-filter/languages/lucene-query-syntax) ve [query_string sorgusu](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-query-string-query): aralıklar, phrase, wildcard, regex ve kaçış.
- [Elastic EQL söz dizimi](https://www.elastic.co/docs/reference/query-languages/eql/eql-syntax): olaylar, diziler, join anahtarları, maxspan, until ve eksik olaylar. Bu, benzer isimli Python `eql` paketi değildir.
- [Discover](https://www.elastic.co/docs/explore-analyze/discover/discover-get-started): veri görünümü ve zaman filtresi bağlamı.

Ürüne bağlı ayrıntılar her dersin kendi kapsam notunda belirtilir. Bu yol sorgu okuryazarlığı kazandırır; TryHackMe laboratuvarlarının veya gerçek SOC incelemesinin yerini almaz.
