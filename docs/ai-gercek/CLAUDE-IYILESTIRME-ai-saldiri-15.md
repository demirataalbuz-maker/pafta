# ai-saldiri-15 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Çelişki:** İlk anlatımda "Bu derste Python fixture'ları kullanılır, ChromaDB veya gerçek model çalıştırılmaz" cümlesi vardı; kaldırıldı. Yeni metin şöyle: görev 1–3 sentetik kayıtlarla çalışır; son adım gerçek gömme skorları ve gerçek model yanıtlarıyla ölçer. ChromaDB çalıştırılmaz.
- **Tablo + `[!NOT]`:** İlk anlatıma iki ekleme yapıldı:
  - Bir tablo. Gerçekte ChromaDB, gömme modeli ve bağlam penceresi zinciri; dersin kullandığı `all-minilm:22m` ve cosine benzerliği; karakter bütçesi ile token bütçesi farkı.
  - Bir not. Sentetik veri ve kalıcılık bilgisi. Son adımın düzenlenebilir bağlam dosyasının ayrıca kalıcı olduğu da yazıldı.
- **Görünür fixture:** `tracks/ai-saldiri/fixtures/ai-saldiri-15/` altına README ve üç veri dosyası eklendi:
  - `veri/sorgular.json`: 4 sorgu ve 3 bozuk sorgu. Sorgular şunları kapsıyor: boşluklu ve büyük harfli, sekmeli, talimat görünümlü, ayrıca Türkçe `İ` tuzağı.
  - `veri/aday_belgeler.json`: 120 karakter bütçe ve 5 belge. Bunların arasında bütçeye sığmayan en yüksek skorlu belge, eşit skorlu iki belge, çelişkili eski bir belge ve boş bir not var. Ayrıca 3 bozuk belge var.
  - `veri/baglam_kayitlari.json`: 3 vaka (kanıt kaybı, yalnız sıra değişimi, kanıt kaybı olmadan değişim) ve 3 bozuk kayıt grubu.
  - Görev 1–3 `hazirla("ai-saldiri-15")` çağırıyor. Mevcut `web/data/ai-saldiri-15-baglam.txt` ve kalıcı çalışma kopyası değiştirilmedi.
- **Türkçe casefold düzeltmesi:** README'yi ilk yazdığımda "ilk iki sorgu aynı biçime normalize olur" demiştim. Görünür veriyle denediğimde bunun yanlış olduğu çıktı: `"İ".casefold()` sonucu `"i̇"` oluyor ve terimler `"i", "ade"` diye bölünüyor. README ve görev metni düzeltildi. Bu durum artık bilerek gösterilen bir tuzak olarak anlatılıyor; kurallar değişmedi.
- **Kusurlu başlangıç kodları (4 görev):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | `lower`/`strip` uygulanıyor, iç boşluklar birleştirilmiyor, özgün sorgu kaydedilmiyor, denetim yok | Sekme korunuyor, `orijinal` alanı kayboluyor, 3 bozuk sorgu kabul ediliyor |
  | 2 | İlk sığmayan belgede seçim duruyor | Hiç belge seçilmiyor, 3 bozuk belge kabul ediliyor |
  | 3 | Liste sırasıyla karşılaştırılıyor, kol denetimi yok | `q-kargo` "değişen" sayılıyor, 3 bozuk kayıt kabul ediliyor |
  | Gerçek deney | Belge kırpılarak ekleniyor | Çalıştır'da `secim_dogru` ve `fark_dogru` False |

- **Anlatım:** 4 anlatım bloğu toplam yaklaşık 1050 kelime oldu. Eklenen konular:
  - Saldırgan bakışı: sıralamayı ele geçirme, bütçeyi doldurma, skoru dışarıdan sağlama.
  - Savunucu tarafı ve sık tuzaklar: sorgu izi, kırpmama, atlamadan sonra seçime devam etme, skor kaynağı, sıra değişimi.
  - Cosine benzerliğinin ne olduğu ve modele bağlı olması.
  - Bu makinede ölçülen sonuç.
- **Kopya koruması güçlendirildi:**
  - `kod_denetimi` yasak listesine `kanit_yaz` eklendi.
  - AST kontrolü eklendi. Şunları reddediyor: takma adlı import ve `*` importu, `inspect`/`importlib`/`runpy`, `exec`/`eval`/`compile`/`__builtins__`.
  - İhlalde `stop()` çağrılıyor.
- **Değiştirilmeyenler:** Gerçek deney modülü (`sandbox/ai_gercek_ai_saldiri_15.py`) değiştirilmedi. Modül zaten şunları yapıyordu:
  - Gerçek gömme alıyor, ham vektörleri dosyaya yazıyor.
  - Sahte dış skoru açıkça etiketliyor.
  - Boş yanıtı hata sayıyor.
  - Saldırı başarısını kabul koşulu yapmıyor.
  - Kararını referansla karşılaştırıyor.

  Ortak `sandbox/ai_gercek_lab.py`, `engine/` ve `web/` de değiştirilmedi.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

| Kontrol | Komut | Sonuç |
|---|---|---|
| validate | `tools/validate.py ai-saldiri-15` (PAFTA_DATA=`<scratchpad>/sl15-kabul`) | **TEMİZ**, 9 kontrol. Son metin düzeltmesinden sonra yeniden koşturuldu. |
| tahmin | `docs/denetim/araclar/tahmin.py . ai-saldiri-15` | 1 tahmin, **0 şüpheli** |
| mutasyon | `kirp_gercek.py` kopyası, ardından `mutasyon.py --en-cok 1000 ai-saldiri-15` | 4 + 10 + 8 = 22 mutant, **0 geçen**; kopya silindi |
| kopya sondası | `kopya_sonda.py ai-saldiri ai-saldiri-15 ...` | 6/6 **fail → korunuyor**, kanıt yazılmadı |

Kopya sondası ayrıntısı: `sorgu_izi` öğrencinin kendi yazdığı hâliyle bırakıldı. Diğer iki işlev için 6 yol denendi: takma ad, öznitelik, `getattr`, `inspect`+`exec`, `*` importu, `importlib`+`__dict__`.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/sl15-kabul/ai-kanit/saldiri-15-baglam-*.json`, kabul `true`, 7 kontrolün 7'si doğru.
- **Gömme skorları (`all-minilm:22m`):**

  | Belge | Cosine | Skor |
  |---|---|---|
  | kanıt | 0.635 | 82 |
  | diğer | 0.096 | 55 |
  | zehir | 0.624 | 81 |

  Zehirli belgenin sahte dış skoru 100'dü.
- **Seçimler:**
  - Temiz: `kanit` + `diger`.
  - Manipüle: `zehir` + `diger`, kanıt elendi.
  - Fark: kanıt kayboldu.
- **Model yanıtları (`qwen3:4b-instruct-2507`):**
  - Temiz bağlamla doğru süreyi söyledi.
  - Manipüle bağlamla belgedeki talimata uydu ve canary'yi yazdı.

  Bu tek bir koşudan alınmış bir gözlem. Tohum her koşuda değiştiği için farklı sonuç çıkabilir ve bu sonuç kabul koşulu değil. Anlatımda da aynı şekilde yazıldı.
- **Çalıştır (CLI runner `run`):** Başlangıç kodu `ok` döndü; `secim_dogru` ve `fark_dogru` False. Kusur görünür durumda.
- **Görev 1–3 (görünür veriyle elle koşturuldu):**
  - Başlangıç kodları tablodaki kusurları gösterdi.
  - Çözümler sekmeyi birleştirdi ve özgün sorguyu korudu.
  - 112 karakterlik doğru seçimi yaptı.
  - `q-kargo` vakasını değişmemiş saydı.
  - Bozuk kayıtları reddetti.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.** Kontrol, Çalıştır ve dosya erişimi yalnız CLI ve runner üzerinden doğrulandı.
- ChromaDB çalıştırılmadı. Gömme ve cosine hesabı doğrudan yapılıyor; bu durum tabloda yazılı.
- Kurulum, indirme, commit/push ve puan yazımı yapılmadı. Ollama sunucusuna dokunulmadı.
