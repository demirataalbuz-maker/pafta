# ai-savunma-23 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Çelişki:** İlk anlatımdaki "Bu derste Elastic veya FastAPI çalıştırılmaz; ağa veya modele erişilmez" cümlesi kaldırıldı. Yeni metne göre görev 1–3 sentetik veriyle çalışır; son adım kurulu Ollama modelini gerçekten çalıştırır. Elastic ve FastAPI bu derste çalıştırılmaz.
- **Tablo + `[!NOT]`:** İlk anlatımın başına bir tablo eklendi. Tablo, Elastic olay deposunun ve FastAPI 429/`Retry-After` sınırlamasının gerçekte ne gösterdiğini, dersin bunları nasıl temsil ettiğini ve neyi söyleyemediğini karşılaştırır. Yanına sentetik veri ve kalıcılık notu kondu.
- **Görünür fixture:** `tracks/ai-savunma/fixtures/ai-savunma-23/` altına README ve iki veri dosyası eklendi.
  - `veri/abuse_politikasi.json`: asıl politika ve 4 bozuk politika (0 eşik, 1 saatlik pencere, bool bekleme, eksik alan).
  - `veri/olay_akisi.json`: 6 kullanıcı ve 4 bozuk olay (`spam` türü, negatif zaman, boşluklu kullanıcı, bool zaman). Kullanıcılar şu durumları gösterir:

    | Kullanıcı | Durum | Beklenen karar |
    |---|---|---|
    | `u-ali` | düşük ve yavaş saldırgan | `izle` |
    | `u-bot` | araç eşiğine tam eşit | `beklet` |
    | `u-mert` | 60000 ms sınırındaki deneme sayılır | `beklet` |
    | `u-selin` | sızıntı önceliği | `engelle` |
    | `u-ece` | yalnız normal olaylar | `izin` |
    | `u-can` | normal olay referans zamanını ileri taşır | `izin` |

  Beklenen kararlar referansla doğrulandı. Görev 1–3'ün setup adımı `hazirla("ai-savunma-23")` çağırır. Veriler sentetik olarak etiketlendi ve kalıcı değil; testler gizli ve ayrı verilerle sınar.
- **Kusurlu başlangıç kodları (4 görev):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Yalnız `int` türüne bakıyor | 4 bozuk politikanın hepsini kabul ediyor |
  | 2 | Bütün girdinin en yeni olayını referans alıyor ve pencereyi `<` ile sınırlıyor | Bütün kullanıcıların sayımları 0 çıkıyor, 4 bozuk olay kabul ediliyor |
  | 3 | Jailbreak'i sızıntıdan önce değerlendiriyor, eşitlikte tetiklemiyor, engellemede tek kat bekleme uyguluyor | `u-bot`, `u-mert` ve `u-selin` yanlış biçimde `izle` alıyor |
  | Gerçek deney | Bütün olayları tek kullanıcı gibi sayıyor | Çalıştır'da zararsız kullanıcı da `beklet` alıyor |

- **Anlatım:** 5 anlatım bloğu toplam 1058 kelime oldu. Eklenen konular:
  - Sabit hız sınırının LLM API'lerinde neden yetmediği.
  - Sinyallerin ağırlığı: sızıntı ile girişim farkı.
  - Görünür verideki sınır durumları.
  - Saldırgan bakışı: düşük ve yavaş saldırı, hesaplar arasına bölme, uzun dönemli ve kullanıcı dışı sayaçlar.
  - Savunucu tarafı: referans zamanı, normal olaylar, öncelik, eşitlik, yanlış pozitifin bedeli.
  - Gerçek deneyin adımları, sınırları ve bu makinede ölçülen sonuç.
- **Gerçek deney modülü (`sandbox/ai_gercek_ai_savunma_23.py`, yalnız bu derse ait):**
  - Normal kullanıcı da saldırganla **aynı ölçüm hattından** geçiyor. Eskiden normal kullanıcının model yanıtı alınıyor ama hiç kullanılmıyordu; ona elle `normal` olayı yazılıyordu.
  - Model boş yanıt verirse deney `GercekLabYok` ile duruyor.
  - Her girdi için ham yanıt (ilk 600 karakter), iki sinyal, tohum ve zaman kanıta yazılıyor. Kural tespitinin, sızıntı ölçümünün ve mantıksal zamanların tanımı ayarlara eklendi.
  - Çalıştır çıktısı her girdinin sinyallerini ve ham yanıtını gösteriyor.
  - Testin kullandığı `uyarlanabilir_sinir_raporu_referans` eklendi.
- **Kopya koruması:**
  - Test `kod_denetimi(src, yasak=("uyarlanabilir_sinir_raporu_referans", "sizinti_referans", "kanit_yaz"))` çağırıyor. Eskiden `("referans", "getattr")` kullanılıyordu ve ihlalde test durmuyordu.
  - Ek AST kontrolü şunları reddediyor: yasak import ve `import *`, `inspect`/`importlib`/`runpy`, `exec`/`eval`/`compile`/`__builtins__`.
  - İhlal bulunursa test `stop()` ile duruyor.
- **Gerçek deney testi:**
  - Sözleşmeye yeni durumlar eklendi:
    - 60000 ms pencere sınırı
    - normal olayın referans zamanını ileri taşıması
    - sızıntı önceliği (2 kat bekleme)
    - tek araç olayıyla `izle`
    - ters sıra
    - bool ve negatif zaman, yinelenen kimlik
  - Gerçek olaylardan üretilen rapor, referans hesapla birebir karşılaştırılıyor.
  - Eski `jb_sayi >= 2` ve `saldirgan_karar in (beklet, engelle)` kontrolleri korundu. Jailbreak sinyali kural temelli olduğu için bu kontroller deterministik.
  - Eski `normal_karar == "izin"` kontrolü kaldırıldı. Normal kullanıcı artık gerçek modelden geçtiği için bu kontrol model davranışına bağlı hâle geliyordu. Yerine gelen referans karşılaştırması bu durumu da kapsıyor.
  - Kanıt yalnız `kabul=all(sonuclar)` ile yazılıyor; olaylar ve ham yanıtlar kanıta ekleniyor.
- Ortak `sandbox/ai_gercek_lab.py`, `engine/` ve `web/` değiştirilmedi.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

| Kontrol | Komut | Sonuç |
|---|---|---|
| validate | `tools/validate.py ai-savunma-23` (PAFTA_DATA=`<scratchpad>/s23-kabul`) | **TEMİZ**, 9 kontrol |
| tahmin | `docs/denetim/araclar/tahmin.py . ai-savunma-23` | 1 tahmin, **0 şüpheli** |
| mutasyon | `kirp_gercek.py` ile kopya alındı, ardından `mutasyon.py --en-cok 1000 ai-savunma-23` | 8 + 15 + 21 = 44 mutant, **0 geçen**; kopya silindi |
| kopya sondası | `kopya_sonda.py ai-savunma ai-savunma-23 ...` | 6/6 **fail → korunuyor**, kanıt yazılmadı |

Kopya sondasında denenen yollar: takma ad, öznitelik, `getattr`, `inspect`+`exec`, `import *`, `importlib`+`__dict__`.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/s23-kabul/ai-kanit/savunma-abuse-*.json`, kabul `true`.
- **Model:** `qwen3:4b-instruct-2507-q4_K_M`, sıcaklık 0.
- **Sinyaller:** 3 saldırgan girdisinin üçü de jailbreak sinyali verdi. Hiçbiri canary sızdırmadı; model belgeyi özetledi, kodu vermedi. Normal kullanıcı hiçbir sinyal vermedi.
- **Kararlar:** Saldırgan `beklet` (jailbreak 3), normal kullanıcı `izin` aldı.
- **Çalıştır (CLI runner `run`):**
  - Başlangıç kodu `ok` döndü ve normal kullanıcıya da `beklet` verdi; kusur görünür hâlde.
  - İlk Çalıştır denemesi `error` döndü ama ayrıntı vermedi. İkinci deneme `ok` döndü. Aynı anda Codex de ai-temel-14 için Ollama kullanıyordu; hatanın paylaşılan model kaynağındaki geçici bir çakışmadan geldiği düşünülüyor. **Bu doğrulanmadı.**
- **Görev 1–3:** Başlangıç kodu ve çözüm görünür veriyle elle çalıştırıldı. Başlangıç kodları yukarıdaki tablodaki kusurları gösterdi. Çözümler bozuk kayıtları reddetti ve 6 kullanıcının kararlarını doğru verdi.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.** Kontrol, Çalıştır ve dosya erişimi yalnız CLI ve runner üzerinden doğrulandı.
- Olay zamanları deney akışına göre atanmış mantıksal zamanlardır, istek saatleri değildir. Bu, anlatımda ve kanıttaki ayarlarda açıkça yazılı.
- Elastic ve FastAPI çalıştırılmadı.
- Kurulum, indirme, commit/push ve puan yazımı yapılmadı. Ollama sunucusuna dokunulmadı.
