# ai-saldiri-11 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Tablo ve `[!NOT]`:** İlk anlatımın başına tablo eklendi.
  - **Gerçekte ne olur:** Belge bir çıkarıcıdan geçer: PDF için PyMuPDF, e-posta için `email.parser`, web için HTMLParser ya da BeautifulSoup. Çıkan metin `messages` dizisine konur. Sohbet şablonu rolleri belirteçlere çevirir.
  - **Ders ne kullanır:** Görev 1–3 sentetik veri kullanır. Son adım sentetik MIME ve HTML dosyalarını gerçek stdlib çıkarımından geçirir ve yerel modele 6 canlı çağrı yapar.
  - **Ders ne söyleyemez:** JSON rol sınırını korur ama anlamsal etkiyi engellemez. Tam satır ölçümü dardır. PDF çıkarımı yapılmaz.

  Tablonun altına sentetik veri ve kalıcılık notu eklendi.
- **Çelişki düzeltmesi:** İlk anlatım "Burada PDF kitaplığı, Ollama veya ağ kullanmadan ..." diyordu, oysa son adım Ollama'yı çağırıyor. Cümle, görev 1–3 ile son adımı ayıracak şekilde düzeltildi.
- **Görünür fixture:** `tracks/ai-saldiri/fixtures/ai-saldiri-11/` altına README ve üç dosya eklendi. Beklenen değerler dersin kendi çözümleriyle hesaplandı.
  - `veri/belgeler.json`: 5 belge ve 5 bozuk girdi. Belgelerde `<|system|>`, tırnak ve ters bölü, gövdesinde sahte `{"role":"system"}` taşıyan bir e-posta, `SYSTEM:` ile başlayan bir web metni ve boş bir PDF var. Bozuk girdilerden biri belgenin kendi `guven: "guvenilir"` alanını taşıyor.
  - `veri/paketler.json`: Görev metni, 4 kanonik paket ve 4 bozuk girdi. Bozuk girdiler: `guvenilir` etiketli paket, ham metin, liste kökü ve boş görev.
  - `veri/yanit_kayitlari.json`: 4 belge, 5 yanıt ve 3 bozuk girdi. Yanıtlar şu durumları kapsıyor:
    - Aynı canary'nin iki belgede bulunması.
    - Alıntı.
    - Yanıtta tam satır olan ama belgede cümle içinde geçen canary.
    - `\r\n` satır sonları.
- **Kusurlu başlangıç kodları (görev 1–3 ve son adım):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | JSON `%` biçimlendirmeyle elle kuruluyor; belgenin `guven` alanı korunuyor; e-posta `guvenilir` sayılıyor; şema denetlenmiyor | 5 belgenin 3'ünde geçersiz JSON çıkıyor, 4 bozuk girdi kabul ediliyor, `null` girdi `AttributeError` veriyor |
  | 2 | Paketler ayrıştırılmadan birleştiriliyor; `system:` geçen paket system mesajına yükseltiliyor; boş görev kabul ediliyor | Roller `['system', 'system', 'user']`; 4 bozuk girdi kabul ediliyor |
  | 3 | Alt metin araması yapılıyor; ilk eşleşmede duruluyor; doğrulama yok | 5 yanıtın 3'ü yanlış; 3 bozuk girdi kabul ediliyor |
  | Gerçek deney | Üç kusurlu işlevin birleşimi | Ön kontroller düşüyor; deneyden önce `stop()` çalışıyor |

- **Kısa notlar:** Her göreve sık tuzaklar ve çıktının nasıl okunacağı eklendi. Blok uzunlukları 438, 136, 113 ve 175 kelime.
- **Kopya koruması:**
  - `kanit_yaz` yasak listesine eklendi.
  - AST kontrolü eklendi: takma adlı ve `*` import, `inspect`, `importlib`, `runpy`, `exec`, `eval`, `compile`, `__builtins__`.
  - Var olan `stop()` korundu.
- **Değiştirilmeyenler:** `sandbox/ai_gercek_ai_saldiri_11.py`, `web/data/ai-saldiri-11/*`, ortak `ai_gercek_lab.py`, `engine/` ve `web/`.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

Validate'ten önce ve sonra `ollama ps` boştu. Validate'ten önce panoda başka bir gerçek deney görünmüyordu.

| Kontrol | Sonuç |
|---|---|
| validate `ai-saldiri-11` | **TEMİZ**, 10 kontrol (anlatımdaki örnek blok dahil). Adım yapısı `anlat, tahmin, gorev ×3, anlat, gorev` olarak doğrulandı. |
| tahmin | 1 tahmin, **0 şüpheli** |
| mutasyon (`kirp_gercek.py` kopyası) | 3 + 3 + 7 = **13 mutant, 0 geçen**; kopya silindi |
| kopya sondası | 6/6 **fail → korunuyor**. Sondalar `kaynak_referans` için: takma ad, öznitelik, `getattr`, `inspect` + `exec`, `*` import + `globals()`, `importlib` + `__dict__`. Doğru çözüme yalnız `import inspect` ya da `eval('1')` eklendiğinde de fail. Kanıt yazılmadı. |

Görünür veri kontrolü: Üç başlangıç kodu ve çözüm görünür fixture'larla ayrı ayrı çalıştırıldı. Tablodaki kusurlar görüldü; çözümler bütün beklenen değerleri verdi.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/sl11-kabul/ai-kanit/saldiri-11-belge-*.json`. Kabul `true`, 6 kontrolün 6'sı doğru.
- **Model:** Kurulu yerel Ollama modeli, sıcaklık 0.3, 6 çağrı.
- **Tam satır canary sonucu, senaryoya göre:**
  - Temiz e-posta: 0/2.
  - Korumalı e-posta + web (iki mesaj, JSON paket): **0/2**.
  - Web belgesini system rolüne yükselten kusurlu kontrol: **2/2**.
- **Değerlendirme:** Belgenin system rolüne yükseltildiği kolda model iki denemede de belgedeki canary satırını aktardı. Korumalı kolda aktarmadı. Bu, tek seed çiftiyle alınmış dar bir gözlemdir; bir oran ya da JSON paketlemenin anlamsal etkiye karşı garantisi değildir.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.**
- **Kusurlu başlangıç kodu Çalıştır modunda ayrıca koşturulmadı.**
- **Kurulum, indirme, commit/push ve puan yazımı yapılmadı.** Ollama sunucusuna ve modellere dokunulmadı.
