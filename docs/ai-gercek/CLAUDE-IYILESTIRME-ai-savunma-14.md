# ai-savunma-14 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Denetçinin eksikleri ve karşılıkları

| Eksik | Yapılan |
|---|---|
| Görünür örnek veri ve kusurlu başlangıç kodu yok | 3 fixture dosyası ve README eklendi; setup `hazirla("ai-savunma-14")` çağırıyor. Bütün başlangıç kodları kusurlu koda çevrildi. |
| Tablo ve sentetik veri notu yok | İlk anlatıma eklendi. |
| Saldırganın neyi denediği ve savunmanın neden kırıldığı az anlatılıyor | Anlatım blokları **~400 → 893 kelime** (472 + 41 + 127 + 103 + 150). Eklenen konular aşağıda. |

Eklenen anlatım konuları:
- **Saldırganın denedikleri:**
  - Metadata servisi ve iç panel hedefleri.
  - `@` kullanıcı bilgisi ve sonek hileleri.
  - `[::1]` ya da `0x7f000001` gibi loopback yazımları.
  - DNS rebinding.
- **Savunmanın kırıldığı yerler:**
  - Alt dizge araması.
  - `netloc` ile `hostname` karışıklığı.
  - İlk ya da "en az bir genel" adres mantığı.
  - Örtük portu ve yönlendirmeyi denetlememek.
- Çıktı okuma (`hedef` alanı) ve her göreve sık tuzaklar.

## Diğer değişiklikler

- **Tablo:**
  - **Gerçekte ne olur:** Ajan fetch/crawler araçları, Squid/Envoy egress proxy, IMDS uç noktaları; izin listesi, DNS genel adres denetimi, bağlantı sabitleme, yönlendirme sınırı.
  - **Ders ne kullanır:** Görev 1–3 sentetik politika, URL ve çözüm kullanır. Son adım yerel modelin `istek_at` önerilerini denetler; **istek atılmaz**.
  - **Ders ne söyleyemez:** Gerçek DNS, TLS ve proxy sınanmaz. IDN/punycode, zone kimliği ve ayrıştırıcı farkları tam kapsanmaz. İki senaryo oran vermez.
- **Netleştirme:** İlk anlatıma son adımda URL'lerin yerel modelden geldiği, ama yine hiçbir isteğin atılmadığı eklendi.
- **Görünür fixture** (`tracks/ai-savunma/fixtures/ai-savunma-14/`). Beklenen değerler dersin kendi çözümleriyle hesaplandı.
  - `veri/politikalar.json`: 9 politika. 2 geçerli. 7 `ValueError`: `izin`, IP literal, büyük harf, joker, port 80, yönlendirme 10, sondaki nokta.
  - `veri/url_istekleri.json`: Politika, 11 URL ve 4 bozuk girdi. URL'ler şunları kapsıyor:
    - AWS ve GCP metadata.
    - **`api.ornek.com@evil.test`** ve **`api.ornek.com.evil.test`** hileleri.
    - `[::1]`.
    - 8080, `ftp` ve fazla yönlendirme.
    - Büyük harfli host (`hostname` küçük harfe çevirir).
  - `veri/dns_cozumleri.json`: Politika, 8 çözüm ve 4 bozuk girdi. Çözümler: **rebinding** (genel ve `127.0.0.1` birlikte), `169.254.169.254`, CGNAT `100.64.0.10`, `::ffff:10.0.0.5`, multicast, boş yanıt, başka alan.
- **Kusurlu başlangıç kodları:**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | `izin` varsayılanı; alan, port ve yönlendirme doğrulaması yok; kopya yok | 9 politikanın 7'si yanlış |
  | 2 | Alt dizge alan araması; kullanıcı bilgisi ve yönlendirme yok; örtük port yok; ilk nedende dur; doğrulama ve sıralama yok | 11 URL'nin 6'sı, sıra ve 4 bozuk girdinin 3'ü yanlış; `kullanici-hilesi` ve `sonek-hilesi` **hazır** çıkıyor |
  | 3 | Yalnız bütün adresler `127.`/`10.` ise ret; boş yanıt geçiyor; doğrulama ve sıralama yok | 8 çözümün 6'sı, sıra ve 4 bozuk girdinin 4'ü yanlış; rebinding **hazır** çıkıyor |
  | Gerçek deney | Görev 2'nin kusurlu işlevi | Sözleşme düşüyor; var olan `all(sonuclar)` kapısı canlı deneyi başlatmıyor (ikinci kanıt `kabul: false`) |

- **Kopya koruması:**
  - Var olan yasak listesi korundu; `kanit_yaz` eklendi.
  - AST kontrolü eklendi: takma adlı ve `*` import, `inspect`, `importlib`, `runpy`, `exec`, `eval`, `compile`, `__builtins__`. İhlalde `stop()` çalışıyor.
- **Değiştirilmeyenler:** `sandbox/ai_gercek_ai_savunma_14.py`, var olan bütün testler, ortak dosyalar, `engine/` ve `web/`.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

Validate'ten önce `ollama ps` boştu.

| Kontrol | Sonuç |
|---|---|
| validate `ai-savunma-14` | **TEMİZ**, 9 kontrol, ilk koşuda. Adım yapısı değişmedi. |
| tahmin | 1 tahmin, **0 şüpheli** |
| mutasyon (`kirp_gercek.py` kopyası) | 14 + 19 + 10 = **43 mutant, 0 geçen**; kopya silindi |
| kopya sondası | 6/6 **fail → korunuyor**. Sandbox'ta kopyalanabilecek bir `referans` işlevi yok. Sondalar, doğru çözüme yasak `ai_lab.kanit_yaz`'ı altı yoldan bağladı. Doğru çözüme yalnız `import inspect` ya da `eval('1')` eklendiğinde de fail. |

Görünür veri kontrolü: Üç başlangıç kodu ve çözüm görünür fixture'larla ayrı ayrı çalıştırıldı. Tablodaki kusurlar görüldü; çözümler bütün beklenen değerleri verdi.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/sv14-kabul/ai-kanit/savunma-egress-*.json` (kabul `true`).
- **Ölçüm:** Modelin 2 gerçek URL önerisi denetlendi.
  - Güvenli öneri → `api.ornek.com`, `hazir`.
  - SSRF önerisi → `metadata.google.internal`, `reddet`, nedenler `["sema", "alan"]`.
- **Değerlendirme:** Model metadata hedefini `http` şemasıyla önerdi. Default-deny izin listesi ve HTTPS zorunluluğu iki ayrı nedenle durdurdu; hiçbir istek atılmadı. Tek koşudan alınmış dar bir gözlemdir.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.**
- **Kurulum, indirme, commit/push ve puan yazımı yapılmadı.** Ollama sunucusuna ve modellere dokunulmadı.
