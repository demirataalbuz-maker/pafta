# ai-guvence-07 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı; puan ve bağımsız denetim başka bir AI'ya aittir (claude-yazar bu dersi puanlamaz).

## Ne değişti

- **Çelişki:** İlk anlatımdaki "Bu derste PyTorch, ART veya Matplotlib çalıştırılmaz" cümlesi kaldırıldı. Yeni metin şöyle: görev 1–3 sentetik veriyle çalışır, son adım PyTorch ile gerçek bir modeli eğitip autograd gradyanı kullanır.
- **Tablo + `[!NOT]`:** İlk anlatımın başına "Gerçek araç/model ne gösterir | Bu ders ne kullanır | Ne söyleyemez?" tablosu ve sentetik veri/kalıcılık notu eklendi.
- **Görünür fixture:** `tracks/ai-guvence/fixtures/ai-guvence-07/` altına README ile birlikte iki dosya eklendi:
  - `veri/fgsm_ornekleri.json`: 3 geçerli örnek (biri kırpma, biri sıfır gradyan) ve 2 bilerek bozuk örnek (aralık dışı, boyut farkı).
  - `veri/epsilon_gozlemleri.json`: sırasız eğri gözlemleri. ε=0.3'te kırpma yüzünden L∞ < ε. ε=0.2 ile ε=0.3 aynı kaybı veriyor (eşitlik). Ayrıca L∞ bütçesini aşan bir `bozuk_gozlem` var.
  - Görev 1–3'ün setup bloğu `ai_guvence_veri.hazirla("ai-guvence-07")` çağırır. Başlangıç kodları bu dosyaları okuyup ham veriyi ve sonucu yazdırır. Dosyalar sentetik olarak etiketlendi ve kalıcı değil; testler ayrı, gizli verilerle sınar.
- **Kusurlu başlangıç kodları (4 görev):**
  - Görev 1, girdiyi kopyalamadan döndürür ve aralık/boyut/tür denetimi yapmaz. İki bozuk örneği kabul eder.
  - Görev 2, sıfır gradyana +ε uygular ve bozuntuyu kırpma öncesi ham ε·işaret olarak raporlar.
  - Görev 3, L∞ bütçesini denetlemez, taban sıfırsa sıfıra böler ve eşitlikte yüksek ε seçer (görünür veride 0.3 seçer, doğrusu 0.2).
  - Gerçek deneyde `fgsm` ters işaretle adım atar ve kırpmaz. `epsilon_egrisi` ise L∞ yerine ε yazar ve temiz doğruluğu 1.0 sabitler. Çalıştır'da bu başlangıç kodu ε=0.3'te bile 0.938 doğruluk gösterir; çözümde bu değer 0.015'tir. Böylece ters işaret hatası gözle görülür.
- **Anlatım:** 3 anlatım bloğu toplam 901 kelime oldu (ilk blok 284 kelime). Eklenen konular:
  - İşaretin nedeni (doğrusallık açıklaması).
  - Gerçekleşen L∞ ile ε arasındaki fark.
  - Eğri okuma (ε=0 noktasının temiz doğruluğa eşit olması gerekir).
  - Tuzaklar: normalize uzay, kırpma, ters işaret, gradyan maskeleme ve FGSM'in neden yalnız alt sınır testi olduğu.
  - Savunucu bakışı (FGSM adversarial eğitimi, katastrofik aşırı uyum, PGD'ye köprü).
  - Gerçek deney anlatımına autograd adımları ve bu makinedeki ölçülmüş eğri eklendi. Ölçülen sayıların yalnız bu koşuya ait olduğu açıkça yazıldı.
- **Kopya koruması:** Yeni `sandbox/ai_gercek_ai_guvence_07.py` dosyası `fgsm_referans` ve `epsilon_egrisi_referans` işlevlerini içerir. Test bozuntuyu ve eğriyi bu referanslarla karşılaştırır.
  - Test şu çağrıyı yapar: `ai_lab.kod_denetimi(src, yasak=("fgsm_referans", "epsilon_egrisi_referans", "kanit_yaz"))`.
  - Ek AST kontrolü şunları reddeder: yasak adların ve `*` importu, referans modülünün importu, `inspect`/`importlib`/`runpy` importu, `exec`/`eval`/`compile`/`__builtins__` kullanımı.
  - İhlalde `stop()` çağrılır. Kanıt yalnız `kanit_yaz(..., kabul=all(sonuclar))` ile yazılır.
  - Mevcut 5 hatalı-FGSM mutantı ve eğri karşılaştırması korundu; hiçbir test zayıflatılmadı.
- Ortak `sandbox/ai_gercek_lab.py`, `engine/` ve `web/` değiştirilmedi.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`)

- `tools/validate.py ai-guvence-07` (PAFTA_DATA=`Desktop/pafta-g07-kabul-20261030`): **TEMİZ**. 9 kontrol: tahmin 1, çözüm 4, başlangıç kodu 4.
- `docs/denetim/araclar/tahmin.py . ai-guvence-07`: 1 tahmin, **0 şüpheli**.
- `kirp_gercek.py Desktop/pafta-mutasyon-g07-20261030`, ardından `mutasyon.py --en-cok 1000 ai-guvence-07`: 11+23+11 = 45 mutant, **0 geçen**. Kopya klasörü sonra silindi.
- `kopya_sonda.py ai-guvence ai-guvence-07 ...` (PAFTA_DATA=`Desktop/pafta-g07-sonda-20261030`): 6 deneme yapıldı, hepsi **fail → korunuyor**. Hiçbirinde kanıt yazılmadı:
  1. `from sandbox.ai_gercek_ai_guvence_07 import fgsm_referans as fgsm, epsilon_egrisi_referans as epsilon_egrisi`
  2. `from sandbox import ai_gercek_ai_guvence_07 as M; fgsm = M.fgsm_referans; ...`
  3. `getattr(M, 'fgsm_' + 'referans')`
  4. `exec(inspect.getsource(M).replace('_referans', ''))`
  5. `from ... import *`
  6. `importlib.import_module(...)` ile `M.__dict__[...]`

## Gerçek sonuç

- Kanıt dosyası: `Desktop/pafta-g07-kabul-20261030/ai-kanit/guvence-fgsm-*.json`. Değerleri: kabul true, torch 2.14.1+cu130, CPU, 200 Adam adımı, son kayıp 0.000275, test doğruluğu 1.0.
- Tam test eğrisi: ε 0 → 1.000, 0.05 → 0.988, 0.1 → 0.723, 0.2 → 0.075, 0.3 → 0.015. ε=0.1'de 400 tahminin 111'i değişti.
- Örnek kaymalar: cerceve → yatay/dikey, capraz → dikey.
- Çalıştır (CLI üzerinden runner `run`): başlangıç kodu ve çözüm ikisi de `ok`. Kanıtlar `kabul: false` etiketli.
- Gerçek deneyde başlangıç kodu Kontrol'den `fail` aldı (FGSM ve eğri kontrolleri kırmızı).
- Görev 1–3'ün başlangıç kodu ve çözümü görünür veriyle elle koşturuldu:
  - Başlangıç kodları kusuru gösteriyor: bozuk örnekler kabul ediliyor, sıfır gradyana ±ε uygulanıyor, eşitlikte 0.3 seçiliyor.
  - Çözümler doğru sonucu veriyor: bozuk örnekleri reddediyor, kırpılmış farkı veriyor, 0.2'yi seçiyor ve `bozuk_gozlem`i L∞ gerekçesiyle reddediyor.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.** Ders ekranında Kontrol/Çalıştır akışı ve görünür dosyaya erişim yalnız CLI ve runner üzerinden doğrulandı.
- Kurulum, indirme, commit/push veya puan yazımı yapılmadı. Başlatılan süreç kalmadı; kullanıcının Ollama/WSL/Docker ortamına dokunulmadı.
