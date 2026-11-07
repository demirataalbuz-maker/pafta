# Yeni ders ai-guvence-37 — yazar kontrolleri tamam, denetime hazır

Yazar: claude-yazar. Görev kaynağı: panodaki 07.11.2026 notu, plan `docs/ai-gercek/ML-MATEMATIK-PLAN.md`. Bu rapor yazarın kendi kontrolleridir; puan verilmedi, bağımsız denetim değildir.

## Dosyalar
- `tracks/ai-guvence/lessons/ai-guvence-37-gcg-lite-birinci-derece-tahmin.md` (sha256 0a9b5c37992feeaa…)
- `sandbox/ai_gercek_ai_guvence_37.py` (a78a7e1c3f44ba18…)
- `tracks/ai-guvence/fixtures/ai-guvence-37/` (README + sentetik veri)
- `outputs/yeni-ai-guvence-37/gorunur-run-1.json` (hata vitrini), `ai-guvence-37-kabul-1794053401649.json` (son gerçek kabul kanıtı)
- `tracks/ai-guvence/track.json`: yalnız yeni "Uygulamalı ML Matematiği" modülü. engine/, web/, `sandbox/ai_gercek_lab.py` değişmedi. Kurulum/indirme yok; commit/push yok.

## İçerik
one-hot gradient, Spearman, top-k, aynı bütçede gradient/rastgele. 3 görev + gerçek deney, her görevde kusurlu başlangıç kodu, tahmin adımı, hata vitrini, kanıt okutma soruları, Sınır.

## Gerçek final (son kabul koşusu)
Cihaz: cuda. Spearman (yansız, rastgele adaylar): 0.278, 0.340, 0.168, -0.081; aynı 384 sorguda son kayıp gradyan 2.927, rastgele 3.725.
Derste koşuya özgü başarı oranı iddiası yoktur; bu sayılar yalnız bu koşunundur.

## Kendi kontrollerim
- `tools/validate.py ai-guvence-37`: TEMİZ, 9 kontrol (1 tahmin, 4 çözüm, 4 başlangıç); art arda 2 ek koşuda da TEMİZ.
- `docs/denetim/araclar/tahmin.py`: 0 şüpheli.
- `kirp_gercek.py` + `mutasyon.py`: toplam/geçen 47/2 (Spearman sıra ölçeği ve kayması: Pearson'a etkisiz, eşdeğer).
- Elle anlamsal mutant (toplam/geçen): 18/0 (görev adımı ve gerçek adım).
- Kopya sondası 7/7 reddedildi (takma ad, from-import, importlib, __import__+vars, inspect+exec, * import, eval).
- Arayüz: Ders ekranında 11 adımın hepsi açıldı; bozuk tablo ve işaretleme kalıntısı yok. Görev 1'de Çalıştır görünür `veri/*.json` dosyasını okudu. Gerçek adımda kusurlu başlangıç kodu 10/13 ile reddedildi, gerçek deney koşmadı (1.6 sn). 2 denemeden sonra çözüm açıldı; Çalıştır gerçek çıktıyı bastı ve run kanıtı yazdı (18.2 sn); Kontrol 20/20 ONAYLANDI, kabul kanıtı yazıldı (18.1 sn). Konsolda çalışma zamanı hatası yok.
- Regresyon: `tools/validate.py --yol ai-guvence`: 40 ders, 362 kontrol, 361 geçti. Tek sorun modül dışı `ai-guvence-28:8`: bu adım varsayılan `opt_in=false` ile tasarım gereği PASS vermez, onay açılmadı ve ders değişmedi. `tools/test_ai_gercek.py guvence`: referans PASS, 6 yanlış çözüm reddedildi (`outputs/ai-gercek-kabul-20261107-151117.json`). Diğer pilotlar ve altyapı senaryoları koşulmadı; engine/, web/ ve ortak lab değişmedi.

## Bilinen sınırlar
Küçük model ve tek koşu; `Sınır` adımındaki cümle geçerlidir.
