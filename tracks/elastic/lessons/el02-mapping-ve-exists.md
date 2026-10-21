---
id: el02
title: Mapping, Keyword, Text ve Alan Varlığı
summary: İndekslenen değer ile _source farkı; boş metin, null, boş dizi; analyzer ve phrase için açık eğitim modeli.
---

::: anlat Aynı metin, iki farklı arama alanı
Elasticsearch'te mapping, alanın nasıl indekslendiğini belirler. Normalizer olmayan bir `keyword` alanında `Error Timeout` bir bütün değerdir; harf ve noktalama önemlidir. Bir `text` alanı analyzer tarafından terimlere dönüştürülür. Bu yüzden keyword'e göre yazılmış tam eşitlik mantığını text alanına taşıyamazsın.

Örneğin yalnız küçük harfli sözcük tokenları üreten **bu dersin açık modeli** için `message: error timeout`, iki terimi içermeye ilişkin bir aramadır; tırnaklı `message: "error timeout"` sıralı phrase arar. Gerçek analyzer tokenizasyon, normalleştirme ve konum bilgisi üretir. Burada onun yerine kayıtlarla birlikte hazır `message_tokens` dizisi veriyoruz. Bu dizi gerçek Elasticsearch analyzer çıktısını hesaplamaz; kendi belirttiğimiz varsayımı görünür kılar.

Bir alanın `.keyword` alt alanı var mı sorusunu adına bakarak cevaplama; mapping'e bak. Text çoklu alanının keyword sürümü tanımlanmış olabilir ama her kayıtta her alt alan için indekslenen değer bulunmayabilir. Sırf `_source` içinde metni görmek, tam eşleşme alanında sorgulanabildiğini göstermez.
:::

::: anlat exists, Python anahtar varlığı değildir
Kibana KQL'de `user.name: *`, **indekslenen bir değer** varlığını arar. Boş metin `""` bir değerdir ve eşleşebilir. Varsayılan null davranışında `null`, `[]` ve yalnız null içeren diziler değer üretmez; `[null, "alice"]` ise bir değer taşır. `0` ve `false` de uygun mapping'lerde gerçek değerlerdir; Python'un `bool(deger)` kontrolü exists için doğru model değildir.

`ignore_above` sınırını aşma, `ignore_malformed` ve indeksleme/doc_values ayarları da kaynağı görünen alanı sorgu açısından değersiz bırakabilir. Özel `null_value` tanımı null'u başka bir değerle indeksleyebilir. Bu alıştırmalarda özel null_value ve bu istisnalar **yok**; varlık yalnız açıklanan düz scalar/dizi kuralıyla modellenir. Canlı sistemde mapping ve `_ignored` gibi bağlamlar ayrıca incelenir.

Python'da `is None` null'u ayırır. `isinstance(v, list)` diziyi ayırır; `any(x is not None for x in v)` en az bir değer ister ve boş metni yanlışlıkla atmaz. İkinci görevde bitişik tokenları görmek için `zip(tokenlar, tokenlar[1:])` yan yana çiftler üretir. Bu araçların hiçbiri serbest KQL metni ayrıştırmaz.

Kaynaklar (21 Ekim 2026): [KQL değer/exists kuralları](https://www.elastic.co/docs/reference/query-languages/kql), [exists ve indeksleme istisnaları](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-exists-query), [keyword](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/keyword), [text](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/text).
:::

::: tahmin
Aşağıdaki **Kibana KQL** filtresini ve JSON'daki mapping/bağlam varsayımlarını oku. Belirtilen sırada hangi belge kimlikleri görünür? Bu yolun sorgu bloğu okunur; Pafta Elastic sunucusunda sorgu çalıştırmaz. Gizli Python denetimi yalnız verilen sabit sorgunun açıklanan küçük modelini kontrol eder.

```kibana
user.name: *
```

```stdin
{
  "mapping": {
    "user.name": "keyword; normalizer/null_value/ignore_above yok; tüm değerler indeksleniyor"
  },
  "context": {
    "order": "girdi sırası",
    "array_semantics": "null olmayan her öğe indekslenen değer; boş metin dahildir"
  },
  "documents": [
    {
      "id": "a",
      "user.name": ""
    },
    {
      "id": "b",
      "user.name": null
    },
    {
      "id": "c",
      "user.name": []
    },
    {
      "id": "d"
    },
    {
      "id": "e",
      "user.name": [
        null,
        "alice"
      ]
    },
    {
      "id": "f",
      "user.name": [
        null
      ]
    }
  ]
}
```

```gercek
a
e
```

```test
import json
import sys
data = json.loads(sys.stdin.read())
for doc in data['documents']:
    value = doc.get('user.name')
    exists = any(item is not None for item in value) if isinstance(value, list) else value is not None
    if exists:
        print(doc['id'])
```

???

`a`daki boş metin indekslenen değerdir. `e`de null yanında alice vardır. `b`, `c`, `d` ve `f` bu mapping varsayımında indekslenen user.name değeri sağlamaz. Anahtarın bulunması ya da Python truthiness kontrolü tek başına yeterli değil.
:::

::: gorev İndekslenen değer modeli
`indeksli(deger)` fonksiyonu bu dersin sınırlı scalar/dizi modeli için Boolean döndürsün: None yok; boş liste veya yalnız None öğeleri yok; diğer scalar değerler var; listede en az bir None olmayan öğe varsa var. Diziler yalnız scalar/None içerir, iç içe dizi verilmez. `""`, `0`, `False` var sayılmalı. Gerçek mapping istisnalarını bu fonksiyona uydurup gizleme.

```starter
def indeksli(deger):
    return False
```

```test
need('indeksli')
for value, expected in [(None,False),([],False),([None],False),([None,None],False),('',True),(0,True),(False,True),('alice',True),([None,''],True),([None,'alice'],True),([0],True),([False],True)]:
    eq(indeksli(value), expected, 'indeks varlığı: '+repr(value))
```

```solution
def indeksli(deger):
    if isinstance(deger, list):
        return any(oge is not None for oge in deger)
    return deger is not None
```

```hint
bool(deger) boş metin, 0 ve False için yanlış sonuç verir; None ile ayrı karşılaştır.
```
:::

::: gorev Hazır tokenlarla phrase oku
Sabit sorgu `message: "error timeout"`. Her kayıtta analyzer çıktısının küçük eğitim modeli olarak `message_tokens` verilmiş: bunlar küçük harfli sıralı tokenlar. `phrase_sec(kayitlar)` yan yana error, timeout içerenlerin id'lerini sırayla döndürsün. Arada başka token varsa veya sıraları tersse eşleşmez. Eksik token dizisi boş kabul edilir. Ham message alanını ayrıca parçalamaya çalışma.

```starter
def phrase_sec(kayitlar):
    return []
```

```test
need('phrase_sec')
rows = [{'id':'a','message_tokens':['error','timeout']}, {'id':'b','message_tokens':['timeout','error']}, {'id':'c','message_tokens':['error','network','timeout']}, {'id':'d','message_tokens':['before','error','timeout','after']}, {'id':'e','message_tokens':['error']}, {'id':'f','message':'error timeout'}, {'id':'g','message_tokens':[]}]
eq(phrase_sec(rows), ['a','d'], 'bitişik ve doğru sıra')
eq(phrase_sec([{'id':'x','message_tokens':['error','error','timeout']},{'id':'y','message_tokens':['errors','timeout']}]), ['x'], 'konum varyasyonu ve token eşitliği')
eq(phrase_sec([]), [], 'boş küme')
```

```solution
def phrase_sec(kayitlar):
    sonuc = []
    for kayit in kayitlar:
        tokenlar = kayit.get('message_tokens', [])
        if any(a == 'error' and b == 'timeout' for a, b in zip(tokenlar, tokenlar[1:])):
            sonuc.append(kayit['id'])
    return sonuc
```

```hint
zip(tokenlar, tokenlar[1:]) bitişik çiftler verir; yalnız iki tokenın listede bulunması phrase için yetmez.
```
:::
