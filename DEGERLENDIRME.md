# Pafta · Sertifika Karşılaştırması (2026-10-20)

> [!NOT]
> 20 Ekim gecesi ders kimlikleri haritadaki sırayla yeniden numaralandı. Bu belgedeki kimlikler **eski** numaralardır (ör. P70–P73 bugün P50, P53, P30 ve P43; SP19 bugün SP17). Eşleme: [tools/numara_eslemesi.json](tools/numara_eslemesi.json).

Her yol, kendi alanındaki en üst düzey sertifikanın ya da resmi eğitimin **resmi konu listesiyle** karşılaştırıldı. Yüzdeler kabaca bir tahmindir: konu listesindeki maddelerin ne kadarının derslerde gerçekten anlatılıp görevle pekiştirildiğini gösterir.

## Denetim · 20 Ekim akşamı

Sabahki değerlendirmeden sonra yollar 142 dersten **227 derse** çıktı. Python dışındaki bütün yollar 6 rütbeye genişletildi. Bu bölüm o işin bağımsız denetimidir.

### Kalite kontrolleri

| Kontrol | Sonuç |
|---|---|
| `tools/validate.py`: her görevin çözümü geçiyor, başlangıç kodu geçmiyor, örnekler hatasız çalışıyor | 227 ders, 2206 kontrol, **temiz** |
| Tahmin açıklamaları: kod çalıştırıldı, çıktının her satırı açıklamada geçiyor mu? (9 çalıştırılabilir yol) | 284 tahminin **hepsi** uyuşuyor |
| Görevlerdeki "beklenen çıktı" blokları: örnek çözüm gerçekten bu çıktıyı veriyor mu? | 78 bloğun **hepsi** doğru (4 işaretin dördü de yanlış alarm: ikisi bilerek `...` ile kısaltılmış, ikisi fonksiyon dönüş değeri) |
| SPL dersleri Splunk belgeleriyle (transaction, chart, timechart) | Tutarlı: transaction sonuçları en yeniden eskiye, yarım işlemler atılıyor, `duration` saniye, `limit=10` ve `OTHER` varsayılanları doğru |
| Uygulama (önizleme) | Açılıyor, konsolda hata yok; SPL'in çok değerli alanları Splunk'taki gibi hücrede alt alta |

### Güncel kapsama

| Yol | Ders | Karşılaştırılan | Sabah | Şimdi | Kalan eksik |
|---|---|---|---|---|---|
| Python | 73 | PCAP + PCPP1 | PCAP ~%90 · PCPP1 ~%50 | PCAP ~%90 · PCPP1 ~%80 | P70–P73 eklendi (kod standartları, pickle/shelve, XML ve INI, yerleşik türlerden türetmek). Kalan: GUI (tkinter, bilerek dışarıda), REST'te tam CRUD, logging'de özel handler |
| Bash | 27 | LPIC-1 (103 + 105) | ~%80 | ~%85 | başlangıç dosyaları ve `alias`, `sha256sum`/`md5sum`, `nice`/`renice`, BRE–ERE farkı, vi |
| SQL | 17 | Oracle 1Z0-071 | ~%70 | ~%80 | görünümler (`CREATE VIEW`), veri sözlüğü (`sqlite_master`, `PRAGMA`) |
| Regex | 22 | regular-expressions.info müfredatı | ~%80 | ~%95 | — |
| KQL | 20 | SC-200 KQL yolu | ~%50 | ~%90 | `render` (görselleştirme; kavram olarak) |
| SPL | 19 | Splunk Power User / Advanced Power User | ~%20 | ~%70 / ~%55 | SP19 eklendi: makrolar (argümanlı), olay türleri, etiketler, alan takma adları, hesaplanan alanlar, arama zamanı sırası, CIM, veri modelleri ve tstats; ilk beşi tezgahta gerçekten çalışıyor. Kalan: iş akışı eylemleri ve panolar (yalnızca adıyla geçiyor), veri modeli kurmak ve hızlandırmak (arayüz işi). |
| PowerShell | 21 | AZ-040 + SOC Telemetrisi | ~%35 | ~%85 | `ps19`–`ps21` (Başpehlivan) eklendi: `Get-Help`/`Get-Command`, sağlayıcılar (`Variable:`, `Env:`, `HKLM:`), CIM (`Get-CimInstance` ve WQL), modüller (`New-Module`, `Export-ModuleMember`), `Invoke-Command -ScriptBlock`, Windows `Security` (4624/4625/4688/4698/4720) ve Sysmon (1/3/7/11/13/22) olay kimlikleri + XML `EventData` ayrıştırma. |
| JavaScript (okuma) | 12 | JSA | ~%30 | ~%65 | `Map`/`Set` ayrıntısı |
| C (okuma) | 13 | CLA | ~%45 | ~%75 | çok dosyalı programlar (`extern`, `static`, başlık dosyaları) |
| PHP (okuma) | 11 | Zend PHP | ~%25 | ~%60 | trait ve namespace ayrıntısı |
| Sigma | 18 | SigmaHQ Şartnamesi | %0 | ~%90 | `sg01`–`sg18`: resmi pySigma + yerel JSON olay motoru, değiştiriciler, filtreler, yaşam döngüsü, korelasyon ve iki proje |
| YARA | 18 | Resmî YARA Belgeleri | %0 | ~%90 | `yr01`–`yr18`: gerçek libyara, metin/hex/regex, konum/boyut, `pe`/`hash`/`math` modülleri ve iki proje |

### Düzeltilenler

- PowerShell yolunun açıklaması derslerde olmayan konuları ("dosya sistemi ve CIM, işler, modüller, Pester testleri") vaat ediyordu. Gerçek içeriğe göre düzeltildi.

### Öncelikli kalan işler

1. ~~**Python · PCPP1:** dört ders (P70–P73).~~ Yapıldı: P70 kod standartları, P71 pickle ve shelve, P72 XML ve INI, P73 yerleşik türleri genişletmek. Python yolu 73 ders.
2. ~~**SPL · bilgi nesneleri:**~~ Yapıldı: SP19. SPL çeviricisi makroları, olay türlerini, etiketleri, alan takma adlarını ve hesaplanan alanları veritabanındaki tanım tablolarından okuyup gerçekten uyguluyor; görevlerde makro açmak, etiketle ve olay türüyle aramak, CIM adlarına eşlemek ve bir tstats aramasının veri modeli karşılığını yazmak var.
3. ~~**PowerShell · AZ-040 ve SOC Telemetrisi:**~~ Yapıldı: `ps19`–`ps21` ile 6. rütbe (Başpehlivan) tamamlandı; PowerShell yolu 21 ders.

### En büyük eksik içerikte değil

`%LOCALAPPDATA%\Pafta\progress.json` hâlâ yok: henüz hiçbir ders adımı açılmadı. 227 ders, bir sertifikaya hazırlanmak için fazlasıyla yeterli. Bundan sonraki her ders, başlamanın yerini tutmaz. Önerilen başlangıç: hedef SOC/purple team olduğuna göre **SPL ve KQL** (Splunk Power User'ın sorgu kısmı artık tam), ardından Python.

## Sabahki değerlendirme

### Kısa hüküm

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

### Yol yol eksikler

#### Python · PCAP ve PCPP1

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

#### Bash · LPIC-1 (103 ve 105)

Komut satırı, filtreler, find/xargs, borular, süreçler, regex, sed/awk, betik yazma, getopts ve tar ile yedekleme var. Kalan küçük boşluklar:

- 105.1: kabuk başlangıç dosyaları (`/etc/profile`, `~/.bash_profile`, `~/.bashrc` sırası), `alias`
- 103.2: `md5sum`/`sha256sum`, `od`, `nl`, `split`
- 103.3: `gzip`/`bzip2`/`xz` ailesi, `dd`, `cpio`
- 103.6: `nice`/`renice`
- 103.7: temel (BRE) ile genişletilmiş (ERE) regex farkının açıkça anlatılması
- 103.8: vi (tezgahta etkileşimli editör çalışmaz; ancak bir okuma dersi olabilir)

Bu yol şu an başka bir oturumda genişletildiği için bu listeyi o oturum bitince kontrol etmek gerekir.

#### SQL · Oracle 1Z0-071

SELECT, WHERE, sıralama, fonksiyonlar, CASE, GROUP BY, JOIN, alt sorgu ve CTE, NULL mantığı, DDL/DML ve işlemler var. Pencere fonksiyonları sınavın da ötesinde. Eksikler:

- Küme işleçleri: `UNION`, `INTERSECT`, `EXCEPT` (Oracle'da `MINUS`); sütun eşleşmesi ve sıralama kuralları
- Görünümler (`CREATE VIEW`)
- Veri sözlüğü: SQLite'ta `sqlite_master` ve `PRAGMA table_info` (Oracle'ın `USER_TABLES` karşılığı)
- `CROSS JOIN`, `FULL OUTER JOIN`
- Tür dönüşüm fonksiyonları (`CAST`) ve tarih fonksiyonlarının derli toplu anlatımı

Oracle'a özgü konular (sequence, synonym, `GRANT`/`REVOKE`) SQLite'ta çalışmadığı için kavram notu olarak geçilebilir.

**Önerilen dersler:** SQ11 Küme işleçleri ve görünümler · SQ12 Veritabanının kendini anlatması (sözlük, PRAGMA, dönüşümler)

#### Regex

Sertifikası yok; ölçüt regular-expressions.info'nun müfredatı. Temelden bakınma ve atomik gruplara kadar var. Eksikler:

- Unicode: Python'da `\w`'nin varsayılan olarak Unicode olması, `re.ASCII`, Türkçe İ/ı büyük-küçük harf tuzağı
- Koşullu desenler `(?(1)...|...)`, değiştirmede `\g<ad>` ve fonksiyonla değiştirme
- Lehçe farkları: grep/sed'in BRE/ERE'si, PCRE, JavaScript ve .NET'te neyin çalışıp neyin çalışmadığı

**Önerilen dersler:** RX12 Unicode ve Türkçe · RX13 Değiştirme ustalığı ve koşullu desenler · RX14 Regex lehçeleri

#### KQL · SC-200 öğrenme yolu

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

#### SPL · Splunk Power User ve Advanced Power User

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

#### PowerShell · AZ-040

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

#### Okuma yolları · JavaScript, C, PHP

Bu üç yol bilerek okuma düzeyinde. Sertifikaların yazma düzeyini hedeflemiyor. Ama okumak için de gereken bazı konular eksik:

- **JavaScript (JSA):** sınıflar, prototip zinciri ve `this`; yerleşik nesneler (`Map`, `Set`, `Date`, `RegExp`); `try`/`catch`; modüller (`import`/`export`, `require`) ve bir npm projesini okumak (`package.json`)
- **C (CLA):** önişlemci (`#define` makroları, `#ifdef`), dosyalar (`fopen`, `fgets`, `fprintf`), çok dosyalı programlar (başlık dosyası, `extern`, `static`), karmaşık bildirimler, tamsayı taşması ve tür yükseltme
- **PHP (ZCPE):** türlü fonksiyonlar, closure ve ok fonksiyonu; sınıflar, arayüzler, trait ve namespace; oturumlar ve çerezler; istisnalar ve hata yönetimi

**Önerilen dersler:** JS06–JS08 · C06–C08 · PH05–PH07 (her yola üçer ders)

### Sertifika düzeyindeki bir programda olup Pafta'da olmayanlar

1. **Deneme sınavı:** Sertifikalar süreli, çoktan seçmeli ve senaryo sorularıyla ölçer. Pafta'da tahmin ve görev var, ama süreli bir "sınav kipi" yok.
2. **Kazanım eşlemesi:** Her dersin hangi sınav maddesini karşıladığı yazmıyor. Derslere `kazanim: PCAP 3.2` gibi bir alan eklenip haritada sertifika kapsamı gösterilebilir.
3. **Arayüzde yapılan işler:** Splunk panoları, Sentinel çalışma kitapları, tkinter gibi konular tezgahta çalışamaz. Bunlar için kavram dersleri ve gerçek ortamda yapılacak alıştırma listeleri gerekir.

### Düzeltme sırası

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
