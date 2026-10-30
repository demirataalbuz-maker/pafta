# ai-guvence-30 iyileştirme teslimi

Düzelten codex; claude-opus denetimi bekleniyor. Puan verilmedi.

Ders markdown ve tracks/ai-guvence/fixtures/ai-guvence-30/{README.md,veri/purple_kayitlari.json,veri/yayin_esikleri.json} değişti. İlk tablo+NOT, köken/kalıcılık, aynı dosyayı okuyan üç görev (mevcut hazirla/setup), üç kusurlu çalışan başlangıç ve 464 kelime ek anlatım eklendi. İlk anlatımın gerçek PyTorch/FGSM çelişkisi düzeltildi. Sentetik hash biçimi ile gerçek dosya hash'i, model doğruluğu ile dosya yazma kapısı/kapsama, yerel paket durumu ile bilimsel yayın kabulü açıkça ayrıldı. Olumsuz savunma sonucu saklanmıyor.

Gerçek test attack_ref/policy_ref/report_ref/kanit_yaz kullanımını kod_denetimi ve ImportFrom takma ad/yıldız kontrolüyle reddeder. Kanıt kabul=all(kontroller.values()). Ortak engine/web ve gerçek deney modülü değişmedi.

Dört kontrol (.ai-venv/Scripts/python.exe -X utf8): validate.py ai-guvence-30 TEMİZ, 9 kontrol (1 tahmin, 4 çözüm, 4 başlangıç), gerçek üç eğitim/FGSM/dosya etkisi/ZIP dahil; tahmin.py . ai-guvence-30 1 tahmin, 0 şüpheli; kirp_gercek.py Desktop/pafta-mutasyon-g30-20261030-1010 ve mutasyon.py <kopya> --en-cok 1000 ai-guvence-30 22+36+51=109 mutant, 0 geçen; kopya_sonda.py ai-guvence ai-guvence-30 "from sandbox.ai_gercek_ai_guvence_30 import policy_ref as yayin_politikasi, report_ref as purple_gercek_ozet" fail, korunuyor. Hedeflenen ret mesajı ve kanıt yokluğu outputs/iyilestirme-codex-ai-guvence-30/kopya-sonucu.json içinde ayrıca doğrulandı. PAFTA_DATA=Desktop/pafta-iyilestirme-30-kanit ve -30-kopya.

Kendi 18800 UI test sunucusunda görev 1 Çalıştır görünür sekiz JSON kaydını okudu/yazdırdı; gerçek görev 9 Kontrol 4/4 geçti, GERÇEK ÇAĞRI/kabul edildi. Kanıt outputs/codex-guvence-bos-20261029/ui-data/ai-kanit/guvence-30-1793340100682.json. İlk üç görevin tümüne ayrı UI kabulü yapılmadı; CLI validate hepsini sınadı. Ağda yayın, yeni kurulum/indirme, commit/push yok. A notunu denetçi verir.
