---
id: el10
title: Lucene · Phrase, Slop ve Fuzzy
summary: Terim konumlarını, transpozisyon maliyetini ve gerçek edit uzaklığını test et.
---

::: anlat Phrase kaynak alt metni değildir
Standard analyzer bu yolda Unicode sözcük ayrıştırması ve küçük harfe dönüştürme yapar. `message:FAILED` indeks terimi failed ile eşleşebilir; normalizersız keyword aynı davranışı göstermez. `message:"failed login"` iki terimin aynı sırada ve bitişik konumlarda bulunmasını ister. Noktalama işaretleri analyzer'dan geçer; kaynak metinde aynı bayt dizisinin bulunması zorunlu değildir.

Slop, phrase konumlarını taşımaya izin veren bütçedir. `"failed login"~1` arada bir terime izin verir. İki terimin yerini ters çevirmek iki konum hareketi gerektirir: login failed slop1 ile değil slop2 ile eşleşir. Slop'u genel olarak “en fazla N boşluk” diye açıklamak bu nedenle yanlıştır.

```lucene
message:"failed login"~1
```

Çok değerli text alanları için konum aralığı 100'dür. ["failed","login"] dizisi bitişik iki terim değildir; slop99 geçmezken slop100 geçebilir. Bu ayar kaynak dizisinin sınırını phrase aramasında korur; bir olay dizisi ilişkisi kurmaz. [Phrase/slop](https://lucene.apache.org/core/9_12_3/queryparser/org/apache/lucene/queryparser/classic/package-summary.html), [position_increment_gap](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/position-increment-gap). Kaynaklar 21 Ekim 2026 tarihinde kontrol edildi.

```meta
dil: lucene
```
:::

::: anlat Fuzzy yazım yakınlığıdır
`user.name:report~1` tek terime bir editlik bulanık eşleşme uygular. Ekleme, silme, değiştirme ve komşu karakter yer değiştirmesi native Lucene fuzzy sorgusunun kurallarıyla hesaplanır. Bu örnekte report, reports ve reprot kabul edilir; repXXt iki değiştirme gerektirir. Keyword alanında harf büyüklüğü normalizer yoksa yine önemlidir. Fuzzy kullanıcının kimliğini veya bir hesap benzerliğinin güvenlik anlamını kanıtlamaz.

```lucene
user.name:report~1
```

`"iki terim"~1` phrase yakınlığı, `terim~1` fuzzy edit uzaklığıdır. Aynı ~ işareti farklı sorgu yapılarına bağlanır. Fuzzy'nin kısa terimlerde ek ölçek kısıtları vardır; “uzaklık N ise tüm kısa sözcükler de geçer” genellemesi yapma. Bu tezgâh fuzzy/regex/jokeri yalnız keyword ve text alanlarında destekler; sayı/tarihe uygulamayı reddeder. [Lucene FuzzyQuery](https://lucene.apache.org/core/9_12_3/core/org/apache/lucene/search/FuzzyQuery.html).

```meta
dil: lucene
```
:::

::: tahmin
Sorguyu çalıştırmadan önce dönecek kimlikleri sırayla tahmin et. Gerçek Lucene motoru kullanılacak. Context sıralaması yoksa belge giriş sırası korunur; bütün veri aşağıdadır.

```lucene
message:"failed login"~1
```

```stdin
{
  "dil": "lucene",
  "mapping": {
    "message": {
      "type": "text",
      "analyzer": "standard"
    },
    "user.name": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "message": "Failed login detected"
    },
    {
      "id": "b",
      "message": "failed remote login"
    },
    {
      "id": "c",
      "message": "login failed"
    },
    {
      "id": "d",
      "message": "failed very remote login"
    },
    {
      "id": "e",
      "message": [
        "failed",
        "login"
      ]
    },
    {
      "id": "f",
      "message": "failed logging"
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
b
```

c ters sıradır ve iki konum hareketi ister. d iki ara terim taşır; e ayrı text dizi değerlerinin 100 konum aralığına takılır; f login terimi değildir.
:::

::: gorev Bir ara terimli phrase adayları
message içinde failed login phrase araması yap; slop tam 1 olsun. Sırayı ters çeviren ve iki ara terimli örneği alma. Ayrı dizi elemanlarını komşu sayma.

Editöre yalnız Lucene sorgusu yaz. `stdin` eşlemeyi, belgeleri ve bağımsız zaman/sıralama bağlamını taşır. Testte `eslesenler()` senin sorgunun kimliklerini döndürür; `eslesenler(belge_listesi)` aynı mapping/context ile yeni belgeleri sınar. Python kodu yazman gerekmiyor.

```starter
*:*
```

```stdin
{
  "dil": "lucene",
  "mapping": {
    "message": {
      "type": "text",
      "analyzer": "standard"
    },
    "user.name": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "message": "Failed login detected"
    },
    {
      "id": "b",
      "message": "failed remote login"
    },
    {
      "id": "c",
      "message": "login failed"
    },
    {
      "id": "d",
      "message": "failed very remote login"
    },
    {
      "id": "e",
      "message": [
        "failed",
        "login"
      ]
    },
    {
      "id": "f",
      "message": "failed logging"
    }
  ],
  "context": {}
}
```

```meta
dil: lucene
```

```test
eq(eslesenler(), ['a', 'b'], "ana korpus")
eq(eslesenler([{'id': 'x', 'message': 'FAILED, LOGIN'}, {'id': 'y', 'message': 'failed x login'}, {'id': 'z', 'message': 'login failed'}, {'id': 'w', 'message': 'failed x y login'}]), ['x', 'y'], "değişen korpus 1")
eq(eslesenler([{'id': 'p', 'message': ['failed', 'login']}, {'id': 'q', 'message': 'unrelated'}, {'id': 'r', 'message': 'prefix failed login suffix'}]), ['r'], "değişen korpus 2")
```

```solution
message:"failed login"~1
```

```hint
Çift tırnaklı phrase sonuna ~1 ekle; tırnaksız iki terim aynı sorgu değildir.
```
:::

::: gorev Tek editlik kullanıcı terimini ara
user.name keyword alanında report terimine fuzzy uzaklığı 1 olanları seç. Harf duyarlılığını koru; normalizer ekleme.

Editöre yalnız Lucene sorgusu yaz. `stdin` eşlemeyi, belgeleri ve bağımsız zaman/sıralama bağlamını taşır. Testte `eslesenler()` senin sorgunun kimliklerini döndürür; `eslesenler(belge_listesi)` aynı mapping/context ile yeni belgeleri sınar. Python kodu yazman gerekmiyor.

```starter
*:*
```

```stdin
{
  "dil": "lucene",
  "mapping": {
    "message": {
      "type": "text",
      "analyzer": "standard"
    },
    "user.name": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "user.name": "report"
    },
    {
      "id": "b",
      "user.name": "reprot"
    },
    {
      "id": "c",
      "user.name": "reports"
    },
    {
      "id": "d",
      "user.name": "repXXt"
    },
    {
      "id": "e",
      "user.name": "other"
    }
  ],
  "context": {}
}
```

```meta
dil: lucene
```

```test
eq(eslesenler(), ['a', 'b', 'c'], "ana korpus")
eq(eslesenler([{'id': 'x', 'user.name': 'repor'}, {'id': 'y', 'user.name': 'reXort'}, {'id': 'z', 'user.name': 'XXport'}, {'id': 'w'}]), ['x', 'y'], "değişen korpus 1")
eq(eslesenler([{'id': 'p', 'user.name': ['other', 'report']}, {'id': 'q', 'user.name': 'REPORT'}, {'id': 'r', 'user.name': 'rport'}]), ['p', 'r'], "değişen korpus 2")
```

```solution
user.name:report~1
```

```hint
Terim tırnaksız tek sözcük ve sonu ~1; iki editli adaylar testte dışarıda kalır.
```
:::
