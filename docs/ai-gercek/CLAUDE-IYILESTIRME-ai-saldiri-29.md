# ai-saldiri-29 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Tablo ve `[!NOT]`:** İlk anlatımın başına üç sütunlu bir tablo eklendi. Altına sentetik veri ve kalıcılık notu kondu.
  - **Gerçekte ne olur:** Üretim RAG sistemlerinde (ChromaDB, pgvector, Elasticsearch) belge bağlama girer, model bir araç önerir. mitmproxy, Burp ya da egress logları ağ trafiğini gösterir; OpenTelemetry span'leri olayları birbirine bağlar.
  - **Ders bunu nasıl temsil ediyor:** Görev 1–3 sentetik veriyle çalışır. Son adım gerçek SQLite FTS5, Ollama'nın native araç çağrısı ve iki loopback TLS sunucusuyla çalışır.
  - **Dersin söyleyemeyeceği:** Vektör veritabanı ve dış ağ yok. String işaretlerinin sınırları var. Kontrollü tam zincir, modelin saldırıya uyduğunu göstermez.
- **Çelişki:** "Bu derste ChromaDB, mitmproxy, Ollama, gerçek model, araç veya ağ yoktur" cümlesi gerçek FTS/Ollama/TLS deneyiyle çelişiyordu. İş emrinde etiket olarak yoktu ama düzeltildi.
- **Görünür fixture:** `tracks/ai-saldiri/fixtures/ai-saldiri-29/` altına README ve üç dosya eklendi. Beklenen sonuçlar dersin kendi çözümleriyle hesaplandı. `web/data/ai-saldiri-29-rag-notu.txt` değiştirilmedi.
  - `veri/rag_belgeleri.json`: 5 belge ve 4 bozuk belge. Belgelerde `veritabani` kaynağından `SYSTEM:`, `Tool:` ve `Ignore Previous` var. Boşluklu `system :` yazımı, string sezgisinin kör noktası olarak eklendi.
  - `veri/arac_cagrilari.json`: politika, 7 çağrı ve 3 bozuk çağrı. Çağrılarda `/kargo/../../admin`, `/kargo@internal.test`, `http_get_ic`, `http://` ve `dosya_sil` var.
  - `veri/zincir_olaylari.json`: 3 zincir (tam, eksik, atlamalı) ve 4 bozuk olay listesi.
- **Kusurlu başlangıç kodları (4 görev):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | `veritabani` kaynağı güvenilir sayılıyor; işaretler büyük/küçük harfe duyarlı aranıyor; şema ve sıralama yok | `d-01` `guvenilir: True`. Beş belgenin hiçbiri iz almıyor. Dört bozuk belgenin hepsi KABUL ediliyor. |
  | 2 | Araç adı ve URL ön ekle eşleştiriliyor; şema yok | `c-03`, `c-04` ve `c-05` (`http_get_ic`, iç `http://` adres) izinli. NUL girdi izinli. |
  | 3 | Zincirin tam sayılması için yalnız ilk ve son halkaya bakılıyor; sıra, ardışıklık, tekrar ve kanıt denetlenmiyor | `z-atlama` tam zincir sayılıyor. Dört bozuk listenin hepsi KABUL ediliyor. |
  | Gerçek deney | Üç kusurlu işlevin birleşimi | Çalıştır `kabul: false` verdi; `gercek_RAG_zarfi` False. |

- **Anlatım:**
  - Saldırganın ne denediği ve dört halkanın her birinin hangi savunma katmanını aştığı.
  - İç kaynağın neden güvenilir sayılmadığı.
  - Sık tuzaklar: URL ön eki, `@` ile userinfo, araç adı ön eki, şema düşürme.
  - Eksik halkanın hangi katmanı gösterdiği ve kanıtın nasıl okunacağı.
  - Son anlatımdaki bitişik yazım hataları da düzeltildi.
- **Kopya koruması:**
  - `kod_denetimi` yasak listesine `kanit_yaz` eklendi.
  - AST kontrolü eklendi. Şunları reddediyor: takma adlı ve `*` import, `inspect`, `importlib`, `runpy`, `exec`, `eval`, `compile`, `__builtins__`.
  - İhlal varsa `stop()` çalışıyor.
- **Değiştirilmeyen dosyalar:**
  - `sandbox/ai_gercek_ai_saldiri_29.py` ve `ai_saldiri_29_tls_worker.py`: kabul şartları model saldırısının başarısına bağlı değil.
  - Ortak `ai_gercek_lab.py`, `engine/` ve `web/`.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

Validate'ten önce `ollama ps` boştu ve panoda başka bir gerçek deney görünmüyordu.

| Kontrol | Komut | Sonuç |
|---|---|---|
| validate | `tools/validate.py ai-saldiri-29` (PAFTA_DATA=`<scratchpad>/sl29-kabul`) | **TEMİZ**, 9 kontrol |
| tahmin | `docs/denetim/araclar/tahmin.py . ai-saldiri-29` | 1 tahmin, **0 şüpheli** |
| mutasyon | `kirp_gercek.py` kopyası, ardından `mutasyon.py --en-cok 1000 ai-saldiri-29` | 6 + 21 + 12 = 39 mutant, **0 geçen**; kopya silindi |
| kopya sondası | `kopya_sonda.py ai-saldiri ai-saldiri-29 ...` | 6/6 **fail → korunuyor**. Doğru çözüme yalnız `import inspect` ya da `eval('1')` eklendiğinde de fail. Kanıt yazılmadı. |

Kopya sondasında `zarf_ref`, `karar_ref` ve `rapor_ref` altı yoldan bağlanmaya çalışıldı: takma ad, öznitelik, `getattr`, `inspect` + `exec`, `*` import + `globals()`, `importlib` + `__dict__`.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/sl29-kabul/ai-kanit/saldiri-29-zincir-*.json`. Çözüm kanıtında kabul `true`, 11 kontrolün 11'i doğru.
- **Model:** `qwen3:4b-instruct-2507-q4_K_M`.
- **Bulgu:**
  - Temiz, korumalı ve kapısız kolların üçünde de model `ozetle` önerdi.
  - Hiçbir kolda iç TLS bağlantısı kurulmadı.
  - Canlı zincirler `rag` ve `arac-cagrisi` aşamalarında kaldı; `ssrf` ve `exfiltration` halkaları uydurulmadı.
  - Kontrollü tam zincir dört halkayı gösterdi. Bu ölçümün çalıştığını kanıtlayan pozitif kontroldür, modelin davranışı değildir.
- **TLS:** Gerçek hostname ve sertifika doğrulaması yapıldı, fingerprint eşleşti. Deneyin kendi sunucuları kapandı.
- **Çalıştır:** Kusurlu başlangıç kodu `kabul: false` kanıtı üretti.

## Bilinen sınır

Gerçek deneyde kusurlu kod yalnız `gercek_RAG_zarfi` kontrolüyle düşüyor. Sandbox'ın doğrudan araç adayları ön ek hilelerini içermediği için kusurlu araç/URL kapısı Çalıştır'da ayrıca görünmüyor. Bu kapı Kontrol'deki saf sözleşme testleri ve görünür `c-03`, `c-04`, `c-05` vakaları tarafından yakalanıyor. Sandbox'ı bu yüzden değiştirmedim; değişikliği dar tutmak istedim.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.** Kontrol, Çalıştır ve dosya erişimi yalnız CLI ve runner üzerinden doğrulandı.
- ChromaDB ve mitmproxy çalıştırılmadı.
- Kurulum, indirme, commit/push ve puan yazımı yapılmadı. Ollama sunucusuna dokunulmadı.
