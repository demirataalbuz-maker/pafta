# Dalga3 — Codex'in üç yeni AI dersi

2026-11-04. Yazım ve yazarın kendi doğrulamaları tamamlandı. Üç ders Opus denetimine teslim edildi/ediliyor; puan verilmedi. Bu rapor bütün AI müfredatının veya geniş Purple/klasik planların tamamlandığı anlamına gelmez.

| Ders | Konu | Gerçek ders ekranı | Saf görev mutantları |
|---|---|---:|---:|
| ai-saldiri-53 | VLM pixel perturbation |67/67|40/40reddedildi|
| ai-saldiri-54 | Güvenlik ML dedektöründe bütçeli black-box evasion |65/65|40/40reddedildi|
| ai-savunma-38 | Gerçek OCR/ASR provenance ve araç etkisi koruması |70/70|30/30reddedildi|

110mekanikmutantın tamamı FAIL oldu; timeout veya altyapı hatası ret diye sayılmadı. Her gerçek finalde boş/sabit cevap,üç anlamlı yanlış,dört oraclekopyası ve ayrıca labmodule namespace yaması reddedildi. PGD için inputmutasyonu da ayrıca sınandı. EksikVLM,eksikOCRimage ve eksikASRcache durumları PASS alamadı. Gerçek kabul receipts kaynak=gercek/kabul=true; Run aynı gerçek araçları çalıştırdı ama kabul=false kaldı. Fixture dosyaları açıkça sentetik,gerçek çağrıdan ayrıdır.

## Gerçek bulgular
AI54,48train/12test sentetik metinle gerçekten sklearn1.9.1modeli fit eder. Arama query96,ayrı değerlendirme72,ikinci model karşılaştırması24olarak kaydedildi. Bu dar veri/modeldeQ1ASR0,Q3/Q4ASR1;meşru kontrolde false-positive0. Gerçek e-posta ürünü başarısı veya genel evasion garantisi değildir.

AI53,pretrained SmolVLM'nin görüntüden gerçek autograd gradientini alır; ağırlıklar donuktur. İki görsel×epsilon0/attack×3adım=12geri geçiş. PNG dosyası yazılır,tekrar okunur ve yeniden VLM'ye verilir. Epsilon0PNG'leri byteolarakaynı;attackgirdileribütçeiçinde. Bu koşuda iki next-token tercihinden1/2değişti;serbest üretilmiş yanıt/jailbreak değil. PyTorch peakallocatedyaklaşık2.23GB;toplamVRAM değildir. Tek seferlik ilk fullvocabulary sondasının yanıltıcı sonucu da kabulfalse olarak hata vitrininde saklandı.

AI38,ikiPNG'den gerçek Tesseract OCR ve ikiSAPIWAV'dan gerçek Whisper ASR üretir. Araç önerisi dar deterministik replay'dir,LLMplannerperformansı diye sunulmaz. Sekiz gerçek dosya akışında korumasız saldırı kontrolü4etki,outbox+silme;korumalıyetkisizetki0,doğruhamarşiv4. Yetki medya içindeki SYSTEM/USER yazısından değil host bağlamından gelir. Dış e-posta gönderilmedi;canary ve bütün dosyalar sentetiktir.

## Kullanıcı onayıyla kurulanlar
- Resmî HuggingFaceTB/SmolVLM-256M-Instruct,rev7e3e67edbbed1bf9888184d9df282b700a323964,Apache2.0.13dosya517.903.046bayt. ModelSHA25674dea5904032e5ae99a2e0eef5179e6ac0f1dedc3ab0c7c2a5d4d387c843203e. .depsaltında,sabitrevizyon/yerelonly;dosyaboyutlarıveupstreamLFSsha doğrulandı. Yeni Pythonpaketi veya imaj indirilmedi.
- Resmî Debian tesseract-ocr5.3.0-2,English/osdvekitaplıklar. Paket/index39.756.840bayt,ekDockerkatmanı128.336.723bayt. Mevcutbase'denayrıpafta-ocr38:tesseract-5.3.0-2,sha256d54c568dc43a4add16eb38cd9e6c1187a1904192bd14170ae9f5bb3790e45ed9. Yeni baseimage veyaWindows/Pythonkurulumu yok.100MBindirmebütçesi paketkurulmadanönce denetlendi. APT doğrulaması,paket/sürüm listesi ve runtimebinarySHA saklandı.

Whisper-small,Pillow,sklearn,torch/transformers veWindowsEnglishSAPI sesi zaten kuruluydu. Yeni ASR modeli veya ses indirilmedi. Ücretli API/abonelik/cloud hesabı açılmadı. Yalnız kendi OCR CID'leri ve kendi test sunucuları kapatıldı; kullanıcı Ollama/WSL/Docker Desktop/Samba süreçleri ve önceden yüklenmiş modeller yönetilmedi. Kanıt dosyaları/görseller/sesler korundu; öğrenci verileri veya kurulumlar silinmedi.

## Dosya değişiklikleri
Yeni3lessonMD,3sandboxmodülü,3fixtureklasörü(ornekJSON/README;AI54'tecorpusJSONda). İlgili iki track.json'a yalnız yeniID'ler eklendi; mevcut derslerin göreli sırası/diğer yazarın dosyaları korundu. Her dersin ayrıntılı dosyaSHA256listesi outputs/yeni-<ID>/teslim.json içinde.

tools/ai_yeni_dersler.py,kalıcı atamaJSON'u ve HTMLşablonu ders_ideşlemesini destekler. Yeni plan7→AI53,plan8→AI54,savunma7→AI38;durum/denetimgerçekID'nin tracker/kuyruğundan okunur.37planbaşlığı değişmedi,aynıdersiki kez sayılmadı. Yeni ajan rehberine bu eşleme ve yeniIDrezervasyonunun nasıl yapılacağı yazıldı. Kopya/yama koruması yalnız ders testlerinde;ortak ai_lab/engine/runner davranışı değiştirilmedi. web/app.js'te yalnız1satırdaki2sabit rozetmetni düzeltildi: Pythonortamı ve canlıölçüm doğru adlandırılıyor.

## Test komutları ve kapsam
python -X utf8 tools/validate.py ai-saldiri-53
python -X utf8 tools/validate.py ai-saldiri-54
python -X utf8 tools/validate.py ai-savunma-38

Her biri1ders9kontrol TEMİZ(4solution4starter1tahmin). Tahmin yardımcı aracı her derste1tahmin0şüpheli verdi. Resmîmutasyonüreteci değiştirilmeden yalnızsafgörevlerde110mutasyon;gerçek final için ayrıyanlış/kopya/bağımlılıkyok denemeleri. Bütün başarılar gerçek test dosyalarında,özet outputs/dalga3-codex-kabul/ozet.json içinde.

Hedefli eski ders regresyonu:47/49/51veSavunma11/12/Saldırı32'nin toplam42modelçalıştırmayankontrolü geçti. python -X utf8 tools/test_sinav.py →12testOK. Bütün müfredatın ağır model deneyleri yeniden koşulmadı. İkinci masaüstü/Linux/macOS kabulü yapılmadı;yalnızbulaptopta çalıştırıldı.

## Denetim ve kalanlar
Her dersin detaylı raporu docs/ai-gercek/CODEX-YENI-<ID>.md,ham çıktılar/receipts outputs/yeni-<ID>altında. Screenshot'lar Desktop/pafta-ai53-ui-kabul-20261103.png,pafta-ai54-ui-kabul-20261103.png,pafta-ai38-ui-kabul-20261104.png. Gerçek medya dosyalarının yolu ilgili receipt'te.

Opus henüz bu üç derse puan vermedi. Dalga3'ün diğer dört başlığı (deepfake/sesklonlamatespiti,watermark/C2PA,unlearning,SOC/AI–Purpleköprüsü) mevcut atama kaydında claude-yazar'da; onlara dokunulmadı. Geniş Purple/klasik modüller açık. Commit/push yapılmadı.


## Ham UTF-8 arşiv düzeltmesi — 2026-11-04
Son kontrolde Windows write_text satır sonu dönüşümünün dosya baytlarını değiştirebileceği görüldü. Arşiv artık write_bytes kullanıyor; doğrulama read_bytes ile tam UTF-8 eşitliği ve SHA256 kontrol ediyor. Güncel gerçek CLI referansı 70/70 ve ders ekranı tekrar 70/70 geçti; her iki koşunun sekiz arşivinde ham bayt/hash eşitliği ayrıca doğrulandı. Önceki kabul yalnız normalize metin eşitliğini kontrol ediyordu. Yeni kanıt yolları teslim.json içindedir. Puan verilmedi, Opus denetimi bekliyor.


## Daha sonraki kullanıcı devri
2026-11-04: Kullanıcı kalan yazılmamış AI derslerini Codex yazsın dedi. SOC köprüsü19 ve unlearning39 artık yazılıp Opus denetimine teslim edildi. C2PA ve ses tespiti için ayrı yeni indirme onayları bekleniyor; henüz yazılmadı. Güncel kaynak CODEX-KALAN-AI-20261104.md; yukarıdaki dörtbaşlıkClaude-yazar notu ilk teslimin tarihsel durumudur.
