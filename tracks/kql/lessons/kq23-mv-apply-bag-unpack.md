---
id: kq23
title: Satır İçindeki Diziler · mv-apply ve bag_unpack
summary: mv-expand'ın satırı çoğaltıp bağlamı dağıtması; mv-apply ile her satırın dizisine kendi alt sorgusunu uygulamak (satır başına top, satır başına summarize); by'sız summarize'ın boş dizide de satır vermesi, top'un vermemesi; evaluate bag_unpack ile dinamik bir nesnenin anahtarlarını sütuna açmak, önek ve çakışma; tezgahın bir yerel öykünme olduğu ve hangi alt işleçleri desteklediği.
kazanim: SC200 2.3, SC200 4.2
---

::: anlat Dizinin içinde sorgu
KQ13'te `mv-expand` ile diziyi satırlara açtın. Açmanın bir bedeli vardır: satırın öteki sütunları her elemanda kopyalanır ve "bu eleman hangi kayda aitti" bilgisi ancak sütunlar üzerinden yeniden gruplanarak geri gelir.

Bu derste `kontroller` tablosuyla çalışacaksın: her satır bir sunucunun bir sağlık kontrolü. `sureler` o kontroldeki yanıt sürelerinin dizisi (milisaniye), `ozellik` sunucunun o anki özellikleri (JSON nesnesi). Tablo bu dersin hazırlığında kuruluyor.

```kql
kontroller
| project zaman, sunucu, sureler, ozellik
```

"Her kontrolün en yavaş iki ölçümü" sorusunu `mv-expand` ile sorarsan `top 2` bütün tabloya uygulanır, her kontrole değil:

```kql
kontroller
| mv-expand s = iff(isempty(sureler), dynamic([]), parse_json(sureler)) to typeof(long)
| top 2 by s desc
| project zaman, sunucu, s
```

`mv-apply` diziyi **her satır için ayrı** açar ve parantez içindeki alt sorguyu o satırın elemanlarına uygular. Alt sorgunun her sonuç satırı, dış satırın sütunlarıyla birleşip çıkar:

```kql
kontroller
| mv-apply s = iff(isempty(sureler), dynamic([]), parse_json(sureler)) to typeof(long) on (top 2 by s desc)
| project zaman, sunucu, s
```

| Parça | Anlamı |
|---|---|
| `s = iff(isempty(sureler), dynamic([]), parse_json(sureler))` | açılacak dizi ve elemana verilecek ad |
| `to typeof(long)` | elemanın tür cast'i; sayıya çevrilemeyen tür null olur; yazmazsan `dynamic` kalır |
| `on ( ... )` | her satırın elemanlarına uygulanacak alt sorgu |

> [!NOT] Bu ders gerçek yerel Microsoft Kusto motorunda çalışır
> Microsoft Kusto Emulator kullanılır; Sentinel hizmeti veya gerçek uç nokta telemetrisi değildir. Eski SQL fixture metni yalnız örnek veriyi native datatable'a aktarır; öğrencinin sorgusu SQLite'a çevrilmez. Eksik string alanları Kusto'da boş metindir; dynamic null ve boş dizi aynı şey değildir. `to typeof(long)` tür cast'idir: dynamic içindeki metin rakamları için otomatik `tolong` dönüşümü yapmaz. Aşağıdaki testler bu farkları gerçek motorla ölçer.

```setup
CREATE TABLE kontroller (zaman TEXT, sunucu TEXT, sureler TEXT, ozellik TEXT);
INSERT INTO kontroller VALUES
 ('2026-10-19 09:00','web01','[120,95,2300,140]','{"bolge":"ist","surum":"2.4.1"}'),
 ('2026-10-19 09:00','web02','[110,130]','{"bolge":"ank","surum":"2.4.1","bakim":"disk"}'),
 ('2026-10-19 09:00','web03','[]','{"bolge":"dis"}'),
 ('2026-10-19 10:00','web01','[700,2410,1900]','{"bolge":"ist","surum":"2.5.0"}'),
 ('2026-10-19 10:00','web02','[180]','{"bolge":"ank","surum":"2.5.0"}');
```
```meta
motor: kusto
timeout: 90
```
:::

::: anlat Boş dizi ve satır başına özet
Alt sorgu bir dış satır için **hiç satır üretmezse** o dış satır sonuçtan düşer. `web03`'ün dizisi boş; `top 2` ona hiçbir satır vermez, bu yüzden yukarıdaki sorguda `web03` yok.

`by`'sız bir `summarize` ise boş girdide de **tek satır** verir: `count()` sıfır, `max()` boş. Bu, `mv-apply`'ı "her kaydın dizisini kendi içinde özetle" sorusu için uygun kılar; kayıt, dizisi boş olsa da sonuçta kalır:

```kql
kontroller
| mv-apply s = iff(isempty(sureler), dynamic([]), parse_json(sureler)) to typeof(long) on (summarize olcum = count(), en_yuksek = max(s))
| project zaman, sunucu, olcum, en_yuksek
```

Aynı soruyu `mv-expand` ve `summarize ... by zaman, sunucu` ile sorsaydın `web03` dönmezdi; o kaydın açılacak elemanı yok, gruplanacak satırı da yok.

```setup
CREATE TABLE kontroller (zaman TEXT, sunucu TEXT, sureler TEXT, ozellik TEXT);
INSERT INTO kontroller VALUES
 ('2026-10-19 09:00','web01','[120,95,2300,140]','{"bolge":"ist","surum":"2.4.1"}'),
 ('2026-10-19 09:00','web02','[110,130]','{"bolge":"ank","surum":"2.4.1","bakim":"disk"}'),
 ('2026-10-19 09:00','web03','[]','{"bolge":"dis"}'),
 ('2026-10-19 10:00','web01','[700,2410,1900]','{"bolge":"ist","surum":"2.5.0"}'),
 ('2026-10-19 10:00','web02','[180]','{"bolge":"ank","surum":"2.5.0"}');
```
```meta
motor: kusto
timeout: 90
```
:::

::: tahmin
Önce `where`, sonra `by`'sız `summarize`. Kaç satır çıkar, `yavas` sütunu ne yazar?

```kql
kontroller
| mv-apply s = iff(isempty(sureler), dynamic([]), parse_json(sureler)) to typeof(long) on (where s > 1000 | summarize yavas = count())
| project zaman, sunucu, yavas
```

???

**Beş satır**, her kontrol için bir tane:

```
2026-10-19 09:00|web01|1
2026-10-19 09:00|web02|0
2026-10-19 09:00|web03|0
2026-10-19 10:00|web01|2
2026-10-19 10:00|web02|0
```

`where` web02 ve web03'ün bütün elemanlarını eler, ama ardından gelen `summarize` `by` almadığı için boş girdide de bir satır verir: `0`. "Bu kontrolde yavaş ölçüm yoktu" bilgisi kaybolmaz. `summarize yavas = count() by s` yazsaydın boş gruplar satır vermez, bu üç kontrol düşerdi.

```setup
CREATE TABLE kontroller (zaman TEXT, sunucu TEXT, sureler TEXT, ozellik TEXT);
INSERT INTO kontroller VALUES
 ('2026-10-19 09:00','web01','[120,95,2300,140]','{"bolge":"ist","surum":"2.4.1"}'),
 ('2026-10-19 09:00','web02','[110,130]','{"bolge":"ank","surum":"2.4.1","bakim":"disk"}'),
 ('2026-10-19 09:00','web03','[]','{"bolge":"dis"}'),
 ('2026-10-19 10:00','web01','[700,2410,1900]','{"bolge":"ist","surum":"2.5.0"}'),
 ('2026-10-19 10:00','web02','[180]','{"bolge":"ank","surum":"2.5.0"}');
```
```meta
motor: kusto
timeout: 90
```
:::

::: gorev 1 · Her kontrolün en yavaş iki ölçümü
Her kontrol için `sureler` dizisindeki **en büyük iki** süreyi listele. Sütunlar: `zaman`, `sunucu`, `s` (süre, `long`). Zamana, sonra sunucuya göre artan; aynı kontrolün süreleri büyükten küçüğe.

Başlangıç sorgusu `top 2`'yi bütün tabloya uyguluyor; her kontrole uygulanmalı.

```starter
kontroller
| mv-expand s = iff(isempty(sureler), dynamic([]), parse_json(sureler)) to typeof(long)
| top 2 by s desc
| project zaman, sunucu, s
```

```test
eq(sutunlar, ["zaman", "sunucu", "s"], "sütunlar")
eq(kullanir("mv-apply"), True, "her kontrolün dizisine ayrı bir top uygulamak için mv-apply kullan")
eq(sonuc, [("2026-10-19 09:00", "web01", 2300), ("2026-10-19 09:00", "web01", 140),
           ("2026-10-19 09:00", "web02", 130), ("2026-10-19 09:00", "web02", 110),
           ("2026-10-19 10:00", "web01", 2410), ("2026-10-19 10:00", "web01", 1900),
           ("2026-10-19 10:00", "web02", 180)],
   "web03'ün dizisi boş, top ona satır vermez; web02 10:00'ın tek ölçümü var")
eq(dene("INSERT INTO kontroller VALUES ('2026-10-19 11:00','web04','[500,90,500,800]','{}'),"
        "('2026-10-19 11:00','web05','[\"300\",\"40\"]','{}');")[7:],
   [("2026-10-19 11:00", "web04", 800), ("2026-10-19 11:00", "web04", 500),
    ("2026-10-19 11:00", "web05", None), ("2026-10-19 11:00", "web05", None)],
   "eşit süreler ayrı ayrı sayılır (800 ve bir 500); metin olarak yazılmış süreler cast ile sayıya çevrilmez; null olur")
```

```solution
kontroller
| mv-apply s = iff(isempty(sureler), dynamic([]), parse_json(sureler)) to typeof(long) on (top 2 by s desc)
| project zaman, sunucu, s
| sort by zaman asc, sunucu asc, s desc
```

```hint
`mv-expand ... | top 2` yerine diziyi `mv-apply s = iff(isempty(sureler), dynamic([]), parse_json(sureler)) to typeof(long) on (top 2 by s desc)` ile aç. Dış sıralamayı en sona `sort by zaman asc, sunucu asc, s desc` ile koy.
```

```hint
`to typeof(long)` yazmazsan `s` dinamik kalır: metin olarak gelen `"300"` ile `"40"` sayı gibi değil metin gibi sıralanabilir.
```

```setup
CREATE TABLE kontroller (zaman TEXT, sunucu TEXT, sureler TEXT, ozellik TEXT);
INSERT INTO kontroller VALUES
 ('2026-10-19 09:00','web01','[120,95,2300,140]','{"bolge":"ist","surum":"2.4.1"}'),
 ('2026-10-19 09:00','web02','[110,130]','{"bolge":"ank","surum":"2.4.1","bakim":"disk"}'),
 ('2026-10-19 09:00','web03','[]','{"bolge":"dis"}'),
 ('2026-10-19 10:00','web01','[700,2410,1900]','{"bolge":"ist","surum":"2.5.0"}'),
 ('2026-10-19 10:00','web02','[180]','{"bolge":"ank","surum":"2.5.0"}');
```
```meta
motor: kusto
timeout: 90
```
:::

::: gorev 2 · Kaydı kaybetmeden özet
Her kontrol için üç sayı: `olcum` (dizideki ölçüm sayısı), `yavas` (1000 ms'den **büyük** ölçüm sayısı) ve `en_yuksek` (en büyük süre). Dizisi boş olan kontrol de `0` ile sonuçta kalsın. Sütunlar: `zaman`, `sunucu`, `olcum`, `yavas`, `en_yuksek`; zamana, sonra sunucuya göre artan.

```starter
kontroller
| mv-expand s = iff(isempty(sureler), dynamic([]), parse_json(sureler)) to typeof(long)
| summarize olcum = count() by zaman, sunucu
```

```test
eq(sutunlar, ["zaman", "sunucu", "olcum", "yavas", "en_yuksek"], "sütunlar")
eq(sonuc, [("2026-10-19 09:00", "web01", 4, 1, 2300), ("2026-10-19 09:00", "web02", 2, 0, 130),
           ("2026-10-19 09:00", "web03", 0, 0, None), ("2026-10-19 10:00", "web01", 3, 2, 2410),
           ("2026-10-19 10:00", "web02", 1, 0, 180)],
   "web03 boş dizisiyle sonuçta kalır: 0 ölçüm, en_yuksek boş")
eq(dene("INSERT INTO kontroller VALUES ('2026-10-19 11:00','web04','[1000,1001]','{}'),"
        "('2026-10-19 11:00','web05',NULL,'{}');")[5:],
   [("2026-10-19 11:00", "web04", 2, 1, 1001), ("2026-10-19 11:00", "web05", 0, 0, None)],
   "tam 1000 ms yavaş değildir (büyük); sureler sütunu boş olan kontrol de 0 ile kalır")
```

```solution
kontroller
| mv-apply s = iff(isempty(sureler), dynamic([]), parse_json(sureler)) to typeof(long) on (
    summarize olcum = count(), yavas = countif(s > 1000), en_yuksek = max(s))
| project zaman, sunucu, olcum, yavas, en_yuksek
| sort by zaman asc, sunucu asc
```

```hint
`mv-expand` boş dizili kaydı satıra açamaz; `summarize ... by zaman, sunucu` de onu geri getiremez. Alt sorgusu `by`'sız bir `summarize` olan `mv-apply` her kayda bir satır verir.
```

```hint
Üç toplamayı aynı `summarize`'a yaz: `count()`, `countif(s > 1000)`, `max(s)`.
```

```setup
CREATE TABLE kontroller (zaman TEXT, sunucu TEXT, sureler TEXT, ozellik TEXT);
INSERT INTO kontroller VALUES
 ('2026-10-19 09:00','web01','[120,95,2300,140]','{"bolge":"ist","surum":"2.4.1"}'),
 ('2026-10-19 09:00','web02','[110,130]','{"bolge":"ank","surum":"2.4.1","bakim":"disk"}'),
 ('2026-10-19 09:00','web03','[]','{"bolge":"dis"}'),
 ('2026-10-19 10:00','web01','[700,2410,1900]','{"bolge":"ist","surum":"2.5.0"}'),
 ('2026-10-19 10:00','web02','[180]','{"bolge":"ank","surum":"2.5.0"}');
```
```meta
motor: kusto
timeout: 90
```
:::

::: anlat bag_unpack: nesneyi sütunlara aç
`ozellik` bir JSON nesnesi. Alanlarını tek tek `tostring(o.bolge)` diye çıkarabilirsin, ama hangi anahtarların geleceğini bilmiyorsan ya da onlarca anahtar varsa `evaluate bag_unpack` her anahtarı **bir sütuna** açar:

```kql
kontroller
| extend o = parse_json(ozellik)
| evaluate bag_unpack(o)
| project zaman, sunucu, bolge, surum, bakim
```

- Kaynak sütun (`o`) sonuçtan düşer; yerine nesnelerde görülen **bütün** anahtarlar gelir.
- Bir satırın nesnesinde olmayan anahtar o satırda **boş**tur (`bakim` yalnız web02 09:00'da dolu).
- İkinci argüman bir önektir: `bag_unpack(o, 'o_')` sütunları `o_bolge`, `o_surum` diye adlandırır.

> [!TUZAK] Sütun listesi veriden gelir
> `bag_unpack`'in hangi sütunları üreteceği sorguya değil **veriye** bağlıdır: yarın bir kayıt yeni bir anahtarla gelirse sonuçta yeni bir sütun belirir; bir anahtar hiç gelmezse sütunu da olmaz ve onu `project` eden sorgu hata verir. Sütun sırası da güvenilir değildir. Bir panoya ya da kurala koyacağın sorguda istediğin sütunları **adıyla** `project` et. Açılan bir anahtar var olan bir sütunla aynı adı taşıyorsa bu tezgah hata verir; önek ver. Gerçek Kusto'da bu durumun davranışını değiştiren ek seçenekler vardır, bu tezgahta yoktur.

```setup
CREATE TABLE kontroller (zaman TEXT, sunucu TEXT, sureler TEXT, ozellik TEXT);
INSERT INTO kontroller VALUES
 ('2026-10-19 09:00','web01','[120,95,2300,140]','{"bolge":"ist","surum":"2.4.1"}'),
 ('2026-10-19 09:00','web02','[110,130]','{"bolge":"ank","surum":"2.4.1","bakim":"disk"}'),
 ('2026-10-19 09:00','web03','[]','{"bolge":"dis"}'),
 ('2026-10-19 10:00','web01','[700,2410,1900]','{"bolge":"ist","surum":"2.5.0"}'),
 ('2026-10-19 10:00','web02','[180]','{"bolge":"ank","surum":"2.5.0"}');
```
```meta
motor: kusto
timeout: 90
```
:::

::: gorev 3 · Özellikleri sütunlara aç
`ozellik` nesnesini `bag_unpack` ile **`o_` önekiyle** aç. Yalnız `o_surum`'u **dolu** olan kontrolleri tut ve şu sütunları yaz: `zaman`, `sunucu`, `o_bolge`, `o_surum`, `o_bakim`. Zamana, sonra sunucuya göre artan.

```starter
kontroller
| extend o = parse_json(ozellik)
| project zaman, sunucu, bolge = tostring(o.bolge)
```

```test
eq(sutunlar, ["zaman", "sunucu", "o_bolge", "o_surum", "o_bakim"], "sütunlar")
eq(kullanir("bag_unpack"), True, "nesneyi evaluate bag_unpack ile aç")
eq(sonuc, [("2026-10-19 09:00", "web01", "ist", "2.4.1", ''), ("2026-10-19 09:00", "web02", "ank", "2.4.1", "disk"),
           ("2026-10-19 10:00", "web01", "ist", "2.5.0", ''), ("2026-10-19 10:00", "web02", "ank", "2.5.0", '')],
   "web03'ün nesnesinde surum yok; bakim yalnız web02 09:00'da")
eq(dene("INSERT INTO kontroller VALUES ('2026-10-19 11:00','web04','[]','{\"surum\":\"2.6.0\",\"zaman\":\"x\"}'),"
        "('2026-10-19 11:00','web05','[]',NULL),('2026-10-19 11:00','web06','[]','[1,2]');")[4:],
   [("2026-10-19 11:00", "web04", '', "2.6.0", '')],
   "nesnede zaman anahtarı olsa da önek çakışmayı önler; boş ya da dizi olan ozellik satırları surumsuz düşer")
```

```solution
kontroller
| extend o = parse_json(ozellik)
| evaluate bag_unpack(o, 'o_')
| where isnotempty(o_surum)
| project zaman, sunucu, o_bolge, o_surum, o_bakim
| sort by zaman asc, sunucu asc
```

```hint
`| evaluate bag_unpack(o, 'o_')` ile aç; ardından `where isnotempty(o_surum)` ile süz.
```

```hint
Önek yazmazsan yeni gelen bir kayıttaki `zaman` anahtarı var olan `zaman` sütunuyla çakışır. Önek bu tür çakışmaları baştan önler.
```

```setup
CREATE TABLE kontroller (zaman TEXT, sunucu TEXT, sureler TEXT, ozellik TEXT);
INSERT INTO kontroller VALUES
 ('2026-10-19 09:00','web01','[120,95,2300,140]','{"bolge":"ist","surum":"2.4.1"}'),
 ('2026-10-19 09:00','web02','[110,130]','{"bolge":"ank","surum":"2.4.1","bakim":"disk"}'),
 ('2026-10-19 09:00','web03','[]','{"bolge":"dis"}'),
 ('2026-10-19 10:00','web01','[700,2410,1900]','{"bolge":"ist","surum":"2.5.0"}'),
 ('2026-10-19 10:00','web02','[180]','{"bolge":"ank","surum":"2.5.0"}');
```
```meta
motor: kusto
timeout: 90
```
:::

::: anlat Yerel gerçek motorun kanıt sınırı
Bu ders Microsoft'un yerel Kusto Emulator sorgu motorunda çalışır; Azure Sentinel/Defender servisi, ajan alımı veya portal kural önizlemesi değildir. Hazırlık SQL'i yalnız örnek tablo verisini çıkarıp typed datatable/let olarak yollar. Öğrencinin KQL'i gerçek motorda ayrıştırılır ve değerlendirilir; desteklenmeyen ürün fonksiyonu sessiz taklit edilmez. Dersin yerel `_GetWatchlist` yardımcı fonksiyonu yalnız fixture listelerini döndürür; gerçek Sentinel watchlist hizmetine erişildiği iddia edilmez. Üretim kümesindeki izin, connector, ingestion, dcount yaklaşık sayımı ve null/string tür sözleşmesi ayrıca doğrulanmalıdır. Sunucu sorgu sınırı 30 saniye; yanıt sınırı 4 MB. Süre veya boyut aşımı başarı sayılmaz.

[Microsoft Kusto Emulator kapsamı](https://learn.microsoft.com/en-us/azure/data-explorer/kusto-emulator-overview). Kurulum README'dedir. Gerçek Sentinel çalışma alanı olmadan portalın **Test with current data** kabulü tamamlanmış sayılmaz.
```meta
motor: kusto
timeout: 90
```
:::


::: anlat OutputSchema: önce sözleşme, sonra veri
`evaluate bag_unpack(o,'b_') : (*, b_ms:long, b_zone:string)` çıktıyı açıkça tanımlar. Baştaki `*` kaynak sütunlarını korur; bag sütunu çıkarılır. Bildirilmeyen yeni bag anahtarları sonuç şemasını genişletmez. Kaynakta b_ms zaten varsa ad çakışmasını ayrıca çözmek gerekir; önek tek başına aynı önekli kaynak alanını sihirle düzeltmez.

Bu native motor sürümünde long OutputSchema sayısal metni sayıya dönüştürür (`"1001"` → 1001), sayı olmayan metinde null üretir; `1000.7` long'a geçerken 1000 olur. String şemasında sayı 4 → `"4"`, nesne → JSON metni olur; eksik/null string boş metindir. Bunlar **bag_unpack OutputSchema dönüşümleridir**; mv-apply typeof(long) cast'iyle aynı davranış sanma. Bu örnekler gerçek sabit imajda çalıştırıldı; başka motor/sürümde gerçek çıktıyı yeniden kontrol et. Bilinmeyen tür veya şemada olmayan alana project gerçek Kusto hatası verir; Pafta bunu başarıya çeviremez.

Microsoft açık OutputSchema'yı büyük veri üzerinde şemayı keşfetme maliyetini azaltmak için önerir. Bu emülatörde performans benchmark'ı yapmıyoruz; kabul yalnız semantik sonuçtur. [bag_unpack OutputSchema](https://learn.microsoft.com/en-us/kusto/query/bag-unpack-plugin).
```meta
motor: kusto
timeout: 90
```
:::

::: gorev Şemayı sabitle ve tür uyuşmazlığını görünür tut
`schema_kayitlari` tablosunda o metnini parse_json ile `bag` sütununa aç. Yalnız id,source_zone ve açılan b_ms/b_zone sütunları kalsın; kaynak `source_zone` korunmalı. `bag_unpack(bag,'b_'):(id:long,source_zone:string,b_ms:long,b_zone:string)` OutputSchema kullan. b_ms null ise durum `tip/eksik`; en az 1000 ise `yavas`; altı `normal`. Son sütun durum, id sırasında dön. 1000 eşit uç dahil; 999 hariç. Bozuk tipli değeri 0 yapıp normal sayma, yeni anahtarı otomatik şemaya alma.

```meta
motor: kusto
timeout: 90
```

```setup
CREATE TABLE schema_kayitlari(id INTEGER,source_zone TEXT,o TEXT);
INSERT INTO schema_kayitlari VALUES
(1,'kaynak-tr','{"ms":999,"zone":"tr"}'),
(2,'kaynak-tr','{"ms":1000,"zone":"tr"}'),
(3,'kaynak-de','{"ms":"1001","zone":4}'),
(4,'kaynak-x','{"ms":"oops","zone":{"x":1}}'),
(5,'kaynak-y','{}'),
(6,'kaynak-z','{"ms":1000.7,"zone":null}');
```

```starter
schema_kayitlari
| extend bag=parse_json(o)
| evaluate bag_unpack(bag,'b_')
| extend durum='normal'
| sort by id asc
```

```test
eq(sutunlar,['id','source_zone','b_ms','b_zone','durum'],'açık OutputSchema; kaynak alanı ve sabit çıktı')
eq(sonuc,[(1,'kaynak-tr',999,'tr','normal'),(2,'kaynak-tr',1000,'tr','yavas'),(3,'kaynak-de',1001,'4','yavas'),(4,'kaynak-x',None,'{"x":1}','tip/eksik'),(5,'kaynak-y',None,'','tip/eksik'),(6,'kaynak-z',1000,'','yavas')],'tip dönüşümü, bozuk tip, eksik alan ve 999/1000 sınırı')
eq(dene('''INSERT INTO schema_kayitlari VALUES (7,'yeni','{"ms":0,"zone":"","late_key":123}');''')[-1],(7,'yeni',0,'','normal'),'yeni anahtar şemayı değiştirmez, sıfır gerçek değer')
eq(dene('''INSERT INTO schema_kayitlari VALUES (7,'yeni','{"ms":null}');''')[-1],(7,'yeni',None,'','tip/eksik'),'JSON null sıfır değildir')
eq(dene('DELETE FROM schema_kayitlari;'),[],'boş veride de OutputSchema sütunları mevcut')
```

```solution
schema_kayitlari
| extend bag=parse_json(o)
| evaluate bag_unpack(bag,'b_'):(id:long,source_zone:string,b_ms:long,b_zone:string)
| extend durum=case(isnull(b_ms),'tip/eksik',b_ms >= 1000,'yavas','normal')
| sort by id asc
```

```hint
Şemanın içindeki id/source_zone kaynak sütunlarını korur; o ve bag'ı dışarıda bırakır. Eksik/bad long null olur; null'u 0'a çevirme.
```
:::
