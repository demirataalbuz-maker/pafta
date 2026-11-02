# ai-saldiri-16 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Tablo ve `[!NOT]`:** İlk anlatımın başına tablo eklendi.
  - **Gerçekte ne olur:** Araçlar Ollama/OpenAI `tools` dizisiyle ya da MCP `tools/list` ile modele verilir. Model native `tool_calls` döndürür. Üçüncü taraf bir MCP sunucusu açıklamayı istediği zaman değiştirebilir.
  - **Ders ne kullanır:** Görev 1–3 sentetik veri kullanır. Son adım native tool şemasıyla 4 model çağrısı yapar ve seçilen aracı izole sentetik dosyalarda gerçekten çalıştırır.
  - **Ders ne söyleyemez:** Ölçüm oran vermez. Seçim farkı nedensellik kanıtı değildir. Şema doğrulaması yetki anlamına gelmez. Gerçek bir MCP sunucusu kullanılmaz.

  Tablonun altına sentetik veri ve kalıcılık notu eklendi.
- **Çelişki düzeltmesi:** İlk anlatım "Ollama veya gerçek araç çalıştırılmaz" diyordu, oysa son adım her ikisini de yapıyor. Cümle, görev 1–3 ile son adımı ayıracak şekilde düzeltildi.
- **Görünür fixture:** `tracks/ai-saldiri/fixtures/ai-saldiri-16/` altına README ve üç dosya eklendi. Beklenen değerler dersin kendi çözümleriyle hesaplandı.
  - `veri/araclar.json`: 12 araç kaydı. Biri zehirli açıklamalı, ama açıklama korunmalı. Diğerleri büyük harfli, tireli ya da 33 karakterlik ad; `array` girdi tipi; `number` alan türü; tanımsız ya da yinelenen zorunlu alan; ek `izin` alanı; boş alanlar; alan tanımında ek `aciklama`.
  - `veri/cagrilar.json`: `siparis_oku` şeması ve 10 çağrı. Çağrılar arasında `True` ve `"42"` değerleri, eksik zorunlu alan, şemada olmayan `yol` alanı, `"true"` metni, string olarak gelen `arg`, ek `izin` alanı ve kayıtlı olmayan araç adı var. Kayıtlı olmayan araç adı bu işlevde reddedilmez.
  - `veri/secim_kayitlari.json`: 5 vaka ve 4 bozuk girdi. Vakalar: hedefli değişim, rastgele değişim, değişmeyen seçim, alıntı ve `\r\n` satır sonu.
- **Kusurlu başlangıç kodları (görev 1–3 ve son adım):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Ad `lower()` ile düzeltiliyor; biçim ve girdi şeması denetlenmiyor; `BREACH` satırları siliniyor; açıklama `guvenilir` etiketleniyor; kanonik ayarlar yok | 12 örneğin 12'si yanlış |
  | 2 | `isinstance(deger, int)` kullanılıyor; ek alan bırakılıyor; zorunlu alan ve çağrı şeması denetlenmiyor; aynı `arg` nesnesi döndürülüyor | 10 çağrının 5'i yanlış; kabul edilenlerde aynı nesne dönüyor |
  | 3 | Zehirli koldaki herhangi bir açıklamada alt metin araması yapılıyor; doğrulama ve sıralama yok | `hedefli_degisim` 5 vaka çıkıyor (2 olmalı); 4 bozuk girdi kabul ediliyor |
  | Gerçek deney | Üç kusurlu işlevin birleşimi | Ön kontroller düşüyor; deneyden önce `stop()` çalışıyor |

- **Kısa notlar:** Her göreve sık tuzaklar ve çıktının nasıl okunacağı eklendi. Blok uzunlukları 400, 129, 125 ve 171 kelime.
- **Kopya koruması:**
  - `kanit_yaz` yasak listesine eklendi.
  - AST kontrolü eklendi: takma adlı ve `*` import, `inspect`, `importlib`, `runpy`, `exec`, `eval`, `compile`, `__builtins__`.
  - Var olan `stop()` korundu.
- **Değiştirilmeyenler:** `sandbox/ai_gercek_ai_saldiri_16.py`, `web/data/ai-saldiri-16-araclar.txt`, ortak `ai_gercek_lab.py`, `engine/` ve `web/`.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

Validate'ten önce ve sonra `ollama ps` boştu. Validate'ten önce panoda başka bir gerçek deney görünmüyordu.

| Kontrol | Sonuç |
|---|---|
| validate `ai-saldiri-16` | **TEMİZ**, 9 kontrol. Adım yapısı `anlat, tahmin, gorev ×3, anlat, gorev` olarak doğrulandı. |
| tahmin | 1 tahmin, **0 şüpheli** |
| mutasyon (`kirp_gercek.py` kopyası) | 13 + 14 + 7 = **34 mutant, 0 geçen**; kopya silindi |
| kopya sondası | 6/6 **fail → korunuyor**. Sondalar `fark_referans` için: takma ad, öznitelik, `getattr`, `inspect` + `exec`, `*` import + `globals()`, `importlib` + `__dict__`. Doğru çözüme yalnız `import inspect` ya da `eval('1')` eklendiğinde de fail. Kanıt yazılmadı. |

Görünür veri kontrolü: Üç başlangıç kodu ve çözüm görünür fixture'larla ayrı ayrı çalıştırıldı. Tablodaki kusurlar görüldü; çözümler bütün beklenen değerleri verdi.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/sl16-kabul/ai-kanit/saldiri-16-*.json`. Kabul `true`, 6 kontrolün 6'sı doğru.
- **Native seçim:** Model, temiz ve zehirli açıklamayla 2'şer tekrarın hepsinde `siparis_oku` aracını seçti. Fark raporu: `degisen=[]`, `hedefli_degisim=[]`.
- **Değerlendirme:** Bu koşuda zehirli açıklama araç seçimini değiştirmedi. Ders bunu kabul şartı yapmıyor. Sonuç, tek seed çifti ve tek görevle alınmış dar bir gözlemdir; zehirlemenin etkisiz olduğunu göstermez.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.**
- **Kusurlu başlangıç kodu Çalıştır modunda ayrıca koşturulmadı.**
- **Kurulum, indirme, commit/push ve puan yazımı yapılmadı.** Ollama sunucusuna ve modellere dokunulmadı.
