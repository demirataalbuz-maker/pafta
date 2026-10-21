---
id: el06
title: Nested Alanlar ve KQL Araştırma Projesi
summary: Aynı çocuk nesnesinde birleşen koşullar; object düzleştirmesinin farkı; zaman, miktar ve dar dışlama içeren mini inceleme.
---

::: anlat Bir çocuktan ad, diğerinden rol alma
Bir belgede kullanıcı nesneleri dizisi düşün: alice/reader ve bob/admin. `alice` adlı bir kullanıcı ile `admin` rolü belgede ayrı ayrı bulunur; ama alice admin değildir. Mapping `nested` olduğunda `user:{ name: alice AND role: admin }`, iki koşulu **aynı çocuk nesnesinde** arar.

Bu yazımın anlamı mapping'e bağlıdır. Normal `object` dizileri alanları düzleştirerek ilişkiyi kaybedebilir; nested ise çocukları ayrı sorgu bağlamında korur. Verinin JSON'da dizi görünmesi kendi başına nested mapping kanıtı değildir. Kaynak JSON'a bakmakla yetinme, mapping'i doğrula.

Bu dersin `user` alanı nested, alt name ve role alanları tek değerli, normalizer olmayan keyword'dür. Python karşılığı `any(cocuk.get('name') == 'alice' and cocuk.get('role') == 'admin' for cocuk in kullanicilar)` olabilir. AND aynı döngü öğesinin içinde olmalı. İki bağımsız any ile başka çocukların verisini birleştirme.
:::

::: anlat Proje: filtreyi bir araştırma sözleşmesine çevir
Mini projede yalnız export eylemi, belirli bir miktar eşiği, sabit UTC araştırma penceresi ve aynı çocukta external/owner ilişkisi aranır. Üst seviyede iki alanın birleşimiyle tanımlı onaylı yedekleme işini dar biçimde dışlarız. Bu tek belge sorgusudur; birden fazla olayın sırasını veya sayısını hesaplamaz.

Gereksinimi parçalara ayır: mapping ve gerekli alanlar; pozitif davranış; aynı çocuk şartı; zaman sınırı; normal istisna; sonuç sırası. Testler eşik altı/eşik/eşik üstü, bitiş anı, bölünmüş çocuklar ve farklı normal filtre kombinasyonlarını kapsar. Bir koşulu çıkarınca hâlâ geçen birkaç örnek, o koşulun gereksiz olduğunu kanıtlamaz.

`get('user', [])` eksik diziyi boş kabul eder; bu görevlerde alan listesi geçerli nesnelerden oluşur. `datetime` yardımcıları önceki paftada hazırlandı. Projede rastgele KQL metni yorumlanmaz; verilen sabit gereksinim Python fonksiyonuna çevrilir. Bu kontrol, canlı Elastic mapping ve sorgu çevirisinin yerini almaz. Gerçek araştırmada ham olumlu/olumsuz örneklerle aynı sorgu native ortamda ayrıca sınanır.

Kaynaklar (21 Ekim 2026): [KQL nested sözdizimi](https://www.elastic.co/docs/reference/query-languages/kql), [nested mapping](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/nested).
:::

::: tahmin
Aşağıdaki **Kibana KQL** filtresini ve JSON'daki mapping/bağlam varsayımlarını oku. Belirtilen sırada hangi belge kimlikleri görünür? Bu yolun sorgu bloğu okunur; Pafta Elastic sunucusunda sorgu çalıştırmaz. Gizli Python denetimi yalnız verilen sabit sorgunun açıklanan küçük modelini kontrol eder.

```kibana
user:{ name: alice AND role: admin }
```

```stdin
{
  "mapping": {
    "user": "nested",
    "user.name": "tek değerli keyword; normalizer yok",
    "user.role": "tek değerli keyword; normalizer yok"
  },
  "context": {
    "order": "girdi sırası",
    "time_filter": "yok",
    "nested_scope": "name ve role aynı çocukta"
  },
  "documents": [
    {
      "id": "a",
      "user": [
        {
          "name": "alice",
          "role": "admin"
        }
      ]
    },
    {
      "id": "b",
      "user": [
        {
          "name": "alice",
          "role": "reader"
        },
        {
          "name": "bob",
          "role": "admin"
        }
      ]
    },
    {
      "id": "c",
      "user": [
        {
          "name": "bob",
          "role": "reader"
        },
        {
          "name": "alice",
          "role": "admin"
        }
      ]
    },
    {
      "id": "d",
      "user": [
        {
          "name": "Alice",
          "role": "admin"
        }
      ]
    },
    {
      "id": "e",
      "user": []
    },
    {
      "id": "f"
    }
  ]
}
```

```gercek
a
c
```

```test
import json
import sys
data = json.loads(sys.stdin.read())
for doc in data['documents']:
    if any(child.get('name') == 'alice' and child.get('role') == 'admin' for child in doc.get('user', [])):
        print(doc['id'])
```

???

`a` ve `c`de tek bir çocuk alice/admin çiftini taşıyor. `b`de şartlar iki ayrı çocukta; nested sorgu bunları birleştirmez. `d` keyword harf farkından, `e` ve `f` uygun çocuk olmamasından elenir.
:::

::: gorev Aynı çocukta ad ve rol
`yetkili(kayit)` şu sabit sorgunun Boolean anlamını kursun: `user:{ name: alice AND role: admin }`. user nested dizisi, çocuklar name/role scalar keyword taşır. Eksik user boş liste; alt alanlar eksik olabilir. Çocuklar arasında koşul birleştirme. Büyük harfi normalleştirme.

```starter
def yetkili(kayit):
    return False
```

```test
need('yetkili')
eq(yetkili({'user':[{'name':'alice','role':'admin'}]}), True, 'aynı çocuk')
eq(yetkili({'user':[{'name':'alice','role':'reader'},{'name':'bob','role':'admin'}]}), False, 'ayrı çocuklar birleşmez')
eq(yetkili({'user':[{'name':'bob','role':'reader'},{'name':'alice','role':'admin'}]}), True, 'çocuk sırası değişebilir')
eq(yetkili({'user':[{'name':'Alice','role':'admin'}]}), False, 'keyword harf farkı')
eq(yetkili({'user':[{'name':'alice'},{'role':'admin'}]}), False, 'eksik alanlı ayrı çocuklar')
eq(yetkili({'user':[]}), False, 'boş dizi')
eq(yetkili({}), False, 'alan yok')
```

```solution
def yetkili(kayit):
    return any(cocuk.get('name') == 'alice' and cocuk.get('role') == 'admin' for cocuk in kayit.get('user', []))
```

```hint
Tek any içinde her çocuk için iki şartı and ile denetle.
```
:::

::: gorev Proje · Export araştırması
Sabit araştırma sorgusunu oku:

```kibana
event.action: export AND transfer.bytes >= 1024 AND
@timestamp >= "2026-10-21T09:00:00Z" AND @timestamp < "2026-10-21T09:05:00Z" AND
user:{ type: external AND role: owner } AND
NOT (actor.name: svc_backup AND job.id: approved_daily)
```

`arastir(kayitlar)` eşleşen id'leri girdi sırasında döndürsün. @timestamp date ve UTC; transfer.bytes tek değerli long; user nested, type/role keyword. Diğer alanlar scalar keyword ve normalizer yok. Eksik zaman/miktar veya uygun çocuk yoksa dışla. Yalnız actor.name svc_backup ve job.id approved_daily **birlikteyse** dışla; tek başına biri yeterli değil. Zamanlar geçerli; bozuk veri/parser yazmak kapsam dışı.

```starter
from datetime import datetime

def utc(metin):
    return datetime.fromisoformat(metin.replace('Z', '+00:00'))

def arastir(kayitlar):
    return []
```

```test
need('arastir')
def doc(identifier, **changes):
    row = {'id':identifier,'event.action':'export','transfer.bytes':1024,'@timestamp':'2026-10-21T09:00:00Z','user':[{'type':'external','role':'owner'}],'actor.name':'analyst','job.id':'manual'}
    row.update(changes)
    return row
rows = [doc('a'),doc('b',**{'transfer.bytes':1023}),doc('c',**{'transfer.bytes':1025}),doc('d',**{'@timestamp':'2026-10-21T08:59:59Z'}),doc('e',**{'@timestamp':'2026-10-21T09:04:59Z'}),doc('f',**{'@timestamp':'2026-10-21T09:05:00Z'}),doc('g',**{'@timestamp':'2026-10-21T09:05:01Z'}),doc('h',**{'event.action':'view'}),doc('i',**{'user':[{'type':'external','role':'reader'},{'type':'internal','role':'owner'}]}),doc('j',**{'actor.name':'svc_backup','job.id':'approved_daily'}),doc('k',**{'actor.name':'svc_backup','job.id':'manual'}),doc('l',**{'actor.name':'analyst','job.id':'approved_daily'})]
eq(arastir(rows), ['a','c','e','k','l'], 'eşik, zaman, nested ve dar filtre')
for field in ('@timestamp','transfer.bytes','user','event.action'):
    row = doc('missing'); del row[field]
    eq(arastir([row]), [], 'zorunlu alan eksik: '+field)
eq(arastir([doc('null',**{'transfer.bytes':None}),doc('nt',**{'@timestamp':None})]), [], 'null zorunlu alan')
eq(arastir([doc('upper',**{'user':[{'type':'External','role':'owner'}]})]), [], 'keyword harf farkı')
eq(arastir(list(reversed([doc('z'),doc('a')]))), ['a','z'], 'girdi sırası korunur')
eq(arastir([]), [], 'boş küme')
```

```solution
from datetime import datetime

def utc(metin):
    return datetime.fromisoformat(metin.replace('Z', '+00:00'))

def arastir(kayitlar):
    start, end = utc('2026-10-21T09:00:00Z'), utc('2026-10-21T09:05:00Z')
    sonuc = []
    for k in kayitlar:
        stamp, miktar = k.get('@timestamp'), k.get('transfer.bytes')
        cocuk_var = any(c.get('type') == 'external' and c.get('role') == 'owner' for c in k.get('user', []))
        normal = k.get('actor.name') == 'svc_backup' and k.get('job.id') == 'approved_daily'
        if k.get('event.action') == 'export' and miktar is not None and miktar >= 1024 and stamp is not None and start <= utc(stamp) < end and cocuk_var and not normal:
            sonuc.append(k['id'])
    return sonuc
```

```hint
Her şartı ayrı Boolean olarak düşün; nested içinde AND, normal filtrede AND, bütün filtreyi NOT. Tüm id’leri sabitleyerek geçmeye çalışma.
```
:::
