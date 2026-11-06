# ai-temel-01 · Codex uygulama ve kendi kabul raporu

Bu rapor bağımsız denetim değildir. Ders takip aracıyla Codex adına alındı. Yalnız bu dersin sonuna gerçek anlatım ve görev eklendi; ortak engine/web/laboratuvar dosyaları değiştirilmedi. İndirme, kurulum, commit ve push yapılmadı.

## Gerçek işlem

Kurulu SmolLM2-135M tokenizer; kimlikler, sözlük tokenları, Unicode karakter ofsetleri ve tam decode. Ortak dil_modeli yardımcısı ağırlıkları da yükler; görev model ileri hesabı veya sohbet üretimi iddia etmez. Model/tokenizer yalnız yerel önbellekten kullanıldı. HF_HUB_OFFLINE ve TRANSFORMERS_OFFLINE testlerde etkin.

## Kabul

- Koşucu referans çözümü: PASS ve kaynak=gercek, kabul=true kanıtı.
- Starter, boş kod, sabit sonuç, strip, karakter sayımı, ters token sırası ve kaymış ofset: tümü FAIL ile reddedildi.
- Test içindeki yedi mutant reddedildi; Unicode, emoji, boş metin, boşluk, yeni satır ve rastgele metinler sınandı.
- Çalıştır modu: OK.
- AI Temel regresyonu: 18 mevcut ders, 130 kontrol; 18 tahmin, 56 çözüm ve 56 starter geçti, TEMİZ. Altı yazılmamış ders hâlâ eksik ve tamamlandı sayılmadı.
- Ayrı test ilerleme diziniyle gerçek Pafta ders ekranında referans kodu girilip Kontrol Et tıklandı: 21/21 KONTROL GEÇTİ; GERÇEK ÇAĞRI / kabul edildi.
- Ekran kanıtı: ai-temel-01-ekran.png. Ham koşucu sonuçları aynı klasördeki JSON dosyalarında; regresyon validate-ai-temel.log içinde.

## Sınırlar

Mutasyonlar anlamlı hata örneklerini ölçer; keyfi kötü amaçlı öğrenci koduna karşı tam güvenlik sınırı veya kapsamlı mutasyon ispatı değildir. Bu dersin tokenizasyon kabulüdür; diğer AI derslerinin gerçek kabulü değildir. Son durum denetime-hazir; bitti yalnız bağımsız denetimden sonra yazılmalı.