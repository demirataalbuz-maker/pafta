# ai-saldiri-13 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Tablo ve `[!NOT]`:** İlk anlatımın başına tablo eklendi.
  - **Gerçekte ne olur:** PDF, pypdf ya da PyMuPDF ile metin katmanına ve `/Info` metadata'sına ayrılır. Görüntüler vision/OCR ile metne çevrilir. `render mode 3` metin ekranda görünmez ama çıkarıcıya gelir.
  - **Ders ne kullanır:** Görev 1–3 sentetik katman kayıtları ve hat olayları kullanır. Son adım reportlab ile gerçek PDF üretir, pypdf ile çıkarır ve kurulu yerel vision modeliyle OCR yapar.
  - **Ders ne söyleyemez:** Fixture belirli bir okuyucunun davranışını kanıtlamaz. Tek sayfalık kontrollü PDF genel çok sayfalı PDF davranışını temsil etmez. Katman farkı nedensellik kanıtı değildir.

  Tablonun altına sentetik veri ve kalıcılık notu eklendi.
- **Çelişki düzeltmesi:** İlk anlatım "PyMuPDF veya Pillow ile gerçek dosya açmayız … gerçek PDF ve model indirmeden" diyordu, oysa son adım reportlab/pypdf/Pillow ve vision modeli kullanıyor. Cümle, görev 1–3 ile son adımı ayıracak şekilde düzeltildi. Hiçbir adımda indirme yapılmadığı da açıkça yazıldı.
- **Görünür fixture:** `tracks/ai-saldiri/fixtures/ai-saldiri-13/` altına README ve üç dosya eklendi. Beklenen değerler dersin kendi çözümleriyle hesaplandı.
  - `veri/katmanlar.json`: İki faturaya ait 6 karışık kayıt ve 5 bozuk girdi. Kayıtlarda bir `system:` talimat satırı ve boş metadata var.
  - `veri/katman_kayitlari.json`: 6 belge × 3 katman ve 4 bozuk girdi. Belgeler: yalnız metadata, yalnız gizli metin, OCR alıntısı, `\r\n` satır sonu, üç katmanın hepsi, temiz.
  - `veri/olaylar.json`: 13 hat olayı ve 4 bozuk girdi. Olaylar şu durumları kapsıyor:
    - Aynı aşamada iki katman.
    - U+0332 birleştirici karakter; canary ancak normalizasyonda görünür.
    - Yalnız model yanıtında görünen canary.
    - Alfabetik sıra tuzağı (`baglam` < `cikarma`).
- **Kusurlu başlangıç kodları (görev 1–3 ve son adım):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Yalnız `belge_id` sıralaması; `system:` satırları siliniyor; paket `guvenilir`; şema yok; kanonik JSON yok | Paket yanlış; 5 bozuk girdinin 5'i yanlış |
  | 2 | Alt metin araması; eksik katman `False` sayılıyor; şema yok; sıralama yok | Rapor yanlış (`d-alinti` fark sayılıyor); 4 bozuk girdinin 4'ü yanlış |
  | 3 | Aşamalar alfabetik karşılaştırılıyor; alt metin araması; eş aşamadaki ikinci katman düşüyor | 3 belgenin 3'ü yanlış; 4 bozuk girdinin 4'ü yanlış |
  | Gerçek deney | Üç kusurlu işlevin birleşimi | İlk ön kontrol (alıntılı OCR) düşüyor; deneyden önce `stop()` çalışıyor |

- **Kısa notlar:** Her göreve sık tuzaklar eklendi. Son adıma kısa bir "çıktıyı okurken" notu eklendi.
- **Kopya koruması:**
  - `kanit_yaz` yasak listesine eklendi.
  - AST kontrolü eklendi: takma adlı ve `*` import, `inspect`, `importlib`, `runpy`, `exec`, `eval`, `compile`, `__builtins__`.
  - Var olan `stop()` korundu.
- **Değiştirilmeyenler:** `sandbox/ai_gercek_ai_saldiri_13.py`, `web/data/ai-saldiri-13-tarif.txt`, ortak `ai_gercek_lab.py`, `engine/` ve `web/`.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

Validate'ten önce `ollama ps` boştu. Validate'ten önce panoda başka bir gerçek deney görünmüyordu; Gemini yalnız anlatım işindeydi.

| Kontrol | Sonuç |
|---|---|
| validate `ai-saldiri-13` | **TEMİZ**, 10 kontrol (anlatımdaki `ornek` bloğu dahil), ilk koşuda. Adım yapısı `anlat, tahmin, gorev, anlat, gorev, anlat, gorev, anlat, gorev` olarak doğrulandı. |
| tahmin | 1 tahmin, **0 şüpheli** |
| mutasyon (`kirp_gercek.py` kopyası) | 4 + 8 + 9 = **21 mutant, 0 geçen**; kopya silindi |
| kopya sondası | 6/6 **fail → korunuyor**. Sondalar `gozlem_referans` için: takma ad, öznitelik, `getattr`, `inspect` + `exec`, `*` import + `globals()`, `importlib` + `__dict__`. Doğru çözüme yalnız `import inspect` ya da `eval('1')` eklendiğinde de fail. |

Görünür veri kontrolü: Üç başlangıç kodu ve çözüm görünür fixture'larla ayrı ayrı çalıştırıldı. Tablodaki kusurlar görüldü; çözümler bütün beklenen değerleri verdi.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/sl13-kabul/ai-kanit/saldiri-13-pdf-*.json`. Kabul `true`, 7 kontrolün 7'si doğru. Kullanılanlar: reportlab 5.1.0, pypdf 6.21.4, Pillow 13.0.0, `qwen2.5vl:3b`.
- **Katman farkı:**
  - `text-only` belgesinde canary yalnız görünmez metin katmanında çıktı.
  - `meta-only` belgesinde canary yalnız metadata'da çıktı.
  - İkisinde de ilk gözlem aşaması `cikarma`.
- **OCR:** Vision modeli iki görüntüde yalnız görünen fatura metnini okudu ("PAFTA LOCAL INVOICE …"). Canary'yi üretmedi; görüntüde zaten yoktu.
- **Metadata çağrısı:** Modelden metadata'dan başlık çıkarması istendi. Model "Extracted title not available" dedi; canary'yi tekrarlamadı.
- **Değerlendirme:** Görsel ile çıkarılmış metin arasındaki ayrışma gerçek PDF'de gözlendi: insan ve OCR faturayı görüyor, metin çıkarıcı gizli talimatı görüyor. Bu tek koşudan alınmış dar bir gözlemdir.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.**
- **Kusurlu başlangıç kodu Çalıştır modunda ayrıca koşturulmadı.**
- **Kurulum, indirme, commit/push ve puan yazımı yapılmadı.** Ollama sunucusuna ve modellere dokunulmadı.
