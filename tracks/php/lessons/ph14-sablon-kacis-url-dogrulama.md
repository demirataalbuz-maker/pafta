---
id: ph14
title: Şablon Kaçışı ve URL Doğrulamanın Sınırları
summary: Blade {{ }} ile {!! !!}, Twig {{ }} ile |raw arasındaki fark ve otomatik kaçışın HTML bağlamına özgü olması; htmlspecialchars'ın PHP 8.1'den beri tek tırnağı da kaçırması; parse_url'ün yetki bölümünde son @'in host'u belirlemesi, http:/// için false dönmesi ve filter_var(FILTER_VALIDATE_URL)'ün kullanıcı bilgisi içeren aldatıcı adresi kabul etmesi; izin listesinin ayrıştırılmış host üzerinde tam eşleşmeyle uygulanması.
kazanim: ZCPE 6.1, ZCPE 6.5
---

::: anlat Şablonda kaçan ve kaçmayan çıktı
Şablon motorları değişkeni HTML'e yazarken **otomatik kaçırır**; ama her motorda bu kaçışı kapatan ikinci bir sözdizimi vardır. Kod incelemesinde önce bu ikinciyi ararsın.

| Motor | Kaçırır | Ham yazar |
|---|---|---|
| Blade (Laravel) | `{{ $deger }}` | `{!! $deger !!}` |
| Twig | `{{ deger }}` | `{{ deger\|raw }}`, `{% autoescape false %}` |

Kaçış, altta `htmlspecialchars` ile aynı işi yapar. PHP 8.1'den beri varsayılan bayraklar `ENT_QUOTES | ENT_SUBSTITUTE | ENT_HTML401`'dir; yani **tek tırnak da** kaçırılır. Bu derste ölçüldü: `htmlspecialchars("<a href='x'>\"&")` çıktısı `&lt;a href=&#039;x&#039;&gt;&quot;&amp;` olur. Eski kodda `ENT_QUOTES` elle verilmişse bunun nedeni budur; artık varsayılandır.

> [!TUZAK] Otomatik kaçış HTML gövdesi içindir, her bağlam için değil
> `htmlspecialchars` beş karakteri (`< > & " '`) HTML varlıklarına çevirir. Bu, metni **HTML gövdesine** ve **tırnaklı bir özniteliğe** güvenle koyar. Tırnaksız bir öznitelikte (`<div class={{ $x }}>`) boşluk yeni bir öznitelik başlatabilir; `<script>` içinde ya da `href="{{ $x }}"` gibi bir URL bağlamında ise kaçırılmış metin hâlâ `javascript:` ile başlayan bir adres olabilir. Doğru soru "kaçırıldı mı?" değil, "hangi bağlama yazılıyor?"dur.
:::

::: anlat parse_url ve filter_var ne söyler, ne söylemez
Bir adresin "bizim sitemize mi gidiyor" sorusunu metin üzerinde yanıtlamaya çalışmak yanıltıcıdır. URL'in **yetki** (authority) bölümü `//` ile başlar ve ilk `/`, `?` ya da `#` karakterinde biter. İçinde `@` varsa, **son** `@`'ten öncesi kullanıcı bilgisidir, sonrası host'tur.

Bu derste ölçülenler (PHP 8.4.24):

| Adres | `parse_url` host | `FILTER_VALIDATE_URL` |
|---|---|---|
| `https://good.example:80@evil.example/` | `evil.example` | **geçer** |
| `http://a@b@c@d.example/yol` | `d.example` | reddeder |
| `http://evil.example?@good.example/` | `evil.example` | — |
| `http://good.example#@evil.example/` | `good.example` | geçer |
| `//evil.example/x` | `evil.example` | reddeder |
| `javascript:alert(1)` | *(host yok)* | reddeder |
| `http:///a` | `parse_url` **false** döner | reddeder |

İlk satır işin özüdür: adres göz ucuyla `good.example`'a gidiyor gibi durur, gerçekte `evil.example`'a gider ve `filter_var` onu **geçerli** sayar. `FILTER_VALIDATE_URL` adresin biçimine bakar; nereye gittiğine, şemanın güvenli olup olmadığına ya da senin sitene ait olup olmadığına bakmaz.

> [!TUZAK] İzin listesini metin üzerinde değil, ayrıştırılmış host üzerinde uygula
> `str_contains($url, "good.example")` ya da `str_ends_with($host, "good.example")` gibi denetimler `https://good.example@evil.example/`, `https://good.example.evil.test/` ve `https://notgood.example/` adreslerinin üçünde de yanılır. Önce `parse_url` ile host'u çıkar, `false` ya da host yoksa reddet, sonra host'u izin listesindeki adlarla **tam** ve harf büyüklüğüne duyarsız karşılaştır. Alt alan adlarına izin verecekseniz bunu `"." . $izinli` ile biten ad kuralı gibi açıkça yazın.
:::

::: tahmin Adres nereye gidiyor?
```php
<?php
foreach (['https://good.example:80@evil.example/', 'http://a@b@c@d.example/yol', 'http:///a'] as $u) {
    $p = parse_url($u);
    echo str_pad($u, 38), " host=", ($p === false ? 'FALSE' : ($p['host'] ?? '-')),
         " filter=", filter_var($u, FILTER_VALIDATE_URL) === false ? 'RED' : 'GECER', "\n";
}
```

```gercek
https://good.example:80@evil.example/  host=evil.example filter=GECER
http://a@b@c@d.example/yol             host=d.example filter=RED
http:///a                              host=FALSE filter=RED
```

???

Birinci satır: host **`evil.example`**'dır. `good.example:80` kısmı `@`'ten önce kaldığı için kullanıcı adı ve paroladır, hedef değil. Üstelik `filter_var` bu adresi **geçerli** sayar — "doğrulamadan geçti" ile "güvenli" aynı şey değildir.

İkinci satır: üç `@` var; host **son** `@`'ten sonrasıdır, yani `d.example`. Burada `filter_var` reddediyor, ama bu kuralı "`@` varsa reddeder" diye genelleme: birinci satırda da `@` vardı ve geçti.

Üçüncü satır: `http:///a` için `parse_url` dizi değil **`false`** döndürür. Dönüşü diziymiş gibi kullanan kod burada sessizce boş host görür; `false` denetimini ayrı yapmak gerekir.
:::

::: gorev Host'u çıkar
`host_coz(url)` yaz: `parse_url`'ün host bulma kuralını modelle; host yoksa `None` döndür.

- `//` yoksa host yoktur.
- Yetki bölümü ilk `//`'den sonra başlar ve ilk `/`, `?` ya da `#` karakterinde biter.
- Yetki boşsa host yoktur.
- Yetkide `@` varsa host **son** `@`'ten sonrasıdır.
- Host kısmındaki `:port` soneki atılır.
- Geriye boş metin kalırsa host yoktur.

IPv6 adresleri (köşeli parantezli) bu modelin dışındadır.

```starter
def host_coz(url):
    if "//" not in url:
        return None
    yetki = url.split("//", 1)[1].split("/")[0]
    return yetki.split("@")[0]
```

```test
need("host_coz")
eq(host_coz("https://good.example:80@evil.example/"), "evil.example", "ölçülen: son @ host'u belirler")
eq(host_coz("http://a@b@c@d.example/yol"), "d.example", "ölçülen: üç @ olsa da sonuncusu")
eq(host_coz("http:///a"), None, "ölçülen: yetki boş, host yok")
eq(host_coz("http://evil.example?@good.example/"), "evil.example", "yetki ? ile biter")
eq(host_coz("http://good.example#@evil.example/"), "good.example", "yetki # ile biter")
eq(host_coz("//evil.example/x"), "evil.example", "şemasız adres")
eq(host_coz("javascript:alert(1)"), None, "// yok")
eq(host_coz("/sadece/yol"), None, "göreli yol")
eq(host_coz("http://good.example:8080/x"), "good.example", "port atılır")
eq(host_coz("https://good.example"), "good.example", "yol olmadan")
eq(host_coz("http://@/yol"), None, "ölçülen: yetki dolu ama host boş, parse_url false döner")
eq(host_coz("http://:8080/x"), None, "ölçülen: yalnız port, host yok")
eq(host_coz("http://@good.example/x"), "good.example", "boş kullanıcı bilgisi host'u bozmaz")
eq(host_coz(""), None, "boş metin")
```

```solution
def host_coz(url):
    if "//" not in url:
        return None
    yetki = url.split("//", 1)[1]
    for ayirac in ("/", "?", "#"):
        yetki = yetki.split(ayirac, 1)[0]
    if not yetki:
        return None
    host = yetki.rsplit("@", 1)[-1]
    host = host.split(":", 1)[0]
    return host or None
```

```hint
Başlangıç kodu iki yerde yanılıyor: yetkiyi yalnız `/` ile kesiyor (`?` ve `#` de bitirir) ve `@`'ten **ilk** parçayı alıyor. Host son `@`'ten sonrasıdır: `rsplit("@", 1)[-1]`.
```

```hint
Sırayı koru: önce yetkiyi ayır, sonra `@`, en son `:port`. Yetki ya da host boş kalırsa `None` döndür — `http:///a` bu yüzden host vermez.
```
:::

::: gorev İzin listesini doğru uygula
`izinli_mi(host, izinli)` yaz: `host_coz` ile çıkarılmış bir host'u izin listesine göre değerlendir.

- Karşılaştırma **tam eşleşme** olmalı; parça içerme ya da sonek eşleşmesi değil.
- Harf büyüklüğü önemsizdir; listedeki adlar da farklı yazılmış olabilir.
- `host` `None` ise sonuç `False`'tur.

```starter
def izinli_mi(host, izinli):
    for ad in izinli:
        if ad in (host or ""):
            return True
    return False
```

```test
need("izinli_mi")
eq(izinli_mi("good.example", ["good.example"]), True, "tam eşleşme")
eq(izinli_mi("GOOD.Example", ["good.example"]), True, "host'un harf büyüklüğü önemsiz")
eq(izinli_mi("good.example", ["GOOD.EXAMPLE"]), True, "listenin harf büyüklüğü de önemsiz")
eq(izinli_mi("evil.example", ["good.example"]), False, "listede yok")
eq(izinli_mi("good.example.evil.test", ["good.example"]), False,
   "parça içeriyor diye geçmemeli: gerçek host evil.test alanında")
eq(izinli_mi("notgood.example", ["good.example"]), False, "sonek eşleşmesi de yetmez")
eq(izinli_mi("good.example.", ["good.example"]), False, "sondaki nokta farklı bir addır")
eq(izinli_mi(None, ["good.example"]), False, "host çıkarılamadıysa reddet")
eq(izinli_mi("good.example", []), False, "boş liste hiçbir şeye izin vermez")
eq(izinli_mi("ikinci.example", ["good.example", "ikinci.example"]), True, "listenin ikinci öğesi")
```

```solution
def izinli_mi(host, izinli):
    if host is None:
        return False
    return host.lower() in [ad.lower() for ad in izinli]
```

```hint
Başlangıç kodu `in` ile **parça arıyor**; `good.example.evil.test` içinde `good.example` geçtiği için yanlışlıkla izin veriyor. İki tarafı da küçült ve eşitliğe bak.
```
:::
