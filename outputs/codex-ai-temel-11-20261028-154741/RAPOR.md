# ai-temel-11 · Gerçek LM tabanlı token-bias DPO · Codex kendi kabul raporu

Ders ortak takip aracından Codex adına alındı. Mevcut adımlar korunarak ders sonuna gerçek anlatım ve görev eklendi. Derse özel yeni yardımcı sandbox/ai_gercek_ai_temel_11.py kullanılır. Ortak engine/web/ai_gercek_lab dosyaları değişmedi. Kurulum, indirme, commit ve push yapılmadı.

## Gerçek ölçüm ve sınır

Kurulu SmolLM2-135M, her Kontrol koşusunda üç sentetik/rastgele kimlikli istemle gerçekten ileri hesaplandı. Son-konum tüm sözlük logitleri dondurulmuş taban olarak aynı eğitim koşusunda önbelleklendi. Gerçek tek-token chosen/rejected tamamlamalarla yalnız ek token_bias parametresi gerçek autograd+SGD ile eğitildi. DPO kaybı, beta, referans düzeltmesi, gradyan ve optimizer adımları bağımsız analitik oracle ve hooklar ile doğrulandı.

Bu tek-token additive output-bias DPO deneyidir. Bütün dil modeli ağırlıkları fine-tuning, çok-token yanıt eğitimi, TRL çalışması veya güvenlik/hizalama başarısı kabulü değildir. Taban logitler fixture değildir: gerçek model girdileri, ağırlık özeti ve gerçek logit SHA-256 özetleri kanıtta bulunur. Kalıcı model dosyası değiştirilmedi.

## Sonuçlar

- Referans PASS; kaynak=gercek, kabul=true kanıtı.
- Starter, boş kod, sabit rapor, referans düzeltmesi yok, beta yok, tercih yönü ters ve backward yok: tümü FAIL ile reddedildi.
- İç testte altı mutant reddedildi. NaN/sonsuz/bool beta ve geçersiz adımlarda politika değişmeden hata vermesi sınandı.
- Çalıştır modu OK.
- beta=1.4, lr=0.08, üç adım örnek koşusunda kayıp 0.693147 → 0.667355 → 0.642893; son tercih marjları yaklaşık 0.109100. Bu sayılar tek koşunun kanıtıdır, sabit test beklentisi değildir.
- Gerçek Pafta ekranında ayrı ilerleme verisiyle Kontrol Et: 8/8 kontrol geçti; GERÇEK ÇAĞRI / kabul edildi. Ekran: ai-temel-11-ekran.png.
- AI Temel regresyonu: 18 mevcut ders / 148 kontrol; 18 tahmin, 65 çözüm ve 65 starter geçti. Altı yazılmamış ders açık kaldı. Rapor eşzamanlı geliştirilen yolun bu koşu anındaki hâline aittir.
- Ham JSON, gerçek kanıt arşivi ve validate-ai-temel.log bu klasörde. HF_HUB_OFFLINE ve TRANSFORMERS_OFFLINE testlerde etkindi.

Kendi kabulüdür; bağımsız denetim değildir. Ders denetime-hazir yapılır; bitti kararı bağımsız denetçiye bırakılır. Mutantlar belirli hata örneklerini kapsar; keyfi öğrenci koduna karşı tam güvenlik sınırı iddiası yoktur.