# ai-temel-12 · Gerçek uyarlama sonrası regresyon · Codex kendi kabul raporu

Ders ortak takip aracından Codex adına alındı. Mevcut adımlar korunarak yalnız bu dersin sonuna gerçek anlatım ve görev eklendi. Yeni derse özel yardımcı sandbox/ai_gercek_ai_temel_12.py, ders 11 yardımcısını salt okunur yeniden kullanır. Ortak engine/web/ai_gercek_lab dosyaları değişmedi. Kurulum/indirme, commit ve push yapılmadı.

## Gerçek deney

SmolLM2-135M gerçek ileri hesaplarından alınan dondurulmuş taban üzerinde token-bias SGD eğitimi yapıldı. Aynı tabandan olumlu kontrol ve ilk kritik vaka için bilerek bozulmuş uyarlayıcı üretildi. Öğrenci modelleri no_grad içinde tekrar çağırıp aynı vakalardaki gerçek iki-token softmax olasılıklarını, oranları, kritik regresyonları ve yayın kapısını hesapladı. Hazır sonuç bool listesi verilmedi. Model çağrı hookları ve ağırlık değişmezliği doğrulandı.

Karar uzayı her vakada iki sentetik etikete karşılık gelen gerçek tokenla sınırlıdır. Bu gerçek bir hesap/eğitim deneyi olsa da serbest metin jailbreak/sızıntı, tam LM fine-tuning, Promptfoo/garak veya genel güvenlik benchmarkı kabulü değildir. Yayın kapısı yalnız deney sonucudur; üretime dağıtım yapılmadı.

## Sonuçlar

- Referans PASS; kaynak=gercek, kabul=true kanıtı.
- Starter, boş kod, sabit rapor, her zaman yayınla, her zaman engelle, kritik regresyonu gizleme ve yanlış eşik eşitliği: tümü FAIL olarak reddedildi.
- İç testte yedi mutant reddedildi. Olumlu/bozuk/geri-kazanım, eşik sınırı, ters vaka sırası, NaN/sonsuz/bool eşikler ve modellerin değerlendirmede değişmezliği sınandı.
- Olumlu kontrol: 3/3 güvenli, yayın True. Kontrollü bozulma: 2/3 güvenli, sentetik-1 kritik regresyon, yayın False. Geri kazanım: 3/3 ve yayın True. Bunlar sentetik karar uzayının koşu sonuçlarıdır.
- Çalıştır modu OK.
- Ayrı test ilerlemesiyle gerçek Pafta ekranında Kontrol Et: 10/10 kontrol geçti, GERÇEK ÇAĞRI / kabul edildi. Ekran: ai-temel-12-ekran.png.
- AI Temel regresyonu: 18 mevcut ders / 150 kontrol; 18 tahmin, 66 çözüm ve 66 starter geçti. Altı yazılmamış ders açık kaldı. Rapor eşzamanlı geliştirilen yolun bu koşu anındaki hâline aittir.
- Ham JSON, gerçek kanıt arşivi ve validate-ai-temel.log bu klasörde. HF_HUB_OFFLINE ve TRANSFORMERS_OFFLINE etkindi.

Kendi kabulüdür; bağımsız denetim değildir. Ders denetime-hazir yapılır; bitti yalnız bağımsız denetçiye bırakılır. Mutantlar belirli hata örneklerini sınar; keyfi öğrenci koduna karşı tam güvenlik sınırı değildir. Kullanıcının servislerine ve diğer ajanın doğrulama süreçlerine dokunulmadı.