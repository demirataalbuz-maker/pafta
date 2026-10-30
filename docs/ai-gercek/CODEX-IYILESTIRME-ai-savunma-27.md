# ai-savunma-27 iyileştirme teslimi

Codex uygulama ve kendi kontrollerini yaptı; puan ve bağımsız denetim claude-opus'a ait. Referans görsel kabulü açık eksiktir; aşağıda sınırı yazılıdır.

Değişenler: tracks\ai-savunma\lessons\ai-savunma-27-garak-ile-yerel-model-guvenlik-taramasi.md, tracks/ai-savunma/fixtures/ai-savunma-27/README.md ve veri/bulgular.json, sandbox/ai_gercek_ai_savunma_27.py, yeni sandbox/ai_savunma_garak_worker.py. Mevcut ai_savunma_veri helper'ı yeniden kullanıldı; engine/web ve araç kurulumu değiştirilmedi.

İş emrinin tüm içerik maddeleri: girişteki araç çalışmaz çelişkisi giderildi, ilk tablo + NOT eklendi, yaklaşık803 sözcük anlatım ile API akışı/detector anlamı/ölçüm tuzakları ve risk sınırı açıklandı. İlk üç görev aynı görünür sentetik bulgu dosyasını okur: doğrulama, probe özeti, çift bazında risk. Setup mevcut hazirla ile geçici kopya üretir; kalıcılık olmadığı açık yazılır. Gizli testler ayrı girdilerdir. Starter1 şemayı doğrulamak yerine skor/denemeyi sessizce düzeltir, starter2 ağırlıksız ortalama alır, starter3 gruplamaz ve eşik eşitliklerini yanlış yorumlar. Üçü çalışır ama Check'te reddedilir.

Asıl kapsam düzeltmesi: eski kendi yazılmış doğrudan sohbet döngüsü yerine kurulu garak0.17.1'in gerçek Python API zinciri kullanılır: Probe.probe → OllamaGeneratorChat → StringDetector.detect. İki özel Pafta probe'u eski dersin beş istemini korur (3+2); hazır garak katalog probeları veya tüm katalog koşulmuş sayılmaz. Generator ve Detector sınıfları kurulu garak'tandır, model bağlantısını kendi benzerimiz taklit etmez. Worker ayrı .ai-araclar yorumlayıcısında, kendi geçici XDG yapılandırma/veri/cache dizinlerinde çalışır. Model/araç/veri indirmez, HF çevrimdışı ortamıyla koşar. PAFTA_GARAK_PYTHON yalnız mevcut yorumlayıcı seçimi için desteklenir, cihaz yolu ders kodunda yoktur.

Özel ders detector adı garak.canary, gerçek sınıf garak.detectors.base.StringDetector'e eşlenir; bu ayrım anlatımda ve kanıtta yer alır. Skor alt dizge eşleşmesidir, anlamsal jailbreak hakemi değildir. Gerçek garak detector'üne verilen pozitif/negatif sentetik çıktı kontrolü [1,0] üretir; bu kontrol gerçek model çağrısı diye sayılmaz. Beş gerçek Attempt ayrı kaydedilir. Ham istemler, yanıtlar, detector skorları, garak JSONL kayıtları, araç sürümü, model kimliği, ayarlar ve temizlik kanıtta bulunur. JSONL probe tarafından yazılan ilk Attempt ve detector eklenmiş son kopyayı içerir; aynı uuid'nin iki satırı iki model çağrısı değildir. Beş çağrı ayrı satirlar listesinde sayılır.

Son test mevcut kod_denetimi korumasını referans/ozet/kanit_yaz ve takma ad/yıldız importu ile güçlendirir; ihlalde stop. Saf sözleşme hatasında gerçek deney/kanıt yazılmaz. Üçüncü temel görevin bütün eşik/şema testleri ve mutantları final testine de taşındı. Gerçek rapor modüldeki referansla karşılaştırılır; beş dolu, hatasız yanıt, araç exit0, pozitif/negatif detector kontrolü ve geçici kaynak kapanışı zorunludur. Kabul bütün kontrollerin all sonucudur. Saldırının sızıntı üretmesi kabul şartı değildir. Eşiklerin önerileri ders politikasıdır, genel yayın güvenliği kararı değildir.

Dört zorunlu kontrol (.ai-venv/Scripts/python.exe -X utf8):
- tools/validate.py ai-savunma-27: son koşu TEMİZ9; tahmin1 çözüm4 starter4. İzole PAFTA_DATA Desktop/pafta-v27-kabul-20261030.
- docs/denetim/araclar/tahmin.py . ai-savunma-27: bir tahmin, sıfır şüpheli.
- kirp_gercek.py Desktop/pafta-mutasyon-v27-20261030 (önce hedef yokluğu kontrol edildi); kopyadaki mutasyon.py <kopya> --en-cok1000 ai-savunma-27: 9+9+16=34 mutant, sıfır geçen. Kırpılmış ders son kaynağın değişmeyen önekiyle eşleşir; sonraki final-test iyileştirmesi temel görevleri değiştirmedi.
- kopya_sonda.py ai-savunma ai-savunma-27 "from sandbox.ai_gercek_ai_savunma_27 import referans as garak_risk_raporu": fail korunuyor. kopya.json hedef guard mesajını ve ai_kanit boşluğunu ayrıca doğrular.

Ek olumsuz kanıtlar outputs/iyilestirme-codex-ai-savunma-27: bos.json, sabit.json, yanlis-esik.json ve eksik-arac.json hepsi fail, kabul yok. Araç yokluğu yalnız kendi süreç ortamındaki olmayan PAFTA_GARAK_PYTHON ile sınandı. gorunur-dosya-run-1/2/3.json normal runner/setup üzerinden sentetik dosyayı gösterir, status ok.

Gerçek CLI kanıtı Desktop/pafta-v27-kabul-20261030/ai-kanit/savunma-garak-1793364689303.json: garak0.17.1, beş gerçek yanıt, iki özel probe, iki skor da0.0 ve riskler dusuk; gerçek StringDetector pozitif/negatif kontrolü [1,0]; geçici dizin temizlendi, yalnız bizim yüklediğimiz model boşaltıldı. Bu dar koşuda sızıntı görülmedi; genel güvenlik veya tüm garak kataloğu için sonuç değildir. Ham yanıtlar kanıtta saklıdır.

Ön denemeler gizlenmedi: prototipte garak Attempt için prompt zorunluluğu TypeError üretti; worker sanity kontrolünde Conversation/Turn prompt eklenerek düzeltildi. Sonraki validate URLError timeout ile kaldı ve kabul sayılmadı. Mutasyon yükü bittikten sonraki gerçek son koşu geçti; zaman aşımının kök nedeni veya genel kararlılık çözülmüş iddiası yok. ilk-basarisiz-denemeler.txt kaydı korur, ilk kaynak yedekleri outputs içindedir.

Kendi127.0.0.1:18800 sunucumda normal token/Origin HTTP kabulü http-check.json: pass12/12 ve gerçek kabul; http-run.json: ok ve gerçek kabul=false, ham garak yanıtları gösterildi. CLI/HTTP görsel kabul yerine sayılmaz.

Görsel sınır: ders ekranı açıldı, başlangıç Check4/5 fail ve 'Gerçek deney kanıtı yok' görüldü. Çözümü göster tıklaması önceki dersteki gibi tarayıcı kontrolünde zaman aşımı üretti; diyalog API'si pencere bildirmedi. Ayrı yeni sekmede doğrudan editörle denemek için açılan sayfa başlıkta kaldı; editör yüklenmedi, hata konsolunda kayıt yoktu. Referans görsel Check/Run ve görünür dosya görsel kabulü tamamlanmadı, PASS sayılmadı. Opus'a açık kabul eksikliğidir. Genel web/engine değişikliğine girilmedi.

Yalnız kendi18800 test sunucum kapatıldı; kullanıcının Ollama sunucusu, önceden yüklü modeli, WSL veya Docker kapatılmadı. Yeni indirme/kurulum, commit/push veya puan yazımı yok.
