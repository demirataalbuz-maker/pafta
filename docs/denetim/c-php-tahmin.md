# C ve PHP tahmin cevaplarının araçla doğrulanması

Kapsam: `tracks/c/lessons/*.md` (13 ders) ve `tracks/php/lessons/*.md` (11 ders), toplam **24 ders, 26 tahmin adımı** (c10 ve ph06'da ikişer tahmin var). Adımlar `engine/lessons.py` içindeki `parse_lesson` ile ayrıştırıldı; her adımın `code` alanı derlenip/çalıştırıldı, stdout `gercek` alanıyla **bayt bayt** karşılaştırıldı. Ders dosyalarına ve DENETIM.md'ye dokunulmadı.

## Toplam

| Sonuç | Ders | Adım | Dersler |
|---|---|---|---|
| aynı | 21 | 23 | c01–c11, ph01, ph03–ph11 |
| farklı | 1 | 1 | ph02 (yalnızca satır sonu boşluğu) |
| platforma bağlı | 1 | 1 | c12 (Windows hedefinde doğrulandı: aynı) |
| tanımsız davranış | 1 | 1 | c13 (ölçülen çıktı aynı) |
| platforma bağlı, doğrulanamadı | 0 | 0 | — |

Kısaca: 26 adımın 25'inde `gercek` birebir doğru. Tek bayt farkı ph02'de; Pafta'nın tahmin karşılaştırması (`engine/sinav.py` `normalize`, satır sonu boşluklarını kırpar) bu farkı yok saydığı için öğrencinin puanını etkilemiyor.

## Araçlar

| Araç | Sürüm | Kullanım |
|---|---|---|
| gcc (Linux x86-64) | gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0 | `-std=c11 -O0 -Wall -Wextra`; `-O2 -Wstrict-aliasing=1`; `-O1 -fsanitize=undefined,address -fno-sanitize-recover=undefined` |
| x86_64-w64-mingw32-gcc | 13-win32 (Ubuntu `gcc-mingw-w64-x86-64`) | Windows x64 (LLP64) hedefi: `-std=c11 -O0`, `-std=c11 -O2` ve `-std` vermeden (msvcrt printf yolu) |
| wine | wine-9.0 (Ubuntu 9.0~repack-4build3) | mingw çıktılarını çalıştırmak için (`WINEDEBUG=-all`, CRLF → LF çevrilerek karşılaştırıldı) |
| PHP | PHP 8.3.6 (cli) (NTS) | `php -n -d error_reporting=-1 -d display_errors=stderr` (php.ini yok, bütün uyarılar açık; json ve mbstring derleme içi) |

Her C adımı beş yapılandırmada (gcc -O0, gcc -O2, gcc+UBSan/ASan, mingw -O0, mingw -O2) ve ek olarak `-std`'siz mingw ile çalıştırıldı. Hiçbir çalıştırmada UBSan/ASan raporu, PHP'de uyarı/notice yok. MSVC ortamda yok; mingw-w64 aynı Windows x64 ABI'sini (LLP64, aynı yapı yerleşimi, 2 baytlık `wchar_t`) kullandığı için Windows ölçümü olarak o alındı.

## C sürücüleri

Tahmin kodlarının çoğu tam program değil. Eklenen en küçük sürücü:

- **Genel kalıp** (c02–c08, c10 adım 2, c11, c12): başa `#include <stdio.h>`, `<string.h>`, `<stdint.h>`, `<wchar.h>`; parça olduğu gibi `int main(void) { ... return 0; }` içine.
- **c01, c10 adım 4**: sürücü yok. c01 tam program; c10'un üç dosyası (`sayac.h`, `sayac.c`, `main.c`) koddaki `// dosya` başlıklarından ayrılıp `gcc main.c sayac.c` ile derlendi.
- **c09**: başlıklar; üç fonksiyon (`topla`, `carp`, `fark`) dosya düzeyinde, kalan satırlar `main` içinde.
- **c11**: genel kalıp; çalışma dizinine `liste.txt` = `"web01\nweb02\n"` (LF, dersin verdiği içerik). Windows'ta (wine) CRLF'li dosyayla da denendi: metin kipi `\r\n`'yi `\n`'ye çevirdiği için çıktı yine aynı.
- **c13**: başlıklar; dersin anlat adımındaki `#pragma pack(push, 1)` + `Baslik` typedef'i + `#pragma pack(pop)`; parça `main` içinde.

## Ders ders sonuç

| Ders | Sonuç | Not |
|---|---|---|
| c01 | aynı | Tam program; 6 yapılandırmada da `3 1 / 3.50 / Cb / ff`. |
| c02 | aynı | `-Wimplicit-fallthrough` uyarısı (dersin konusu, beklenen). `üç`/`diğer` UTF-8 bayt olarak aynı yazılıyor; Windows konsolunda doğru görünmesi kod sayfasına bağlı (`chcp 65001`), bayt çıktısı değişmiyor. |
| c03 | aynı | |
| c04 | aynı | |
| c05 | aynı | |
| c06 | aynı | `-Wsign-compare` uyarısı (dersin konusu). `(signed char)0xF0` tanımsız değil **uygulama tanımlı** (C11 6.3.1.3p3); gcc, mingw ve MSVC −16 verir. İşaretsiz taşma (`x - 1`, `uint8_t c = 300`) tanımlıdır. |
| c07 | aynı | Dolgu ve bayt sırası uygulama tanımlı; ders "x86-64, Windows ya da Linux" dediği gibi ikisinde de `8 12 8 / 44`. Union üzerinden okuma C'de tanımlı. |
| c08 | aynı | |
| c09 | aynı | |
| c10 | aynı | Adım 2 (makrolar) `5 9 / 10`; adım 4 (üç dosya) `3 36 100`. İkisi de aynı. |
| c11 | aynı | LF ve (Windows'ta) CRLF dosyada aynı. |
| c12 | platforma bağlı | Windows'a özgü: `sizeof(L"Pafta")`. mingw+wine (Windows x64): `5 5 / 6 12` = `gercek`, **doğrulandı**. Linux gcc: `5 5 / 6 24`; ders metni bu farkı zaten açıklıyor. |
| c13 | tanımsız davranış | `uint8_t veri[12]` dizisi `(const Baslik *)` ile okunuyor: katı takma ad kuralını çiğniyor (C11 6.5p7), tanımsız davranış. `pack(1)` olduğu için hizalama sorunu yok. Ölçülen çıktı 6 yapılandırmanın hepsinde `1 2 12` = `gercek`; ders de NOT kutusunda bu dönüşümün tartışmalı olduğunu söylüyor. |
| ph01 | aynı | PHP 8 öncelik kuralı (`+` önce) doğrulandı: `33`. |
| ph02 | farklı | Yalnızca 1. satır sonundaki boşluk. Açıklama "(sonunda bir boşluk)" diyor ama `gercek` çitinde boşluk yok. Pafta karşılaştırması satır sonu boşluğunu kırptığı için puanlamayı etkilemiyor. Aşağıda yan yana. |
| ph03 | aynı | |
| ph04 | aynı | mbstring gerekiyor. Windows PHP'de `php_mbstring` php.ini'den açılmazsa `mb_strlen` ölümcül hata verir (ortam notu, cevabı etkilemez). |
| ph05 | aynı | |
| ph06 | aynı | Adım 2 (yapıcıda özellik tanımlama, `static` dönüş türü) ve adım 4 (trait/namespace) ikisi de aynı. |
| ph07 | aynı | 8.1'deki `htmlspecialchars` varsayılan bayrak değişikliği yalnızca `'` karakterini etkiler; girdide `'` yok, 8.0'da da sonuç aynı olurdu. |
| ph08 | aynı | |
| ph09 | aynı | `password_hash` rastgele tuz kullanır, ama `password_verify("yanlis", …)` her çalıştırmada `false`. |
| ph10 | aynı | |
| ph11 | aynı | |

## Farklı çıkanlar

### ph02 · tahmin adımı 1

Görünmeyen boşluk `␠` ile gösterildi.

| Satır | Beklenen (`gercek`) | Gerçek (PHP 8.3.6) |
|---|---|---|
| 1 | `web01 db01` | `web01 db01␠` |
| 2 | `3 181` | `3 181` |
| 3 | `web01,db01,web03` | `web01,db01,web03` |
| 4 | `bool(false)` | `bool(false)` |
| 5 | `bool(false)` | `bool(false)` |

Sebep: döngü her sunucudan sonra `"$ad "` yazıyor, boşluk son elemandan sonra da basılıyor. Bayt bayt fark var ama anlamca fark yok. Düzeltme yerel denetçinin kararı: ya `gercek`'in 1. satırına sondaki boşluk eklenir (açıklamayla tutarlı olur), ya da normalize zaten kırptığı için olduğu gibi bırakılır.

## Platform ve sürüm notları

- **Windows'a özgü varsayım** yalnızca c12'de var (`wchar_t` 2 bayt). Windows x64 hedefiyle ölçüldü, sonuç doğru. c07'deki yapı dolgusu ve bayt sırası Windows x64 ve Linux x86-64'te aynı. `long` boyutuna dayanan bir tahmin yok.
- **MSVC'ye özgü** bir şey kullanılmıyor: `#pragma pack(push, 1)` MSVC'de de var, `%zu` VS2015'ten beri destekleniyor. MSVC'nin kendisiyle ölçüm yapılamadı.
- **PHP sürümü**: yalnızca 8.3.6 ölçüldü. Sürüme duyarlı noktalar (ph01'deki `+`/`.` önceliği, ph03'teki sayı-metin karşılaştırması, ph06'daki `static` dönüş türü ve yapıcıda özellik tanımlama, ph07'deki `htmlspecialchars` bayrakları) PHP 8.0'dan beri aynı davranıyor. PHP 7'de ph03'ün 2. satırı `bool(true)` olurdu, ph06 sözdizimi hatası verirdi; ph01 ise 33'e başka sırayla (`("32") + 1`) ulaşırdı. Dersler açıkça PHP 8 diyor.
- **Tanımsız davranış**: yalnızca c13 (katı takma ad). UBSan bu tür ihlali yakalamaz; karar standarda göre verildi. Başlatılmamış okuma, işaretli taşma ya da sınır dışı erişim hiçbir tahminde yok (ASan/UBSan temiz).
