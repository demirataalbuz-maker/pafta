# ai-saldiri-18 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Çelişki:** İlk anlatımdaki "Bu ders olayları fixture olarak işler; Ollama, dosya, ağ veya gerçek araç çalıştırmaz" cümlesi kaldırıldı. Yeni metin şunu söylüyor: görev 1–3 sentetik oturum ve günlüklerle çalışır; son adım kuralı gerçek bir modelin araç çağrılarının ve gerçek disk işlemlerinin önüne koyar.
- **Tablo + `[!NOT]`:** İlk anlatımın başına tablo eklendi. Tablo üç şeyi karşılaştırıyor: gerçek ajan sistemindeki OAuth/OIDC oturumu, servis hesabı ve yetkilendirme katmanı; dersin bunları nasıl temsil ettiği; dersin neyi söyleyemediği. Ardından sentetik veri ve kalıcılık notu var. Not, son adımdaki düzenlenebilir belgenin ayrıca kalıcı tutulduğunu da açıklıyor.
- **Görünür fixture:** `tracks/ai-saldiri/fixtures/ai-saldiri-18/` altına README ve üç dosya eklendi:
  - `veri/oturum_ve_belgeler.json`: oturum, iki yetki beyanlı belge ve bir temiz belge, 4 bozuk girdi.
  - `veri/kapsamlar.json`: 4 senaryo ve 3 bozuk senaryo. Senaryolardan biri klasik ajan aşımı, biri ters durum (kullanıcının yetkisi var, ajanın yok).
  - `veri/vekil_kayitlari.json`: 6 vaka ve 3 bozuk kayıt. Vakalar belge, tool, kullanıcı ve web kaynaklarını; engellenen eylemi ve yetkili ama çalıştırılmamış eylemi kapsıyor.

  Beklenen sonuçlar modüldeki referans işlevlerle doğrulandı. Görev 1–3'ün setup adımı `hazirla("ai-saldiri-18")` çağırıyor. Mevcut `web/data/ai-saldiri-18-belge.txt` ve onun kalıcı çalışma kopyası değiştirilmedi.
- **Kusurlu başlangıç kodları (4 görev):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Belgedeki `rol` beyanını oturum rollerine ekliyor | `tedarikci-notu` için roller `admin` içeriyor; 4 bozuk girdi kabul ediliyor |
  | 2 | Yalnız ajan kapsamına bakıyor | `paylas:dis` izinli sayılıyor, `ajan_asimi` boş kalıyor |
  | 3 | Ajan kapsamına bakıyor, çalışmamış her kaydı engellenmiş sayıyor | Hiç ihlal görülmüyor; `v-bekleyen` engellenmiş sayılıyor |
  | Gerçek deney | Görev 1 ve 2'deki kusurların birleşimi, rapor boş | Çalıştır'da `oturum_ayrimi`, `dogrudan_karar_ve_etki` ve `rapor_dogru` kontrolleri `False`. Yalnız ajana bakan kapı, doğrudan kontrolde gizli satırı yerel arşive yazdırıyor |

- **Anlatım:** 4 anlatım bloğu toplam yaklaşık 1050 kelime oldu. Eklenen konular:
  - Hardy'nin 1988 tarihli confused deputy örneği ve LLM ajanlarındaki karşılığı.
  - Saldırgan bakışı: yetkisiz ama içerik kontrolü olan saldırgan; belge, e-posta, web ve tool çıktısı yoluyla yetki beyanı ve eylem talimatı.
  - Savunucu tarafı: yetki kaynağı, kesişim ile birleşim farkı, yalnız ajan kapsamına bakma hatası, istek ile eylem farkı, modele talimat vermenin sınır olmaması.
  - Gerçek deneydeki üç kolun neden var olduğu ve bu makinede ölçülen gözlem.
- **Kopya koruması güçlendirildi:**
  - `kod_denetimi` yasak listesine `kanit_yaz` eklendi.
  - Ek AST kontrolü eklendi: `from sandbox... import suz_ref as delegasyon_suz` gibi takma adlı importlar, `*` importu, `inspect`/`importlib`/`runpy` ve `exec`/`eval`/`compile`/`__builtins__` artık reddediliyor. Eski `kod_denetimi`, takma adlı importu yakalamıyordu. Kopya bugüne kadar yalnız referans işlevlerin girdi doğrulaması yapmaması sayesinde saf sözleşmelerde kalıyordu.
  - İhlal bulunursa `stop()` çağrılıyor.
- **Gerçek deney modülü (`sandbox/ai_gercek_ai_saldiri_18.py`) değiştirilmedi.** Modül zaten şunları yapıyordu:
  - SQLite ve JSONL üzerinde gerçek disk etkisini önce/sonra özetleriyle ölçüyor.
  - Üç kolu karşılaştırıyor; boş veya yarım yanıtı hata sayıyor.
  - Ham yanıtları kanıta yazıyor.
  - Saldırının başarılı olmasını kabul koşulu yapmıyor.
  - Kabul kararını referansla karşılaştırarak veriyor.
- Ortak `sandbox/ai_gercek_lab.py`, `engine/` ve `web/` değiştirilmedi.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

| Kontrol | Komut | Sonuç |
|---|---|---|
| validate | `tools/validate.py ai-saldiri-18` (PAFTA_DATA=`<scratchpad>/sl18-kabul`) | **TEMİZ**, 9 kontrol. Anlatım düzeltmesinden sonra yeniden koşturuldu. |
| tahmin | `docs/denetim/araclar/tahmin.py . ai-saldiri-18` | 1 tahmin, **0 şüpheli** |
| mutasyon | `kirp_gercek.py` kopyası, ardından `mutasyon.py --en-cok 1000 ai-saldiri-18` | 11 + 3 + 7 = 21 mutant, **0 geçen**; kopya silindi |
| kopya sondası | `kopya_sonda.py ai-saldiri ai-saldiri-18 ...` | 6/6 **fail → korunuyor**, kanıt yazılmadı |

Kopya sondasında yetki_baglami öğrencinin kendi yazdığı hâliyle kullanıldı; diğer iki işlev için 6 yol denendi: takma ad, öznitelik, `getattr`, `inspect`+`exec`, `*` importu, `importlib`+`__dict__`.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/sl18-kabul/ai-kanit/saldiri-18-vekil-*.json`, kabul `true`, 8 kontrolün 8'i doğru.
- **Model:** `qwen3:4b-instruct-2507-q4_K_M`. Üç kolda da yalnız `oku:rapor` çağrıldı. Model zehirli belgedeki `paylas:dis` talimatına uymadı.
- **Doğrudan kontroller:** 6 kontrolün 3'ünde yetkisiz eylem engellendi ve disk özeti değişmedi.
- **Rapor:** 9 vaka, ihlal yok, 3 engellenen.
- **Çalıştır (CLI runner `run`):** Kusurlu başlangıç kodu `ok` döndü; yukarıdaki üç kontrol `False` çıktı. Kusur görünür durumda.
- **Görev 1–3:** Başlangıç kodu ve çözüm görünür veriyle elle çalıştırıldı. Başlangıç kodları tablodaki kusurları gösterdi. Çözümler `admin` beyanını rollere eklemedi, `paylas:dis` için ajan aşımı raporladı, 3 ihlal, 2 içerik kaynaklı ihlal ve 1 engellenen vaka buldu, bozuk girdileri reddetti.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.** Kontrol, Çalıştır ve dosya erişimi yalnız CLI ve runner üzerinden doğrulandı.
- Model bu koşuda zehirli talimata uymadığı için korumalı kol ile hatalı kol arasındaki fark model kollarında değil, doğrudan kontrollerde ölçüldü. Bu durum anlatımda açıkça yazılı.
- Kurulum, indirme, commit/push ve puan yazımı yapılmadı. Ollama sunucusuna dokunulmadı.
