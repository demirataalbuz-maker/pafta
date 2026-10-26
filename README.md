# Pafta

Ders ders öğreten, önce anlatıp sonra yazdıran yerel bir dil öğrenme uygulaması. Motor çok dilli; her dil bir **yol**:

| Yol | Pafta | Koşucu | Durum |
|---|---|---|---|
| **Python** | 73 (6 rütbe, Minik → Başpehlivan; sıfırdan CPython'un içine; PCAP ve PCPP1'in GUI dışındaki konuları) | `python`: run, test, Röntgen (değişkenlerle adım adım), Bytecode | hazır |
| **Regex** | 22 (6 rütbe; Unicode, lehçeler, günlük biçimleri, iki proje) | `regex`: eşleşme tablosu, test, Ağaç (`re.DEBUG`) | hazır |
| **Bash** | 28 (6 rütbe; awk, sed, getopts, iki proje, kabuk ortamı: başlangıç dosyaları, alias, sha256sum, nice) | `bash`: Git Bash, test, Röntgen (`bash -x` izi) | hazır |
| **PowerShell** | 21 (6 rütbe; Windows olay günlükleri, gelişmiş fonksiyonlar, sınıflar, XML, sağlayıcılar, CIM, modüller, Security ve Sysmon telemetrisi) | `powershell`: Windows PowerShell 5.1, test, Röntgen (`Set-PSDebug -Trace 1`); her çalıştırmada `olaylar.json` hazır | hazır |
| **HTTP ve HTML** | 24 (6 rütbe; HTTP net, HTML okuma; HT17–HT24 Burp, TLS, gerçek tarayıcı CORS/SameSite, CSRF, nesne yetkisi, yönlendirme, WebSocket ve GraphQL) | `http`: Python; eski Bilet Masası korunur. Ek derslerde gerçek HTTP/TLS, kurulu Edge/Chromium ve graphql-core; [kurulum, sınırlar ve elle Burp kabulü](docs/http-lab.md) | hazır |
| **SQL** | 18 (6 rütbe; pencere çerçeveleri, boşluk-ada, oturumlar, özyineleme, görünümler ve veri sözlüğü) | `sql`: bellek içi SQLite, sonuç tabloları, test, Plan (`EXPLAIN QUERY PLAN`) | hazır |
| **KQL (Kusto)** | 20 (6 rütbe; let, parse, dinamik veri, arg_max, sıralı satırlar, oturumlar, IP, render, iki proje) | `kql`: [sandbox/kql.py](sandbox/kql.py) KQL alt kümesini SQLite'a çevirir; SQL düğmesi karşılığı gösterir | hazır |
| **SPL** | 19 (6 rütbe; timechart, chart, eventstats/streamstats, lookup, transaction, append, bilgi nesneleri ve CIM, iki proje) | `spl`: [sandbox/spl.py](sandbox/spl.py) Splunk arama dilinin alt kümesini SQLite'a çevirir | hazır |
| **JavaScript** (okuma) | 12 (6 rütbe; Map ve Set, kapsam ve this, sınıflar, hatalar, Node sunucu kodu, küçültülmüş kod, proje) | `javascript`: Node.js | hazır |
| **C** (okuma) | 13 (6 rütbe; taşma, yapı düzeni, bayt tamponları, fonksiyon işaretçileri, önişlemci ve çok dosyalı programlar, dosya G/Ç, Windows API, ayrıştırıcı projesi) | `python`: C kodu okunur, tahminin cevabı derste sabit (`gercek` bloğu); görevlerde davranış Python'da kurulur | hazır |
| **PHP** (okuma) | 11 (6 rütbe; metinler ve baytlar, closure'lar, sınıflar, namespace ve trait'ler, PDO, oturumlar ve parolalar, JSON ve hatalar, uç nokta projesi) | `python`: C ile aynı düzen, PHP 8 kuralları | hazır |
| **Java** (okuma) | 12 (6 rütbe; ilkel türler ve taşma, String havuzu ve equals, koleksiyonlar ve kutulama, Optional, record ve JavaBeans, Stream, istisnalar, Path ve dizin aşımı, Servlet filtreleri ve Spring, JDBC, yansıma/JSON/XML, denetleyici projesi) | `python`: C ile aynı düzen, Java 21 kuralları | hazır |
| **C# (.NET)** (okuma) | 12 (6 rütbe; değer/referans türleri ve checked, string == ve Substring(başlangıç, uzunluk), null güvenliği ?/??, Dictionary ve TryGetValue, özellikler ve record, LINQ ve ertelenmiş çalıştırma, Path.Combine tuzağı, async/await, ASP.NET Core ara katmanı ve denetleyiciler, EF Core FromSqlInterpolated/FromSqlRaw, DI/IConfiguration/System.Text.Json, Web API projesi) | `python`: C ile aynı düzen, .NET 8 / C# 12 kuralları | hazır |
| **Assembly (x86/x64)** (okuma) | 12 (6 rütbe; 64/32/16/8-bit yazmaç dilimleri ve mov, aritmetik/bit/lea, little-endian bellek ve movzx/movsx, RFLAGS ve cmp/test, işaretsiz ja/jb ile işaretli jg/jl dallanmaları ve cmovcc, yığın/push-pop ve prolog/epilog, Windows x64 ve System V ABI çağrı kuralları, diziler/dizgiler/struct hizalaması, C kontrol kalıpları, yığın kanaryası ve jo taşma denetimi, objdump/RIP-göreli adresleme ve rol/ror, ikili paket doğrulayıcı projesi) | `python`: C ile aynı düzen, x86-64 Intel sözdizimi kuralları | hazır |
| **Sigma** | 18 (6 rütbe; seçimler, modifier'lar, veri kalitesi, yanlış pozitifler, dağıtım/korelasyon okuma ve iki proje) | `sigma`: resmi pySigma ayrıştırıcısı + JSON olaylarında yerel test backend'i | hazır |
| **YARA** | 24 (6 rütbe; metin/hex, regex, sayım/konum, PE import/export ve bölümler, ELF/.NET metadata, hash/math ve iki proje) | `yara`: gerçek yara-python/libyara; bellek içindeki örnek baytları tarar | hazır |
| **Elastic / Kibana** | 27 (6 rütbe; KQL/Lucene/EQL, gerçek ingest/ECS, Security kuralları ve ES\|QL) | `elastic`: temel dersler Lucene/yerel EQL; EL20–EL27 gerçek Elasticsearch/Kibana 9.5.5 Basic API | hazır |
| **CMD / Batch** | 24 (6 rütbe; parametreler, değişken açılımı, for/for /f, dosya ve metin akışı, EVTX, yapılandırma, token ve DACL sorguları) | `cmd`: gerçek Windows cmd.exe; run/test, UTF-8 girdi/çıktı | hazır |
| **Wireshark / tcpdump** | 29 (6 rütbe; filtreler, PCAPNG, TLS/HTTP2/QUIC, TCP iş akışı, SMB2/Kerberos/LDAP, CLI raporu ve kontrollü yakalama) | `packets`: gerçek TShark 4.6.8 + libpcap 1.10.6; PK29 için Kali WSL tcpdump loopback laboratuvarı | hazır |
| **Active Directory ve LDAP** | 25 (6 rütbe; LDAP/Get-AD*, ACL ve erişim yolu, S4U, AD CS, TLS/imzalama/CBT) | `ad`: AD01–AD12 yerel filtre motoru, AD13–AD14/AD16–AD17/AD19–AD20 çevrimdışı kanıt analizi; AD15/AD18/AD21–AD23 Pafta içinden gerçek Windows Server AD/KDC/CA | hazır |

SQL, KQL ve SPL yollarının bütün sorguları aynı örnek veritabanında çalışır: [tracks/sql/ornek.sql](tracks/sql/ornek.sql) (küçük bir şirketin BT operasyonu: ekipler, personel, sunucular, biletler, ölçümler). Her çalıştırmada bellekte sıfırdan kurulur. KQL ve SPL çevirileri gerçek Kusto ve Splunk'ın inceliklerine sadık kalır (KQL'de varsayılan `sort` yönü azalan, `join`'in varsayılanı `innerunique`; SPL'de aramada büyük-küçük harf duyarsızlığı, OR'un AND'den önce bağlanması, `!=` ile `NOT` farkı, `join`'in `max=1` davranışı), ama tam bir motor değildir: desteklenmeyen işleç anlaşılır bir hatayla reddedilir. KQL'de "şimdi" sabittir (2026-10-19 12:00), böylece `ago()` her gün aynı sonucu verir. KQL ve SPL yolları bu veritabanının üstüne günlük tablolarını yükler: [tracks/kql/veri.sql](tracks/kql/veri.sql) (`istekler`: web istek günlüğü, `ayrinti` sütunu JSON; `gunluk`: serbest metinli uygulama günlüğü; `dagitimlar`: sürüm dağıtımları); SPL bunlara Splunk'taki gibi bir `_time` alanı da ekler ([tracks/spl/veri.sql](tracks/spl/veri.sql)). SPL'de `eval` bölmesi her zaman ondalıklıdır ve `count(eval(...)) as ad`, `earliest`, `latest`, `stdev` desteklenir. Splunk'ın bilgi nesneleri de [tracks/spl/veri.sql](tracks/spl/veri.sql)'deki tablolardan okunur: makrolar (ters tırnakla çağrılır, ayrıştırmadan önce metin olarak açılır), olay türleri (`eventtype=`), etiketler (`tag=`, `tag::alan=`), alan takma adları ve hesaplanan alanlar (her `sourcetype=` aramasında kendiliğinden, Splunk'ın arama zamanı sırasıyla). Son ikisi varsayılan olarak boştur; dersler kendi hazırlık bloklarında doldurur. Çevirici süre (`timespan`), bool ve dinamik türleri izler ve çıktıyı KQL biçiminde gösterir (`1.02:30:00`, `true`); `datetime_diff` gerçek Kusto gibi birim sınırlarını sayar; `prev`/`next`/`row_cumsum` serileştirilmemiş girdide hata verir.

## Çalıştırma

- **⚡ Programlar → Pafta** ya da Başlat menüsünde **Pafta**
- Elle: `pythonw Pafta.pyw` (Edge uygulama penceresi açılır; pencere kapanınca sunucu ~40 sn sonra kendini kapatır)
- Geliştirme: `python server.py --port 8765` (tarayıcıda `http://127.0.0.1:8765/`; `--veri KLASOR` ile ayrı bir ilerleme klasörü)

Gereksinim: Python 3.11+, Microsoft Edge (yoksa varsayılan tarayıcı açılır). Bash yolu için Git for Windows (`C:\Program Files\Git\bin\bash.exe`); PowerShell ve CMD yolları Windows'la gelen Windows PowerShell 5.1 ve cmd.exe'yi, JavaScript yolu Node.js'i kullanır. C, PHP, Java, C# ve Assembly okuma yolları için derleyici gerekmez. Elastic tezgahı JDK 17+ ve `python tools/install_elastic_runtime.py` ile kurulan pinli Lucene JAR'larını kullanır; EL01–EL19 görevleri için Elasticsearch/Kibana kurulumu gerekmez; EL20–EL27 gerçek Docker laboratuvarını ister. Python bileşenleri Sigma/YARA bağımlılıkları dışında standart kütüphaneyi kullanır.

### Kali WSL Linux koşucusu

Python ve Bash dersleri/adımları `backend: wsl` seçtiğinde **gerçek Linux** üzerinde çalışır. Varsayılan yollar mevcut Windows Python/Git Bash koşucularını kullanır. Linux seçimi Çalıştır, Kontrol, tahmin, Röntgen, Python Bytecode, tekrar, sınav puanlama ve `tools/validate.py` için aynıdır; Linux ortamı eksikse Windows'a sessiz geçiş yapılmaz.

**Gereksinimler:** Windows üzerinde WSL 2, kurulmuş ve ilk kullanıcı kurulumu tamamlanmış bir Linux dağıtımı, o dağıtımda `/usr/bin/python3` (3.11+, bu teslimde 3.14.7 ile doğrulandı) ve `/bin/bash`. Linux çekirdeği `pidfd_open`/`pidfd_send_signal` ve `PR_SET_CHILD_SUBREAPER` desteklemeli (güncel WSL 2); koşucu bu olanaklar yoksa açık hata verir. Kurulum için [Microsoft WSL yönergesi](https://learn.microsoft.com/en-us/windows/wsl/install) ve [Kali WSL belgesi](https://www.kali.org/docs/wsl/wsl-preparations/) kullanılabilir. `wsl.exe -l -v` kurulu dağıtımların adını gösterir.

Dağıtım adı **`PAFTA_WSL_DISTRO` ortam ayarından** her çalıştırmada okunur; verilmezse `kali-linux`. Pafta'yı başlatmadan önce PowerShell'de `$env:PAFTA_WSL_DISTRO = 'kali-linux'`, Git Bash'te `export PAFTA_WSL_DISTRO=kali-linux` ayarlanabilir. Dağıtım adı komut satırına ayrı argüman olarak geçirilir; WSL'nin varsayılan dağıtımı ve Windows'un `bash.exe` araması kullanılmaz.

Koşucunun kendisi Python standart kütüphanesiyle çalışır. **Ekosistem görevleri** için seçilen Linux ortamında pip, venv/ensurepip, setuptools, wheel; Requests, aiohttp, Beautiful Soup, Scapy, pwntools ve gerektiğinde Impacket bulunmalıdır. Bash'in ilgili ekleri ShellCheck/Bats gerektirir. Kali paket adları: `python3-pip`, `python3-venv`, `python3-setuptools`, `python3-wheel`, `python3-requests`, `python3-aiohttp`, `python3-bs4`, `python3-scapy`, `python3-pwntools`, `python3-impacket`, `shellcheck`, `bats`. Bunlar **Windows Python'a veya Windows `.deps` klasörüne kurulmuş olmakla sağlanmaz**. Koşucu paket yüklemez; eksik modül/komut gerçek yorumlayıcının hatası olarak görünür. Bu bilgisayarda paketler önceden kurulu olduğundan bu teslimde paket indirilmedi.

**Ders yazarı için seçim:** dersin ön bilgisindeki `backend: wsl` bütün adımlara miras kalır; tek adımdaki `meta` bloğu bunu geçersiz kılabilir. Yalnız bir adımı seçmek için:

````text
```meta
backend: wsl
timeout: 120
```
````

Yukarıdaki iç `meta` bloğu ders dosyasına yazılır; `backend: native` yerel koşucuyu seçer. Kod dili yine `python` veya `bash`; yeni bir yol açmak gerekmez. Python API'sinde `runners.get("python-wsl")` / `runners.get("bash-wsl")` veya `runners.for_step(runner, step)`; serbest API çalıştırmasında `{"track":"python","backend":"wsl", ...}` kullanılabilir. Geçersiz backend veya desteklenmeyen dil açıkça reddedilir.

Her iş Linux dosya sisteminde **`/tmp/pafta_wsl_*/calisma`** oluşturur; kod ve JSON UTF-8/LF olarak taşınır, depo veya `/mnt/c` üzerinde çalışılmaz. Girdi ve argümanlar veri olarak aktarılır; stdout/stderr ayrı döner, süreç çalıştırmalarında `kod` gerçek çıkış kodudur. Python'da Çalıştır gerçek `kod.py` sürecini çalıştırır; görev testleri aynı Linux yorumlayıcısında mevcut `eq/ok/run` ve ad alanı yardımcılarını, Bash testleri `calis/run` yardımcılarını kullanır. Python testinde sıfır dışı `sys.exit` başarı sayılmaz. Röntgen/Bytecode mevcut öğretim düzeneğini kullanır. `runtime` sonucunda dağıtım, Python sürümü/yolu, çalışma dizini, süre ve temizlik sonucu bulunur. Regresyon testi paketlerin gerçek `__file__`/sürümlerini de denetler.

Hazırlık (`setup`), öğrenci kodu ve görev testi **aynı Linux çalışma dizininde** çalışır; Windows yolu içeren hazırlıklar taşınabilir değildir. API laboratuvarında sunucu da istemci de bu işin içinde başlatılmalıdır; Windows/WSL `127.0.0.1` eşdeğerliği varsayılmaz. Her işin sonunda geçici dosyalar silinir. Venv görevi temiz venv'i açıkça oluşturmalı; varsayılan Linux yorumlayıcısı sistem paketlerini görür, temiz venv sistem paketlerini kendiliğinden devralmaz. Ortama `PIP_NO_INDEX=1` verilir; örnek wheel yerelde, `--no-index --no-build-isolation --no-deps` ile üretilip geçici venv'e kurulabilir. Bu ayar ağ yalıtımı değildir.

Linux işinin varsayılan sınırı **Çalıştır/Röntgen/Bytecode için 60 sn, görev testi için toplam 120 sn**; yazar `timeout` ile 0'dan büyük ve **en fazla 300 sn** seçebilir. Süre hazırlığı ve testlerin bütün tekrarlarını kapsar; her `run()` için yeniden başlamaz. WSL başlatması için ayrıca 30 sn, bağlantı kesilmesi sonrası temizliği beklemek için 12 sn pay vardır. Bu makinede iki ölçümde venv yaklaşık 2,5 sn, yerel wheel kurulumu 0,5 sn; wheel üretimi dahil yaklaşık 6,2 sn sürdü. Bunlar başka makineler için garanti değil, varsayılan süreyi seçmek için ölçümlerdir.

Linux gözeticisi zaman aşımı, iptal, normal bitiş ve üst sürecin bağlantıyı kapatmasında kendi alt süreçlerini sonlandırıp toplar; `setsid` ile ayrılan çocuk/torunlar da dahildir. Eşzamanlı işler birbirinin süreçlerini kapatmaz. Python çağırıcısı `WslRunner.execute(job, timeout=..., cancel_event=threading.Event())` ile iptal isteyebilir; mevcut arayüzde ayrı bir iptal düğmesi yoktur. **Bu yaşam döngüsü denetimi bir güvenlik sandbox'ı değildir:** öğrenci programı dağıtımdaki kullanıcının yetkileriyle çalışır. WSL yanıt vermez ve temizlik doğrulanamazsa sonuç bunu açık hata olarak bildirir; bütün dağıtım kapatılmaz.

Gerçek Linux regresyonları (kurulu paketleri kullanır; yalnız geçici venv'e yerel test wheel'i kurulur):

```text
python tools/test_wsl_runtime.py
python tools/test_wsl_integration.py
python tools/validate.py
```

İlk test UTF-8/LF, stdin/argv, çıkış kodu/stderr, gerçek import yolları, çevrimdışı wheel/venv, zaman aşımı, iptal, Windows çağırıcısının kapanması ve Linux çocuk/torun temizliğini; ikincisi geçici derslerle API/tahmin/sınav/validate yönlendirmesini sınar. Koşucu tasarımının dayanakları: [WSL komutları](https://learn.microsoft.com/en-us/windows/wsl/basic-commands), [Python subprocess](https://docs.python.org/3.14/library/subprocess.html), [Linux subreaper](https://man7.org/linux/man-pages/man2/PR_SET_CHILD_SUBREAPER.2const.html).

### Ağ filtreleri tezgahı

Wireshark / tcpdump yolunda öğrenci gerçek filtre ve CLI komutu yazar. Wireshark görüntü filtreleri `tshark -n -r - -Y FILTRE` ile, BPF ise libpcap'in `pcap_compile` ve `pcap_offline_filter` işlevleriyle çalışır. Bu iki filtre motoru yalnız çevrimdışı kayıt okur. TShark'ın `-f` seçeneği kayıtlı dosyada BPF uygulamaz; iki dil birbirine çevrilmez. PK29 ayrıca yalnız kendi ürettiği localhost UDP trafiğinde gerçek tcpdump yakalaması yapar.

TShark 4.6.8 bu bilgisayarda kuruludur. Başka yerde TShark PATH'te, standart Wireshark klasöründe veya `PAFTA_TSHARK` tam yolunda bulunmalı. BPF bağımlılığı: `python -m pip install --target .deps -r requirements-packets.txt`. Windows x64'te paketin sürücü gerektirmeyen tcpdump DLL'i (libpcap 1.10.6) kullanılır; Npcap kurulması gerekmez. Python paket sürümü ile C kütüphanesi sürümü ayrıdır. Eksik araç hata verir; filtreyi tahminen değerlendiren bir yedek motor yoktur.

Girdi JSON'unda `dil` (`wireshark`, `bpf` veya `tshark`) ve `kayit` seçilir; ilk ikisinde filtre, sonuncusunda sınırlı gerçek TShark komutu yazılır. `kayit` yerine `pcap_base64` ile kayıt baytları verilebilir (en fazla 8 MiB). Classic PCAP 2.4 ve PCAPNG 1.0 Enhanced Packet Block; Ethernet/RAW/SLL/SLL2 desteklenir. PCAPNG eski Packet Block/Simple Packet Block ve başka linktype'lar açık hata verir. Her arayüzün gerçek DLT'siyle BPF derlenir; zaman çözünürlüğü tam kesirle saklanır. Hostname/servis adı çözülmez; IP operandları sayısal IP/CIDR kullanır. `anahtar` yalnız `yok`, `yanlis`, `tls-h2`, `quic-lab` eğitim profillerini alır; kullanıcıdan keylog dosya yolu alınmaz. Gerçek protokol/anahtar korpusları ve üreticileri [kayıt dökümünde](tracks/packets/captures/README.md) açıklanır.

**PK29 gereksinimi:** Windows WSL, `PAFTA_WSL_DISTRO` (varsayılan `kali-linux`) dağıtımında Python 3 ve tcpdump (bu makinede 4.99.6/libpcap 1.10.6); `wsl -d kali-linux -u root` çalışabilmeli. Laboratuvar root ile yalnız `lo` arayüzünde kendi rastgele UDP uç çiftini yakalar, ilgisiz bir UDP porta gönderdiği gürültüyü de dışlar. Linux `/tmp` klasörü, paket/süre sınırı ve süreç temizliği kullanılır. Döndürme profili loopback MTU ≥60028 ister; ağ ayarını değiştirmez. Öğrenci komutundan fiziksel arayüz, başka dosya yolu veya program çalıştırma kabul edilmez. Bu bağımlılıklar yoksa PK29 açık hata verir; önceki çevrimdışı dersler için WSL gerekmez. Bu çalışma sırasında paket kurulmadı. Korpusları yeniden üretmek isteyen yazarlar için ek kurulu Scapy/ssl/cryptography/hpack/aioquic bağımlılıkları kayıt dökümünde belirtilir.

Sonuçta eşleşen frame numaraları ve boyları görünür. **Kaydın tamamı** açılır bölümünde eğitim paketlerinin kaynak/hedef, port ve açıklamaları yer alır. [Kayıt dökümü](tracks/packets/captures/README.md) sentetik paketlerin tümünü ve SHA-256 değerlerini listeler. Ders görevleri ham paket baytlarında sınanır; kendi çözümlerini Serbest Tezgah'ta da deneyebilirsin. Filtre eşleşmesi tek başına saldırı kanıtı değildir.

Sigma ve YARA'nın bağımlılıklarını, **Pafta'yı başlatan Python sürümüyle**, proje klasöründe kur:

```text
python -m pip install --target .deps -r requirements-detection.txt
```

`.deps/` Git'e girmez; kurulum başka projelerin paketlerini değiştirmez. Bu bilgisayarda Python 3.11 için pySigma 1.5.1 ve yara-python 4.5.4 kurulmuştur. Başka Python sürümüne/mimarisine geçerken uyumlu paketleri bu klasöre yeniden kur. Çalışan uygulama eski sunucuyu kullanıyorsa yeni koşucuları yüklemek için Pafta'yı kapatıp yeniden aç.

### Sigma ve YARA tezgahları

Sigma girdisi tek bir JSON olay nesnesi, nesne listesi veya JSONL'dir. Sonuç, eşleşen olayların `id` değerlerini (yoksa 1'den başlayan sıra numarasını), kural başlıklarını ve olay tablosunu gösterir. `logsource` dağıtım/telemetri sözleşmesidir: yerel tezgah verilen olayların doğru kaynaktan seçildiğini varsayar; olaylara gizlice bir kaynak filtresi eklemez. Resmi pySigma seçicileri ve koşulları ayrıştırır; Pafta'nın yerel backend'i AND/OR/NOT, 1/all of, temel metin modifier'ları, `all`, `cased`, `re` bayrakları, `cidr`, `exists`, null ve sayısal karşılaştırmaları değerlendirir. Alan adları büyük/küçük harfe duyarlıdır. Sayısal karşılaştırmada sayıya çevrilebilen JSON metinleri kabul edilir; null, boş metin ve eksik alan aynı şey değildir. Kuraldaki sayısal sabitler ±2^53 aralığıyla sınırlıdır; olayların tam sayı değerleri karşılaştırılırken hassasiyet korunur. Korelasyonlar, pipeline/alan eşleme ve üretim SIEM dönüşümü okuma konularıdır; bu tezgahta çalışmaz. Desteklenmeyen özellik açık hata verir.

YARA girdisi varsayılan olarak UTF-8 metindir. `hex:4d 5a 00` veya `base64:TVoA` önekiyle ikili veri verilebilir. Gerçek libyara kuralları derler ve yalnızca verilen baytları tarar; eşleşen kural adlarını, string konumlarını ve motor uyarılarını gösterir. Dosya yolu, süreç taraması ve `include` kullanılmaz. Her iki yolda veri sınırı 1 MiB, Sigma'da en fazla 1000 olay, YARA'da tarama başına 2 saniye sınırı vardır; ortak koşucu ayrıca süreç zaman aşımı uygular. Örnekler sentetik eğitim verileridir.

Görev testlerinde ortak `eq/ok/raises/src` yanında Sigma'da `eslesir(olay, kural_basligi=None)`, `eslesenler(olaylar, kural_basligi=None)`, `kural_adlari` ve `kurallar`; YARA'da `eslesir(veri, kural_adi=None)`, `eslesenler(veri)` ve `derle(kaynak)` vardır. YARA yardımcılarında `str` her zaman gerçek UTF-8 metindir; hex/base64 önekini yalnızca UI girdi çözücüsü yorumlar. Her görev hem olumlu hem olumsuz örneklerle sınanır ve normal tekrar sistemine katılır.

Doğrulama:

```text
python tools/validate.py --yol sigma
python tools/validate.py --yol yara
python tools/test_sigma_runtime.py
python tools/test_yara_runtime.py
python tools/test_detection_integration.py
```

Resmi dayanaklar: [Sigma şartnamesi](https://sigmahq.io/sigma-specification/specification/sigma-rules-specification.html), [pySigma](https://github.com/SigmaHQ/pySigma), [YARA Python API](https://yara.readthedocs.io/en/stable/yarapython.html).

### Elastic / Kibana sorgu tezgahı

Bu yol **KQL (Kusto)** yolundan ayrıdır. Öğrenci Kibana KQL, Lucene ve EQL sorgusu yazar; sorgu JSON girdisindeki mapping ve sentetik belgeler üzerinde değerlendirilir. Tahmin yanıtı da aynı motorla hesaplanır. KQL gerçek Lucene sorgularına ayrılır; Lucene yolu gerçek Classic QueryParser, analyzer, phrase/slop/fuzzy/regex kullanır. EQL sınırlı yerel yorumlayıcıdır; sequence anahtarları, maxspan ve until sınırları test edilir. Desteklenmeyen özellikler açık hatadır. Temel motor sunucu başlatmaz; EL19 karşılaştırma yönergesidir. EL20–EL27 için aşağıdaki gerçek laboratuvar gerekir. JDK 17+ gerekir (Android Studio JBR kullanılabilir); JAR'lar SHA-512 ile doğrulanır. Ayrıntılar, destek sınırları ve resmi kaynaklar: [yolun sözleşmesi](tracks/elastic/README.md).

```text
python tools/install_elastic_runtime.py
python tools/validate.py --yol elastic
python tools/test_elastic_curriculum.py
python tools/test_elastic_integration.py
python tools/audit_elastic_mutations.py
node --test tools/test_elastic_ui.mjs
```

#### Elastic 41–44: gerçek yerel laboratuvar

Docker Desktop açık olmalı; iki resmi imaj sürüm ve SHA-256 digest ile
`tools/elastic_lab_setup.py` içinde sabitlenir. İndirme yalnız açık kurulum
komutuyla yapılır; ders çalıştırmak paket indirmez veya Docker başlatmaz:

```powershell
python tools/elastic_lab_setup.py --pull --start
# Sonraki açılışlar (indirme yapmadan):
python tools/elastic_lab_setup.py --start
# Çalışmayı bitirince:
python tools/elastic_lab_setup.py --stop
```

Elasticsearch 9.5.5: `http://127.0.0.1:19200`; Kibana aynı sürüm:
`http://127.0.0.1:15601`. Basic lisans, kimlik doğrulama ve API anahtarları
etkindir; trial açılmaz. Her konteynere 2 GiB sınır ayrılır; Docker'a diğer
çalışan laboratuvarlarla birlikte yeterli RAM verin. Otomatik açılış yoktur.
Parola ve şifreleme anahtarları Git dışında `.deps/elastic-lab/` içinde
üretilir; Kibana kullanıcı adı `elastic`, parola `password` dosyasındadır.
Bu **yalnız localhost HTTP öğretim ortamıdır**: konteynerler arasındaki HTTP
TLS kullanmaz. EL19'un gerçek dağıtım TLS yönergesini karşılamaz; internete
veya yerel ağa port açmayın. Üretimde TLS ve en az yetki gerekir.

Gerçek pipeline + bulk alımı, EQL, Security create/preview ve ES|QL API'leri
kullanılır. Her işin rastgele indeksi/kuralı/pipeline'ı temizlenir. Security
önizlemesi operational alarm diye gösterilmez; gerçek zamanlayıcı kabulü ayrı
betikle sınanır. ES|QL için okuma anahtarı yalnız işin indeksine yetkilidir.
İleri dersler `stdin.backend: elastic` ile seçilir; yerel motora fallback yoktur.
Elastic Agent kurulmaz: EL20 gerçek üst süreç gözlemini NDJSON dosyasından
pipeline'a alır; bu gözlem Sysmon/EVTX/Agent olayı olarak sunulmaz.


### CMD / Batch tezgahı

`cmd` yolu yazma seviyesindedir: kod gerçek cmd.exe'de `/d /q /e:on /v:off` seçenekleriyle çalışır. Komut uzantıları açık, gecikmeli genişleme başlangıçta kapalıdır. Kaynaklar UTF-8/LF; geçici batch dosyaları UTF-8/CRLF'dir. Başlatıcı kod sayfasını 65001 yapar; Girdi kutusu UTF-8/CRLF dosyasından stdin'e yönlendirilerek ardışık `set /p` okumaları korunur. Her iş geçici çalışma klasöründe çalışır. Native komutların kodlama ve ayrıştırma sınırları derslerde belirtilir.

Görev çözümü batch, gizli testler Python'dır: `out`, `hata_cikti`, `run(stdin, argv)` ve `calis(stdin, argv)` (kod/cikti/hata sözlüğü) mevcut süreç yollarıyla aynıdır. `argv` değerlerinde çift tırnak, NUL ve satır sonu desteklenmez; boşluk, Unicode ve kabuk özel karakterlerinin aktarımı testlidir. Bu aktarım, öğrencinin kendi betiğinde yanlış tırnaklama veya `call` ile yeniden yorumlama etkisini ortadan kaldırmaz. CMD'de Röntgen/Bytecode yoktur. Ayrıntılı sözleşme ve kaynaklar: [CMD yolu](tracks/cmd/README.md).

```text
python tools/validate.py --yol cmd
python tools/test_cmd_runtime.py
python tools/test_cmd_curriculum.py
python tools/test_cmd_integration.py
python tools/audit_cmd_mutations.py
python tools/test_cmd_config_mutations.py
python tools/test_cmd_token_mutations.py
node --test tools/test_cmd_ui.mjs
```

## Bir paftanın akışı

Her pafta adımlardan oluşur:

| Adım | Ne olur |
|---|---|
| **Anlat** | Kavram, ölçü notlu kod örnekleri (▶ Çalıştır, ⇢ Tezgaha al), Derin su / Tuzak / Güvenlik kutuları |
| **Tahmin** | Kodun çıktısını tahmin edersin; çalıştırılabilir yolda gerçek çalıştırmayla, okuma yolunda açıklanan sabit cevapla karşılaştırılır |
| **Görev** | Kodu sen yazarsın, testler denetler; geçince "ONAYLANDI" mührü basılır |

Tezgah (sağ panel): editör, Çıktı, Kontrol, **Röntgen** ve dile göre bir görünüm (Python'da Bytecode, Regex'te Ağaç, SQL'de Plan, KQL ve SPL'de SQL karşılığı). Röntgen Python'da kodu adım adım yürütüp her satırda değişkenleri gösterir (aynı renk = aynı nesne); Bash ve PowerShell'de yorumlayıcının çalıştırdığı komutları sırasıyla, değişkenler yerine konmuş haliyle gösterir. Regex'te Röntgen yerine eşleşme tablosu, SQL'de her sorgunun sonuç tablosu vardır. Sigma ve YARA'da olay/bayt eşleşmeleri gösterilir. Geçilen görevler **Tekrar** kutularına düşer (1, 3, 7, 16, 35 gün). **Serbest tezgah** diller için ayrı bir çalışma alanıdır (`#/tezgah/<dil>`: python, regex, bash, powershell, cmd, sql, kql, spl, javascript, sigma, yara, packets, elastic, ad). Elastic sorguları JSON corpus üzerinde denenir. Okuma yollarında (C, PHP) tezgah, görevlerdeki Python içindir.

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

**CMD / Batch** dersleri de süreç testlerini kullanır. Kod blokları `cmd` (`batch`/`bat` takma adları), betik değişkenleri `%%I` biçimindedir. Tahmin veya görevde `meta` içindeki `argv` gerçek çalıştırmaya aktarılır. Beklenen hata kodunu `calis()` sonucu üzerinden sınamak için görevin ilk çalışmasının başarılı olmasını sağlayan varsayılan veya meta argümanları verilir.

**Okuma yolları (C, PHP)**: `track.json`'da `"runner": "python"`, `"dil": "python"` ve `"okuma_dili": "c"` (ya da `"php"`). Anlatım ve tahmin kodu ` ``c ` / ` ``php ` bloklarında yazılır ve çalıştırılmaz; tahmin adımına gerçek çıktı bir ` ``gercek ` bloğuyla elle verilir (ön yüze tahmin edilmeden gönderilmez). Görevler, okunan kodun davranışını Python'da kurdurur ve Python testleriyle denetlenir. `gercek` blokları doğrulayıcı tarafından çalıştırılamadığı için C/PHP davranışını iyi bildiğin örneklerle sınırlı tut ve Python karşılığıyla çapraz denetle.

**Elastic yazma yolu** `"runner": "elastic"`, `"dil": "elastic"` kullanır. Adımın `meta.dil` alanı ve JSON `stdin.dil` değeri `kibana`, `lucene` veya `eql` seçer; tahmin çiti de bu dildedir. Tahminlerde `gercek` ve sorguya özel Python modelleri yoktur. Görev çözümü sorgudur; gizli Python testleri `eslesenler(veri=None)`, `referans(sorgu, veri=None, dil=None)` ve `korpus` yardımcılarıyla gerçek sorgu sonuçlarını sınar. Açık kimlik beklentileri ve sınır corpus'ları eklenmelidir; yalnız çözüm metni denetimi yapılmaz.

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

CMD CM19–CM20: yerleşik wevtutil ile çevrimdışı EVTX sorgu ve aktarımı. Sentetik kayıtlar geçici EVT dosyasından Windows tarafından gerçek EVTX’e dönüştürülür; ek paket veya yönetici kurulumu gerekmez. Unicode XML çıktısı /uni:true ile UTF-16LE olarak saklanır.

CMD CM21–CM22: yerleşik `sc.exe`, `schtasks.exe` ve `reg.exe` ile salt okunur servis, görev ve kayıt defteri sorguları. Sonuçlar canlı makineye göre değişir; testler sabit hizmet adlarını ve başarısız sorgu sınırlarını denetler.

CMD CM23–CM24: `whoami.exe` ile canlı tokenın kullanıcı, grup ve ayrıcalık CSV'si; `icacls.exe` ile yalnız geçici dosyaların DACL görünümü ve ayrıca gerçek dosya okuma tanığı. ACL değiştirilmez.

### Pafta içinden gerçek Active Directory laboratuvarı

AD15 (ACL), AD18 (S4U), AD21 (CA) ve AD22–AD23 (LDAP bağlantısı) gerçek ürün üzerinde çalışır. **Dersin Çalıştır/Kontrol düğmeleri yeterlidir:** Pafta gerekli konukları arka planda açar, kodu VMware Tools ile aktarır ve sonucu ders ekranına getirir. Öğrencinin VM konsoluna girip komut kopyalaması gerekmez. İlk soğuk açılış için konuk başına 180 saniye hazırlık payı vardır; görev testleri toplam 240 saniyeyle sınırlıdır. Öğrenci PowerShell kodu yalnız bu laboratuvarda Domain Admin hesabıyla çalışır; bu bir kısıtlı yetki sandbox'ı değildir. İş bitince Windows Job Object çocuk süreçleri de kapatır; VM'ler sonraki ders için açık kalır.

Gereksinimler: Windows, kurulu VMware Workstation ve onun `vmrun.exe`, `vmware-vdiskmanager.exe`, `windows.iso` dosyaları; [resmî Windows Server 2025 Evaluation ISO](https://www.microsoft.com/en-us/evalcenter/download-windows-server-2025); iki konuk için toplam 6 GB ayrılmış RAM ve sanal disk başına 60 GB büyüyebilen boş disk alanı (ISO ayrıca yaklaşık 8,2 GB). Host ve diğer uygulamalar için ek RAM gerekir. Workstation konumu kurulum betiğindeki `VMWARE` sabitidir. VMware VMnet1 host-only ağı /24 olmalıdır; betik bu ağın .10/.11 adreslerini yalnız yeni Pafta konuklarına ayırır. Bu adreslerin başka bir cihazda kullanılmaması gerekir.

Bir defalık hazırlık: ISO'yu `%LOCALAPPDATA%\Pafta\labs\ad\media\WindowsServer2025-eval-en-us.iso` konumuna koyup depo kökünde `python tools/setup_ad_vm.py --provision` çalıştır. Betik yeni `PF-DC01` (AD DS/DNS/KDC/Enterprise CA) ve `PF-APP01` üye sunucusunu kurar; `pafta.test` etki alanını ve sabit deney hesaplarını hazırlar. Windows kurulumu ve yeniden başlatmalar süre alır. Komut yeniden çalıştırıldığında kaydedilmiş aşamalardan devam eder. Betik ISO veya paket indirmez; eksik gereksinim açık hata verir. VM, özel parola ve kurulum medyası depoya girmez; özel durum `%LOCALAPPDATA%\Pafta\labs\ad` altında saklanır. Bu klasörü veya VM disklerini paylaşma. Yeni konuklar host-only ağdadır; ana bilgisayarın etki alanı, DNS ve güvenlik duvarı ayarları değiştirilmez. Mevcut VM'ler kullanılmaz.

AD22–AD23 ayrıca WSL 2 ve `PAFTA_WSL_DISTRO` (varsayılan `kali-linux`) içinde mevcut Python 3, Impacket (`LDAPConnection` signing/CBT alanlarını destekleyen sürüm), pyOpenSSL ve OpenLDAP `ldapsearch` ister. Bu teslimde mevcut Kali Python 3.14.7, Impacket 0.14.0.dev0, pyOpenSSL 26.4.0, cryptography 49.0.0 ve OpenLDAP 2.6.14 kullanıldı; kurulum betiği paket kurmaz. CA yalnız istemcinin o bağlantısına güvenilir; Windows veya Kali'nin genel güven deposu değiştirilmez. LDAPS istemcisi CA/ad kontrolü ve aynı yaprak sertifikanın karşılaştırmasını yapar; Always CBT ve zorunlu LDAP signing politikaları yalnız laboratuvar DC'sindedir. Bu laboratuvar genel bir uzak AD istemcisi değildir.

**Evaluation süresi:** Microsoft bu sürümü 180 günle sınırlar ve otomatik kapanmayı önlemek için ilk 10 gün içinde internetten etkinleştirme ister ([resmî koşullar](https://www.microsoft.com/en-us/evalcenter/evaluate-windows-server-2025)). Host-only kurulum internet etkinleştirmesini yapmaz; bu teslimde etkinleştirme doğrulanmış değildir. Süresiz laboratuvar lisansı vaat edilmez. Etkinleştirme veya lisanslı imaja geçiş ayrı bakım işidir; süresi dolmuş bir VM'de ders başarısı beklenmemelidir.

Yazar doğrulaması: `python tools/test_ad_vm_runtime.py` taşıma/parola gizleme ve gerçek Windows Job Object yaşam döngüsünü; `python tools/test_ad_advanced.py` çevrimdışı tahminleri ve mutasyonları sınar. `PAFTA_AD_LIVE=1` ayarıyla aynı betik canlı tahmin/görevleri ve ek mutasyonları da çalıştırır. `tools/test_ad_app.py` API yönlendirmesini geçici ilerleme dosyasıyla; `tools/capture_ad_evidence.py` gerçek S4U/LDAP cevaplarını ve aynı zaman aralığındaki DC 4769 XML'ini ölçer. `python tools/validate.py --yol ad` canlı dersleri de gerçek konuklarda çalıştırır; bu kontrol VM'leri başlatabilir ve yalnız deney nesnelerini geçici değiştirip geri alır. AD01–AD12 için VMware/WSL gerekmez. AD13–AD14, AD16–AD17 ve AD19–AD20 sentetik normalize kesitlerdir; gerçek ACL/S4U/CA kabulünün yerine geçtikleri iddia edilmez.

YR23–YR24 `motor: python` ile gerçek yara-python paket/tarama API'sini kullanır (`sandbox/yara_bundle.py`); include yalnız verilen kaynak sözlüğünden gelir, normal YARA tezgahı disk include'ı açmaz. AD24–AD25 çevrimdışı SYSVOL/LAPS kanıt ayrıştırma dersleridir; VM veya LAPS dağıtımı gerektirmez.
