# ai-saldiri-33 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Tablo ve `[!NOT]`:** İlk anlatımın başına üç sütunlu bir tablo eklendi:
  - **Gerçekte ne olur:** vLLM, SGLang ve llama.cpp ortak önek önbelleği tutar. Çok kiracılı servislerde ortak önek isabeti zamanlamadan sezilebilir; bu yüzden prompt sızıntısı araştırılmıştır.
  - **Ders nasıl temsil ediyor:** Görev 1–3 sentetik milisaniyelerle çalışır. Son adım yerel Ollama'da 3+3 gerçek duvar saati ölçümü yapar.
  - **Ders ne söyleyemez:** Tek kullanıcılı yerel kurulum çok kiracılı ortamı temsil etmez. 3+3 ölçüm istatistiksel kanıt değildir. Ölçülen süre TTFT değildir.

  Altına sentetik veri ve kalıcılık notu eklendi.
- **Görünür fixture:** `tracks/ai-saldiri/fixtures/ai-saldiri-33/` altına bir README ve üç dosya eklendi:
  - `veri/grup_olcumleri.json`: 950 ms'lik tek aykırı hit ve 5 bozuk liste.
  - `veri/esik_olcumleri.json`: Eşiğe eşit hit, yavaş hit (FN), hızlı miss (FP), `yalniz_miss` (TPR `None`) ve 3 bozuk liste.
  - `veri/aday_olcumleri.json`: Kontrol adayı, tek şanslı ölçüm, eşik sınırında 5,0 ms, eşit fark (sıralama) ve 3 bozuk liste.

  Beklenen sonuçlar dersin kendi çözümleriyle hesaplandı.
- **Başlangıç kodları:** İş emrinde `kusurlu` etiketi yoktu. Görev 1–3 başlangıçları `return {}` idi ve görünür veriyi okuyamıyordu. Bu yüzden, önceki derslerdeki desenle tutarlı olacak şekilde, kusurlu ve veri okuyan kodlara çevrildi:

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Ortalama kullanıyor, fark ters işaretli, doğrulama yok | Hit "medyanı" 268,5. `0 ms`, `true` ve `"40"` KABUL ediliyor; iki liste ValueError yerine ZeroDivisionError ile çöküyor. |
  | 2 | `<` kullanıyor, tanımsız oranı 0.0 sayıyor, doğrulama yok | TP=1, FN=2 (60 ms'lik hit kaçıyor); `yalniz_miss` için TPR 0.0; 3 bozuk liste KABUL ediliyor. |
  | 3 | Ortalama kullanıyor, `>` kullanıyor, eşitlikte ada göre sıralamıyor, doğrulama yok | `aday-tek-sansli` 26,33 ile sinyal veriyor; `aday-esik-sinirinda` sinyal vermiyor; `aday-b` `aday-a`'nın önüne geçiyor; 3 bozuk liste KABUL ediliyor. |
  | Gerçek deney | Mevcut kusurlu `grup_ozeti`'ne ek olarak 2 ve 3. kusurlu işlevler | Kontrol, saf sözleşme testinde düşüyor ve deneyden önce `stop()` çalışıyor. |

- **Anlatım:** Aşağıdaki konular eklendi:
  - Prefill ve KV önbelleğinin altta nasıl çalıştığı.
  - Saldırganın aday önekleri nasıl ölçtüğü.
  - Aykırı değer ve medyan ilişkisi.
  - Eşik tuzakları: `<` / `<=`, tanımsız oran, yalnız doğruluğa bakmak.
  - Aday raporunun kontrol adayıyla birlikte nasıl okunacağı.
  - Gerçek deneyde kanıtın nasıl okunacağı.
- **Doğruluk düzeltmeleri:** Son anlatım "`num_predict=1`, yalnız ilk token / TTFT yükünü ölçmek için" diyordu. Gerçek çağrılar ise `en_fazla=8` ve `sicaklik=0.1` kullanıyor. Ölçülen `sure_ms` de isteğin tamamının duvar saati süresi. Anlatım buna göre düzeltildi. `sandbox/ai_gercek_ai_saldiri_33.py` dosyasındaki kanıta yazılan `ayarlar` alanı da aynı hatayı taşıyordu (`en_fazla_token: 1, sicaklik: 0.0`). Bu alan gerçek değerlerle düzeltildi ve `olcum` açıklaması eklendi. Bu, sandbox'taki tek değişikliktir; ölçüm ve kontrol mantığına dokunulmadı.
- **Kopya koruması:**
  - Mevcut `kod_denetimi` döngüsüne AST kontrolleri eklendi: takma adlı ve `*` import, `inspect`, `importlib`, `runpy`, `exec`, `eval`, `compile`, `__builtins__`.
  - Testin mevcut `if not all(checks): stop()` yapısı korunuyor.
  - Gerçek adımın başlangıç, test ve çözüm kodları modülü `importlib.import_module(...)` ile yüklüyordu. Bu kullanım yeni kuralla çakıştığı için aynı anlamdaki `from sandbox import ai_gercek_ai_saldiri_33 as L` ile değiştirildi.
- Ortak `ai_gercek_lab.py`, `engine/` ve `web/` değiştirilmedi.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

Validate'ten önce `ollama ps` boştu ve panoda başka bir gerçek deney görünmüyordu.

| Kontrol | Komut | Sonuç |
|---|---|---|
| validate | `tools/validate.py ai-saldiri-33` (PAFTA_DATA=`<scratchpad>/sl33-kabul`) | **TEMİZ**, 9 kontrol (adım yapısı da doğrulandı) |
| tahmin | `docs/denetim/araclar/tahmin.py . ai-saldiri-33` | 1 tahmin, **0 şüpheli** |
| mutasyon | `kirp_gercek.py` kopyası, ardından `mutasyon.py --en-cok 1000 ai-saldiri-33` | 12 + 21 + 24 = 57 mutant, **0 geçen**; kopya silindi |
| kopya sondası | `kopya_sonda.py ai-saldiri ai-saldiri-33 ...` | 6/6 **fail → korunuyor**. Doğru çözüme yalnız `import inspect` ya da `eval('1')` eklendiğinde de fail. Kanıt yazılmadı. |

Kopya sondasında üç `*_referans` işlevi altı yoldan bağlanmaya çalışıldı: takma ad, öznitelik, `getattr`, `inspect` + `exec`, `*` import + `globals()`, `importlib` + `__dict__`.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/sl33-kabul/ai-kanit/saldiri-33-kv-cache-timing-*.json`. Kabul `true`, 6 kontrolün 6'sı doğru.
- **Model:** `qwen3:4b-instruct-2507-q4_K_M`.
- **Ham süreler:**
  - Miss: 4032, 658, 638 ms.
  - Hit: 111, 77, 72 ms.
- **Medyanlar:** Hit 77 ms, miss 658 ms, fark 581 ms. Eşik 367,5 ms'de doğruluk 1,0.
- **Bulgu:**
  - İlk miss ölçümü (4032 ms) modelin GPU'ya yüklenmesini de içeriyor. Medyan bu aykırı değerden etkilenmedi; dersin anlattığı aykırı değer ve medyan konusu canlı veride de görüldü.
  - Kontrol adayı (`aday-gurultu-kontrol`) sinyal vermedi.
  - Bu sonuç tek kullanıcılı yerel bir ölçümdür ve 3 tekrara dayanır; prompt çalma ya da çok kiracılı sızıntı kanıtı değildir.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.** Kontrol ve dosya erişimi yalnız CLI ve runner üzerinden doğrulandı.
- **Kusurlu başlangıç kodu Çalıştır modunda ayrıca koşturulmadı.** Kontrol'deki davranışı validate ile doğrulandı.
- **Kurulum, indirme, commit/push ve puan yazımı yapılmadı.** Ollama sunucusuna dokunulmadı.
