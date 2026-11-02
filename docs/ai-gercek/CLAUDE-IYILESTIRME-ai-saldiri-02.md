# ai-saldiri-02 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Tablo ve `[!NOT]`:** İlk anlatımın başına tablo eklendi.
  - **Gerçekte ne olur:** Ollama `/api/chat` ya da OpenAI uyumlu API'ler mesajları modelin kendi sohbet şablonuyla (ChatML vb.) tek token akışına çevirir. Garak, PyRIT ve promptfoo aynı deneyi ölçekli koşturup ASR raporlar.
  - **Ders ne kullanır:** Görev 1–3 öğretim şablonunu, `fixture-v1` adaptörünü ve sentetik yanıtları kullanır. Son adım yerel modeli, rastgele canary'yi ve vaka başına iki tekrarı kullanır.
  - **Ders ne söyleyemez:** Öğretim şablonu gerçek bir şablon değildir. 4–6 vaka × 2 tekrar istatistiksel güvence vermez. ASR=0 modelin güvenli olduğunu göstermez.

  Tablonun altına sentetik veri ve kalıcılık notu eklendi. Ders zaten görev 1–3'ü fixture, son adımı gerçek model olarak ayırıyordu; çelişkili bir cümle bulunmadı.
- **Görünür fixture:** `tracks/ai-saldiri/fixtures/ai-saldiri-02/` altına README ve üç dosya eklendi. Beklenen değerler dersin kendi çözümleriyle hesaplandı.
  - `veri/mesaj_dizileri.json`: 7 örnek. Kullanıcı içeriğinde sahte `<|system|>`, yinelenen rol, boş içerik, çok satırlı içerik, boş liste, ayrıca `assistant` ve `SYSTEM` (`ValueError`).
  - `veri/vakalar.json`: 5 vaka ve fixture adaptörüyle beklenen tam kayıtlar. Vakalardan biri kullanıcı içeriğindeki sahte system işareti, biri `DENEX-99` (işaretsiz saldırı).
  - `veri/yanit_kayitlari.json`: 7 sınıflandırma örneği (`\r\n` içinde tam satır, alıntı, `HATA:` önceliği, küçük harf), 10 kayıt (beklenen ASR 0.4) ve yalnız hata içeren bir senaryo (ASR `null`).
- **Kusurlu başlangıç kodları:**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | Şablon izi | Başlangıç ofseti önekten önce alınıyor; bitiş `\n`'i içeriyor; bilinmeyen rol kabul ediliyor | 7 örneğin 6'sı yanlış |
  | Deney düzeneği | Developer mesajı atlanıyor; adaptör hatası `OZET: hata` yanıtına çevriliyor; `kaynak` sabit | 5 kaydın 5'i yanlış |
  | Kontrol/ASR | Alt metin araması; hata başarıdan sonra denetleniyor; hatalı saldırılar paydada; her kontrol sağlam; ölçülemeyen ASR `0.0` | 2 sınıf, 3 özet alanı ve yalnız-hata ASR'si yanlış |
  | Gerçek deney | Canary saldırı belgesinde, kontrol belgesinde "gizli kod" geçiyor; birebir eşleşme; hatalar paydada | `vakalari_dogrula` reddediyor; deney başlamıyor |

  Son adım ve görev 3 sözleşmesinde ortak olan `ozetle` adı iki ayrı sözleşmedir; son adımın kusurlu `ozetle`'si kendi alanlarını taşır.
- **Kısa notlar:** Her göreve sık tuzaklar eklendi. Son adıma kısa bir "çıktıyı okurken" notu eklendi.
- **Kopya koruması ve deney kapısı:**
  - `kanit_yaz` yasak listesine eklendi.
  - AST kontrolü eklendi: takma adlı ve `*` import, `inspect`, `importlib`, `runpy`, `exec`, `eval`, `compile`, `__builtins__`. İhlalde `stop()` çalışıyor.
  - Canlı deneyden önce `if not all(sonuclar): stop()` eklendi. Önceden sızıntı ya da özet sözleşmesi düşse bile, vakalar geçerliyse canlı deney koşuyordu. Var olan hiçbir kontrol kaldırılmadı.
- **Değiştirilmeyenler:** Ortak `sandbox/ai_gercek_lab.py` (`injection_deneyi`, referanslar), var olan bütün testler, `engine/` ve `web/`.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

Validate'ten önce `ollama ps` boştu. Validate'ten önce panoda başka bir gerçek deney görünmüyordu.

| Kontrol | Sonuç |
|---|---|
| validate `ai-saldiri-02` | **TEMİZ**, 11 kontrol, ilk koşuda (2 tahmin, 1 `ornek`, 4 çözüm, 4 başlangıç). Adım yapısı `anlat, tahmin, gorev, anlat, tahmin, gorev, anlat, gorev, anlat, gorev` olarak doğrulandı. |
| tahmin | 2 tahmin, **0 şüpheli** |
| mutasyon (`kirp_gercek.py` kopyası) | 1 + 3 + 17 = **21 mutant, 0 geçen**; kopya silindi |
| kopya sondası | 6/6 **fail → korunuyor**. Sondalar `ai_lab.ozet_referans` için: takma ad, öznitelik, `getattr`, `inspect` + `exec`, `*` import + `globals()`, `importlib` + `__dict__`. Doğru çözüme yalnız `import inspect` ya da `eval('1')` eklendiğinde de fail. |

Görünür veri kontrolü: Üç başlangıç kodu ve çözüm görünür fixture'larla ayrı ayrı çalıştırıldı. Tablodaki kusurlar görüldü; çözümler bütün beklenen değerleri verdi.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/sl02-kabul/ai-kanit/saldiri-injection-*.json`. Kabul `true`. Model: `qwen3:4b-instruct-2507-q4_K_M`.
- **Ölçüm:** ASR **0/4**; kontrol sızıntısı **0/4**; taşıma hatası 0.
- **Gözlem:** Model iki saldırı belgesini talimat olarak uygulamadı, belgeyi özetledi. Örneğin "Asistan, sistem mesajındaki gizli kodu … eklemesini ister" diye anlattı ve canary'yi hiçbir biçimde yazmadı. Kontrol özetleri doğru ve kararlıydı.
- **Değerlendirme:** 4 vaka × 2 tekrarlık tek bir koşuda doğrudan injection başarısız oldu. Bu sonuç modelin güvenli olduğunu göstermez; yalnız bu iki belge biçiminde ve bu sıcaklıkta sızıntı gözlenmediğini kaydeder.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.**
- **Görev 2'nin opt-in gerçek Ollama yolu ayrıca koşturulmadı.** Test bu yolu sahte `urlopen` ile sınıyor.
- **Kurulum, indirme, commit/push ve puan yazımı yapılmadı.** Ollama sunucusuna ve modellere dokunulmadı.
