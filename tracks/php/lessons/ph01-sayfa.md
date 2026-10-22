---
id: ph01
title: Bir PHP Sayfasını Okumak
summary: <?php etiketi, echo, $ ile değişkenler, çift ve tek tırnak farkı, . ile birleştirme ve PHP 8'de değişen işleç önceliği.
kazanim: ZCPE 1.1
---

::: anlat PHP bir HTML üreticisidir
PHP, sunucuda çalışıp tarayıcıya giden sayfayı **üreten** bir dildir. Bir `.php` dosyasında `<?php ... ?>` arasındaki kısım çalışır, dışarıdaki HTML olduğu gibi gönderilir. Bu yolda PHP kodunu okuyacak, çıktısını tahmin edecek ve görevlerde aynı davranışı Python'da kuracaksın.

```php
<!doctype html>
<h1>Sunucu durumu</h1>
<?php
$ad = "web01";              // değişkenler $ ile başlar, tür bildirilmez
$cpu = 72;
echo "<p>$ad: %$cpu</p>\n"; // echo çıktıya yazar
?>
<p>Sayfanın sonu</p>
```

### Tırnaklar
| Yazım | Ne olur |
|---|---|
| `"Merhaba $ad\n"` | çift tırnak: değişkenler ve `\n` gibi kaçışlar **yorumlanır** |
| `'Merhaba $ad\n'` | tek tırnak: metin **harfi harfine** kalır |
| `"Toplam: {$s['adet']}"` | karmaşık ifadeler süslü parantez içinde |
| `$a . $b` | birleştirme `.` ile yapılır (`+` sayısal toplamadır) |

```php
<?php
$n = 3;
echo "adet: $n\n";       // adet: 3
echo 'adet: $n\n';       // adet: $n\n   (satır sonu da yok)
echo "a" . "b" . 1, "\n";  // ab1   echo virgülle birden çok değer alabilir
```

### Sayılar
`/` her zaman gerçek bölme yapar (`7 / 2` → `3.5`); tam sayı bölmesi için `intdiv(7, 2)` → `3`. Kalan `%` ile alınır.

> [!TUZAK]
> PHP 8 ile işleç önceliği değişti: artık `+` ve `-`, `.`'dan **önce** yapılır. `"Toplam: " . $a + $b` PHP 7'de önce birleştirip sonra toplamaya çalışırdı. PHP 8'de `"Toplam: " . ($a + $b)` olarak yorumlanır. Eski bir kod tabanını okurken hangi sürümde çalıştığını bilmek önemlidir; şüphede parantez beklenir.
:::

::: tahmin
Kod istek parametresi olmadan, PHP 8 ile çalıştırılıyor. Çıktı nedir?

```php
<?php
$ad = "Ece";
$n = 3;
echo "Merhaba $ad\n";
echo 'Merhaba $ad' . "\n";
echo $n . "2" + 1, "\n";
echo intdiv(7, 2), " ", 7 / 2, "\n";
```

```gercek
Merhaba Ece
Merhaba $ad
33
3 3.5
```

???

`Merhaba Ece`, `Merhaba $ad`, `33`, `3 3.5`. Çift tırnak `$ad`'ı yerine koyar, tek tırnak koymaz. PHP 8'de `+`, `.`'dan önce yapılır: `"2" + 1` sayısal toplama olarak 3 verir, sonra `$n` ile birleşip "33" olur. `intdiv` tam sayı bölmesi, `/` gerçek bölmedir.
:::

::: gorev Etiket fonksiyonu
Aşağıdaki PHP fonksiyonunu Python'a `etiket(ad, rol, cpu)` olarak çevir.

```php
function etiket($ad, $rol, $cpu) {
    return strtoupper($ad) . ' [' . $rol . "] %$cpu";
}
```

```starter
def etiket(ad, rol, cpu):
    return f"{ad} [{rol}] %{cpu}"
```

```test
need("etiket")
eq(etiket("web01", "web", 72), "WEB01 [web] %72", "web01, web, 72")
eq(etiket("db01", "veritabanı", 91), "DB01 [veritabanı] %91", "rol değişmeden kalır")
```

```solution
def etiket(ad, rol, cpu):
    return ad.upper() + " [" + rol + "] %" + str(cpu)
```

```hint
`strtoupper` Python'da `.upper()`. Çift tırnaklı kısım `$cpu`'yu yerine koyar.
```
:::

::: gorev Satır sayacı
Aşağıdaki PHP kodunun ürettiği metni döndüren `liste_html(adlar)` fonksiyonunu Python'da yaz.

```php
function liste_html($adlar) {
    $html = "<ul>";
    $i = 1;
    foreach ($adlar as $ad) {
        $html .= "<li>$i. $ad</li>";
        $i++;
    }
    return $html . '</ul>';
}
```

```starter
def liste_html(adlar):
    return "<ul>" + "".join(adlar) + "</ul>"
```

```test
need("liste_html")
eq(liste_html(["web01", "db01"]), "<ul><li>1. web01</li><li>2. db01</li></ul>", "iki eleman")
eq(liste_html([]), "<ul></ul>", "boş liste")
```

```solution
def liste_html(adlar):
    html = "<ul>"
    for i, ad in enumerate(adlar, 1):
        html += f"<li>{i}. {ad}</li>"
    return html + "</ul>"
```

```hint
`.=` sona eklemedir (Python'da `+=`). Sayaç 1'den başlıyor: `enumerate(adlar, 1)`.
```
:::
