---
id: el01
title: Kibana KQL, Discover ve Dil Haritası
summary: Kusto ile Kibana KQL farkı; Lucene, EQL ve ES|QL amaçları; data view, zaman filtresi ve sorgunun birlikte etkisi.
---

::: anlat Aynı kısaltma, farklı dil
Pafta'daki **KQL** yolunda gördüğün `tablo | where ...` ifadesi Microsoft'un **Kusto Query Language** dilidir. Buradaki **Kibana Query Language** ise `event.dataset: auth AND user.name: alice` gibi belge filtreleri yazar. İkisinin KQL diye kısaltılması sözdizimlerini aynı yapmaz. Kibana bir arayüz, Elasticsearch veriyi indeksleyen ve sorgulayan sistemdir.

Bu Elastic okuma yolunda üç ayrı sözdizimini ayıracağız: Kibana KQL belge filtreler; Lucene query-string ayrı bir arama sözdizimidir; EQL olayların koşullarını ve zaman içindeki ilişkilerini anlatır. ES|QL ise borularla veri işleme ve özetleme yapabilen başka bir Elastic dilidir. Boru görmen onu Kusto yapmaz. Query DSL de Elasticsearch'ün JSON sorgu biçimidir. Birini öğrenmek diğerlerinin kurallarını otomatik taşımaz.

Güncel Elastic belgeleri Kibana KQL'yi Kibana sorgu çubuğu dışında Query DSL `kql` bileşeni ve ES|QL `KQL` fonksiyonuyla da gösteriyor. Bu derslerdeki bağlam **Discover klasik modunda Kibana KQL**: özel backend seçenekleri varsayılmıyor. Dilin işi filtrelemek; buradaki bir KQL koşulunun sonuna `summarize` ekleyip tablo özeti alamazsın.

> [!NOT]
> Bu bir **okuma yolu**. `kibana` blokları yerel Elastic motorunda çalıştırılmaz. Görevlerde belirli bir sorgunun mantığını Python'da kurarsın; genel KQL ayrıştırıcısı yazmıyorsun. Test başarısı, gerçek Kibana kümesinde doğrulama yapıldığını göstermez.
:::

::: anlat Discover sonucu yalnız sorgu metninden oluşmaz
Discover klasik modda seçili **data view** ile KQL veya Lucene kullanır. Data view, hangi indeks/veri akışlarının kapsamda olduğunu ve varsa zaman alanını belirler. Zaman filtresi de bu alan üzerinde görünür belgeleri sınırlar. Doğru kullanıcı adını ararken yanlış data view veya zaman aralığı seçmek sıfır sonuç verebilir. ES|QL modu için aynı data view gereksinimini varsayma; o farklı bir çalışma biçimidir.

İncelemeyi yeniden üretmek için sorguyu, seçili veri kapsamını, mutlak zaman aralığını, zaman alanını ve görüntüleme sırasını kaydet. “Son beş dakika” sürekli değişir. Bu paftada zamanlar ISO 8601 UTC'dir; sabit yarı açık `[09:00:00Z, 09:05:00Z)` aralığını **eğitim bağlamı** olarak kullanıyoruz. Bu, Kibana'nın her tarih seçicisinin varsayılan sınır politikası hakkında bir iddia değildir.

Python görevlerinde `dict.get(ad)` eksik anahtarda `None` verir. `datetime.fromisoformat(metin.replace('Z', '+00:00'))` bu derste verilen UTC zamanını karşılaştırılabilir nesneye çevirir. Listeyi sırayla gezip eşleşen kaydın `id` değerini ekle; bir sıralama koşulu verilmedikçe girdi sırasını koru. Noktalı alan adları bu alıştırmalarda düz sözlük anahtarlarıdır.

Kaynaklar (21 Ekim 2026'da kontrol edildi): [Discover](https://www.elastic.co/docs/explore-analyze/discover), [Kibana filtreleri ve zaman](https://www.elastic.co/docs/explore-analyze/query-filter/filtering), [Kibana KQL](https://www.elastic.co/docs/reference/query-languages/kql).
:::

::: tahmin
Aşağıdaki **Kibana KQL** filtresini ve JSON'daki mapping/bağlam varsayımlarını oku. Belirtilen sırada hangi belge kimlikleri görünür? Bu yolun sorgu bloğu okunur; Pafta Elastic sunucusunda sorgu çalıştırmaz. Gizli Python denetimi yalnız verilen sabit sorgunun açıklanan küçük modelini kontrol eder.

```kibana
event.dataset: auth AND user.name: alice
```

```stdin
{
  "mapping": {
    "event.dataset": "keyword, normalizer yok",
    "user.name": "keyword, normalizer yok",
    "@timestamp": "date"
  },
  "context": {
    "data_view": "yalnız auth kayıtları",
    "time_field": "@timestamp",
    "start_inclusive": "2026-10-21T09:00:00Z",
    "end_exclusive": "2026-10-21T09:05:00Z",
    "order": "girdi sırası"
  },
  "documents": [
    {
      "id": "a",
      "event.dataset": "auth",
      "user.name": "alice",
      "@timestamp": "2026-10-21T09:00:00Z"
    },
    {
      "id": "b",
      "event.dataset": "auth",
      "user.name": "alice",
      "@timestamp": "2026-10-21T09:05:00Z"
    },
    {
      "id": "c",
      "event.dataset": "auth",
      "user.name": "Alice",
      "@timestamp": "2026-10-21T09:02:00Z"
    },
    {
      "id": "d",
      "event.dataset": "web",
      "user.name": "alice",
      "@timestamp": "2026-10-21T09:01:00Z"
    },
    {
      "id": "e",
      "event.dataset": "auth",
      "user.name": "alice",
      "@timestamp": "2026-10-21T09:04:59Z"
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
from datetime import datetime
data = json.loads(sys.stdin.read())
context = data['context']
def utc(text):
    return datetime.fromisoformat(text.replace('Z', '+00:00'))
start = utc(context['start_inclusive'])
end = utc(context['end_exclusive'])
for doc in data['documents']:
    stamp = doc.get('@timestamp')
    if doc.get('event.dataset') == 'auth' and doc.get('user.name') == 'alice' and stamp is not None and start <= utc(stamp) < end:
        print(doc['id'])
```

???

`a` ve `e` görünür. `b` bitiş sınırındadır ve bu bağlamda dışlanır. `c`de keyword kullanıcı adı Alice; alice ile aynı değer değildir. `d`, auth kapsamı dışında. Sonuçlar alfabetik değil, verilen belge sırasındadır.
:::

::: gorev Zaman ve veri kapsamını birlikte uygula
`gorunur(kayit, baslangic, bitis)` Boolean döndürsün: event.dataset tam `auth` ve @timestamp mevcutsa, verilen UTC yarı açık `[baslangic, bitis)` penceresine üyeliği denetlesin. Kullanıcı adı bu görevde aranmaz. Zamanı olmayan kayıt False. Verilen zaman metinleri geçerli UTC ISO 8601'dir; sayısal eşik gibi baş/son sınırları da test et.

Bu, sabit Discover bağlamını anlamak için küçük bir modeldir; data view desenlerini veya serbest sorgu metnini ayrıştırma.

```starter
from datetime import datetime

def utc(metin):
    return datetime.fromisoformat(metin.replace('Z', '+00:00'))

def gorunur(kayit, baslangic, bitis):
    return False
```

```test
need('gorunur')
start, end = '2026-10-21T09:00:00Z', '2026-10-21T09:05:00Z'
for stamp, expected in [('2026-10-21T08:59:59Z', False), ('2026-10-21T09:00:00Z', True), ('2026-10-21T09:04:59Z', True), ('2026-10-21T09:05:00Z', False), ('2026-10-21T09:05:01Z', False)]:
    eq(gorunur({'event.dataset':'auth','@timestamp':stamp}, start, end), expected, 'zaman sınırı: '+stamp)
eq(gorunur({'event.dataset':'web','@timestamp':start}, start, end), False, 'yanlış veri kümesi')
eq(gorunur({'event.dataset':'auth'}, start, end), False, 'zaman eksik')
eq(gorunur({'@timestamp':start}, start, end), False, 'veri kümesi eksik')
eq(gorunur({'event.dataset':'auth','@timestamp':'2026-10-21T10:00:00Z'}, '2026-10-21T10:00:00Z', '2026-10-21T10:01:00Z'), True, 'pencere parametreleri kullanılır')
```

```solution
from datetime import datetime

def utc(metin):
    return datetime.fromisoformat(metin.replace('Z', '+00:00'))

def gorunur(kayit, baslangic, bitis):
    stamp = kayit.get('@timestamp')
    return kayit.get('event.dataset') == 'auth' and stamp is not None and utc(baslangic) <= utc(stamp) < utc(bitis)
```

```hint
Önce veri kümesi ve zaman varlığını denetle; sonra başlangıç <= zaman < bitiş.
```
:::

::: gorev Keyword eşitliğini koru
`sec(kayitlar)` şu sabit Kibana KQL filtresinin anlamını kursun: `event.dataset: auth AND user.name: alice`. İki alan normalizer olmayan tek değerli keyword; case-sensitive. Eşleşen id listesini girdi sırasında döndür. Zaman kapsamının bu göreve gelmeden uygulandığı varsayılır. Boş veya eksik alan eşleşmez.

```starter
def sec(kayitlar):
    return []
```

```test
need('sec')
rows = [{'id':'z','event.dataset':'auth','user.name':'alice'}, {'id':'a','event.dataset':'auth','user.name':'Alice'}, {'id':'m','event.dataset':'web','user.name':'alice'}, {'id':'c','event.dataset':'auth','user.name':'alice'}, {'id':'missing','event.dataset':'auth'}, {'id':'blank','event.dataset':'auth','user.name':''}]
eq(sec(rows), ['z','c'], 'iki koşul ve harf farkı, girdi sırası')
eq(sec(list(reversed(rows))), ['c','z'], 'alfabetik sıralama yapılmaz')
eq(sec([{'id':'x','event.dataset':'AUTH','user.name':'alice'}, {'id':'n','user.name':'alice'}]), [], 'normalleştirme varsayma')
eq(sec([]), [], 'boş küme')
```

```solution
def sec(kayitlar):
    return [kayit['id'] for kayit in kayitlar if kayit.get('event.dataset') == 'auth' and kayit.get('user.name') == 'alice']
```

```hint
İki get eşitliğini and ile bağla; lower() ekleme.
```
:::
