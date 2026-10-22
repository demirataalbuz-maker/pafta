---
id: ph03
title: Gevşek Türler ve Karşılaştırma
summary: == ile ===, sayısal metinler, PHP 8'de değişen metin-sayı karşılaştırması, (int) ve intval, ctype_digit ile giriş doğrulama.
kazanim: ZCPE 1.1, ZCPE 3.1, ZCPE 6.5
---

::: anlat Gevşek karşılaştırma
PHP'de `==` karşılaştırmadan önce türleri dönüştürür, `===` ise tür ve değerin **ikisinin de** aynı olmasını ister. Kuralları bilmeden `==` okumak yanıltıcıdır:

| İfade | PHP 8 sonucu | Neden |
|---|---|---|
| `"10" == "1e1"` | true | iki taraf da sayısal metin: sayı olarak karşılaştırılır (10 = 10) |
| `100 == "1e2"` | true | sayı ile sayısal metin: sayı olarak |
| `"1" == "01"` | true | iki sayısal metin |
| `0 == "a"` | **false** | sayı ile sayısal olmayan metin: sayı metne çevrilir, "0" ≠ "a" (PHP 7'de true idi) |
| `null == false` | true | null, false sayılır |
| `"abc" == "ABC"` | false | metin karşılaştırması harfe duyarlı |
| `1 === "1"` | false | tür farklı |

> [!GÜVENLİK]
> Kimlik, belirteç ya da parola özeti gibi değerleri `==` ile karşılaştırmak tehlikelidir: sayısal görünen iki farklı metin "eşit" sayılabilir (`"1e3" == "1000"` true'dur). Güvenli kod `===` kullanır; gizli değerleri karşılaştırırken ayrıca süreden bilgi sızdırmayan `hash_equals()` kullanır.

### Sayıya çevirmek
`(int)` ve `intval()` metnin **başındaki** sayıyı alır, gerisini sessizce atar; hiç sayı yoksa 0 verir:

```php
<?php
var_dump((int)"12abc", intval("abc"), intval("  42"), intval("-7x"), intval("3.9"));
// int(12) int(0) int(42) int(-7) int(3)
```

Bu sessiz davranış yüzünden "12abc" gibi bozuk bir girdi 12 olarak kabul edilebilir. Doğrulama için önce metnin **yalnızca** rakamlardan oluştuğu denetlenir: `ctype_digit($s)` (yalnızca 0–9, boş metinde false).
:::

::: tahmin
PHP 8 ile çıktı:

```php
<?php
var_dump("10" == "1e1");
var_dump(0 == "a");
var_dump("1" == "01");
var_dump(100 == "1e2");
var_dump("abc" === "abc");
var_dump(null == false);
```

```gercek
bool(true)
bool(false)
bool(true)
bool(true)
bool(true)
bool(true)
```

???

İkinci satır `bool(false)`, diğer beşi `bool(true)`. Sayısal metinler sayı olarak karşılaştırılır (10 = 1e1, 1 = 01, 100 = 1e2). PHP 8'de sayı ile sayısal olmayan metin karşılaştırılırken sayı metne çevrilir: "0" ile "a" eşit değil. `null` gevşek karşılaştırmada `false`'a eşittir.
:::

::: gorev Yaş doğrulama
Aşağıdaki PHP doğrulama fonksiyonunu Python'a `gecerli_yas(s)` olarak çevir. `ctype_digit` yalnızca ASCII rakamları (0–9) kabul eder ve boş metinde false döner.

```php
function gecerli_yas($s) {
    return ctype_digit($s) && (int)$s >= 18 && (int)$s <= 120;
}
```

```starter
def gecerli_yas(s):
    return s.isdigit() and 18 <= int(s) <= 120
```

```test
need("gecerli_yas")
eq(gecerli_yas("25"), True, "25")
eq(gecerli_yas("17"), False, "17 küçük")
eq(gecerli_yas("120"), True, "120 sınır")
eq(gecerli_yas("0018"), True, "baştaki sıfırlar: ctype_digit kabul eder, 18")
eq(gecerli_yas(""), False, "boş metin")
eq(gecerli_yas("18.5"), False, "nokta rakam değil")
eq(gecerli_yas("+20"), False, "işaret rakam değil")
eq(gecerli_yas("٢٥"), False, "Arapça-Hint rakamları: Python isdigit true der, ctype_digit false")
```

```solution
def gecerli_yas(s):
    if s == "" or any(c not in "0123456789" for c in s):
        return False
    return 18 <= int(s) <= 120
```

```hint
Python'un `isdigit()` Unicode rakamları da kabul eder (٢٥, ²). `ctype_digit` yalnızca 0–9'u kabul eder: karakterleri `"0123456789"` içinde ara.
```
:::

::: gorev intval
PHP'nin `intval($s)` davranışını metinler için taklit eden `php_intval(s)` fonksiyonunu Python'da yaz: baştaki boşlukları (boşluk, sekme, satır sonu) atla, isteğe bağlı bir `+` ya da `-` ve ardından gelen rakamları al; rakam yoksa 0 döndür.

```starter
def php_intval(s):
    try:
        return int(s)
    except ValueError:
        return 0
```

```test
need("php_intval")
for metin, beklenen in [("12abc", 12), ("abc", 0), ("  42", 42), ("-7x", -7), ("+5", 5), ("3.9", 3),
                        ("\t\n 8 ", 8), ("", 0), ("-", 0), ("x12", 0)]:
    eq(php_intval(metin), beklenen, f"intval({metin!r})")
```

```solution
import re

def php_intval(s):
    m = re.match(r"[ \t\n\r\v\f]*([+-]?\d+)", s)
    return int(m.group(1)) if m else 0
```

```hint
Düzenli ifade: baştaki boşluklar `[ \t\n\r\v\f]*`, sonra `([+-]?\d+)`. `re.match` yalnızca metnin başında arar.
```
:::
