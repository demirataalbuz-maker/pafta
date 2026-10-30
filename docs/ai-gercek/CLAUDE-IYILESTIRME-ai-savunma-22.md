# ai-savunma-22 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Çelişki:** İlk anlatımdaki "Bu derste OpenTelemetry veya SigNoz çalıştırılmaz; ağa veya modele erişilmez" cümlesi kaldırıldı. Yeni metin: görev 1–3 sentetik veriyle çalışır; son adım kurulu Ollama modelini araç çağrısıyla gerçekten çalıştırır. OpenTelemetry ve SigNoz çalıştırılmaz.
- **Tablo + `[!NOT]`:** İlk anlatımın başına bir tablo eklendi. Tablo OpenTelemetry'deki span, `trace_id` ve `gen_ai.*` özniteliklerini ve SigNoz/Jaeger görünümünü, dersin bunları nasıl temsil ettiğini ve neyi söyleyemeyeceğini gösterir. Yanına sentetik veri ve kalıcılık notu kondu.
- **Görünür fixture:** `tracks/ai-savunma/fixtures/ai-savunma-22/` altına README ve iki dosya eklendi.
  - `veri/telemetri_politikasi.json`: asıl politika ve 4 bozuk politika (isteğe bağlı iz, 0 olay, 600000 ms, bool sınır).
  - `veri/otel_olaylari.json`: üç iz, karışık sırada:
    - `iz-7f3a` tam bir zincirdir.
    - `iz-91bc` üç sorun taşır: guardrail yeniden denenmiştir, aynı zamanda iki olay vardır (dosyada `b` önce gelir), süre 6,3 sn'dir ve istek ortasında model sürümü q4'ten q8'e geçer.
    - `iz-c044` model araç çağırdığını söylediği hâlde `arac` olayı içermez.
  - Dosyada ayrıca 4 bozuk olay var: bool zaman, boşluklu sürüm, TAB içeren detay, `log` türü.
  - Beklenen rapor referansla doğrulandı. Görev 1–3'ün setup adımı `hazirla("ai-savunma-22")` çağırır. Veriler sentetik etiketli ve kalıcı değil; testler gizli ve ayrı verilerle sınar.
- **Kusurlu başlangıç kodları (4 görev):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | bool'u int sayıyor, aralık ve bayrak denetimi yok | 4 bozuk politika kabul ediliyor |
  | 2 | Yalnız zamana göre sıralıyor, şema denetimi yok | `t2-guard-b` `a`'nın önünde kalıyor, 4 bozuk olay kabul ediliyor |
  | 3 | Eksik türü görmüyor, süreyi ilk ve son **gelen** olaydan hesaplıyor, sürüm denetimi yok | `iz-7f3a` −805 ms çıkıyor, `iz-c044` `tam` sayılıyor, `surum` nedeni eksik |
  | Gerçek deney | Eksik türü görmüyor | Çalıştır'da guardrail ve araç olayı olmayan gerçek iz `tam` çıkıyor |

- **Anlatım:** 5 anlatım bloğu toplam 996 kelime oldu. Eklenen konular:
  - korelasyonun neden bir güvenlik kontrolü olduğu
  - görünür verideki her izin gerçek hayattaki anlamı (canary dağıtımı, loglanmamış araç)
  - saldırgan bakışı: guardrail'i atlatınca olayın oluşmaması, log hattının tıkanması, detaya ham prompt yazılması
  - sık tuzaklar: geliş sırası, eksik tür, boş iz, süre hesabı
  - gerçek deneyin 5 adımı ve sınırları
  - bu makinede ölçülen sonuç
- **Gerçek deney modülü (`sandbox/ai_gercek_ai_savunma_22.py`, yalnız bu derse ait):**
  - **Araç artık gerçekten çalışıyor.** Eskiden `ARACLAR` tanımlıydı ama hiç çağrılmıyordu; araç olayı yalnız modelin araç adını söylemesinden üretiliyordu. Şimdi `topla`, modelin verdiği argümanlarla çalıştırılıyor ve sonuç (ya da hata türü) araç olayına yazılıyor.
  - Model ne metin ne araç çağrısı döndürürse `GercekLabYok` hatası veriliyor.
  - Kanıta yazılanlar: ham araç çağrıları, model yanıtı (600 karakter), bütün olaylar ve ayarlar. Ayarlara guardrail kuralının tanımı ve eksik izin nasıl kurulduğu da dahil.
  - Çalıştır çıktısı artık ham araç çağrısını da gösteriyor.
  - Testin kullandığı `korelasyonlu_iz_raporu_referans` eklendi.
- **Kopya koruması:**
  - Test, `kod_denetimi(src, yasak=("korelasyonlu_iz_raporu_referans", "kanit_yaz"))` çağırıyor. Eskiden yasak listesi `("referans", "getattr")` idi ve ihlalde test durmuyordu.
  - Ek AST kontrolü şunları yakalıyor: yasak isim importu, `*` importu, `inspect`/`importlib`/`runpy`, `exec`/`eval`/`compile`/`__builtins__`.
  - İhlal bulunursa test `stop()` ile duruyor.
- **Gerçek deney testi:**
  - Sözleşmeye eklenen vakalar: ters sıra, `yinelenen`+`sure`+`surum` birlikte, süre sınırına eşitlik, bool zaman, boşluklu detay, yinelenen kimlik, olay sınırı aşımı.
  - **Bilerek yapılan değişiklik:** Eski `cagrilan == "topla"` ve `tam_karar == "tam"` kontrolleri kaldırıldı. Bu kontroller, modelin aracı çağırmasını kabul koşulu yapıyordu. Rehber §6'ya göre model davranışı kabul koşulu olamaz.
  - Yerine gelen kontroller:
    - Rapor, referans hesapla birebir aynı olmalı.
    - Eksik iz `eksik` nedeni almalı.
    - Model aracı çağırdıysa araç hatasız çalışmış olmalı.

    Model aracı çağırmazsa doğru rapor gerçek izi de `eksik` sayar ve test yine geçer. Doğru bir çözüm için testin sıkılığı azalmadı; referans karşılaştırması eskisinden daha sıkı.
  - Kanıt yalnız `kabul=all(sonuclar)` ile yazılıyor.
- Ortak `sandbox/ai_gercek_lab.py`, `engine/` ve `web/` değiştirilmedi.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

| Kontrol | Komut | Sonuç |
|---|---|---|
| validate | `tools/validate.py ai-savunma-22` (PAFTA_DATA=`<scratchpad>/s22-kabul`) | **TEMİZ**, 9 kontrol. Fixture sırası ve anlatım düzeltmesinden sonra yeniden koşturuldu. |
| tahmin | `docs/denetim/araclar/tahmin.py . ai-savunma-22` | 1 tahmin, **0 şüpheli** |
| mutasyon | `kirp_gercek.py` ile kopya alınıp `mutasyon.py --en-cok 1000 ai-savunma-22` | 8 + 17 + 24 = 49 mutant, **0 geçen**. Sonraki değişiklikler yalnız fixture ve anlatımdaydı. Kopya silindi. |
| kopya sondası | `kopya_sonda.py ai-savunma ai-savunma-22 ...` | 6/6 **fail → korunuyor**, hiç kanıt yazılmadı |

Kopya sondasında denenen 6 yol: takma ad, öznitelik, `getattr`, `inspect`+`exec`, `*` importu, `importlib`+`__dict__`.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/s22-kabul/ai-kanit/savunma-telemetri-*.json` (kabul true)
- **Model:** `qwen3:4b-instruct-2507-q4_K_M`
- **Araç çağrısı:** Model `topla(a=5, b=3)` çağırdı. Araç gerçekten çalıştı ve 8.0 döndürdü. Model yanıtı 26 token, koşudan koşuya 6–9 sn sürdü.
- **Rapor:**
  - Gerçek iz (`z-tam`): `tam`
  - Eksik iz (`z-eksik`): `hatali`, neden `["eksik"]`
- **Çalıştır (CLI runner `run`):** Kusurlu başlangıç kodu `ok` döndü ama eksik izi de `tam` saydı; kusur görünür hâlde.
- **Görev 1–3, görünür veriyle elle koşturuldu:**
  - Başlangıç kodları yukarıdaki tablodaki kusurları gösterdi.
  - Çözümler bozuk kayıtları reddetti, eşit zamanlı olayları kimliğe göre sıraladı ve 3 izi doğru raporladı (910 ms `tam`; `yinelenen`/`sure`/`surum`; `eksik`).

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.** Kontrol, Çalıştır ve dosya erişimi yalnız CLI ve runner üzerinden doğrulandı.
- Guardrail olayı küçük bir alt dize kontrolünden geliyor; gerçek bir guardrail servisi değil. Bu, anlatımda ve kanıtın ayarlar alanında açıkça yazılı.
- OpenTelemetry ve SigNoz çalıştırılmadı.
- Kurulum, indirme, commit/push ve puan yazımı yapılmadı. Ollama sunucusuna dokunulmadı.
