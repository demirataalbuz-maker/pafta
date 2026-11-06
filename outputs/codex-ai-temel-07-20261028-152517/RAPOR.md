# ai-temel-07 · Gerçek kısa bağlam ve konum deneyi · Codex kendi kabulü

Ders takip aracıyla Codex tarafından alındı. Mevcut adımlar korunarak yalnız bu dersin sonuna anlatım ve gerçek görev eklendi. Ortak engine/web/laboratuvar dosyaları değiştirilmedi. Yeni indirme/kurulum, commit ve push yapılmadı.

## Gerçek ölçüm

Kurulu SmolLM2-135M tokenizer ve CPU üzerinde gerçek model ileri hesabı kullanıldı. Gerçek max_position_embeddings değeri raporlandı. Metnin son 1–32 tokenı ve 0..N-1 position_ids modele gönderildi; son konumun logit özeti bağımsız gerçek ileri hesapla karşılaştırıldı. Forward pre-hook, modele giden gerçek kimlikleri, konumları ve use_cache=False ayarını doğruladı.

Bu deney tam context kapasitesi, uzun bağlam kalitesi veya sohbet talimatlarının korunması için kabul değildir. Önceki öğretim sinüs tablosunun gerçek modelin konum algoritması olduğu iddia edilmez.

## Kabul sonuçları

- Referans çözüm PASS ve kaynak=gercek, kabul=true kanıtı.
- Starter, boş kod, sabit boş rapor, ilk tokenları koruma, ters sıra, ilk-konum logitleri, sıfır konumlar: tümü FAIL ile reddedildi.
- İç testte boş/eksik işlev, boş sözlük, sabit gerçek sonuç ve dört anlamlı mutant (toplam yedi) reddedildi.
- Çalıştır modu OK.
- Gerçek Pafta ders ekranında ayrı ilerleme verisiyle Kontrol Et: 11/11 kontrol geçti, GERÇEK ÇAĞRI / kabul edildi. Ekran kanıtı: ai-temel-07-ekran.png.
- AI Temel regresyonu: 18 mevcut ders, 140 kontrol; 18 tahmin, 61 çözüm, 61 starter geçti. Altı yazılmamış ders açık bırakıldı. Sonuç, eşzamanlı geliştirilen yolun bu koşu anındaki hâline aittir.
- Ham negatif/pozitif koşucu çıktıları JSON dosyalarında; validate-ai-temel.log regresyon kaydıdır. Testler HF_HUB_OFFLINE ve TRANSFORMERS_OFFLINE etkin biçimde çalıştı.

Kendi kabulüdür; bağımsız denetim değildir. Ders denetime-hazir yapılır. Keyfi öğrenci koduna karşı tam güvenlik sınırı veya bütün AI derslerinin gerçek kabulü iddia edilmez. Yalnız bu test için açılan sunucu kapatılır; kullanıcının Ollama/WSL/Docker süreçlerine dokunulmaz.