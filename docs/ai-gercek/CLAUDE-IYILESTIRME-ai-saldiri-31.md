# ai-saldiri-31 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Tablo ve `[!NOT]`:** İlk anlatımın başına üç sütunlu tablo eklendi.
  - **Gerçekte ne olur:** Tarayıcı ajanı sayfayı ekran görüntüsü, `textContent`, `innerText` ve erişilebilirlik ağacı kanallarından alır. Eylemleri araç çağrısı olarak gelir.
  - **Ders ne kullanır:** Görev 1–3 sentetik sayfa, bağlantı ve kayıtları kullanır. Son adım ağı kesilmiş başsız Chromium'da tek bir yerel sayfayı açar.
  - **Ders ne söyleyemez:** Derste model ya da ajan yoktur, bu yüzden ajanın yönlendirilip yönlendirilmediği ölçülmez. HTMLParser sınıf tabanlı CSS'i, ekran dışına itilmiş metni ve `font-size:0` gibi gizlemeleri tanımaz. Alan süzgeci yönlendirme, DNS ve TLS denetlemez.

  Tablonun altına sentetik veri ve kalıcılık notu eklendi.
- **Çelişki düzeltmesi:** İlk anlatım "Playwright, Browser Use, Ollama veya gerçek web sitesi gerekmez" diyordu, oysa son adım Playwright Chromium kullanıyor. Cümle, görev 1–3 ile ağı kesilmiş son adımı ayıracak şekilde düzeltildi.
- **Görünür fixture:** `tracks/ai-saldiri/fixtures/ai-saldiri-31/` altına README ve üç dosya eklendi. Beklenen çıktılar dersin kendi çözümleriyle hesaplandı.
  - `veri/sayfalar.json`: 6 sayfa ve 4 bozuk girdi. Sayfalarda gizli `div` ve JSON-LD, `STYLE="Display : NONE"`, gizli alt ağaç, `data-style` tuzağı, void etiketler var. Ayrıca sınıfla gizlenen bir canary sınır örneği olarak eklendi (`s-06`): HTMLParser bu canary'yi görünür sayar, Chromium ise gizler.
  - `veri/eylem_adaylari.json`: 11 aday ve 4 bozuk girdi. Adaylar arasında sahte son ek, sorgu parametresi, kullanıcı bilgisi, `:8443`, `:99999`, alt alan adı, `javascript:` ve sondaki nokta var.
  - `veri/dom_ekran_kayitlari.json`: 6 vaka, karışık sırada 12 kayıt ve 3 bozuk girdi. Vakalar arasında yalnız ekranda görülen canary (`d-03`), alıntı (`d-04`) ve `\r\n` (`d-05`) var.
- **Kusurlu başlangıç kodları (4 görev):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Gizlilik yalnız son açılan etiketten okunuyor; stilde boşluksuz küçük harfli `display:none` aranıyor; `aria-hidden` yok sayılıyor; `script` / `style` görünür sayılıyor; etiket dengesi denetlenmiyor | 6 sayfanın 4'ü yanlış, 4 bozuk girdinin hepsi kabul ediliyor |
  | 2 | Alan adı URL metninde alt string olarak aranıyor; şema ve port denetlenmiyor; şema ihlalinde hata yok | 11 adayın 10'u izinli sayılıyor, 4 bozuk girdi kabul ediliyor |
  | 3 | Alt metin araması yapılıyor; eksik kanal ve boş canary geçiliyor; yalnız ekranda görülen fark `degisen` listesine girmiyor; listeler sıralanmıyor | `d-04` alıntısı DOM eşleşmesi sayılıyor, `d-03` `degisen` listesinde yok, 3 bozuk girdi kabul ediliyor |
  | Gerçek deney | Üç kusurlu işlevin birleşimi | Saf kontrol düşüyor; `stop()` Chromium açılmadan çalışıyor |

- **Anlatım:** Dört anlatım bloğu 635, 134, 121 ve 173 kelimeye çıktı. Eklenen konular:
  - **Kanallar:** `textContent`, `innerText` ve erişilebilirlik ağacı farkı. `aria-hidden` öğesi ekranda görünür ama ağaçta yoktur; "yalnız ekran okuyucu" metninde durum tersidir.
  - **Saldırganın gizleme yolları:** sınıf, `font-size:0`, renk, `left:-9999px`, `alt` / `title`, JSON-LD. Saldırı yüzeyi olarak kullanıcı içeriği: yorum, e-posta, paylaşılan belge.
  - **Savunmanın neden kırıldığı:** sınıf CSS'i, JavaScript ile sonradan eklenen içerik, alt string izin listesi, açık yönlendirme.
  - Her görev için sık tuzaklar ve çıktının nasıl okunacağı.
  - Son adımda `aria-hidden` paragrafının neden fonksiyonda gizli, Chromium'un `innerText` çıktısında görünür olduğu. Bu davranış ayrı bir Playwright koşusuyla doğrulandı: `innerText` `ARIA-P` metnini içeriyor, erişilebilirlik ağacı içermiyor.
- **Kopya koruması:**
  - `kod_denetimi` yasak listesine `kanit_yaz` eklendi.
  - AST kontrolü eklendi. Takma adlı ve `*` import, `inspect`, `importlib`, `runpy`, `exec`, `eval`, `compile` ve `__builtins__` reddediliyor.
- **Değiştirilmeyenler:**
  - `sandbox/ai_gercek_ai_saldiri_31.py`, ortak `ai_gercek_lab.py`, `engine/` ve `web/` değiştirilmedi.
  - Son adımın meta bilgisindeki `gereksinim: torch` satırı bu deney için anlamsız görünüyor (deney torch kullanmıyor). Motor davranışına dokunduğu için değiştirilmedi; denetçinin kararına bırakıldı.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

Validate'ten önce `ollama ps` boştu ve panoda başka bir gerçek deney görünmüyordu. Bu derste model kullanılmıyor.

| Kontrol | Sonuç |
|---|---|
| validate `ai-saldiri-31` | **TEMİZ**, 9 kontrol. Adım yapısı `anlat, tahmin, gorev ×3, anlat, gorev` olarak doğrulandı. |
| tahmin | 1 tahmin, **0 şüpheli** |
| mutasyon (`kirp_gercek.py` kopyası) | 17 + 11 + 6 = **34 mutant, 0 geçen**; kopya silindi |
| kopya sondası | 6/6 **fail → korunuyor**. Sondalar `eylem_suz_referans` ve `dom_ekran_farki_referans` için: takma ad, öznitelik, `getattr`, `inspect` + `exec`, `*` import + `globals()`, `importlib` + `__dict__`. Doğru çözüme yalnız `import inspect` ya da `eval('1')` eklendiğinde de fail. Kanıt yazılmadı. |

Görünür veri kontrolü: Dört başlangıç kodu ve çözüm görünür fixture'larla ayrı ayrı çalıştırıldı. Tablodaki kusurlar görüldü; çözümler bütün beklenen değerleri verdi.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/sl31-kabul/ai-kanit/saldiri-31-dom-enjeksiyonu-*.json`. Kabul `true`, 5 kontrolün 5'i doğru.
- **Ortam:** Chromium `156.0.8078.4`, headless, ağ `route.abort()` ile kapalı.
- **Katmanlar:** Gizli katmanda dinamik canary, `display:none` talimatı ve `aria-hidden` notu var. Kod katmanında `const GIZLI = "BREACH:PAFTA-…"` var.
- **Fark:** `yalniz_dom=["chromium-v1"]`. Canary `textContent` içinde tam satır, `innerText` içinde yok.
- **Eylemler:** `bag-1` ve `bag-2` izinli, `bag-3` (dış alan) ve `bag-4` (HTTP) reddedildi.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.**
- **Kusurlu başlangıç kodu Çalıştır modunda ayrıca koşturulmadı.**
- **Kurulum, indirme, commit/push ve puan yazımı yapılmadı.** Var olan Playwright 1.64.1 ve Chromium kullanıldı; başlatılan tarayıcılar kapandı.
