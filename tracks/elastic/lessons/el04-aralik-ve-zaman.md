---
id: el04
title: Sayısal Aralıklar ve Sabit UTC Penceresi
summary: Açık/kapalı sınırlar, mapping türü, çok değerli alan tuzağı; UTC tarih aralığını eşik komşularıyla okumak.
---

::: anlat Bir eşik, birim ve tür ister
Kibana KQL sayısal aralıkları `<`, `<=`, `>` ve `>=` ile yazar. `http.response.bytes >= 1024 AND http.response.bytes < 2048` alt sınırı dahil, üst sınırı hariç tutar. Bayt sayısı long/integer gibi sayısal mapping'de olmalı; içinde rakam görmen keyword alanını sayısal alan yapmaz. Bir kimlik numarası her zaman ölçülebilir bir miktar da değildir.

Bir sınırı sınarken hemen altını, kendisini ve hemen üstünü dene. Yalnız 5000 gibi çok büyük bir olumlu değer, >= yerine > yazıldığını göstermez. Görevler hem alt hem üst sınırın çevresini dener. Eksik veya null miktarın aralıkta sayılmaması gerekir; bu dersin görevleri geçerli sayısal scalar değer veya eksik/null kabul eder.

> [!TUZAK]
> Çok değerli sayısal alanlarda iki ayrı KQL koşulu farklı öğelerce sağlanabilir. Resmi örnekte `number > 300 AND number < 400`, `[500, 10]` dizisi için eşleşebilir: 500 ilkini, 10 ikincisini sağlar. Bu yüzden **tek değerli** varsayımını derslerde açık yazıyoruz. Aynı öğenin bütün aralık şartlarını sağlaması gereken tasarımı diziye bu basit modelle taşımamalısın.
:::

::: anlat Saat dilimini sonuçtan sonra tahmin etme
Zaman damgası tarih mapping'iyle karşılaştırılır. Zaman içeren ISO değerlerini tırnakla yaz: `@timestamp >= "2026-10-21T09:00:00Z"`. Z son eki UTC'yi belirtir. Açık saat dilimi olmayan metnin nasıl yorumlandığını uygulama ayarları etkileyebilir; bu örneklerde Z kullanarak belirsizliği kaldırıyoruz.

`now-5m` gibi göreli aralıklar her çalıştırmada başka belgeleri kapsayabilir. Bir araştırmayı devrederken sabit başlangıç/bitiş ve sınır işaretlerini paylaş. Sorgu içinde tarih koşulu varsa Discover zaman seçicisi onu geçersiz kılmaz; her ikisi kapsamı daraltabilir. Buradaki tahminde ek UI zaman filtresi yoktur; zaman aralığı yalnız görünen sorgudan gelir.

Python modelinde datetime nesneleriyle karşılaştıracağız. Girdiler geçerli UTC zamanları; bozuk tarih çözümleme bu görevin kapsamı değildir. `stamp is not None` yokluğu ayırır; sonra `utc(baslangic) <= utc(stamp) < utc(bitis)` yarı açık pencereyi verir. Tarihi yalnız `"09:" in metin` gibi bir parçayla seçmek gün/saat sınırlarında yanlış sonuç üretir.

Kaynaklar (21 Ekim 2026): [KQL aralıklar ve çok değerli alanlar](https://www.elastic.co/docs/reference/query-languages/kql), [Kibana zaman kapsamı](https://www.elastic.co/docs/explore-analyze/query-filter/filtering).
:::

::: tahmin
Aşağıdaki **Kibana KQL** filtresini ve JSON'daki mapping/bağlam varsayımlarını oku. Belirtilen sırada hangi belge kimlikleri görünür? Bu yolun sorgu bloğu okunur; Pafta Elastic sunucusunda sorgu çalıştırmaz. Gizli Python denetimi yalnız verilen sabit sorgunun açıklanan küçük modelini kontrol eder.

```kibana
@timestamp >= "2026-10-21T09:00:00Z" AND @timestamp < "2026-10-21T09:05:00Z" AND http.response.bytes >= 1024 AND http.response.bytes < 2048
```

```stdin
{
  "mapping": {
    "@timestamp": "date; tüm metinler UTC Z",
    "http.response.bytes": "tek değerli long"
  },
  "context": {
    "additional_ui_time_filter": "yok",
    "order": "girdi sırası",
    "threshold_units": "bayt"
  },
  "documents": [
    {
      "id": "a",
      "@timestamp": "2026-10-21T09:00:00Z",
      "http.response.bytes": 1024
    },
    {
      "id": "b",
      "@timestamp": "2026-10-21T09:04:59Z",
      "http.response.bytes": 2047
    },
    {
      "id": "c",
      "@timestamp": "2026-10-21T09:05:00Z",
      "http.response.bytes": 1024
    },
    {
      "id": "d",
      "@timestamp": "2026-10-21T09:01:00Z",
      "http.response.bytes": 2048
    },
    {
      "id": "e",
      "@timestamp": "2026-10-21T09:01:00Z",
      "http.response.bytes": 1023
    },
    {
      "id": "f",
      "http.response.bytes": 1500
    }
  ]
}
```

```gercek
a
b
```

```test
import json
import sys
from datetime import datetime
data = json.loads(sys.stdin.read())
def utc(text):
    return datetime.fromisoformat(text.replace('Z', '+00:00'))
start = utc('2026-10-21T09:00:00Z')
end = utc('2026-10-21T09:05:00Z')
for doc in data['documents']:
    stamp, amount = doc.get('@timestamp'), doc.get('http.response.bytes')
    if stamp is not None and amount is not None and start <= utc(stamp) < end and 1024 <= amount < 2048:
        print(doc['id'])
```

???

`a` alt zaman ve alt boyut sınırında olduğu için dahil. `b` iki üst sınırın da hemen altında. `c` tam bitiş zamanında, `d` tam üst boyut sınırında; ikisi dışarıda. `e` boyut alt sınırının altında, `f`de zaman yok. Tek bir koşulun doğru olması yetmez.
:::

::: gorev İki sayısal sınırı oku
`boyut_sec(kayitlar)` sabit `http.response.bytes >= 1024 AND http.response.bytes < 2048` koşulunun id'lerini döndürsün. Tek değerli long varsayılır; eksik/null eşleşmez. Sıralama girdi sırasıdır. Sayısal metin veya Boolean verilmez; model mapping dönüşümü yapmaz.

```starter
def boyut_sec(kayitlar):
    return []
```

```test
need('boyut_sec')
for amount, expected in [(1023,False),(1024,True),(1025,True),(2047,True),(2048,False),(2049,False),(0,False),(-1,False)]:
    eq(boyut_sec([{'id':'x','http.response.bytes':amount}]), ['x'] if expected else [], 'boyut sınırı: '+str(amount))
eq(boyut_sec([{'id':'a','http.response.bytes':1500},{'id':'b','http.response.bytes':None},{'id':'c'},{'id':'d','http.response.bytes':1600}]), ['a','d'], 'eksik ve null, sıra')
eq(boyut_sec([]), [], 'boş küme')
```

```solution
def boyut_sec(kayitlar):
    sonuc = []
    for k in kayitlar:
        miktar = k.get('http.response.bytes')
        if miktar is not None and 1024 <= miktar < 2048:
            sonuc.append(k['id'])
    return sonuc
```

```hint
None kontrolünden sonra alt sınır <=, üst sınır < olsun.
```
:::

::: gorev Parametreli UTC araştırma penceresi
`zaman_sec(kayitlar, baslangic, bitis)` @timestamp değeri `[baslangic, bitis)` aralığında bulunan id'leri sırayla döndürsün. Zamanlar geçerli UTC ISO 8601, scalar; eksik/null zaman dışarıda. Fonksiyonun parametreleri bu sabit aralık okuma alıştırmasını farklı pencerede sınamamızı sağlar; serbest bir KQL metni verilmez.

```starter
from datetime import datetime

def utc(metin):
    return datetime.fromisoformat(metin.replace('Z', '+00:00'))

def zaman_sec(kayitlar, baslangic, bitis):
    return []
```

```test
need('zaman_sec')
start, end = '2026-10-21T09:00:00Z', '2026-10-21T09:05:00Z'
stamps = ['2026-10-21T08:59:59Z','2026-10-21T09:00:00Z','2026-10-21T09:00:01Z','2026-10-21T09:04:59Z','2026-10-21T09:05:00Z','2026-10-21T09:05:01Z']
rows = [{'id':str(i),'@timestamp':stamp} for i,stamp in enumerate(stamps)] + [{'id':'missing'},{'id':'null','@timestamp':None}]
eq(zaman_sec(rows,start,end), ['1','2','3'], 'iki uç ve bir saniyelik komşuları')
eq(zaman_sec(rows,'2026-10-21T09:05:00Z','2026-10-21T09:06:00Z'), ['4','5'], 'yeni pencere kullanılır')
eq(zaman_sec(rows,start,start), [], 'boş yarı açık pencere')
eq(zaman_sec([],start,end), [], 'boş veri')
```

```solution
from datetime import datetime

def utc(metin):
    return datetime.fromisoformat(metin.replace('Z', '+00:00'))

def zaman_sec(kayitlar, baslangic, bitis):
    start, end = utc(baslangic), utc(bitis)
    sonuc = []
    for k in kayitlar:
        stamp = k.get('@timestamp')
        if stamp is not None and start <= utc(stamp) < end:
            sonuc.append(k['id'])
    return sonuc
```

```hint
UTC tarih nesnelerini oluştur; bitişi dahil etme. String parçasına veya sistemin bugünkü tarihine bağlı kalma.
```
:::
