# ai-savunma-21 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Çelişki:** İlk anlatımdaki "Bu derste MLflow veya Git çalıştırılmaz; ağa, modele veya depoya erişilmez" cümlesi kaldırıldı. Yeni metin: görev 1–3 sentetik veriyle çalışır; son adımda prompt özetleri gerçekten hesaplanır ve yerel Ollama modeli gerçekten çalıştırılır. MLflow ve Git çalıştırılmaz.
- **Tablo + `[!NOT]`:** İlk anlatımın başına bir tablo eklendi. Tablo, MLflow Model Registry, Git PR akışı ve dal koruma kurallarının ne yaptığını, dersin bunları nasıl temsil ettiğini ve neyi söyleyemeyeceğini gösteriyor. Yanına sentetik veri ve kalıcılık notu eklendi.
- **Görünür fixture:** `tracks/ai-savunma/fixtures/ai-savunma-21/` altına bir README ve iki veri dosyası eklendi:
  - `veri/registry_politikasi.json`: asıl politika ve 4 bozuk politika (0 onay, isteğe bağlı geri alma, `agent` türü, bool onay).
  - `veri/degisiklik_kayitlari.json`, üç bölüm:
    - Görev 2 için 5 kayıt: temiz değişiklik, sahibin kendi onayı, izinsiz tür, eşit geri alma sürümü, içerik değişmeyen sürüm artışı.
    - Görev 3 için 3 kayıt: normal ilerleme, aktif sürümün tekrar yayımlanması, ilk sürüm (geri alma hedefi yok).
    - 4 bozuk kayıt: yinelenen onaycı, büyük harfli özet, bool sürüm, ASCII dışı sahip.

  Özetler örnek metinlerin gerçek SHA-256 değerleridir. Beklenen kararlar referansla doğrulandı. Görev 1–3'ün setup adımı `hazirla("ai-savunma-21")` çağırıyor. Veri sentetik olarak etiketli ve kalıcı değil; testler gizli ve ayrı verilerle sınıyor.
- **Kusurlu başlangıç kodları (4 görev):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Bayrakları, tür değerlerini, bool/0 onayı denetlemiyor | 4 bozuk politikanın hepsini kabul ediyor |
  | 2 | Sahibi de onaycı sayıyor; geri almada `>` kullanıyor; şema denetimi yok | `prompt-v4-sahip` ve `model-v7` "aday" çıkıyor, 4 bozuk kayıt kabul ediliyor |
  | 3 | Sürüm ilerlemesini denetlemiyor, nedenleri boş yazıyor, yayına eski özeti koyuyor | `model-v6-tekrar` yayına giriyor, `prompt-ilk` nedensiz kalıyor |
  | Gerçek deney | Özetleri hiç karşılaştırmıyor, sahibi de onaycı sayıyor | Çalıştır'da gerçek sahte sürüm (`r-sahte`) "aday" çıkıyor |

- **Anlatım:** 5 anlatım bloğu toplam 1025 kelime oldu. Eklenen konular:
  - Promptun neden sürümlenmesi gereken bir güvenlik bileşeni olduğu.
  - "Dört göz" ilkesi ve sahibin kendi değişikliğini onaylaması.
  - İlk sürümün geri alma hedefi olmaması ve fail-closed davranış.
  - Saldırgan bakışı: sahte sürüm, kendi onayı, aynı sürümü yeniden yayımlama, geri alma hedefini bozma.
  - Özetin anlamı değil baytları ölçtüğü.
  - Sık tuzaklar: string sürüm karşılaştırması, `>=` / `>` karışıklığı.
  - Gerçek deneyin 3 adımı ve bu makinede gözlenen sonuç.
- **Gerçek deney modülü (`sandbox/ai_gercek_ai_savunma_21.py`, yalnız bu derse ait):**
  - **Döngüsel kontrol kaldırıldı.** Eski `dagitilan_sha == sha_v2` kontrolü aynı sabit metnin özetini iki kez hesaplayıp karşılaştırıyordu. Her zaman doğru çıkıyor, hiçbir şey ölçmüyordu. Bu kontrol ve `deploy_registry_eslesme` alanı çıkarıldı.
  - Model artık yalnız v2 ile değil, **v1 ve v2 ile ayrı ayrı** aynı belgeyi özetliyor. İki ham yanıt ve özetleri kanıta yazılıyor. Model boş yanıt verirse `GercekLabYok` hatası atılıyor ve ayarlar kaydediliyor.
  - Üçüncü bir kayıt eklendi: `r-bosluk`. Bu kayıtta v1'in sonuna yalnız bir boşluk eklendi; özet değiştiği için kayıt "aday" olur. Amaç, özet kontrolünün anlamsız bir değişiklikle atlatılabildiğini göstermek.
  - Testin kullandığı `registry_degisiklikleri_denetle_referans` eklendi.
- **Kopya koruması:**
  - Test `kod_denetimi(src, yasak=("registry_degisiklikleri_denetle_referans", "kanit_yaz"))` çağırıyor. Eski hâli `("referans", "getattr")` idi ve ihlalde test durmuyordu.
  - Ek AST kontrolü şunları reddediyor: yasaklı import ve `import *`, `inspect`/`importlib`/`runpy`, `exec`/`eval`/`compile`/`__builtins__`.
  - İhlal bulunursa `stop()` çağrılıyor.
- **Gerçek deney testi:**
  - Sözleşmeye eklenen vakalar:
    - sahibi içeren iki kişilik onay
    - eşit geri alma sürümü
    - dört nedenin birlikte çıktığı tam çıktı
    - bool sürüm, ASCII dışı sahip, yinelenen kimlik, 0 geri alma
  - Gerçek kayıtlardan çıkan rapor, referans hesapla birebir karşılaştırılıyor.
  - Eski `gercek_karar`/`sahte_karar` kontrolleri korundu.
  - Kanıt yalnız `kabul=all(sonuclar)` ile yazılıyor; kayıtlar ve ham yanıtlar kanıta ekleniyor.
- Ortak `sandbox/ai_gercek_lab.py`, `engine/` ve `web/` değiştirilmedi.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

| Kontrol | Komut | Sonuç |
|---|---|---|
| validate | `tools/validate.py ai-savunma-21` (PAFTA_DATA=`<scratchpad>/s21-kabul`) | **TEMİZ**, 9 kontrol |
| tahmin | `docs/denetim/araclar/tahmin.py . ai-savunma-21` | 1 tahmin, **0 şüpheli** |
| mutasyon | `kirp_gercek.py` ile kopya, ardından `mutasyon.py --en-cok 1000 ai-savunma-21` | 6 + 17 + 19 = 42 mutant, **0 geçen**; kopya silindi |
| kopya sondası | `kopya_sonda.py ai-savunma ai-savunma-21 ...` | 6/6 **fail → korunuyor**, kanıt yazılmadı |

Kopya sondasında denenen 6 yol: takma adla import, öznitelik erişimi, `getattr`, `inspect` + `exec`, `import *`, `importlib` + `__dict__`.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/s21-kabul/ai-kanit/savunma-registry-*.json`, kabul `true`.
- **Model:** `qwen3:4b-instruct-2507-q4_K_M`, sıcaklık 0, tohum 5.
- **Özetler:** v1 = `2cd0378eed63…`, v2 = `774bab18eb84…`, v1 + boşluk = `91a7cdf964ae…`.
- **Model yanıtları:** v1 ve v2 aynı belgeyi farklı cümlelerle ama aynı anlamda özetledi.
- **Kararlar:**

  | Kayıt | Karar |
  |---|---|
  | `r-gercek` | aday |
  | `r-sahte` | karantina, neden `ozet` |
  | `r-bosluk` | aday |

- **Çalıştır (CLI runner `run`):** Kusurlu başlangıç kodu `ok` döndü ve üç kaydın üçüne de "aday" dedi; kusur görünür hâlde.
- **Görev 1–3:** Başlangıç kodu ve çözüm görünür veriyle elle çalıştırıldı. Başlangıç kodları yukarıdaki tablodaki kusurları gösterdi. Çözümler bozuk kayıtları reddetti ve doğru kararları verdi:
  - Görev 2: `guardrail-v4` → `tur`, `model-v7` → `geri_alma`, `prompt-v4-sahip` → `onay`, `prompt-v5-noop` → `ozet`.
  - Görev 3: yalnız `prompt-v3` yayına girdi; `model-v6-tekrar` → `surum`, `prompt-ilk` → `geri_alma`.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.** Kontrol, Çalıştır ve dosya erişimi yalnız CLI ve runner üzerinden doğrulandı.
- MLflow ve Git çalıştırılmadı.
- Kurulum, indirme, commit/push ve puan yazımı yapılmadı. Ollama sunucusuna dokunulmadı.
