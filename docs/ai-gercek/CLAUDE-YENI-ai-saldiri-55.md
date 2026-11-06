# Yeni ders ai-saldiri-55 (plan-saldiri-9, Deepfake / ses tespiti): yazar kontrolleri tamam, denetime hazır

- Yazar: claude-yazar. Atama: ortak pano 04.11.2026 18:13 kararı.
- Puan verilmedi; bağımsız denetim claude-opus'tadır.
- Görsel sınama yapılmadı; kabul CLI üzerinden `tools/validate.py` ile yapıldı.

## Kurulum (kullanıcı onayıyla, 04.11.2026: "İkisini de onayla")

Liste, codex'in hazırladığı `SES-TESPIT-KURULUM-ONAYI.md` ile birebir aynı. Beş dosyanın sha256'sı da listeyle eşleşti.

| Dosya | Kaynak / sürüm | Boyut | sha256 (ilk 8) |
|---|---|---|---|
| `piper_tts-1.8.0-cp39-abi3-win_amd64.whl` | PyPI (GPLv3) | 34.119.688 bayt | `5da9bfdb` |
| `pathvalidate-3.3.1-py3-none-any.whl` | PyPI | 24.305 bayt | `5263baab` |
| `en_US-ljspeech-medium.onnx` (+ `.onnx.json`, `MODEL_CARD`) | rhasspy/piper-voices @ `e7229f7d` | 63.531.379 bayt | `6f52a751` |
| `clean/validation-00000-of-00001.parquet` | hf-internal-testing/librispeech_asr_dummy @ `5be91486` | 9.192.059 bayt | `4e69a06f` |

- Wheel'ler `.ai-venv`'e **kurulmadı**. Yol taşması denetimiyle `.deps/ses-tespit/pkg` altına açıldı ve sandbox bu klasörü yalnız deney sırasında `sys.path`'e ekliyor.
- Mevcut paketler kullanıldı: onnxruntime 1.31.1, numpy, scipy, scikit-learn 1.9.1, PyAV, PyArrow.
- Windows SAPI (Microsoft Zira) işletim sisteminde yerleşik; kurulum yapılmadı.
- Model kartına göre LJSpeech: tek konuşmacı, kamu malı veri, 22.050 Hz.

## Eklenen / değişen dosyalar

- `tracks/ai-saldiri/lessons/ai-saldiri-55-sentetik-ses-tespiti.md` (sha256 7fac6d0473476d48…)
- `sandbox/ai_gercek_ai_saldiri_55.py` (6100f730d3de1094…)
- `tracks/ai-saldiri/fixtures/ai-saldiri-55/README.md` ve `veri/ses.json` (545e4e1272d67032…). Dosya sentetik; ses ya da model skoru içermiyor.
- `outputs/yeni-ai-saldiri-55/` altında iki kanıt dosyası:
  - `yazar-sondasi.json`: hata vitrininin kaynağı.
  - `saldiri55-kabul-1793807460548.json`: son kabul kanıtı.
- `tracks/ai-saldiri/track.json`: "Adaptif Saldırılar ve Purple Doğrulama" modülünde 54'ten hemen sonra yalnız `ai-saldiri-55` eklendi.
- `engine/`, `web/` ve `sandbox/ai_gercek_lab.py` değişmedi. Commit/push yok.

## Kaynak doğrulaması

- **ASVspoof 2019** (Wang vd., arXiv:1911.01601): sentez, dönüştürme ve tekrar oynatma saldırıları ile karşı önlemler. Özette t-DCF geçiyor; EER özette yok. Bu yüzden ders EER'i yalnız "yaygın kullanılır" diye anıyor.
- **Piper LJSpeech sesi:** `MODEL_CARD` dosyasından okundu.

## İçerik

### Görevler

1. **`grup_bol`:** metne göre grup bölmesi.
   - Sıralama sha256'ya göre, test sayısı Python `round` ile.
   - Aynı metnin gerçek ve sentetik kaydı aynı tarafa düşer.
   - İki tarafta da iki kaynak bulunması zorunlu.
2. **`esik_metrikleri` ve `esit_hata`:**
   - TPR/FPR'nin paydaları sınıf büyüklükleri.
   - EER, `|fpr−fnr|` en küçük olacak şekilde seçilir; eşitlikte önce toplam hata, sonra eşik belirler.
3. **`kosul_raporu`:** temize göre düşüş ve artışları, `kirilan` (tpr < 0.5), `en_kotu` (EER artışı en büyük) ve `kirilgan` (temiz EER ≤ 0.1 iken bir koşulda TPR düşüşü ≥ 0.5) değerlerini raporlar.

### KUSURLU başlangıç kodları

Üç kusurlu başlangıç kodu var; kusurlar kodda yorumla söylenmez.

- **K1:** kayıt indeksine göre bölüyor; aynı metin iki tarafa düşüyor.
- **K2:** katı eşik kullanıyor, paydası toplam örnek sayısı; EER yerine toplam hatayı küçültüyor.
- **K3:**
  - Düşüşün işareti ters.
  - `kirilan` için `<=` kullanılıyor.
  - `en_kotu` TPR'ye göre seçiliyor.
  - `kirilgan` temiz şartı olmadan hesaplanıyor.
  - Sıralama yok.

### Anlatım öğeleri

- Kaynak tablosu ve NOT.
- "Saldırgan ne dener" bölümü: kısayolu kırmak, kanalı değiştirmek, başka üretici kullanmak.
- "Savunma neden kırılır" bölümü: tek konuşmacı ve tek TTS confound'u, metin sızıntısı, eşik ile EER farkı.
- Tahmin bloğu: Python `round` ve `>` / `>=` farkı.
- Eşleme: `esleme: ai-saldiri-54, ai-saldiri-53, ai-savunma-37`.
- Hata vitrini, yazar koşusundan üç örnekle: kısayol, kalibrasyon kayması, görülmemiş üretici.
- Kanıt okutma ve Sınır cümlesi.

## Gerçek final (son kabul koşusu)

- **Ortam:** 45 metin (30 eğitim / 15 test), 45 Piper sentezi ve 15 SAPI sentezi. Deney yaklaşık 13 sn, validate toplamı yaklaşık 43 sn.

| Model | Koşul | TPR (eşik 0.5) | FPR | EER |
|---|---|---|---|---|
| A_karisik_hz | temiz | 1.000 | 0.000 | 0.000 |
| A_karisik_hz | gurultu_20db | 1.000 | 0.000 | 0.000 |
| A_karisik_hz | telefon | 0.000 | 0.000 | 0.000 |
| A_karisik_hz | ornekleme_16k | 0.067 | 0.000 | 0.000 |
| A_karisik_hz | sapi | 0.000 | 0.000 | 0.200 |
| B_esit_hz | temiz | 1.000 | 0.000 | 0.000 |
| B_esit_hz | gurultu_20db | 1.000 | 0.000 | 0.000 |
| B_esit_hz | telefon | 1.000 | 0.000 | 0.000 |
| B_esit_hz | ornekleme_16k | 1.000 | 0.000 | 0.000 |
| B_esit_hz | sapi | 0.000 | 0.000 | 0.800 |

- **Kısayol:** A modelinin temizdeki başarısı örnekleme hızı kısayolundan geliyor. Sentetik ses 16 kHz'e indirilince A'nın TPR'si 0.067'ye düşüyor; B'ninki etkilenmiyor.
- **Kalibrasyon kayması:** A'da telefon bandında TPR 0, EER 0. Sıralama korunuyor, eşik kayıyor.
- **Görülmemiş üretici:** SAPI iki modelde de yakalanmıyor. B'nin EER'i 0.8; skor sıralaması rastgeleden de kötü.
- **Kırılganlık:** iki model de `kirilgan` çıktı, çünkü ikisi de SAPI'de çöktü.
- **Kabul şartları:**
  - Dört işlevin gerçek veride referansla birebir aynı olması.
  - Aynı metnin iki tarafta olmaması.
  - 90 kayıt ve 10 × 30 gerçek skor.
  - Kapsamın kanıtta yazılı olması: 16 kHz tek konuşmacı, 22050 Hz Piper, SAPI Zira.

  Dedektörün başarılı olması ya da kırılması kabul şartı değil.

## Kendi kontrollerim (`.ai-venv/Scripts/python.exe -X utf8`)

- **`tools/validate.py ai-saldiri-55`:** TEMİZ, 9 kontrol (1 tahmin, 4 solution, 4 starter). `gereksinim: torch`.
- **`tahmin.py`:** 1 tahmin, 0 şüpheli.
- **`kirp_gercek.py` + `mutasyon.py --en-cok 1000`:** 10 + 19 + 14 = 43 mutant, 0 geçen. İlk turda 6 mutant geçti:
  - İkisi eşdeğerdi; kaynakları kaldırıldı: gereksiz oran üst sınırı ve sıralama anahtarındaki `/2`.
  - Dördü sonraki bir denetimin arkasında kalıyordu. Bool etiketli iki sınıflı örnek ve `temiz` satırı dışındaki ad hataları için testler eklendi.
- **Kopya sondası 7/7 reddedildi** (son çözüm üzerinde yeniden koşuldu):
  - Altısı `kod_denetimi(..., izin=())` ile testte düştü.
  - inspect + exec hata vererek düştü.

## Bilinen sınırlar / denetçiye not

- **Kapsamın en önemli sınırı.** Gerçek sınıf tek konuşmacıdan, sentetik sınıf tek TTS sesinden geliyor. Dedektör konuşmacı ya da ses kimliğini öğrenmiş olabilir ve bu deney bunu ayıramaz. Ders bunu anlatımda, hata vitrininde, kanıt sorusunda ve Sınır cümlesinde açıkça söylüyor; genel deepfake tespit başarısı iddia edilmiyor.
- **Koşudan koşuya değişkenlik.** Piper çıktısı koşudan koşuya biraz değişiyor. Örnek: A'nın `ornekleme_16k` TPR'si yazar koşusunda 0, kabul koşusunda 0.067; B'nin telefon TPR'si 0.933'e karşı 1.0. Ders sabit sayı iddia etmiyor.
- **Etik sınır.** Kimsenin sesi klonlanmıyor ve mikrofon kullanılmıyor. Üretilen WAV dosyaları geçici klasörde kalıyor ve siliniyor.
- **Platform.** Final yalnız Windows'ta çalışıyor ve onaylı `.deps/ses-tespit` kurulumu gerekiyor. Kurulum yoksa `GercekLabYok` ile duruyor; otomatik indirme yok.
