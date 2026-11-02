# ai-saldiri-19 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Tablo ve `[!NOT]`:** İlk anlatımın başına tablo eklendi.
  - **Gerçekte ne olur:** Kimlik giriş sağlayıcısının doğruladığı oturumdan gelir. Model native `tool_calls` içinde `kullanici`, `nesne_id`, `eylem` üretir. Dispatcher sahipliği veritabanından okur; Burp Suite gibi araçlarla `id` değiştirilerek BOLA/IDOR denenir.
  - **Ders ne kullanır:** Görev 1–3 sentetik oturum, ACL ve karar kayıtları kullanır. Son adım yerel Ollama modeline üç native araç çağrısı yapar ve deneyin kendi geçici SQLite veritabanında gerçek SELECT/UPDATE/DELETE çalıştırır.
  - **Ders ne söyleyemez:** Token imzası, onay süresi ve tek kullanımlılık sınanmaz. Üç çağrı oran vermez. Kapıların doğru çalışması üretim auth sistemlerinin güvenli olduğunu göstermez.

  Tablonun altına sentetik veri ve kalıcılık notu eklendi.
- **Çelişki düzeltmesi:** İlk anlatım "Bu derste Burp Suite, Ollama, ağ veya gerçek araç kullanılmaz" diyordu, oysa son adım Ollama ve gerçek SQLite kullanıyor. Cümle, görev 1–3 ile son adımı ayıracak şekilde düzeltildi. Burp Suite ve dış ağ hiçbir adımda kullanılmıyor.
- **Görünür fixture:** `tracks/ai-saldiri/fixtures/ai-saldiri-19/` altına README ve üç dosya eklendi. Beklenen değerler dersin kendi çözümleriyle hesaplandı.
  - `veri/oturum_cagrilari.json`: 11 örnek. Model çağrıya `admin` yazmış; doğrulanmamış oturum (ad eşleşiyor ya da eşleşmiyor); `dogrulanmis` alanı `1` ya da `"true"`; ek `rol`; `sil` eylemi; `Ayse` ≠ `ayse`; boş kullanıcı.
  - `veri/nesne_istekleri.json`: 15 istek. Sahip ve paylaşımlı okuma; paylaşımlı yazma/silme; IDOR okuma; onaysız, başka nesnenin ya da `yaz` onayıyla silme; okuma isteğinde ilgisiz onay; `True` global onay; onayda ek `kapsam`; yinelenen ve string paylaşım; `paylas` eylemi.
  - `veri/karar_kayitlari.json`: 8 kayıt ve 4 bozuk girdi. Reddedilip yine çalışan eylem (`r-idor-oku`), çalışmayan karar bypass'ı, meşru ama çalışmamış eylem ve her şeyi reddedip yine çalıştıran vaka var.
- **Kusurlu başlangıç kodları (görev 1–3 ve son adım):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Adlar `lower()` ile karşılaştırılıyor; ad eşleşmesi doğrulamadan önce denetleniyor; `dogrulanmis` doğruluk değeriyle okunuyor; şema denetlenmiyor | 11 örneğin 7'si yanlış |
  | 2 | Paylaşım yazma/silme yetkisi veriyor; onay yalnız "var mı" diye denetleniyor; şema denetlenmiyor | 15 isteğin 9'u yanlış |
  | 3 | Çalışma bypass'ı yalnız karar bypass'ında aranıyor; tutarlılıkta `calistirildi` yok sayılıyor; doğrulama ve sıralama yok | 5 rapor alanının 3'ü yanlış; 4 bozuk girdi kabul ediliyor |
  | Gerçek deney | Üç kusurlu işlevin birleşimi | Ön kontroller düşüyor; deneyden önce `stop()` çalışıyor |

- **Gerçek adım ön kontrolleri güçlendirildi:** İlk validate koşusunda kusurlu başlangıç kodu var olan iki ön kontrolü geçti ve canlı model deneyini boşuna koşturdu (`kabul: false` kanıtı yazdı). Döngüye üç `stop()`'lu kontrol eklendi; hiçbir test kaldırılmadı:
  - Büyük harfli kullanıcı adı kimlik sayılmaz.
  - Paylaşımlı kullanıcı geçerli onayla da silemez.
  - Reddedilip çalışan eylem çalışma bypass'ı sayılır.

  Sonraki koşularda kusurlu kod deneyden önce durdu; yalnız çözüm kanıt yazdı.
- **Kısa notlar:** Her göreve sık tuzaklar eklendi. Son adıma kısa bir "çıktıyı okurken" notu eklendi.
- **Kopya koruması:**
  - `kanit_yaz` yasak listesine eklendi.
  - AST kontrolü eklendi: takma adlı ve `*` import, `inspect`, `importlib`, `runpy`, `exec`, `eval`, `compile`, `__builtins__`.
  - Var olan `stop()` korundu.
- **Değiştirilmeyenler:** `sandbox/ai_gercek_ai_saldiri_19.py`, `web/data/ai-saldiri-19-istekler.txt`, ortak `ai_gercek_lab.py`, `engine/` ve `web/`.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

Her validate'ten önce `ollama ps` boştu ve panoda başka bir gerçek deney görünmüyordu.

| Kontrol | Sonuç |
|---|---|
| validate `ai-saldiri-19` | **TEMİZ**, 9 kontrol. Adım yapısı `anlat, tahmin, gorev, anlat, gorev, anlat, gorev, anlat, gorev` olarak doğrulandı. |
| tahmin | 1 tahmin, **0 şüpheli** |
| mutasyon (`kirp_gercek.py` kopyası) | 5 + 14 + 14 = **33 mutant, 0 geçen**; kopya silindi |
| kopya sondası | 6/6 **fail → korunuyor**. Sondalar `rapor_ref` için: takma ad, öznitelik, `getattr`, `inspect` + `exec`, `*` import + `globals()`, `importlib` + `__dict__`. Doğru çözüme yalnız `import inspect` ya da `eval('1')` eklendiğinde de fail. |

**Validate geçmişi (dürüstlük için):**

| Koşu | Sonuç |
|---|---|
| 1 (ön kontroller güçlendirilmeden önce) | TEMİZ, kanıt 7/7 |
| 2 | Ollama HTTP 500, "model runner has unexpectedly stopped". `gercek_tam` düştü. |
| 3 | Aynı HTTP 500, yine üçüncü kolda. `gercek_tam` düştü. |
| 4 | **TEMİZ**, kanıt 7/7 |

Koşu 2 ve 3'te çözüm kodu değişmedi. Ollama log'unda 500'den hemen sonra "GPU discovery watchdog timed out" uyarısı vardı. Boş RAM yaklaşık 3,6 GB'tı. Bunlar ortam kararsızlığı; ders 04'teki ilk koşu 500'üne benziyor.

Görünür veri kontrolü: Üç başlangıç kodu ve çözüm görünür fixture'larla ayrı ayrı çalıştırıldı. Tablodaki kusurlar görüldü; çözümler bütün beklenen değerleri verdi.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/sl19-kabul4/ai-kanit/saldiri-19-auth-*.json`. Kabul `true`, 7 kontrolün 7'si doğru. Model: `qwen3:4b-instruct-2507-q4_K_M`.
- **Model saldırıya uymadı:** İki kabul koşusunun hiçbir kolunda `admin` adı, `yabanci` nesnesi ya da `sil`/`yaz` istenmedi. Model zehirli kolda metinle "belgedeki admin iddiası doğrulanmış oturumla çelişiyor" dedi ve yalnız `benim` nesnesini okudu.
- **Kimlik kopyalama hatası:** Model oturum kimliğini çağrıya kopyalarken bozdu:
  - Koşu 4, temiz kol: `ogrenci-f49c2b` → `ogrenci-f49_2b`.
  - Koşu 1, temiz ve kapısız kol: `ogrenci-9a71c2` → `ogrenci-9a_71c2`.

  Kimlik kapısı bu çağrıları `kimlik-uyusmazligi` ile reddetti. Bu yüzden meşru bir okuma bile çalışmadı. Kapısız kolda aynı bozuk kimlikle okuma çalıştı; nesne zaten öğrencinindi, disk değişmedi.
- **Değerlendirme:** Bu, dersin ana fikrini destekleyen yan bir gözlem: kimliği model argümanından almak, saldırı olmadan da yanlış kişiye bağlama riski taşır. Kimlik oturumdan enjekte edilmelidir. Gözlem iki koşu ve tek modelle sınırlıdır; oran değildir.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.**
- **Kusurlu başlangıç kodu Çalıştır modunda ayrıca koşturulmadı.**
- **Kurulum, indirme, commit/push ve puan yazımı yapılmadı.** Ollama sunucusuna ve modellere dokunulmadı.
