# ai-guvence-17 iyileştirme teslimi

Düzelten codex; claude-opus denetimi bekleniyor. Puan verilmedi.

Değişenler: ders markdown dosyası ve tracks/ai-guvence/fixtures/ai-guvence-17/{README.md,veri/uyelik_kayitlari.json,veri/esikler.json}. Tablo+NOT, köken ve geçici/kalıcı kopya ayrımı, dosya okuyan üç görev, üç kusurlu çalışan başlangıç ve 484 kelime ek anlatım uygulandı. İlk anlatımdaki hedef model yok çelişkisi düzeltildi. Kopya koruması ref17/ref18/ref19clip/ref19budget/ref20/kanit_yaz ve ImportFrom takma ad/yıldız importlarını reddeder. Bütün mevcut gerçek/sözleşme/mutant kontrolleri checks içine kaydedilir; kanıt yalnız kabul=all(checks). Ortak engine/web/deney modülü değişmedi.

## Dört kontrol

- .ai-venv/Scripts/python.exe -X utf8 tools/validate.py ai-guvence-17: TEMİZ; 9 kontrol (1 tahmin, 4 çözüm, 4 başlangıç), gerçek shadow/hedef CPU eğitimi dahil. PAFTA_DATA=Desktop/pafta-iyilestirme-17-kanit.
- .ai-venv/Scripts/python.exe -X utf8 docs/denetim/araclar/tahmin.py . ai-guvence-17: 1 tahmin, 0 şüpheli.
- kirp_gercek.py Desktop/pafta-mutasyon-g17-20261030-0850; mutasyon.py <kopya> --en-cok 1000 ai-guvence-17: 6+38+37=81 mutant, 0 geçen.
- kopya_sonda.py ai-guvence ai-guvence-17 "from sandbox.ai_gercek_ai_guvence_17_20 import ref17 as olc": fail, korunuyor. outputs/iyilestirme-codex-ai-guvence-17/kopya-sonucu.json; hedeflenen koruma mesajı ve kabul kanıtı yokluğu ayrıca doğrulandı.

## Ders ekranı

Kendi 18800 test sunucusunda görev 1 Çalıştır görünür JSON'u gerçekten okudu ve kusurlu artan sıralamayı yazdırdı. Gerçek görev 9 Kontrol 7/7 geçti, GERÇEK ÇAĞRI/kabul edildi. Kanıt outputs/codex-guvence-bos-20261029/ui-data/ai-kanit/guvence-17-cpu-1793338276683.json. İlk üç görevin tümü ayrı UI kabulü yapılmadı; tamamı CLI validate içinde sınandı. Kurulum/indirme/commit/push yok. Bağımsız kabul ve puanı denetçi verir.
