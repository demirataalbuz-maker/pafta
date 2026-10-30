# ai-guvence-18 iyileştirme teslimi

Düzelten codex; claude-opus denetimi bekleniyor. Puan verilmedi.

Değişenler: tracks/ai-guvence/lessons/ai-guvence-18-asiri-ogrenme-ile-gizlilik-riski-iliskisi.md ve tracks/ai-guvence/fixtures/ai-guvence-18/{README.md,veri/deney_kayitlari.json,veri/esikler.json}. İlk tablo ve NOT köken/kalıcılık ayrımını açıklıyor; ilk üç görev aynı görünür dosyayı setup/hazirla ile okuyup sonuç yazdırıyor. Üç boş başlangıç yerine kusuru yorumla açıklanmış çalışan kod var. Ek anlatım 484 kelime; mevcut açıklamalar da korunuyor. İlk anlatımdaki model eğitilmez çelişkisi düzeltildi. Ortak deney modülü, engine/web değiştirilmedi; yeni kurulum/indirme/commit/push yok.

Gerçek test: modüldeki ref17/ref18/ref19clip/ref19budget/ref20 ve kanit_yaz için kod_denetimi; ImportFrom takma ad/yıldız kontrolü. Kopya çözüm guard içinde ok(False) ve stop() ile reddediliyor. Bütün mevcut sözleşme, canlı ölçüm ve mutant kontrolleri checks içinde toplanıyor; kanıt yalnız kabul=all(checks). Deney davranışı aynı.

## Dört zorunlu kontrol

- .ai-venv/Scripts/python.exe -X utf8 tools/validate.py ai-guvence-18: TEMİZ, 9 kontrol (1 tahmin, 4 çözüm, 4 başlangıç). Gerçek CPU eğitimi dahil. PAFTA_DATA=Desktop/pafta-iyilestirme-18-kanit.
- .ai-venv/Scripts/python.exe -X utf8 docs/denetim/araclar/tahmin.py . ai-guvence-18: 1 tahmin, 0 şüpheli.
- kirp_gercek.py Desktop/pafta-mutasyon-g18-20261030-0830; mutasyon.py <kopya> --en-cok 1000 ai-guvence-18: görevlerde 12+18+28=58 mutant, 0 geçen. Son düzeltme yalnız çıkarılan gerçek test bloğundaki import satırıydı; üç sentetik görevin son hali aynı.
- kopya_sonda.py ai-guvence ai-guvence-18 "from sandbox.ai_gercek_ai_guvence_17_20 import ref18 as olc": fail, korunuyor. outputs/iyilestirme-codex-ai-guvence-18/kopya-sonucu.json, ayrıca hedeflenen koruma mesajı ve kanıt yokluğu doğrulandı. Sözdizimi hatasından kaynaklanan önceki ret kabul sayılmadı; düzeltmeden sonra yeniden koşuldu.

## Ders ekranı

Kendi 18800 test sunucusunda görev 1 Çalıştır görünür dosyadaki üç kaydı okudu/yazdırdı. Gerçek görev 9 Kontrol 9/9 geçti; GERÇEK ÇAĞRI/kabul edildi. Kanıt: outputs/codex-guvence-bos-20261029/ui-data/ai-kanit/guvence-18-cpu-1793337756903.json. Yeni ilk üç görevin tamamı ayrı UI kabulü yapılmadı; CLI validate hepsini sınadı. Puan veya bağımsız kabul iddiası yok.
