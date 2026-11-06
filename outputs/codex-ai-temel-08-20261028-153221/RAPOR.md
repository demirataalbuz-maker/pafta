# ai-temel-08 · Gerçek KV cache · Codex kendi kabul raporu

Ders ortak takip aracıyla Codex adına alındı. Mevcut adımların sonuna gerçek anlatım ve görev eklendi. Ortak engine/web/laboratuvar dosyaları değiştirilmedi. İndirme, kurulum, commit ve push yapılmadı.

## Gerçek ölçüm

Yerel SmolLM2-135M gerçek cache nesnesiyle prefill + devam işlemi yapıldı. Cache uzunluğu devamdan önce ve sonra ölçüldü. Cache'li son logitler aynı girdinin cache'siz tam ileri hesabıyla karşılaştırıldı. Forward pre-hook, önek ve kalan tokenların doğru cache uzunluğuyla modele gittiğini doğruladı. Deney CPU'da, HF_HUB_OFFLINE ve TRANSFORMERS_OFFLINE etkin şekilde çalıştı.

Çok kiracılı sunucu yalıtımı, continuous batching, GPU bellek veya hızlanma kabulü yapılmadı. Bu alanlar bu dersin yeni göreviyle tamamlanmış sayılmaz. Mevcut deterministik kiracı görevleri korundu.

## Kabul

- Referans çözüm PASS; kaynak=gercek, kabul=true kanıtı.
- Starter, boş kod, sabit cevap, cache'i yok sayma, ilk konum logitleri ve öneki yeniden cache'e ekleme: tümü FAIL ile reddedildi.
- İç testte altı mutant reddedildi. Gerçek cache 2–24 tokenlık kısa girdilerde bağımsız tam hesapla karşılaştırıldı; tolerans 1e-3.
- Çalıştır modu OK.
- Ayrı ilerleme verisiyle gerçek Pafta ekranında Kontrol Et: 8/8 kontrol geçti; GERÇEK ÇAĞRI / kabul edildi. Ekran: ai-temel-08-ekran.png.
- AI Temel regresyonu: 18 mevcut ders / 142 kontrol; 18 tahmin, 62 çözüm ve 62 starter geçti. Altı yazılmamış ders açık kaldı. Sonuç, yolun bu koşu anındaki hâline aittir; Claude aynı yolda eşzamanlı çalışıyor.
- Ham koşucu JSON dosyaları, gerçek kanıt arşivi ve validate-ai-temel.log bu klasörde.

Kendi kabulüdür, bağımsız denetim değildir. Son durum denetime-hazir; bitti yalnız bağımsız denetimden sonra işaretlenmeli. Mutantlar belirli hata örnekleridir, keyfi öğrenci koduna karşı tam güvenlik sınırı değildir.