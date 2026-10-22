---
id: ph09
title: Oturumlar, Çerezler ve Parolalar
summary: session_start ve $_SESSION, girişten sonra session_regenerate_id, çerez seçenekleri (Secure, HttpOnly, SameSite, Max-Age), password_hash ile password_verify, sayısal görünen özetlerde == tuzağı, hash_equals ve form belirteci (CSRF) denetimi.
kazanim: ZCPE 4.2, ZCPE 6.3, ZCPE 6.4
---

::: anlat Oturum: sunucunun hafızası
HTTP durumsuzdur: her istek birbirinden bağımsızdır. Bir kullanıcının giriş yapmış olduğunu hatırlamak için sunucu bir **oturum** açar, verisini kendinde tutar ve tarayıcıya yalnızca rastgele bir **oturum kimliği** çerezi verir:

```php
<?php
session_start();                                  // çerezdeki kimlikle oturumu bul ya da yeni aç
if (password_verify($_POST["parola"], $kayit["parola_ozeti"])) {
    session_regenerate_id(true);                  // girişte YENİ kimlik: eski kimlik geçersiz olur
    $_SESSION["kullanici_id"] = $kayit["id"];
}
// sonraki isteklerde:
$girisli = isset($_SESSION["kullanici_id"]);
```

| Satır | Neden |
|---|---|
| `session_regenerate_id(true)` | giriş öncesindeki kimliğin giriş sonrasında da geçerli kalmasını önler |
| `session_destroy()` + çerezi silmek | çıkış |
| oturum verisinde yalnızca kimlik | parolalar ve gizli bilgiler oturuma da yazılmaz |

### Çerez seçenekleri
```php
<?php
setcookie("tercih", "koyu", [
    "expires"  => time() + 30 * 86400,
    "path"     => "/",
    "secure"   => true,          // yalnızca HTTPS üzerinden gönderilir
    "httponly" => true,          // JavaScript (document.cookie) okuyamaz
    "samesite" => "Lax",         // başka sitelerden gelen isteklerde gönderilmez (üst düzey gezinme hariç)
]);
```

Bu bayrakların karşılığı, tarayıcıya giden `Set-Cookie` başlığındaki özniteliklerdir: `tercih=koyu; Max-Age=2592000; Path=/; Secure; HttpOnly; SameSite=Lax`. Bir uygulamanın yanıt başlıklarına bakarken oturum çerezinde `HttpOnly` ve `Secure` görmemek bir yapılandırma bulgusudur.
:::

::: anlat Parolalar ve karşılaştırma
Parolalar hiçbir zaman düz metin ya da hızlı bir özetle (MD5, SHA-1) saklanmaz. PHP'nin hazır fonksiyonları yavaş ve tuzlu bir özet üretir:

```php
<?php
$ozet = password_hash("Gizli-Parola-1", PASSWORD_DEFAULT);   // her çağrıda farklı çıktı: içinde rastgele tuz var
var_dump(password_verify("Gizli-Parola-1", $ozet));          // bool(true)
var_dump(password_verify("yanlis", $ozet));                  // bool(false)
if (password_needs_rehash($ozet, PASSWORD_DEFAULT)) { /* girişte yeniden özetle */ }
```

### == ile özet karşılaştırmak
Özetleri ya da belirteçleri `==` ile karşılaştırmak PHP'de iki ayrı sorun doğurur:

1. `"0e1234"` gibi "0e" ile başlayıp rakamla devam eden metinler **sayısal metin** sayılır (0 × 10¹²³⁴ = 0). İki farklı özet bu biçimdeyse `==` onları **eşit** bulur (PH03).
2. `==` ve `===` ilk farklı baytta durur; karşılaştırmanın süresi, eşleşen ön ekin uzunluğu hakkında bilgi sızdırır.

İkisinin de çözümü `hash_equals($beklenen, $gelen)`'dir: türü dönüştürmez ve her zaman aynı sürede karşılaştırır.

### Form belirteci (CSRF)
Bir form, kullanıcının oturumuna bağlı rastgele bir belirteç taşır; sunucu her POST'ta onu denetler. Böylece başka bir sitenin, kullanıcının tarayıcısı üzerinden habersiz istek göndermesi engellenir:

```php
<?php
$_SESSION["belirtec"] ??= bin2hex(random_bytes(32));        // formu çizerken
// POST geldiğinde:
$gelen = $_POST["belirtec"] ?? "";
if (!is_string($gelen) || !hash_equals($_SESSION["belirtec"], $gelen)) {
    http_response_code(403);
    exit("geçersiz istek");
}
```
:::

::: tahmin
PHP 8 ile çıktı:

```php
<?php
var_dump("0e1234" == "0e9999");
var_dump("0e1234" === "0e9999");
var_dump(hash_equals("abc", "abc"));
var_dump(password_verify("yanlis", password_hash("dogru", PASSWORD_DEFAULT)));
```

```gercek
bool(true)
bool(false)
bool(true)
bool(false)
```

???

`bool(true)`: iki metin de sayısal metindir ve sayı olarak ikisi de 0'dır. `bool(false)`: `===` metinleri olduğu gibi karşılaştırır. `bool(true)`: aynı metinler. `bool(false)`: yanlış parola, özetle doğrulanmaz.
:::

::: gorev Belirteci doğru denetle
`belirtec_gecerli(oturumdaki, gelen)` fonksiyonunu yaz: iki değer de boş olmayan **metin**se ve eşitse `True` döndürsün; karşılaştırmayı sabit süreli yap (`hmac.compare_digest`). Değerlerden biri `None`, boş ya da metin dışı bir türse `False`.

```starter
def belirtec_gecerli(oturumdaki, gelen):
    return oturumdaki == gelen
```

```test
need("belirtec_gecerli")
b = "9f2c" * 16
eq(belirtec_gecerli(b, b), True, "aynı belirteç")
eq(belirtec_gecerli(b, b[:-1] + "0"), False, "son karakter farklı")
eq(belirtec_gecerli(b, None), False, "belirteç gönderilmemiş")
eq(belirtec_gecerli(None, None), False, "oturumda belirteç yok: None == None doğru sayılmamalı")
eq(belirtec_gecerli("", ""), False, "boş belirteç")
eq(belirtec_gecerli(b, ["dizi"]), False, "metin dışı tür")
ok("compare_digest" in src, "hmac.compare_digest kullan")
```

```solution
import hmac


def belirtec_gecerli(oturumdaki, gelen):
    if not isinstance(oturumdaki, str) or not isinstance(gelen, str):
        return False
    if oturumdaki == "" or gelen == "":
        return False
    return hmac.compare_digest(oturumdaki, gelen)
```

```hint
Önce türleri denetle: ikisi de `str` ve boş değil. Başlangıç kodu `None == None` için `True` döndürüyor; oturumda belirteç yokken her istek geçerdi.
```

```hint
Sabit süreli karşılaştırma: `hmac.compare_digest(a, b)`: PHP'deki `hash_equals`'ın karşılığı.
```
:::

::: gorev Çerez başlığı
`cerez_basligi(ad, deger, saniye, guvenli=True, yalnizca_http=True, samesite="Lax")` fonksiyonunu yaz: `Set-Cookie` başlığının değerini şu sırayla kursun: `ad=deger; Max-Age=saniye; Path=/`, ardından `guvenli` ise `; Secure`, `yalnizca_http` ise `; HttpOnly`, `samesite` boş değilse `; SameSite=...`.

```starter
def cerez_basligi(ad, deger, saniye, guvenli=True, yalnizca_http=True, samesite="Lax"):
    return f"{ad}={deger}"
```

```test
need("cerez_basligi")
eq(cerez_basligi("oturum", "a1b2", 3600), "oturum=a1b2; Max-Age=3600; Path=/; Secure; HttpOnly; SameSite=Lax", "varsayılanlar")
eq(cerez_basligi("tercih", "koyu", 86400, yalnizca_http=False), "tercih=koyu; Max-Age=86400; Path=/; Secure; SameSite=Lax", "JS okuyabilir")
eq(cerez_basligi("x", "1", 60, guvenli=False, yalnizca_http=False, samesite=""), "x=1; Max-Age=60; Path=/", "özniteliksiz")
eq(cerez_basligi("oturum", "z", 600, samesite="Strict"), "oturum=z; Max-Age=600; Path=/; Secure; HttpOnly; SameSite=Strict", "Strict")
```

```solution
def cerez_basligi(ad, deger, saniye, guvenli=True, yalnizca_http=True, samesite="Lax"):
    parcalar = [f"{ad}={deger}", f"Max-Age={saniye}", "Path=/"]
    if guvenli:
        parcalar.append("Secure")
    if yalnizca_http:
        parcalar.append("HttpOnly")
    if samesite:
        parcalar.append(f"SameSite={samesite}")
    return "; ".join(parcalar)
```

```hint
Parçaları bir listeye koy ve `"; ".join(...)` ile birleştir; isteğe bağlı öznitelikleri koşullu ekle.
```
:::
