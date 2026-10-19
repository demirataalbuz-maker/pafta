# Pafta · Sertifika Karşılaştırması (2026-10-20)

Her yol, kendi alanındaki en üst düzey sertifikanın ya da resmi eğitimin **resmi konu listesiyle** karşılaştırıldı. Yüzdeler kabaca bir tahmindir: konu listesindeki maddelerin ne kadarının derslerde gerçekten anlatılıp görevle pekiştirildiğini gösterir.

## Kısa hüküm

| Yol | Ders | Karşılaştırılan | Kapsama | Hüküm |
|---|---|---|---|---|
| Python | 69 | PCAP + PCPP1 (Python Institute) | PCAP ~%90 · PCPP1 ~%50 | Çok güçlü, ama PCPP1'in iki bölümü hiç yok |
| Bash | 27 (artıyor) | LPIC-1, konu 103 + 105 | ~%80 | Güçlü; diğer oturum hâlâ yazıyor |
| SQL | 10 | Oracle 1Z0-071 | ~%70 | Sağlam; küme işleçleri ve görünümler eksik |
| Regex | 11 | Sertifikası yok; regular-expressions.info müfredatı | ~%80 | İyi; Unicode/Türkçe ve lehçe farkları eksik |
| KQL | 8 | SC-200 · "KQL ile sorgu" öğrenme yolu (4 modül) | ~%50 | Temel var, Sentinel'de her gün kullanılanlar yok |
| SPL | 7 | Splunk Core Power User + Advanced Power User | ~%20 | **En büyük açık** |
| PowerShell | 13 | AZ-040 (Microsoft resmi eğitimi) | ~%35 | İnce; yönetimin yarısı yok |
| JavaScript (okuma) | 5 | JSA (JS Institute) | ~%30 | Okuma hedefi için yeterli başlangıç; sınıf ve prototip yok |
| C (okuma) | 5 | CLA (C++ Institute) | ~%45 | Önişlemci, dosyalar, çok dosyalı programlar yok |
| PHP (okuma) | 4 | Zend Certified PHP Engineer | ~%25 | Nesne yönelimi, oturumlar ve hatalar yok |

**Bir uyarı:** `%LOCALAPPDATA%\Pafta\progress.json` dosyası hiç oluşmamış, yani henüz hiçbir adım tamamlanmamış. 153 ders hazır. İçerik eksikleri gerçek, ama şu an önündeki en büyük engel içerik değil, başlamak.

## Yol yol eksikler

### Python · PCAP ve PCPP1

PCAP'ın neredeyse tamamı var. Nesne yönelimi, dekoratörler, istisnalar ve kopyalama PCPP1 düzeyinde, hatta Python'un içi (descriptor, metasınıf, bytecode) PCPP1'in ötesinde. Eksikler PCPP1'in şu bölümlerinde:

| PCPP1 bölümü | Ağırlık | Durum | Eksik |
|---|---|---|---|
| 1 · İleri OOP | %35 | ~%85 | `pickle` ve `shelve` ile serileştirme (1.11), yerleşik türlerden türetmek (1.8: `dict`/`list` alt sınıfı, `UserDict`, `__missing__`) |
| 2 · Kod standartları | %12 | **yok** | PEP 8, PEP 20, PEP 257, docstring biçimleri, linter |
| 3 · GUI (tkinter) | %20 | **yok** | Bilerek dışarıda bırakılabilir: hedefe katkısı düşük, tezgahta pencere açmak da sorunlu |
| 4 · Ağ | %18 | ~%60 | XML (`xml.etree.ElementTree`), REST'te PUT/DELETE ile tam CRUD |
| 5 · Dosya ve ortam | %15 | ~%50 | `configparser` ile .ini, değer ara-değerlendirmesi (interpolation), logging'de özel handler ve formatter |

PCAP'ta küçük boşluklar: `platform` ve `random` modülleri, `bytearray`, `errno`.

**Önerilen dersler:** P70 Kod Standartları (PEP 8/20/257) · P71 pickle, shelve ve güvenli serileştirme · P72 XML ve INI dosyaları · P73 Yerleşik türleri genişletmek

### Bash · LPIC-1 (103 ve 105)

Komut satırı, filtreler, find/xargs, borular, süreçler, regex, sed/awk, betik yazma, getopts ve tar ile yedekleme var. Kalan küçük boşluklar:

- 105.1: kabuk başlangıç dosyaları (`/etc/profile`, `~/.bash_profile`, `~/.bashrc` sırası), `alias`
- 103.2: `md5sum`/`sha256sum`, `od`, `nl`, `split`
- 103.3: `gzip`/`bzip2`/`xz` ailesi, `dd`, `cpio`
- 103.6: `nice`/`renice`
- 103.7: temel (BRE) ile genişletilmiş (ERE) regex farkının açıkça anlatılması
- 103.8: vi (tezgahta etkileşimli editör çalışmaz; ancak bir okuma dersi olabilir)

Bu yol şu an başka bir oturumda genişletildiği için bu listeyi o oturum bitince kontrol etmek gerekir.

### SQL · Oracle 1Z0-071

SELECT, WHERE, sıralama, fonksiyonlar, CASE, GROUP BY, JOIN, alt sorgu ve CTE, NULL mantığı, DDL/DML ve işlemler var. Pencere fonksiyonları sınavın da ötesinde. Eksikler:

- Küme işleçleri: `UNION`, `INTERSECT`, `EXCEPT` (Oracle'da `MINUS`); sütun eşleşmesi ve sıralama kuralları
- Görünümler (`CREATE VIEW`)
- Veri sözlüğü: SQLite'ta `sqlite_master` ve `PRAGMA table_info` (Oracle'ın `USER_TABLES` karşılığı)
- `CROSS JOIN`, `FULL OUTER JOIN`
- Tür dönüşüm fonksiyonları (`CAST`) ve tarih fonksiyonlarının derli toplu anlatımı

Oracle'a özgü konular (sequence, synonym, `GRANT`/`REVOKE`) SQLite'ta çalışmadığı için kavram notu olarak geçilebilir.

**Önerilen dersler:** SQ11 Küme işleçleri ve görünümler · SQ12 Veritabanının kendini anlatması (sözlük, PRAGMA, dönüşümler)

### Regex

Sertifikası yok; ölçüt regular-expressions.info'nun müfredatı. Temelden bakınma ve atomik gruplara kadar var. Eksikler:

- Unicode: Python'da `\w`'nin varsayılan olarak Unicode olması, `re.ASCII`, Türkçe İ/ı büyük-küçük harf tuzağı
- Koşullu desenler `(?(1)...|...)`, değiştirmede `\g<ad>` ve fonksiyonla değiştirme
- Lehçe farkları: grep/sed'in BRE/ERE'si, PCRE, JavaScript ve .NET'te neyin çalışıp neyin çalışmadığı

**Önerilen dersler:** RX12 Unicode ve Türkçe · RX13 Değiştirme ustalığı ve koşullu desenler · RX14 Regex lehçeleri

### KQL · SC-200 öğrenme yolu

Microsoft'un resmi yolu dört modül: KQL ifadeleri kurmak, sonuçları özetlemek, çok tablolu sorgular, veriyle çalışmak. Pafta'da `where`, `project`, `extend`, `summarize`, `sort`/`top`, `join` ve zaman var. Eksikler:

- `let` (değişken, tablo ve fonksiyon tanımı), `search`
- `union`
- `parse` işleci
- Dinamik veri: `parse_json`, `mv-expand`, `bag_unpack`. Sentinel tablolarında çok sık geçer.
- `arg_max`/`arg_min`, `make_set`/`make_list`
- `datatable` ile satır içi veri
- `render` (görselleştirme; tezgahta grafik yok, kavram olarak anlatılabilir)

Bunlar için `sandbox/kql.py` çeviricisinin genişlemesi gerekiyor: `let`, `union`, `parse`, `mv-expand` (SQLite'ın `json_each`'i ile), `arg_max`, `make_set`, `datatable`.

**Önerilen dersler:** KQ09 let ve union · KQ10 parse ve metinden alan · KQ11 Dinamik veri ve JSON · KQ12 arg_max ve kümeler · KQ13 Proje

### SPL · Splunk Power User ve Advanced Power User

En büyük açık burada. Pafta'da arama, eval/where, stats, sort/top/dedup, rex, bin, join ve alt arama var. Sınav konularından sorgu diliyle ilgili olanların çoğu yok:

| Sınav maddesi | Eksik |
|---|---|
| PU 1.0 Görselleştirme komutları | `chart`, `timechart` |
| PU 2.3 | `fillnull` |
| PU 3.0 Olayları ilişkilendirmek (%15) | `transaction`; ne zaman `transaction`, ne zaman `stats` |
| APU 1.0 İstatistik | `eventstats`, `streamstats`, `appendpipe` |
| APU 2.6 | `makeresults` |
| APU 3.0 Lookup | `lookup`, `inputlookup`, `outputlookup` |
| APU 12.0 | `xyseries`, `untable`, `foreach` |
| APU 13.0 Çok değerli alanlar (%7) | `makemv`, `mvexpand`, `mvcount`, `mvindex`, `split` |
| APU 16.6 | `append` |
| APU 6.0 | `spath` |

Splunk arayüzünde yapılan işler (makrolar, etiketler, olay türleri, alan takma adları, veri modelleri, CIM, panolar) tezgahta çalışmaz. Kavram dersi olarak anlatılabilir; makrolar sorgu içinde açılarak taklit edilebilir.

Bunlar için `sandbox/spl.py` çeviricisinin genişlemesi gerekiyor.

**Önerilen dersler:** SP08 chart, timechart ve fillnull · SP09 eventstats ve streamstats · SP10 transaction ve stats ile ilişkilendirme · SP11 lookup ve inputlookup · SP12 Çok değerli alanlar · SP13 append, makeresults, xyseries · SP14 Bilgi nesneleri (kavram) · SP15 Proje

### PowerShell · AZ-040

AZ-040, Microsoft'un "PowerShell ile yönetimi otomatikleştirmek" eğitimi (sınavı yok, ama resmi müfredat). Pafta'da temeller, parametreler, koleksiyonlar, boru hattı, fonksiyonlar, nesneler, CSV/JSON, hata yönetimi ve olay günlükleri var. Eksikler:

- Yardım ve keşif: `Get-Help`, `Get-Command`
- Sağlayıcılar ve sürücüler: `Env:`, `Variable:`, `Function:`, kayıt defteri (salt okuma)
- Gelişmiş fonksiyonlar: `[CmdletBinding()]`, `-Verbose`, `-WhatIf`/`ShouldProcess`, splatting, scriptblock
- Metin ve regex: `-replace`, `Select-String`, `[regex]`, here-string
- Modüller: `.psm1`, `Import-Module`, `Export-ModuleMember`; yürütme ilkesi ve betik imzalama (kavram)
- İşler: `Start-Job`, `Receive-Job`, `Wait-Job`; zamanlanmış işler (kavram)
- CIM/WMI: `Get-CimInstance` ile yerel sistem bilgisi
- PowerShell 5 sınıfları ve `enum`
- Uzaktan yönetim: `Invoke-Command`, oturumlar (tezgahta WinRM yok; okuma dersi)

**Önerilen dersler:** PS14 Yardım, keşif ve sağlayıcılar · PS15 Gelişmiş fonksiyonlar · PS16 Metin ve regex · PS17 Modüller ve betik güvenliği · PS18 İşler ve CIM · PS19 Sınıflar ve enum · PS20 Uzaktan yönetimi okumak · PS21 Proje

### Okuma yolları · JavaScript, C, PHP

Bu üç yol bilerek okuma düzeyinde. Sertifikaların yazma düzeyini hedeflemiyor. Ama okumak için de gereken bazı konular eksik:

- **JavaScript (JSA):** sınıflar, prototip zinciri ve `this`; yerleşik nesneler (`Map`, `Set`, `Date`, `RegExp`); `try`/`catch`; modüller (`import`/`export`, `require`) ve bir npm projesini okumak (`package.json`)
- **C (CLA):** önişlemci (`#define` makroları, `#ifdef`), dosyalar (`fopen`, `fgets`, `fprintf`), çok dosyalı programlar (başlık dosyası, `extern`, `static`), karmaşık bildirimler, tamsayı taşması ve tür yükseltme
- **PHP (ZCPE):** türlü fonksiyonlar, closure ve ok fonksiyonu; sınıflar, arayüzler, trait ve namespace; oturumlar ve çerezler; istisnalar ve hata yönetimi

**Önerilen dersler:** JS06–JS08 · C06–C08 · PH05–PH07 (her yola üçer ders)

## Sertifika düzeyindeki bir programda olup Pafta'da olmayanlar

1. **Deneme sınavı:** Sertifikalar süreli, çoktan seçmeli ve senaryo sorularıyla ölçer. Pafta'da tahmin ve görev var, ama süreli bir "sınav kipi" yok.
2. **Kazanım eşlemesi:** Her dersin hangi sınav maddesini karşıladığı yazmıyor. Derslere `kazanim: PCAP 3.2` gibi bir alan eklenip haritada sertifika kapsamı gösterilebilir.
3. **Arayüzde yapılan işler:** Splunk panoları, Sentinel çalışma kitapları, tkinter gibi konular tezgahta çalışamaz. Bunlar için kavram dersleri ve gerçek ortamda yapılacak alıştırma listeleri gerekir.

## Düzeltme sırası

1. **SPL:** en büyük açık; SOC işlerinde Splunk sertifikası değerli
2. **KQL:** Sentinel'de her gün kullanılan işleçler
3. **PowerShell:** Windows yönetiminin eksik yarısı
4. **Python:** PCPP1'in kod standartları, serileştirme, XML/INI bölümleri
5. **SQL ve Regex:** ikişer-üçer ders
6. **Okuma yolları:** üçer ders
7. **Bash:** diğer oturum bitince kalan küçük boşluklar

## Kaynaklar

- [PCPP1 sınav konuları](https://pythoninstitute.org/pcpp1-exam-syllabus) · [PCAP sınav konuları](https://pythoninstitute.org/pcap-exam-syllabus) · [PCPP2](https://pythoninstitute.org/pcpp2) (konu listesi henüz yayımlanmadı)
- [LPIC-1 v5.0 hedefleri](https://wiki.lpi.org/wiki/LPIC-1_Objectives_V5.0)
- [Splunk Core Certified Power User sınav planı](https://www.splunk.com/en_us/pdfs/training/splunk-test-blueprint-power-user.pdf) · [Advanced Power User sınav planı](https://www.splunk.com/en_us/pdfs/training/splunk-test-blueprint-advanced-power-user.pdf)
- [Microsoft Learn · KQL ile Sentinel sorguları (SC-200)](https://learn.microsoft.com/en-us/training/paths/sc-200-utilize-kql-for-azure-sentinel/)
- [AZ-040 eğitim içeriği](https://www.fastlaneus.com/course/microsoft-az-040t00)
- [Oracle 1Z0-071 konu özeti](https://www.examcert.app/blog/oracle-1z0-071-syllabus-2026/) (Oracle'ın resmi sayfası doğrudan okunamadı)
- [JSA sınavı](https://www.credly.com/org/openedg/badge/jsa-41-01-jsa-certified-associate-javascript-programmer) · [CLA sınavı](https://cppinstitute.org/cla) · [Zend PHP sınavı](https://www.zend.com/training/php-certification-exam)
