# ai-savunma-24 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Kapsam eksiğine yanıt

Denetçinin kapsam notu şuydu: "Sigma kuralları kendi eşleştiriciyle sınanıyor; gerçek Sigma derleyicisi (pySigma/sigma-cli) yok."

**`.ai-venv` içinde pySigma 2.0.1 zaten kurulu.** Bu yüzden indirme ya da kurulum yapılmadı. Gerçek deney artık kuralları gerçek Sigma YAML'ından `SigmaCollection.from_yaml` ile ayrıştırıyor ve şu alanları ders şemasına çeviriyor:

- başlık
- UUID kimlik
- `level`
- `logsource.category`
- `|contains` değerleri
- `|all` belirleyicisi

pySigma'nın kendi doğrulaması da derste kullanılıyor:

- Kimlik UUID değilse `SigmaIdentifierError` hatası verir. Fixture yazılırken bu hatayla karşılaşıldı ve kimlikler UUID'ye çevrildi.
- Bilinmeyen bir belirleyici gelirse (`|contians`) `SigmaModifierError` hatası verir. Deney bu reddi kanıta yazar.

Ders, Sigma'nın tam koşul dilini (`1 of`, `not`) ve Elastic'e dönüştürmeyi hâlâ kapsamıyor. Bu sınır tabloda açıkça yazıyor.

## Ne değişti

- **Çelişki:** "Bu derste Sigma veya Elastic çalıştırılmaz; ağa veya modele erişilmez" cümlesi kaldırıldı. Yeni metne göre görev 1–3 sentetik veriyle çalışır; son adım pySigma'yı ve yerel Ollama modelini gerçekten çalıştırır. Elastic ve sigma-cli çalıştırılmaz.
- **Tablo + `[!NOT]`:** Gerçek Sigma yapısı (`title`, `id`, `level`, `logsource`, `detection`, `condition`), pySigma ve sigma-cli'nin işlevi ve dersin sınırları tabloya, sentetik veri ve kalıcılık bilgisi nota yazıldı.
- **Görünür fixture:** `tracks/ai-savunma/fixtures/ai-savunma-24/` altında:
  - `veri/sigma/llm_injection.yml` ve `llm_egress_yetki.yml`: **gerçek Sigma biçiminde** 5 kural. pySigma 2.0.1 ile ayrıştırılabilir.
  - `veri/kurallar.json`: bu YAML'ların pySigma ile ayrıştırılıp ders şemasına çevrilmiş hâli. İçinde 4 bozuk kural da var: pasif, büyük harfli, yinelenen, `network` alanlı.
  - `veri/olaylar.json`: 10 olay ve 4 bozuk olay. Olaylar şu durumları gösteriyor:

    | Durum | Olaylar |
    |---|---|
    | İki kural eşleşiyor | `e-02`, `e-10` |
    | Yanlış negatif: Türkçe ifade, `https://`, IP adresiyle metadata | `e-03`, `e-04`, `e-05` |
    | Yanlış pozitif: destek kaydında alıntı | `e-08` |
    | Alan sınırı | `e-09` |

  - README. Görev 1–3 `hazirla("ai-savunma-24")` çağırıyor. Görev 1'in başlangıç kodu YAML'ın ilk satırlarını gösteriyor.
- **Kusurlu başlangıç kodları (4 görev):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Yalnız seviyeyi denetliyor | 4 bozuk kural kabul ediliyor |
  | 2 | Alan denetimi yok, casefold yok, `tumu` yerine `herhangi` uygulanıyor | `e-01` kaçıyor; `e-04`, `e-05`, `e-09` yanlış eşleşiyor |
  | 3 | Seviyeyi alfabetik `max` ile seçiyor, şema denetimi yok | `e-10` `orta` alıyor (doğrusu `kritik`), 4 bozuk olay kabul ediliyor |
  | Gerçek deney | Casefold yok | Çalıştır'da gerçek "Ignore previous" girdisi temiz sayılıyor |

- **Anlatım:** 5 anlatım bloğu toplam 1037 kelime oldu. Eklenen konular:
  - Sigma'nın neden var olduğu: SIEM'den bağımsızlık, sürüm kontrolü, test.
  - YAML'dan ders şemasına çeviri tablosu.
  - Çıktının nasıl okunacağı: yanlış pozitif ve yanlış negatif örnekleri.
  - Saldırgan bakışı ve `|all` ile `herhangi` arasındaki denge.
  - Savunucu tarafı ve sık tuzaklar: alan, büyük harf, UUID, alarm yorgunluğu.
  - Gerçek deneyin adımları ve bu makinede ölçülen sonuç.
- **Gerçek deney modülü (`sandbox/ai_gercek_ai_savunma_24.py`, yalnız bu derse ait), baştan yazıldı:**
  - **Uydurma olay kaldırıldı.** Eskiden model aracı çağırmazsa egress olayı sabit `METADATA_URL` ile uyduruluyordu; kritik alarm kontrolü bu yüzden her zaman geçiyordu. Şimdi egress olayı yalnız modelin gerçek araç çağrısından üretiliyor.
  - **Modelin gerçek yanıtı artık bir olay** (`o-yanit`). Eskiden model yanıtları hiç kullanılmıyordu.
  - Kurallar pySigma ile ayrıştırılıyor. Bozuk YAML'ın reddi kaydediliyor.
  - Boş yanıt deneyi `GercekLabYok` ile durduruyor.
  - Kanıta şunlar yazılıyor: pySigma sürümü, ayrıştırılan kural ayrıntıları (alan adı, belirleyiciler, değerler, koşul), ham yanıtlar ve araç çağrıları.
  - Testin kullandığı `sigma_alarm_raporu_referans` eklendi.
- **Kopya koruması:**
  - `kod_denetimi(src, yasak=("sigma_alarm_raporu_referans", "kanit_yaz"))`. Eskiden yasak listesi `("referans", "getattr")` idi ve ihlalde test durmuyordu.
  - Ek AST kontrolü şunları reddediyor: yasaklı ve `*` import, `inspect`/`importlib`/`runpy`, `exec`/`eval`/`compile`/`__builtins__`.
  - İhlalde `stop()` çalışıyor.
- **Gerçek deney testi:**
  - Sözleşmeye yeni durumlar eklendi: ters sıra, iki kural eşleşmesi (`tumu` ve casefold), `https` yanlış negatifi, alan sınırı, boşluk ve TAB içeren metin, yinelenen kimlik.
  - Yeni kontroller:
    - pySigma 2 kural ayrıştırmış ve bozuk kuralı reddetmiş olmalı.
    - Girdi olayı `yuksek` almalı (deterministik).
    - Zararsız olay temiz kalmalı (deterministik).
    - Model URL önerdiyse ve URL `http://` ile `metadata` içeriyorsa `kritik` almalı.
    - Rapor, referans hesapla birebir aynı olmalı.
  - Kanıt yalnız `kabul=all(sonuclar)` ile yazılıyor.
- Ortak `sandbox/ai_gercek_lab.py`, `engine/` ve `web/` değiştirilmedi.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

| Kontrol | Komut | Sonuç |
|---|---|---|
| validate | `tools/validate.py ai-savunma-24` (PAFTA_DATA=`<scratchpad>/s24-kabul`) | **TEMİZ**, 9 kontrol. Fixture ve başlangıç kodu düzeltmesinden sonra yeniden koşturuldu. |
| tahmin | `docs/denetim/araclar/tahmin.py . ai-savunma-24` | 1 tahmin, **0 şüpheli** |
| mutasyon | `kirp_gercek.py` ile kopya, ardından `mutasyon.py --en-cok 1000 ai-savunma-24` | 10 + 15 + 15 = 40 mutant, **0 geçen**. Sonraki değişiklikler yalnız fixture, başlangıç kodu ve anlatımda oldu. Kopya silindi. |
| kopya sondası | `kopya_sonda.py ai-savunma ai-savunma-24 ...` | 6/6 **fail → korunuyor**, kanıt yazılmadı |

Kopya sondasında denenen 6 yol: takma ad, öznitelik, `getattr`, `inspect` + `exec`, `*` import, `importlib` + `__dict__`.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/s24-kabul/ai-kanit/savunma-sigma-*.json`, kabul true.
- **Ortam:** pySigma 2.0.1, model `qwen3:4b-instruct-2507-q4_K_M`.
- **Ayrıştırma:** 2 kural ayrıştırıldı. Bozuk YAML `SigmaModifierError: Unknown modifier 'contians'` ile reddedildi.
- **Araç çağrısı:** Model `istek_at` aracını çağırdı ve URL'yi aynen önerdi: `http://metadata.google.internal/computeMetadata/v1/token`.
- **Kararlar:**

  | Olay | Karar |
  |---|---|
  | `o-girdi` | alarm / yuksek |
  | `o-yanit` | temiz (model kalıbı alıntılamadı) |
  | `o-temiz` | temiz |
  | `o-egress` | alarm / kritik |

- **Çalıştır (CLI runner `run`):** Başlangıç kodu `ok` döndü ama gerçek "Ignore previous" girdisini temiz saydı; kusur görünür hâlde.
- **Görev 1–3, görünür veriyle elle koşturuldu:** Başlangıç kodları tablodaki kusurları gösterdi. Çözümler bozuk kayıtları reddetti, `e-10` için `kritik` verdi ve yanlış pozitif/negatifleri beklendiği gibi raporladı.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.** Kontrol, Çalıştır ve dosya erişimi yalnız CLI ve runner üzerinden doğrulandı.
- sigma-cli ile Elastic sorgusuna dönüştürme ve Sigma'nın tam koşul dili kapsanmadı. Bu sınır tabloda belirtildi.
- Kurulum, indirme, commit/push ve puan yazımı yapılmadı. Ollama sunucusuna dokunulmadı.
