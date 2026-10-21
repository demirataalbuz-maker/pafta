---
id: el14
title: EQL · Liste, Kalıp ve Null
summary: in/in~, like/like~ ve ?alan ile sorgu yaz; literal null denetimini bilinmeyen karşılaştırmadan ayır.
---

::: anlat Liste değerleriyle kalıbı karıştırma
`in ("cmd.exe", "powershell.exe")` değer listesidir; `in~` aynı listede ASCII harf farkını kaldırır. `like "cmd?.exe"` harf duyarlı kalıptır; `like~` ve `:` harf duyarsız joker eşleşmesidir. `?` tam bir, `*` sıfır veya daha çok karakter tutar. Köşeli parantez bir glob karakter sınıfı değildir. `in ("cmd*.exe")` yıldızı literal sayar.

EQL metinleri çift tırnaklı veya raw üç çift tırnaklıdır. String kaçışları ile wildcard kuralları ayrı katmanlardır: backslash, * veya ? jokerini devre dışı bırakan bir EQL pattern operatörü değildir. Literal yıldızı tam karşılaştırmak için `==` kullan. Yerel harf duyarsız işlemler yalnız ASCII değerleri kabul eder; Unicode exact `==` desteklidir, Unicode insensitive açık hatadır.

```eql
process where process.name like~ "cmd?.exe"
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
    "user.id": "keyword"
  },
  "documents": [
    {
      "id": "m1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "CMD.EXE",
      "user.id": "u1"
    },
    {
      "id": "m2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "user.id": null
    },
    {
      "id": "m3",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "powershell.exe"
    },
    {
      "id": "m4",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "PowerShell.Exe",
      "user.id": ""
    },
    {
      "id": "m5",
      "@timestamp": "2026-10-21T00:00:04.000Z",
      "event.category": "file",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "user.id": "u2"
    },
    {
      "id": "m6",
      "@timestamp": "2026-10-21T00:00:05.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd1.exe",
      "user.id": "u3"
    },
    {
      "id": "m7",
      "@timestamp": "2026-10-21T00:00:06.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd12.exe",
      "user.id": "u4"
    }
  ],
  "context": {
    "tiebreaker_field": "id"
  }
}
```
:::

::: anlat Null, false değildir
`?user.id` mapping'de olmayan alanı null kabul eder. Mapping'de olan ama olayda eksik/null bulunan değer de null'dır. Boş keyword metni `""` geçerli bir değerdir. EQL'nin `== null` ve `!= null` ifadeleri özel varlık/yokluk denetimidir; ES|QL'nin `IS NULL` yazımıyla karıştırma.

Buna karşılık eksik `alan == "x"` sonucu bilinmeyendir; `not` bu bilinmeyeni true yapmaz. `and` için false belirleyicidir, `or` için true belirleyicidir; sadece true sonuçlu olaylar seçilir. Bu yüzden `alan != "x"` eksik değeri kendiliğinden dahil etmez. Kaynak: [Elastic EQL opsiyonel alanlar ve karşılaştırmalar](https://www.elastic.co/docs/reference/query-languages/eql/eql-syntax).

```eql
process where process.name in~ ("cmd.exe", "powershell.exe") and ?user.id != null
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
    "user.id": "keyword"
  },
  "documents": [
    {
      "id": "m1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "CMD.EXE",
      "user.id": "u1"
    },
    {
      "id": "m2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "user.id": null
    },
    {
      "id": "m3",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "powershell.exe"
    },
    {
      "id": "m4",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "PowerShell.Exe",
      "user.id": ""
    },
    {
      "id": "m5",
      "@timestamp": "2026-10-21T00:00:04.000Z",
      "event.category": "file",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "user.id": "u2"
    },
    {
      "id": "m6",
      "@timestamp": "2026-10-21T00:00:05.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd1.exe",
      "user.id": "u3"
    },
    {
      "id": "m7",
      "@timestamp": "2026-10-21T00:00:06.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd12.exe",
      "user.id": "u4"
    }
  ],
  "context": {
    "tiebreaker_field": "id"
  }
}
```
:::

::: tahmin
ASCII adlar, açık keyword mapping ve olaylar girdidedir. Null ile boş metni ve kategori farkını ayır. Sonuç hangi kimliklerden oluşur?

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
    "user.id": "keyword"
  },
  "documents": [
    {
      "id": "m1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "CMD.EXE",
      "user.id": "u1"
    },
    {
      "id": "m2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "user.id": null
    },
    {
      "id": "m3",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "powershell.exe"
    },
    {
      "id": "m4",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "PowerShell.Exe",
      "user.id": ""
    },
    {
      "id": "m5",
      "@timestamp": "2026-10-21T00:00:04.000Z",
      "event.category": "file",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "user.id": "u2"
    },
    {
      "id": "m6",
      "@timestamp": "2026-10-21T00:00:05.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd1.exe",
      "user.id": "u3"
    },
    {
      "id": "m7",
      "@timestamp": "2026-10-21T00:00:06.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd12.exe",
      "user.id": "u4"
    }
  ],
  "context": {
    "tiebreaker_field": "id"
  }
}
```

```eql
process where process.name in~ ("cmd.exe", "powershell.exe") and ?user.id != null
```

???

`m1` ve `m4` ad listesine harf duyarsız uyar ve kullanıcı değeri taşır. m4'te boş metin null değildir. m2 null, m3 eksik kullanıcı taşır; m5 yanlış kategori, m6/m7 yanlış adlardır.

```text
m1
m4
```
:::

::: gorev Ad listesi ve kullanıcı varlığı
Process kategorisinde adı ASCII harf duyarsız `cmd.exe` veya `powershell.exe` olan, ayrıca `?user.id` değeri null olmayan olayları seç. Boş kullanıcı metni kabul; eksik veya null kullanıcı dışarıda. Alan mapping'de hiç yoksa opsiyonel alan nedeniyle hata yerine boş sonuç gelmeli.

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
    "user.id": "keyword"
  },
  "documents": [
    {
      "id": "m1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "CMD.EXE",
      "user.id": "u1"
    },
    {
      "id": "m2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "user.id": null
    },
    {
      "id": "m3",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "powershell.exe"
    },
    {
      "id": "m4",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "PowerShell.Exe",
      "user.id": ""
    },
    {
      "id": "m5",
      "@timestamp": "2026-10-21T00:00:04.000Z",
      "event.category": "file",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "user.id": "u2"
    },
    {
      "id": "m6",
      "@timestamp": "2026-10-21T00:00:05.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd1.exe",
      "user.id": "u3"
    },
    {
      "id": "m7",
      "@timestamp": "2026-10-21T00:00:06.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd12.exe",
      "user.id": "u4"
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
eq(eslesenler(),["m1","m4"],"dersteki gerçek sorgu sonucu")
eq(eslesenler(veri={"documents":list(reversed(korpus["documents"]))}),["m1","m4"],"girdi sırası değil timestamp+tiebreaker sırası")
from datetime import datetime, timedelta, timezone
def olay(kimlik,t_ms=0,kategori="process",sira=0,**alanlar):
    zaman=datetime(2026,10,21,tzinfo=timezone.utc)+timedelta(milliseconds=t_ms)
    e={"id":kimlik,"@timestamp":zaman.isoformat(timespec="milliseconds").replace("+00:00","Z"),"event.category":kategori,"event.sequence":sira}
    e.update(alanlar)
    return e
docs=[olay("a",0,**{"process.name":"CMD.EXE","user.id":"u"}),olay("b",1,**{"process.name":"PowerShell.Exe","user.id":""}),olay("c",2,**{"process.name":"cmd.exe","user.id":None}),olay("d",3,**{"process.name":"cmd.exe"}),olay("e",4,"file",**{"process.name":"cmd.exe","user.id":"u"}),olay("f",5,**{"process.name":"cmd*.exe","user.id":"u"}),olay("g",6,**{"process.name":"powershell.exe.bak","user.id":"u"})]
eq(eslesenler(veri={"documents":docs}),["a","b"],"harf/listenin tam değeri/category/null birbirinden bağımsız")
mapped=dict(korpus["mapping"]); del mapped["user.id"]
eq(eslesenler(veri={"mapping":mapped,"documents":docs}),[],"unmapped kaynak anahtarı indekslenmiş değer değildir")
```

```solution
process where process.name in~ ("cmd.exe", "powershell.exe") and ?user.id != null
```

```hint
in~ listesi and ?user.id != null. ifadenin varlık denetimi boş metni dışlamaz.
```
:::

::: gorev Tam bir karakterlik boşluk
Process kategorisindeki adı `cmd?.exe` kalıbına ASCII harf duyarsız uyanları seç. `cmd.exe` ve `cmd12.exe` uymasın; `CMD1.EXE` ve `cmd*.exe` uysun: girişteki yıldız burada tek karakterlik bir veridir. Başka kategori veya sonuna .bak eklenmiş ad dışarıda.

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
    "user.id": "keyword"
  },
  "documents": [
    {
      "id": "m1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "CMD.EXE",
      "user.id": "u1"
    },
    {
      "id": "m2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "user.id": null
    },
    {
      "id": "m3",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "powershell.exe"
    },
    {
      "id": "m4",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "PowerShell.Exe",
      "user.id": ""
    },
    {
      "id": "m5",
      "@timestamp": "2026-10-21T00:00:04.000Z",
      "event.category": "file",
      "event.sequence": 0,
      "process.name": "cmd.exe",
      "user.id": "u2"
    },
    {
      "id": "m6",
      "@timestamp": "2026-10-21T00:00:05.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd1.exe",
      "user.id": "u3"
    },
    {
      "id": "m7",
      "@timestamp": "2026-10-21T00:00:06.000Z",
      "event.category": "process",
      "event.sequence": 0,
      "process.name": "cmd12.exe",
      "user.id": "u4"
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
eq(eslesenler(),["m6"],"dersteki gerçek sorgu sonucu")
eq(eslesenler(veri={"documents":list(reversed(korpus["documents"]))}),["m6"],"girdi sırası değil timestamp+tiebreaker sırası")
from datetime import datetime, timedelta, timezone
def olay(kimlik,t_ms=0,kategori="process",sira=0,**alanlar):
    zaman=datetime(2026,10,21,tzinfo=timezone.utc)+timedelta(milliseconds=t_ms)
    e={"id":kimlik,"@timestamp":zaman.isoformat(timespec="milliseconds").replace("+00:00","Z"),"event.category":kategori,"event.sequence":sira}
    e.update(alanlar)
    return e
adlar=("cmd.exe","cmd1.exe","CMD1.EXE","cmd12.exe","cmd*.exe","cmd?.exe","cmd[1].exe","cmd1.exe.bak")
docs=[olay(str(i),i,**{"process.name":ad}) for i,ad in enumerate(adlar)]
docs.extend([olay("wrong",20,"file",**{"process.name":"cmd1.exe"}),olay("missing",21)])
eq(eslesenler(veri={"documents":docs}),["1","2","4","5"],"joker uzunluğu, harf ve literal veri karakterleri")
```

```solution
process where process.name like~ "cmd?.exe"
```

```hint
like~ "cmd?.exe"; in~ joker genişletmez, like ise büyük harfi dışlar.
```
:::
