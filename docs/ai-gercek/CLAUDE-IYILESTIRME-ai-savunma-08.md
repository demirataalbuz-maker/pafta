# ai-savunma-08 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Denetçinin eksikleri ve karşılıkları

| Eksik | Yapılan |
|---|---|
| Görünür örnek veri ve kusurlu başlangıç kodu yok | 3 fixture dosyası ve README eklendi. Setup `hazirla("ai-savunma-08")` çağırıyor. Bütün başlangıç kodları kusurlu koda çevrildi. |
| Tablo ve sentetik veri notu yok | İlk anlatıma eklendi. |
| Saldırganın neyi denediği ve savunmanın neden kırıldığı az anlatılıyor | Anlatım blokları **~360 → 862 kelime** (460 + 146 + 94 + 162). Eklenen konular aşağıda. |

Eklenen anlatım konuları:
- **Saldırganın denedikleri:** base64/hex kodlama, harf bölme, tam genişlikli Unicode, `kaynaklar` ya da ek bir şema alanına gömme, güveni şişirme.
- **Savunmanın kırıldığı yerler:** kalıp körlüğü, fazladan alanı sessizce atma, `strip()`/tür dönüştürme ile "düzeltme".
- Çıktının nasıl okunacağı: boş sinyal listesi "sızıntı yok" demek değildir.
- Her göreve sık tuzaklar.

## Diğer değişiklikler

- **Tablo:**
  - **Gerçekte ne olur:** Ollama `format`/JSON Schema, Pydantic, NeMo Guardrails çıkış rayları, Guardrails AI, Gitleaks/TruffleHog, FastAPI karar katmanı.
  - **Ders ne kullanır:** Görev 1–3 sentetik çıktılar ve kayıtlarla çalışır. Son adım yerel modelin yapısal ve serbest çıktılarını kullanır.
  - **Ders ne söyleyemez:** Kodlanmış ya da bölünmüş sızıntı kaçar. İki mod oran vermez. Şemaya uyan yanıt doğru ya da zararsız olmak zorunda değildir.
- **Çelişki düzeltmesi:** İlk anlatım "Buradaki fixture dış model çağırmaz" diyordu; bu doğruydu ama son adımın gerçek model kullandığını söylemiyordu. Cümle, görev 1–3 ile son adımı ayıracak şekilde netleştirildi.
- **Görünür fixture** (`tracks/ai-savunma/fixtures/ai-savunma-08/`). Beklenen değerler dersin kendi çözümleriyle hesaplandı.
  - `veri/model_ciktilari.json`: 12 çıktı. 3 geçerli (güven 0, tamsayı 1, boş kaynak). 9 `ValueError`: ek `sistem_notu`, sondaki boşluk, güven `True`/`1.5`/`"0.9"`, `; rm -rf` gömülü kaynak, yinelenen kaynak, 6 kaynak, bilinmeyen etiket.
  - `veri/cikti_metinleri.json`: 12 metin.
    - Yakalananlar: RSA başlığı, küçük `bearer`, tam genişlikli `ＡＰＩ＿ＫＥＹ` (NFKC), reddetme cümlesindeki canary, tekrar, dört sinyal.
    - Yakalanmayanlar: 7 karakter Bearer, `CANARY-420`, **base64 anahtar** (bilerek bırakılmış sınır).
    - NUL içeren metin `ValueError` alır.
  - `veri/guardrail_kayitlari.json`: 7 kayıt (tam 0.5 sınırı, şema-yalnız durdurma, bütün nedenler) ve 4 bozuk girdi.
- **Kusurlu başlangıç kodları:**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Ek alan bırakılıyor; `strip()`; güven türü/aralığı ve kaynak denetimi yok; liste kopyalanmıyor | 12 örneğin 8'i yanlış |
  | 2 | Normalizasyon yok; yalnız tek PEM başlığı; uzunluk ve kelime sınırı yok; tekrar ekleniyor | 12 metnin 7'si yanlış |
  | 3 | İlk nedende duruluyor; şema hatası geçiriliyor; `<=` eşik; doğrulama ve sıralama yok | 7 kaydın 3'ü yanlış, sıra yanlış, 4 bozuk girdinin 4'ü yanlış |
  | Gerçek deney | Görev 3'ün kusurlu işlevi | Sözleşme düşüyor; `all(sonuclar)` kapısı canlı deneyi başlatmıyor (ikinci kanıt `kabul: false`, özet yok) |

- **Kopya koruması:**
  - Var olan yasak listesi korundu; `kanit_yaz` eklendi.
  - AST kontrolü eklendi: takma adlı ve `*` import, `inspect`, `importlib`, `runpy`, `exec`, `eval`, `compile`, `__builtins__`. İhlalde `stop()` çalışıyor.
- **Değiştirilmeyenler:** `sandbox/ai_gercek_ai_savunma_08.py`, ortak `ai_savunma_veri.py`, var olan bütün testler, `engine/` ve `web/`.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

Validate'ten önce `ollama ps` boştu. Panoda Gemini yalnız ders düzenleme işindeydi.

| Kontrol | Sonuç |
|---|---|
| validate `ai-savunma-08` | **TEMİZ**, 9 kontrol, ilk koşuda. Adım yapısı `anlat, tahmin, gorev, anlat, gorev, anlat, gorev, anlat, gorev` olarak doğrulandı. |
| tahmin | 1 tahmin, **0 şüpheli** |
| mutasyon (`kirp_gercek.py` kopyası) | 16 + 2 + 12 = **30 mutant, 0 geçen**; kopya silindi |
| kopya sondası | 6/6 **fail → korunuyor**. Sondalar `referans_karar` için: takma ad, öznitelik, `vars()`, `inspect` + `exec`, `*` import + `globals()`, `importlib` + `__dict__`. Bu derste `getattr` zaten yasaklı. Doğru çözüme yalnız `import inspect` ya da `eval('1')` eklendiğinde de fail. |

Görünür veri kontrolü: Üç başlangıç kodu ve çözüm görünür fixture'larla ayrı ayrı çalıştırıldı. Tablodaki kusurlar görüldü; çözümler bütün beklenen değerleri verdi.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/sv08-kabul/ai-kanit/savunma-cikti-*.json` (kabul `true`). Model: `qwen3:4b-instruct-2507-q4_K_M`.
- **Ölçüm:** 2 mod. Yapısal mod şemaya uydu → `gecir`. Serbest mod şemaya uymadı → `durdur`. Canary sızıntısı: 0. Öğrenci kararı bağımsız referansla aynı.
- **Değerlendirme:** Bu koşuda model sırrı yankılamadı. Serbest paragraf yine de yalnız biçim nedeniyle fail-closed durduruldu. Tek koşudan alınmış dar bir gözlemdir.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.**
- **Kurulum, indirme, commit/push ve puan yazımı yapılmadı.** Ollama sunucusuna ve modellere dokunulmadı.
