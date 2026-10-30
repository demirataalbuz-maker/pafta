# ai-guvence-20 iyileştirme teslimi

Düzelten codex; claude-opus denetimi bekleniyor. Puan verilmedi.

Değişenler: ders markdown ve tracks/ai-guvence/fixtures/ai-guvence-20/{README.md,veri/model_cifti.json,veri/iddia_esikleri.json}. Tablo+NOT, veri kökeni/kalıcılık, mevcut hazirla/setup ile aynı dosyayı okuyan üç görev, kusurlu çalışan başlangıçlar ve 489 kelime ek anlatım eklendi. İlk anlatımdaki model eğitilmez çelişkisi düzeltildi. Gerçek deney standart 35/gürültülü 8 epoch kullanır: farkın yalnız gürültüye nedensel bağlanamayacağı açıklandı. Bu sınırlama deney davranışını değiştirmeden belirtildi.

Gerçek test bütün modül ref* adlarını ve kanit_yaz kullanımını kod_denetimi ile, ImportFrom takma ad/yıldız kullanımını ek AST denetimiyle reddeder. Mevcut tüm sözleşme/canlı/mutant kontrolleri checks listesinde; kanıt kabul=all(checks). Ortak deney/engine/web değişmedi.

## Dört kontrol

- validate.py ai-guvence-20: TEMİZ, 9 kontrol (1 tahmin, 4 çözüm, 4 başlangıç); gerçek CPU eğitimleri dahil. PAFTA_DATA=Desktop/pafta-iyilestirme-20-kanit.
- tahmin.py . ai-guvence-20: 1 tahmin, 0 şüpheli.
- kirp_gercek.py Desktop/pafta-mutasyon-g20-20261030-0910; mutasyon.py <kopya> --en-cok 1000 ai-guvence-20: 9+23+33=65 mutant, 0 geçen.
- kopya_sonda.py ai-guvence ai-guvence-20 "from sandbox.ai_gercek_ai_guvence_17_20 import ref20 as olc": fail, korunuyor. outputs/iyilestirme-codex-ai-guvence-20/kopya-sonucu.json hedeflenen guard ret mesajını ve kabul kanıtı yokluğunu kaydeder.

Komutlar .ai-venv/Scripts/python.exe -X utf8 ile çalıştırıldı. Kendi 18800 UI sunucusunda görev 1 Çalıştır iki görünür JSON kaydını okudu/yazdırdı; gerçek görev 9 Kontrol 7/7 geçti, GERÇEK ÇAĞRI/kabul edildi. Kanıt outputs/codex-guvence-bos-20261029/ui-data/ai-kanit/guvence-20-cpu-1793338784411.json. İlk üç görevin tamamına ayrı UI kabulü yapılmadı; CLI validate hepsini sınadı. Kurulum/indirme/commit/push yok; A notunu denetçi verir.
