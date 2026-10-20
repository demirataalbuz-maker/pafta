# Pafta

Ders ders öğreten, önce anlatıp sonra yazdıran yerel bir dil öğrenme uygulaması. Motor çok dilli; her dil bir **yol**:

| Yol | Pafta | Koşucu | Durum |
|---|---|---|---|
| **Python** | 69 (6 rütbe, Minik → Başpehlivan; sıfırdan CPython'un içine) | `python`: run, test, Röntgen (değişkenlerle adım adım), Bytecode | hazır |
| **Regex** | 22 (6 rütbe; Unicode, lehçeler, günlük biçimleri, iki proje) | `regex`: eşleşme tablosu, test, Ağaç (`re.DEBUG`) | hazır |
| **Bash** | 27 (6 rütbe; awk, sed, getopts, iki proje) | `bash`: Git Bash, test, Röntgen (`bash -x` izi) | hazır |
| **PowerShell** | 18 (Windows olay günlükleri, gelişmiş fonksiyonlar, sınıflar, XML) | `powershell`: Windows PowerShell 5.1, test, Röntgen (`Set-PSDebug -Trace 1`); her çalıştırmada `olaylar.json` hazır | hazır |
| **SQL** | 17 (6 rütbe; pencere çerçeveleri, boşluk-ada, oturumlar, özyineleme) | `sql`: bellek içi SQLite, sonuç tabloları, test, Plan (`EXPLAIN QUERY PLAN`) | hazır |
| **KQL** | 20 (6 rütbe; let, parse, dinamik veri, arg_max, sıralı satırlar, oturumlar, IP, iki proje) | `kql`: [sandbox/kql.py](sandbox/kql.py) KQL alt kümesini SQLite'a çevirir; SQL düğmesi karşılığı gösterir | hazır |
| **SPL** | 18 (6 rütbe; timechart, chart, eventstats/streamstats, lookup, transaction, append, iki proje) | `spl`: [sandbox/spl.py](sandbox/spl.py) Splunk arama dilinin alt kümesini SQLite'a çevirir | hazır |
| **JavaScript** (okuma) | 12 (6 rütbe; kapsam ve this, sınıflar, hatalar, Node sunucu kodu, küçültülmüş kod, proje) | `javascript`: Node.js | hazır |
| **C** (okuma) | 13 (6 rütbe; taşma, yapı düzeni, bayt tamponları, fonksiyon işaretçileri, önişlemci, dosya G/Ç, Windows API, ayrıştırıcı projesi) | `python`: C kodu okunur, tahminin cevabı derste sabit (`gercek` bloğu); görevlerde davranış Python'da kurulur | hazır |
| **PHP** (okuma) | 11 (6 rütbe; metinler ve baytlar, closure'lar, sınıflar, PDO, oturumlar ve parolalar, JSON ve hatalar, uç nokta projesi) | `python`: C ile aynı düzen, PHP 8 kuralları | hazır |
| Sigma, YARA | — | — | planlı (`status: planned`) |

SQL, KQL ve SPL yollarının bütün sorguları aynı örnek veritabanında çalışır: [tracks/sql/ornek.sql](tracks/sql/ornek.sql) (küçük bir şirketin BT operasyonu: ekipler, personel, sunucular, biletler, ölçümler). Her çalıştırmada bellekte sıfırdan kurulur. KQL ve SPL çevirileri gerçek Kusto ve Splunk'ın inceliklerine sadık kalır (KQL'de varsayılan `sort` yönü azalan, `join`'in varsayılanı `innerunique`; SPL'de aramada büyük-küçük harf duyarsızlığı, OR'un AND'den önce bağlanması, `!=` ile `NOT` farkı, `join`'in `max=1` davranışı), ama tam bir motor değildir: desteklenmeyen işleç anlaşılır bir hatayla reddedilir. KQL'de "şimdi" sabittir (2026-10-19 12:00), böylece `ago()` her gün aynı sonucu verir. KQL ve SPL yolları bu veritabanının üstüne günlük tablolarını yükler: [tracks/kql/veri.sql](tracks/kql/veri.sql) (`istekler`: web istek günlüğü, `ayrinti` sütunu JSON; `gunluk`: serbest metinli uygulama günlüğü; `dagitimlar`: sürüm dağıtımları); SPL bunlara Splunk'taki gibi bir `_time` alanı da ekler ([tracks/spl/veri.sql](tracks/spl/veri.sql)). SPL'de `eval` bölmesi her zaman ondalıklıdır ve `count(eval(...)) as ad`, `earliest`, `latest`, `stdev` desteklenir. Çevirici süre (`timespan`), bool ve dinamik türleri izler ve çıktıyı KQL biçiminde gösterir (`1.02:30:00`, `true`); `datetime_diff` gerçek Kusto gibi birim sınırlarını sayar; `prev`/`next`/`row_cumsum` serileştirilmemiş girdide hata verir.

## Çalıştırma

- **⚡ Programlar → Pafta** ya da Başlat menüsünde **Pafta**
- Elle: `pythonw Pafta.pyw` (Edge uygulama penceresi açılır; pencere kapanınca sunucu ~40 sn sonra kendini kapatır)
- Geliştirme: `python server.py --port 8765` (tarayıcıda `http://127.0.0.1:8765/`; `--veri KLASOR` ile ayrı bir ilerleme klasörü)

Gereksinim: Python 3.11+ (sadece standart kütüphane), Microsoft Edge (yoksa varsayılan tarayıcı açılır). Bash yolu için Git for Windows (`C:\Program Files\Git\bin\bash.exe`); PowerShell yolu Windows'la gelen PowerShell 5.1'i, JavaScript yolu Node.js'i kullanır. C ve PHP için derleyici gerekmez.

## Bir paftanın akışı

Her pafta adımlardan oluşur:

| Adım | Ne olur |
|---|---|
| **Anlat** | Kavram, ölçü notlu kod örnekleri (▶ Çalıştır, ⇢ Tezgaha al), Derin su / Tuzak / Güvenlik kutuları |
| **Tahmin** | Kodun çıktısını tahmin edersin, sonra gerçek çalıştırmayla karşılaştırılır |
| **Görev** | Kodu sen yazarsın, testler denetler; geçince "ONAYLANDI" mührü basılır |

Tezgah (sağ panel): editör, Çıktı, Kontrol, **Röntgen** ve dile göre bir görünüm (Python'da Bytecode, Regex'te Ağaç, SQL'de Plan, KQL ve SPL'de SQL karşılığı). Röntgen Python'da kodu adım adım yürütüp her satırda değişkenleri gösterir (aynı renk = aynı nesne); Bash ve PowerShell'de yorumlayıcının çalıştırdığı komutları sırasıyla, değişkenler yerine konmuş haliyle gösterir. Regex'te Röntgen yerine eşleşme tablosu, SQL'de her sorgunun sonuç tablosu vardır. Geçilen görevler **Tekrar** kutularına düşer (1, 3, 7, 16, 35 gün). **Serbest tezgah** sekiz dilde boş bir çalışma alanıdır (`#/tezgah/<dil>`: python, regex, bash, powershell, sql, kql, spl, javascript). Okuma yollarında (C, PHP) tezgah, görevlerdeki Python içindir.

Kısayollar: `Ctrl+Enter` çalıştır · `Ctrl+Shift+Enter` kontrol et · `Ctrl+/` yorum · `Tab`/`Shift+Tab` girinti · Röntgende `←` `→`

## Klasörler

```text
Pafta.pyw            başlatıcı (sunucu + Edge penceresi + tek örnek kontrolü)
server.py            yerel HTTP sunucusu (127.0.0.1, Host/Origin kontrolü, oturum belirteci)
engine/lessons.py    yol ve ders okuyucu (.md → adımlar)
engine/progress.py   ilerleme, seri, Leitner tekrar kutuları
engine/runners.py    dil koşucuları: python, regex, bash, powershell, sql, kql, spl, javascript
sandbox/py_harness.py  kullanıcı kodunu ayrı süreçte çalıştıran düzenek
                     (run/test/trace/dis · regex_run/regex_test/regex_dis · proc_run/proc_test/proc_trace
                      · sql_run/sql_test/sql_dis · kql_* ve spl_*: çevir, sonra SQL gibi koş)
sandbox/kql.py, spl.py  KQL ve SPL → SQLite çeviricileri (her | aşaması bir CTE)
web/                 arayüz (index.html, style.css, app.js, editor.js, md.js, hl.js)
tracks/<yol>/track.json   yolun modülleri, rütbeleri, koşucusu ve dili
tracks/<yol>/lessons/*.md dersler
tools/validate.py    bütün görevleri doğrular
tools/tahmin_denetle.py  Python tahmin açıklamalarındaki sayıları gerçek çıktıyla karşılaştırır
```

İlerleme `%LOCALAPPDATA%\Pafta\progress.json` dosyasındadır; proje klasörü taşınsa da kaybolmaz.

## Ders biçimi

```markdown
---
id: p70
title: Ders başlığı
summary: tek satırlık özet
---

::: anlat Adım başlığı
Markdown metin. Kod bloklarında `#!` ile ölçü notu: `x = 1  #! not`
> [!DERİN] / [!TUZAK] / [!GÜVENLİK] / [!NOT] / [!ZEN]
:::

::: tahmin
Soru metni
` ``python
print(2 ** 10)
` ``
???
Tahminden sonra gösterilecek açıklama
:::

::: gorev Görev başlığı
Görev metni
` ``starter  ` ``   başlangıç kodu
` ``stdin    ` ``   (isteğe bağlı) girdi
` ``setup    ` ``   (isteğe bağlı) görev klasörünü hazırlayan gizli kod
` ``test     ` ``   eq(), ok(), yakin(), raises(), run(), run_code(), need(), uses(), calls()
` ``solution ` ``   örnek çözüm
` ``hint     ` ``   ipucu (birden çok olabilir)
` ``meta     ` ``   timeout: 10
:::
```

### Dile göre farklar

| | Python | Regex | Bash / PowerShell | SQL |
|---|---|---|---|---|
| Kod bloğu | ` ``python ` | ` ``regex `: üstte desen, `---`, altta metin | ` ``bash ` / ` ``powershell ` | ` ``sql ` (hata veren örnek için ` ``sql norun `) |
| Girdi | `input()` | test metni (Girdi kutusu "Metin") | stdin; PowerShell'de `$Girdi` dizisi | yok; girdi örnek veritabanıdır |
| `test` yardımcıları | yukarıdakiler | `desen`, `eslesir()`, `tam()`, `bul()`, `grup()`, `gruplar()`, `adli()`, `hepsi()`, `degistir()`, `bol()` | `out`, `run(stdin, argv)`, `calis()` → `{kod, cikti, hata}`, `hata_cikti`, `src` | `sonuc` (son sorgunun satırları, tuple listesi), `sonuclar`, `sutunlar`, `sorgu(sql)` (betikten sonraki veritabanında), `dene(hazirlik)` (temiz veritabanına hazırlık ekleyip betiği yeniden koşar), `kullanir("group by")`, `out`, `src` |
| `meta` | `timeout`, `argv` | `timeout` | `timeout`, `argv: a "b c"` (kabuktaki gibi tırnaklı; tezgahtaki Çalıştır ve Röntgen de bu argümanlarla koşar) | `timeout` |
| `setup` | Python | — | Python (dosyaları `newline="\n"` ile yaz; CRLF Bash'te `\r` sorununa yol açar) | SQL (örnek veritabanından sonra çalışır) |

SQL çıktısı (`out`, tahmin karşılaştırması) sqlite3 kabuğunun liste biçimindedir: başlıksız, sütunlar `|` ile ayrık, boş değer `NULL`. Ders yazarken `cikti` bloklarını gerçek çıktıyla karşılaştırmak için çözümü tezgahta bir kez çalıştır.

**KQL ve SPL** dersleri SQL'in test yardımcılarını aynen kullanır (`sonuc`, `sutunlar`, `sorgu`, `dene`, `kullanir`); kod blokları ` ``kql ` ve ` ``spl `, boş değer çıktıda boş görünür. Boş satırla ayrılmış her sorgu ayrı bir sonuç tablosu verir.

**JavaScript** dersleri Bash/PowerShell gibi süreç olarak koşar (`out`, `run`, `calis`); girdi `require("fs").readFileSync(0, "utf8")` ile okunur.

**Okuma yolları (C, PHP)**: `track.json`'da `"runner": "python"`, `"dil": "python"` ve `"okuma_dili": "c"` (ya da `"php"`). Anlatım ve tahmin kodu ` ``c ` / ` ``php ` bloklarında yazılır ve çalıştırılmaz; tahmin adımına gerçek çıktı bir ` ``gercek ` bloğuyla elle verilir (ön yüze tahmin edilmeden gönderilmez). Görevler, okunan kodun davranışını Python'da kurdurur ve Python testleriyle denetlenir. `gercek` blokları doğrulayıcı tarafından çalıştırılamadığı için C/PHP davranışını iyi bildiğin örneklerle sınırlı tut ve Python karşılığıyla çapraz denetle.

Yeni ders ekleyince `track.json`'daki ilgili modülün `lessons` listesine id'yi ekle ve doğrula:

```bash
python tools/validate.py                      # bütün etkin yollar
python tools/validate.py --yol powershell     # tek yol
python tools/validate.py --yol bash bs04      # tek ders
```

Ders dosyalarını LF satır sonuyla kaydet (Python'dan yazarken `newline=""`).

Doğrulayıcı her görevde örnek çözümün **geçtiğini**, başlangıç kodunun **geçmediğini**, tahmin ve anlatım kodlarının hatasız çalıştığını kontrol eder.

## Yeni dil yolu eklemek

1. `tracks/<yol>/track.json` içinde `"status": "active"`, `"runner": "<ad>"`, `"dil"` (vurgulama ve kod blokları için), isteğe bağlı `"kahraman"` (harita başlığı) ve `"girdi_etiketi"`, modüller ve rütbeleri tanımla
2. `engine/runners.py`'de koşucuyu ekle. Komut satırı aracıyla çalışan diller için `ProcRunner` yeterli: `RUNNERS`'a komutu, dosya adını, iz modunu ve hata satırı desenini veren bir girdi yaz (bash ve powershell örnekleri orada). Koşucunun `ozellik` alanı (`{"roentgen": bool, "dis": "düğme adı" | None}`) arayüzde hangi düğmelerin görüneceğini belirler; desteklenmeyen görünüm için `trace`/`dis` `None` döndürür ve sunucu isteği reddeder
3. `web/hl.js`'ye bir sözdizimi vurgulayıcı ekle (`kural()` ile birkaç satır), `web/md.js`'deki `dilAdi`'ye takma adları ekle, `engine/lessons.py`'deki `KOD_DILLERI`'ne dili ekle
4. Dersleri `tracks/<yol>/lessons/` altına yaz ve `--yol` ile doğrula

## Güvenlik

Sunucu kod çalıştırdığı için üç kilit var: yalnızca `127.0.0.1`'e bağlanır, Host ve Origin başlıklarını denetler (DNS rebinding'e karşı), `/api/*` istekleri her açılışta üretilen gizli bir belirteç ister. Kod ayrı bir süreçte, `python -I` ile (Bash/PowerShell betikleri de bu düzeneğin açtığı alt süreçte), geçici bir klasörde ve zaman sınırıyla çalışır; süre dolunca süreç ağacı `taskkill /T` ile kapatılır. Bu bir **kum havuzu değildir**: yalnızca kendi yazdığın kodu çalıştır.
