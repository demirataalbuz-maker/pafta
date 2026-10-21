---
id: el05
title: Jokerler · Literal Karakter ve Kaçış
summary: KQL yalnız yıldız jokerini kullanır; ? literal, kaçırılmış yıldız literal; quoted değer ve daraltılmış text joker sınırı.
---

::: anlat Yıldız ile soru işareti aynı işlevde değil
KQL'de joker yalnız `*` karakteridir; sıfır veya daha çok karakteri temsil eder. `process.name: svc*` bu keyword alanda svc, svc-agent ve svc-test gibi tam terimleri seçer. `?` ise Lucene query-string'deki tek karakter jokeri gibi davranmaz: KQL `code: svc?*`, gerçek soru işaretinden sonra herhangi bir ek arar.

Normalizer olmayan keyword'de harf farkı korunur. Lowercase normalizer tanımlanırsa terim ve desen aynı normalizasyonu görür. Text jokeri native indeks terimlerinde çalışır; bir message dizesinin tamamına genel Python regex uygulanmaz.

Bu tezgâhta başta yıldız açık: `*agent` yazılabilir. Gerçek Kibana'da query:allowLeadingWildcards ayarını ayrıca kontrol et; baştaki joker maliyetli olabilir. Kaynak: [KQL jokerleri](https://www.elastic.co/docs/reference/query-languages/kql).

```meta
dil: kibana
```

```stdin
{
  "dil": "kibana",
  "mapping": {
    "process.name": {
      "type": "keyword"
    },
    "file.name": {
      "type": "keyword"
    },
    "event.action": {
      "type": "keyword"
    },
    "code": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "process.name": "svc-agent",
      "file.name": "report?2026.txt",
      "event.action": "read",
      "code": "svc?worker"
    },
    {
      "id": "b",
      "process.name": "svc-test",
      "file.name": "report12026.txt",
      "event.action": "read",
      "code": "svcAworker"
    },
    {
      "id": "c",
      "process.name": "svc",
      "file.name": "report?",
      "event.action": "read",
      "code": "svc?"
    },
    {
      "id": "d",
      "process.name": "Svc-agent",
      "file.name": "Report?2026.txt",
      "event.action": "read",
      "code": "Svc?worker"
    },
    {
      "id": "e",
      "process.name": "xsvc-agent",
      "file.name": "report?2026.txt",
      "event.action": "write",
      "code": "svc*worker"
    },
    {
      "id": "f",
      "process.name": "svc-test-extra",
      "file.name": "report?*",
      "event.action": "read"
    },
    {
      "id": "yok"
    }
  ],
  "context": {}
}
```

```kibana
process.name: svc*
```
:::

::: anlat Kaçış, iki dilin özelliklerini birbirine eklemez
`file.name: report\**`, report sonrasında literal yıldız ve ardından joker ister. `file.name: "report*"` ise yalnız literal report* değerini arar. Literal iki nokta için `url: https\://example.test/` veya tırnaklı tam URL kullan. Boşluklu keyword değerini tırnaklamak okunaklıdır; tırnaksız boşluklu değer de bir keyword değeridir. Çift tırnak içindeki tırnak/backslash ayrıca kaçırılır.

Regex `/.../`, fuzzy `~1`, phrase slop ve boost bu KQL görevlerinin sözdizimi değildir; tezgâh bunları açık hata olarak reddeder. Bunları keyword literalinde arayacaksan çift tırnak kullan. Alan adında joker ve alansız arama da bu tezgâhın sınırları dışında.

Ayrıca text alanında **boşluklu karma joker değeri** bu motorda reddedilir: Kibana onu query_string'e geçirerek başka terim mantığı kurabilir. Ayrı `AND`/`OR` koşulları yaz. Keyword boşluklu joker deseni desteklenir. Kaynak: [Kaçış kuralları](https://www.elastic.co/docs/reference/query-languages/kql).

```meta
dil: kibana
```

```stdin
{
  "dil": "kibana",
  "mapping": {
    "process.name": {
      "type": "keyword"
    },
    "file.name": {
      "type": "keyword"
    },
    "event.action": {
      "type": "keyword"
    },
    "code": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "process.name": "svc-agent",
      "file.name": "report?2026.txt",
      "event.action": "read",
      "code": "svc?worker"
    },
    {
      "id": "b",
      "process.name": "svc-test",
      "file.name": "report12026.txt",
      "event.action": "read",
      "code": "svcAworker"
    },
    {
      "id": "c",
      "process.name": "svc",
      "file.name": "report?",
      "event.action": "read",
      "code": "svc?"
    },
    {
      "id": "d",
      "process.name": "Svc-agent",
      "file.name": "Report?2026.txt",
      "event.action": "read",
      "code": "Svc?worker"
    },
    {
      "id": "e",
      "process.name": "xsvc-agent",
      "file.name": "report?2026.txt",
      "event.action": "write",
      "code": "svc*worker"
    },
    {
      "id": "f",
      "process.name": "svc-test-extra",
      "file.name": "report?*",
      "event.action": "read"
    },
    {
      "id": "yok"
    }
  ],
  "context": {}
}
```

```kibana
file.name: report\?* AND event.action: read
```
:::

::: tahmin
JSON içindeki mapping, belgeler ve context birlikte geçerli. Sorgunun döndürdüğü belge kimliklerini girdi sırasıyla tahmin et. `context.sort` verilmemişse alfabetik sıra uygulanmaz.

```meta
dil: kibana
```

```stdin
{
  "dil": "kibana",
  "mapping": {
    "process.name": {
      "type": "keyword"
    },
    "file.name": {
      "type": "keyword"
    },
    "event.action": {
      "type": "keyword"
    },
    "code": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "process.name": "svc-agent",
      "file.name": "report?2026.txt",
      "event.action": "read",
      "code": "svc?worker"
    },
    {
      "id": "b",
      "process.name": "svc-test",
      "file.name": "report12026.txt",
      "event.action": "read",
      "code": "svcAworker"
    },
    {
      "id": "c",
      "process.name": "svc",
      "file.name": "report?",
      "event.action": "read",
      "code": "svc?"
    },
    {
      "id": "d",
      "process.name": "Svc-agent",
      "file.name": "Report?2026.txt",
      "event.action": "read",
      "code": "Svc?worker"
    },
    {
      "id": "e",
      "process.name": "xsvc-agent",
      "file.name": "report?2026.txt",
      "event.action": "write",
      "code": "svc*worker"
    },
    {
      "id": "f",
      "process.name": "svc-test-extra",
      "file.name": "report?*",
      "event.action": "read"
    },
    {
      "id": "yok"
    }
  ],
  "context": {}
}
```

```kibana
code: svc?*
```

???

```text
a
c
```

`?` literal soru işaretidir; yıldızın boş eki kabul etmesi sayesinde `svc?` de eşleşir. Svc büyük harfle başladığından ve diğer değerler literal soru işareti taşımadığından elenir.
:::

::: gorev Önek ve tek değer dışlaması

process.name svc ile başlasın; tam svc-test değerini dışla. svc-test-extra dışlanmasın. Alan normalizer olmayan keyword, dolayısıyla harf farkı korunsun.

```meta
dil: kibana
```

```stdin
{
  "dil": "kibana",
  "mapping": {
    "process.name": {
      "type": "keyword"
    },
    "file.name": {
      "type": "keyword"
    },
    "event.action": {
      "type": "keyword"
    },
    "code": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "process.name": "svc-agent",
      "file.name": "report?2026.txt",
      "event.action": "read",
      "code": "svc?worker"
    },
    {
      "id": "b",
      "process.name": "svc-test",
      "file.name": "report12026.txt",
      "event.action": "read",
      "code": "svcAworker"
    },
    {
      "id": "c",
      "process.name": "svc",
      "file.name": "report?",
      "event.action": "read",
      "code": "svc?"
    },
    {
      "id": "d",
      "process.name": "Svc-agent",
      "file.name": "Report?2026.txt",
      "event.action": "read",
      "code": "Svc?worker"
    },
    {
      "id": "e",
      "process.name": "xsvc-agent",
      "file.name": "report?2026.txt",
      "event.action": "write",
      "code": "svc*worker"
    },
    {
      "id": "f",
      "process.name": "svc-test-extra",
      "file.name": "report?*",
      "event.action": "read"
    },
    {
      "id": "yok"
    }
  ],
  "context": {}
}
```

```starter
process.name: "__pafta_baslangic__"
```

```test
eq(eslesenler(), ['a', 'c', 'f'], "girdi korpusunun sabit kimlikleri")
eq(referans('process.name: svc* AND NOT process.name: svc-test'), ['a', 'c', 'f'], "referans sorgunun native sağlaması")
ek = [{'id': 'bos-ek', 'process.name': 'svc'}, {'id': 'normal', 'process.name': 'svc-prod'}, {'id': 'test', 'process.name': 'svc-test'}, {'id': 'test-uzun', 'process.name': 'svc-test-extra'}, {'id': 'harf', 'process.name': 'SVC-prod'}, {'id': 'onceki', 'process.name': 'xsvc-prod'}, {'id': 'null', 'process.name': None}]
eq(eslesenler({"documents": ek}), ['bos-ek', 'normal', 'test-uzun'], "değişen belgeler ve yakın karşı örnekler")
eq(eslesenler({"documents": list(reversed(ek))}), ['test-uzun', 'normal', 'bos-ek'], "sonuç girdi sırasını izler")
```

```solution
process.name: svc* AND NOT process.name: svc-test
```

```hint
Önek jokerini, tam değer dışlamasıyla AND kullanarak birleştir.
```

:::

::: gorev Literal soru işareti ve işlem türü

file.name tam report? önekiyle başlasın; soru işareti literal, devamında sıfır veya daha çok karakter olabilir. Ayrıca event.action tam read olsun. Başka tek karakteri ? yerine kabul etme.

```meta
dil: kibana
```

```stdin
{
  "dil": "kibana",
  "mapping": {
    "process.name": {
      "type": "keyword"
    },
    "file.name": {
      "type": "keyword"
    },
    "event.action": {
      "type": "keyword"
    },
    "code": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "process.name": "svc-agent",
      "file.name": "report?2026.txt",
      "event.action": "read",
      "code": "svc?worker"
    },
    {
      "id": "b",
      "process.name": "svc-test",
      "file.name": "report12026.txt",
      "event.action": "read",
      "code": "svcAworker"
    },
    {
      "id": "c",
      "process.name": "svc",
      "file.name": "report?",
      "event.action": "read",
      "code": "svc?"
    },
    {
      "id": "d",
      "process.name": "Svc-agent",
      "file.name": "Report?2026.txt",
      "event.action": "read",
      "code": "Svc?worker"
    },
    {
      "id": "e",
      "process.name": "xsvc-agent",
      "file.name": "report?2026.txt",
      "event.action": "write",
      "code": "svc*worker"
    },
    {
      "id": "f",
      "process.name": "svc-test-extra",
      "file.name": "report?*",
      "event.action": "read"
    },
    {
      "id": "yok"
    }
  ],
  "context": {}
}
```

```starter
process.name: "__pafta_baslangic__"
```

```test
eq(eslesenler(), ['a', 'c', 'f'], "girdi korpusunun sabit kimlikleri")
eq(referans('file.name: report\\?* AND event.action: read'), ['a', 'c', 'f'], "referans sorgunun native sağlaması")
ek = [{'id': 'soru', 'file.name': 'report?x', 'event.action': 'read'}, {'id': 'bos-ek', 'file.name': 'report?', 'event.action': 'read'}, {'id': 'yildiz', 'file.name': 'report?*', 'event.action': 'read'}, {'id': 'tek-karakter', 'file.name': 'reportAx', 'event.action': 'read'}, {'id': 'yazma', 'file.name': 'report?x', 'event.action': 'write'}, {'id': 'harf', 'file.name': 'Report?x', 'event.action': 'read'}, {'id': 'eksik', 'file.name': 'report?x'}, {'id': 'literal-yildiz', 'file.name': 'report*x', 'event.action': 'read'}]
eq(eslesenler({"documents": ek}), ['soru', 'bos-ek', 'yildiz'], "değişen belgeler ve yakın karşı örnekler")
eq(eslesenler({"documents": list(reversed(ek))}), ['yildiz', 'bos-ek', 'soru'], "sonuç girdi sırasını izler")
```

```solution
file.name: report\?* AND event.action: read
```

```hint
KQL’de ? zaten literal; \? ile açıkça gösterebilirsin. Ardından * ve read koşulu gerekir.
```

:::
