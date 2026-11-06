# AI Savunma38 — multimodal OCR/ASR güven sınırı teslimi

2026-11-04 · Yazar: Codex. Kendi kontrolleri tamamlandı; bağımsız claude-opus denetimi bekleniyor. Puan verilmedi. Plan kaydı plan-savunma-7, gerçek ders ai-savunma-38.

## Sonuç ve kapsam
Gerçek Tesseract OCR ve gerçek Whisper ASR çıktıları, host provenance bilgisi korunarak yerel dosya araçlarına bağlandı. Dört medya girdisi (iki PNG, iki WAV), her biri için korumasız ve korumalı olmak üzere8ayrı dosya akışı çalıştı. Korumasız saldırı kontrolünde iki kanalda toplam4gerçek etki oluştu: sentetik canary yerel outbox dosyasına yazıldı ve kendi private.txt dosyası silindi. Korumalı akışlarda yetkisiz etki0; dört meşru arşiv dosyası ham OCR/ASR metniyle birebir aynı.

Önemli yöntem ayrımı: algılama araçları/model çağrıları gerçek; araç önerisi üretimi iki komutlu, açıkça etiketlenmiş deterministik replay'dir. Gerçek LLM planner'ın bu komutları seçtiği, genel jailbreak başarısı veya tüm multimodal saldırılara dayanıklılık iddia edilmez. Böyle bir rastgele başarı kabul şartı yapılmadı. Replay'den sonraki dosya/outbox etkisi ise gerçek, hash ve dosya içeriğiyle ölçülür. Dış e-posta/ağ gönderimi yok; outbox yalnız kendi JSONL dosyasıdır.

## Onaylı kurulum ve gerçek araçlar
Kullanıcı OCR kurulumunu ayrıca onayladı. Resmî Debian Bookworm depolarından tesseract-ocr5.3.0-2,English/osd verisi ve gerekli kitaplıklar kuruldu. Ölçülen ağ planı39.756.840bayt; ek Docker katmanı128.336.723bayt. Mevcut pafta-ai-s51:mlflow-2.2.1 yalnız base dosya sistemi olarak kullanıldı; MLflow servisi açılmadı. Yeni base image,Windows paketi veya Python paketi yok.

OCR image pafta-ocr38:tesseract-5.3.0-2,IDsha256:d54c568dc43a4add16eb38cd9e6c1187a1904192bd14170ae9f5bb3790e45ed9. Parent katmanları değişmediği doğrulandı. Paket/sürüm listesi,TesseractbinarySHA256 ve diller outputs/ocr38-kurulum/kurulum.json içinde. Ders imageID'yi bu onaylı kurulum kaydıyla eşleştirir; yokluk/uyumsuzluk kabul edilmez. Runtime sürümü tesseract5.3.0,leptonica1.82.0 ve ilgili codec sürümleri receipt'te. Bu sürümün en yeni upstream sürüm olduğu söylenmez.

OCR konteyneri create→CIDyakala→start-ai→rm-fCID ile yönetilir. Networknone,read-onlyroot,UID10001,capdropALL,no-new-privileges,256MB/PID32 sınırı,tmpfs/tmp;hostmount/port/socket yok. Yalnız kendi oluşturduğu64hexCID kaldırılır ve dockerps ile yokluğu doğrulanır. Son güvence olarak create--pullnever eklendi; bu bayrakla tek gerçek OCR çağrısı ayrıca geçti ve kendi konteyneri kapandı (ocr-no-pull.json). Kurulum dışında otomatik pull/paket/model indirmesi yok.

Ses Windows'un mevcut MicrosoftZiraDesktop,en-US SAPI sesiyle16kHz/16bit/monoWAVolarak üretildi. Base64EncodedCommand yol/metin tırnaklarını güvenli taşır; mikrofon veya gerçek kişinin kaydı kullanılmaz. SAPI nesnesi Dispose edilir, kendi PowerShell çağrısı biter. Mevcut Systran/faster-whisper-small rev536b0662742c02347bc0e980a01041f333bce120,CTranslate2 CPU/int8,beam1,languageen ile gerçek transkript üretir. Yeni ASR modeli indirilmedi. Whispermodel.binSHA256:3e305921506d8872816023e4c273e75d2419fb89b24da97b4fe7bce14170d671. Faster-whisper/CTranslate2/Pillow/Python sürümleri ve cihaz receipt'te; host'taki diğer model/GPU süreçleri yönetilmez.

## Öğrencinin yaptığı iş
Üç kusurlu starter ve bağımsız görev: kaynak_etiketi ham metni değiştirmeden UTF8hash ve veri etiketi üretir; arac_izni yalnız host'un kullanıcı yetkisiyle verdiği tam dosya/metin hash'ine izin verir; etki_raporu gerçek akışların canary/outbox/not sonuçlarını ayırır. Policy hata/yanlış tipte fail-closed çalışır, çağrı/bağlam kopyası verilir. Host provenance medya metnindeki SYSTEM/USER yazısından türetilmez. İçerikte delete kelimesi bulunması, yetkili düzTXT arşivini engellemez. Arşivlenmiş metnin sonraki okuyucuda da veri olarak kalması gerektiği açıklanır.

İlk tablo,NOT,görünür multimodal/ornek.json+README,hazirla,tahmin→çıktı→fark,hata vitrini,saldırı12/32eşlemesi,gerçek kanıtı yorumlama ve sınır cümlesi var. Fixture sentetiktir; canlı OCR/ASR yerine sunulmaz. Setup geçici çalışma kopyası yapar. UI Run'da bu dosyaya ogrenci_deneme alanı yazılıp geri okundu; gerçek deney bağımsız medyadan çalışmaya devam etti. Sonraki çağrıya kalıcılık iddiası yoktur.

## Kontroller
- python -X utf8 tools/validate.py ai-savunma-38 →1ders9kontrol TEMİZ:4solution,4starter,1tahmin.
- tahmin.py . ai-savunma-38 →1tahmin0şüpheli.
- Resmî mutasyon.py KURALLAR/mutantlar üreteci aynen3safgörevde uygulandı:30üretilen,30FAIL,0PASS,0timeout. Gerçek medya deneyi mekanik mutasyon tekrarlarına dahil edilmedi.
- Boş/sabit cevap RET. İçerikten güven yükseltme,kaynak kontrolünü kaldırma,keywordblock ile meşru arşivi reddetme3/3RET. Referans importu/attribute/getattr/inspect+exec4/4RET. Importedmodule namespace yaması ayrıca RET. Bu retlerde kabultruekanıt yok.
- Kaynak koruması ai_lab.kod_denetimi(...,izin=()) ve ders içi importednamespace/__globals__ ASTkontrolüdür. Bütün saf eq/raises sonuçları kabulall(checks)'e katılır; ön koşul hatasında gerçek kabul yazılmaz. Bu bütün Python programlarının genel güvenlik sandbox'ı olduğu iddiası değildir.
- Yerel OCR imageyokluğunda FAIL,kabultrueyok,otomatikpull yok. İzole boş HFcache ile ASRmodelyokluğunda FAIL,kabultrueyok; gerçekleşmiş OCR çağrıları partialkabulfalse receipt'inde korunur ve kendi konteynerleri kapanır. Kurulumlar/cache silinmedi.
- UI Check70/70gerçekkabul. UI starterRET. Run gerçek medya/dosya deneyi yaptı; görünür fixturekopyası değiştirilip okundu, çıktı gerçek+deterministikreplay ayrımını ve kabulfalse durumunu gösterdi. ScreenshotDesktop/pafta-ai38-ui-kabul-20261104.png.
- Hedefli regresyon: eski ai-savunma11/12 ve ai-saldiri32'nin model çalıştırmayan21kontrolü geçti. Önceki Dalga3işinde49/51/47'nin21safkontrolü de geçmişti. Sınav testi12/12OK. BütünAIyolunun ağır model deneylerinin yeniden koşulduğu iddia edilmez.

## Kaynak ve kanıt dosyaları
tracks/ai-savunma/lessons/ai-savunma-38-multimodal-ocr-asr-guardrail.md; sandbox/ai_gercek_ai_savunma_38.py; fixtures/ai-savunma-38. Track kaydı Araç ve Yürütme Bekçisi'nde12'den sonra; mevcut sıra/diğer ajan dersleri korunur. Motorai-gercek,gereksinimtorch mevcut.ai-venv seçimi içindir; gerçek araçlar OCR+WhisperCPU'dur. Ortak engine/runner değiştirilmedi. Daha önce web/app.js'teki tek rozet satırında iki statik metin düzeltildi; çalışma davranışı değişmedi.

outputs/yeni-ai-savunma-38/teslim.json güncel kaynakSHA256listesi ve CLI/UI/Runreceiptyollarıdır. Aynı klasörde reference-final.json,negatif/kopya/yama/missing-dependency sonuçları,pure-mutations.json,regresyon-pure.json,ocr-no-pull.json vardır. PNG/WAV ve8akışın dosyaları receipt.media altında korunur. Yeni makinede OCRimage ve kurulum kimlik kaydı,yerelWhispersmall,Pythonortamı veWindowsEnglishSAPI sesi gerekir; yokluk PASS sayılmaz. Bu Windows laptop dışında masaüstü/Linux/macOS kabulü yapılmadı.

Denetim ve puan Opus'tadır. Bu teslim Dalga3'ün yalnız Codex'e atanan3dersini tamamlar; diğer yazarın4başlığı ve geniş Purple/klasik planlar bitmiş değildir. Commit/push yok.


## Ham UTF-8 arşiv düzeltmesi — 2026-11-04
Son kontrolde Windows write_text satır sonu dönüşümünün dosya baytlarını değiştirebileceği görüldü. Arşiv artık write_bytes kullanıyor; doğrulama read_bytes ile tam UTF-8 eşitliği ve SHA256 kontrol ediyor. Güncel gerçek CLI referansı 70/70 ve ders ekranı tekrar 70/70 geçti; her iki koşunun sekiz arşivinde ham bayt/hash eşitliği ayrıca doğrulandı. Önceki kabul yalnız normalize metin eşitliğini kontrol ediyordu. Yeni kanıt yolları teslim.json içindedir. Puan verilmedi, Opus denetimi bekliyor.
