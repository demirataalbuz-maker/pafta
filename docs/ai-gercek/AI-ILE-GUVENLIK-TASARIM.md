# AI ile Güvenlik Yolu (`ai-ile-guvenlik`) · Faz A Tasarım Önerisi

Hazırlayan: `antigravity` · Tarih: 29 Ekim 2026 · Referans: `docs/ai-gercek/ANTIGRAVITY-GOREV.md` §11

## 1. Yol Kimliği ve Amacı

- **Yol Kimliği (`id`):** `ai-ile-guvenlik`
- **Adı (`name`):** `AI ile Güvenlik: Zafiyet Avı, Triyaj ve Otonom Savunma`
- **Grup / Koşucu:** `"group": "ai"`, `"runner": "python"`, `"dil": "python"`, `"order": 34`
- **Rol (`role`):** Yerel dil modellerini, gömme (embedding) modellerini ve kural motorlarını siber güvenlik iş akışlarında (statik kod denetimi, keşif/fuzzing otomasyonu, log/alarm triyajı ve kapsam kilitli güvenlik ajanı geliştirme) doğrulanabilir birer mühendislik aracı olarak kullanmak.
- **Slogan (`tagline`):** `"Halüsinasyonu ölçülen LLM'den kapsam kilitli güvenlik ajanına; Purple ve Web laboratuvarlarıyla konuşan yerel AI güvenlik mühendisliği."`
- **Kahraman:** `["Alarmdan", "Kanıt", "a"]`

### Güvenlik ve Kapsam Sınırları (Zorunlu İlkeler)
1. **Yalnız Yerel ve Ücretsiz Araçlar:** Tüm dersler yerel Ollama modelleri (`qwen3:4b`, `qwen3:8b`, `all-minilm:22m`), `.ai-venv` (PyTorch, Playwright, scikit-learn) ve Pafta'nın yerleşik laboratuvarları (`sandbox/http_tezgah.py`, SQLite/FTS5, yerel Sigma/Elastic korpusları) üzerinde çalışır.
2. **Dış Ağa Çıkış Yok (`127.0.0.1` ve Yerel Dosya Kilidi):** Keşif, fuzzing ve ajan derslerinde hedef yalnızca Pafta'nın kendi yerel laboratuvarlarıdır.
3. **Kapsam Kilidi ve İnsan Onayı (Human-in-the-Loop):** Ajanların çalıştırabileceği araçlar izinli hedef listesiyle (`allowlist`) sınırlandırılır; yıkıcı veya durum değiştiren her eylemde kriptografik/açık insan onayı kapısı zorunludur.
4. **Halüsinasyon Doğrulama Şartı:** Modelin "açık buldum" veya "saldırı var" iddiası tek başına bulgu sayılmaz; gerçek yürütücü/sorgu çıktısıyla doğrulanmayan her model iddiası **yanlış pozitif / halüsinasyon** olarak ölçülür.

---

## 2. Altı Modül ve 18 Derslik Müfredat Taslağı

### Modül 1 · `minik` · Yerel LLM'i Güvenlik Aracı Olarak Kullanmak
> **Zen:** *"Doğrulanmamış model çıktısı bulgu değil, yalnız sınanacak bir hipotezdir."*

| Sıra | Ders Kimliği | Başlık | Ne Öğretir (Hücum + Savunma / Doğrulama) | Kurulu Araç | Gerçek Deney (`motor: ai-gercek`) | Mevcut Ders Bağları |
|---|---|---|---|---|---|---|
| 1 | `ai-ile-guvenlik-01` | **Yapılandırılmış Güvenlik Çıktısı ve Şema Zorlama** | Güvenlik analizinde serbest metin yerine katı JSON şeması üretme, eksik/fazla alanları ve tip kaymalarını yakalama, yeniden deneme bütçesi. | Ollama (`ai_lab.SohbetOturumu`) | Yerel modelden CVE/bulgu özeti için JSON şeması isteme ve deterministik doğrulayıcıyla şema uyumunu ölçme. | `ai-temel-14`, `ai-saldiri-10` |
| 2 | `ai-ile-guvenlik-02` | **Güvenlik Analizinde Halüsinasyon ve Kanıt Eşleştirme** | Modelin raporladığı satır numarası, dosya yolu, CVE veya paket adını kaynak dosyayla çapraz doğrulama; halüsinasyon oranını (`hallucination_rate`) hesaplama. | Ollama + Python `ast`/`difflib` | Yerel modelin sentetik bir kod/log dosyası hakkındaki iddialarını gerçek dosya satırlarıyla karşılaştırıp uydurma referansları ayıklama. | `ai-guvence-32`, `ai-saldiri-41` |
| 3 | `ai-ile-guvenlik-03` | **Embedding ile Güvenlik Korpusu ve Benzer Zafiyet Arama** | Zafiyet kayıtlarını, olay özetlerini ve yama notlarını yerel embedding modeliyle indeksleme; kosinüs benzerliği ve eşik kalibrasyonu ile benzer vakaları bulma. | Ollama `all-minilm:22m` / SQLite | Gerçek `all-minilm:22m` gömmeleriyle yerel zafiyet/olay korpusunda benzerlik araması ve yanlış eşleşme ölçümü. | `ai-temel-16`, `ai-saldiri-15` |

### Modül 2 · `tesviye` · Kod Okuma ve Zafiyet Avında LLM
> **Zen:** *"Statik analiz aday üretir, model bağlamı okur, yürütücü kanıtlar."*

| Sıra | Ders Kimliği | Başlık | Ne Öğretir (Hücum + Savunma / Doğrulama) | Kurulu Araç | Gerçek Deney (`motor: ai-gercek`) | Mevcut Ders Bağları |
|---|---|---|---|---|---|---|
| 4 | `ai-ile-guvenlik-04` | **AST Ön-Elemesi ve LLM ile Kaynak–Evye (Source-to-Sink) Triyajı** | Python `ast` ile tehlikeli çağrı adaylarını (`subprocess`, `eval`, ham SQL) çıkarma; sabit dizge ile kullanıcı girdisini ayırt etmek için LLM triyajı ve yanlış pozitif (`FP`) ölçümü. | Python `ast` + Ollama | Gerçek Python dosyalarında `ast` taraması + yerel LLM triyajı; sabit güvenli çağrılarla gerçek enjeksiyon evyelerini ayırma. | `pu02`, `ai-savunma-11` |
| 5 | `ai-ile-guvenlik-05` | **Kimlik Bilgisi ve Sır Sızıntısı Avında Bağlamsal Triyaj** | Regex/entropi tarayıcılarının ürettiği yüzlerce sahte alarmı (test anahtarı, örnek UUID, şablon) gerçek sır sızıntısından ayırma; modele gerçek sırrı göndermeden maskeli bağlamla sınıflandırma. | Python `re`/entropi + Ollama | Maskelenmiş yerel yapılandırma dosyalarında entropi + yerel LLM sınıflandırması ile TPR/FPR ölçümü. | `ai-saldiri-39`, `ai-savunma-08` |
| 6 | `ai-ile-guvenlik-06` | **Yama Önerisi Üretimi ve Regresyon Doğrulaması** | Açıklı kod parçası için yerel modelden yama (`diff`) üretme; yamanın hem açığı kapattığını (exploit testi) hem de normal işlevi bozmadığını (birim testi) otomatik sınama. | Ollama + `unittest`/`subprocess` | Yerel modelin ürettiği yama adayını gerçek Python alt sürecinde güvenlik ve işlev testlerinden geçirme. | `ai-savunma-29`, `ai-guvence-04` |

### Modül 3 · `kucuk-orta` · Keşif ve Fuzzing Otomasyonu
> **Zen:** *"Akıllı yük üretimi kapsam kilidi olmadan çalıştırılmaz."*

| Sıra | Ders Kimliği | Başlık | Ne Öğretir (Hücum + Savunma / Doğrulama) | Kurulu Araç | Gerçek Deney (`motor: ai-gercek`) | Mevcut Ders Bağları |
|---|---|---|---|---|---|---|
| 7 | `ai-ile-guvenlik-07` | **Kapsam Kilitli HTTP Keşfi ve Parametre Haritalama** | Yerel web tezgahından (`127.0.0.1`) dönen uç noktaları ve form parametrelerini ayrıştırma; kapsam dışı host/port/yöntemleri reddeden deterministik keşif kapısı. | `sandbox/http_tezgah.py` + Ollama | Yerel HTTP tezgahında çalışan uç noktaları modelle sınıflandırıp kapsam kilidinden geçirerek güvenli test planı çıkarma. | `ai-saldiri-36`, `ai-guvence-34` |
| 8 | `ai-ile-guvenlik-08` | **Dilbigisi Destekli (Grammar-Guided) Fuzzing Yükü Üretimi** | Modelin rastgele bozuk metin yerine hedef ayrıştırıcının (JSON, URL, SQL, başlık) sınır durumlarını zorlayan kurallı mutasyon yükleri üretmesi ve yanıt anomalisi tespiti. | Ollama + yerel ayrıştırıcı | Yerel modelle sınır durumu yükleri üretip yerel hedef ayrıştırıcıda istisna/durum kodu farklarını ölçme. | `ai-saldiri-10`, `ai-guvence-08` |
| 9 | `ai-ile-guvenlik-09` | **Başsız Tarayıcı (Playwright) ile DOM Güvenlik Denetimi** | Yerel HTML uygulamasında Playwright ile form, gizli girdi ve CSP/bağlantı yüzeyini toplama; dış ağ kapalıyken (`route.abort()`) model destekli güvenlik kontrol listesi doğrulaması. | Playwright + Chromium + Ollama | Başsız Chromium'da yerel sayfayı açıp DOM yüzeyini çıkarma ve yerel modelle güvenlik bulgularını doğrulama. | `ai-saldiri-31`, `ai-saldiri-09` |

### Modül 4 · `buyuk-orta` · Log, Telemetri ve Alarm Triyajı
> **Zen:** *"Özet hız kazandırır; ham log satırı ise tek gerçektir."*

| Sıra | Ders Kimliği | Başlık | Ne Öğretir (Hücum + Savunma / Doğrulama) | Kurulu Araç | Gerçek Deney (`motor: ai-gercek`) | Mevcut Ders Bağları |
|---|---|---|---|---|---|---|
| 10 | `ai-ile-guvenlik-10` | **Çoklu Log Akışı Özeti ve Kanıt Satırı Doğrulaması** | Binlerce satırlık web/kimlik doğrulama/DNS logunu kümeleme, yerel modelle olay özeti üretme ve özetteki her IP/kullanıcı/zaman damgasını ham log satırlarıyla doğrulama. | Ollama + yerel JSONL logları | Yerel modelin ürettiği olay özetindeki varlıkları (`IP`, `user`, `event_id`) ham log kayıtlarıyla karşılaştırıp uydurma varlıkları reddetme. | `pu15`, `ai-savunma-22` |
| 11 | `ai-ile-guvenlik-11` | **LLM Destekli Sigma Kuralı Taslağı ve Yanlış Alarm Sınaması** | Saldırı örneğinden yerel modelle Sigma kuralı taslağı üretme; kuralın şemasını doğrulama ve temiz/saldırı log korpusunda yakalama (`TPR`) ile yanlış alarm (`FPR`) oranını ölçme. | Ollama + YAML/Sigma değerlendirici | Yerel modelden Sigma kuralı üretip gerçek yerel log korpusunda hem saldırıyı yakaladığını hem temiz trafiği bozmadığını sınama. | `ai-savunma-24`, `pu08` |
| 12 | `ai-ile-guvenlik-12` | **Log Enjeksiyonuna Dayanıklı SOC Triyaj Hattı** | Saldırganın `User-Agent` veya kullanıcı adına gömdüğü dolaylı prompt injection yüklerinin SOC özetleyici modelini yanıltmasını (alarm gizleme / sahte temiz raporu) engelleme. | Ollama (`ai_lab.SohbetOturumu`) | Zehirli log satırı içeren yerel olay akışında korumasız ve veri-ayrımlı SOC triyaj hattını canlı modelde karşılaştırma. | `ai-saldiri-02`, `ai-savunma-04` |

### Modül 5 · `basalti` · Kendi Güvenlik Ajanını Yazmak
> **Zen:** *"En güçlü ajan, yetkisinin nerede bittiğini kod düzeyinde bilen ajandır."*

| Sıra | Ders Kimliği | Başlık | Ne Öğretir (Hücum + Savunma / Doğrulama) | Kurulu Araç | Gerçek Deney (`motor: ai-gercek`) | Mevcut Ders Bağları |
|---|---|---|---|---|---|---|
| 13 | `ai-ile-guvenlik-13` | **Salt-Okunur Keşif Ajanı ve Deterministik Kapsam Kilidi** | Araç çağıran (`tool-calling`) yerel güvenlik ajanında hedef IP/alan/dosya kapsam kilidi, adım bütçesi ve döngü kırıcı (`circuit breaker`) tasarımı. | Ollama (`araclar_gerekli=True`) | Yerel modelle çalışan keşif ajanında kapsam içi ve kapsam dışı araç çağrılarını sandbox üzerinde canlı sınama. | `ai-savunma-11`, `ai-saldiri-16` |
| 14 | `ai-ile-guvenlik-14` | **Yıkıcı Eylemlerde İnsan Onayı (HITL) ve İmzalı Görev Kapısı** | Güvenlik ajanının karantina, IP engelleme veya dosya silme gibi yüksek etkili araçları yalnızca doğrulanmış insan onayı jetonu ve parametre özeti (`SHA-256`) eşleştiğinde çalıştırması. | Ollama + `hashlib`/`hmac` | Canlı ajan döngüsünde onaysız veya değiştirilmiş parametreli müdahale çağrılarının yürütücü tarafından reddedildiğini kanıtlama. | `ai-savunma-12`, `ai-saldiri-18` |
| 15 | `ai-ile-guvenlik-15` | **Çok Ajanlı Mavi/Mor Takım İş Akışı (Toplayıcı → Analist → Doğrulayıcı)** | Kanıt toplayan ajan, hipotez kuran analist ajan ve bulguyu bağımsız araçla doğrulayan hakem ajanın görev ayrımı; ajanlar arası mesajda zehirlenme izolasyonu. | Ollama (`ai_lab.SohbetOturumu`) | Yerel model üzerinde 3 adımlı (Toplayıcı → Analist → Hakem) canlı ajan zinciri ve doğrulama kapısı deneyi. | `ai-saldiri-43`, `ai-savunma-30` |

### Modül 6 · `baspehlivan` · Güvenlik Ajanını Değerlendirmek ve Güvence
> **Zen:** *"Ölçülmeyen otomasyon, hataları insan hızından makine hızına çıkarır."*

| Sıra | Ders Kimliği | Başlık | Ne Öğretir (Hücum + Savunma / Doğrulama) | Kurulu Araç | Gerçek Deney (`motor: ai-gercek`) | Mevcut Ders Bağları |
|---|---|---|---|---|---|---|
| 16 | `ai-ile-guvenlik-16` | **Güvenlik Ajanlarında Hassasiyet, Duyarlılık ve Maliyet Dengesi** | Farklı istem/model/eşik ayarlarında güvenlik ajanının `precision`, `recall`, `F1`, gecikme (`ms`) ve token maliyetini birlikte ölçüp Pareto optimal yapılandırmayı seçme. | Ollama + `.ai-araclar/promptfoo` | Yerel vakalar üzerinde güvenlik ajanını çoklu tohumda koşup doğruluk ve token bütçesi eğrisini çıkarma. | `ai-guvence-04`, `ai-savunma-31` |
| 17 | `ai-ile-guvenlik-17` | **Güvenlik Ajanına Karşı Kırmızı Takım (Anti-Triage & Evasion)** | Saldırganın güvenlik ajanını kör etmek, yanlış hedefe yönlendirmek veya sonsuz araç döngüsüne sokmak için kullandığı karşı-saldırıları sınama ve sağlamlaştırma. | Ollama (`ai_lab.SohbetOturumu`) | Zehirlenmiş kaynak kod/log girdilerine karşı güvenlik ajanının dayanıklılığını ve bütçe/izolasyon kontrollerini canlı ölçme. | `ai-saldiri-38`, `ai-saldiri-40` |
| 18 | `ai-ile-guvenlik-18` | **Uçtan Uca Yerel AI destekli Olay Müdahale ve Doğrulama Tatbikatı** | Log anomalisi tespiti → kök neden hipotezi → kapsam kilitli inceleme → insan onaylı müdahale → regresyon kuralı üretimini tek bir tekrarlanabilir kanıt paketinde birleştirme. | Ollama + SQLite + Sandbox | Baştan sona yerel sandbox üzerinde çalışan, her adımı kanıtlı AI destekli olay müdahale tatbikatı. | `ai-savunma-30`, `ai-guvence-05` |

---

## 3. Onay Sonrası Uygulama Adımları (Faz B ve Faz C)
1. Kullanıcı tasarım önerisini onayladığında `tracks/ai-ile-guvenlik/track.json` ve `ai_mufredat_plan_v3.json` güncellenip `python -X utf8 ai_panel_uret.py` çalıştırılacak.
2. `tools/ai_ders_takip.py` içindeki `YOLLAR` listesine `"ai-ile-guvenlik"` eklenecek ve `YOL_HARITASI.html` içine `A22 · AI ile Güvenlik yolu` kutusu işlenecek.
3. Her ders §3–§6 standardında (görünür sentetik fixture, gizli test verisi, gerçekçi kusurlu başlangıç kodu, `mutasyon.py` 0 geçen, sonda `motor: ai-gercek` canlı deney ve kanıt) sırayla yazılacak.
