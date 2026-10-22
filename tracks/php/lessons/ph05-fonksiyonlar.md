---
id: ph05
title: Fonksiyonlar ve Kapsam
summary: PHP fonksiyonlarının kendi kapsamı (dışarıdaki değişkeni görmemesi), global ve static, başvuruyla geçirme (&), tür bildirimleri ve strict_types, varsayılan ve adlandırılmış argümanlar, closure'larda use ile ok fonksiyonlarının değeri yakalaması.
kazanim: ZCPE 2.1, ZCPE 2.2, ZCPE 2.3, ZCPE 2.4
---

::: anlat Her fonksiyon kendi dünyasıdır
PHP'de bir fonksiyon, dışarıda tanımlanmış değişkenleri **görmez**. Python'dan ve JavaScript'ten farklı olarak üst kapsama otomatik erişim yoktur:

```php
<?php
$x = 10;
function f() {
    return isset($x) ? "var" : "yok";   // "yok": $x burada tanımsız
}
function g() {
    global $x;                          // açıkça istenirse dışarıdaki $x
    return $x;
}
```

| Yapı | Anlamı |
|---|---|
| `global $x;` | fonksiyon içinde dışarıdaki `$x`'i kullan (eski kodda yaygın; okunmasını zorlaştırır) |
| `static $n = 0;` | çağrılar arasında değerini koruyan yerel değişken |
| `function f(&$x)` | **başvuruyla** geçirme: fonksiyon çağıranın değişkenini değiştirir |
| `function f(int $x): string` | tür bildirimleri |
| `function f($a, $b = 2)` | varsayılan değer |
| `f(b: 5, a: 1)` | adlandırılmış argümanlar (PHP 8) |

### Tür bildirimleri ve strict_types
PHP varsayılan olarak tür bildirimlerini **zorlamaz, dönüştürür**: `int` bekleyen bir fonksiyona `"5"` verilirse 5'e çevrilir. Dosyanın en başına `declare(strict_types=1);` yazılırsa dönüşüm yapılmaz, yanlış tür `TypeError` verir. Modern PHP kodlarının çoğu bu satırla başlar; okurken dosyanın tepesine bak.

```php
<?php
declare(strict_types=1);
function kare(int $n): int { return $n * $n; }
echo kare(4);        // 16
// kare("4");        // TypeError: strict_types açık
```
:::

::: anlat Closure'lar: use ve fn
İsimsiz fonksiyonlar da dış değişkenleri kendiliğinden görmez; hangi değişkeni istediklerini `use` ile söylerler. `use` değişkenin **o anki değerini** kopyalar; başvuru isteniyorsa `use (&$x)` yazılır:

```php
<?php
$carpan = 3;
$f1 = function ($v) use ($carpan) { return $v * $carpan; };   // 3 kopyalandı
$f2 = fn($v) => $v * $carpan;                                 // ok fonksiyonu: dış değişkenleri kendiliğinden, değer olarak yakalar
$carpan = 5;
echo $f1(2), " ", $f2(2);    // 6 6: ikisi de tanımlandıkları andaki 3'ü kullanır
```

| Yazım | Dış değişken |
|---|---|
| `function () use ($x) { }` | `$x`'in **tanım anındaki** kopyası |
| `function () use (&$x) { }` | `$x`'in kendisi: sonraki değişiklikler görünür |
| `fn() => $x` | PHP 7.4+: kullanılan bütün dış değişkenler, tanım anındaki değerleriyle |

> [!NOT]
> `array_map`, `array_filter` ve `usort` gibi fonksiyonlara verilen closure'larda bu kurallar sürekli karşına çıkar. `use` satırını unutmak PHP'de "Undefined variable" uyarısına ve `null` ile çalışan sessiz bir hataya yol açar.
:::

::: tahmin
PHP 8 ile çıktı:

```php
<?php
$x = 10;
function f() { return isset($x) ? "var" : "yok"; }
echo f(), "\n";

function arttir(&$n) { $n++; }
$a = 1;
arttir($a);
echo $a, "\n";

function sayac() { static $s = 0; return ++$s; }
sayac();
sayac();
echo sayac(), "\n";

$carpan = 3;
$f1 = function ($v) use ($carpan) { return $v * $carpan; };
$f2 = fn($v) => $v * $carpan;
$carpan = 5;
echo $f1(2), " ", $f2(2), "\n";
```

```gercek
yok
2
3
6 6
```

???

`yok`, `2`, `3`, `6 6`. Fonksiyon dışarıdaki `$x`'i görmez. `&$n` başvuruyla geçtiği için `$a` 2 olur. `static $s` çağrılar arasında korunur; üçüncü çağrı 3 döndürür. `use` ve ok fonksiyonu `$carpan`'ı tanımlandıkları anda (3) yakalar; sonradan 5 yapmak onları etkilemez.
:::

::: gorev Başvuruyla toplama
Aşağıdaki PHP fonksiyonu bir sayaç dizisini **başvuruyla** alıp günceller ve hiçbir şey döndürmez. Python'da `say(sayaclar, anahtar)` olarak yaz: sözlüğü yerinde değiştirsin, olmayan anahtarı 1'den başlatsın ve `None` döndürsün.

```php
function say(array &$sayaclar, string $anahtar): void {
    $sayaclar[$anahtar] = ($sayaclar[$anahtar] ?? 0) + 1;
}
```

```starter
def say(sayaclar, anahtar):
    yeni = dict(sayaclar)
    yeni[anahtar] = yeni.get(anahtar, 0) + 1
    return yeni
```

```test
need("say")
s = {}
for k in ["web01", "db01", "web01"]:
    r = say(s, k)
eq(s, {"web01": 2, "db01": 1}, "sözlük yerinde değişmeli")
eq(r, None, "void: hiçbir şey döndürmez")
```

```solution
def say(sayaclar, anahtar):
    sayaclar[anahtar] = sayaclar.get(anahtar, 0) + 1
```

```hint
`&$sayaclar` çağıranın dizisinin kendisidir. Python'da gelen sözlüğü kopyalamadan değiştir; `$x ?? 0` için `sozluk.get(anahtar, 0)`.
```
:::

::: gorev Kopyalayan ve paylaşan closure
İki PHP closure'unun davranışını Python'da taklit et: `kopyalayan(baslangic)` ve `paylasan(kutu)`.

```php
$esik = 80;
$a = function ($cpu) use ($esik) { return $cpu > $esik; };     // kopya
$b = function ($cpu) use (&$esik) { return $cpu > $esik; };    // başvuru
$esik = 90;
// $a(85) → true (hâlâ 80'e bakıyor),  $b(85) → false (artık 90'a bakıyor)
```

`kopyalayan(esik)` bir fonksiyon döndürsün; dönen fonksiyon `cpu > esik` sonucunu, **oluşturulduğu andaki** eşikle versin. `paylasan(kutu)` ise `kutu` adlı sözlüğün `"esik"` anahtarına **her çağrıda** baksın.

```starter
def kopyalayan(esik):
    return lambda cpu: cpu > 0


def paylasan(kutu):
    esik = kutu["esik"]
    return lambda cpu: cpu > esik
```

```test
need("kopyalayan")
need("paylasan")
kutu = {"esik": 80}
a = kopyalayan(kutu["esik"])
b = paylasan(kutu)
kutu["esik"] = 90
eq(a(85), True, "kopya: hâlâ 80")
eq(b(85), False, "başvuru: artık 90")
eq(b(95), True, "başvuru: 95 > 90")
eq(a(80), False, "kopya: tam 80 eşiği aşmaz")
eq(b(90), False, "başvuru: tam 90 eşiği aşmaz")
```

```solution
def kopyalayan(esik):
    return lambda cpu: cpu > esik


def paylasan(kutu):
    return lambda cpu: cpu > kutu["esik"]
```

```hint
Kopya için eşiği fonksiyon oluşturulurken yakala. Paylaşım için değeri değil, **kutuyu** yakala ve her çağrıda `kutu["esik"]`'i oku.
```
:::
