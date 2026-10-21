---
id: el13
title: EQL · Olay Kategorisi ve Koşul
summary: event.category ile where, ECS alanları, == ile : farkı ve EQL okuma alıştırmasının sınırları.
---

::: anlat Önce hangi olay, sonra hangi değer?
Bir süreç başlangıcını ve onun ardından gelen ağ bağlantısını araştırırken tek tek belge filtrelemek yetmeyebilir. **Elasticsearch EQL**, olay koşullarını ve zaman sıralı dizileri ifade eder. Başlangıç biçimi `kategori where koşul`dur. Aşağıdaki sorgu yalnız `process` kategorisini seçer; süreç adını ve argüman sayısını ayrıca denetler:

```eql norun
process where event.type == "start" and process.name == "cmd.exe" and process.args_count >= 3
```

Kategori için API'nin varsayılan alanı `event.category`, zaman için `@timestamp`'tir. `process.name` ise süreç adıdır; `event.type` olayın daha ayrıntılı türüdür. Bu üç alanı birbirinin yerine okumak farklı kayıtları seçtirir. `any where ...` kategori sınırlamasını kaldırır.

Bu dersin sözleşmesi: kategori ve diğer metinler indekslenmiş `keyword`, `process.args_count` tamsayı, `@timestamp` tarih alanıdır. Eğitim JSON'unda ECS adlarını noktalı düz anahtarlarla gösteriyoruz. Kategori bu örneklerde tek değerdir; çok değerli alan, analizör ve gerçek mapping davranışı Python görevlerinin konusu değildir. Elasticsearch EQL doğrudan `text` alanları veya `nested` alanların içini sorgulamaz; Python sözlüğünde anahtar bulabilmek bu sınırlamaları ortadan kaldırmaz.
:::

::: anlat Harf farkı ve dil farkı
`process.name == "cmd.exe"` harfe duyarlıdır. `process.name : "cmd.exe"` aynı metni harf farkını gözetmeden karşılaştırır; `:` ayrıca jokerli metin kalıplarını destekler. `== "cmd*.exe"` ise joker açmaz, yıldızı gerçek karakter sayar. Sonraki derste kalıpları ayrı inceleyeceğiz. EQL metinleri çift tırnakla yazılır.

**EQL, ES|QL değildir.** ES|QL'nin `FROM ... | WHERE ...` tablo hattını bu sorguya taşıma. Kibana KQL ve Microsoft Kusto KQL de ayrı dillerdir. Doğru sekmeyi ve API'yi seçmek, doğru koşulu yazmak kadar önemlidir.

Pafta bu okuma yolunda Elasticsearch açmaz ve EQL çalıştırmaz. Görevlerde, açıkça verilen tek bir koşulun Python karşılığını kuracaksın. Testler bu küçük veri sözleşmesini doğrular; gerçek Elastic sorgusunun derlendiği veya bütün EQL'nin taklit edildiği anlamına gelmez.

Kaynaklar: [EQL sözdizimi](https://www.elastic.co/docs/reference/query-languages/eql/eql-syntax), [EQL arama API'si](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-eql-search).
:::

::: tahmin
Mapping yukarıdaki gibidir; tüm zamanlar aynı günün UTC zamanlarıdır. Kayıtlar zaten artan zaman sırasında. Aşağıdaki koşula uyan `event.id` değerlerini giriş sırasıyla yaz. `>= 3` sınırına ve harf farkına ayrı bak.

```eql
process where event.type == "start" and process.name == "cmd.exe" and process.args_count >= 3
```

```stdin
[
  {"event.id":"e1","@timestamp":"2026-10-21T09:00:00.000Z","event.category":"process","event.type":"start","process.name":"cmd.exe","process.args_count":2},
  {"event.id":"e2","@timestamp":"2026-10-21T09:00:01.000Z","event.category":"process","event.type":"start","process.name":"cmd.exe","process.args_count":3},
  {"event.id":"e3","@timestamp":"2026-10-21T09:00:02.000Z","event.category":"process","event.type":"start","process.name":"CMD.EXE","process.args_count":4},
  {"event.id":"e4","@timestamp":"2026-10-21T09:00:03.000Z","event.category":"file","event.type":"start","process.name":"cmd.exe","process.args_count":4},
  {"event.id":"e5","@timestamp":"2026-10-21T09:00:04.000Z","event.category":"process","event.type":"start","process.name":"cmd.exe","process.args_count":4}
]
```

```gercek
e2
e5
```

```test
import json, sys
for e in json.load(sys.stdin):
    if e.get("event.category") == "process" and e.get("event.type") == "start" and e.get("process.name") == "cmd.exe" and e.get("process.args_count", -1) >= 3:
        print(e["event.id"])
```

???

`e2` tam üç argümanla sınırdadır; `e5` sınırı aşar. `e1` iki argümanlıdır. `e3`'te büyük harfler `==` koşulunu bozarken `e4` yanlış kategoridedir. Gizli doğrulayıcı yalnız bu fixture'ın koşulunu hesaplar, EQL sorgusu ayrıştırmaz.
:::

::: gorev Bir süreç koşulunu uygula
`surec_adayi(olay)` fonksiyonu, tahmindeki koşulun sonucunu `True`/`False` döndürsün. Eksik veya `None` alan eşleşmesin. `process.args_count` yalnız tamsayı olabilir; `bool`, sayı gibi kabul edilmesin. Bu, tek koşulluk okuma alıştırmasıdır.

```starter
def surec_adayi(olay):
    return olay.get("event.category") == "process"
```

```test
def ornek(n=3, **degisim):
    e = {"event.category":"process", "event.type":"start", "process.name":"cmd.exe", "process.args_count":n}
    e.update(degisim)
    return e
for n, beklenen in ((2, False), (3, True), (4, True)):
    eq(surec_adayi(ornek(n)), beklenen, f"argüman sınırı: {n}")
eq(surec_adayi(ornek(3, **{"process.name":"CMD.EXE"})), False, "== harfe duyarlı")
eq(surec_adayi(ornek(3, **{"event.type":"end"})), False, "süreç sonu başlangıç değildir")
eq(surec_adayi(ornek(3, **{"event.category":"network"})), False, "kategori zorunlu")
for n in (None, "3", True):
    eq(surec_adayi(ornek(n)), False, "mapping dışı tür")
eq(surec_adayi({}), False, "eksik alanlar")
```

```solution
def surec_adayi(olay):
    n = olay.get("process.args_count")
    return (olay.get("event.category") == "process"
            and olay.get("event.type") == "start"
            and olay.get("process.name") == "cmd.exe"
            and type(n) is int and n >= 3)
```

```hint
Üç metin koşulu ve tamsayı eşiği birlikte doğru olmalı. Python'da bool, int'in alt sınıfıdır; burada type(n) is int kullanabilirsin.
```
:::

::: gorev İki sorgunun farkını raporla
`harf_ozeti(olaylar)` iki liste döndürsün: `{"esit": [...], "esnek": [...]}`. Her ikisi de `process` kategorisindeki `start` olaylarını seçsin. `esit`, `process.name == "cmd.exe"`; `esnek`, `process.name : "cmd.exe"` koşulunun kimliklerini içersin. Argüman sayısı bu görevde sorgulanmıyor. Metinler ASCII, kimlikler benzersiz; sırayı koru. Eksik/`None` ad eşleşmesin.

```starter
def harf_ozeti(olaylar):
    return {"esit": [], "esnek": []}
```

```test
olaylar = [{"event.id":str(i), "event.category":"process", "event.type":"start", "process.name":ad}
           for i, ad in enumerate(("cmd.exe", "CMD.EXE", "Cmd.Exe", "cmd1.exe", "cmd.exe.bak", None), 1)]
eq(harf_ozeti(olaylar), {"esit":["1"], "esnek":["1","2","3"]}, "eşitlik ve harf farkı")
eq(harf_ozeti(list(reversed(olaylar))), {"esit":["1"], "esnek":["3","2","1"]}, "sıralama ekleme")
for alan, deger in (("event.category", "file"), ("event.type", "end")):
    e = dict(olaylar[0]); e[alan] = deger
    eq(harf_ozeti([e]), {"esit":[], "esnek":[]}, "ortak ön koşullar")
eq(harf_ozeti([{"event.id":"x"}]), {"esit":[], "esnek":[]}, "eksik kayıt")
```

```solution
def harf_ozeti(olaylar):
    sonuc = {"esit": [], "esnek": []}
    for olay in olaylar:
        if olay.get("event.category") != "process" or olay.get("event.type") != "start":
            continue
        ad = olay.get("process.name")
        if ad == "cmd.exe":
            sonuc["esit"].append(olay["event.id"])
        if isinstance(ad, str) and ad.lower() == "cmd.exe":
            sonuc["esnek"].append(olay["event.id"])
    return sonuc
```

```hint
Kategori ve tür iki liste için ortak. Yalnız esnek karşılaştırmada ASCII adı lower() ile karşılaştır; bütün olayı küçük harfe çevirme.
```
:::
