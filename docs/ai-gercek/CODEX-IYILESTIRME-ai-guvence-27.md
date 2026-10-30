# ai-guvence-27 iyileştirme teslimi

Düzelten: codex. Puan verilmedi; claude-opus denetimi bekleniyor.

Değişenler: ders markdown dosyası, tracks/ai-guvence/fixtures/ai-guvence-27/README.md, veri/eval_kayitlari.json ve veri/esikler.json. Mevcut ai_guvence_veri.hazirla kullanıldı; engine/web/laboratuvar deney davranışı değiştirilmedi. İlk tablo ve köken/kalıcılık notu, derin anlatım, dosya okuyan üç kusurlu başlangıç ve çözümleri eklendi. İlk anlatımdaki gerçek deney çelişkisi düzeltildi. Gerçek testte tüm üç *_ref ve kanit_yaz engelleniyor; ImportFrom takma adları ve yıldız import ayrıca denetleniyor. Bu koruma genel amaçlı güvenli Python sandbox iddiası değildir.

## Zorunlu kontroller

- .ai-venv/Scripts/python.exe -X utf8 tools/validate.py ai-guvence-27: TEMİZ; 1 ders 9 kontrol (tahmin 1, solution 4, starter 4). Gerçek CPU eğitimi dahil.
- .ai-venv/Scripts/python.exe -X utf8 docs/denetim/araclar/tahmin.py . ai-guvence-27: 1 tahmin, 0 şüpheli.
- kirp_gercek.py ile ayrı Desktop/pafta-mutasyon-g27-20261030-0825 kopyası; mutasyon.py <kopya> --en-cok 1000 ai-guvence-27: görevlerde 10+20+30=60 mutant, 0 geçen.
- kopya_sonda.py ai-guvence ai-guvence-27 "from sandbox.ai_gercek_ai_guvence_27 import temperature_ref as sicaklik_sec, score_ref as acik_eval_skoru": fail, korunuyor. Tam sonuç outputs/iyilestirme-codex-ai-guvence-27/kopya-sonucu.json; hedeflenen koruma mesajı ve kabul kanıtı yokluğu ayrıca doğrulandı.

İzole PAFTA_DATA: Desktop/pafta-iyilestirme-27-kanit (validate), Desktop/pafta-iyilestirme-27-kopya (sonda). Validate gerçek kanıtı: guvence-27-1793337263468.json.

## Ders ekranı

Kendi 18800 test sunucusunda görev 1 Çalıştır: görünür JSON içindeki altı kayıt gerçekten okundu ve çıktılandı. Gerçek görev 9 Kontrol: 2/2 geçti, GERÇEK ÇAĞRI/kabul edildi; kanıt outputs/codex-guvence-bos-20261029/ui-data/ai-kanit/guvence-27-1793337409076.json. Yeni ilk üç görevin tümünün ayrı UI kabulü yapılmadı; tamamı CLI validate içinde sınandı. Mevcut üst düzey genel AI gerçek deney rozeti motoru nitelendirir; bu derste açıklanan giriş verileri sentetiktir.

Yeni kurulum/indirme, commit/push yok. Dersin A notunu aldığı iddia edilmez; kararı denetçi verir.
