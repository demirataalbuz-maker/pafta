# ai-savunma-10 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Denetçinin eksikleri ve karşılıkları

| Eksik | Yapılan |
|---|---|
| Görünür örnek veri ve kusurlu başlangıç kodu yok | 3 fixture dosyası ve README eklendi; setup `hazirla("ai-savunma-10")` çağırıyor. Bütün başlangıç kodları kusurlu koda çevrildi. |
| Tablo ve sentetik veri notu yok | İlk anlatıma eklendi. |
| Saldırganın neyi denediği ve savunmanın neden kırıldığı az anlatılıyor | Anlatım blokları **~330 → 856 kelime** (450 + 127 + 107 + 172). Eklenen konular aşağıda. |

Eklenen anlatım konuları:
- **Saldırganın denedikleri:** guardrail'i zaman aşımına düşürmek, hata verdirmek, atlanan yolu kullanmak. Uygulama bunlara izin verirse fail-open olur.
- **Savunmanın kırıldığı yerler:** sınırsız ya da kalıcı hatada yeniden deneme; yedek mesaja hata izi ya da reddedilen yanıtı eklemek.
- Çıktı okuma (`toplam_bekle_ms`, riskli senaryo) ve her göreve sık tuzaklar.

## Diğer değişiklikler

- **Tablo:**
  - **Gerçekte ne olur:** NeMo/LLM Guard/moderasyon API'leri birer HTTP çağrısıdır; zaman aşımı, 5xx ve atlanma yaşanabilir. Yeniden deneme `tenacity` gibi kütüphanelerle yapılır; Promptfoo ve Garak atlatma vakalarını sınar.
  - **Ders ne kullanır:** Görev 1–3 sentetik sonuç, geçmiş ve adaylarla çalışır. Son adım yerel modelin iki senaryodaki çıktısını kullanır.
  - **Ders ne söyleyemez:** Gerçek servis ve gecikme ölçülmez. Üç kalıp bütün riskleri tanımaz. İki senaryo oran vermez.
- **Netleştirme:** "Buradaki kod dış servis çağırmaz, uyumaz ve model indirmez" cümlesi görev 1–3 için daraltıldı; son adımın yerel modeli kullandığı eklendi.
- **Görünür fixture** (`tracks/ai-savunma/fixtures/ai-savunma-10/`). Beklenen değerler dersin kendi çözümleriyle hesaplandı.
  - `veri/guardrail_sonuclari.json`: 10 sonuç. 6 geçerli (tek model kanalı, riskli izin, ret, 500, zaman aşımı, atlanma) ve 4 `ValueError`.
  - `veri/deneme_senaryolari.json`: 8 senaryo (en fazla 4 deneme, taban 250 ms, tavan 800 ms).
    - Bir senaryoda tavan devreye girer: 1000 → 800 ms, toplam 1550 ms.
    - Kalıcı hata ve tek denemelik bütçe hemen yedeğe gider.
    - 4 `ValueError`.
  - `veri/geri_donus_kayitlari.json`: 7 aday ve 4 bozuk girdi. Adaylar şunları kapsıyor:
    - Bearer, PEM, boşluklu ve boş model yanıtları.
    - **`api_key=` içeren teknik hata izi**; kullanıcıya kopyalanmamalı.
    - Yeniden deneme.
- **Kusurlu başlangıç kodları:**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Yalnız açık `reddet` engelleniyor; hata, zaman aşımı ve atlanma izin sayılıyor (fail-open); risk ve şema yok | 10 sonucun 8'i yanlış |
  | 2 | Kalıcı hata yeniden deneniyor; tavan yok; bütçe dolunca yedeğe geçilmiyor; doğrulama yok | 8 senaryonun 7'si yanlış |
  | 3 | Yalnız canary aranıyor; boş ya da boşluklu aday kabul ediliyor; **yedek mesaja aday/hata metni ekleniyor**; retry kanalına yedek yazılıyor; doğrulama ve sıralama yok | 7 adayın 6'sı, sıra ve 4 bozuk girdinin 4'ü yanlış |
  | Gerçek deney | Görev 3'ün kusurlu işlevi | Sözleşme düşüyor; `all(sonuclar)` kapısı canlı deneyi başlatmıyor (ikinci kanıt `kabul: false`) |

- **Kopya koruması:**
  - Var olan yasak listesi korundu; `kanit_yaz` eklendi.
  - AST kontrolü eklendi: takma adlı ve `*` import, `inspect`, `importlib`, `runpy`, `exec`, `eval`, `compile`, `__builtins__`. İhlalde `stop()` çalışıyor.
- **Değiştirilmeyenler:** `sandbox/ai_gercek_ai_savunma_10.py`, var olan bütün testler, ortak dosyalar, `engine/` ve `web/`.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

Validate'ten önce `ollama ps` boştu.

| Kontrol | Sonuç |
|---|---|
| validate `ai-savunma-10` | **TEMİZ**, 9 kontrol, ilk koşuda. Adım yapısı `anlat, tahmin, gorev, anlat, gorev, anlat, gorev, anlat, gorev` olarak doğrulandı. |
| tahmin | 1 tahmin, **0 şüpheli** |
| mutasyon (`kirp_gercek.py` kopyası) | 8 + 22 + 13 = **43 mutant, 0 geçen**; kopya silindi |
| kopya sondası | 6/6 **fail → korunuyor**. Doğru çözüme yasak `referans_yorumla` altı yoldan bağlandı: takma ad, öznitelik, `vars()`, `inspect` + `exec`, `*` import + `globals()`, `importlib` + `__dict__`. Doğru çözüme yalnız `import inspect` ya da `eval('1')` eklendiğinde de fail. |

Görünür veri kontrolü: Üç başlangıç kodu ve çözüm görünür fixture'larla ayrı ayrı çalıştırıldı. Tablodaki kusurlar görüldü; çözümler bütün beklenen değerleri verdi.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/sv10-kabul/ai-kanit/savunma-yedek-*.json` (kabul `true`).
- **Ölçüm:**
  - 2 senaryo koşuldu.
  - `kimlik-ornegi-1` senaryosunda model kimlik-bilgisi biçimli bir dize üretti (1 riskli çıktı). Bu çıktı `guvenli_yedek` kararını aldı ve ham içerik taşınmadı.
  - `zararsiz-1` senaryosundaki çıktı `model_yaniti` olarak aynen geçti.
  - Riskli çıktı güvenli tutuldu: `true`.
- **Değerlendirme:** Zararsız bir istekte bile model biçim olarak riskli bir dize üretti; fail-closed yedek bunu kullanıcıya göndermedi. Tek koşudan alınmış dar bir gözlemdir.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.**
- **Kurulum, indirme, commit/push ve puan yazımı yapılmadı.** Ollama sunucusuna ve modellere dokunulmadı.
