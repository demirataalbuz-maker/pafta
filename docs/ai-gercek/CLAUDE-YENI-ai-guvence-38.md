# Yeni ders ai-guvence-38 — yazar kontrolleri tamam, denetime hazır

Yazar: claude-yazar. Görev kaynağı: panodaki 07.11.2026 notu, plan `docs/ai-gercek/ML-MATEMATIK-PLAN.md`. Bu rapor yazarın kendi kontrolleridir; puan verilmedi, bağımsız denetim değildir.

## Dosyalar
- `tracks/ai-guvence/lessons/ai-guvence-38-embedding-geometrisi-pca-ve-hubness.md` (sha256 c6a4ca3d8584bed0…)
- `sandbox/ai_gercek_ai_guvence_38.py` (b7c714c7714b9326…)
- `tracks/ai-guvence/fixtures/ai-guvence-38/` (README + sentetik veri)
- `outputs/yeni-ai-guvence-38/gorunur-run-1.json` (hata vitrini), `ai-guvence-38-kabul-1794053409465.json` (son gerçek kabul kanıtı)
- `tracks/ai-guvence/track.json`: yalnız yeni "Uygulamalı ML Matematiği" modülü. engine/, web/, `sandbox/ai_gercek_lab.py` değişmedi. Kurulum/indirme yok; commit/push yok.

## İçerik
kosinüs kimliği, merkezli güç iterasyonu, hubness, Gaussian taban. 3 görev + gerçek deney, her görevde kusurlu başlangıç kodu, tahmin adımı, hata vitrini, kanıt okutma soruları, Sınır.

## Gerçek final (son kabul koşusu)
Cihaz: {'kip': 'gpu', 'gpu_kilit_bekleme_sn': 0.0}. Kosinüs ort.: ayni_konu_farkli_kalip=0.660, ayni_kalip_farkli_konu=0.806, farkli=0.574; %90 varyans bileşeni minilm 20, gaussian 88; kontrast 1.51/0.14; çarpıklık 0.93/0.12.
Derste koşuya özgü başarı oranı iddiası yoktur; bu sayılar yalnız bu koşunundur.

## Kendi kontrollerim
- `tools/validate.py ai-guvence-38`: TEMİZ, 9 kontrol (1 tahmin, 4 çözüm, 4 başlangıç); art arda 2 ek koşuda da TEMİZ.
- `docs/denetim/araclar/tahmin.py`: 0 şüpheli.
- `kirp_gercek.py` + `mutasyon.py`: toplam/geçen 46/0.
- Elle anlamsal mutant (toplam/geçen): 18/0 (görev adımı ve gerçek adım).
- Kopya sondası 7/7 reddedildi (takma ad, from-import, importlib, __import__+vars, inspect+exec, * import, eval).
- Arayüz: Ders ekranında 11 adımın hepsi açıldı; bozuk tablo ve işaretleme kalıntısı yok. Görev 1'de Çalıştır görünür `veri/*.json` dosyasını okudu. Gerçek adımda kusurlu başlangıç kodu 10/13 ile reddedildi, gerçek deney koşmadı (1.3 sn). 2 denemeden sonra çözüm açıldı; Çalıştır gerçek çıktıyı bastı ve run kanıtı yazdı (7.9 sn); Kontrol 20/20 ONAYLANDI, kabul kanıtı yazıldı (9.4 sn). Konsolda çalışma zamanı hatası yok.
- Regresyon: `tools/validate.py --yol ai-guvence`: 40 ders, 362 kontrol, 361 geçti. Tek sorun modül dışı `ai-guvence-28:8`: bu adım varsayılan `opt_in=false` ile tasarım gereği PASS vermez, onay açılmadı ve ders değişmedi. `tools/test_ai_gercek.py guvence`: referans PASS, 6 yanlış çözüm reddedildi (`outputs/ai-gercek-kabul-20261107-151117.json`). Diğer pilotlar ve altyapı senaryoları koşulmadı; engine/, web/ ve ortak lab değişmedi.

## Bilinen sınırlar
Küçük model ve tek koşu; `Sınır` adımındaki cümle geçerlidir.
