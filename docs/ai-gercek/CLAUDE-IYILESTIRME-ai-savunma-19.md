# ai-savunma-19 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Tablo + `[!NOT]`:** İlk anlatıma bir tablo eklendi. Tablo şunları karşılaştırıyor:
  - Gerçekte ne olur: Qdrant'ta payload kiracı alanı ve `filter`, ayrı koleksiyon seçeneği, kiracının oturumdan alınması.
  - Ders bunu nasıl temsil eder.
  - Ders neyi söyleyemez: veritabanı düzeyinde filtreleme, indeks ayrımı, yedekler ve gömme vektörlerinden sızıntı.

  Tablonun altına sentetik veri ve kalıcılık notu eklendi.
- **Çelişki:** "Bu derste Qdrant, FastAPI, ağ veya model kullanılmaz" cümlesi gerçek deneyle çelişiyordu. İş emrinde etiket olarak yoktu ama düzeltildi.
- **Görünür fixture:** `tracks/ai-savunma/fixtures/ai-savunma-19/` altına README ve üç veri dosyası eklendi:
  - `veri/vektor_politikasi.json`: asıl politika ve 5 bozuk politika (çapraz kiracı açık, filtre isteğe bağlı, joker kiracı, top_k 500, bool skor).
  - `veri/vektor_sorgulari.json`: 6 sorgu. Aralarında filtre oyunu, tanımsız kiracı, aşırı top_k, üç nedenin birden geçtiği sorgu ve sınırda top_k örnekleri var.
  - `veri/vektor_kayitlari.json`: 7 ham sonuç ve 3 bozuk kayıt. Sonuçlarda en yüksek skorlu iki kayıt başka kiracıya ait; ayrıca eşit skor, eşik eşitliği ve eşik altı örnekleri var.
  - Beklenen sonuçlar referansla doğrulandı. Görev 1–3 `hazirla("ai-savunma-19")` çağırıyor.
- **Kusurlu başlangıç kodları (4 görev):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Yalnız kiracı listesinin boş olmadığına bakıyor | 5 bozuk politika kabul ediliyor |
  | 2 | Kiracıyı istemci filtresinden alıyor; top_k sınırında `>=` kullanıyor | `q-filtre-oyunu` filtre nedeniyle reddedilmiyor; `q-normal` ve `q-sinir` yanlış biçimde reddediliyor |
  | 3 | Önce skora göre top_k ile kesip sonra kiracı filtresini uyguluyor | Yalnız `a-iade` dönüyor; 3 bozuk kayıt kabul ediliyor |
  | Gerçek deney | Kiracıyı istemci filtresinden alıyor | Çalıştır'da manipüle sorgu kiracı-b'nin kaydını getiriyor |

- **Anlatım:** 5 anlatım bloğu toplam yaklaşık 870 kelime. Eklenen konular:
  - Neden iki kez filtrelenir: eksik filtre hatası ve katmanlı savunma.
  - Saldırgan bakışı: filtreyi değiştirme, aşırı top_k, sorguyu hedef belgeye benzetme.
  - Sık tuzaklar: filtreyi istemciden almak, sessiz kırpma, filtre ile kesme sırası, eşitlik.
  - Gerçek deneyin adımları ve bu makinede ölçülen sonuç.
- **Gerçek deney modülü (`sandbox/ai_gercek_ai_savunma_19.py`, yalnız bu derse ait):**
  - Gömme vektörleri doğrulanıyor. Geçersiz vektör gelirse `GercekLabYok` hatası veriliyor.
  - İkinci bir gerçek sorgu eklendi: aynı kiracı ama filtresi kiracı-b'ye çevrilmiş. Bu sorgunun boş dönmesi bekleniyor.
  - Öğrencinin sonucu bağımsız `yetkili_vektorleri_getir_referans` ile karşılaştırılıyor.
  - Kayıtlar, ayarlar ve vektör boyutu kanıta yazılıyor.
- **Kopya koruması:**
  - Yasak listesi `("yetkili_vektorleri_getir_referans", "kanit_yaz")` oldu. Eskiden `("referans", "getattr")` idi ve ihlalde test durmuyordu.
  - AST kontrolü eklendi; ihlalde `stop()` çağrılıyor.
- **Gerçek deney testi:**
  - Sözleşmeye eklenenler: eşit skorda kimlik sırası; top_k 6 ile red, top_k 5 ile kabul; yabancı kayıtların kotayı doldurduğu durumda yine doğru sonuç; yinelenen kimlik, skor 1.2, bool skor, NUL karakter.
  - Gerçek veride eklenen kontroller: referansla birebir sonuç, manipüle filtreli sorgunun boş dönmesi, çapraz kiracı sızıntısının olmaması.
  - **Bilerek yapılan değişiklik:** Eski `en_yuksek_kiraci == "b"` kontrolü kaldırıldı. Bu kontrol, gömme modelinin kiracı-b kaydına en yüksek skoru vermesini kabul koşulu yapıyordu. Artık bu bilgi bulgu olarak kaydediliyor.
- Ortak `sandbox/ai_gercek_lab.py`, `engine/` ve `web/` değiştirilmedi.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

| Kontrol | Komut | Sonuç |
|---|---|---|
| validate | `tools/validate.py ai-savunma-19` (PAFTA_DATA=`<scratchpad>/s19-kabul`) | **TEMİZ**, 9 kontrol |
| tahmin | `docs/denetim/araclar/tahmin.py . ai-savunma-19` | 1 tahmin, **0 şüpheli** |
| mutasyon | `kirp_gercek.py` kopyası, ardından `mutasyon.py --en-cok 1000 ai-savunma-19` | 10 + 15 + 26 = 51 mutant, **0 geçen**; kopya silindi |
| kopya sondası | `kopya_sonda.py ai-savunma ai-savunma-19 ...` | 6/6 **fail → korunuyor**, kanıt yazılmadı |

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/s19-kabul/ai-kanit/savunma-kiraci-*.json`, kabul `true`.
- **Gömme modeli:** `all-minilm:22m`.
- **Skorlar:** `b-iade` 0.910 (en yüksek, kiracı-b), `a-iade` 0.761, `a-kargo` 0.496.
- **Olağan sorgu:** `a-iade` ve `a-kargo` döndü. Sonuç referansla aynı, çapraz sızıntı yok.
- **Manipüle filtreli sorgu:** Boş döndü.
- **Çalıştır (CLI runner `run`):** Başlangıç kodu `ok` döndü, ancak manipüle sorgu boş dönmedi. Kusur görünür.
- **Görev 1–3 (görünür veriyle elle koşturuldu):**
  - Başlangıç kodları tablodaki kusurları gösterdi.
  - Çözümler 5 bozuk politikayı reddetti.
  - Sorgu kararlarını README tablosuyla aynı verdi.
  - `a-iade`, `a-sss` ve `a-kargo` kayıtlarını getirdi; 3 bozuk kaydı reddetti.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.** Kontrol, Çalıştır ve dosya erişimi yalnız CLI ve runner üzerinden doğrulandı.
- Qdrant ve FastAPI çalıştırılmadı.
- Kurulum, indirme, commit/push ve puan yazımı yapılmadı. Ollama sunucusuna dokunulmadı.
