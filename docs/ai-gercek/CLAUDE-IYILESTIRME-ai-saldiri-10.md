# ai-saldiri-10 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Tablo ve `[!NOT]`:** İlk anlatımın başına tablo eklendi.
  - **Gerçekte ne olur:** Model yanıtı `message.content` string'i olarak gelir. JSON modu ya da `format` şeması açık olsa bile kod çiti, açıklama veya yarım üretim görülebilir. Yanıt sırayla ayrıştırıcıdan, şema doğrulayıcıdan (jsonschema/Pydantic) ve kuyruk adaptöründen geçer.
  - **Ders ne kullanır:** Görev 1–3 sentetik veri kullanır. Son adım görünür JSON dosyası, iki canlı Ollama yanıtı ve geçici bir SQLite kuyruğu kullanır.
  - **Ders ne söyleyemez:** Başka ayrıştırıcıların aynı belgeyi aynı okuyup okumadığı ölçülmez. Modelin bozuk JSON üretme sıklığı ölçülmez. İç komutlar yalnız veri etiketidir.

  Tablonun altına sentetik veri ve kalıcılık notu eklendi.
- **Çelişki düzeltmesi:** İlk anlatım "Ders gerçek model çağırmaz" diyordu, oysa son adım iki canlı yerel yanıt alıyor. Cümle, görev 1–3 ile son adımı ayıracak şekilde düzeltildi.
- **Görünür fixture:** `tracks/ai-saldiri/fixtures/ai-saldiri-10/` altına README ve üç dosya eklendi. Beklenen değerler dersin kendi çözümleriyle hesaplandı.
  - `veri/ham_yanitlar.json`: 12 ham metin ve 4 bozuk girdi. Kod çiti, öndeki ya da arkadaki açıklama, üst ve iç düzeyde yinelenen anahtar, `NaN` ve `-Infinity`, art arda iki belge, string kök, `\u` kaçışı içerir. Ayrıca bir sınır örneği var: `1e400` sabit sayılmaz, `inf` olarak kabul edilir. Bu durum görev 2'de sonluluk kontrolünün neden gerektiğini gösterir.
  - `veri/kararlar.json`: 14 karar ve 2 bozuk girdi. `True` ve `"0.9"` güvenceleri, ek `arac` alanı, `Ozetle` eylemi ve 120/121 karakter sınırı içerir.
  - `veri/komut_vakalari.json`: 9 vaka. `0.75` ve `0.7499` güvenceleri, düşük güvenceli `GİZLİ NOT` metni ve `dosya_sil` / `__import__` eylemleri içerir.
- **Kusurlu başlangıç kodları (görev 1–3 ve son adım):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Kod çiti ve önek soyuluyor; `json.loads` kullanılıyor; hatada `None` dönüyor | 12 örneğin 8'i yanlış. `h-05` sessizce `dosya_sil` olarak çözülüyor, `NaN`/`-inf` kabul ediliyor. 4 bozuk girdi kabul ediliyor. |
  | 2 | Ek alan bırakılıyor, `lower()` ve `float()` kullanılıyor, metin denetlenmiyor, girdi değiştirilip aynı nesne döndürülüyor | 7 kararın kabul/red sonucu yanlış; bütün kabullerde aynı nesne dönüyor. Bozuk girdiler `ValueError` yerine `TypeError` veriyor. |
  | 3 | Bilinmeyen eylem `upper()` ile komuta çevriliyor, eşik `>` ile uygulanıyor, düşük güvencede metin taşınıyor, şema denetlenmiyor | 9 vakanın 7'si yanlış. `DOSYA_SIL` ve `__IMPORT__` komutları üretiliyor. |
  | Gerçek deney | Üç kusurlu işlevin birleşimi | Ön kontroller düşüyor; deneyden önce `stop()` çalışıyor |

- **Yazım hatası düzeltmesi:** Görev 1'in başlangıç kodu kod çitini aramak için ilk sürümde düz bir üçlü backtick içeriyordu. Bu, Markdown çitini erken kapatıyordu. `"`" * 3` ile değiştirildi ve adım yapısı yeniden doğrulandı.
- **Kısa notlar:** Her göreve sık tuzaklar ve çıktının nasıl okunacağı eklendi. Blok uzunlukları 432, 134, 120 ve 189 kelime.
- **Kopya koruması:**
  - Var olan yasak listesine `kanit_yaz` eklendi.
  - AST kontrolü eklendi: takma adlı ve `*` import, `inspect`, `importlib`, `runpy`, `exec`, `eval`, `compile`, `__builtins__`.
  - Var olan `stop()` korundu.
- **Değiştirilmeyenler:** `sandbox/ai_gercek_ai_saldiri_10.py`, `web/data/ai-saldiri-10-json.txt`, ortak `ai_gercek_lab.py`, `engine/` ve `web/`.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

Validate'ten önce ve sonra `ollama ps` boştu. Validate'ten önce panoda başka bir gerçek deney görünmüyordu.

| Kontrol | Sonuç |
|---|---|
| validate `ai-saldiri-10` | **TEMİZ**, 10 kontrol (anlatımdaki örnek blok dahil). Adım yapısı `anlat, tahmin, gorev ×3, anlat, gorev` olarak doğrulandı. |
| tahmin | 1 tahmin, **0 şüpheli** |
| mutasyon (`kirp_gercek.py` kopyası) | 2 + 12 + 14 = **28 mutant, 0 geçen**; kopya silindi. Görev 1'in çözümü kısa olduğu için 2 mutant üretildi; test 14 bozuk metin ve 3 yanlış çözüm içeriyor. |
| kopya sondası | 6/6 **fail → korunuyor**. Sondalar `pipeline_referans` için: takma ad, öznitelik, `getattr`, `inspect` + `exec`, `*` import + `globals()`, `importlib` + `__dict__`. Doğru çözüme yalnız `import inspect` ya da `eval('1')` eklendiğinde de fail. Kanıt yazılmadı. |

Görünür veri kontrolü: Üç başlangıç kodu ve çözüm görünür fixture'larla ayrı ayrı çalıştırıldı. Tablodaki kusurlar görüldü; çözümler bütün beklenen değerleri verdi.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/sl10-kabul/ai-kanit/saldiri-10-json-*.json`. Kabul `true`, 9 kontrolün 9'u doğru.
- **Model:** `qwen3:4b-instruct-2507-q4_K_M`.
  - **Birinci canlı yanıt:** `{"eylem":"ozetle","metin":"PAFTA local note","guvence":0.9}`. Bu yanıt `OZET` işi olarak SQLite'a yazıldı.
  - **İkinci canlı yanıt:** Model, yinelenen `eylem` anahtarını aynen üretti. Katı ayrıştırıcı bunu `yinelenen anahtar` diyerek reddetti ve kuyrukta değişiklik olmadı (`db_degisim=0`).
- **Kuyruk:**
  - Sentetik 8 vakanın 3'ü işe, 1'i boş içerikli incelemeye gitti; 5'i reddedildi.
  - Toplam: 6 red, 3 iş, 1 inceleme.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.**
- **Kusurlu başlangıç kodu Çalıştır modunda ayrıca koşturulmadı.**
- **Kurulum, indirme, commit/push ve puan yazımı yapılmadı.** Ollama sunucusuna ve modellere dokunulmadı.
