# ai-savunma-16 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Tablo + `[!NOT]`:** İlk anlatımın başına bir tablo eklendi. Tablo üç şeyi anlatıyor:
  - Qdrant'ın vektör ve payload yapısı, payload ile kaynak defterinin karşılaştırılması.
  - Dersin bunları nasıl temsil ettiği.
  - Dersin neyi söyleyemeyeceği: özet yeniden hesaplanmıyor, imza kriptografik olarak doğrulanmıyor, deney yalnız üç parçalık.

  Yanına sentetik veri ve kalıcılık notu kondu.
- **Çelişki:** "Bu derste FastAPI veya Qdrant çağrısı yapılmaz" cümlesi gerçek deneyle çelişecek biçimde okunuyordu. İş emrinde etiket yoktu, ama cümle düzeltildi.
- **Görünür fixture:** `tracks/ai-savunma/fixtures/ai-savunma-16/` altına README ve üç dosya eklendi.
  - `veri/kaynak_defteri.json`: 5 kaynak (pasif ve imzasız kaynaklar dahil, iki basamaklı sürüm bileşeni olan bir kaynak dahil) ve 5 bozuk defter (başında sıfır olan sürüm, `v` önekli sürüm, tanımsız güven, `1` değeri, yinelenen kimlik).
  - `veri/getirilen_parcalar.json`: 7 parça. Bu parçalardan en yüksek skorlu dördünün üçü doğrulanamıyor: tahrif edilmiş sürüm, yetim kaynak, pasif kaynak, imzasız not.
  - `veri/provenance_kayitlari.json`: Referansla üretilmiş provenance kayıtları ve 3 bozuk kayıt (çelişkili, yinelenen neden, `kritik`).
  - Beklenen sonuçlar referansla doğrulandı. Görev 1–3 `hazirla("ai-savunma-16")` çağırıyor.
- **Kusurlu başlangıç kodları (4 görev):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Sürümde yalnız üç parça olup olmadığına bakıyor | 5 bozuk defter kabul ediliyor |
  | 2 | Yalnız kaynağın varlığına bakıyor, bilinmeyen kaynağa `orta` güven veriyor | Tahrif, pasif ve imzasız parçalar doğrulanabilir çıkıyor; yetim parça `orta` alıyor |
  | 3 | Doğrulanabilirliği yok sayıyor | `p-tahrif` (0.93) listenin başına çıkıyor, 3 bozuk kayıt kabul ediliyor |
  | Gerçek deney | En yüksek skorlu iki parçayı alıyor | Çalıştır'da gerçek skorlarla `c-zehirli` seçiliyor |

- **Anlatım:** 5 anlatım bloğu, toplam yaklaşık 900 kelime. Eklenen konular:
  - Saldırgan bakışı: dört sahte içerik yolu ve sorguya benzeyecek biçimde yazılmış metin.
  - Skorun neden güven sayılmadığı ve provenance kapısının sıralamadan önce gelmesi gerektiği.
  - Sık tuzaklar: sürümü sayı gibi karşılaştırmak, bilinmeyen kaynağa varsayılan güven vermek, pasif kaynak, çelişkili kayıt.
  - Gerçek deneyin adımları, bu makinede ölçülen skorlar ve "doğru görünen ama talimat taşıyan içerik" notu.
- **Gerçek deney modülü (`sandbox/ai_gercek_ai_savunma_16.py`, yalnız bu derse ait):**
  - Gömme vektörleri doğrulanıyor: sayı, boyut, sonlu değer ve sıfır olmayan norm. Geçersizse `GercekLabYok` hatası veriliyor.
  - Öğrencinin seçimi bağımsız `guvenli_rag_secimi_referans` ile karşılaştırılıyor; sonuç `secim_dogru` alanında.
  - "Tahrif edilmiş parça seçilenlerden daha alakalı mıydı?" bilgisi artık öğrencinin değil, referans seçimin skorlarına göre hesaplanıyor.
  - Metinler, provenance ve vektör boyutu kanıta yazılıyor.
- **Kopya koruması:**
  - Yasak listesi `("guvenli_rag_secimi_referans", "referans_provenance", "kanit_yaz")` oldu. Eski hâli `("referans", "referans_provenance", "getattr")` idi ve ihlalde test durmuyordu.
  - AST kontrolü eklendi; ihlalde `stop()` çağrılıyor.
- **Gerçek deney testi:**
  - Sözleşmeye yeni durumlar eklendi: eşit skorda kimlik sırası, `bilinmiyor` güvenin `dusuk` eşikte de seçilmemesi, yinelenen kimlik, 1.5 ve bool skor, yinelenen neden, `kritik` güven.
  - Gerçek skorlarla yapılan seçimin referansla birebir aynı olması kontrolü eklendi.
  - **Bilerek yapılan değişiklik:** Eski `zehirli_daha_alakali_secilenden` kontrolü kaldırıldı. Bu kontrol, gömme modelinin tahrif edilmiş parçaya seçilen bir parçadan daha yüksek skor vermesini kabul koşulu yapıyordu; yani bir ölçüm sonucunu şart koşuyordu. Bilgi artık bulgu olarak kanıtta tutuluyor. Asıl savunma kontrolü (tahrif edilmiş parça doğrulanamaz ve seçilmez) korundu. Referans karşılaştırması eklendi.
  - Kanıt yalnız `kabul=all(sonuclar)` ile yazılıyor.
- Ortak `sandbox/ai_gercek_lab.py`, `engine/` ve `web/` değiştirilmedi.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

| Kontrol | Komut | Sonuç |
|---|---|---|
| validate | `tools/validate.py ai-savunma-16` (PAFTA_DATA=`<scratchpad>/s16-kabul`) | **TEMİZ**, 9 kontrol |
| tahmin | `docs/denetim/araclar/tahmin.py . ai-savunma-16` | 1 tahmin, **0 şüpheli** |
| mutasyon | `kirp_gercek.py` kopyası, ardından `mutasyon.py --en-cok 1000 ai-savunma-16` | 5 + 20 + 13 = 38 mutant, **0 geçen**; kopya silindi |
| kopya sondası | `kopya_sonda.py ai-savunma ai-savunma-16 ...` | 6/6 **fail → korunuyor**, kanıt yazılmadı |

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/s16-kabul/ai-kanit/savunma-rag-*.json`, kabul `true`.
- **Gömme modeli:** `all-minilm:22m`, 384 boyut.
- **Kosinüs skorları:**

  | Parça | Skor |
  |---|---|
  | `c-guncel` | 0.761 |
  | `c-zehirli` | 0.579 |
  | `c-kargo` | 0.496 |

- **Seçim (`orta` eşik):** `c-guncel` ve `c-kargo`; referansla aynı. `c-zehirli` `surum` nedeniyle elendi. Bu parça seçilen `c-kargo`'dan daha alakalıydı.
- **Çalıştır (CLI runner `run`):** Başlangıç kodu `ok` döndü ama `c-zehirli` parçasını seçti; referansla uyumsuzluk görünür.
- **Görev 1–3 (görünür veriyle elle koşturuldu):** Başlangıç kodları tablodaki kusurları gösterdi. Çözümler:
  - 5 bozuk defteri ayrı nedenlerle reddetti.
  - Provenance'ı README tablosuyla aynı üretti.
  - `p-politika` ve `p-sss` parçalarını seçti, 3 bozuk kaydı reddetti.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.** Kontrol, Çalıştır ve dosya erişimi yalnız CLI ve runner üzerinden doğrulandı.
- Qdrant ve FastAPI çalıştırılmadı.
- `metin_sha256` alanı metinden yeniden hesaplanmadı. Bu, iş emri dışı bir sözleşme değişikliği olurdu; tabloda sınır olarak yazıldı.
- Kurulum, indirme, commit/push ve puan yazımı yapılmadı. Ollama sunucusuna dokunulmadı.
