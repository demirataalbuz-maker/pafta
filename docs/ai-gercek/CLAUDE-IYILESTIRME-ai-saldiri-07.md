# ai-saldiri-07 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Tablo ve `[!NOT]`:** İlk anlatımın başına tablo eklendi.
  - **Gerçekte ne olur:** Binlerce sorgu atılır; istek ve ham yanıt (`seed`, `temperature`, `done_reason`) kaydedilir. Yanıt dağılımı ya da logit/olasılık bilgisi bir aday modelle karşılaştırılır. Ücret, hız sınırı ve kullanım şartları sorgu bütçesini belirler.
  - **Ders ne kullanır:** Görev 1–3 sentetik sorgular, bir yanıt kaseti ve gözlem kayıtları kullanır. Son adım, yerel modele iki profille 8 gerçek çağrı yapar.
  - **Ders ne söyleyemez:** Ağırlık, mimari ya da model kimliği çıkarılmaz. Son adımdaki iki profil aynı modeldir. Ders başka birinin uç noktasına sorgu göndermez.

  Tablonun altına sentetik veri ve kalıcılık notu eklendi.
- **Çelişki düzeltmesi:** İlk anlatım "Bu ders ağ çağrısı yapmadan deterministik fixture kullanır" diyordu, oysa son adım yerel Ollama'yı çağırıyor. Cümle, görev 1–3 ile son adımı ayıracak şekilde düzeltildi.
- **Görünür fixture:** `tracks/ai-saldiri/fixtures/ai-saldiri-07/` altına README ve üç dosya eklendi. Beklenen değerler dersin kendi çözümleriyle hesaplandı.
  - `veri/sorgu_seti.json`: 3 sorgu, kayıttan oynatılan (replay) yanıt kaseti, 7 bozuk set ve 1 zaman aşımı vakası. Bozuk setlerden birinin ilk sorgusu geçerlidir; bu set, çağrıdan önce doğrulama yapılıp yapılmadığını ölçer.
  - `veri/gozlem_kayitlari.json`: Karışık sırada 6 kayıt ve 3 bozuk küme. Kayıtlar arasında `HAYIR\n` yanıtı (satır sonu farkı) ve `Türkçe` yanıtı (`ensure_ascii` farkı) var.
  - `veri/uc_karsilastirma.json`: İki uç noktanın kayıtları, bir vakası atılmış `eksik_uc_b` kaydı ve 3 bozuk çift.
- **Kusurlu başlangıç kodları (görev 1–3 ve son adım):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Doğrulama çağrılarla iç içe yapılıyor; tekrar `0`'dan sayılıyor; `int()` kullanılıyor; sınır ve yineleme denetimi yok; adaptör hatası `"HATA"` yanıtına çevriliyor | Tekrarlar `0..n-1` çıkıyor. 7 bozuk setin 6'sı kabul ediliyor; reddedilen sette bile model 2 kez çağrılıyor. Zaman aşımı yutuluyor. |
  | 2 | Kayıtlar sıralanmıyor, `ensure_ascii=True` ve `strip()` kullanılıyor, kararlılık kayıt sayısına bölünüyor, yineleme denetlenmiyor | İmza farklı, `kararli_vaka=3`, `kararlilik=0.5`, ters sırada imza değişiyor; 3 bozuk küme kabul ediliyor |
  | 3 | Yalnız ortak anahtarlar karşılaştırılıyor, yineleme ve yanıt türü denetlenmiyor, boş sette `0.0` dönüyor, sıralama yok | Eksik uçla yapay `eslesme=1.0` çıkıyor; 3 bozuk çift kabul ediliyor |
  | Gerçek deney | Üç kusurlu işlevin birleşimi | Saf kontroller düşüyor; deneyden önce `stop()` çalışıyor |

- **Kısa notlar:** Her göreve sık tuzaklar ve çıktının nasıl okunacağı eklendi. İş emrinde anlatım istenmiyordu. Blok uzunlukları 441, 130, 110 ve 268 kelime.
- **Kopya koruması:**
  - `kanit_yaz` yasak listesine eklendi.
  - AST kontrolü eklendi: takma adlı ve `*` import, `inspect`, `importlib`, `runpy`, `exec`, `eval`, `compile`, `__builtins__`.
  - Önceki denetim ihlal bulsa da testi durdurmuyordu. Artık ihlalde `stop()` çalışıyor.
- **Değiştirilmeyenler:** `sandbox/ai_gercek_ai_saldiri_07.py`, `tracks/ai-saldiri/veri/ai-saldiri-07-ornek-gozlem.jsonl`, son adımın `setup` bloğu, ortak `ai_gercek_lab.py`, `engine/` ve `web/`.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

Validate'ten önce ve sonra `ollama ps` boştu. Validate'ten önce panoda başka bir gerçek deney görünmüyordu.

| Kontrol | Sonuç |
|---|---|
| validate `ai-saldiri-07` | **TEMİZ**, 11 kontrol (anlatımdaki iki örnek blok dahil). Adım yapısı `anlat, tahmin, gorev ×3, anlat, gorev` olarak doğrulandı. |
| tahmin | 1 tahmin, **0 şüpheli** |
| mutasyon (`kirp_gercek.py` kopyası) | 10 + 8 + 4 = **22 mutant, 0 geçen**; kopya silindi |
| kopya sondası | 6/6 **fail → korunuyor**. Sondalar `parmak_izi_referans` ve `karsilastir_referans` için: takma ad, öznitelik, `getattr`, `inspect` + `exec`, `*` import + `globals()`, `importlib` + `__dict__`. Doğru çözüme yalnız `import inspect` ya da `eval('1')` eklendiğinde de fail. Kanıt yazılmadı. |

Görünür veri kontrolü: Üç başlangıç kodu ve çözüm görünür fixture'larla ayrı ayrı çalıştırıldı. Tablodaki kusurlar görüldü; çözümler bütün beklenen değerleri verdi.

**Sınır:** Görev 3'ün başlangıç kodu ana `uc_a` / `uc_b` karşılaştırmasında doğru sonucu veriyor. Kusurlar eksik anahtarlı ve bozuk çiftlerde görünüyor; gizli test bu kodu reddediyor.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/sl07-kabul/ai-kanit/saldiri-07-parmak-izi-*.json`. Kabul `true`, 6 kontrolün 6'sı doğru.
- **Model:** `qwen3:4b-instruct-2507-q4_K_M`, kendi CPU sunucusunda.
- **`T=0.0` sınıflandırıcı profili:** 4 gözlem, iki vaka da kararlı (`kararlilik=1.0`).
- **`T=0.6` açıklamalı profil:** 4 gözlem, iki vakadan biri kararlı (`kararlilik=0.5`).
- **Karşılaştırma:** `eslesme=0.0`; iki vaka da farklı.
- **Değerlendirme:** Aynı model, yalnız sıcaklık ve system talimatı değişince hiçbir yanıtta eşleşmedi. Bu, eşleşme oranının kimlik kanıtı olmadığını dersin kendi örneğiyle gösteriyor.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.**
- **Kusurlu başlangıç kodu Çalıştır modunda ayrıca koşturulmadı.**
- **Kurulum, indirme, commit/push ve puan yazımı yapılmadı.** Kullanıcının Ollama sunucusuna ve modellerine dokunulmadı.
