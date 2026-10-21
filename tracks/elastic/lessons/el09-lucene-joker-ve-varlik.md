---
id: el09
title: Lucene · İndekslenmiş Varlık ve Kaçış
summary: Var olan değeri kaynak anahtardan ayır; *, ? ve literal kaçışları gerçek sorguda yaz.
---

::: anlat Exists kaynak anahtarını saymaz
`user.name:*` alanın indekslenmiş bir değeri olup olmadığını sınar. `_exists_:user.name` aynı amaç için desteklenir. Kaynakta anahtarın bulunması yeterli değildir: null ve boş dizi değer üretmez. Boş keyword metni ise indekslenebilir ve varlık koşulunu sağlar. Bir dizi içinde null ile geçerli metin birlikteyse geçerli metin yeterlidir.

Bu derste user.name için ignore_above:12 var. On iki karakteri aşan tek değer kaynakta görünür ama bu keyword indeksine girmez; yalnız o değer varsa exists false olur. null_value tanımlansaydı açık null yerine o terim indekslenebilirdi; alanın hiç bulunmaması yine aynı şey değildir. Pafta index:false alanını sorgulamayı desteklemez; gerçek Elasticsearch'teki doc_values seçeneklerini burada varsayma.

```lucene
user.name:* AND (NOT user.name:svc_*)
```

Bu filtre var olan kullanıcıları alır ve svc_ önekiyle eşleşen değer taşıyan belgeleri çıkarır. Dizide hem alice hem svc_backup varsa NOT bütün belgeyi çıkarır. [Elastic exists davranışı](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-exists-query), [ignore_above](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/ignore-above). Kaynaklar 21 Ekim 2026 tarihinde kontrol edildi.

```meta
dil: lucene
```
:::

::: anlat Lucene soru işareti gerçek jokerdir
Lucene `*` ile sıfır veya daha çok, `?` ile tam bir karakter eşler. KQL dersindeki literal `?` kuralını buraya taşıma. `file.name:report?.txt`, report1.txt ve report?.txt gibi tek karakterli arayı kabul eder; report12.txt kabul edilmez. Normalizersız keyword alanında harf büyüklüğü korunur; Report1.txt farklıdır.

Literal jokeri ters eğik çizgiyle kaçır: `file.name:report\?.txt` yalnız gerçek soru işaretli adı ister. `file.name:report\*.txt` ise gerçek yıldız içeren adı ister. Editörde tek sorgu katmanı vardır; JSON API gövdesine aynı sorguyu koyarken JSON'un ters eğik çizgi kaçışını ayrıca yaparsın. Dersin stdin JSON'u sorgu değildir, veri korpusudur.

```lucene
file.name:report\?.txt
```

Jokerler keyword değerinin veya text alanındaki tek indeks teriminin üzerinde çalışır; kendiliğinden tüm kaynak içinde alt metin araması yapmaz. Başta yıldız burada desteklenir, geniş gerçek indekslerde maliyeti yüksek olabilir. [Lucene terim jokerleri ve kaçış](https://lucene.apache.org/core/9_12_3/queryparser/org/apache/lucene/queryparser/classic/package-summary.html).

```meta
dil: lucene
```
:::

::: tahmin
Sorguyu çalıştırmadan önce dönecek kimlikleri sırayla tahmin et. Gerçek Lucene motoru kullanılacak. Context sıralaması yoksa belge giriş sırası korunur; bütün veri aşağıdadır.

```lucene
user.name:* AND (NOT user.name:svc_*)
```

```stdin
{
  "dil": "lucene",
  "mapping": {
    "user.name": {
      "type": "keyword",
      "ignore_above": 12
    },
    "file.name": {
      "type": "keyword"
    },
    "host.name": {
      "type": "keyword"
    }
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
      "id": "d",
      "user.name": "svc_backup"
    },
    {
      "id": "e",
      "user.name": "alice"
    },
    {
      "id": "f",
      "user.name": "thirteenchars!"
    },
    {
      "id": "g",
      "user.name": [
        null,
        "bob"
      ]
    }
  ],
  "context": {}
}
```

```meta
dil: lucene
```

???

Çıktı:

```text
a
e
g
```

Boş keyword var sayılır; null/[] sayılmaz. f değeri ignore_above sınırını aşar. d svc_ önekinden dışlanır.
:::

::: gorev Var olan kişisel kullanıcıları seç
İndekslenmiş user.name değeri bulunan belgeleri al; değerlerinden biri svc_ önekiyle başlıyorsa belgeyi çıkar. Boş metni ayrıca dışlama.

Editöre yalnız Lucene sorgusu yaz. `stdin` eşlemeyi, belgeleri ve bağımsız zaman/sıralama bağlamını taşır. Testte `eslesenler()` senin sorgunun kimliklerini döndürür; `eslesenler(belge_listesi)` aynı mapping/context ile yeni belgeleri sınar. Python kodu yazman gerekmiyor.

```starter
*:*
```

```stdin
{
  "dil": "lucene",
  "mapping": {
    "user.name": {
      "type": "keyword",
      "ignore_above": 12
    },
    "file.name": {
      "type": "keyword"
    },
    "host.name": {
      "type": "keyword"
    }
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
      "id": "d",
      "user.name": "svc_backup"
    },
    {
      "id": "e",
      "user.name": "alice"
    },
    {
      "id": "f",
      "user.name": "thirteenchars!"
    },
    {
      "id": "g",
      "user.name": [
        null,
        "bob"
      ]
    }
  ],
  "context": {}
}
```

```meta
dil: lucene
```

```test
eq(eslesenler(), ['a', 'e', 'g'], "ana korpus")
eq(eslesenler([{'id': 'x', 'user.name': 'abcdefghijkl'}, {'id': 'y', 'user.name': 'abcdefghijklm'}, {'id': 'z', 'user.name': ['alice', 'svc_job']}, {'id': 'w', 'user.name': None}]), ['x'], "değişen korpus 1")
eq(eslesenler([{'id': 'p', 'user.name': 'Svc_job'}, {'id': 'q', 'user.name': []}, {'id': 'r', 'user.name': ['', 'bob']}]), ['p', 'r'], "değişen korpus 2")
```

```solution
user.name:* AND (NOT user.name:svc_*)
```

```hint
Önce varlık koşulu, ardından NOT svc_*; ignore_above motor tarafından mapping üzerinden uygulanır.
```
:::

::: gorev Literal soru işareti ve host kapsamı
Yalnız lab01 hostunda, adı tam olarak gerçek soru işareti içeren report?.txt olan belgeyi seç. report1.txt ve report12.txt bu görevde kabul edilmez.

Editöre yalnız Lucene sorgusu yaz. `stdin` eşlemeyi, belgeleri ve bağımsız zaman/sıralama bağlamını taşır. Testte `eslesenler()` senin sorgunun kimliklerini döndürür; `eslesenler(belge_listesi)` aynı mapping/context ile yeni belgeleri sınar. Python kodu yazman gerekmiyor.

```starter
*:*
```

```stdin
{
  "dil": "lucene",
  "mapping": {
    "user.name": {
      "type": "keyword",
      "ignore_above": 12
    },
    "file.name": {
      "type": "keyword"
    },
    "host.name": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "host.name": "lab01",
      "file.name": "report?.txt"
    },
    {
      "id": "b",
      "host.name": "lab01",
      "file.name": "report1.txt"
    },
    {
      "id": "c",
      "host.name": "lab02",
      "file.name": "report?.txt"
    },
    {
      "id": "d",
      "host.name": "lab01",
      "file.name": "report12.txt"
    }
  ],
  "context": {}
}
```

```meta
dil: lucene
```

```test
eq(eslesenler(), ['a'], "ana korpus")
eq(eslesenler([{'id': 'x', 'host.name': 'lab01', 'file.name': 'Report?.txt'}, {'id': 'y', 'host.name': 'lab01', 'file.name': ['other', 'report?.txt']}, {'id': 'z', 'file.name': 'report?.txt'}]), ['y'], "değişen korpus 1")
eq(eslesenler([{'id': 'p', 'host.name': 'lab01', 'file.name': 'report*.txt'}, {'id': 'q', 'host.name': 'lab01', 'file.name': 'report?.txt'}]), ['q'], "değişen korpus 2")
```

```solution
host.name:lab01 AND file.name:report\?.txt
```

```hint
Soru işaretini \? yap. İki alanı AND ile bağla; JSON içine sorgu yazmıyorsun.
```
:::
