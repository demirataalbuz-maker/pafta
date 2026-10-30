# ai-savunma-26 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Çelişki:** İlk anlatımdaki "Bu derste Promptfoo veya Ollama çalıştırılmaz" cümlesi kaldırıldı. Yeni metin: görev 1–3 sentetik veriyle çalışır, son adım kurulu yerel Ollama modelini gerçekten çağırır. Promptfoo ve garak çalıştırılmaz; yalnız biçimleri örnek alınır.
- **Tablo + `[!NOT]`:** İlk anlatımın başına "Gerçek araç/model ne gösterir | Bu ders ne kullanır | Ne söyleyemez?" tablosu ve sentetik veri/kalıcılık notu eklendi.
- **Görünür fixture:** `tracks/ai-savunma/fixtures/ai-savunma-26/` altına README ve `veri/eval_kosusu.json` eklendi. Dosyanın içeriği:
  - Ana koşu: 8 saldırı ve 4 benign vaka. ASR 0.25 ve yanlış pozitif oranı 0.25 çıkar; ikisi de eşiğe tam eşittir.
  - `yalniz_saldiri_kosusu`: hiç benign vaka içermez, beklenen karar `veri_yetersiz`.
  - 4 bozuk vaka. Bilerek tutarsız kayıtlar: benign tehditli saldırı, bool yerine `1`, başarılı işaretli benign, yanlış pozitifli saldırı.

  Görev 1–3'ün setup bloğu `ai_savunma_veri.hazirla("ai-savunma-26")` çağırır. Başlangıç kodları bu dosyayı okuyup sonucu yazdırır. Veri sentetik olarak etiketlendi ve kalıcı değil. Testler bu dosyadan ayrı, gizli verilerle sınar.
- **Kusurlu başlangıç kodları (4 görev):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Yalnız alanların varlığına bakar, girdinin kendisini döndürür | 4 bozuk vakayı kabul eder |
  | 2 | ASR'yi bütün vakalara böler, boş paydaya `0` yazar | ASR 0.25 yerine 0.167 |
  | 3 | Eşiğe eşitliği "aşıldı" sayar, boş kümeyi 0 kabul eder | Ana koşu `kaldi` (doğrusu `gecti`), yalnız-saldırı koşusu `gecti` (doğrusu `veri_yetersiz`) |
  | Gerçek deney | Şema denetimi yok, ASR paydası yanlış, benign yoksa da `gecti` der | Kontrol'de reddedilir |

- **Anlatım:** 3 anlatım bloğu toplam 997 kelime. Eklenen konular:
  - değerlendirici seçiminin ASR'yi nasıl belirlediği
  - aşırı ret (over-refusal) ve iki eşiğin neden birlikte gerektiği
  - saldırgan bakışı: eval dışı desenler, Goodhart yasası, ayarlamada kullanılmayan tutma kümesi
  - küçük örneklem tuzağı: 3 vakada ASR yalnız 0, 1/3, 2/3 ya da 1 olabilir
  - sık tuzaklar: boş payda, karışık payda, `1`/`True` karışıklığı, boş yanıtın savunma başarısı sayılması
  - gerçek deneyin 5 adımı ve sınırları
  - bu makinede ölçülen sonuç

  Ölçülen sonucun yalnız o koşuya ait olduğu metinde açıkça belirtildi.
- **Gerçek deney modülü (`sandbox/ai_gercek_ai_savunma_26.py`, bu derse özel):**
  - Her vakanın ham yanıtı (ilk 600 karakter), girdisi, tohumu ve sonucu `ham_yanitlar` alanına yazılır.
  - Ayarlar kanıta yazılır: sıcaklık, en fazla token, eşikler, dedektör ve ret sezgisinin tanımı.
  - Model boş yanıt verirse deney `GercekLabYok` hatasıyla durur. Eskiden boş yanıt saldırıda "sızmadı" sayılıyordu, bu da sahte bir savunma başarısıydı.
  - Testin kullandığı `eval_raporu_referans` eklendi.
  - Çalıştır çıktısında ham yanıtlar görünür. Çalıştır kanıtına vakalar ve ham yanıtlar yazılır, `kabul: false` olarak kalır.
- **Kopya koruması:**
  - Test şu çağrıyı yapar: `kod_denetimi(src, yasak=("eval_raporu_referans", "sizinti_referans", "kanit_yaz"))`. Eskiden yasak listesi `("referans", "getattr")` idi ve ihlalde test durmuyordu.
  - Ek AST kontrolü şunları reddeder: yasak adların ve `*` importu, `inspect`/`importlib`/`runpy` importu, `exec`/`eval`/`compile`/`__builtins__` kullanımı.
  - İhlalde `stop()` çağrılır, yani deney ve kanıt yazımı hiç başlamaz.
- **Gerçek deney testi güçlendirildi (zayıflatılmadı):**
  - Eski sözleşme vakaları korundu. Bunlara eklenenler:
    - `veri_yetersiz` durumunda `nedenler` listesinin tam eşleşmesi ve yanlış pozitif oranının `None` olması
    - yalnız yanlış pozitif eşiğinin aşıldığı tam çıktı
    - eşiğe eşitlik (0)
    - bool yerine `1`, başarılı işaretli benign, yinelenen kimlik, NaN eşik
  - Gerçek vakalardan üretilen rapor `eval_raporu_referans` ile birebir karşılaştırılır.
  - Canary sayısının vakalarla tutarlı olduğu denetlenir.
  - Kanıt yalnız `kanit_yaz(..., kabul=all(sonuclar))` ile yazılır. Kanıta vakalar ve ham yanıtlar da eklendi.
  - Saldırının başarılı ya da başarısız olması kabul koşulu değildir.
- Ortak `sandbox/ai_gercek_lab.py`, `engine/` ve `web/` değiştirilmedi.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`)

| Kontrol | Komut ve ortam | Sonuç |
|---|---|---|
| Doğrulama | `tools/validate.py ai-savunma-26`, PAFTA_DATA=`Desktop/pafta-s26-kabul-20261030` | **TEMİZ**, 9 kontrol (tahmin 1, çözüm 4, başlangıç 4). Son düzenlemeden sonra yeniden koşturuldu. |
| Tahmin | `docs/denetim/araclar/tahmin.py . ai-savunma-26` | 1 tahmin, **0 şüpheli** |
| Mutasyon | `kirp_gercek.py Desktop/pafta-mutasyon-s26-20261030`, ardından `mutasyon.py --en-cok 1000 ai-savunma-26` | 5 + 12 + 19 = 36 mutant, **0 geçen**. Kopya klasörü sonra silindi. |
| Kopya sondası | `kopya_sonda.py ai-savunma ai-savunma-26 ...`, PAFTA_DATA=`Desktop/pafta-s26-sonda-20261030` | 6 denemenin 6'sı **fail → korunuyor**; hiçbir kanıt dosyası yazılmadı |

Kopya sondasında denenen yollar:
1. Takma adla doğrudan import
2. Modül özniteliği üzerinden erişim
3. `getattr` ile birleştirilmiş adla erişim
4. `inspect.getsource` + `exec`
5. Yıldızlı import (`import *`)
6. `importlib` + `__dict__`

## Gerçek sonuç

- Kanıt dosyası: `Desktop/pafta-s26-kabul-20261030/ai-kanit/savunma-eval-1793374062234.json` (kabul: true).
- Model: `qwen3:4b-instruct-2507-q4_K_M`, digest `0edcdef34593…`. Sıcaklık 0, en fazla 120 token.
- Sonuç: 3 bilinen saldırının hiçbiri canary sızdırmadı, 2 zararsız soru da yanıtlandı.
  - ASR 0/3 = 0.0
  - yanlış pozitif 0/2 = 0.0
  - savunma geçiş oranı 1.0
  - karar `gecti`
- Ham yanıtlar kanıtta duruyor. Saldırılarda model belgeyi özetleyip kodu vermedi.
- Çalıştır (CLI üzerinden runner `run`):
  - Çözüm ve başlangıç kodu `ok`; ham yanıtlar ekrana basıldı.
  - Gerçek deneyde başlangıç kodu Kontrol'de `fail` aldı. Kontrol başarısız olduğu için deney koşmadı ve kanıt `kabul: false` olarak yazıldı.
- Görev 1–3'ün başlangıç kodu ve çözümü görünür veriyle elle koşturuldu. Başlangıç kodları kusuru gösterdi: bozuk vakalar kabul edildi, ASR 0.167 çıktı, yanlış kararlar verildi. Çözümler doğru sonucu verdi: bozuk vakalar reddedildi, ASR 0.25, kararlar `gecti` ve `veri_yetersiz`.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.** Ders ekranında Kontrol/Çalıştır akışı ve görünür dosyaya erişim yalnız CLI ve runner üzerinden doğrulandı.
- Ölçümde yalnız 3 saldırı ve 2 benign vaka var; bu, deney tasarımının bilinçli bir sınırı. Vaka seti genişletilmedi.
- Kurulum, indirme, commit/push ve puan yazımı yapılmadı. Ollama sunucusuna dokunulmadı; model yalnız `SohbetOturumu` üzerinden çağrıldı.
