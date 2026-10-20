---
id: ph06
title: Metinler ve Baytlar
summary: PHP metinlerinin bayt dizisi olması; strlen ile mb_strlen, strtoupper ile mb_strtoupper, strpos'un 0 döndürmesi tuzağı ve str_contains, substr, explode/implode, sprintf/printf biçimleri, heredoc ve "{$x}" ara değer yerleştirme.
---

::: anlat Bir metin, bir bayt dizisi
PHP'de bir metin (string) aslında **bayt dizisidir**; kodlamayı bilmez. Türkçe harfler UTF-8'de 2 bayt kapladığı için bayt sayan fonksiyonlar "yanlış" görünen sonuçlar verir:

| Fonksiyon | Ne sayar / ne yapar | `"şehir"` için |
|---|---|---|
| `strlen($s)` | bayt | 6 |
| `mb_strlen($s)` | karakter (UTF-8) | 5 |
| `strtoupper($s)` | yalnızca ASCII harfleri büyütür | `şEHIR` |
| `mb_strtoupper($s)` | Unicode harfleri büyütür | `ŞEHIR` |
| `substr($s, 0, 1)` | ilk **bayt** | yarım bir `ş` (bozuk karakter) |
| `mb_substr($s, 0, 1)` | ilk karakter | `ş` |

Kullanıcı adı uzunluğu, metin kısaltma ya da büyük-küçük harf dönüşümü yapan kodda `mb_` fonksiyonlarını aramak, okurken yapılacak ilk kontroldür. `strtoupper`'ın Türkçe `i`'yi `İ` değil `I` yapması da cabası.

### strpos'un 0 tuzağı
`strpos($samanlik, $igne)` bulduğu **konumu** döndürür, bulamazsa `false`. Aranan metnin başta olması durumunda konum `0`'dır ve `0` gevşek karşılaştırmada `false` sayılır:

```php
<?php
$yol = "admin.php";
if (strpos($yol, "admin")) {            // 0 → yanlışımsı: buraya GİRMEZ
    echo "bulundu";
}
if (strpos($yol, "admin") !== false) {  // doğrusu
    echo "bulundu";
}
if (str_contains($yol, "admin")) {      // PHP 8: daha açık
    echo "bulundu";
}
```

Bu kalıp yetki ve yol denetimlerinde ciddi hatalara yol açar: "metnin başında X varsa izin verme" diye yazılmış bir `if (strpos(...))` tam da o durumda çalışmaz.
:::

::: anlat Birleştirme, bölme, biçimlendirme
| Fonksiyon | Örnek | Sonuç |
|---|---|---|
| `explode(",", "a,b,,c")` | metni böl | `["a", "b", "", "c"]` |
| `implode("\|", $dizi)` | birleştir | `"a\|b\|\|c"` |
| `substr("pafta", 1, 3)` | 1. bayttan 3 bayt | `"aft"` |
| `substr("pafta", -2)` | son 2 bayt | `"ta"` |
| `str_replace("a", "o", $s)` | bütün eşleşmeleri değiştir | |
| `trim($s)` | baş ve sondaki boşlukları at | |
| `sprintf("%05.1f", 3.14159)` | biçimlendir | `"003.1"` |

`printf` ve `sprintf` belirteçleri C'dekilerle aynıdır (C01): `%d`, `%s`, `%x`, `%05.1f`, `%-6s` (sola yaslı, 6 genişlik).

Çift tırnaklı metinlerde ve heredoc'ta değişkenler yerine konur; karmaşık ifadeler için süslü parantez kullanılır:

```php
<?php
$s = ["ad" => "web01", "cpu" => 72];
echo "Sunucu {$s['ad']} yükü %{$s['cpu']}\n";
echo <<<METIN
    Rapor: {$s['ad']}
    METIN;
```
:::

::: tahmin
PHP 8 ile (UTF-8 kaynak dosyası) çıktı:

```php
<?php
$s = "şehir";
echo strlen($s), " ", mb_strlen($s), "\n";
$y = "admin.php";
echo strpos($y, "admin") ? "bulundu" : "bulunamadı", "\n";
var_dump(strpos($y, "admin") !== false);
echo substr("pafta", 1, 3), " ", substr("pafta", -2), "\n";
printf("%05.1f|%-6s|%x\n", 3.14159, "ab", 255);
```

```gercek
6 5
bulunamadı
bool(true)
aft ta
003.1|ab    |ff
```

???

`6 5`: `ş` UTF-8'de 2 bayttır; `strlen` bayt, `mb_strlen` karakter sayar. `bulunamadı`: `strpos` 0 döndürür, 0 yanlışımsıdır. `bool(true)`: `!== false` doğru denetimdir. `aft ta`: substr baytlarla çalışır; ASCII metinde karakterle aynı. `003.1|ab    |ff`: 5 genişlik sıfırla doldurulmuş tek ondalık, 6 genişlik sola yaslı metin, onaltılık 255.
:::

::: gorev strlen ve mb_strlen
`strlen_php(s)` ve `mb_strlen_php(s)` fonksiyonlarını yaz: ilki metnin UTF-8 bayt sayısını, ikincisi karakter sayısını versin. Sonra aşağıdaki PHP doğrulamasını `kullanici_adi_gecerli(s)` olarak, **olduğu gibi** (bayt sayarak) çevir.

```php
function kullanici_adi_gecerli(string $s): bool {
    return strlen($s) >= 3 && strlen($s) <= 8;
}
```

```starter
def strlen_php(s):
    return len(s)


def mb_strlen_php(s):
    return len(s)


def kullanici_adi_gecerli(s):
    return 3 <= len(s) <= 8
```

```test
need("strlen_php")
need("mb_strlen_php")
need("kullanici_adi_gecerli")
eq((strlen_php("şehir"), mb_strlen_php("şehir")), (6, 5), "şehir")
eq((strlen_php("web01"), mb_strlen_php("web01")), (5, 5), "ASCII")
eq(kullanici_adi_gecerli("ali"), True, "3 bayt")
eq(kullanici_adi_gecerli("ğö"), True, "2 karakter ama 4 bayt: PHP kodu kabul eder")
eq(kullanici_adi_gecerli("çağrışım"), False, "8 karakter ama 13 bayt: PHP kodu reddeder")
```

```solution
def strlen_php(s):
    return len(s.encode("utf-8"))


def mb_strlen_php(s):
    return len(s)


def kullanici_adi_gecerli(s):
    return 3 <= strlen_php(s) <= 8
```

```hint
Python'da `len(metin)` karakter sayar (mb_strlen gibi). Bayt sayısı için `len(metin.encode("utf-8"))`.
```
:::

::: gorev strpos'u doğru denetle
Aşağıdaki iki PHP fonksiyonunu Python'a çevir. `strpos_php(samanlik, igne)` PHP'deki gibi konumu ya da `False` döndürsün; `hatali_denetim` ve `dogru_denetim` ise PHP kodlarının sonuçlarını versin.

```php
function hatali_denetim($yol) { return strpos($yol, "/admin") ? "engelle" : "izin"; }
function dogru_denetim($yol)  { return strpos($yol, "/admin") !== false ? "engelle" : "izin"; }
```

```starter
def strpos_php(samanlik, igne):
    return samanlik.find(igne)


def hatali_denetim(yol):
    return "engelle" if "/admin" in yol else "izin"


def dogru_denetim(yol):
    return "engelle" if "/admin" in yol else "izin"
```

```test
need("strpos_php")
need("hatali_denetim")
need("dogru_denetim")
eq(strpos_php("/admin/panel", "/admin"), 0, "başta: 0")
eq(strpos_php("/site/admin", "/admin"), 5, "ortada")
eq(strpos_php("/site", "/admin"), False, "yok: False")
eq(hatali_denetim("/admin/panel"), "izin", "PHP'deki hata: 0 yanlışımsı")
eq(hatali_denetim("/site/admin"), "engelle", "ortadaysa çalışıyor")
eq(dogru_denetim("/admin/panel"), "engelle", "doğru denetim")
eq(dogru_denetim("/site"), "izin", "yoksa izin")
```

```solution
def strpos_php(samanlik, igne):
    konum = samanlik.find(igne)
    return False if konum == -1 else konum


def hatali_denetim(yol):
    return "engelle" if strpos_php(yol, "/admin") else "izin"


def dogru_denetim(yol):
    return "engelle" if strpos_php(yol, "/admin") is not False else "izin"
```

```hint
Python'da `find` bulamazsa −1 döndürür; PHP'deki gibi `False` yap. Sonra hatalı sürümde dönüşü doğrudan koşul olarak kullan: 0 yanlışımsıdır.
```

```hint
`!== false` Python'da `is not False` olur: 0 da geçerli bir sonuç sayılır.
```
:::
