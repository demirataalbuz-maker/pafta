---
id: el13
title: EQL · Kategori ve Gerçek Sorgu
summary: EQL sözdizimiyle sorgu yaz; category, keyword eşitliği ve sayısal aralıkları yerel motorla çalıştır.
---

::: anlat event category where koşul
`process where process.name == "cmd.exe"` iki şart ister: category alanındaki değer `process`, ad alanındaki değer tam `cmd.exe`. Varsayılan kategori alanı ECS `event.category`'dir; `any` kategori kısıtını kaldırır ve kategori değeri olmayan olayı da kapsayabilir. EQL, ES|QL'nin `FROM ... | WHERE` dili değildir. Alan adları ve `==` metin eşitliği harf duyarlıdır; `==` içinde yıldız joker olmaz.

Bu yol artık EQL sorgusunu senin yazdığın çalışma yoludur. Tezgâh, açık mapping ve sentetik olaylar üzerinde sınırlı bir yerel yorumlayıcı kullanır; Elasticsearch sunucusu çalıştırmaz. Her olayın `id` kimliği benzersizdir. Sonuç timestamp, sonra açık `tiebreaker_field` sırasındadır; bu örnekte ikinci alan `id`'dir.

```eql
process where process.name == "cmd.exe"
```

```meta
dil: eql
```

```stdin
{
  "dil": "eql",
  "mapping": {
    "id": "keyword",
    "@timestamp": "date",
    "event.category": "keyword",
    "event.sequence": "long",
    "process.name": "keyword",
    "process.args_count": "long"
  },
  "documents": [
    {
      "id": "p1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "process.args_count": 0
    },
    {
      "id": "p2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "CMD.EXE",
      "process.args_count": 1
    },
    {
      "id": "p3",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "file",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "process.args_count": 2
    },
    {
      "id": "p4",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd*.exe",
      "process.args_count": 3
    },
    {
      "id": "p5",
      "@timestamp": "2026-10-21T00:00:04.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "process.args_count": 4
    },
    {
      "id": "p6",
      "@timestamp": "2026-10-21T00:00:05.000Z",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "process.args_count": 2
    }
  ],
  "context": {
    "tiebreaker_field": "id"
  }
}
```
:::

::: anlat Mapping ve ölçülebilir sınırlar
Keyword alanını tam metinle, long alanını sayıyla karşılaştır. `>= 1 and <= 3` iki ucu da içerir; `and`, `or`'dan önce bağlanır. Alanın olayda eksik olması ile mapping'de hiç olmaması farklıdır. Mapping'de olmayan normal alan sorgu hatasıdır; sonraki ders `?alan` ve null kontrolünü işler.

Yerel kapsam düz ve tek değerli keyword/long/integer/double/date/boolean alanlardır. Sorgulanan text/nested alanı, diziler, fonksiyon, aritmetik, regex ve pipe açık hata verir. Mapping normalizer/null_value/ignore_above seçenekleri de bu modelde yoktur. Tarih girişi ortak tezgâhta zonlu ISO, en fazla milisaniye hassasiyetindedir. Kaynak: [Elastic EQL syntax](https://www.elastic.co/docs/reference/query-languages/eql/eql-syntax).

```eql
process where process.args_count >= 1 and process.args_count <= 3
```

```meta
dil: eql
```

```stdin
{
  "dil": "eql",
  "mapping": {
    "id": "keyword",
    "@timestamp": "date",
    "event.category": "keyword",
    "event.sequence": "long",
    "process.name": "keyword",
    "process.args_count": "long"
  },
  "documents": [
    {
      "id": "p1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "process.args_count": 0
    },
    {
      "id": "p2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "CMD.EXE",
      "process.args_count": 1
    },
    {
      "id": "p3",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "file",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "process.args_count": 2
    },
    {
      "id": "p4",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd*.exe",
      "process.args_count": 3
    },
    {
      "id": "p5",
      "@timestamp": "2026-10-21T00:00:04.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "process.args_count": 4
    },
    {
      "id": "p6",
      "@timestamp": "2026-10-21T00:00:05.000Z",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "process.args_count": 2
    }
  ],
  "context": {
    "tiebreaker_field": "id"
  }
}
```
:::

::: tahmin
Mapping ve altı olay girdide açıkça verilmiştir. `p6` category taşımıyor. Tam, harf duyarlı adı ve category koşulunu birlikte değerlendir; çıktı kimlikleri hangi sırayla gelir?

```meta
dil: eql
```

```stdin
{
  "dil": "eql",
  "mapping": {
    "id": "keyword",
    "@timestamp": "date",
    "event.category": "keyword",
    "event.sequence": "long",
    "process.name": "keyword",
    "process.args_count": "long"
  },
  "documents": [
    {
      "id": "p1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "process.args_count": 0
    },
    {
      "id": "p2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "CMD.EXE",
      "process.args_count": 1
    },
    {
      "id": "p3",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "file",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "process.args_count": 2
    },
    {
      "id": "p4",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd*.exe",
      "process.args_count": 3
    },
    {
      "id": "p5",
      "@timestamp": "2026-10-21T00:00:04.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "process.args_count": 4
    },
    {
      "id": "p6",
      "@timestamp": "2026-10-21T00:00:05.000Z",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "process.args_count": 2
    }
  ],
  "context": {
    "tiebreaker_field": "id"
  }
}
```

```eql
process where process.name == "cmd.exe"
```

???

`p1` ve `p5` iki koşulu da sağlar. `p2` büyük harflidir; `p3` file kategorisindedir; `p4` literal yıldız taşır; `p6` category koşulunu sağlamaz. `==` yıldızı genişletmez.

```text
p1
p5
```
:::

::: gorev Yalnız tam process adı
`process` kategorisinde `process.name` değeri tam, harf duyarlı `cmd.exe` olan olayları döndüren EQL sorgusu yaz. Joker, alt dize veya başka kategori kabul edilmesin.

```meta
dil: eql
```

```stdin
{
  "dil": "eql",
  "mapping": {
    "id": "keyword",
    "@timestamp": "date",
    "event.category": "keyword",
    "event.sequence": "long",
    "process.name": "keyword",
    "process.args_count": "long"
  },
  "documents": [
    {
      "id": "p1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "process.args_count": 0
    },
    {
      "id": "p2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "CMD.EXE",
      "process.args_count": 1
    },
    {
      "id": "p3",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "file",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "process.args_count": 2
    },
    {
      "id": "p4",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd*.exe",
      "process.args_count": 3
    },
    {
      "id": "p5",
      "@timestamp": "2026-10-21T00:00:04.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "process.args_count": 4
    },
    {
      "id": "p6",
      "@timestamp": "2026-10-21T00:00:05.000Z",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "process.args_count": 2
    }
  ],
  "context": {
    "tiebreaker_field": "id"
  }
}
```

```starter
any where false
```

```test
eq(eslesenler(),["p1","p5"],"dersteki gerçek sorgu sonucu")
eq(eslesenler(veri={"documents":list(reversed(korpus["documents"]))}),["p1","p5"],"girdi sırası değil timestamp+tiebreaker sırası")
from datetime import datetime, timedelta, timezone
def olay(kimlik,t_ms=0,kategori="process",sira=0,**alanlar):
    zaman=datetime(2026,10,21,tzinfo=timezone.utc)+timedelta(milliseconds=t_ms)
    e={"id":kimlik,"@timestamp":zaman.isoformat(timespec="milliseconds").replace("+00:00","Z"),"event.category":kategori,"event.sequence":sira}
    e.update(alanlar)
    return e
docs=[olay("a",0,**{"process.name":"cmd.exe"}),olay("b",1,**{"process.name":"CMD.EXE"}),olay("c",2,"file",**{"process.name":"cmd.exe"}),olay("d",3,**{"process.name":"cmd.exe.bak"}),olay("e",4,**{"process.name":"cmd*.exe"}),olay("f",5)]
eq(eslesenler(veri={"documents":docs}),["a"],"kategori, harf, tam değer ve eksiklik ayrı karşı örnekler")
eq(eslesenler(veri={"documents":[olay("unicode",0,**{"process.name":"çmd.exe"})]}),[],"UTF-8 tam eşitlik joker değildir")
```

```solution
process where process.name == "cmd.exe"
```

```hint
process where process.name == "cmd.exe". == ile : aynı harf davranışını vermez.
```
:::

::: gorev İki kapalı sayı sınırı
`process` olaylarından `process.args_count` 1 ile 3 arasında, iki uç dahil olanları seç. File kategorisi, eksik/null sayaç, 0 ve 4 dışarıda olsun. EQL'de zincirleme `1 <= alan <= 3` yerine iki karşılaştırma yaz.

```meta
dil: eql
```

```stdin
{
  "dil": "eql",
  "mapping": {
    "id": "keyword",
    "@timestamp": "date",
    "event.category": "keyword",
    "event.sequence": "long",
    "process.name": "keyword",
    "process.args_count": "long"
  },
  "documents": [
    {
      "id": "p1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "process.args_count": 0
    },
    {
      "id": "p2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "CMD.EXE",
      "process.args_count": 1
    },
    {
      "id": "p3",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "file",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "process.args_count": 2
    },
    {
      "id": "p4",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd*.exe",
      "process.args_count": 3
    },
    {
      "id": "p5",
      "@timestamp": "2026-10-21T00:00:04.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "process.args_count": 4
    },
    {
      "id": "p6",
      "@timestamp": "2026-10-21T00:00:05.000Z",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "process.args_count": 2
    }
  ],
  "context": {
    "tiebreaker_field": "id"
  }
}
```

```starter
any where false
```

```test
eq(eslesenler(),["p2","p4"],"dersteki gerçek sorgu sonucu")
eq(eslesenler(veri={"documents":list(reversed(korpus["documents"]))}),["p2","p4"],"girdi sırası değil timestamp+tiebreaker sırası")
from datetime import datetime, timedelta, timezone
def olay(kimlik,t_ms=0,kategori="process",sira=0,**alanlar):
    zaman=datetime(2026,10,21,tzinfo=timezone.utc)+timedelta(milliseconds=t_ms)
    e={"id":kimlik,"@timestamp":zaman.isoformat(timespec="milliseconds").replace("+00:00","Z"),"event.category":kategori,"event.sequence":sira}
    e.update(alanlar)
    return e
docs=[olay(str(i),i,**{"process.args_count":n}) for i,n in enumerate((0,1,2,3,4))]
docs.extend([olay("wrong",6,"file",**{"process.args_count":2}),olay("missing",7),olay("null",8,**{"process.args_count":None})])
eq(eslesenler(veri={"documents":docs}),["1","2","3"],"alt/eşit/üst ve category bağımsızlığı")
eq(eslesenler(veri={"documents":[olay("negative",0,**{"process.args_count":-1})]}),[],"negatif sayı dışarı")
```

```solution
process where process.args_count >= 1 and process.args_count <= 3
```

```hint
process category; args_count >= 1 and args_count <= 3.
```
:::
