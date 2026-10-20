---
id: sp19
title: Bilgi nesneleri, CIM ve veri modelleri
summary: Bir kez tanımlanıp herkesin kullandığı arama parçaları; argümanlı makrolar ve metin olarak açılmaları, olay türleri ve etiketler, props.conf'ta alan takma adları ve hesaplanan alanlar, arama zamanı işlem sırası, CIM alan adları, veri modelleri ve tstats.
---

::: anlat Bilgi nesnesi nedir?
Gerçek bir Splunk kurulumunda aramaların çoğu sıfırdan yazılmaz. Ekipler sık kullanılan parçaları **bilgi nesnesi** (knowledge object) olarak bir kez tanımlar, herkes adıyla kullanır. Tanımlar Splunk Web'de *Ayarlar* menüsünden ya da doğrudan `.conf` dosyalarından yapılır. Her nesnenin bir sahibi ve paylaşım düzeyi vardır: **özel** (yalnızca sahibi), **uygulama** (o uygulamanın kullanıcıları) ya da **genel** (bütün uygulamalar).

| Nesne | Ne işe yarar | Tanımlandığı yer | Aramada |
|---|---|---|---|
| makro | aramanın bir parçasını adla saklar | `macros.conf` | `` `ad` ``, `` `ad(a, b)` `` |
| olay türü | kayıtlı bir aramayla olayları sınıflar | `eventtypes.conf` | `eventtype=ad` |
| etiket | bir alan=değer çiftine ad verir | `tags.conf` | `tag=ad`, `tag::alan=ad` |
| alan takma adı | bir alana ikinci bir ad verir | `props.conf`, `FIELDALIAS-` | kendiliğinden |
| hesaplanan alan | her olaya bir `eval` ifadesi uygular | `props.conf`, `EVAL-` | kendiliğinden |
| otomatik lookup | başvuru tablosunu her aramada ekler | `props.conf`, `LOOKUP-` | kendiliğinden |
| iş akışı eylemi | alan menüsüne bağlantı ya da arama ekler | `workflow_actions.conf` | arayüzde tıklanır |
| veri modeli | etiketlere dayalı, CIM adlı bir veri kümesi | `datamodels.conf` | `\| tstats ... from datamodel=...` |

### Arama zamanı işlem sırası
Splunk bir olayı okurken arama zamanı işlemlerini **sabit bir sırayla** uygular:

1. alan çıkarma (satır içi `EXTRACT`, dönüşümlü `REPORT`, otomatik anahtar=değer)
2. alan takma adları (`FIELDALIAS`)
3. hesaplanan alanlar (`EVAL`)
4. otomatik lookup'lar (`LOOKUP`)
5. olay türleri
6. etiketler

Sıranın sonucu: hesaplanan bir alan bir takma adı kullanabilir, bir olay türü hesaplanan bir alana bakabilir, bir etiket bir olay türüne verilebilir. Tersi olmaz: bir takma ad, sonradan hesaplanan bir alana ad veremez. Hesaplanan alanlar da aynı anda değerlendirilir, biri ötekini kullanamaz.

> [!NOT]
> Pafta tezgahında bu tanımlar veritabanındaki tablolardan okunur: `makrolar`, `olay_turleri`, `etiketler`, `alan_takma_adlari` ve `hesaplanan_alanlar`. İstersen `| inputlookup makrolar` ile içlerine bakabilirsin.
:::

::: anlat Makrolar
Makro, bir arama parçasına verilen addır. `macros.conf`'ta argüman sayısı adın parçasıdır: `yavas(1)` ile `yavas` iki ayrı makrodur. Argümanlar tanımda `$ad$` olarak geçer:

```ini
[sunucu_hatalari]
definition = sourcetype=istekler durum>=500

[yavas(1)]
args = esik
definition = sure_ms>$esik$

[yuzde(2)]
args = pay, payda
definition = round(100 * $pay$ / $payda$, 1)
```

Makro **ters tırnakla** çağrılır (`` ` ``, tek tırnak değil). Splunk aramayı ayrıştırmadan önce her çağrıyı tanımının metniyle değiştirir. Bu yüzden bir makro arama terimleri, bütün bir komut ya da bir `eval` ifadesi olabilir:

```spl
`sunucu_hatalari`
| stats count by sunucu
```

```spl
`web_istekleri` `yavas(1000)`
| `sunucu_ozeti`
```

```spl
`web_istekleri`
| stats count(eval(durum>=400)) AS hata, count AS toplam by sunucu
| eval oran = `yuzde(hata, toplam)`
```

Tezgahtaki makrolar:

| Çağrı | Tanım |
|---|---|
| `` `web_istekleri` `` | `sourcetype=istekler` |
| `` `sunucu_hatalari` `` | `sourcetype=istekler durum>=500` |
| `` `hata_kodlari` `` | `durum=500 OR durum=503` |
| `` `yavas(esik)` `` | `sure_ms>$esik$` |
| `` `yuzde(pay, payda)` `` | `round(100 * $pay$ / $payda$, 1)` |
| `` `sunucu_ozeti` `` | `stats count AS istek, avg(sure_ms) AS ort_sure by sunucu` |

Splunk Web'de arama kutusundayken **Ctrl+Shift+E** (macOS'ta Cmd+Shift+E) aramayı makroları açılmış hâliyle gösterir. Tezgahta bir makro hatası, hata mesajının sonuna aramanın açılmış hâlini ekler.

> [!TUZAK]
> Makro bir **metindir**, bir değer değil. `` | `yavas(500)` `` boru işaretinden sonra `| sure_ms>500` olur ve hata verir: arama terimi olan bir makroyu arama terimlerinin yazıldığı yerde kullan. Birden çok terim içeren tanımları parantez içine al: makronun önüne `NOT` gelirse parantezsiz tanım yalnızca ilk terimi olumsuzlar.
:::

::: tahmin
İki sayı yazar. Hangileri?

```spl
sourcetype=istekler NOT `hata_kodlari`
| stats count

sourcetype=istekler NOT (`hata_kodlari`)
| stats count
```

???

`23`, sonra `22`. `hata_kodlari` metin olarak açılır ve ilk arama `NOT durum=500 OR durum=503` olur. `NOT` yalnızca hemen arkasındaki terime bağlanır: `(NOT durum=500) OR durum=503`. Bu, 26 istekten yalnızca üç tane 500'ü atar; 503'lük istek `OR` sayesinde geri gelir. Parantezli aramada `NOT` bütün tanıma uygulanır ve dört hatalı istek de düşer.
:::

::: anlat Olay türleri ve etiketler
**Olay türü**, bir olay sınıfına ad veren kayıtlı bir aramadır. Tanımında boru (`|`) ve alt arama olamaz; yalnızca arama terimleri:

```ini
# eventtypes.conf
[sunucu_hatasi]
search = sourcetype=istekler durum>=500

[yazma_istegi]
search = sourcetype=istekler (yontem=POST OR yontem=PUT OR yontem=DELETE)
```

**Etiket**, bir alan=değer çiftine verilen addır. Olay türü de, sourcetype da etiketlenebilen birer alandır:

```ini
# tags.conf
[eventtype=sunucu_hatasi]
hata = enabled

[eventtype=istemci_hatasi]
hata = enabled

[sourcetype=istekler]
web = enabled

[yontem=POST]
yazma = enabled
```

Aramada `eventtype=ad`, `tag=etiket` ve yalnızca bir alana bakan `tag::alan=etiket` yazılır. `*` joker karakteri de çalışır:

```spl
eventtype=yavas_istek
| table sunucu yol sure_ms
```

```spl
sourcetype=istekler tag=hata
| stats count by durum
```

```spl
sourcetype=istekler tag::yontem=yazma NOT eventtype=istemci_hatasi
| table yontem yol durum
```

Tezgahtaki olay türleri: `sunucu_hatasi` (durum ≥ 500), `istemci_hatasi` (400–499), `yavas_istek` (süre > 1000 ms), `yazma_istegi` (POST, PUT, DELETE), `uygulama_hatasi` (gunluk, seviye ERROR). Etiketler: `hata` (üç hata olay türü), `performans` (`yavas_istek`), `web` (`sourcetype=istekler`), `yazma` (POST, PUT, DELETE).

Etiketin değeri anlamdadır: "hata" kavramının tanımı değişirse yalnızca `tags.conf` değişir, ona dayanan bütün aramalar, uyarılar ve panolar kendiliğinden doğru kalır.

> [!NOT]
> Gerçek Splunk her olaya, eşleştiği olay türlerini `eventtype` ve etiketlerini `tag` adlı çok değerli alanlar olarak da ekler; `stats count by eventtype` orada çalışır. Tezgah yalnızca süzmeyi destekler. Bir de gerçek Splunk bir olay türünü bütün sourcetype'larda arar, tezgahta ise her arama tek bir sourcetype okur: `sourcetype` yazmazsan olay türünün ya da etiketin tanımındaki sourcetype kullanılır.
:::

::: anlat Alan takma adları, hesaplanan alanlar ve CIM
Farklı kaynaklar aynı şeye farklı adlar verir: bir günlükte `istemci`, ötekinde `clientip`, bir başkasında `src_ip`. **CIM** (Common Information Model), Splunk'ın ortak alan adları sözlüğüdür: istemci adresi her yerde `src`, hedef `dest`, kullanıcı `user`, HTTP yöntemi `http_method`, durum kodu `status`, yol `uri_path`. Kaynak verisine dokunmadan bu adları `props.conf` verir:

```ini
# props.conf
[istekler]
FIELDALIAS-cim = istemci AS src sunucu AS dest kullanici AS user yontem AS http_method durum AS status yol AS uri_path
EVAL-durum_sinifi = case(durum>=500, "5xx", durum>=400, "4xx", true(), "başarılı")
```

Bu adımda tezgaha bu iki satırın karşılığı tanımlı. Takma adlar ve hesaplanan alan, her `sourcetype=istekler` aramasında **kendiliğinden** gelir:

```spl
sourcetype=istekler status>=500
| table _time src dest http_method uri_path status durum_sinifi
```

### Veri modelleri ve tstats
**Veri modeli**, etiketlerle tanımlanan ve CIM adlarıyla çalışan bir veri kümesidir. CIM'in `Web` veri modeli `tag=web` etiketli olayları kapsar; `Authentication` modeli `tag=authentication`, `Network_Traffic` modeli `tag=network tag=communicate`. Bir kaynağı bir modele bağlamak, ona doğru etiketi ve CIM adlarını vermektir. Ondan sonra o model için yazılmış her rapor ve pano, hiç değiştirilmeden o kaynağı da okur.

Bir veri modeli **hızlandırılmışsa** Splunk onun özetlerini önceden hesaplar ve `tstats` bu özetlerden okur. Ham olaylara dokunmadığı için aynı `stats` aramasından kat kat hızlıdır:

```spl norun
| tstats count from datamodel=Web where Web.status>=500 by Web.dest
```

`summariesonly=true` yalnızca hazır özetleri kullanır: daha hızlıdır ama özetlenmemiş son verileri atlar. Tezgahta `tstats` yok. Aynı soruyu veri modelinin tanımıyla, yani etiketle ve CIM adlarıyla sorarsın:

```spl
tag=web status>=500
| stats count by dest
```

```setup
INSERT INTO alan_takma_adlari VALUES
 ('istekler', 'istemci', 'src'), ('istekler', 'sunucu', 'dest'), ('istekler', 'kullanici', 'user'),
 ('istekler', 'yontem', 'http_method'), ('istekler', 'durum', 'status'), ('istekler', 'yol', 'uri_path');
INSERT INTO hesaplanan_alanlar VALUES
 ('istekler', 'durum_sinifi', 'case(durum>=500, "5xx", durum>=400, "4xx", true(), "başarılı")');
```
:::

::: gorev Makrolarla hata oranı
`web_istekleri` makrosuyla başla. Her sunucu için istek sayısını (`toplam`) ve durumu 500 ya da üstü olan istekleri (`hata`) say, sonra hata yüzdesini `yuzde` makrosuyla `oran` alanına yaz. Sütunlar: `sunucu`, `toplam`, `hata`, `oran`.

```starter
sourcetype=istekler
| stats count AS toplam by sunucu
```

```test
import re
eq(sutunlar, ["sunucu", "toplam", "hata", "oran"], "sunucu, toplam, hata, oran")
eq(sonuc, [("web01", 11, 3, 27.3), ("web02", 9, 1, 11.1), ("web03", 6, 0, 0.0)], "web01 %27.3, web02 %11.1, web03 %0")
ok(re.search(r"`\s*web_istekleri\s*`", src), "aramaya `web_istekleri` makrosuyla başla")
ok(re.search(r"`\s*yuzde\s*\(", src), "oranı `yuzde(pay, payda)` makrosuyla hesapla")
```

```solution
`web_istekleri`
| stats count AS toplam, count(eval(durum>=500)) AS hata by sunucu
| eval oran = `yuzde(hata, toplam)`
```

```hint
Hatalı istekleri aynı `stats` içinde say: `count(eval(durum>=500)) AS hata`. Makro bir eval ifadesine de açılabilir: `` | eval oran = `yuzde(hata, toplam)` ``.
```
:::

::: gorev Makroyu aç
Aşağıdaki aramanın makroları **açılmış** hâlini yaz: aynı sonucu veren ama hiç ters tırnak içermeyen arama. Tanımlar anlatımdaki tabloda.

```spl norun
`web_istekleri` `yavas(1000)`
| `sunucu_ozeti`
```

```starter
`web_istekleri` `yavas(1000)`
| `sunucu_ozeti`
```

```test
eq(sutunlar, ["sunucu", "istek", "ort_sure"], "sunucu, istek, ort_sure")
eq([(r[0], r[1], round(r[2], 1)) for r in sonuc], [("web01", 3, 2203.3), ("web02", 2, 1900.0)], "iki sunucuda yavaş istek var")
ok("`" not in src, "ters tırnak kullanma: makroları kendin aç")
ok(kullanir("stats"), "sunucu_ozeti bir stats komutudur")
```

```solution
sourcetype=istekler sure_ms>1000
| stats count AS istek, avg(sure_ms) AS ort_sure by sunucu
```

```hint
Her çağrının yerine tanımını yaz ve `$esik$` yerine `1000` koy: `web_istekleri` → `sourcetype=istekler`, `yavas(1000)` → `sure_ms>1000`.
```
:::

::: gorev Etiketle ve olay türüyle
Yazma isteklerinden istemci hatasıyla bitmeyenleri yönteme göre say: `yontem`, `count`. Hangi yöntemin yazma sayıldığını ve hangi durumların istemci hatası olduğunu aramada yazma; bu bilgiler `yazma` etiketinde ve `istemci_hatasi` olay türünde duruyor.

```starter
sourcetype=istekler (yontem=POST OR yontem=PUT OR yontem=DELETE)
| stats count by yontem
```

```test
import re
eq(sonuc, [("POST", 2), ("PUT", 1)], "POST 2, PUT 1 (DELETE isteği 404 ile bitti)")
ok(kullanir("tag"), "yazma isteklerini etiketle seç")
ok(kullanir("eventtype"), "istemci hatalarını olay türüyle ayır")
ok(not re.search(r"\b(POST|PUT|DELETE)\b", src) and not kullanir("durum"), "yöntem adlarını ve durum kodlarını aramaya yazma")
```

```solution
sourcetype=istekler tag=yazma NOT eventtype=istemci_hatasi
| stats count by yontem
```

```hint
`tag=yazma` üç yöntemi birden seçer. `NOT eventtype=istemci_hatasi` 400'lü durumla biten istekleri atar.
```
:::

::: gorev CIM adlarıyla
Bu adımda alan takma adı tanımlı değil. Durumu 400 ya da üstü olan istekleri hedef sunucu ve durum koduna göre say, ama sonucu **CIM adlarıyla** ver: `dest`, `status`, `count`.

```starter
sourcetype=istekler durum>=400
| stats count by sunucu durum
```

```test
eq(sutunlar, ["dest", "status", "count"], "CIM adları: dest, status, count")
eq(sonuc, [("web01", 500, 2), ("web01", 503, 1), ("web02", 404, 1), ("web02", 500, 1)], "dört grup")
```

```solution
sourcetype=istekler durum>=400
| rename sunucu AS dest, durum AS status
| stats count by dest status
```

```hint
`rename sunucu AS dest, durum AS status` alanları CIM adlarına çevirir; `stats` yeni adları kullanır. `props.conf`'taki `FIELDALIAS` aynı işi her aramada kendiliğinden yapar.
```
:::

::: gorev Veri modeli gibi sor
Bu adımda anlatımdaki `props.conf` tanımları (takma adlar ve `durum_sinifi`) yüklü. Bir panoda şu arama var:

```spl norun
| tstats count from datamodel=Web where Web.durum_sinifi="5xx" by Web.dest
```

Tezgahta aynı soruyu veri modelinin kendi tanımıyla sor: sourcetype yerine modelin etiketi, ham alan adları yerine CIM adları ve hesaplanan alan. Sütunlar: `dest`, `count`.

```starter
sourcetype=istekler durum>=500
| stats count by sunucu
```

```test
eq(sutunlar, ["dest", "count"], "dest, count")
eq(sonuc, [("web01", 3), ("web02", 1)], "web01 3, web02 1")
ok(kullanir("tag"), "veri modelinin kısıtı bir etikettir: tag=web")
ok(not kullanir("sourcetype"), "sourcetype yazma: kaynağı etiket belirlesin")
ok(not kullanir("durum") and not kullanir("sunucu"), "ham alan adları yerine CIM adlarını ve hesaplanan alanı kullan")
```

```solution
tag=web durum_sinifi="5xx"
| stats count by dest
```

```hint
`Web` modeli `tag=web` olaylarını kapsar. Koşulda hesaplanan `durum_sinifi` alanını, gruplamada takma ad `dest`'i kullan.
```

```setup
INSERT INTO alan_takma_adlari VALUES
 ('istekler', 'istemci', 'src'), ('istekler', 'sunucu', 'dest'), ('istekler', 'kullanici', 'user'),
 ('istekler', 'yontem', 'http_method'), ('istekler', 'durum', 'status'), ('istekler', 'yol', 'uri_path');
INSERT INTO hesaplanan_alanlar VALUES
 ('istekler', 'durum_sinifi', 'case(durum>=500, "5xx", durum>=400, "4xx", true(), "başarılı")');
```
:::
