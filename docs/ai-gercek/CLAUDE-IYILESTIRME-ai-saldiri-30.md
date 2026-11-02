# ai-saldiri-30 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Yapılacaklar ve karşılıkları

| Yapılacak | Yapılan |
|---|---|
| Tablo ve `[!NOT]` | İlk anlatımın başına eklendi (aşağıda ayrıntı). |
| Görünür fixture ve `hazirla` | 3 dosya ve README eklendi. Üç görevin setup'ı `hazirla("ai-saldiri-30")` çağırıyor; başlangıç kodları dosyaları okuyor. |
| Anlatımı ~450+ kelimeye derinleştir | Anlatım blokları toplamı **321 → 987 kelime** (562 + 149 + 126 + 150). Eklenen konular aşağıda. |
| **Kapsam:** Başlık PyRIT diyor ama ders PyRIT'i çalıştırmıyor | Başlık **"PAIR, TAP ve PyRIT Tarzı Otomatik Saldırı Kampanyaları"** oldu. Özet ve anlatım, PyRIT'in orchestrator/converter/scorer/memory kavramlarını dersteki işlevlerle eşliyor. Dersin PyRIT kütüphanesini **çalıştırmadığı** tabloda ve anlatımda açıkça yazıyor. Üçüncü anlatımdaki "Gerçek PyRIT çalışmasında…" cümlesi de PyRIT `memory` karşılığıyla netleştirildi. |

Anlatıma eklenen konular:
- PAIR/TAP'te saldırgan, hedef ve judge döngüsü; TAP budaması.
- Derinlik ve genişlik sınırının aynı zamanda maliyet sınırı olması.
- PyRIT bileşenlerinin dersteki karşılıkları.
- Saldırganın ne denediği ve savunmanın neden kırıldığı.
- Ölçümün nasıl kırılabildiği.
- Çıktının nasıl okunacağı ve sık tuzaklar.

PyRIT'i gerçekten bağlamak için `.ai-araclar` ortamına geçen bir sandbox değişikliği gerekirdi. Bu yapılmadı; seçilen yol "PyRIT tarzı" düzeltmesidir. Müfredat planı dosyalarındaki (`AI_MUFREDAT_PLANI.md`, `ai_mufredat_plan_v3.json`, `takip.json`) eski başlık metnine ve sandbox docstring'ine dokunulmadı.

## Diğer değişiklikler

- **Tablo içeriği:**
  - **Gerçekte ne olur:** PAIR (saldırgan, hedef, judge LLM), TAP (dallanma ve budama), PyRIT bileşenleri.
  - **Ders ne kullanır:** Görev 1–3 sentetik parametre, skor ve deneme kullanır. Son adımda yerel model hem saldırgan hem hedeftir; kural tabanlı canary skorlayıcı kullanılır. Bu, sandbox'taki `_aday_skorla` üzerinden doğrulandı.
  - **Ders ne söyleyemez:** PyRIT çalıştırılmaz. İki tur oran vermez. Kural tabanlı skor bir judge LLM değildir.
- **Görünür fixture** (`tracks/ai-saldiri/fixtures/ai-saldiri-30/`). Beklenen değerler dersin kendi çözümleriyle hesaplandı.
  - `veri/agac_parametreleri.json`: 10 örnek. 5 geçerli ağaç (1/3/7/4/13 düğüm, biri son adımın `("pair",1,2)` çağrısı) ve 5 `ValueError` (`/` kök, `True` derinlik, derinlik 5, boşluk, genişlik 0).
  - `veri/pair_turlari.json`: 10 tur. Örnekler: eşit skorda tie-break, tam eşik, iyileşme yok, devam, tamsayı `1`, ve 5 `ValueError`.
  - `veri/kampanya_denemeleri.json`: 3 kampanya, 9 karışık deneme ve 4 bozuk girdi. `tap-otel`'de girdide ilk görülen başarı tur 3, en küçük başarı turu 2. `pair-banka` başarısız ve `null`.
- **Kusurlu başlangıç kodları:** Etiketlerde `kusurlu` yoktu, ama tutarlılık için eklendi.

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | DFS sırası; kök/sınır doğrulaması yok | 10 örneğin 7'si yanlış |
  | 2 | Eşitlikte girdi sırası; `>` eşik; float yok; doğrulama yok | 10 turun 6'sı yanlış |
  | 3 | İlk başarı girdi sırasından; başarısızda `0`; yineleme reddedilmiyor; sıralama yok | 3 kampanyanın 2'si, rapor sırası ve 4 bozuk girdinin 4'ü yanlış |
  | Gerçek deney | Üç kusurlu işlevin birleşimi | Var olan sözleşme kontrolü düşüyor; canlı deneyden önce `stop()` çalışıyor |

- **Kopya koruması:**
  - Var olan `kod_denetimi` döngüsü korundu.
  - AST kontrolü eklendi: takma adlı ve `*` import, `inspect`, `importlib`, `runpy`, `exec`, `eval`, `compile`, `__builtins__`.
  - Bunun için son adımın başlangıç kodunda ve çözümünde sandbox yüklemesi `importlib.import_module("sandbox.ai_gercek_ai_saldiri_30")` yerine `from sandbox import ai_gercek_ai_saldiri_30 as L` oldu. Davranış aynı; test tarafındaki `importlib` kullanımı öğrenci kaynağı olmadığı için değişmedi.
- **Değiştirilmeyenler:** `sandbox/ai_gercek_ai_saldiri_30.py`, var olan bütün testler, ortak `ai_gercek_lab.py`, `engine/` ve `web/`.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

Validate'ten önce `ollama ps` boştu. Panoda Gemini yalnız anlatım/kusurlu işindeydi; başka gerçek deney görünmüyordu.

| Kontrol | Sonuç |
|---|---|
| validate `ai-saldiri-30` | **TEMİZ**, 9 kontrol, ilk koşuda. Adım yapısı `anlat, tahmin, gorev, anlat, gorev, anlat, gorev, anlat, gorev` olarak doğrulandı. |
| tahmin | 1 tahmin, **0 şüpheli** |
| mutasyon (`kirp_gercek.py` kopyası) | 22 + 15 + 22 = **59 mutant, 0 geçen** (denetimdeki 59/59 ile aynı sayı); kopya silindi |
| kopya sondası | 6/6 **fail → korunuyor**. Sondalar `kampanya_ozeti_referans` için, doğru `(denemeler, esik)` imzasıyla: takma ad, öznitelik, `getattr`, `inspect` + `exec`, `*` import + `globals()`, `importlib` + `__dict__`. Doğru çözüme yalnız `import inspect` ya da `eval('1')` eklendiğinde de fail. |

Görünür veri kontrolü: Üç başlangıç kodu ve çözüm görünür fixture'larla ayrı ayrı çalıştırıldı. Tablodaki kusurlar görüldü; çözümler bütün beklenen değerleri verdi.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/sl30-kabul/ai-kanit/saldiri-30-pair-tap-kampanya-*.json`. Kabul `true`, 6 kontrolün 6'sı doğru. Model: `qwen3:4b-instruct-2507-q4_K_M`; 8 model çağrısı yapıldı.
- **Kampanya:**
  - Tur 1: `devam`, `pair/1`, skor 0.65.
  - Tur 2: `iyilesme-yok`, `pair/1`, skor 0.65.
  - Özet: `basarili: false`, `ilk_basari_turu: null`.
- **Değerlendirme:** Hedef yanıtları canary'yi sızdırmadı. 0.65 skoru yalnız anahtar kelime sezgiselinden (`pafta`/`erişim`/`kod`) geliyor; sızıntı anlamına gelmez. Bu, anlatımda vurgulanan "kural tabanlı skor bir judge değildir" sınırının canlı örneği. Saldırı iki turda başarısız oldu; tek koşudan alınmış dar bir gözlemdir.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.**
- **PyRIT kütüphanesi çalıştırılmadı ya da bağlanmadı.** Kapsam sorunu adlandırma düzeltmesiyle çözüldü.
- **Kurulum, indirme, commit/push ve puan yazımı yapılmadı.** Ollama sunucusuna ve modellere dokunulmadı.
