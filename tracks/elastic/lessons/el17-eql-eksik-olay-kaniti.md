---
id: el17
title: EQL · Eksik Olay ve Sonucu Daraltmak
summary: ![] için maxspan, eksik telemetriyi olay yokluğundan ayırmak; runs, pipe sınırları ve sequence yanıtındaki boş aşama.
---

::: anlat Olmayan olayı hangi aralıkta aradın?
“Oturum açıldıktan sonra dosya okundu, arada çıkış yok” sorusunun olumlu ve olumsuz aşamaları vardır. EQL'de `![ ... ]` eksik olay koşuludur; böyle bir sequence için `with maxspan` zorunludur ve en az bir olumlu aşama bulunmalıdır.

```eql norun
sequence by host.id, user.id with maxspan=5m
  [authentication where event.action == "login"]
  ![authentication where event.action == "logout"]
  [file where event.action == "read"]
```

Buradaki ortadaki olumsuz aşama iki olumlu olayın **zaman damgaları arasını** sorar; uçlarla aynı zaman damgasındaki bir kayıt bu açık zaman aralığına girmez. Bunu önceki dersteki ordinal kullanan `until` kontrolüyle karıştırma. “O kullanıcı hayatı boyunca hiç çıkış yapmadı” sonucu da çıkmaz. Aynı kullanıcı adı başka makinede bulunabilir; anahtarın host parçasını koru. Bu örneklerde kullanıcı ve makine kimlikleri dolu, tek değerli keyword alanlarıdır; zamanlar ve sıra numaraları tamdır.

İndekste olay görünmemesi, olayın hiç yaşanmadığını kanıtlamaz. Sensör durmuş, arama aralığı dar, shard yanıtı kısmi veya veri gecikmiş olabilir. Gerçek soruşturma bu kalite bilgisini ayrıca toplar. Python görevindeki `belirsiz` etiketi analistin veri kalitesi kararıdır; EQL'nin döndürdüğü özel bir durum değildir.
:::

::: anlat Tekrarlı aşama, pipe ve kanıt listesi
`with runs=3`, aynı olay ölçütünü dizide üç kez art arda yazmanın kısaltmasıdır; değer aralığı 1–100'dür. Başka olayların hiç araya girmemesi anlamına gelmez. EQL'deki `by` anahtarı SQL'deki serbest `JOIN` komutuna dönüşmez.

```eql norun
sequence by host.id, user.id with maxspan=5m
  [authentication where event.action == "login"]
  [file where event.action == "read"] with runs=3
| head 5
```

Elasticsearch EQL'nin `head`/`tail` pipe'ları sonuçtaki olay veya dizilerin sayısını daraltır. `| head 5`, dizinin beş olaylı olduğu ya da beş dakika sürdüğü anlamına gelmez. Endgame EQL örneklerindeki `join`, `child of`, `| count` veya `| unique` ifadelerini Elasticsearch'e aynı biçimde taşıma. ES|QL'nin pipe komutları da başka bir dildir.

Eksik aşamalı bir arama sonucunda `events` listesinde `missing: true` yer tutucusu bulunabilir. Bu nesneye sahte bir `_id` atayıp gözlenmiş olay sayma. Aşağıdaki ikinci görev yalnız verilen yanıtı özetler; yeni sequence keşfetmez.

Kaynaklar: [EQL eksik olay ve sınırlamalar](https://www.elastic.co/docs/reference/query-languages/eql/eql-syntax), [EQL pipe'ları](https://www.elastic.co/docs/reference/query-languages/eql/eql-pipe-ref), [arama yanıtı](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-eql-search), [Elastic'in eksik aşama zaman aralığı](https://github.com/elastic/elasticsearch/blob/main/x-pack/plugin/eql/src/main/java/org/elasticsearch/xpack/eql/execution/sequence/TumblingWindow.java).
:::

::: tahmin
Veri eksiksizdir. Mapping keyword/date/long sözleşmesini kullanır; API isteğinde `tiebreaker_field: "event.sequence"` ayarlanmıştır. Her anahtarda bir login ve bir read vardır. Hangi olumlu olay çiftleri tamamlanır? Eksik aşamayı bir kimlikle doldurma.

```eql
sequence by host.id, user.id with maxspan=5m
  [authentication where event.action == "login"]
  ![authentication where event.action == "logout"]
  [file where event.action == "read"]
```

```stdin
[
  {"event.id":"l1","@timestamp":"2026-10-21T13:00:00.000Z","event.sequence":1,"event.category":"authentication","event.action":"login","host.id":"h1","user.id":"u1"},
  {"event.id":"r1","@timestamp":"2026-10-21T13:00:01.000Z","event.sequence":2,"event.category":"file","event.action":"read","host.id":"h1","user.id":"u1"},
  {"event.id":"l2","@timestamp":"2026-10-21T13:00:02.000Z","event.sequence":3,"event.category":"authentication","event.action":"login","host.id":"h2","user.id":"u2"},
  {"event.id":"o2","@timestamp":"2026-10-21T13:00:03.000Z","event.sequence":4,"event.category":"authentication","event.action":"logout","host.id":"h2","user.id":"u2"},
  {"event.id":"r2","@timestamp":"2026-10-21T13:00:04.000Z","event.sequence":5,"event.category":"file","event.action":"read","host.id":"h2","user.id":"u2"}
]
```

```gercek
l1 -> r1
```

```test
import json, sys
from datetime import datetime
events = json.load(sys.stdin)
def key(e):
    return (e["host.id"], e["user.id"])
def order(e):
    return (datetime.fromisoformat(e["@timestamp"].replace("Z", "+00:00")), e["event.sequence"])
for a in events:
    if (a["event.category"],a["event.action"]) != ("authentication","login"):
        continue
    for b in events:
        if (b["event.category"],b["event.action"]) != ("file","read") or key(a) != key(b):
            continue
        if not order(a) < order(b) or (order(b)[0] - order(a)[0]).total_seconds() > 300:
            continue
        if not any(key(x) == key(a) and (x["event.category"],x["event.action"]) == ("authentication","logout") and order(a)[0] < order(x)[0] < order(b)[0] for x in events):
            print(a["event.id"] + " -> " + b["event.id"])
```

???

`l1/r1` arasında ilgili çıkış kaydı yoktur. `l2/r2` arasında `o2` vardır; ikinci aday elenir. Bu kararın “veri eksiksiz” varsayımına dayandığını raporda sakla. Fixture doğrulaması genel bir EQL sequence motoru değildir.
:::

::: gorev Eksik olaydan önce veri kalitesini değerlendir
`eksik_karari(bas, son, gozlenen, telemetri_tam)` fonksiyonunu yaz. Telemetri tam değilse `"belirsiz"`; tamsayı `t_ms` değerleri için süre 0'dan küçük veya 300000'den büyükse `"elenir"`; aynı `host.id` ve `user.id` için iki zamanın **kesin arasında** authentication/logout varsa `"elenir"`; aksi halde `"aday"` döndür. Bas ve son önceden seçilmiş doğru kategorili, aynı dolu anahtarlı adaydır. Eşit zamanlı olumlu uçların kendi sırası önceden doğrulanmıştır; sıfır süre mümkündür. Ortadaki eksik aşamada yalnız açık timestamp aralığını denetle: uç zamanına eşit logout engellemesin. Başka anahtarın çıkış kaydı da engellemesin.

```starter
def eksik_karari(bas, son, gozlenen, telemetri_tam):
    return "aday"
```

```test
def e(t, **ek):
    x = {"t_ms":t, "host.id":"h", "user.id":"u", "event.category":"authentication", "event.action":"logout"}
    x.update(ek); return x
bas = e(1000)
for fark, beklenen in ((-1,"elenir"), (0,"aday"), (1,"aday"), (299999,"aday"), (300000,"aday"), (300001,"elenir")):
    eq(eksik_karari(bas,e(1000+fark),[],True), beklenen, f"pencere {fark}")
for t, beklenen in ((999,"aday"), (1000,"aday"), (1001,"elenir"), (1999,"elenir"), (2000,"aday"), (2001,"aday")):
    eq(eksik_karari(bas,e(2000),[e(t)],True), beklenen, f"çıkış zamanı {t}")
for ek in ({"host.id":"baska"}, {"user.id":"baska"}, {"user.id":None}, {"event.category":"process"}, {"event.action":"login"}):
    eq(eksik_karari(bas,e(2000),[e(1500,**ek)],True), "aday", "ilgili çıkış olmalı")
eq(eksik_karari(bas,e(2000),[],False), "belirsiz", "kayıt yok ama sensör eksik")
eq(eksik_karari(bas,e(2000),[e(1500)],False), "belirsiz", "kalite etiketi öncelikli")
```

```solution
def eksik_karari(bas, son, gozlenen, telemetri_tam):
    if not telemetri_tam:
        return "belirsiz"
    fark = son["t_ms"] - bas["t_ms"]
    if fark < 0 or fark > 300000:
        return "elenir"
    for e in gozlenen:
        if (e.get("host.id"), e.get("user.id")) != (bas["host.id"], bas["user.id"]):
            continue
        if (e.get("event.category"), e.get("event.action")) == ("authentication", "logout") and bas["t_ms"] < e["t_ms"] < son["t_ms"]:
            return "elenir"
    return "aday"
```

```hint
Önce eksik telemetri, sonra süre, sonra ilgili çıkış. Başka makinenin logout olayını kullanıcıya bakıp tek başına kullanma.
```
:::

::: gorev Eksik aşamayı olaymış gibi sayma
`dizi_ozeti(dizi)` verilen tek sequence nesnesinden `{"anahtarlar": demet, "olaylar": liste, "eksik": sayı}` üretsin. `join_keys` sırasını koru. `events` içinde `missing` tam olarak `True` olan yer tutucuları say; diğer nesnelerde `_id` varsa sırayla listele. Aynı `_id` tekrar görünürse kendiliğinden tekilleştirme; özet veriyi saklamalıdır. Boş listeler geçerlidir. Bu çıktı gerçek EQL yanıtının tamamı değil, okuma kolaylığı için bir özettir.

```starter
def dizi_ozeti(dizi):
    return {"anahtarlar": (), "olaylar": [], "eksik": 0}
```

```test
eq(dizi_ozeti({"join_keys":["h","u"], "events":[{"_id":"l1"},{"missing":True},{"_id":"r1"}]}),
   {"anahtarlar":("h","u"), "olaylar":["l1","r1"], "eksik":1}, "ortadaki eksik aşama")
for sayi in (0,1,2):
    d = {"join_keys":["u","h"], "events":[{"missing":True}] * sayi + [{"_id":"x","missing":False}]}
    eq(dizi_ozeti(d), {"anahtarlar":("u","h"), "olaylar":["x"], "eksik":sayi}, f"yer tutucu sayısı {sayi}")
eq(dizi_ozeti({"join_keys":["h"], "events":[{"_id":"x"},{"_id":"x"},{"_id":"y"}]}),
   {"anahtarlar":("h",), "olaylar":["x","x","y"], "eksik":0}, "runs benzeri tekrarlar korunur")
eq(dizi_ozeti({"events":[{}, {"missing":True,"_id":"sahte"}]}), {"anahtarlar":(),"olaylar":[],"eksik":1}, "eksik aşama sahte id ile olaya dönüşmez")
eq(dizi_ozeti({}), {"anahtarlar":(),"olaylar":[],"eksik":0}, "boş özet")
```

```solution
def dizi_ozeti(dizi):
    ids, eksik = [], 0
    for e in dizi.get("events", []):
        if e.get("missing") is True:
            eksik += 1
        elif "_id" in e:
            ids.append(e["_id"])
    return {"anahtarlar":tuple(dizi.get("join_keys", [])), "olaylar":ids, "eksik":eksik}
```

```hint
missing kontrolünü _id kontrolünden önce yap. Sayı veya indis eşikleri yerine nesneleri giriş sırasıyla dolaş.
```
:::
