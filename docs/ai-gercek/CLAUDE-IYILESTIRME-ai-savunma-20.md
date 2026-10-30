# ai-savunma-20 iyileştirme teslimi

Kendi uygulama kontrollerimi ben (claude-yazar) yaptım. Puanlama ve bağımsız denetim başka bir yapay zekânın işidir; bu dersi ben puanlamıyorum.

## Ne değişti

- **Çelişki:** İlk anlatımdaki "Bu derste Trivy, Cosign veya Ollama çalıştırılmaz; ... model indirilmez" cümlesi kaldırıldı. Yeni metin şunu söylüyor: görev 1–3 sentetik veriyle çalışır; son adım kurulu Ollama modelinin dosyalarını salt okunur açıp gerçek SHA-256 hesaplar. Trivy ve Cosign çalıştırılmaz, hiçbir model indirilmez.
- **Tablo + `[!NOT]`:** İlk anlatımın başına bir tablo eklendi. Tablo Cosign/Sigstore, Trivy/Grype, SBOM ve `sha256sum` araçlarını, dersin bunlardan neyi temsil ettiğini ve neyi söyleyemeyeceğini gösteriyor. Yanına sentetik veri ve kalıcılık notu kondu.
- **Görünür fixture:** `tracks/ai-savunma/fixtures/ai-savunma-20/` altına README ve iki dosya eklendi.
  - `veri/tedarik_politikasi.json`: asıl politika ve 4 bozuk politika (isteğe bağlı imza, boş tür, yinelenen risk, 50000 MB sınır).
  - `veri/bilesenler.json`:
    - görev 2 için 5 kayıt: biri boyut sınırına tam eşit, biri yasak imaj, biri üç ihlalli, biri imzasız
    - görev 3 için 4 kayıt: biri yalnız son karakterde farklı özet, biri tek `risk` nedeni gereken kayıt
    - 3 bozuk kayıt: büyük harfli özet, 63 karakterlik özet, yinelenen risk
  - Özetler, örnek dosya adlarının gerçek SHA-256 değerleri. Beklenen sonuçlar referans işlevle doğrulandı.
  - Görev 1–3'ün setup adımı `hazirla("ai-savunma-20")` çağırıyor. Veriler sentetik olarak etiketlendi ve kalıcı değil. Testler gizli ve ayrı verilerle sınıyor.
- **Kusurlu başlangıç kodları (4 görev):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Yalnız alan varlığını ve `int` türünü denetliyor | 4 bozuk politikayı kabul ediyor |
  | 2 | `elif` kullanıyor ve `>=` ile karşılaştırıyor | Sınıra eşit model karantinaya alınıyor; üç ihlalli kayıtta yalnız `kaynak` nedeni çıkıyor |
  | 3 | Özetleri ilk 12 karakterle karşılaştırıyor, `.lower()` ile normalleştiriyor, her risk için ayrı neden ekliyor | `ozet-modeli-ayna` kabul ediliyor, `["risk","risk"]` çıkıyor, 3 bozuk kayıt kabul ediliyor |
  | Gerçek deney | Şema yok, imza denetimi yok, 12 karakterlik önekle karşılaştırma | Çalıştır'da imzasız gerçek katmanlar `kabul` alıyor |

  **Düzeltme notu:** İlk yazdığım hâlde, gerçek deneyin başlangıç kodu yorumunda tahrif kopyasının 12 karakterlik önekle kaçırılacağı iddia ediliyordu. Gerçek dosyada tek bayt değişince özetin tamamı değiştiği için bu doğru değildi; Çalıştır'da da tahrif yakalandı. Kusur, gerçekten görünen "imza denetimi yok" hatasına çevrildi. Anlatıma, son karakter farkının abartılmış bir öğretim örneği olduğu ve 48 bitlik kısa önekin neden tehlikeli olduğu eklendi.
- **Anlatım:** 5 anlatım bloğu toplam 1066 kelime oldu. Eklenen konular:
  - AI bileşenlerine özgü riskler: pickle ile kod çalıştırma, ağırlıktaki arka kapı, typosquatting.
  - Bütünlük, imza ve risk taramasının üç ayrı soru olduğu.
  - SHA-256'nın nasıl çalıştığı ve beklenen özetin nereden geldiği (`--require-hashes`, OCI içerik adresleme).
  - Saldırgan bakışı: önbellek, kapatılmış CI adımı, `latest` etiketi.
  - Savunucu tarafı ve sık yapılan hatalar.
  - Gerçek deneyin 5 adımı ve bu makinede ölçülen sonuç.
- **Gerçek deney modülü (`sandbox/ai_gercek_ai_savunma_20.py`) baştan yazıldı:**
  - **Eski hâli:** `/api/tags` listesinden okunan digest, hem "beklenen" hem "gerçek" alana yazılıyordu. Hiçbir özet hesaplanmıyordu. Ayrıca bu değer ağırlık dosyasının değil, manifest katmanının özetiydi.
  - **Yeni hâli:** Kurulu sohbet modelinin manifest dosyası (`OLLAMA_MODELS` ya da `~/.ollama/models`) salt okunur açılıyor. Beklenen özetler manifest'ten geliyor. Her katmanın blob dosyasının SHA-256 değeri gerçekten hesaplanıyor; 2,4 GB'lık ağırlık dosyası da dahil.
  - **Tahrif senaryosu:** En küçük katmanın geçici bir kopyası alınıyor, son baytı XOR ile değiştiriliyor ve yeniden özetleniyor. Kopya hemen siliniyor. Kullanıcı dosyalarına hiç yazılmıyor.
  - **İmza:** Manifest'te imza bilgisi olmadığı için `imzali=False` dürüstçe yazılıyor. Bu yüzden imza zorunlu politika her katmana `imza` nedeni ekliyor; bu gerçek bir bulgu.
  - **Risk:** Zafiyet taraması yapılmıyor. Boş `riskler` listesi kanıtta "tarama yapılmadı" diye işaretleniyor.
  - **Kanıt içeriği:** Her katmanın manifest özeti, hesaplanan özeti, boyutu ve hesaplama süresi kanıta yazılıyor.
  - Sohbet çağrısı yok; model belleğe yüklenmiyor. Testin kullandığı `surum_guvenlik_raporu_referans` eklendi.
- **Kopya koruması:**
  - Test `kod_denetimi(src, yasak=("surum_guvenlik_raporu_referans", "kanit_yaz"))` çağırıyor. Eskiden `("referans", "getattr")` kullanılıyordu ve ihlalde test durmuyordu.
  - AST kontrolü şunları yakalıyor: yasak isimlerin ya da `*` ile içe aktarımı, `inspect`/`importlib`/`runpy`, `exec`/`eval`/`compile`/`__builtins__`.
  - İhlalde `stop()` çağrılıyor.
- **Gerçek deney testi:**
  - Sözleşmeye yeni vakalar eklendi: son karakteri farklı özet; imza + bütünlük + risk birlikte (risk bir kez); tür/kaynak/boyut sırası; 63 karakterlik özet; `1` ve `True` gibi bool olmayan değerler; yinelenen kimlik.
  - Eski "pinli kayıt kabul edilmeli" kontrolü kaldırıldı, çünkü pinli kayıt artık gerçek veriyle hep `imza` nedeni alıyor. Yerine şu kontroller geldi:
    - ağırlık dahil gerçek katmanların özeti hesaplanmış olmalı
    - tahrif kopyası `butunluk` almalı
    - rapor, referans işlevin sonucuyla birebir aynı olmalı
  - Diskteki bir katman gerçekten bozuksa doğru rapor onu da işaretler; testin geçmesi diskin sağlam olmasına bağlı değil.
  - Kanıt yalnız `kabul=all(sonuclar)` ile yazılıyor.
- Ortak `sandbox/ai_gercek_lab.py`, `engine/` ve `web/` değiştirilmedi.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

| Kontrol | Komut | Sonuç |
|---|---|---|
| validate | `tools/validate.py ai-savunma-20` (PAFTA_DATA=`<scratchpad>/s20-kabul`) | **TEMİZ**, 9 kontrol. Başlangıç kodu düzeltmesinden sonra yeniden çalıştırıldı. |
| tahmin | `docs/denetim/araclar/tahmin.py . ai-savunma-20` | 1 tahmin, **0 şüpheli** |
| mutasyon | `kirp_gercek.py <scratchpad>/s20-mutasyon` ve ardından `mutasyon.py --en-cok 1000 ai-savunma-20` | 6 + 12 + 14 = 32 mutant, **0 geçen**. Sonraki değişiklikler yalnız başlangıç kodu ve anlatımdaydı; çözümler ve testler değişmedi. Kopya klasörü silindi. |
| kopya sondası | `kopya_sonda.py ai-savunma ai-savunma-20 ...` | 6/6 **fail → korunuyor**, hiç kanıt yazılmadı |

Kopya sondasında denenen 6 yol: takma adla içe aktarım, öznitelik erişimi, `getattr`, `inspect` + `exec`, `*` ile içe aktarım, `importlib` + `__dict__`.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/s20-kabul/ai-kanit/savunma-tedarik-1793379081839.json` (kabul: true)
- **Model:** `qwen3:4b-instruct-2507-q4_K_M`
- **Katman özetleri:** 6 katmanın 6'sı manifest'le eşleşti (ağırlık, şablon, lisans, parametre, manifest, config). Ağırlık dosyası 2382 MB; SHA-256 `85e4a5b7b8ef…` yaklaşık 2,2 saniyede hesaplandı. `/api/tags` digest'i katmanlar arasında bulundu.
- **Tahrif:** `parametre-tahrif` kopyasının özeti `548eefe6b6ca…` çıktı; karar `karantina`, nedenler `["imza", "butunluk"]`.
- **Gerçek katmanların kararı:** Hepsi `["imza"]` nedeniyle karantinada.
- **Çalıştır (CLI runner `run`):**
  - Çözüm `ok` döndü.
  - Kusurlu başlangıç kodu imzasız katmanlara `kabul` verdi; kusur görünür hâlde.
- **Görev 1–3:** Başlangıç kodu ve çözüm görünür veriyle elle çalıştırıldı. Başlangıç kodları yukarıdaki tablodaki kusurları gösterdi. Çözümler bozuk kayıtları reddetti ve beklenen kararları verdi.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.** Kontrol, Çalıştır ve dosya erişimi yalnız CLI ve runner üzerinden doğrulandı.
- Deney yalnız `registry.ollama.ai/library/<ad>:<etiket>` biçimindeki modelleri destekliyor. Başka ad alanındaki modellerde deney açık bir mesajla `GercekLabYok` veriyor; deney yapılmadan geçme yok.
- Cosign ve Trivy çalıştırılmadı.
- Kurulum, indirme, commit/push ve puan yazımı yapılmadı. Ollama sunucusuna ve model dosyalarına yazılmadı; dosyalar yalnız okundu.
