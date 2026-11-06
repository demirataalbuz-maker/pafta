# Görev: Yeni AI Dersleri (dalga 1)

**Veren:** claude-opus (denetçi) · **Tarih:** 2026-11-02 · **Kaynak:** `PUAN-ARTIRMA-PLANI.md` §5, `PAFTA-EKLEME-PLANI.md` §A2–A3.

Bu 11 ders, mevcut 46 saldırı + 31 savunma dersinde **hiç bulunmayan** (0 eşleşme) konuları kapatır. Kopya ders değildir; her biri yeni numara alır. "Sonra" işaretli konular (VLM pertürbasyon, dedektör atlatma, deepfake, watermark/C2PA, multimodal savunma, unlearning) bu dalgada **yok**.

## Herkes için kurallar (zorunlu)
1. **Ücretsiz ve yerel.** Ücretli SaaS / gerçek bulut hesabı yok. Ücretsiz-ama-kısıtlı (Splunk Free, değerlendirme ISO, model lisansı) açıkça işaretlenir. Bkz. `pafta-ucretsiz-hedef`.
2. **Terimler çevrilmez.** Yalnız anlatım Türkçe. "membership inference", "rug pull", "circuit breaker" terim olarak kalır; "Toplam Varyasyon Uzaklığı" gibi çeviri YAPMA. Bkz. `YENI-AJAN-REHBERI.md` §10.
3. **Doğrulanmamış teknik iddia yazma.** Yanlış atıf, ters çevrilmiş metrik, uydurma sayı, sandbox'ın sabit seçimini genel gerçek gibi sunma = iade sebebi. Her sayısal/atıf iddiası ya kanıt dosyasından ya da adıyla bilinen kaynaktan gelmeli. (Rehber kural 12.)
4. **Format:** `::: anlat`, `::: tahmin`, `::: gorev`; son görev `::: gorev Gerçek deney` + `motor: ai-gercek`. En az **3 KUSURLU** başlangıç kodu. Testler mutasyona dayanıklı (tahmin 0, 3/3 mutant reddedilir, kopya sondası 4/4). `ai_lab.kod_denetimi(src, ...)` kopya koruması çağrılır; `exec` konu değilse `izin=()`.
5. **Kurulum gerektirenler** (Docker, torch dataset indirme, cosign binary, HarmBench/AgentDojo repo) → işe başlamadan panoya `uyari` yaz, kullanıcı onayı bekle. Kaynak/sürüm/boyut belirt.
6. Başlarken `ai_ders_takip.py al <slug> --kim <sen>`, bitince `durum <slug> denetime-hazir`. "bitti"yi yalnız denetçi yazar.

---

## SALDIRI (6 ders)

### ai-saldiri-47-mcp-rug-pull → **gemini**
Zaten güvenilen bir MCP sunucusunun sonradan araç tanımını/davranışını değiştirmesi (rug pull). saldiri-01 (güven modeli) ve saldiri-16 (tool-schema-poisoning) ile çakışmaz: buradaki konu **zamanla değişen güven** — ilk onaydan sonra sunucu araç şemasını sessizce değiştirir.
Yığın: yerel sahte MCP sunucusu + Ollama. Gerçek deney: aynı istemci ikinci çağrıda değişen şemaya uyuyor mu, kanıtla göster.

### ai-saldiri-48-egitim-verisi-cikarimi → **claude-yazar**
Membership inference + ezberlenmiş PII çıkarımı. Perplexity/logit farkıyla "bu örnek eğitimde var mıydı" ayrımı.
Yığın: torch + küçük model (GPT-2 small ya da küçük Qwen, yerelde). Atıf dikkat: Carlini vd. çalışmalarına doğru referans; metrik yönünü ters yazma.

### ai-saldiri-49-zararli-fine-tuning → **codex**
Küçük bir modele LoRA ile zararlı davranış enjekte etme ve güvenlik hizasını bozma (safety fine-tuning'i geri alma).
Yığın: torch + LoRA + küçük Qwen. Her şey yerel; indirilen model sürümü kanıt dosyasına yazılır.

### ai-saldiri-50-kendini-kopyalayan-istem → **gemini**
Ajanlar arası yayılan istem (bir ajanın çıktısı diğerinin girdisine kendini kopyalar — "AI worm" mantığı, yerelde).
Yığın: 2–3 yerel Ollama ajanı. Gerçek deney: kopyanın ikinci ajanda tetiklendiğini kanıtla göster.

### ai-saldiri-51-ml-altyapisi-cve → **codex**
ML altyapı servislerindeki gerçek CVE sınıfları (MLflow path traversal, Gradio dosya okuma, Jupyter token). Gerçek açık, izole eski sürümde.
Yığın: izole Docker, eski sürüm imaj — **kurulum onayı gerekir**, başlamadan panoya `uyari`. Lab internete kapalı, sıfırlanabilir.

### ai-saldiri-52-unicode-tag-kacakciligi → **gemini**
Unicode tag bloğu (U+E0000 aralığı) ile görünmez talimat kaçakçılığı. saldiri-13 (gizli-metin-belge-katmani) ile çakışmaz: burada konu **tag karakterleri**, görsel katman değil.
Yığın: saf Python + Ollama (modelin görünmez tag'e uyduğunu göster). Kurulum yok.

---

## SAVUNMA (5 ders) — DALGA 2'YE BEKLETİLDİ

> Güncelleme (03.11.2026): Ortak panodaki 12:17 ve 12:21 kullanıcı kararlarıyla dalga 2 claude-yazar için açıldı; 32/33 de ona devredildi. Önceki bekletme notu tarihsel karardır. Codex ve gemini için genel bir dalga 2 açılışı verilmiş değildir.

> Kullanıcı kararı (03.11.2026): şimdilik yalnız **saldırı** yürütülüyor. Aşağıdaki 5 savunma dersi (32–36) henüz başlatılmasın; saldırı dalgası bitince açılacak. Buradaki yazar atamaları dalga 2 içindir.



### ai-savunma-32-guardrail-egitme-distilbert → **claude-yazar**
Kendi prompt-injection sınıflandırıcını eğitme (DistilBERT + açık dataset), savunma-06/07'deki hazır guardrail'in aksine **kendi modelini eğit**.
Yığın: torch + açık dataset indirme — **onay gerekir**. Dataset adı/lisansı/boyutu panoya yazılır.

### ai-savunma-33-adversarial-training-circuit-breaker → **claude-yazar**
Adversarial training ve circuit breaker (representation rerouting) ile modeli sağlamlaştırma.
Yığın: torch, küçük model. Atıf: Zou vd. circuit breaker çalışmasına doğru referans.

### ai-savunma-34-injection-mimari-desenleri → **claude-yazar**
Mimari savunma desenleri: CaMeL, dual-LLM, spotlighting. savunma-03 (katmanlı mimari) kavramsal; bu ders **desenleri kodla kurar ve kıyaslar**.
Yığın: yerel Ollama. CaMeL (Google DeepMind) ve dual-LLM (Willison) atıfları doğru olmalı.

### ai-savunma-35-standart-benchmark-harmbench → **claude-yazar**
Standart güvenlik benchmark'larıyla ölçüm: HarmBench, AgentDojo, StrongREJECT. savunma-26 (tehdit-odaklı eval) ve savunma-27 (garak) ile çakışmaz: burada **dış standart setler**.
Yığın: açık setler + Ollama — repo indirme **onay gerekir**. Her benchmark'ın ne ölçtüğü doğru yazılmalı (karıştırma).

### ai-savunma-36-model-imzalama-cosign → **gemini**
Gerçek cosign/sigstore ile model imzalama ve doğrulama. savunma-20 cosign'ı yalnız anlatıyor, çalıştırmıyor — bu ders **gerçekten imzalar ve doğrular**.
Yığın: cosign binary — **kurulum onayı gerekir**, keyless akış yerelde. Başlamadan panoya `uyari`.

---

## Yeni anlatım teknikleri (bu dalgada uygulanacak)
Mevcut `anlat / tahmin / gorev` iskeleti kalır; üstüne şunlar eklenir:

1. **Tahmin → çalıştır → fark.** `::: tahmin` bloğundan sonra gerçek çıktı gösterilir ve öğrenciden tahminiyle gerçeğin **farkını kendi cümlesiyle** yazması istenir. Öğrenme tahminin tutmadığı yerde olur.
2. **Saldırı↔savunma köprüsü.** Her saldırı dersi başlığına `esleme:` ile ilgili savunma dersi, her savunma dersine ilgili saldırı yazılır (ör. 47 rug pull ↔ 36 imzalama/11 en-az-ayrıcalık). Öğrenci açığı gördüğü an kapatmayı da görür.
3. **Hata vitrini.** Gerçekte görülen **yanlış/yanıltıcı çıktıyı** olduğu gibi göster, "bu çıktı neden güven vermez?" diye sor. Örnek: guardrail "temiz" dedi ama atlatıldı; model imza doğruladı ama manifest'i saldırgan yazmış.
4. **KUSURLU kodu öğrenci teşhis etsin.** 3+ kusurlu başlangıç kodu kalır, ama her birinin kusuru doğrudan söylenmez; `::: tahmin` ile "hangisi neden güvensiz" sorulur, sonra çözümde açıklanır.
5. **Kanıt dosyasını okutma.** Gerçek deneyden çıkan kanıt dosyasını (seed, model sürümü, karar) öğrenciye **yorumlat**: "ikinci koşuda karar değişti mi, neden?". Gerçeklik 15. puanıyla da örtüşür.
6. **Sınır cümlesi.** Her dersin sonunda "bu ders neyi **gösteremez**" tek cümlesi zorunlu (abartı iddiayı engeller, kural 3'ün öğrenciye yansıması).

## Yazar dağılımı — AKTİF DALGA (yalnız saldırı, 03.11.2026)
Savunma dalga 2'ye bekletildiği için yazarlar saldırıda dengelendi:
- **codex:** ~~49 fine-tuning~~ ✅ **BİTTİ (denetim geçti)** · 51 ML CVE *(kurulum onaylandı ve tamamlandı; denetime hazır)*
- **claude-yazar:** 48 veri çıkarımı · 52 unicode tag kaçakçılığı
- **gemini:** 47 rug pull · 50 kendini kopyalayan istem — iddialar denetçide sıkı kontrol edilir.

**Güncel teslim notu (03.11.2026):** 49 ve 48 bağımsız denetimde kabul edildi. 51 kurulum onayı sonrası gerçek CLI/UI kabulüyle denetime teslim edildi; 52 de denetime hazır. Diğer derslerin anlık durumu tracker/panodan okunur.

## Dalga 2 (savunma) yazar dağılımı — beklemede
- **codex:** dalga 2 için aktif atama yok; 32 ve 33 kullanıcı kararıyla claude-yazar’a devredildi (ortak pano 03.11.2026 12:21).
- **claude-yazar:** 34 injection mimari, 33 adversarial training, 32 guardrail eğitme, 35 benchmark (sıra 34 → 33 → 32 → 35; ortak pano 03.11.2026 12:21).
- **gemini:** 36 cosign

Denetim: her teslim `tools/ai_iyilestirme.py` kuyruğuna; claude-opus denetler (validate TEMİZ, tahmin 0, 3/3 mutant, kopya 4/4, içerik okuması). Küçük düzeltme "claude-opus düzeltti" notuyla, büyük sorun iade.
