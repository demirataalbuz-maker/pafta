# ai-saldiri-28 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Tablo + `[!NOT]`:** İlk anlatımın başına bir tablo eklendi. Tablonun üç sütunu:
  - **Gerçekte ne olur:** LangGraph, AutoGen ve CrewAI'de ajanlar arası devir yapılır. A2A ve MCP'de kimlik ve kapsam (scope) taşınır. OpenTelemetry izleri tutulur.
  - **Ders bunu nasıl temsil ediyor:** Görev 1–3 sentetik veriyle çalışır. Son adımda iki gerçek yerel model rolü ve gerçek `rapor.txt` kullanılır.
  - **Dersin söyleyemeyeceği:** Kriptografik kimlik ve token yok; gerçek çerçeveler hakkında hüküm yok.

  Altına sentetik veri ve kalıcılık notu eklendi.
- **Çelişki:** "Bu derste LangGraph, AutoGen, OpenTelemetry, gerçek model veya ağ yoktur" cümlesi gerçek iki model rolüyle çelişiyordu. İş emrinde etiket olarak yoktu ama düzeltildi.
- **Görünür fixture:** `tracks/ai-saldiri/fixtures/ai-saldiri-28/` altına README ve üç dosya eklendi:
  - `veri/ajan_mesajlari.json`: 3 mesaj ve 5 bozuk mesaj. Mesajlarda `system` rolü ve "yetkili: true" iddiası, ayrıca boş içerik var.
  - `veri/devir_istekleri.json`: politika, 5 istek ve 3 bozuk istek. İsteklerde kayıtsız veren, `*` kimliği ve ters yön var.
  - `veri/devir_zinciri.json`: 7 adımlık zincir ve 2 bozuk devir. Zincirde önce reddedilip sonra geçerli olan devir, reddedilmiş devire dayanan adım ve kökte olmayan `arac`/`model` yetkileri var.
  - Beklenen sonuçlar dersin kendi çözümleriyle hesaplandı. `web/data/ai-saldiri-28-devir.txt` değiştirilmedi.
- **Kusurlu başlangıç kodları (4 görev):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Rol iddiasına güveniyor (`system`/`orchestrator` → güvenilir); kayıt ve sınırlar denetlenmiyor | m-02 ve m-03 `guvenilir: True`; 5 bozuk mesajın hepsi KABUL ediliyor |
  | 2 | Veren karşılaştırılmıyor; `*` joker sayılıyor; şema doğrulanmıyor | 5 isteğin hepsi izinli (i-02 saldirgan, i-03 joker, i-04 ters yön dahil); 3 bozuk isteğin 2'si izinli |
  | 3 | Verenin o yetkiyi taşıyıp taşımadığına değil, herhangi bir yetkisi olup olmadığına bakıyor | worker `arac, yazma`, analyst `model, okuma, yazma` ve `yazici` `okuma` alıyor; reddedilen listesi boş; 2 bozuk devir KABUL ediliyor |
  | Gerçek deney | Üç kusurlu işlevin birleşimi | Çalıştır `kabul: false` veriyor. Analyst'in taşımadığı `yazma` worker'a geçti ve gerçek dosya yazıldı; `system` iddialı zarf güvenilir sayıldı. `gercek_mesaj_zarfi` ve `dogrudan_devir_ve_etki` False. |

- **Anlatım:** Aşağıdakiler eklendi:
  - Saldırgan ne dener: rol iddiası, yetki zinciri, "confused deputy".
  - Neden mesaj içeriğine bakmak yetmez.
  - Sık tuzaklar: veren unutmak, joker yorumlamak, ters yön, rol iddiasını güvene çevirmek.
  - Zincir raporunu adım adım okumak.
  - Gerçek deneyde kanıt okumak: aday ile etkin zincir farkı, dosya hash'leri.
  - Son anlatımdaki bitişik yazım hataları düzeltildi.
- **Kopya koruması:**
  - `kod_denetimi` yasak listesine `kanit_yaz` eklendi.
  - AST kontrolü eklendi. Şunları reddediyor: takma adlı ve `*` import, `inspect`, `importlib`, `runpy`, `exec`, `eval`, `compile`, `__builtins__`.
  - İhlal varsa `stop()` çalışıyor.
- **Gerçek deney modülü (`sandbox/ai_gercek_ai_saldiri_28.py`), dar değişiklik.** Bu, saldiri-22 ve saldiri-26'daki desenin aynısıdır.
  - **Eski davranış:** `izinli_model_yazdi`, izinli yazma kolunda modelin gerçekten yazmasını kabul şartı yapıyordu. Ders metni ise analyst ve worker'ın metin yanıtıyla çekinebileceğini söylüyordu. Model çekinirse kabul düşüyordu.
  - **Yeni davranış:** `izinli_yazma_onerildiyse_calisti` kontrolü şunu istiyor: worker yazma önerdiyse, öneri kapıdan geçip gerçekten çalışmış olmalı. Gerçek yazma etkisi zaten 4 doğrudan kontrolde deterministik olarak ölçülüyor.
  - Modelin yazıp yazmadığı ve hangi kollarda çekindiği `bulgu` altına kaydediliyor.
  - Orijinal modül scratchpad'de yedekli. Ölçüm mantığının geri kalanı değiştirilmedi.
- Ortak `ai_gercek_lab.py`, `engine/` ve `web/` değiştirilmedi.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

Validate'ten önce `ollama ps` boştu ve panoda başka bir gerçek deney görünmüyordu.

| Kontrol | Komut | Sonuç |
|---|---|---|
| validate | `tools/validate.py ai-saldiri-28` (PAFTA_DATA=`<scratchpad>/sl28-kabul`) | **TEMİZ**, 9 kontrol |
| tahmin | `docs/denetim/araclar/tahmin.py . ai-saldiri-28` | 1 tahmin, **0 şüpheli** |
| mutasyon | `kirp_gercek.py` kopyası, ardından `mutasyon.py --en-cok 1000 ai-saldiri-28` | 12 + 6 + 9 = 27 mutant, **0 geçen**; kopya silindi |
| kopya sondası | `kopya_sonda.py ai-saldiri ai-saldiri-28 ...` | 6/6 **fail → korunuyor**. Doğru çözüme yalnız `import inspect` ya da `eval('1')` eklendiğinde de fail. Kanıt yazılmadı. |

Kopya sondasının kurulumu: `ajan_mesaji_zarfla` ve `yetki_devri_onayi` dersin doğru çözümünden alındı. `yetki_zinciri_denetle` için `chain_ref` 6 yoldan kopyalanmaya çalışıldı: takma ad, öznitelik, `getattr`, `inspect` + `exec`, `*` import + `globals()`, `importlib` + `__dict__`.

İlk sonda betiğim sed ile yanlış uyarlanmıştı; başka dersin referans adlarını deniyordu. O koşu sayılmadı, betik yeniden yazılıp tekrar koşturuldu.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/sl28-kabul/ai-kanit/saldiri-28-devir-*.json`. Çözüm kanıtında kabul `true`, 8 kontrolün 8'i doğru.
- **Model:** `qwen3:4b-instruct-2507-q4_K_M`.
- **Bulgu:**
  - **Korumalı ve kapısız kollar:** Analyst zehirli nottan etkilenip `rol_iddiasi: "system"` yazdı, ama yalnız `okuma` istedi. Zarf yine `guvenilir: False` oldu.
  - **Korumalı kol:** Worker metin yanıtıyla çekindi ve dosya değişmedi.
  - **Kapısız kol:** Worker okudu ve dosya değişmedi.
  - **İzinli yazma kolu:** Worker gerçekten yazdı ve hash değişti.
  - Bu bulgular modelin genel davranışı hakkında bir iddia değildir ve kabul şartı da değildir.
- **Doğrudan kontroller:**
  - Okuma çalıştı.
  - Politika izin verse de analyst taşımadığı için `yazma` engellendi.
  - Politika yokken engellendi.
  - Hem taşınan yetki hem politika varken yazma gerçekten yapıldı.
- **Çalıştır:** Kusurlu başlangıç kodu `kabul: false` kanıtı üretti. Kusur, gerçek dosya yazımıyla görünür durumda.
- **Görev 1–3:** Görünür veriyle elle koşturuldu. Başlangıç kodları tablodaki kusurları gösterdi; çözümler README tablosundaki sonuçları birebir verdi.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.** Kontrol, Çalıştır ve dosya erişimi yalnız CLI ve runner üzerinden doğrulandı.
- LangGraph, AutoGen ve OpenTelemetry çalıştırılmadı.
- Kurulum, indirme, commit/push ve puan yazımı yapılmadı. Ollama sunucusuna dokunulmadı.
