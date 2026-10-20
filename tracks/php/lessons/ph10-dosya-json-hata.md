---
id: ph10
title: Dosyalar, JSON ve Hatalar
summary: include ve require farkı ve __DIR__, file_get_contents ve file_put_contents, json_decode'un dizi ve nesne kipleri ve hatada null döndürmesi, JSON_THROW_ON_ERROR, array_merge ile + işlecinin farkı, istisnalar ve üretimde hata göstermemek.
---

::: anlat Dosyalar ve içe alma
| Yapı | Dosya yoksa |
|---|---|
| `include "a.php"` | uyarı verir, devam eder |
| `require "a.php"` | ölümcül hata, durur |
| `include_once` / `require_once` | dosya daha önce alınmışsa tekrar almaz |

Göreli yollar çalışma klasörüne göre çözüldüğü için güvenilir kod her zaman betiğin kendi klasörünü kullanır: `require __DIR__ . "/ayar.php";`.

```php
<?php
$metin = file_get_contents(__DIR__ . "/veri/ayar.json");   // hatada false
file_put_contents(__DIR__ . "/gunluk.txt", "satır\n", FILE_APPEND | LOCK_EX);
```

> [!GÜVENLİK]
> `include` ya da `file_get_contents`'e verilen yol istekten geliyorsa (`$_GET["sayfa"]`), kullanıcı programın okuyacağı ya da çalıştıracağı dosyayı seçebilir. Güvenli kod yolu sabit bir izin listesinden seçer ya da `realpath()` ile çözüp izin verilen klasörün içinde kaldığını denetler (JS10'daki kalıbın PHP karşılığı).
:::

::: anlat JSON ve diziler
`json_decode` ikinci argümana göre farklı türler döndürür ve **hata durumunda istisna fırlatmaz**, sessizce `null` döndürür:

```php
<?php
$j = '{"ad":"web01","portlar":[80,443],"etkin":true}';
$dizi = json_decode($j, true);          // ilişkisel dizi: $dizi["ad"]
$nesne = json_decode($j);               // stdClass nesnesi: $nesne->ad
$bozuk = json_decode("{bozuk");         // null, json_last_error() hata kodunu verir
$guvenli = json_decode($j, true, flags: JSON_THROW_ON_ERROR);   // hatada JsonException
```

`null` hem "bozuk JSON" hem de geçerli `"null"` metninin sonucu olabildiği için, hatayı `json_last_error()` ya da `JSON_THROW_ON_ERROR` olmadan güvenle ayırt edemezsin.

### Dizileri birleştirmek: array_merge ile +
| İşlem | Aynı metin anahtarında |
|---|---|
| `array_merge($a, $b)` | **sağdaki** kazanır |
| `$a + $b` | **soldaki** kazanır; `$b`'den yalnızca `$a`'da olmayan anahtarlar eklenir |

Varsayılan ayarlarla kullanıcı ayarlarını birleştiren kodda hangisinin kullanıldığı, kimin kimi ezdiğini belirler:

```php
<?php
$varsayilan = ["port" => 80, "hata_ayikla" => false];
$kullanici  = ["port" => 8443];
print_r(array_merge($varsayilan, $kullanici));   // port 8443: kullanıcı kazandı
print_r($kullanici + $varsayilan);               // port 8443: soldaki kazandı, hata_ayikla eklendi
```

### Hatalar ve istisnalar
PHP 8'de çoğu ciddi hata `Error` ya da `Exception` olarak fırlatılır ve `try/catch (Throwable $e)` ile yakalanır. Üretim sunucusunda hatalar **gösterilmez**, günlüğe yazılır: `display_errors=Off`, `log_errors=On`. Ekranda yığın izi ve dosya yolları gösteren bir hata sayfası, uygulamanın iç yapısını dışarıya açar.
:::

::: tahmin
PHP 8 ile çıktı:

```php
<?php
$j = '{"ad":"web01","portlar":[80,443],"etkin":true}';
$a = json_decode($j, true);
echo $a["portlar"][1], " ", count($a), "\n";
$o = json_decode($j);
echo $o->ad, " ", var_export($o->etkin, true), "\n";
var_dump(json_decode("{bozuk"));
echo json_last_error() === JSON_ERROR_NONE ? "tamam" : "hata", "\n";
```

```gercek
443 3
web01 true
NULL
hata
```

???

`443 3`: dizi kipinde `portlar` sıralı bir dizidir, 1. eleman 443; nesnede üç anahtar var. `web01 true`: nesne kipinde alanlara `->` ile erişilir; `var_export` bool'u `true` diye yazar. `NULL`: bozuk JSON istisna fırlatmaz, `null` döner. `hata`: hatanın tek izi `json_last_error()`'dadır.
:::

::: gorev Ayar dosyası
Aşağıdaki PHP fonksiyonunu Python'a `ayar_oku(metin)` olarak çevir: geçerli bir JSON **nesnesi** değilse `ValueError("geçersiz ayar")` fırlatsın (bozuk JSON, dizi, sayı, `null` hepsi geçersiz); geçerliyse varsayılanlarla `array_merge` gibi birleştirip döndürsün.

```php
function ayar_oku(string $metin): array {
    $o = json_decode($metin);                 // nesne kipi: {} ile [] ayırt edilebilsin
    if (!($o instanceof stdClass)) {
        throw new InvalidArgumentException("geçersiz ayar");
    }
    return array_merge(["port" => 80, "hata_ayikla" => false], (array)$o);
}
```

Neden nesne kipi? Dizi kipinde (`json_decode($metin, true)`) hem `{}` hem `[]` aynı boş PHP dizisine dönüşür; ikisini ayırt etmenin yolu kalmaz.

```starter
import json


def ayar_oku(metin):
    return json.loads(metin)
```

```test
need("ayar_oku")
eq(ayar_oku('{"port": 8443}'), {"port": 8443, "hata_ayikla": False}, "kullanıcı portu kazanır")
eq(ayar_oku("{}"), {"port": 80, "hata_ayikla": False}, "boş nesne: varsayılanlar")
for bozuk in ["{bozuk", "[1, 2]", "42", "null", ""]:
    try:
        ayar_oku(bozuk)
        ok(False, f"{bozuk!r} reddedilmeliydi")
    except ValueError as e:
        eq(str(e), "geçersiz ayar", f"{bozuk!r} reddedildi")
```

```solution
import json


def ayar_oku(metin):
    try:
        a = json.loads(metin)
    except json.JSONDecodeError:
        raise ValueError("geçersiz ayar")
    if not isinstance(a, dict):
        raise ValueError("geçersiz ayar")
    return {"port": 80, "hata_ayikla": False, **a}
```

```hint
`json.loads` bozuk metinde `JSONDecodeError` fırlatır (o da bir `ValueError`'dır, ama mesajı farklıdır); yakalayıp kendi mesajınla yeniden fırlat.
```

```hint
Yalnızca sözlük kabul edilir: `isinstance(a, dict)`. `array_merge` sağdakini kazandırır: `{**varsayilan, **a}`.
```
:::

::: gorev array_merge ile +
Metin anahtarlı PHP dizileri için iki birleştirmeyi Python sözlükleriyle taklit et: `array_merge(a, b)` ve `arti(a, b)` (PHP'deki `$a + $b`). Anahtar **sırası** da PHP'deki gibi olsun: önce `a`'nın anahtarları kendi sırasıyla, sonra `b`'de olup `a`'da olmayanlar.

```starter
def array_merge(a, b):
    return {**a, **b}


def arti(a, b):
    return {**a, **b}
```

```test
need("array_merge")
need("arti")
v = {"port": 80, "hata_ayikla": False}
k = {"port": 8443, "tema": "koyu"}
eq(list(array_merge(v, k).items()), [("port", 8443), ("hata_ayikla", False), ("tema", "koyu")], "sağdaki kazanır")
eq(list(arti(v, k).items()), [("port", 80), ("hata_ayikla", False), ("tema", "koyu")], "soldaki kazanır")
eq(list(arti(k, v).items()), [("port", 8443), ("tema", "koyu"), ("hata_ayikla", False)], "sıra: önce sol")
```

```solution
def array_merge(a, b):
    sonuc = dict(a)
    sonuc.update(b)
    return sonuc


def arti(a, b):
    sonuc = dict(a)
    for anahtar, deger in b.items():
        if anahtar not in sonuc:
            sonuc[anahtar] = deger
    return sonuc
```

```hint
`+` işlecinde soldaki değerler hiç değişmez; sağdan yalnızca **yeni** anahtarlar eklenir.
```
:::
