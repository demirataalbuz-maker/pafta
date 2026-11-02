# ai-savunma-09 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Denetçinin eksikleri ve karşılıkları

| Eksik | Yapılan |
|---|---|
| Görünür örnek veri ve kusurlu başlangıç kodu yok | 3 fixture dosyası ve README eklendi; setup `hazirla("ai-savunma-09")` çağırıyor. Bütün başlangıç kodları kusurlu koda çevrildi. |
| Tablo ve sentetik veri notu yok | İlk anlatıma eklendi. |
| Saldırganın neyi denediği ve savunmanın neden kırıldığı az anlatılıyor | Anlatım blokları **~330 → 850 kelime** (441 + 140 + 120 + 149). Eklenen konular aşağıda. |

Eklenen anlatım konuları:
- **Saldırganın denedikleri:** kartı harflerle ya da noktalı yazdırmak, telefon gruplarını değiştirmek, `[at]`/`[dot]`, JSON alanlarına bölmek, PII'yi log ya da araç argümanı kanalına taşımak.
- **Savunmanın kırıldığı yerler:** Luhn ve aralık denetimi eksik olunca yanlış alarm ve kural gevşetme; ofset sırası gözetilmezse değerin bir kısmının açıkta kalması.
- Her göreve çıktı okuma ve sık tuzaklar.

## Diğer değişiklikler

- **Tablo:**
  - **Gerçekte ne olur:** Presidio tanıyıcı ve anonymizer, LLM Guard çıkış tarayıcıları, kurumsal DLP.
  - **Ders ne kullanır:** Görev 1–3 sentetik metin, aralık ve olaylarla çalışır. Son adım yerel modelin sentetik kayıttan ürettiği çıktıyı kullanır.
  - **Ders ne söyleyemez:** Ad, adres, TC kimlik ve yeniden biçimlendirilmiş değerler kaçar. Tek çıktı oran vermez. Redaksiyon başka kanallardaki sızıntıyı kapatmaz.
- **Netleştirme:** İlk anlatımdaki "Dış servis veya gerçek kişi verisi yoktur" cümlesine görev 1–3'ün model çağırmadığı ve son adımın yerel modeli sentetik kayıtla çağırdığı eklendi.
- **Görünür fixture** (`tracks/ai-savunma/fixtures/ai-savunma-09/`). Beklenen değerler dersin kendi çözümleriyle hesaplandı.
  - `veri/pii_metinleri.json`: 11 metin.
    - Bulunanlar: dört tür birden, tireli Mastercard testi, 13 haneli kart, iki e-posta.
    - Bulunmayanlar: `256.10.0.1`, `1.2.3.4.5`, Luhn'suz 16 hane, biçimi farklı telefon (bilinçli sınır), `admin@localhost`.
    - NUL → `ValueError`.
  - `veri/donusum_ornekleri.json`: 9 örnek. Standart, her şeyi redakte ve her şeyi koru politikaları; 3 karakterlik tam maske; bitişik aralık. 4 `ValueError`: çakışma, eksik tür, `sil` eylemi, taşan bitiş.
  - `veri/dlp_olaylari.json`: 9 olay (log/dış API/yanıt × tür, boş varlık) ve 4 bozuk girdi.
- **Kusurlu başlangıç kodları:**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | IP aralığı ve komşu kontrolü yok; Luhn yok; gevşek telefon kalıbı; değer rapora giriyor; sıralama yok | 11 metnin 9'u yanlış |
  | 2 | Baştan dönüşüm (ofset kayması); kısa değer maskelenmiyor; `koru` sayılıyor; doğrulama yok | 9 örneğin 9'u yanlış |
  | 3 | Log'da yalnız kart; dış API'de e-posta/telefon geçiriliyor; IP incelenmiyor; tür sırası ve doğrulama yok | 9 olayın 5'i ve sıra yanlış; 4 bozuk girdinin 4'ü yanlış |
  | Gerçek deney | Görev 2'nin kusurlu işlevi | Sözleşme düşüyor; `all(sonuclar)` kapısı canlı deneyi başlatmıyor (ikinci kanıt `kabul: false`) |

- **Kopya koruması:**
  - Var olan yasak listesi korundu; `kanit_yaz` eklendi.
  - AST kontrolü eklendi: takma adlı ve `*` import, `inspect`, `importlib`, `runpy`, `exec`, `eval`, `compile`, `__builtins__`. İhlalde `stop()` çalışıyor.
- **Değiştirilmeyenler:** `sandbox/ai_gercek_ai_savunma_09.py`, var olan bütün testler, ortak dosyalar, `engine/` ve `web/`.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

Validate'ten önce `ollama ps` boştu.

| Kontrol | Sonuç |
|---|---|
| validate `ai-savunma-09` | **TEMİZ**, 9 kontrol, ilk koşuda. Adım yapısı `anlat, tahmin, gorev, anlat, gorev, anlat, gorev, anlat, gorev` olarak doğrulandı. |
| tahmin | 1 tahmin, **0 şüpheli** |
| mutasyon (`kirp_gercek.py` kopyası) | 26 + 19 + 11 = **56 mutant, 0 geçen**; kopya silindi |
| kopya sondası | 6/6 **fail → korunuyor**. Doğru çözüme yasak `referans_bul` altı yoldan bağlandı: takma ad, öznitelik, `vars()`, `inspect` + `exec`, `*` import + `globals()`, `importlib` + `__dict__`. Son adımdaki `pii_donustur`'un sandbox'ta birebir referansı yok. Doğru çözüme yalnız `import inspect` ya da `eval('1')` eklendiğinde de fail. |

Görünür veri kontrolü: Üç başlangıç kodu ve çözüm görünür fixture'larla ayrı ayrı çalıştırıldı. Tablodaki kusurlar görüldü; çözümler bütün beklenen değerleri verdi.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/sv09-kabul/ai-kanit/savunma-dlp-*.json` (kabul `true`).
- **Ölçüm:**
  - Gerçek model çıktısında 3 PII bulundu: e-posta, IPv4 ve kart.
  - DLP 3 dönüşüm uyguladı; dönüşüm sonrası kalan PII 0.
  - Kanal `dis_api`, karar `durdur` (kart var).
- **Not:** Telefon tanınan PII arasında yoktu. Kanıt dosyası ham metni saklamadığı için modelin telefonu yeniden mi biçimlendirdiğini yoksa hiç mi yazmadığını bu koşudan doğrulayamadım. "Kalan PII 0" yalnız tanıyıcının gördüğü biçimler için geçerlidir; anlatımın son notu da bunu söylüyor.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.**
- **Kurulum, indirme, commit/push ve puan yazımı yapılmadı.** Ollama sunucusuna ve modellere dokunulmadı.
