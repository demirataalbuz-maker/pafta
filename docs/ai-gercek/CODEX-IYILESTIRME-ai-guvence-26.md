# ai-guvence-26 iyileştirme teslimi

Düzelten codex; claude-opus denetimi bekleniyor. Puan verilmedi.

Ders markdown dosyası ve tracks/ai-guvence/fixtures/ai-guvence-26/{README.md,veri/replikasyon_kayitlari.json,veri/esikler.json} değişti. İlk tablo+NOT veri kökenini ve iki ayrı kalıcılık davranışını açıklıyor. İlk üç görev aynı görünür JSON'u mevcut ai_guvence_veri.hazirla/setup ile okuyor ve sonuç yazdırıyor. Boş başlangıçlar yerine şema kontrolünü atlayan, farkın işaretini ters hesaplayan ve tam eşikte alarm veren kusurlu çalışan kodlar eklendi. Ek anlatım 477 kelime; yöntem replikasyonu ile kaynak makale skorunun birebir tekrarının farkı açık. İlk anlatımın gerçek deney çelişkisi düzeltildi.

Gerçek test kod_denetimi ile attack_ref/ozet_ref/kanit_yaz kullanımını ve ek AST kontrolüyle ImportFrom takma ad/yıldız importu reddediyor; kanıt kabul=all(kontroller.values()). Deney modülü, engine/web, gerçek eğitim/FGSM davranışı değiştirilmedi.

## Dört zorunlu kontrol

- .ai-venv/Scripts/python.exe -X utf8 tools/validate.py ai-guvence-26: TEMİZ, 9 kontrol (1 tahmin, 4 çözüm, 4 başlangıç), gerçek CPU/autograd dahil. PAFTA_DATA=Desktop/pafta-iyilestirme-26-kanit.
- .ai-venv/Scripts/python.exe -X utf8 docs/denetim/araclar/tahmin.py . ai-guvence-26: 1 tahmin, 0 şüpheli.
- kirp_gercek.py Desktop/pafta-mutasyon-g26-20261030-0840; mutasyon.py <kopya> --en-cok 1000 ai-guvence-26: 32+39+47=118 mutant, 0 geçen.
- kopya_sonda.py ai-guvence ai-guvence-26 "from sandbox.ai_gercek_ai_guvence_26 import attack_ref as fgsm_replika, ozet_ref as replika_ozeti": fail, korunuyor. outputs/iyilestirme-codex-ai-guvence-26/kopya-sonucu.json içinde hedeflenen ret mesajı ve kabul kanıtı yokluğu ayrıca doğrulandı.

## Ders ekranı

Kendi 18800 test sunucusunda görev 1 Çalıştır görünür dosyadaki altı kaydı okudu/yazdırdı. Gerçek görev 9 Kontrol 3/3 geçti, GERÇEK ÇAĞRI/kabul edildi. Kanıt outputs/codex-guvence-bos-20261029/ui-data/ai-kanit/guvence-26-1793337999257.json. Yeni ilk üç görevin tümünün ayrı UI kabulü yapılmadı; tamamı CLI validate içinde sınandı. Yeni indirme/kurulum/commit/push yok. A notunu denetçi verir.
