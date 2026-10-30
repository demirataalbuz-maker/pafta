# Codex — Güvence 21–25 devir kaydı

Yalnız atanmış 109–113 kutuları. Durum: uygulama ve CLI kabulü tamam; ders ekranı Kontrol/Çalıştır kabulünü ana ajan yapacak. UI yapılmadan denetime-hazır değildir. Ortak engine/web davranışı değiştirilmedi; kurulum/indirme/commit/push yok. CPU; GPU/Ollama kullanılmadı.

Her derse eski görevlerin sonuna anlat + motor:ai-gercek görev eklendi. Görünür sentetik ayar: web/data/ai-guvence-N-deney.txt. Kalıcı ayrı kopya: PAFTA_DATA/calisma/ai-guvence-N/ayar.json; göreli PAFTA_DATA proje köküne göre çözülür; yalnız exclusive create ile yoksa oluşturulur. Çalıştır tam yolu ve içeriği gösterir; metin editöründe düzenlenir. Kontrol ayrı seedlerle geçici veri kullanır.

21 gerçek autograd ağırlık/veri/torch-sürüm dosyalarını öğrenci fonksiyonuyla hashler; dosyayı değiştirdikten sonra hash/boyut farkını doğrular, kök dışına erişimi reddeder. Lisans/provenance taraması değildir.
22 safetensors gerçek kitaplıkla yüklenir; inert pickle yalnız pickletools ile incelenir (unpickle yok). GGUF v3 yalnız başlık örneğidir, GGUF inference yok. Template politika kontrolü tam enjeksiyon tarayıcısı değildir.
23 autograd eğitilmiş modelin ağırlıklarına öğrenci simetrik fake-quant/dequant işlevi 2/4/8 bit uygulanır. Gerçek eşli tahmin/logit/regresyon ölçümü; hız/bellek veya LLM güvencesi yok.
24 gerçek özellik-tetikleyicili model eğitilir; ayrı temiz fine-tune verisiyle güncellenir. Sabit ayrı değerlendirme örneklerinin temiz/tetikli ve yakın tetik tahminleri, iki fazdaki ağırlık hashleri ölçülür. Küçük sınıflandırıcıdır; LLM sleeper-agent replikasyonu değildir. ASR/kalıcılık yüksek olma şartı yok.
25 kendi safetensors artefaktının hash/kaynak/biçim/sürüm kapısı gerçek yükleme ve inference etkisini belirler. Bilinmeyen dosya veya Python kodu yüklenmez. İkinci iç kapı yalnız kendi ürettiği bilinen baytlara izin verir. İmza/uzak provenance doğrulaması veya tam sandbox değildir.

Çalışan kabul komutu: python -X utf8 outputs/codex-guvence-21-25-20261029/test_acceptance.py (proje içinde kaydedildi). Çıktılar acceptance.json ve gN-*.json. Her ders referans/başlangıç/boş/sabit/3 anlamlı mutant/eksik ortam/Run/kalıcılık. Tam sonuçlar aşağıdadır.


## Son CLI kabulü — tamam, UI ana ajanda

Her dersin gerçek görevi **0 tabanlı 7** (ekrandaki 8. adım), önceki yeni anlat 6. adımdır. READY.json beş dersin tamamını listeler. Bu rapor uygulayıcı kabulüdür, bağımsız denetim değildir.

CLI: **50/50 beklenen sonuç** (her ders 10/10): referans gerçek kanıtla PASS; starter/boş/sabit/3 anlamlı mutant FAIL; olmayan PAFTA_AI_PYTHON → BağımlılıkEksik; Run gerçek kanıtla başarılı ve kabul:false; farklı cwd/yeni süreçte göreli PAFTA_DATA öğrenci kopyası aynı proje kökünde ve düzenleme korunuyor.

Ek olarak **5/5 düzenlenmiş Run**: öğrenci kopyasında seed=1234+dersNo ve adim=31 yapıldı; gerçek eğitim kanıtındaki seed/adim değişti, dosya baytları korunuyor. **5/5 HTTP**: ana ajanın 18800 sunucusunda /data/ai-guvence-N-deney.txt baytları görünür kaynakla aynı. Bunlar UI Kontrol/Çalıştır kabulü değildir.

Son regresyon: **5 ders, 45 kontrol TEMİZ**; 5 tahmin,20 çözüm,20 starter. tools/validate.py bütün eski ve yeni adımları sınadı. İlk regresyonun 25’teki Windows dosya paylaşımı OSError kaydı validate.log içinde korunur. Neden: load_file ile eşlenmiş adayı aynı yolda yeniden yazmak. Düzeltme: her vaka ayrı safetensors dosyası; son regresyon validate-final.log temiz. Ortak koşucu değiştirilmedi.

Gerçek ölçümler: 23’te iki görülmemiş seed için 2/4/8 bit eşli regresyon sayıları [1,0,0] ve [5,1,0] (256 örnek). 24’te iki görülmemiş seedin önce/sonra tetik hedef oranları 1.0→1.0 ve 0.979167→0.979167; temiz doğruluk sayıları 96→96 ve93→94 /96. Saldırı başarısı kabul şartı yapılmadı. Gerçek model loss izleri, logitler, ham ölçüm girdileri, ağırlık hashleri ve sürümler kanıtta.

22: her seedde 9 biçim/template vakası, tek gerçek safetensors yüklemesi; pickle sadece inert dict opcode incelemesi, yüklenme0. GGUF inference yapılmadı. 25: her seedde 6 kapı vakası; yalnız sağlam aday gerçek inference ve yükleme marker dosyası oluşturdu. Hash/kaynak/biçim/sürüm bozulanlar ve eksik manifesto reddedildi. Kaynak allowlist sentetik yerel politikasını ölçer.

Starter ve çözümde aynı ai_lab.CALISTIR/goster kancası her beş derste Library üzerinden doğrulandı. Öğrenci yalnız istenen işlevleri uygular; kanca Run deneyini başlatır. Parent17–20 kanca düzeltmesi bu dilimi etkilemez.

### Tekrar çalıştırma ve kanıt dizini

- python -X utf8 outputs/codex-guvence-21-25-20261029/test_acceptance.py
- python -X utf8 outputs/codex-guvence-21-25-20261029/check_edited_run.py
- python -X utf8 tools/validate.py ai-guvence-21 ai-guvence-22 ai-guvence-23 ai-guvence-24 ai-guvence-25 (PAFTA_DATA kendi çıktına ayarlanır)

İlk ana kabul aynı kaynaklı Desktop/test_guvence_21_25.py ile çalıştı; proje içindeki test_acceptance.py göreli ROOT kullanan tekrar çalıştırılabilir kopyasıdır. check_edited_run.py ilk testten sonra çalışır; yalnız kendi cli-data kopyasını değiştirir. Kullanıcı UI çalışma dosyalarına dokunmaz.

acceptance.json tüm test sonuçlarını; gN-reference.json kabul kanıt yolunu; gN-run.json ve gN-run-edited.json Run sonuçlarını; edited-run-and-visible.json HTTP/öğrenci düzenleme kanıtını; evidence-index.json gerçek JSON kanıtların tam yollarını taşır. PAFTA_DATA/ai-kanit dosyaları korunur. Kontrol temp ağırlıkları temizlenir; giriş/logit/hash/loss kanıtı kalır, Run ağırlıkları ayrı kalıcı deney klasörlerinde tutulur.

### Değişen ders kaynakları

- tracks\ai-guvence\lessons\ai-guvence-21-model-ve-veri-sbom-envanteri.md
- sandbox/ai_gercek_ai_guvence_21.py
- web/data/ai-guvence-21-deney.txt
- tracks\ai-guvence\lessons\ai-guvence-22-pickle-safetensors-gguf-ve-chat-template-riskleri.md
- sandbox/ai_gercek_ai_guvence_22.py
- web/data/ai-guvence-22-deney.txt
- tracks\ai-guvence\lessons\ai-guvence-23-quantization-kaynakli-guvenlik-regresyonu.md
- sandbox/ai_gercek_ai_guvence_23.py
- web/data/ai-guvence-23-deney.txt
- tracks\ai-guvence\lessons\ai-guvence-24-sleeper-agent-ve-model-agirligi-backdoor-olcumu.md
- sandbox/ai_gercek_ai_guvence_24.py
- web/data/ai-guvence-24-deney.txt
- tracks\ai-guvence\lessons\ai-guvence-25-yerel-model-tedarik-zinciri-degerlendirmesi.md
- sandbox/ai_gercek_ai_guvence_25.py
- web/data/ai-guvence-25-deney.txt

Ayrıca yalnız bu rapor, CODEX-GUVENCE-21-25-READY.json ve outputs/codex-guvence-21-25-20261029/* kabul dosyaları/testleri. Pano/tracker yalnız resmi araçlarıyla güncellendi. Başka ders, ortak engine/web davranışı, kurulum, indirme, GPU, commit/push veya başka kullanıcı sohbeti yok.

### Kalan kabul

Tarayıcı/Windows UI eylemi yapılmadı: kullanıcı talimatıyla ana ajan yapacak. Her ders için 18800 üzerinde #/ders/ai-guvence/ai-guvence-N/7 yolunda iki başlangıç Kontrolü; sonra Çözümü göster, Kontrol ve Çalıştır. Görünür /data dosyasını ve Run’da yazılan öğrenci dosyası yolunu incele. UI geçmeden denetime-hazır yazılmadı. Ana ajan daha önce UI’ı tamamladıysa mevcut tracker durumu geri alınmaz. İkinci cihaz ve bağımsız denetim bu raporun kapsamında tamamlanmadı.
