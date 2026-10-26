# PF-2026-102 · Örnek inceleme raporu

Bu belge sentetik eğitim vakasıdır; gerçek ihlal veya saldırı zinciri üretildiği iddia edilmez. Hazırlayan: Pafta eğitim laboratuvarı, 26 Ekim 2026. Durum: inceleme açık; yetkisiz kullanım doğrulanmadı.

## Yönetici özeti

ws01/alice için 26 Ekim 2026 09:00:00–09:02:00 UTC kapalı penceresinde üç başarısız giriş kaydı seçildi. Aynı cihazın vaka envanterindeki adresinden bakım scripti yoluna HTTP isteği ve daha sonra aynı hesapla ilişkilendirilmiş bir süreç gözlemi var. Bu paket yetkisiz erişimi, istenen baytların çalıştırılmasını veya veri sızmasını kanıtlamıyor. SOC, bakım sahibi ve kullanıcıyla değişiklik kaydını doğrulamalı; uç nokta dosya/oturum kanıtlarını korumalı. Hizmet etkisi yüksek izolasyon kararı olay sorumlusuna bırakıldı; herhangi bir önleme değişikliği uygulanmadı.

## Kapsam ve kanıt

Vaka dosyaları `veri/` altında. manifest.json, olaylar.jsonl/vaka.json/vaka.pcap SHA256 değerlerini içerir. Bu manifest bağımsız imza veya erişim zinciri değildir. Sorgular `sandbox/capstone_lab.py` üzerinden mevcut yerel Kusto/SPL→SQLite ve pySigma/yerel olay motoruyla; paket filtresi kurulu gerçek TShark ile çalıştırılır. Üretim Sentinel/Splunk dağıtım sonucu değildir. BT01 bütünlük kontrolü başarısızsa bu sonuçları kullanma.

Host/IP envanteri: ws01→10.0.0.10, ws02→10.0.0.11; yalnız vaka anı için sağlanmış eşlemedir. Normalize olaylarda zaman vaka başlangıcından göreli tam saniye; PCAP zamanı kayıt başlığından gelir. Kaynak saat hata bütçesi iki saniye. Paket kaydı yalnız dört HTTP isteğidir, bütün ağ trafiği veya dosya içeriği değildir.

## Yeniden üretim

Kusto sorusu: `olaylar | where source == "auth" and host == "ws01" and user == "alice" and outcome == "failure" and ts >= 0 and ts <= 120 | project id`

SPL sorusu: `sourcetype=olaylar | where source="auth" AND host="ws01" AND user="alice" AND outcome="failure" AND ts>=0 AND ts<=120 | table id`

Sigma kaynağı: BT03 kuralı; logsource windows/process_creation, Image|endswith `\powershell.exe`, CommandLine|contains `\health.ps1`, aynı seçim içinde AND. Yalnız endpoint kayıtlarına uygulanır.

TShark filtresi: `ip.src == 10.0.0.10 and http.host == "updates.lab.test" and http.request.uri == "/health.ps1"`

Pafta tezgâhında BT04 `incele` bu dört metinle çalıştırılır. CLI kabulü: `python tools/validate.py --yol bitirme` ve `python tools/test_capstone.py`. Teslim raporunda araç sürümleri/bağımlılıkları ve depo commit'i ayrıca kaydedilir; bu belge her makinede aynı TShark sürümünün kurulu olduğunu varsaymaz.

## UTC zaman çizelgesi

| UTC | Kanıt | Gözlem |
|---|---|---|
| 09:00:00 | auth:a-start | İlk kapalı uçta başarısız giriş kaydı |
| 09:01:00 | auth:a-mid | Başarısız giriş kaydı |
| 09:02:00 | auth:a-edge | Son kapalı uçta başarısız giriş kaydı |
| 09:02:05 | auth:a-ok | Başarılı giriş kaydı; önceki başarısızlarla aynı oturum olduğu kanıtlanmadı |
| 09:02:10 | vaka.pcap#frame=1 | 10.0.0.10→updates.lab.test /health.ps1 HTTP isteği |
| 09:02:10 | proxy:w-get | Ayrı proxy sensöründe 200 sonucu; PCAP yanıtı değildir |
| 09:02:15 | endpoint:p-run | PowerShell bakım scripti metni içeren süreç kaydı |

BT04 otomatik çizelgesi yalnız seçili auth/Sigma/frame kanıtlarını içerir. Burada a-ok ve w-get ham paketten ayrıca açıkça eklendi; her satır kaynak kimliğini korur. Aynı saniyeli gözlemler için neden-sonuç sırası atanmadı. Başlangıçtan önceki a-before ve sonraki a-after ham pakette korunur, sorulan auth penceresine alınmaz.

## Gözlem, yorum ve bilinmeyen

- Gözlem: Kusto/SPL aynı üç başarısız auth id'sini döndürür. Sorgu sözleşmesi ve kontrol grupları BT02 testlerinde korunur.
- Gözlem: Sigma yalnız p-run kaydını seçer. Süreç adı/script metni belirlenen davranışa uygundur; içeriğin zararlı olduğuna hükmetmez.
- Gözlem: Frame 1 üç ağ koşulunu taşır. Frame 2 başka istemci, frame 3 farklı URI, frame 4 farklı HTTP Host kontrolüdür.
- Hipotez: Yetkili bakım akışı bu gözlemleri açıklayabilir. Bakım iş emri henüz pakette yoktur.
- Bilinmeyen: Hesabı kimin kullandığı, istekteki dosyanın hash'i, süreçte çalıştırılan dosyayla aynı olup olmadığı, payload içeriği ve veri sızması. Başarılı auth tek başına bu soruları çözmez.

## Tespit boşluğu ve öneri

G1: CommandLine alanı eksik gelirse BT03 seçicisi kayıt seçemez. Bu bir telemetri/alan eşleme bağımlılığıdır; “kuralı bütün süreçlere genişlet” önerisi değildir. Tanık: p-run kaydından CommandLine kaldırıldığında BT03 olumsuz kontrolü eşleşme olmadığını gösterir. Meşru bakım kayıtları negatif/inceleme dışı olarak ayrı etiketlenmeli; pozitif etiketi zararlı niyet anlamına gelmemeli.

Sahip: Detection Engineering; hedef: 27 Ekim 2026 09:00 UTC. Önce kaynak alanının toplandığını ve eşlendiğini doğrula; veri sağlığı alarmı ve korunmuş kontrollü kayıtla test ekle. Kural/veri sürümünü ayrı tut. Geri dönüş: yeni mapping/pipeline sürümünü önceki onaylı sürüme döndür, etkilenen alarm kuyruğunu yeniden incele. Kabul: temsilî etiketli korpusta BT06 kapıları, eksik alan negatif kontrolü, meşru bakım FP incelemesi; üretimde ayrı kontrollü sensör→alarm→analist kabulü. Replay tek başına üretim kabulü sayılmaz.

SOC/vaka sorumlusu bakım ve kullanıcı doğrulamasını 26 Ekim 2026 18:00 UTC'ye kadar tamamlasın. Bunlar eğitim senaryosunun önerilen tarihleridir, yapılmış işlemler değildir. Kullanıcı ve kurum bağlamı gerçek olayda ayrıca belirlenir. Nihai insan incelemesi: iddiaların ham kanıtla anlam ilişkisi, bilinmeyenler, gizlilik, hizmet etkisi ve önerinin gözlenen boşlukla ilişkisi kontrol edilir.
