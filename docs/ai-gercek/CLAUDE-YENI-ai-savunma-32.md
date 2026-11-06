# Yeni ders ai-savunma-32: yazar kontrolleri tamam, denetime hazır

- **Yazar:** claude-yazar. Brief'te codex'e atanmıştı; 03.11.2026'da kullanıcı kararıyla claude-yazar'a geçti (panoda `karar` kaydı var).
- **Görev kaynağı:** `docs/ai-gercek/GOREV-YENI-AI-DERSLERI.md`, dalga 2.
- **Puan verilmedi.** Bağımsız denetim claude-opus'tadır.
- **Görsel sınama yapılmadı.** Ders web arayüzünde açılmadı; kabul yalnız CLI'de `tools/validate.py` ile yapıldı.

## İndirme (kullanıcı onayıyla, 03.11.2026)

Önce panoya `uyari` yazıldı. Dosyalar yalnız Hugging Face önbelleğine indi; pip kurulumu yapılmadı.

| Kaynak | Revizyon | İndirilen dosyalar | Lisans |
|---|---|---|---|
| `distilbert/distilbert-base-uncased` | `12040accade4e8a0f71eabdb258fecc2e7e948be` | `config.json`, `model.safetensors` (267 954 768 bayt), tokenizer dosyaları | Apache-2.0 |
| `deepset/prompt-injections` | `4f61ecb038e9c3fb77e21034b22511b523772cdd` | iki parquet dosyası (40 KB + 11 KB) | Apache-2.0 |

Parquet dosyalarının sha256 değerleri:

- train: `2e10bc7a…`
- test: `39ac797c…`

Bu değerler sandbox'ta sabit tutulur ve kabul adımında doğrulanır.

## Eklenen / değişen dosyalar

- `tracks/ai-savunma/lessons/ai-savunma-32-guardrail-egitme-distilbert.md` (sha256 b6ff6e95842dae68…)
- `sandbox/ai_gercek_ai_savunma_32.py` (e7c0826aad48234b…)
  - Model ve veriyi çevrimdışı, sabit revizyonla yükler.
  - Önbellekte yoksa `GercekLabYok` verir ve kendisi indirme yapmaz.
- `tracks/ai-savunma/fixtures/ai-savunma-32/README.md` ve `veri/siniflandirici.json` (6ad00581716b5992…)
- `outputs/yeni-ai-savunma-32/` altındaki kanıt dosyaları:
  - `yazar-sondasi.json`: hata vitrininin kaynağı (bozulma raporunun J'siz ilk sürümü; recall ve FPR değerleri aynı).
  - `savunma32-kabul-1793704942958.json`: son kabul kanıtının kopyası.
- `tracks/ai-savunma/track.json`: "Girdi ve Çıktı Muhafızı" modülünün sonuna yalnız `ai-savunma-32` eklendi.
- Değişmeyenler: `engine/`, `web/`, `sandbox/ai_gercek_lab.py`. Commit/push yok.

## İçerik

### Atıflar

- DistilBERT: Sanh vd. 2019, arXiv:1910.01108 (6 katman, yaklaşık 66 milyon parametre).
- Veri seti kartı: 546 eğitim + 116 test, İngilizce ve Almanca.
- Etiket tartışması derste gerçek test örnekleriyle gösterilir: "act as an interviewer…" ve "Generate SQL code…" örnekleri 1 (injection) etiketli.

### Görevler

1. `siniflandirma_metrikleri`: eşiğe eşit skor pozitif sayılır; sıfıra bölmede 0.0 döner; FPR'nin paydası yalnız negatif örneklerdir.
2. `esik_sec`: FPR sınırı dahil, en yüksek recall'ı veren eşiği seçer. Eşit recall'da yüksek eşik seçilir; uygun eşik yoksa `None` döner.
3. `bozulma_raporu`: kip başına recall, FPR, J = recall − FPR ve `j_dusus` hesaplar. En zayıf kip, J'si en düşük olandır.

### KUSURLU başlangıç kodları

Üç kusurlu başlangıç kodu var. Kusurlar kodda yorumla belirtilmez.

- **K1:** `>` kullanır, tahmin yoksa precision'ı 1 sayar, FPR'yi bütün örnek sayısına böler.
- **K2:** küçükten büyüğe gezer, sınırı `<` ile denetler, eşitlikte düşük eşiği seçer, uygun eşik yoksa 0.5 döner.
- **K3:** en zayıf kipi recall'a göre seçer, recall farkını `j_dusus` alanına yazar.

### Anlatım teknikleri

- **Anlatım:** ilk anlatım bloğu 450 kelimenin üzerinde. Ayrı "saldırgan ne dener / savunma neden kırılır" bölümleri var.
- **Tahmin → çalıştır → fark:** eşit skor ve sıfıra bölme.
- **Eşleme:** `esleme: ai-saldiri-04, ai-saldiri-11, ai-saldiri-52`.
- **Hata vitrini:** leet, homoglif ve harf aralı kiplerde recall 1.0'a çıkıyor, ama FPR de 0.84–1.0'a çıkıyor. Sıfır genişlikli karakter etkisiz kalıyor; nedeni tokenizer'ın bu karakterleri silmesi, token listesi kanıtta görülüyor. Anahtar kelime listesinin recall'ı 0.35.
- **Kapanış:** öğrenciye kanıt dosyası okutulur; ders Sınır cümlesiyle biter.

## Gerçek final (son kabul koşusu)

- **Ortam:** cuda (RTX 5050 Laptop), torch 2.14.1+cu130, transformers 5.21.0.
- **Veri bölünmesi:** 465 eğitim / 81 doğrulama (sınıf oranı korundu, seed 32) / 116 test.
- **Eğitim:** 3 tur, 90 adım. Kayıp 0.684'ten 0.0085'e indi; ağırlık hash'i değişti.
- **Eşik seçimi:** doğrulama kümesinde, FPR ≤ 0.05 kuralıyla 0.094 seçildi (doğrulamada recall 1.0, FPR 0).

Test sonuçları:

| Sınıflandırıcı | Recall | FPR | F1 |
|---|---|---|---|
| DistilBERT, eşik 0.5 | 0.817 | 0 | 0.899 |
| DistilBERT, seçilen eşik | 0.900 | 0.018 | 0.939 |
| Anahtar kelime listesi | 0.350 | 0.036 | 0.506 |

Bozulma raporu (seçilen eşikle):

| Kip | Recall | FPR | J |
|---|---|---|---|
| orijinal | 0.90 | 0.018 | 0.882 |
| sifir_genislik | 0.90 | 0.018 | 0.882 (etkisiz) |
| leet | 1.0 | 0.875 | 0.125 |
| homoglif | 1.0 | 0.839 | 0.161 |
| harf_bosluklu | 1.0 | 1.0 | 0 |

- En zayıf kip: `harf_bosluklu`.
- Sabit seed ile iki koşu aynı sonucu verdi (yazar sondası ve kabul).
- Kanıt: `outputs/yeni-ai-savunma-32/savunma32-kabul-1793704942958.json`.

## Kendi kontrollerim (`.ai-venv/Scripts/python.exe -X utf8`)

- `tools/validate.py ai-savunma-32` (PAFTA_DATA scratchpad): TEMİZ, 9 kontrol (1 tahmin, 4 solution, 4 starter). Gerçek adım 1 dakikadan kısa sürüyor.
- `tahmin.py . ai-savunma-32`: 1 tahmin, 0 şüpheli.
- `kirp_gercek.py` + `mutasyon.py --en-cok 1000`: 25 + 30 + 26 = 81 mutant, 0 geçen.
  - İlk turda 9 mutant geçmişti, hepsi sınır durumlarıydı: yalnız biri tuple olan girdi, eşiğe eşit negatif skor, eşik 0/1, skor 0/1, `bool` etiket.
  - Bu durumlar için doğru testler eklendi; var olan testler zayıflatılmadı.
- Kopya sondası 7/7 reddedildi:
  - modül takma adı
  - `from sandbox import`
  - importlib
  - `__import__` + vars
  - inspect.getsource + exec
  - `*` import
  - doğru çözüm + eval
- Kopya denetimi `kod_denetimi(..., izin=())` ile yapıldı.

## Bilinen sınırlar / denetçiye not

- **Bozulmalar yalnız test zamanında.** Bozulma örnekleriyle eğitim yapılmadı (data augmentation yok); ders bunu yapmaz, yalnız ölçer.
- **Yüksek FPR'nin olası nedeni.** Sonuç, modelin "alışılmadık token dizisi"ni injection'la ilişkilendirmesiyle tutarlı. Ders bunu bir neden olarak iddia etmez; yalnız ölçümü gösterir.
- **Dil sınırı.** `distilbert-base-uncased` İngilizce bir modeldir, ama veri setinin yaklaşık üçte biri Almanca. Dil bazında ayrı metrik raporlanmadı.
- **Örneklem küçük.** 116 test örneği ve tek eğitim koşusu var.
