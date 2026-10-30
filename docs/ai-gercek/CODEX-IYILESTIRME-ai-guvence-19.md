# ai-guvence-19 iyileştirme teslimi

Düzelten codex; claude-opus denetimi bekleniyor. Puan verilmedi.

Değişenler: ders markdown ve tracks/ai-guvence/fixtures/ai-guvence-19/{README.md,veri/dp_kayitlari.json,veri/politika.json}. Tablo+NOT, köken/kalıcılık ayrımı, mevcut hazirla/setup ile dosyayı okuyan üç görev, üç kusurlu çalışan başlangıç ve 459 kelime ek anlatım eklendi. Model eğitilmez çelişkisi ve epsilon/delta açıklaması düzeltildi. Sentetik σC kaydı ile gerçek ortalama gradyan σ2C/n mekanizması ayrıldı. Bun/Steinke birincil kaynak önermeleri 1.3/1.6 ve bileşim okunarak mevcut hesabın dayanağı doğrulandı: https://arxiv.org/html/1605.02065v1 . Açık seed ve ham izlerin üretim gizlilik yayını olmadığı vurgulandı.

Gerçek test, modüldeki bütün ref* işlevler ve kanit_yaz için kod_denetimi + ImportFrom takma ad/yıldız kontrolünü kullanır. Bütün eski sözleşme/canlı ölçüm/mutant kontrolleri checks içine kaydedilir; kanıt kabul=all(checks). Ortak deney/engine/web davranışı değişmedi.

## Dört kontrol

- validate.py ai-guvence-19: TEMİZ, 9 kontrol (1 tahmin, 4 çözüm, 4 başlangıç), gerçek autograd/optimizer dahil; PAFTA_DATA=Desktop/pafta-iyilestirme-19-kanit.
- tahmin.py . ai-guvence-19: 1 tahmin, 0 şüpheli.
- kirp_gercek.py Desktop/pafta-mutasyon-g19-20261030-0900; mutasyon.py <kopya> --en-cok 1000 ai-guvence-19: 21+27+44=92 mutant, 0 geçen. Son değişiklik yalnız anlatımda gürültü ölçeği cümlesiydi, görev kodları aynı.
- kopya_sonda.py ai-guvence ai-guvence-19 "from sandbox.ai_gercek_ai_guvence_17_20 import ref19clip as olc, ref19budget as butce": fail, korunuyor. outputs/iyilestirme-codex-ai-guvence-19/kopya-sonucu.json; hedeflenen guard ret mesajı ve kabul kanıtı yokluğu ayrıca doğrulandı.

Komutlar .ai-venv/Scripts/python.exe -X utf8 ile koşuldu. UI: kendi 18800 test sunucusunda görev 1 Çalıştır görünür beş JSON kaydını okudu/yazdırdı. Gerçek görev 9 Kontrol 7/7 geçti, GERÇEK ÇAĞRI/kabul edildi; kanıt outputs/codex-guvence-bos-20261029/ui-data/ai-kanit/guvence-19-cpu-1793338540787.json. İlk üç görevin tümü ayrı UI kabulü yapılmadı, CLI validate hepsini sınadı. Kurulum/indirme/commit/push yok; A notunu denetçi verir.
