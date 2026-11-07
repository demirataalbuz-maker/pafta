# Yeni ders ai-guvence-39 — yazar kontrolleri tamam, denetime hazır

Yazar: claude-yazar. Görev kaynağı: panodaki 07.11.2026 notu, plan `docs/ai-gercek/ML-MATEMATIK-PLAN.md`. Bu rapor yazarın kendi kontrolleridir; puan verilmedi, bağımsız denetim değildir.

## Dosyalar
- `tracks/ai-guvence/lessons/ai-guvence-39-uyelik-cikarimi-istatistigi-lira-ve-guven-araligi.md` (sha256 7e0381a7d69f7080…)
- `sandbox/ai_gercek_ai_guvence_39.py` (c294f924e1407d05…)
- `tracks/ai-guvence/fixtures/ai-guvence-39/` (README + sentetik veri)
- `outputs/yeni-ai-guvence-39/gorunur-run-1.json` (hata vitrini), `ai-guvence-39-kabul-1794053421537.json` (son gerçek kabul kanıtı)
- `tracks/ai-guvence/track.json`: yalnız yeni "Uygulamalı ML Matematiği" modülü. engine/, web/, `sandbox/ai_gercek_lab.py` değişmedi. Kurulum/indirme yok; commit/push yok.

## İçerik
logit güven, Gaussian likelihood ratio, Clopper-Pearson, shadow modeller. 3 görev + gerçek deney, her görevde kusurlu başlangıç kodu, tahmin adımı, hata vitrini, kanıt okutma soruları, Sınır.

## Gerçek final (son kabul koşusu)
Cihaz: cuda. Eğitim/test 1.000/0.727; kayıp eşiği AUC 0.642, TPR 0.062 [0.041,0.091]; LiRA tarzı AUC 0.770, TPR 0.268 [0.225,0.314].
Derste koşuya özgü başarı oranı iddiası yoktur; bu sayılar yalnız bu koşunundur.

## Kendi kontrollerim
- `tools/validate.py ai-guvence-39`: TEMİZ, 9 kontrol (1 tahmin, 4 çözüm, 4 başlangıç); art arda 2 ek koşuda da TEMİZ.
- `docs/denetim/araclar/tahmin.py`: 0 şüpheli.
- `kirp_gercek.py` + `mutasyon.py`: toplam/geçen 45/3 (log oranda sadeleşen 2π, kökte erişilmez eşitlik, 50→51 adım: eşdeğer).
- Elle anlamsal mutant (toplam/geçen): 15/0 (görev adımı ve gerçek adım).
- Kopya sondası 7/7 reddedildi (takma ad, from-import, importlib, __import__+vars, inspect+exec, * import, eval).
- Arayüz: Ders ekranında 11 adımın hepsi açıldı; bozuk tablo ve işaretleme kalıntısı yok. Görev 1'de Çalıştır görünür `veri/*.json` dosyasını okudu. Gerçek adımda kusurlu başlangıç kodu 10/13 ile reddedildi, gerçek deney koşmadı (3.4 sn). 2 denemeden sonra çözüm açıldı; Çalıştır gerçek çıktıyı bastı ve run kanıtı yazdı (17.0 sn); Kontrol 20/20 ONAYLANDI, kabul kanıtı yazıldı (14.9 sn). Konsolda çalışma zamanı hatası yok.
- Regresyon: `tools/validate.py --yol ai-guvence`: 40 ders, 362 kontrol, 361 geçti. Tek sorun modül dışı `ai-guvence-28:8`: bu adım varsayılan `opt_in=false` ile tasarım gereği PASS vermez, onay açılmadı ve ders değişmedi. `tools/test_ai_gercek.py guvence`: referans PASS, 6 yanlış çözüm reddedildi (`outputs/ai-gercek-kabul-20261107-151117.json`). Diğer pilotlar ve altyapı senaryoları koşulmadı; engine/, web/ ve ortak lab değişmedi.

## Bilinen sınırlar
Küçük model ve tek koşu; `Sınır` adımındaki cümle geçerlidir.
