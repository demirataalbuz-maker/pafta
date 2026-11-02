# ai-saldiri-09 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Tablo ve `[!NOT]`:** İlk anlatımın başına üç sütunlu bir tablo eklendi:
  - **Gerçekte ne olur:** Model yanıtı sohbet arayüzünde, e-postada ya da Markdown görüntüleyicide render edilir. Burp ve DevTools bunu DOM'da gösterir; DOMPurify, bleach ve CSP savunma sağlar.
  - **Ders ne kullanır:** Görev 1–3 sentetik model çıktılarıyla çalışır. Son adım iki gerçek Ollama yanıtını Python `HTMLParser` ile inceler.
  - **Ders ne söyleyemez:** Tarayıcı ve JavaScript çalışmaz; parser'ın etiket bulması XSS kanıtı değildir; dersteki Markdown dönüştürücüsü genel bir motor değildir; URL kabulü SSRF koruması değildir.

  Tablonun altına sentetik veri ve kalıcılık notu eklendi.
- **Doğruluk:** "Bu ders ... dönüşüm sözleşmesini standart Python fixture'larıyla test eder" cümlesi, son adımdaki gerçek model ve HTMLParser ile eksik kalıyordu. Görev 1–3 ile son adım ayrı ayrı anlatılacak şekilde düzeltildi.
- **Görünür fixture:** `tracks/ai-saldiri/fixtures/ai-saldiri-09/` altına README ve üç dosya eklendi:
  - `veri/html_ornekleri.json`: 5 örnek ve 3 bozuk girdi. Örnekler `onerror`, tek tırnaklı attribute, önceden kaçışlanmış görünen metin ve boş metin içerir.
  - `veri/url_ornekleri.json`: 12 adres ve 2 bozuk girdi. Adresler arasında karışık harfli `javascript:`, `data:`, kullanıcı bilgisi, boş host, `:99999`, boşluk, sekme, `\\` ve şemasız adres var.
  - `veri/markdown_ornekleri.json`: 6 örnek ve 2 bozuk girdi. Örnekler `&` içeren güvenli hedef, iç içe parantez, ham `<img onerror>`, kullanıcı bilgili hedef, çok satırlı bağlantı ve bağlantı metninde `<script>` içerir.

  Beklenen çıktılar dersin kendi çözümleriyle hesaplandı. `web/data/ai-saldiri-09-ciktilar.txt` değiştirilmedi.
- **Kusurlu başlangıç kodları (4 görev):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Elle ve yanlış sırayla `replace` yapılıyor (`&` en sonda); tek tırnak kaçışlanmıyor; `str()` her girdiyi kabul ediyor | `h-01` sonucu `&amp;lt;img ...` olarak çift kodlanıyor; `h-02` ve `h-04` sonuçlarında `'` ham kalıyor; 3 bozuk girdi KABUL ediliyor |
  | 2 | Yalnız önek kontrolü yapılıyor; string olmayan girdide `None` dönüyor | Kullanıcı bilgisi, `https:///yol`, `:99999`, boşluk ve sekme içeren 5 adres kabul ediliyor; bozuk girdiler sessizce `None` dönüyor |
  | 3 | Önek kontrolü yapılıyor; HTML kaçışı yok | `m-03` ve `m-06` sonuçlarında ham `<` kalıyor; `m-04` hedefi korunuyor; `m-01` sonucunda `&` kaçışlanmıyor; 2 bozuk girdi KABUL ediliyor |
  | Gerçek deney | Üç kusurlu işlevin birleşimi | Kontrol, yeni metinle yapılan saf kontrolde düşüyor ve deneyden önce `stop()` çalışıyor |

- **Anlatım (iş emrinde etiketli değildi, kısa tutuldu):** İki bölüm eklendi:
  - HTML kaçışı için sık tuzaklar: `replace` sırası, tek tırnak, çift kodlama.
  - URL için önek kontrolünü geçen ama politikaya uymayan adresler ve karışık harfli şema.
- **Kopya koruması:**
  - `kod_denetimi` yasak listesine `kanit_yaz` eklendi.
  - AST kontrolü eklendi. Şunları reddediyor: takma adlı ve `*` import, `inspect`, `importlib`, `runpy`, `exec`, `eval`, `compile`, `__builtins__`.
  - İhlal varsa `stop()` çalışıyor.
- **Değiştirilmeyenler:**
  - `sandbox/ai_gercek_ai_saldiri_09.py` değiştirilmedi. Kabul şartları referans karşılaştırmasıdır; modelin tehlikeli çıktı vermesini şart koşmaz.
  - Ortak `ai_gercek_lab.py`, `engine/` ve `web/` değiştirilmedi.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

Validate'ten önce `ollama ps` boştu ve panoda başka bir gerçek deney görünmüyordu.

| Kontrol | Komut | Sonuç |
|---|---|---|
| validate | `tools/validate.py ai-saldiri-09` (PAFTA_DATA=`<scratchpad>/sl09-kabul`) | **TEMİZ**, 10 kontrol (anlatımdaki örnek blok dahil; adım yapısı doğrulandı) |
| tahmin | `docs/denetim/araclar/tahmin.py . ai-saldiri-09` | 1 tahmin, **0 şüpheli** |
| mutasyon | `kirp_gercek.py` kopyası, ardından `mutasyon.py --en-cok 1000 ai-saldiri-09` | 0 + 5 + 7 = 12 mutant, **0 geçen**; kopya silindi. Görev 1'in çözümü tek satırlık `html.escape` olduğu için mutant üretilmedi. |
| kopya sondası | `kopya_sonda.py ai-saldiri ai-saldiri-09 ...` | 6/6 **fail → korunuyor**. Doğru çözüme yalnız `import inspect` ya da `eval('1')` eklendiğinde de fail. Kanıt yazılmadı. |

Kopya sondası şöyle kuruldu: `html_guvenli` doğru biçimde yazıldı. `url_referans` ve `markdown_referans` ise 6 yoldan bağlanmaya çalışıldı: takma ad, öznitelik, `getattr`, `inspect` + `exec`, `*` import + `globals()`, `importlib` + `__dict__`.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/sl09-kabul/ai-kanit/saldiri-09-cikti-*.json`. Kabul `true`, 5 kontrolün 5'i doğru.
- **Model:** `qwen3:4b-instruct-2507-q4_K_M`. İki canlı yanıt alındı:
  1. `<b>PAFTA</b> & "not"`
  2. `[sample](javascript:alert) and [lesson](https://ornek.test/)`
- **HTMLParser:** Ham girdide 4 örnekte etiket oluştu: 3 sentetik ve 1 canlı. Korumalı çıktıda etiket oluşan örnek sayısı **0**.
- **Değerlendirme:** Modelin HTML ya da `javascript:` bağlantısı üretmesi bir gözlemdir, kabul şartı değildir. HTMLParser JavaScript çalıştırmaz; bu sonuç tarayıcıda XSS çalıştığı anlamına gelmez.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.** Kontrol ve dosya erişimi yalnız CLI ve runner üzerinden doğrulandı. Üretilen `.html` dosyaları tarayıcıda açılmadı.
- **Kusurlu başlangıç kodu Çalıştır modunda ayrıca koşturulmadı.**
- **Kurulum, indirme, commit/push ve puan yazımı yapılmadı.** Ollama sunucusuna dokunulmadı.
