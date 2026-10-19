---
id: ph02
title: Diziler ve Döngüler
summary: Sıralı ve ilişkisel diziler, foreach, sık kullanılan dizi fonksiyonları, explode/implode, isset ile empty farkı ve var_dump.
---

::: anlat PHP'nin tek veri yapısı: dizi
PHP'de liste de sözlük de **dizidir** (array). Anahtar verilmezse 0'dan başlayan sayılar kullanılır:

```php
<?php
$roller = ["web", "db", "dizin"];                        // sıralı: 0, 1, 2
$cpu = ["web01" => 72, "db01" => 91, "web03" => 18];     // ilişkisel: anahtar => değer
$cpu["dc01"] = 33;                                       // ekle
$roller[] = "yedek";                                     // sona ekle

foreach ($cpu as $ad => $deger) {                        // anahtar ve değer
    echo "$ad: $deger\n";
}
echo count($cpu), " ", $roller[1], "\n";                 // 4 db
```

| Fonksiyon | Ne yapar | Python karşılığı |
|---|---|---|
| `count($a)` | eleman sayısı | `len(a)` |
| `array_keys($a)`, `array_values($a)` | anahtarlar / değerler | `list(d)`, `list(d.values())` |
| `in_array($x, $a)` | değerlerde var mı | `x in d.values()` |
| `array_key_exists($k, $a)` | anahtar var mı | `k in d` |
| `array_sum($a)`, `max($a)` | toplam, en büyük | `sum`, `max` |
| `explode(",", $s)` | metni böl | `s.split(",")` |
| `implode(",", $a)` | birleştir | `",".join(a)` |
| `array_map($fn, $a)`, `array_filter($a, $fn)` | dönüştür, süz | `map`, `filter` |

### isset ve empty
| | `isset($x)` | `empty($x)` |
|---|---|---|
| tanımsız ya da `null` | false | true |
| `0`, `"0"`, `""`, `[]`, `false` | true | **true** |
| `"web"`, `72` | true | false |

> [!TUZAK]
> `empty("0")` **true** döner: PHP "0" metnini boş sayar. Bir form alanına 0 yazan kullanıcıyı "hiçbir şey girmedi" diye reddeden kodların sebebi budur. Gerçekten "değer var mı" diye soruluyorsa `isset` ve `!== ""` birlikte kullanılır.

`var_dump` bir değeri türüyle birlikte yazar; kod incelemede ve hata ayıklamada sık görülür: `var_dump(72 > 50)` → `bool(true)`.
:::

::: tahmin
Çıktı:

```php
<?php
$s = ["web01" => 72, "db01" => 91, "web03" => 18];
foreach ($s as $ad => $cpu) {
    if ($cpu > 50) echo "$ad ";
}
echo "\n", count($s), " ", array_sum($s), "\n";
echo implode(",", array_keys($s)), "\n";
var_dump(isset($s["db02"]), empty($s["web03"]));
```

```gercek
web01 db01
3 181
web01,db01,web03
bool(false)
bool(false)
```

???

`web01 db01` (sonunda bir boşluk), `3 181`, `web01,db01,web03`, `bool(false)`, `bool(false)`. CPU'su 50'yi aşan iki sunucu yazılır. Dizide 3 eleman var, toplamları 181. `db02` anahtarı olmadığı için `isset` false; `web03`'ün değeri 18 olduğu için `empty` false. `var_dump` her değeri ayrı satıra türüyle yazar.
:::

::: gorev Ayar satırı
Aşağıdaki PHP fonksiyonu `anahtar=değer;anahtar=değer` biçimindeki bir ayar satırını diziye çeviriyor. Python'a `ayar_coz(satir)` olarak çevir: bir `dict` döndürsün.

```php
function ayar_coz($satir) {
    $sonuc = [];
    foreach (explode(";", $satir) as $parca) {
        $parca = trim($parca);
        if ($parca === "" || strpos($parca, "=") === false) continue;
        [$k, $v] = explode("=", $parca, 2);
        $sonuc[trim($k)] = trim($v);
    }
    return $sonuc;
}
```

```starter
def ayar_coz(satir):
    return dict(p.split("=") for p in satir.split(";"))
```

```test
need("ayar_coz")
eq(ayar_coz("port=443;tls=evet"), {"port": "443", "tls": "evet"}, "iki ayar")
eq(ayar_coz(" host = web01 ; ; bozuk ; yol=/a=b "), {"host": "web01", "yol": "/a=b"}, "boşluklar, boş ve = içermeyen parçalar, değerde =")
eq(ayar_coz(""), {}, "boş satır")
```

```solution
def ayar_coz(satir):
    sonuc = {}
    for parca in satir.split(";"):
        parca = parca.strip()
        if parca == "" or "=" not in parca:
            continue
        k, v = parca.split("=", 1)
        sonuc[k.strip()] = v.strip()
    return sonuc
```

```hint
`explode("=", $parca, 2)` en fazla iki parçaya böler: Python'da `split("=", 1)`.
```

```hint
`strpos(...) === false`, "= yoksa" demektir: `"=" not in parca`.
```
:::

::: gorev empty'nin davranışı
PHP'nin `empty($x)` sonucunu Python değerleri için taklit eden `php_empty(x)` fonksiyonunu yaz: `None`, `False`, `0`, `0.0`, `""`, `"0"` ve boş liste/sözlük için `True`, diğer her şey için `False`.

```starter
def php_empty(x):
    return not x
```

```test
need("php_empty")
for deger, beklenen in [(None, True), (False, True), (0, True), (0.0, True), ("", True), ("0", True),
                        ([], True), ({}, True), ("00", False), (" ", False), ("web", False), (72, False), ([0], False)]:
    eq(php_empty(deger), beklenen, f"empty({deger!r})")
```

```solution
def php_empty(x):
    return x == "0" or not x
```

```hint
Python'un `not x`'i neredeyse aynı davranır; tek fark `"0"` metni: Python onu doğru sayar, PHP boş sayar.
```
:::
