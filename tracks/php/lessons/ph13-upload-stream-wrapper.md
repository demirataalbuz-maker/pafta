---
id: ph13
title: Yükleme ve Akış Sarmalayıcıları
summary: $_FILES'ın alanları ve hangilerinin istemciden geldiği; UPLOAD_ERR kodlarının sırası ve önce hata kodunun denetlenmesi; dosya adının son uzantısı, büyük/küçük harf ve uzantısı olmayan adlar; istemcinin bildirdiği MIME tipinin kanıt olmaması (ölçüldü: .jpg adlı PHP dosyası text/x-php); PHP'de bir "yol"un sarmalayıcı adresi olabilmesi — php://filter, data://, php://temp — ve allow_url_fopen ile allow_url_include farkı.
kazanim: ZCPE 6.5, ZCPE 4.1
---

::: anlat $_FILES: hangi alan kimden geliyor
Bir form dosya gönderdiğinde PHP yüklenen dosyayı geçici bir yere yazar ve `$_FILES` dizisini doldurur:

```php norun
$_FILES['belge'] = [
    'name'     => 'rapor.pdf',          // İSTEMCİNİN verdiği ad
    'type'     => 'application/pdf',    // İSTEMCİNİN verdiği MIME tipi
    'tmp_name' => '/tmp/phpA1B2C3',     // PHP'nin yazdığı geçici yol
    'error'    => 0,                    // PHP'nin koyduğu sonuç kodu
    'size'     => 10240,                // PHP'nin saydığı bayt
];
```

İlk iki alan **tarayıcıdan gelen metinlerdir**; isteyen istediğini yazabilir. Son üçü PHP'nin kendi ölçümüdür.

Önce `error` denetlenir, çünkü sıfır değilse `tmp_name` kullanılabilir bir dosya göstermez:

| Sabit | Değer | Anlamı |
|---|---|---|
| `UPLOAD_ERR_OK` | 0 | yükleme tamam |
| `UPLOAD_ERR_INI_SIZE` | 1 | `upload_max_filesize` aşıldı |
| `UPLOAD_ERR_FORM_SIZE` | 2 | formdaki `MAX_FILE_SIZE` aşıldı |
| `UPLOAD_ERR_PARTIAL` | 3 | dosya yarım geldi |
| `UPLOAD_ERR_NO_FILE` | 4 | dosya seçilmedi |
| `UPLOAD_ERR_NO_TMP_DIR` | 6 | geçici dizin yok |
| `UPLOAD_ERR_CANT_WRITE` | 7 | diske yazılamadı |
| `UPLOAD_ERR_EXTENSION` | 8 | bir PHP eklentisi durdurdu |

Beş yoktur; numaralar sıralı değildir, bu yüzden "5'ten küçükse tamamdır" gibi bir kısaltma yazma. Geçici dosyayı yerine taşırken `move_uploaded_file` kullanılır: `is_uploaded_file` ile aynı denetimi yapar, yani yalnız bu istekte yüklenmiş bir geçici dosyayı kabul eder; sıradan `rename`/`copy` bu güvenceyi vermez.
:::

::: anlat Ad, tip ve içerik üç ayrı şeydir; yol da dosya olmayabilir
Bir yüklemeyi kabul ederken üç farklı "bu nedir?" kaynağı vardır ve üçü de aynı şeyi söylemez. Bu derste ölçüldü: içinde PHP kodu olan bir dosyayı `sahte.jpg` adıyla kaydedip `mime_content_type` ile sorduğunda yanıt **`text/x-php`** gelir. Ad `.jpg` der, istemci `image/jpeg` demiş olabilir, içerik PHP'dir.

Uzantı okumak da göründüğü kadar basit değildir; `pathinfo(...)['extension']` **son** noktadan sonrasını verir ve harf büyüklüğünü korur:

| Ad | `extension` |
|---|---|
| `rapor.php.jpg` | `jpg` |
| `rapor.jpg.php` | `php` |
| `arsiv.tar.gz` | `gz` |
| `rapor.PHP` | `PHP` |
| `.gitignore` | `gitignore` |
| `rapor` | *(yok)* |

Karşılaştırmayı `strtolower` ile yap, uzantısı olmayan adı ayrıca ele al ve kararı **son** uzantıya göre ver.

İkinci konu: PHP'de dosya fonksiyonlarına verilen metin her zaman bir dosya yolu değildir. Metin bir **sarmalayıcı** adresi olabilir. Bu kurulumda kayıtlı olanlar ölçüldü: `https, ftps, compress.zlib, php, file, glob, data, http, ftp, phar`.

```php norun
file_get_contents("php://filter/read=convert.base64-encode/resource=gizli.txt");
// gizli.txt'in içeriğini base64'e çevirerek verir: "aWNlcmlr"
file_get_contents("data://text/plain;base64,cGFmdGE=");   // "pafta"
$h = fopen("php://temp", "r+");                            // bellekte geçici akış
```

> [!TUZAK] İki ayrı ayar, iki ayrı sınır
> `allow_url_fopen` açıkken (bu kurulumda **açık**) `file_get_contents`/`fopen` uzak ve sarmalayıcı adreslerini açabilir. `allow_url_include` ise ayrı bir ayardır ve burada **kapalıdır**: `include`/`require` uzak adres alamaz. Biri kapalı diye diğerinin de kapalı olduğunu varsayma. Asıl ders şudur: dışarıdan gelen bir metni dosya fonksiyonuna vermeden önce onun bir **yol** olduğunu doğrula; `php://filter` örneğinin gösterdiği gibi, "dosya okuma" sandığın çağrı içeriği dönüştürerek de okuyabilir.
:::

::: tahmin Ad ne diyor, içerik ne diyor?
```php
<?php
file_put_contents("sahte.jpg", "<?php echo 1; ?>");
var_dump(mime_content_type("sahte.jpg"));
foreach (['rapor.php.jpg','rapor.jpg.php','.gitignore','rapor.PHP'] as $f)
    echo $f, " -> ", pathinfo($f)['extension'] ?? '-', "\n";
echo UPLOAD_ERR_NO_FILE, " ", UPLOAD_ERR_CANT_WRITE, "\n";
```

```gercek
string(10) "text/x-php"
rapor.php.jpg -> jpg
rapor.jpg.php -> php
.gitignore -> gitignore
rapor.PHP -> PHP
4 7
```

???

`string(10) "text/x-php"`: ad `.jpg` ile bitiyor ama `mime_content_type` **içeriğe** bakar ve PHP görür. Üç kaynak (ad, istemcinin bildirdiği tip, içerik) birbirinden bağımsızdır; yalnız üçüncüsü dosyanın kendisinden gelir.

Uzantılar: `rapor.php.jpg` → `jpg`, `rapor.jpg.php` → `php` — **son** nokta belirler, baştaki aldatıcı parça değil. `.gitignore` → `gitignore`: nokta ile başlayan ad "uzantısız" sayılmaz, bütün gövde uzantı olur. `rapor.PHP` → `PHP`: harf büyüklüğü korunur, bu yüzden listeyle karşılaştırırken küçült.

`4 7`: `UPLOAD_ERR_NO_FILE` 4, `UPLOAD_ERR_CANT_WRITE` 7'dir; arada 5 yoktur.
:::

::: gorev Yüklemeyi kabul et
`kabul(dosya, izinli, azami)` yaz: bir `$_FILES` girdisini denetleyip sonucu döndür.

`dosya` sözlüğünde `error`, `name`, `size` ve `type` anahtarları vardır. Denetim sırası:

1. `error` sıfır değilse `"hata:<kod>"` döndür.
2. `size` `azami`'yi aşıyorsa `"buyuk"` döndür.
3. Adın **son** uzantısı (küçük harfe çevrilmiş) `izinli` listesinde değilse ya da adın hiç uzantısı yoksa `"uzanti"` döndür.
4. Hepsi geçerse `"tamam"`.

`type` istemciden gelir; karara katma.

```starter
def kabul(dosya, izinli, azami):
    if dosya["type"] not in ("image/jpeg", "image/png"):
        return "uzanti"
    if dosya["size"] > azami:
        return "buyuk"
    return "tamam"
```

```test
need("kabul")
JPG = {"error": 0, "name": "rapor.jpg", "size": 10, "type": "image/jpeg"}
eq(kabul(JPG, ["jpg", "png"], 100), "tamam", "geçerli yükleme")
eq(kabul({**JPG, "error": 4}, ["jpg"], 100), "hata:4", "dosya seçilmemiş")
eq(kabul({**JPG, "error": 1, "size": 99999}, ["jpg"], 100), "hata:1",
   "hata kodu boyuttan önce denetlenir")
eq(kabul({**JPG, "size": 200}, ["jpg"], 100), "buyuk", "boyut sınırı")
eq(kabul({**JPG, "size": 100}, ["jpg"], 100), "tamam", "sınıra eşit boyut geçer")
eq(kabul({**JPG, "name": "rapor.jpg.php"}, ["jpg"], 100), "uzanti", "son uzantı belirler")
eq(kabul({**JPG, "name": "rapor.php.jpg"}, ["jpg"], 100), "tamam", "baştaki parça uzantı değildir")
eq(kabul({**JPG, "name": "rapor.JPG"}, ["jpg"], 100), "tamam", "harf büyüklüğü önemsiz")
eq(kabul({**JPG, "name": "rapor"}, ["jpg"], 100), "uzanti", "uzantısı olmayan ad")
eq(kabul({**JPG, "name": "kabuk.php", "type": "image/jpeg"}, ["jpg"], 100), "uzanti",
   "istemcinin bildirdiği tip karara katılmaz")
eq(kabul({**JPG, "name": "rapor.png", "type": "text/x-php"}, ["jpg", "png"], 100), "tamam",
   "istemci tipi yanlış olsa da uzantı izinliyse geçer")
```

```solution
def kabul(dosya, izinli, azami):
    if dosya["error"] != 0:
        return f"hata:{dosya['error']}"
    if dosya["size"] > azami:
        return "buyuk"
    ad = dosya["name"]
    if "." not in ad:
        return "uzanti"
    if ad.rsplit(".", 1)[1].lower() not in izinli:
        return "uzanti"
    return "tamam"
```

```hint
Başlangıç kodu istemcinin `type` alanına güveniyor ve `error`'a hiç bakmıyor. Sırayı şartnamedeki gibi kur: `error`, sonra `size`, sonra uzantı.
```

```hint
Son uzantı için `ad.rsplit(".", 1)` kullan ve `.lower()` ile karşılaştır. Hiç nokta yoksa uzantı yoktur; `.gitignore` gibi adlarda ise nokta vardır ve gövdenin tamamı uzantı sayılır.
```
:::

::: gorev Bu bir yol mu, sarmalayıcı mı?
`hedef_turu(yol)` yaz: bir dosya fonksiyonuna verilen metnin sıradan bir yol mu yoksa bir sarmalayıcı adresi mi olduğunu söyle.

- Metin `<şema>://` ile başlıyorsa şemayı (küçük harfe çevirmeden, olduğu gibi) döndür.
- Şema bir harfle başlar; sonrasında harf, rakam, `+`, `-` ve `.` bulunabilir. Bu kurala uymayan bir önek şema sayılmaz.
- Başka her şey için `"dosya"` döndür.

```starter
def hedef_turu(yol):
    if "://" in yol:
        return yol.split("://")[0]
    return "dosya"
```

```test
import re
need("hedef_turu")
eq(hedef_turu("php://filter/read=convert.base64-encode/resource=gizli.txt"), "php", "php sarmalayıcısı")
eq(hedef_turu("data://text/plain;base64,cGFmdGE="), "data", "data sarmalayıcısı")
eq(hedef_turu("https://ornek.test/x"), "https", "uzak adres")
eq(hedef_turu("compress.zlib://arsiv.gz"), "compress.zlib", "şema nokta içerebilir")
eq(hedef_turu("/var/www/rapor.txt"), "dosya", "mutlak yol")
eq(hedef_turu("rapor.txt"), "dosya", "göreli yol")
eq(hedef_turu("alt/dizin/rapor.txt"), "dosya", "eğik çizgi şema yapmaz")
eq(hedef_turu("C:\\veri\\rapor.txt"), "dosya", "iki nokta tek başına şema değildir")
eq(hedef_turu("/yuklemeler/data://x"), "dosya", "şema yalnız metnin başındaysa geçerlidir")
eq(hedef_turu("://x"), "dosya", "şema boş olamaz")
eq(hedef_turu("1php://x"), "dosya", "şema rakamla başlayamaz")
eq(hedef_turu("a_b://x"), "dosya", "alt çizgi şemada geçerli değil")
eq(hedef_turu(""), "dosya", "boş metin")
```

```solution
import re

def hedef_turu(yol):
    eslesme = re.match(r"([A-Za-z][A-Za-z0-9+.-]*)://", yol)
    return eslesme.group(1) if eslesme else "dosya"
```

```hint
Başlangıç kodu `"://"` geçen her metni sarmalayıcı sayıyor; `a_b://x` ya da `://x` de öyle görünür. Şemayı bir düzenli ifadeyle baştan eşleştir: harfle başlamalı ve yalnız harf, rakam, `+`, `-`, `.` içermeli.
```
:::
