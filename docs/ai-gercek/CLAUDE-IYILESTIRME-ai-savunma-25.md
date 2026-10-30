# ai-savunma-25 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Çelişki:** İş emrinde etiket olarak yoktu, ama ilk anlatımda gerçek deneyle çelişen bir cümle vardı: "Bu derste Elastic, SigNoz veya MLflow'a bağlanılmaz; ağ, gerçek model ve gerçek olay verisi kullanılmaz." Bu cümle de düzeltildi.
- **Tablo + `[!NOT]`:** İlk anlatımın başına bir tablo eklendi. Tablo üç şeyi gösteriyor: gerçek bir olayda kanıtın nereden toplandığı (Elastic, SigNoz, MLflow, uygulama sunucusu), manifesto ve devir zincirinin nasıl tutulduğu, ve dersin neyi söyleyemeyeceği (imza, zaman damgası servisi, değiştirilemez depolama yok). Ardından sentetik veri ve kalıcılık notu var.
- **Görünür fixture:** `tracks/ai-savunma/fixtures/ai-savunma-25/` altına README ve üç veri dosyası eklendi:
  - `veri/kanit_manifestolari.json`: 3 geçerli manifesto ve 5 bozuk manifesto. Geçerlilerden biri 0 baytlık boş bir yedek, biri 2,4 GB'lık bir ağırlık dosyası. Bozuklar: büyük harfli özet, kısa özet, boşluklu kimlik, negatif bayt, bool zaman.
  - `veri/olaylar.json`: sırası karışık 4 olay ve 3 bozuk olay. Olaylar dört seviyeyi ve dört kategoriyi kapsıyor; birinin kanıt listesi boş.
  - `veri/devir_zinciri.json`: karışık sırada iki kanıtın devir kayıtları (birinde aynı saniyede iki devir var) ve 5 bozuk zincir. Bozuk zincirler: sıra atlama, zamanın geri gitmesi, kopuk sahiplik, değişen özet, sıfırdan başlamama.
  - Görev 1–3 `hazirla("ai-savunma-25")` çağırıyor.
- **Kusurlu başlangıç kodları (4 görev):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Özeti yalnız uzunluğa göre denetliyor, 0 baytı reddediyor | `bos-yedek` reddediliyor; büyük harf, boşluklu kimlik ve bool zaman kabul ediliyor |
  | 2 | Erişimi kanıttan önce sınırlıyor, her olaya bu adımı ekliyor, seviyeleri alfabetik sıralıyor | Plan sırası `INC-044, 041, 043, 042` oluyor |
  | 3 | Girdi sırasıyla işliyor, devir kurallarını denetlemiyor | `gateway-log` için son sahip `olay-yoneticisi` çıkıyor (doğrusu `adli-depo`), 5 bozuk zincir kabul ediliyor |
  | Gerçek deney | Özeti büyük harfe "normalleştiriyor" | Çalıştır'da doğru manifesto hem şema hem bütünlük kontrolünden kalıyor |

- **Anlatım:** 3 anlatım bloğu, yaklaşık 800 kelime. Eklenen konular:
  - AI olayının farkı: kanıt sohbet kaydına, RAG belgesine, ajan loguna ve model sürümüne dağılır; hızlı müdahale kanıtı yok edebilir; bu yüzden sıra kaydet, koru, sınırla olmalıdır.
  - Saldırgan bakışı.
  - Savunucu tarafı ve sık tuzaklar: boş dosya, özetin biçimi, zaman, sahiplik.
  - Gerçek deneyin 5 adımı ve bu makinede ölçülen sonuç.
- **Gerçek deney modülü (`sandbox/ai_gercek_ai_savunma_25.py`, yalnız bu derse ait):**
  - **Gerçek tahrif senaryosu eklendi.** Eski "sahte" manifestonun özeti yalnız sıfırlardan oluşuyordu. Şimdi kanıt dosyasının geçici bir kopyasında yalnız `ozet` alanının sonuna ` [duzenlendi]` ekleniyor (13 bayt, biçim korunuyor). Kopya yeniden özetleniyor ve doğru manifestoyla karşılaştırılıyor. Asıl kanıt dosyasına dokunulmuyor, kopya siliniyor.
  - Model boş yanıt verirse `GercekLabYok` hatasıyla duruluyor.
  - Model yanıtı, manifestolar ve ayarlar kanıta yazılıyor.
  - Bütünlük kontrolüne bayt sayısı da eklendi.
  - Testin kullandığı `kanit_manifestu_dogrula_referans` eklendi.
- **Kopya koruması:**
  - Yasak listesi `("kanit_manifestu_dogrula_referans", "kanit_yaz")` oldu. Eskiden `("referans", "getattr")` idi ve ihlalde test durmuyordu.
  - AST kontrolü eklendi; ihlalde `stop()` çağrılıyor.
- **Gerçek deney testi:**
  - Sözleşmeye eklenen durumlar: girdiyi değiştirmeme, 64 karakterlik kimlik, `bayt=0` ve `zaman=0`, bool ve kesirli zaman, 65 karakterlik kimlik, `-` ile başlayan kimlik, onaltılık olmayan özet.
  - Eklenen kontroller: tahrif edilmiş kopyanın yakalanması; iki gerçek manifestoda çıktının referansla birebir aynı olması.
  - Eski iki kontrol korundu.
- Ortak `sandbox/ai_gercek_lab.py`, `engine/` ve `web/` değiştirilmedi.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

| Kontrol | Komut | Sonuç |
|---|---|---|
| validate | `tools/validate.py ai-savunma-25` (PAFTA_DATA=`<scratchpad>/s25-kabul`) | **TEMİZ**, 9 kontrol. Fixture sırası düzeltildikten sonra yeniden koşturuldu. |
| tahmin | `docs/denetim/araclar/tahmin.py . ai-savunma-25` | 1 tahmin, **0 şüpheli** |
| mutasyon | `kirp_gercek.py`, ardından `mutasyon.py --en-cok 1000 ai-savunma-25` | 5 + 11 + 14 = 30 mutant, **0 geçen**; kopya silindi |
| kopya sondası | `kopya_sonda.py ai-savunma ai-savunma-25 ...` | 6/6 **fail → korunuyor**, kabul kanıtı yazılmadı |

## Gerçek sonuç

- **Kanıt dosyası:** `<scratchpad>/s25-kabul/ai-kanit/savunma-olay-*.json`, kabul true.
- **Model:** `qwen3:4b-instruct-2507`. Belgeyi şöyle özetledi: "Pafta, yerel modellerle çalışabilen bir güvenlik eğitimini sunar ve kurulumu birkaç komutla tamamlanır."
- **Özetler:**

  | Dosya | SHA-256 | Boyut |
  |---|---|---|
  | Gerçek kanıt dosyası | `f2d48253edc7…` | 1938 bayt |
  | Tahrif edilmiş kopya | `2bb03a480369…` | 1951 bayt |

- **Sonuçlar:**

  | Manifesto | Şema | Bütünlük |
  |---|---|---|
  | Doğru | geçti | geçti |
  | Sahte (sıfır özet) | geçti | kaldı |
  | Doğru, tahrif edilmiş kopyaya karşı | — | kaldı |

- **Çalıştır (CLI runner `run`):** Kusurlu başlangıç kodu `ok` döndü. Doğru manifesto şema ve bütünlük kontrolünden kaldı, yani kusur görünür durumda.
- **Görev 1–3, görünür veriyle elle koşturuldu:** Başlangıç kodları yukarıdaki tablodaki kusurları gösterdi. Çözümler şunları yaptı:
  - Boş yedeği kabul etti.
  - Doğru plan sırasını üretti; `erisimi_sinirla` adımını yalnız kritik ve yüksek seviyeli olaylara koydu.
  - Devir zincirini doğru özetledi.
  - 5 bozuk zinciri ayrı ayrı nedenlerle reddetti.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.** Kontrol, Çalıştır ve dosya erişimi yalnız CLI ve runner üzerinden doğrulandı.
- Elastic, SigNoz ve MLflow çalıştırılmadı.
- Kurulum, indirme, commit/push ve puan yazımı yapılmadı. Ollama sunucusuna dokunulmadı.
