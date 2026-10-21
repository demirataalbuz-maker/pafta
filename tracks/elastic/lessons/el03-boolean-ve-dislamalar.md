---
id: el03
title: Boolean Gruplar ve Dar Dışlamalar
summary: AND/OR/NOT ile parantez; eksik alanın NOT sonucu; dar normal davranış filtresini açık kurmak.
---

::: anlat Mantık cümlesini parantezle görünür yap
`event.category: process AND (user.name: alice OR user.name: bob)` aynı belgenin process kaydı ve iki kullanıcıdan birine ait olmasını ister. OR iki ayrı olayı birleştirmez. AND koşulları tek belge üzerinde uygulanır. KQL iki olayın zaman sırasını bu Boolean ifadeyle kurmaz; bunun için sonraki EQL derslerinde başka yapı okuyacağız.

Karışık ifadelerde parantez yaz. KQL'nin Kibana çubuğu ile Elasticsearch bileşeni arasındaki öncelik ayrıntıları aynı kabul edilmemelidir. Bu yol, sonucu örtük önceliğe bağlamak yerine grupları açık yazar: `(A OR B) AND NOT C`. KQL anahtar sözcükleri AND, OR ve NOT harf duyarsızdır; keyword **alan değerleri** bununla aynı davranışı kazanmaz.

Bir filtreden tek bir parantezi çıkarmak kapsamı değiştirebilir. Gereksinimi sesli oku: “process türünde, alice veya bob kullanıcısında, lab makinesi dışında.” Test kümesinde her şartı tek başına bozulan bir kayıt olmalı; yalnız bütünüyle ilgisiz bir normal kayıt bu hataları yakalamaz.
:::

::: anlat NOT, alanı var olan normal kayıt demek değildir
`NOT host.name: lab` yazınca host.name alanı eksik belge de lab koşulunu sağlamadığı için dışlamadan geçebilir. “host adı mevcut ve lab değil” istiyorsan `host.name: * AND NOT host.name: lab` yaz. Bu ayrım alarmda veri eksikliği ile normal davranışı karıştırmamak için önemlidir.

Dar normal istisna, iki alan birlikteyse dışlama olabilir: `NOT (user.name: svc_backup AND process.parent.name: backup-agent)`. Aynı servis hesabının farklı üst süreçten etkinliği dışarıda kalmamalı. Hesabı bütünüyle allowlist'e almak, gereksinimden daha geniş bir kör alan yaratır.

Python'da `and`, `or`, `not` Boolean bağlantılarıdır; `x in ('alice','bob')` iki olası değeri denetler. `get` ile eksik alanı None olarak okuyacağız. Bu dersin keyword alanları tek değerli ve normalizer içermez; dizi/nested semantiği bu basit modele gizlice eklenmez.

Kaynak (21 Ekim 2026): [KQL birleşik koşullar, dışlama ve bağlam farkları](https://www.elastic.co/docs/reference/query-languages/kql).
:::

::: tahmin
Aşağıdaki **Kibana KQL** filtresini ve JSON'daki mapping/bağlam varsayımlarını oku. Belirtilen sırada hangi belge kimlikleri görünür? Bu yolun sorgu bloğu okunur; Pafta Elastic sunucusunda sorgu çalıştırmaz. Gizli Python denetimi yalnız verilen sabit sorgunun açıklanan küçük modelini kontrol eder.

```kibana
event.category: process AND (user.name: alice OR user.name: bob) AND NOT host.name: lab
```

```stdin
{
  "mapping": {
    "event.category": "tek değerli keyword",
    "user.name": "tek değerli keyword",
    "host.name": "tek değerli keyword; normalizer yok"
  },
  "context": {
    "time_filter": "yok; tüm verilen belgeler kapsamda",
    "order": "girdi sırası"
  },
  "documents": [
    {
      "id": "a",
      "event.category": "process",
      "user.name": "alice",
      "host.name": "prod"
    },
    {
      "id": "b",
      "event.category": "process",
      "user.name": "bob",
      "host.name": "lab"
    },
    {
      "id": "c",
      "event.category": "network",
      "user.name": "bob",
      "host.name": "prod"
    },
    {
      "id": "d",
      "event.category": "process",
      "user.name": "bob"
    },
    {
      "id": "e",
      "event.category": "process",
      "user.name": "Alice",
      "host.name": "prod"
    }
  ]
}
```

```gercek
a
d
```

```test
import json
import sys
data = json.loads(sys.stdin.read())
for doc in data['documents']:
    if doc.get('event.category') == 'process' and doc.get('user.name') in ('alice', 'bob') and doc.get('host.name') != 'lab':
        print(doc['id'])
```

???

`a` bütün pozitif koşulları sağlar ve lab değildir. `d`de host.name yok; lab eşleşmesi yanlış olduğundan NOT doğrudur. `b` lab filtresine takılır, `c` yanlış olay türüdür, `e` keyword harf farkından elenir. Host varlığı ayrıca istenseydi d de dışlanırdı.
:::

::: gorev Varlık ve dışlama birlikte
`sec(kayitlar)` şu sabit koşulu yorumlasın: `event.category: process AND user.name: (alice OR bob) AND host.name: * AND NOT host.name: lab`. Bu görevde scalar keyword host adı varlığı, değerin None olmaması demektir; boş metin indekslenir. Zaman filtresi yok; id'ler girdi sırasında dönsün.

```starter
def sec(kayitlar):
    return []
```

```test
need('sec')
rows = [{'id':'a','event.category':'process','user.name':'alice','host.name':'prod'}, {'id':'b','event.category':'process','user.name':'bob','host.name':'lab'}, {'id':'c','event.category':'process','user.name':'bob'}, {'id':'d','event.category':'process','user.name':'bob','host.name':''}, {'id':'e','event.category':'network','user.name':'bob','host.name':'prod'}, {'id':'f','event.category':'process','user.name':'Alice','host.name':'prod'}, {'id':'g','event.category':'process','user.name':'bob','host.name':None}]
eq(sec(rows), ['a','d'], 'dışlama ve exists ayrı koşullardır')
eq(sec([{'id':'x','event.category':'process','user.name':'bob','host.name':'LAB'}]), ['x'], 'keyword değerinde büyük harf ayrıdır')
eq(sec([]), [], 'boş küme')
```

```solution
def sec(kayitlar):
    return [k['id'] for k in kayitlar if k.get('event.category') == 'process' and k.get('user.name') in ('alice','bob') and k.get('host.name') is not None and k.get('host.name') != 'lab']
```

```hint
host adı için is not None kullan; boş metni bool ile atma.
```
:::

::: gorev Servis hesabını körleştirme
`incele(kayit)` Boolean döndürsün: event.action export ise, yalnız user.name svc_backup VE process.parent.name backup-agent birlikte olduğunda dışla. Bu sabit koşulun modelidir: `event.action: export AND NOT (user.name: svc_backup AND process.parent.name: backup-agent)`. Alanlar tek değerli keyword. Diğer eylemler False; filtre alanları eksikse dar normal biçim doğrulanmadığı için export eşleşebilir.

```starter
def incele(kayit):
    return False
```

```test
need('incele')
for user, parent, expected in [('svc_backup','backup-agent',False),('svc_backup','terminal',True),('analyst','backup-agent',True),('analyst','terminal',True)]:
    eq(incele({'event.action':'export','user.name':user,'process.parent.name':parent}), expected, 'dar filtre kombinasyonu')
eq(incele({'event.action':'export'}), True, 'normal biçim alanları eksik')
eq(incele({'event.action':'view','user.name':'analyst','process.parent.name':'terminal'}), False, 'yanlış eylem')
eq(incele({}), False, 'eylem eksik')
```

```solution
def incele(kayit):
    normal = kayit.get('user.name') == 'svc_backup' and kayit.get('process.parent.name') == 'backup-agent'
    return kayit.get('event.action') == 'export' and not normal
```

```hint
Filtrede iki alan AND; sonra bütün filtreyi not ile tersine çevir.
```
:::
