---
id: el05
title: Jokerler, Kaçış ve Değer Grupları
summary: KQL yalnız yıldız jokeri, literal soru işareti, tırnaklı yıldız ve kaçış; keyword harf farkı ve alan değer grupları.
---

::: anlat KQL jokerini Lucene veya glob sanma
Kibana KQL'de desteklenen joker `*`dır: sıfır veya daha çok karakter. `file.name: report*.json`, report.json ve report_daily.json gibi değerleri seçebilir. `?` bu dilde “bir karakter” jokeri değildir; örneğin `report?.json` içindeki soru işareti literal karakterdir. Lucene ve shell glob kurallarını buraya taşımayacağız.

Joker keyword alanı normalizer olmadan harf farkını kaldırmaz: Report ile report farklı kalır. Tırnak içindeki yıldız ise literal yıldızdır: `file.name: "report*.json"` gerçek değerinde yıldız bulunan adı arar. Bir pattern ile yıldız içeren bir metni aramak aynı soru değildir.

Başta yıldız olan desenler geniş arama maliyeti yaratabilir; Kibana'daki `query:allowLeadingWildcards` ayarı bunları sınırlandırabilir. Bu dersteki örnekler başta sabit önek kullanır. Sayı/date/Boolean/IP alanlarına string wildcard uygulamak mapping türü hatası üretebilir; böyle bir durumda “sonuç yok” diye yorumlama.
:::

::: anlat Özel karakterleri iki dosya biçiminde karıştırma
Bir URL'deki iki nokta veya bir değerdeki parantez, sorgu sözdizimiyle karışabilir. `url.full: "https://example.invalid/a?b=1"` gibi tırnak kullanabilirsin. Tırnak içinde gerçek çift tırnak ve ters eğik çizgi kaçırılır. Örneğin Windows yolunu KQL metninde `file.path: "C:\\Logs\\audit.log"` biçiminde okursun. Aynı metni JSON'a gömmek gerekirse JSON'un kendi kaçış katmanı da eklenir.

Bir alanda birden çok değer için `user.name: (alice OR bob)` yazmak, `user.name: alice OR user.name: bob` fikrini açıkça toplar. Bunlar mevcut belge üzerinde alternatif değerlerdir, iki kullanıcının aynı anda oturum açması anlamına gelmez. Bir anahtar sözcüğü gerçek değer olarak arıyorsan tırnakla: `tag: "AND"`.

Python görevleri tek sabit patterni yorumlar. `metin.startswith('report')` öneki, `.endswith('.json')` sonu denetler. Bunlar genel wildcard yorumlayıcısı değildir ve `?` için `fnmatch` kullanmayacağız; fnmatch onu farklı yorumlar. Literal görevde normal eşitlik kullan. Bu yolla sorgu ile örneklerin anlamsal sınırını çalışıyoruz.

Kaynak (21 Ekim 2026): [KQL wildcard, escaping ve value groups](https://www.elastic.co/docs/reference/query-languages/kql).
:::

::: tahmin
Aşağıdaki **Kibana KQL** filtresini ve JSON'daki mapping/bağlam varsayımlarını oku. Belirtilen sırada hangi belge kimlikleri görünür? Bu yolun sorgu bloğu okunur; Pafta Elastic sunucusunda sorgu çalıştırmaz. Gizli Python denetimi yalnız verilen sabit sorgunun açıklanan küçük modelini kontrol eder.

```kibana
file.name: report*.json AND user.name: (alice OR bob)
```

```stdin
{
  "mapping": {
    "file.name": "tek değerli keyword; normalizer yok",
    "user.name": "tek değerli keyword; normalizer yok"
  },
  "context": {
    "order": "girdi sırası",
    "time_filter": "yok",
    "wildcard": "yalnız yıldız, tırnaksız pattern"
  },
  "documents": [
    {
      "id": "a",
      "file.name": "report.json",
      "user.name": "alice"
    },
    {
      "id": "b",
      "file.name": "report_daily.json",
      "user.name": "bob"
    },
    {
      "id": "c",
      "file.name": "Report_daily.json",
      "user.name": "alice"
    },
    {
      "id": "d",
      "file.name": "report_daily.json.bak",
      "user.name": "bob"
    },
    {
      "id": "e",
      "file.name": "report?.json",
      "user.name": "alice"
    },
    {
      "id": "f",
      "file.name": "report_daily.json",
      "user.name": "Alice"
    }
  ]
}
```

```gercek
a
b
e
```

```test
import json
import sys
data = json.loads(sys.stdin.read())
for doc in data['documents']:
    name = doc.get('file.name')
    if isinstance(name,str) and name.startswith('report') and name.endswith('.json') and doc.get('user.name') in ('alice','bob'):
        print(doc['id'])
```

???

`a`da yıldız sıfır karakteri kapsar; `b`de _daily parçasını kapsar. `e`de soru işareti normal bir karakterdir ve yıldız onu da kapsayabilir. `c` dosya adında büyük R, `f` kullanıcı adında büyük A yüzünden elenir. `d` .json ile bitmez.
:::

::: gorev Tek sabit yıldız desenini yorumla
`desen_sec(kayitlar)`, `file.name: report*.json` filtresinin bu tek değerli, normalizer olmayan keyword modelini kursun. Başta report, sonda .json; aradaki parça boş olabilir. Eksik/null ad dışarıda. id'leri girdi sırasında döndür. Rastgele desen almayacak, genel wildcard parser yazmayacak.

```starter
def desen_sec(kayitlar):
    return []
```

```test
need('desen_sec')
rows = [{'id':'a','file.name':'report.json'}, {'id':'b','file.name':'report_daily.json'}, {'id':'c','file.name':'report?.json'}, {'id':'d','file.name':'Report.json'}, {'id':'e','file.name':'xreport.json'}, {'id':'f','file.name':'report.json.bak'}, {'id':'g'}, {'id':'h','file.name':None}, {'id':'i','file.name':'report*literal.json'}]
eq(desen_sec(rows), ['a','b','c','i'], 'sıfır/çok karakter, harf ve iki sınır')
eq(desen_sec([{'id':'n','file.name':'reportxjson'},{'id':'m','file.name':'report.json'}]), ['m'], 'nokta literal ve son ek tam')
eq(desen_sec([]), [], 'boş veri')
```

```solution
def desen_sec(kayitlar):
    sonuc = []
    for k in kayitlar:
        ad = k.get('file.name')
        if isinstance(ad,str) and ad.startswith('report') and ad.endswith('.json'):
            sonuc.append(k['id'])
    return sonuc
```

```hint
Sabit pattern için iki string sınır kontrolü yeterli; lower veya fnmatch ekleme.
```
:::

::: gorev Soru işareti literal, değer grubu alternatif
Sabit sorgu: `file.name: "report?.json" AND event.action: (open OR read)`. `literal_sec(kayitlar)` yalnız adı tam report?.json olan open/read olaylarının id'lerini döndürsün. report1.json eşleşmez; soru işareti tek karakter jokeri değildir. Alanlar tek değerli keyword ve harf duyarlı.

```starter
def literal_sec(kayitlar):
    return []
```

```test
need('literal_sec')
rows = [{'id':'a','file.name':'report?.json','event.action':'open'}, {'id':'b','file.name':'report?.json','event.action':'read'}, {'id':'c','file.name':'report1.json','event.action':'open'}, {'id':'d','file.name':'report?.json','event.action':'delete'}, {'id':'e','file.name':'report?.json','event.action':'OPEN'}, {'id':'f','file.name':'report?.json'}, {'id':'g','event.action':'open'}, {'id':'h','file.name':'Report?.json','event.action':'read'}]
eq(literal_sec(rows), ['a','b'], 'literal soru işareti ve değer grubu')
eq(literal_sec([{'id':'x','file.name':'report*.json','event.action':'read'}]), [], 'yıldız metni farklı değer')
eq(literal_sec([]), [], 'boş küme')
```

```solution
def literal_sec(kayitlar):
    return [k['id'] for k in kayitlar if k.get('file.name') == 'report?.json' and k.get('event.action') in ('open','read')]
```

```hint
Ad için tam eşitlik; eylem için iki öğeli üyelik kontrolü.
```
:::
