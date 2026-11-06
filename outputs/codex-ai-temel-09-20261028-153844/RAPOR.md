# ai-temel-09 · Gerçek torch eğitim döngüsü · Codex kendi kabul raporu

Ders ortak takip aracından alındı. Önceki adımlar korunarak yalnız bu dersin sonuna gerçek anlatım ve görev eklendi. Ortak engine/web/laboratuvar dosyaları değişmedi. Yeni kurulum/indirme, commit ve push yapılmadı.

## Gerçek ölçüm

CPU float64 Linear(2,1,bias=True), gerçek MSE backward ve gerçek torch.optim.SGD. Parametre gradient hookları her adımın autograd gradyanlarını, optimizer step-post-hook gerçek güncellemeleri saydı. Modelin yerinde değişen ağırlıkları, autograd veya optimizer kullanmayan bağımsız analitik MSE gradyan hesabıyla karşılaştırıldı. Veri 3/5/6 sentetik örnek; 1/3/5 adım ve farklı öğrenme oranları. Veri tohumu ve girdiler kanıta kaydedildi.

Bu sentetik regresyon üzerinde gerçek eğitimdir; dil modeli fine-tuning, genelleme, güvenlik başarısı veya TensorBoard kabulü değildir.

## Sonuçlar

- Referans çözüm PASS; kaynak=gercek, kabul=true kanıtı.
- Starter, boş kod, sabit rapor, zero_grad atlama, ortalama yerine toplam kayıp, backward atlama ve optimizer.step atlama: tümü FAIL olarak reddedildi.
- İçeride yedi mutant reddedildi. Geçersiz adımda modelin değişmediği de sınandı.
- Çalıştır modu OK.
- Ayrı test ilerleme diziniyle gerçek Pafta ekranında Kontrol Et: 9/9 kontrol geçti; GERÇEK ÇAĞRI / kabul edildi. Ekran: ai-temel-09-ekran.png.
- AI Temel regresyonu: 18 mevcut ders / 144 kontrol; 18 tahmin, 63 çözüm, 63 starter geçti. Altı yazılmamış ders açık kaldı. Sonuç eşzamanlı geliştirilen yolun bu test anındaki hâline aittir.
- Ham JSON, gerçek kanıt arşivi ve validate-ai-temel.log bu klasörde. Testler çevrimdışı ortam bayraklarıyla çalıştı; hazır dil modeli yüklenmedi veya indirilmedi.

Kendi kabulüdür; bağımsız denetim değildir. Ders denetime-hazir; bitti yalnız bağımsız denetimden sonra. Mutantlar belirli hata örneklerini kapsar; keyfi öğrenci koduna karşı tam güvenlik sınırı değildir.