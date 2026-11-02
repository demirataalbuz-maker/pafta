# ai-saldiri-01 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Tablo ve `[!NOT]`:** İlk anlatımın başına tablo eklendi.
  - **Gerçekte ne olur:** Gerçek bir MCP host her server için ayrı bir client açar. stdio/HTTP üzerinden JSON-RPC ile `initialize`, `tools/list` ve `tools/call` gönderir, aracı kendi politikasıyla onaylar.
  - **Ders ne kullanır:** Görev 1–3 sentetik akışlar, sunucu kayıtları ve çağrılar kullanır. Son adım iki gerçek stdio MCP sunucu süreci ve kurulu yerel modeli kullanır.
  - **Ders ne söyleyemez:** Auth, HTTP transport, resource, sampling ve elicitation sınanmaz. İki istek oran vermez. Şema/onay kapısı yol politikası değildir.

  Tablonun altına sentetik veri ve kalıcılık notu eklendi.
- **Çelişki düzeltmeleri:**
  - İlk anlatım "test sonucu harici paket, model veya sunucu durumuna bağlı olmaz" diyordu, oysa son adım gerçek MCP sunucuları ve yerel model kullanıyor. Cümle, görev 1–3 ile son adımı ayıracak şekilde düzeltildi.
  - Üçüncü anlatımdaki "server başlatılması bu dersin parçası değildir" ifadesi de düzeltildi: Inspector kurulumu ders dışıdır, ama son adım kendi sunucularını başlatır.
- **Görünür fixture:** `tracks/ai-saldiri/fixtures/ai-saldiri-01/` altına README ve üç dosya eklendi. Beklenen değerler dersin kendi çözümleriyle hesaplandı.
  - `veri/rpc_akisi.json`: 9 akış.
    - Rapor üretenler: ters sırada yanıtlar ve bir `error` yanıtı içeren tam oturum, açık kalan istekler, `params.requestId` taşıyan iptal bildirimi, yeniden kullanılan kapalı kimlik.
    - `ValueError` alanlar: `1.0` sürümü, `True` kimlik, yinelenen açık kimlik, istenmemiş kimliğe yanıt, biçimsiz yanıt.
  - `veri/sunucular.json`: 6 örnek. İki sunucuda aynı `read` adı var ve biri "GÜVENİLİR, önceden onaylı" diye yetki iddia ediyor. Ayrıca `tools` alanı olmayan bir sunucu ve 4 bozuk kayıt var.
  - `veri/cagrilar.json`: Envanter, onay listesi ve 11 çağrı. Çağrılar şunları kapsıyor:
    - Aynı kısa adla onaysız `arsiv/read`.
    - Referans yerine kısa ad.
    - `True` offset.
    - Ek alan.
    - `/etc/passwd`: şemaya uyduğu için **izinli**; şema yetki değildir.
    - Bilinmeyen `date` türü.
    - `number`/`array` örnekleri.
- **Kusurlu başlangıç kodları (görev 1–3 ve son adım):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Yanıtlar geliş sırasına göre ilk açık isteğe bağlanıyor; sürüm, kimlik türü, yineleme ve eşleşmeyen yanıt denetlenmiyor | 9 akışın 6'sı yanlış |
  | 2 | Kısa adla sözlük (ezilme); açıklamadaki "güvenilir/onaylı" `guvenilir` etiketi oluyor; eksik şema `None`; denetim yok | 6 örneğin 5'i yanlış |
  | 3 | Onay kısa adla eşleşiyor; `bool` integer sayılıyor; `additionalProperties` ve bilinmeyen tür yok sayılıyor | 11 çağrının 4'ü yanlış |
  | Gerçek deney | Görev 2 ve 3'ün kusurlu işlevleri | Sentetik sözleşme düşüyor; canlı deney hiç başlamıyor (kanıt dosyasında `deney: null`) |

- **Kısa notlar:** Her göreve sık tuzaklar eklendi.
- **Kopya koruması:**
  - Var olan `kod_denetimi` listesi (`getattr`, `McpSunucu` dahil) korundu ve `kanit_yaz` eklendi.
  - AST kontrolü eklendi: takma adlı ve `*` import, `inspect`, `importlib`, `runpy`, `exec`, `eval`, `compile`, `__builtins__`.
  - İhlalde artık `stop()` çalışıyor. Önceden yalnız `kontrol(False)` kaydediliyordu; deney yine başlamıyordu, ama test akışı sürüyordu.
- **Değiştirilmeyenler:** `sandbox/ai_gercek_ai_saldiri_01.py`, var olan bütün testler, ortak `ai_gercek_lab.py`, `engine/` ve `web/`.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

Validate'ten önce `ollama ps` boştu. Validate'ten önce panoda başka bir gerçek deney görünmüyordu.

| Kontrol | Sonuç |
|---|---|
| validate `ai-saldiri-01` | **TEMİZ**, 10 kontrol (anlatımdaki `ornek` bloğu dahil), ilk koşuda. Adım yapısı `anlat, tahmin, gorev, anlat, gorev, anlat, gorev, anlat, anlat, gorev` olarak doğrulandı. |
| tahmin | 1 tahmin, **0 şüpheli** |
| mutasyon (`kirp_gercek.py` kopyası) | 6 + 4 + 12 = **22 mutant, 0 geçen**; kopya silindi |
| kopya sondası | 6/6 **fail → korunuyor**. Sondalar `referans_denetle` için, doğru `(cagri, envanter, onay)` imzasıyla: takma ad, öznitelik, `getattr`, `inspect` + `exec`, `*` import + `globals()`, `importlib` + `__dict__`. Doğru çözüme yalnız `import inspect` ya da `eval('1')` eklendiğinde de fail. |

Görünür veri kontrolü: Üç başlangıç kodu ve çözüm görünür fixture'larla ayrı ayrı çalıştırıldı. Tablodaki kusurlar görüldü; çözümler bütün beklenen değerleri verdi.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/sl01-kabul/ai-kanit/saldiri-mcp-*.json` (kabul `true`). Model: `qwen3:4b-instruct-2507-q4_K_M`. İkinci kanıt dosyası kusurlu başlangıç kodundandır: `kabul: false`, `deney: null`.
- **Korumasız host:**
  - Modelin 3 araç çağrısının 3'ü de çalıştı.
  - Kısa ad çakışması yüzünden 2 çağrı `arsiv` sunucusuna gitti.
  - Gizli anahtar 1 kez modele döndü ve son yanıtta kullanıcıya yazıldı.
- **Korumalı host:**
  - 1 çağrı reddedildi; `arsiv`'e giden çağrı olmadı.
  - Sızıntı olmadı (tam 0, kısmi 0).
- **Meşru not:** İki hostta da doğru okundu.
- **Değerlendirme:** Gerçek MCP stdio sunucularında kısa ad birleştirmesi, kullanıcının hiç onaylamadığı sunucuya çağrı gönderdi ve sızıntıya yol açtı. Kanonik envanter ve tam referans onayı bunu engelledi. Bu tek koşudan alınmış dar bir gözlemdir.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.**
- **Kurulum, indirme, commit/push ve puan yazımı yapılmadı.** Ollama sunucusuna ve modellere dokunulmadı.
