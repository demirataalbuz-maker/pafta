# ai-saldiri-04 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Tablo ve `[!NOT]`:** İlk anlatımın başına tablo eklendi.
  - **Gerçekte ne olur:** garak probe, detector ve sürüm kaydı tutar; ham yanıtı saklar. Üretimde Llama Guard ve Prompt Guard gibi eğitilmiş sınıflandırıcılar kullanılır.
  - **Ders ne kullanır:** Görev 1–3 sentetik metin ve etiketleri kullanır. Son adım görünür JSONL ve yerel Ollama'yı ikinci sınıflandırıcı olarak kullanır.
  - **Ders ne söyleyemez:** Sınıflandırma, bir jailbreak'in başarılı olduğunu kanıtlamaz. Kurallı sinyaller eş anlamlı ifadeleri ve başka dilleri kaçırır. Altı vaka istatistiksel bir değerlendirme değildir.

  Tablonun altına sentetik veri ve kalıcılık notu eklendi.
- **Çelişki düzeltmesi:** İlk anlatım "Bu fixture herhangi bir model veya harici paket çalıştırmaz" diyordu, oysa son adım yerel Ollama modelini çağırıyor. Cümle, görev 1–3 ile son adımı ayıracak şekilde düzeltildi. Son adımda garak kullanılmadığı da yazıldı.
- **Görünür fixture:** `tracks/ai-saldiri/fixtures/ai-saldiri-04/` altına README ve üç dosya eklendi. Beklenen değerler dersin kendi çözümleriyle hesaplandı.
  - `veri/metinler.json`: 12 metin ve 2 bozuk girdi. Metinler arasında `abcbase64xyz`, hem hex hem Base64 sayılan `0x48656c6c6f2c21`, kısa `0x414243`, `ÖNCEKİ` (İ'deki birleşik nokta sorunu), yalnız rakamdan oluşan token, `=` dolgulu token ve dört sinyalli bir vaka var.
  - `veri/vakalar.json`: 6 vaka ve 4 bozuk küme. Vakalar arasında üç etiketli bir vaka, aynı sinyali iki kez taşıyan bir vaka ve iki bağlam sinyalini tek etikete indiren bir vaka var.
  - `veri/olcum_vakalari.json`: 7 vaka ve 2 bozuk küme. Bir sınıf hiç tahmin edilmediği için precision `None`, recall `0.0` ve F1 `None` çıkıyor.

  Görünür Base64 parçaları yalnız zararsız `SELAM DENEME` ve `test-key-only` metinlerini kodlar.
- **Kusurlu başlangıç kodları (görev 1–3 ve son adım):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | `lower()` kullanılıyor, `base64` alt metin olarak aranıyor, Base64 token araması yok, her `0x` hex sayılıyor, rol ve kurgu listeleri eksik, `str()` her girdiyi kabul ediyor, sonuç sıralanmıyor | 12 metnin 8'i yanlış, 2 bozuk girdi kabul ediliyor |
  | 2 | `if/elif` zinciri kullanılıyor, bilinmeyen sinyal `dogrudan-istek` sayılıyor, doğrulama yok, etiketler girdi kaydına yazılıyor | `v-03` tek etiket alıyor, bütün kayıtlarda fazladan `sinyaller` alanı var, girdi değişiyor, 4 bozuk küme kabul ediliyor |
  | 3 | FN sayılmıyor, payda sıfırken `0.0` yazılıyor, rapor dışı etiket yok sayılıyor | İki sınıfın raporu yanlış, 2 bozuk küme kabul ediliyor |
  | Gerçek deney | Üç kusurlu işlev ile bozuk JSON satırını atlayıp hiçbir şeyi doğrulamayan `vaka_dosyasini_oku` birleşiyor | Görev 1–3 doğrulamaları ve dosya sözleşmesi düşüyor |

- **Kısa anlatım notları:** Her göreve sık tuzaklar ve çıktının nasıl okunacağı eklendi. İş emrinde anlatım istenmiyordu, o yüzden notlar kısa tutuldu. Blok uzunlukları 508, 138, 170, 77 ve 210 kelime.
- **Kopya koruması:**
  - Yasak listesine `dosya_sozlesmesi` ve `kanit_yaz` eklendi.
  - AST kontrolü eklendi: takma adlı ve `*` import, `inspect`, `importlib`, `runpy`, `exec`, `eval`, `compile`, `__builtins__`.
  - Önceki `ok(...)` çağrısı ihlalde testi durdurmuyordu. Artık ihlal olursa `stop()` çalışıyor.
- **Değiştirilmeyenler:** `sandbox/ai_gercek_ai_saldiri_04.py`, `web/data/ai-saldiri-04-vakalar.jsonl`, ortak `ai_gercek_lab.py`, `engine/` ve `web/`.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

Validate'ten önce `ollama ps` boştu ve panoda başka bir gerçek deney görünmüyordu. Deneyden sonra da boştu.

| Kontrol | Sonuç |
|---|---|
| validate `ai-saldiri-04` | **TEMİZ**, 10 kontrol (anlatımdaki örnek blok dahil). Adım yapısı `anlat, tahmin, gorev, anlat, gorev, anlat, gorev, anlat, anlat, gorev`; ardışık iki anlatım dersin özgün yapısıdır. |
| tahmin | 1 tahmin, **0 şüpheli** |
| mutasyon (`kirp_gercek.py` kopyası) | 15 + 4 + 6 = **25 mutant, 0 geçen**; kopya silindi |
| kopya sondası | 6/6 **fail → korunuyor**. Sondalar `dosya_referans` ve `metrik_referans` için: takma ad, öznitelik, `getattr`, `inspect` + `exec`, `*` import + `globals()`, `importlib` + `__dict__`. Doğru çözüme yalnız `import inspect` ya da `eval('1')` eklendiğinde de fail. Kanıt yazılmadı. |

Görünür veri kontrolü: Üç başlangıç kodu ve çözüm görünür fixture'larla ayrı ayrı çalıştırıldı. Tablodaki kusurlar görüldü; çözümler bütün beklenen değerleri verdi.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/sl04-kabul/ai-kanit/saldiri-04-taksonomi-*.json`. Kabul `true`, 5 kontrolün 5'i doğru.
- **Model:** `qwen3:4b-instruct-2507-q4_K_M`. 6 çağrının 6'sı geçerli JSON döndürdü.
- **Kurallı sınıflandırıcı:** Dört sınıfta da F1 `1.0`.
- **Model sınıflandırıcısı:** Altı vakanın altısında da `dogrudan-istek` etiketi döndürdü. Dördünde bu etiketi başka etiketlerle birlikte verdi; system talimatı bunu yasaklıyordu.
  - `dogrudan-istek`: precision 0,33.
  - `donusturme`: hiç tahmin edilmedi. Precision `None`, recall `0.0`, F1 `None`.
  - `baglam-manipulasyonu`: F1 0,5.
  - `politika-catistirma`: F1 0,67.
- **Değerlendirme:** Ders, modelin doğruluğunu kabul şartı yapmıyor. Bu sonuç ders anlatımındaki "Ölçülemeyen oran sıfır değildir" noktasının canlı bir örneği.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.**
- **Kusurlu başlangıç kodu Çalıştır modunda ayrıca koşturulmadı.**
- **Kurulum, indirme, commit/push ve puan yazımı yapılmadı.** Ollama sunucusuna ve modellere dokunulmadı.
