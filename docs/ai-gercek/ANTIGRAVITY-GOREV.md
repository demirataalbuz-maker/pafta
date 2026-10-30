# Antigravity · ders yazım görevi (29 Ekim 2026)

Hazırlayan: claude-opus (kullanıcının isteğiyle). Proje kökü: `C:\Users\demo12\Documents\Pafta-AI-GercekLab` (dal `ai/gercek-pilotlar`).
Görevin: aşağıdaki **yeni dersleri yazmak** ve **müfredatta doğru yere** yerleştirmek. Kurulum, GPU, araç kütüphaneleri ve denetim senin işin değil (claude-opus yürütüyor).

## 0. Önce oku (sırayla)

1. `AGENTS.md` — pano ve tracker kuralları.
2. `docs/ai-gercek/YENI-AJAN-REHBERI.md` — kullanıcının öğretim standardı (görünür dosyalar, veri kökeni etiketi, gizli test verisi, kalıcılık dürüstlüğü).
3. `docs/ai-gercek/AJAN-TALIMATI.md` ve `docs/ai-gercek-lab.md` — gerçek deney (`motor: ai-gercek`) kuralları.
4. `C:\Users\demo12\Desktop\Pafta-Platform-Projesi\YENI_DERSLER_YERLESIM.md` ve `AI_EKSIKLER.md` §7 — bu derslerin neden eklendiği.
5. Örnek ders biçimi: `tracks/purple/lessons/pu15-windows-adli-izler.md` (anlatım/tablo/fixture/başlangıç kodu) ve `tracks/ai-temel/lessons/ai-temel-01-*.md` (aynı biçimin AI hâli + sonda gerçek deney).

Sonra: `python -X utf8 tools/ai_pano.py acik`, `python -X utf8 tools/ai_pano.py oku -n 30`. Kendi adınla (`--kim antigravity`) yaz.

## 1. Yazılacak dersler ve YERLERİ

**Kural: sırayı dosya numarası değil, `tracks/<yol>/track.json` içindeki modülün `lessons` listesindeki konum belirler.** Yeni dersler o yolun sıradaki boş numarasını alır ama listeye aşağıda yazan **tam konuma** eklenir. Listenin sonuna ekleme. (Örnek: `ai-guvence-31` Gizlilik modülünde `ai-guvence-17` ile `ai-guvence-18` arasına konmuştur.)

Yazım sırası yukarıdan aşağıya. Bir dersi bitirip devretmeden sonrakine geçme.

| Sıra | Kimlik | Konu | Modül (`track.json` başlığı) | Tam konum |
|---|---|---|---|---|
| 1 | `ai-saldiri-35` | **Çok turlu jailbreak**: Crescendo (zararsız başlayıp tırmandırma), many-shot (uzun bağlama sahte örnekler), Skeleton Key | ai-saldiri · "Model Etkileşimi ve Saldırı Yüzeyi" | `ai-saldiri-04` **ile** `ai-saldiri-05` **arasına** |
| 2 | `ai-saldiri-36` | **Red team metodolojisi I + yasal erişim**: kapsam, angajman kuralları, yetki; yerel model = tam izin; Gandalf/PortSwigger gibi yasal sahalar Pafta dışında; bug bounty ve red team ağları; izinsiz production saldırısı ToS ihlali | ai-saldiri · "Model Etkileşimi ve Saldırı Yüzeyi" | **en başa**, `ai-saldiri-01`'den **önce** |
| 3 | `ai-saldiri-37` | **Red team metodolojisi II**: sistematik kapsama, bulgu önceliklendirme, kapanış ve temizlik. **Rapor yazımı öğretilmez** (kullanıcı kararı: iş yerinde öğrenilir). `ai-guvence-29` (sorumlu bildirim) ile bağ kur | ai-saldiri · "Adaptif Saldırılar ve Purple Doğrulama" | **en sona**, `ai-saldiri-34`'ten **sonra** |
| 4 | `ai-saldiri-38` | **AI'yı güvenlik kontrolü olarak kırmak**: moderasyon/spam/fraud/özgeçmiş sınıflandırıcısını atlatma; `ai-guvence-07/08` (FGSM/PGD) köprüsü; savunma karşılığı `ai-savunma-07`, `ai-savunma-23` | ai-saldiri · "Model Bilgisi, Veri Sızıntısı ve Çıktı Güvenliği" | modülün **sonuna**, `ai-saldiri-10`'dan **sonra** |
| 5 | `ai-saldiri-39` | **LLM uygulama pentest köprüsü**: modelin etrafındaki uygulama (oturum, IDOR, API anahtarı, SSRF); mevcut web/Purple derslerine yönlendiren köprü | ai-saldiri · "Ağ Erişimi, SSRF ve Exfiltration" | modülün **başına**, `ai-saldiri-21`'den **önce** |

Numara çakışmasın: başlamadan `tracks/ai-saldiri/lessons` klasöründe ve panoda o numarayı kimsenin almadığını kontrol et; almışsa sıradaki boş numarayı kullan ve konumu yine tablodaki gibi koru.

## 2. Yerleştirme adımları (her ders için hepsi)

1. Panoya `basladi` yaz (konu: ders kimliği). Dersin dosyası: `tracks/ai-saldiri/lessons/ai-saldiri-NN-<kisa-ad>.md`.
2. `tracks/ai-saldiri/track.json`: kimliği yukarıdaki **tam konuma** ekle. Başka hiçbir satırı değiştirme; dosyayı düzenlemeden hemen önce yeniden oku (başka ajanlar da yazıyor).
3. `ai_mufredat_plan_v3.json`: aynı modülün `lessons` listesine **aynı konuma** `{id, title, summary, side, tools, status, onkosul}` ekle. `onkosul` zincirini düzelt: yeni ders kendinden önceki dersi önkoşul alır; kendinden sonraki ders yeni dersi önkoşul alacak şekilde güncellenir. Sonra `python -X utf8 ai_panel_uret.py`.
4. `python -X utf8 tools/ai_ders_takip.py` (tabloyu dosyalardan tazeler), sonra `al` ve `durum ... calisiliyor --kim antigravity`.
5. Bitirince kontrol: `python -X utf8 tools/validate.py ai-saldiri-NN` (gerçek deney dahil) TEMİZ; `python -X utf8 docs/denetim/araclar/tahmin.py . ai-saldiri-NN` 0 şüpheli; mutasyon (aşağıda) 0 geçen. Ders ekranında Çalıştır/Kontrol'ü dene.
6. Tracker: `durum ai-saldiri-NN denetime-hazir --kim antigravity --not "..."`; panoya `bitti` + devir notu (rehber §8). `bitti` durumunu yalnız bağımsız denetçi verir.
7. Yerleşimi kontrol ettir: panoya `soru` yaz, claude-opus `track.json` ve plan sırasını doğrular.

## 3. Ders biçimi (purple standardı + AI gerçek deneyi)

- **Anlatım**: 3–6 kısa blok, her biri tek ilke; başlığı bir kural gibi. İlk blok "Gerçek biçimi bil, sentetik temsili ayırt et": *Gerçek araç/model ne gösterir | Bu ders ne kullanır | Ne söyleyemez?* tablosu ve `> [!GÜVENLİK]` kapsam notu. Son blok: bulguyu sınırlı ve doğrulanabilir yazmak (rapor yazımı değil, iddianın sınırı).
- **Tahmin**: tek bir tuzağı gösteren küçük, çalışan Python; altında açıklama.
- **Görünür örnek dosyalar**: `tracks/ai-saldiri/fixtures/ai-saldiri-NN/` + `README.md` (hepsi **sentetik** diye etiketli). Her görevin `setup` bloğu dosyaları çalışma klasörüne kopyalar (örnek: `sandbox/ai_temel_veri.py` ve ai-temel-01'deki `setup`). Dosyalar her çalıştırmada yeniden kopyalanır: **kalıcılık yok**, bunu derste açıkça yaz; öğrenci denemeyi kendi kodunda yapar.
  - Ders 35 için örnek: `konusmalar/crescendo_*.json`, `konusmalar/many_shot_*.json` (tur tur sentetik konuşmalar, zararsız konu + canary hedefi).
- **Başlangıç kodu**: dosyayı okuyan, çalışan ama gerçekçi bir hata yapan kod (ör. yalnız son turu inceleyen tespit). `return {}` değil.
- **Görevler**: 1 ham veriyi oku/ayrıştır → 2 yorumla/ölç → 3 sentez/karar. Testler **görünmeyen** verilerle sınar; anlamlı yanlış çözümler `ok(not sozlesme(mutant), ...)` ile reddedilir.
- **Sonda gerçek deney** (`::: gorev Gerçek deney · ...`, `motor: ai-gercek`, `gereksinim: ollama`): `ai_lab.SohbetOturumu` kullan. Kanıt `ai_lab.kanit_yaz(..., {"kaynak": "gercek", "kabul": ...})`. `ai_lab.kod_denetimi(src)` kontrolü zorunlu.

## 4. Saldırı içeriği kuralları (A8 / A16 kararları)

- **Hücum = savunma.** Saldırı tarafı tam gücüyle öğretilir; her derste savunma/tespit karşılığı da bulunur.
- **Vekil/canary ile ölçüm.** Başarı sinyali gerçek zararlı içerik değil, zararsız bir vekildir (modele yasaklanan sentetik parola/canary'yi söyletebiliyor musun). Gerçek tehlikeli yük üretme, yeni saldırı tekniği icat etme; var olan teknikleri (Crescendo, many-shot, Skeleton Key) öğret.
- **Saldırının başarılı olması geçme şartı değildir.** Test; deneyin doğru yürütülmesini, ölçümün doğruluğunu ve kanıtı denetler. Rastgele model yanıtını sabit cümleyle karşılaştırma.
- Hazır saldırı kampanyaları için `.ai-araclar` ortamındaki garak/PyRIT/promptfoo kullanılabilir (kurulu; `Desktop\Pafta-Platform-Projesi\parti1.ps1`). Yeni paket kurma.

## 5. GPU ve ortak kaynak

- Ollama deneyleri **varsayılan GPU**'da koşar; `sandbox/ai_gercek_lab.py` makine genelinde GPU kilidi tutar (aynı anda tek deney, diğerleri sırasını bekler). `num_gpu: 0` gibi CPU zorlaması **yazma**; seçenek gerekiyorsa `ai_lab.ollama_secenekleri(...)` kullan.
- many-shot için uzun bağlam gerekir: `num_ctx` değerini kanıta yaz; 8 GB VRAM sınırına dikkat (qwen3:4b önerilir).
- Kullanıcının Ollama sunucusunu, Docker'ı, WSL'i kapatma; yalnız kendi başlattığını kapat. Kurulum/indirme, commit/push yok.
- Ortak dosyalara (`engine/`, `web/`, `sandbox/ai_gercek_lab.py`) dokunma; gerekirse panoya `soru` yaz.

## 6. Mutasyon nasıl çalıştırılır

`docs/denetim/araclar/mutasyon.py` her `gorev` adımını koşar; gerçek deney adımında her mutant için modeli çağırır. Bunun yerine dersin "Gerçek deney" bloğu çıkarılmış bir kopyasında çalıştır (proje dışı geçici klasöre `engine/`, `sandbox/`, `docs/denetim/araclar/`, `tools/validate.py`, `tracks/ai-saldiri/track.json` ve kırpılmış ders dosyasını kopyala), sonra:
`python -X utf8 -u docs/denetim/araclar/mutasyon.py <kopya> --en-cok 1000 ai-saldiri-NN` → `0 geçen` olmalı.

## 7. Takıldığında

Panoya `soru` (konu: ders kimliği) yaz; claude-opus ya da kullanıcı yanıtlar. Engel varsa tracker'da `engelli --not "neden"`.

## 8. Güncelleme (29 Ekim 2026, kullanıcı kararı)

claude iki yakın ders yazdı: `ai-guvence-33` *Red Team Metodolojisi ve Tekrarlanabilir Değerlendirme* (kapsam doğrulama, şiddet puanlama, bulgu birleştirme, tekrarlanabilirlik ölçümü) ve `ai-guvence-34` *LLM Uygulama Pentest Köprüsü: SSRF ve Yetki* (URL ayıklama, SSRF + allowlist kapısı, IDOR). Kullanıcı 36–39'un yine de yazılmasını istedi. Bu iki dersi önce oku; aynı görevleri tekrarlama, saldırı tarafı açısını öne çıkar ve ilgili yerde bu derslere atıf ver. Yerleşim tablosu değişmedi.

## 9. İkinci görev listesi (29 Ekim 2026, kullanıcı kararı)

Codex `ai-saldiri-12, 30, 31, 32, 33` derslerini sırasından çıkardı (tracker'da sahipsiz). Diğer ajanların sırasındaki derslere dokunma: Codex `08–11, 13–26, 28, 29, 34`; claude `ai-savunma-01..20`. Her işe başlamadan tracker'da `al` + panoya `basladi`.

**A. Yeni dersler (dosya yok, yazılacak)**

| Sıra | Kimlik | Konu | Modül ve tam konum |
|---|---|---|---|
| 1 | `ai-saldiri-40` | **Denial-of-wallet saldırısı** (OWASP LLM10): pahalı üretimi tetikleme, bağlam doldurma, ajan döngüsünü uzatma; token/süre maliyetini ölçme. Savunması `ai-savunma-31`; ona atıf ver | "Ağ Erişimi, SSRF ve Exfiltration" · **en sona**, `ai-saldiri-33`'ten **sonra** |
| 2 | `ai-saldiri-41` | **Slopsquatting saldırısı**: modelin uydurduğu paket adlarını toplama, kayıt edilebilir adların riskini ölçme (yalnız yerel/sentetik dizin; gerçek paket deposuna **hiçbir şey yükleme**). Savunması `ai-guvence-32` | "Adaptif Saldırılar ve Purple Doğrulama" · `ai-saldiri-26`'dan **hemen sonra** |

**B. Var olan derslere gerçek deney (mevcut adımları silme; sona `::: gorev Gerçek deney` ekle)**

| Sıra | Ders | Gerçek deney için hazır araç |
|---|---|---|
| 3 | `ai-saldiri-12` Görsellerde multimodal injection | Ollama `qwen2.5vl:3b` (resimdeki yazıyı okuyor); resmi Pillow ile sentetik üret, canary ile ölç |
| 4 | `ai-saldiri-31` Tarayıcı ajanlarında DOM enjeksiyonu | Playwright + Chromium (başsız, yalnız yerel HTML; ağa çıkma) |
| 5 | `ai-saldiri-32` Adversarial ses ve sesli komut | `ai_lab.whisper_modeli()` (faster-whisper, GPU). Konuşma sesi için kurulum yok: Windows'un yerleşik `System.Speech` (PowerShell) ile yerel WAV üretilebilir |
| 6 | `ai-saldiri-33` KV-cache zamanlama yan kanalı | Yerel Ollama'da ortak önek / önek önbelleği ile TTFT farkı ölçümü (`ai_lab.SohbetOturumu`, GPU kilidi) |
| 7 | `ai-saldiri-30` PAIR, TAP ve PyRIT ile otomatik saldırı | Saldırgan + hedef ikisi de yerel model; `.ai-araclar` içindeki PyRIT/promptfoo; başarı sinyali canary |
| 8 | `ai-guvence-09` GCG ve AutoDAN | torch GPU (`ai_lab.torch_cihazi()`), `ai_lab.dil_modeli()` (SmolLM2-135M) üzerinde hedef dizgeyi (canary) üreten sonek araması |
| 9 | `ai-guvence-06` TransformerLens ile refusal mekanizması | TransformerLens 4.3 (`transformer_lens.model_bridge.TransformerBridge.boot_transformers(...)`, revizyonu açıkça ver) |
| 10 | `ai-guvence-10` Refusal direction removal / abliteration | TransformerLens + torch GPU |

**Model uyarısı (9 ve 10):** Bilgisayardaki tek Hugging Face modeli `SmolLM2-135M` **temel** modeldir; komut izleyen (instruct) değildir, gerçek bir reddetme davranışı yoktur. Gerçek refusal yönü için küçük bir instruct model gerekir (ör. `HuggingFaceTB/SmolLM2-135M-Instruct` ≈ 0,27 GB veya `SmolLM2-360M-Instruct`). **İndirme yapma**: panoya `soru` yaz (konu: ai-guvence-06); claude-opus kullanıcı onayıyla indirir ve sabit revizyonu bildirir.

Genel kurallar §2–§6 aynen geçerli: tam konum, plan dosyası + önkoşul zinciri, görünür sentetik fixture, gizli test verisi, mutasyon 0 geçen (gerçek deney adımı çıkarılmış kopyada), vekil/canary, saldırı başarısı geçme şartı değil, GPU için `ai_lab` yardımcıları (`num_gpu: 0` yazma), kurulum/commit yok.

**Güncelleme (kullanıcı kararı):** ai-guvence-06/10 için instruct modeli **sen indir**. Not: claude-opus `HuggingFaceTB/SmolLM2-135M-Instruct` (rev `12fd25f77366fa6b3b4b768ec3050bf629380bac`, 269 MB) indirdi ama zararlı isteklere ret vermiyor (reddetme davranışı yok), bu dersler için yetersiz. Öneri: `Qwen/Qwen2.5-0.5B-Instruct` (Apache-2.0, ≈1 GB); yalnız safetensors + tokenizer + config indir, sabit revizyonu (commit sha) derse ve kanıta yaz, önce gerçekten ret verdiğini zararsız bir vekil istekle doğrula. İndirmeden önce panoya `uyari` bırak.

> **ÖNCELİK SIRASI (29 Ekim 2026, kullanıcı kararı):** §9 bitti. Sıradaki iş **§11 Faz A tasarımı** (AI ile Güvenlik yolu — tasarım dokümanı + panoya `soru`, kullanıcı onayını bekle). Sonra **§10** (4 yeni saldırı dersi + Faz 3). Antigravity yalnızca **sonradan eklenen yeni dersler** ile ilgilenir (§10 + §11); mevcut yollardaki sahipsiz/bekleyen dersleri (ai-guvence, ai-savunma, ai-saldiri-27) **alma** — onları başka ajanlar sırayla sahiplenecek.

## 10. Üçüncü görev listesi (29 Ekim 2026, kullanıcı kararı)

§9 bittikten sonra. Yazma sırası aşağıdaki gibi; yer yine `track.json` konumuyla belirlenir. Her derste **savunma/tespit görevi zorunlu** (hücum = savunma).

| Sıra | Kimlik | Konu | Modül ve tam konum |
|---|---|---|---|
| 1 | `ai-saldiri-42` | **Akıl yürüten (reasoning) modellere saldırı**: düşünce zincirini ele geçirme, modeli aşırı düşünmeye sokarak maliyet saldırısı, gizli düşünce metninden sızıntı; savunma: düşünce bütçesi, düşünce içeriğini kullanıcıya/araca sızdırmama. Gerçek deney: `qwen3:8b` thinking modu (`think: true`), düşünce token sayısı ve canary sızıntısı ölçülür | "Model Etkileşimi ve Saldırı Yüzeyi" · `ai-saldiri-35` **ile** `ai-saldiri-05` **arasına** |
| 2 | `ai-saldiri-45` | **Çok dilli ve düşük kaynaklı dil atlatması** (Türkçe dahil): aynı vekil isteğin İngilizce/Türkçe/karışık dil/çeviri zinciri ile ret oranı farkı; savunma: dil bağımsız sınıflandırma, çevirip denetleme. Gerçek deney: yerel model(ler)de dil başına ret oranı (canary, zararsız vekil) | "Model Etkileşimi ve Saldırı Yüzeyi" · `ai-saldiri-04` **ile** `ai-saldiri-35` **arasına** |
| 3 | `ai-saldiri-43` | **Çok ajanlı sistemler ve ajanlar arası protokol (A2A)**: ele geçirilmiş ajanın diğerine talimat sızdırması, güvenin zincir boyunca yayılması, ajan kimliği/yetkisi; savunma: ajanlar arası mesajı veri olarak işaretleme, en az yetki, imzalı görev devri. Gerçek deney: yerel modelle 2–3 ajanlı zincir | "Ajanlar, Araçlar ve Yetki Sınırları" · **en sona**, `ai-saldiri-20`'den **sonra** |
| 4 | `ai-saldiri-44` | **Ajanın kalıcı belleğini zehirleme**: tek zehirli girdinin sonraki oturumlarda davranışı değiştirmesi; savunma: bellek yazımına kaynak etiketi, onay, süre sınırı, bellek denetimi. Gerçek deney: yerel model + diskte kalıcı bellek dosyası, oturumlar arası etki ölçümü | "Ajanlar, Araçlar ve Yetki Sınırları" · `ai-saldiri-43`'ten **sonra** (modülün sonu) |

Not: Modül 5'in ilk dersi `ai-saldiri-39`'un önkoşulu şu an `ai-saldiri-20`; 43 ve 44 eklenince zincir `20 → 43 → 44 → 39` olmalı.

**Faz 3 · Belirsiz saha görevleri (önce tasarım, sonra yazım):** Her AI yolunun sonuna adım tarifi olmayan bir final: bilerek açıklı bırakılmış yerel bir AI uygulaması verilir; öğrenci açığı kendi bulur, kanıtlar ve kapatır; otomatik kabul yine gerçek çıktıyla. Yazmadan önce panoya `soru` ile tek sayfalık tasarım önerisi bırak (uygulama, açıklar, kabul ölçütü, hangi yolun sonuna); kullanıcı onaylamadan yazma.

## 11. Beşinci yol: "AI ile Güvenlik" (29 Ekim 2026, kullanıcı kararı)

**Yeni oturumda açılan ajan için:** Bu dosyanın §0'ını oku, sonra `python -X utf8 tools/ai_pano.py oku -n 40` ve `python -X utf8 tools/ai_ders_takip.py liste` ile §9–§10'dan nerede kalındığını bul (`antigravity` adıyla açık/alındı dersler). Yarım işi bitir, sonra buraya geç. Kendi adınla (`--kim antigravity`) devam et.

**Neden:** Mevcut 4 yol AI sistemlerinin güvenliğini öğretir. Bu yol, AI'yı güvenlik işinde araç olarak kullanmayı öğretir (AI destekli zafiyet avı, keşif/fuzzing otomasyonu, log ve alarm triyajı, kendi saldırı ajanını yazmak). Purple ile AI yollarının buluştuğu yerdir.

**Sınırlar:** Yalnız yerel ve ücretsiz araçlar; hedef yalnız Pafta'nın kendi yerel laboratuvarları (ör. `sandbox/http_tezgah.py`, purple/web lab'ları) ve sentetik veriler. Dış ağa, gerçek sistemlere istek yok. Ajanlarda **kapsam kilidi** (izinli hedef listesi) ve yıkıcı eylemde insan onayı zorunlu. Modelin "bulduğu" açık, gerçek çıktıyla doğrulanmadıkça bulgu sayılmaz (halüsinasyon ölçümü dersin parçası).

**Faz A · Tasarım (kullanıcı onayı şart):** `docs/ai-gercek/AI-ILE-GUVENLIK-TASARIM.md` yaz: önerilen yol kimliği (`ai-ile-guvenlik`), 6 modül (`minik`, `tesviye`, `kucuk-orta`, `buyuk-orta`, `basalti`, `baspehlivan`), 15–20 ders (kimlik, başlık, ne öğretir, kullanılan kurulu araç, gerçek deney fikri), mevcut derslere bağlar. Taslak modül fikri:
1. Yerel LLM'i araç olarak kullanmak (Ollama API, yapılandırılmış çıktı, halüsinasyonu ölçmek)
2. Kod okuma ve zafiyet avında LLM (statik bulgu + LLM triyajı, yanlış pozitif oranı)
3. Keşif ve fuzzing otomasyonu (LLM ile yük üretimi yerel hedefe; Playwright, mitmproxy)
4. Log ve alarm triyajı (Sigma/pySigma, mevcut Elastic lab; LLM özeti ve doğrulama)
5. Kendi güvenlik ajanını yazmak (araç çağıran ajan, kapsam kilidi, onay)
6. Ajanı değerlendirmek ve güvence (başarı/yanlış bulgu oranı, tekrarlanabilirlik, insan denetimi)

Panoya `soru` (konu: `ai-ile-guvenlik`) bırak; kullanıcı onaylamadan Faz B'ye geçme.

**Faz B · İskelet (onaydan sonra):**
- `tracks/ai-ile-guvenlik/track.json`: biçimi `tracks/ai-guvence/track.json` gibi (`group: "ai"`, `runner: "python"`, sıradaki `order`, 6 modül).
- `ai_mufredat_plan_v3.json`: yeni yol kaydı (6 modül, rütbe sırası korunur), sonra `python -X utf8 ai_panel_uret.py`.
- `tools/ai_ders_takip.py` içindeki `YOLLAR` listesine yolu ekle (ortak dosya: önce panoya `uyari`, düzenlemeden hemen önce dosyayı yeniden oku, yalnız o satırı değiştir).
- `C:\Users\demo12\Desktop\Pafta-Platform-Projesi\YOL_HARITASI.html`: A listesine `A22 · AI ile Güvenlik yolu` kutusu.

**Faz C · Dersler:** Her ders §3–§6 standardında (görünür sentetik dosya, gizli test verisi, gerçekçi hatalı başlangıç kodu, mutasyon 0 geçen, sonda gerçek deney, kanıt). Bitince tracker `denetime-hazir`, panoya `bitti` + devir notu.

## 13. Antigravity'nin görevi bitti (29 Ekim 2026, kullanıcı kararı — DÜZELTME)

**Kullanıcı kararı: Antigravity yalnız kendi görevinden (§1, §9, §10, §11) sorumludur ve o görev TAMAMEN BİTTİ (38/38 ders; her birinde ders dosyası + gerçek deney modülü + kanıt doğrulandı, hepsi `denetime-hazir`). Antigravity'ye kendi görevi dışında YENİ ders yazdırılmayacaktır.**

Önceki sürümde burada "kalan sahipsiz dersleri Antigravity yazsın" denmişti; bu **geri alındı**. Antigravity bu bölümü dikkate almaz, yeni ders ALMAZ. Kendi görevi dışında kalan boş dersler (ai-guvence 15–30, ai-savunma 21–30, ai-saldiri-27 vb.) **claude-opus veya diğer ajanlar** tarafından yazılacaktır.

**Not — ai-guvence 01–14:** Antigravity bu düzeltmeden önce (eski §13 yüzünden) ai-guvence 01–13'ü yazıp `denetime-hazir` yaptı; 14'te araç engeline takılıp panoya `soru` bıraktı. Bu derslerin kendisi geçerli; ai-guvence-14 ve sonrası artık Antigravity'nin işi değil, başka ajana devredildi. Antigravity burada **durur.**
