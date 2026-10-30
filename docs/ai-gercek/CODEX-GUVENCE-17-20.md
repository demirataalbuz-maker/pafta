# CODEX GUVENCE 17–20 devir

CLI TAMAM / UI BEKLIYOR. Tracker calisiliyor kalır; denetime-hazir veya bağımsız denetim iddiası yok.

Kapsam yalnız ai-guvence-17/18/19/20 (kutular105–108). Eski adımlar korundu. Ortak motor/web davranışı, G14/G16 veya başka serit dosyası değiştirilmedi. Kurulum, indirme, GPU eğitimi, commit/push ve başka süreç durdurma yok.

## Uygulama

- G17: iki bağımsız shadow/target çifti, gerçek 12–24–2 MLP/SGD/autograd/CPU; eşik yalnız shadow üyeliklerinden seçilir. Hedef true-class olasılıklarına öğrenci AUC/TPR/FPR/avantaj ölçümü uygulanır.
- G18: her tohumda aynı veri, başlangıç ağırlıkları ve mimariyle 3/35 epoch gerçek eğitim; öğrenci genelleme açığı ve AUC risk raporunu üretir. İki tohum sonucu monoton risk varsayımını doğrulamaya zorlanmaz.
- G19: gerçek örnek başına autograd, öğrencinin L2 kırpması gerçek optimizer gradyanına girer. Sabit n replace-one duyarlılık2C/n; 8 tam batch Gaussian adım, öğrenci her adımda konservatif zCDP/RDP bütçesi hesaplar; sigma ve2sigma ayrı adaylar.
- G20: standart eğitim ve örnek-başı kırpılmış Gaussian eğitim, iki tohumda gerçek AUC/fayda karşılaştırması; öğrenci iddia kapısını değerlendirir. Desteğin çıkmaması PASSı engellemez; düşük AUC biçimsel garanti değildir.

## Kesin UI devri

| Ders | Gerçek görev indeksi (sıfırdan) | URL |
|---|---:|---|
| ai-guvence-17 | 7 | http://127.0.0.1:18800/#/ders/ai-guvence/ai-guvence-17/7 |
| ai-guvence-18 | 7 | http://127.0.0.1:18800/#/ders/ai-guvence/ai-guvence-18/7 |
| ai-guvence-19 | 7 | http://127.0.0.1:18800/#/ders/ai-guvence/ai-guvence-19/7 |
| ai-guvence-20 | 7 | http://127.0.0.1:18800/#/ders/ai-guvence/ai-guvence-20/7 |

Dört derste yeni görünür veri anlatı indeksi6. G17/18 toplam8 adım; G19/20 kaynak/varsayım anlatısı sonradan eklenmiş, toplam9 adım (kaynak anlatısı8). UI düğmelerinde gerçek görev8. Parent sunucusu18800 yeniden başlatılmadı/kapatılmadı. G17 üzerinde bir başlangıç Kontrol çağrısı gönderildi; sonucun DOM gözlemi yapılmadan UI koordinasyon talimatıyla duruldu. Çözüm açılmadı; parent kalan starter denemesini ve çözümle Kontrol/Çalıştır kabulünü yapmalı. G18/19/20 UIye dokunulmadı. UI PASS/ekran görüntüsü/görünür dosya tıklama kabulü BEKLIYOR.

## Kabul komutları ve gerçek sonuç

Proje kökünde:

```text
python -X utf8 outputs/codex-guvence-17-20/accept.py
python -X utf8 outputs/codex-guvence-17-20/run-persistence.py
PAFTA_DATA=outputs/codex-guvence-17-20/validation-data python -X utf8 tools/validate.py ai-guvence-17 ai-guvence-18 ai-guvence-19 ai-guvence-20
```

Son satır ortam ataması açıklayıcıdır; PowerShellde `$env:PAFTA_DATA="outputs/codex-guvence-17-20/validation-data"` sonra python komutu kullanıldı.

- CLI36/36 beklenen sonuç: her ders referans PASS+gerçek kabul kanıtı; starter/boş/sabit/3 anlamlı mutant RED; eksik yorumlayıcı BağımlılıkEksik; göreli PAFTA_DATA kökü ve düzenlenmiş kopyanın korunması.
- CLI Run4/4: seed991, ornek11, sigma3 düzenlenmiş ayarı gerçek eğitimde kullanıldı, dosya byte olarak korundu; Run kanıtı kabul:false/mod:run, Kontrol kanıtı kabul:true/mod:test.
- Son regresyon:4 ders36kontrol, tahmin4/solution16/starter16; TEMİZ. İlk regresyonda G20 utility mutantı için yetersiz kontrat vakası bulundu ve düzeltildi; validate.txt eski sonucu, validate-final.txt son kabulü saklar.
- Görünür dosyaların HTTP GET ve içeriği: 4/4; fixture-http.json. Bu UI tıklama kabulü değildir.

## Kanıtlar ve ölçümler

- ai-guvence-17: `C:\Users\demo12\Documents\Pafta-AI-GercekLab\outputs\codex-guvence-17-20\cli-data\ai-kanit\guvence-17-cpu-1793299795010.json`
  Gerçek özet: `[{"auc": 0.781065, "tpr": 0.769231, "fpr": 0.384615, "avantaj": 0.384615}, {"auc": 0.840237, "tpr": 0.615385, "fpr": 0.230769, "avantaj": 0.384615}]`
- ai-guvence-18: `C:\Users\demo12\Documents\Pafta-AI-GercekLab\outputs\codex-guvence-17-20\cli-data\ai-kanit\guvence-18-cpu-1793299848082.json`
  Gerçek özet: `[{"acik": 0.307692, "auc": 0.650888, "risk": true}, {"acik": 0.384615, "auc": 0.739645, "risk": true}, {"acik": 0.076923, "auc": 0.615385, "risk": false}, {"acik": 0.230769, "auc": 0.56213, "risk": false}]`
- ai-guvence-19: `C:\Users\demo12\Documents\Pafta-AI-GercekLab\outputs\codex-guvence-17-20\cli-data\ai-kanit\guvence-19-cpu-1793299901849.json`
  Gerçek özet: `[{"sigma": 1.75, "epsilon": 9.061711505454005, "test_dogruluk": 0.5384615384615384}, {"sigma": 3.5, "epsilon": 4.204325140482105, "test_dogruluk": 0.6153846153846154}, {"sigma": 1.75, "epsilon": 9.061711505454005, "test_dogruluk": 0.5384615384615384}, {"sigma": 3.5, "epsilon": 4.204325140482105, "test_dogruluk": 0.5384615384615384}]`
- ai-guvence-20: `C:\Users\demo12\Documents\Pafta-AI-GercekLab\outputs\codex-guvence-17-20\cli-data\ai-kanit\guvence-20-cpu-1793299970886.json`
  Gerçek özet: `[{"auc_azalisi": 0.035503, "dogruluk_kaybi": 0.153846, "destekli": false, "bicimsel_garanti": false}, {"auc_azalisi": 0.076923, "dogruluk_kaybi": 0.0, "destekli": false, "bicimsel_garanti": false}]`

CLI tam sonuçlar: outputs/codex-guvence-17-20/cli-acceptance.json; Run/persistence: cli-run-persistence.json; tam regresyon: validate-final.txt. Kanıtlar model/torch sürümü, CPU, giriş özellik/etiketleri, gerçek logitler, eğitim loss izi, ağırlık SHA256, tohum/ayarlar, kırpma/gürültü normları/bütçe, öğrenci kod SHA256 içerir.

## Görünür veri ve kalıcılık

web/data/ai-guvence-17..20-ayarlar.txt sentetik JSON ayarlarıdır; gerçek model çıktısı değildir. Dersin bağlantısı /data/ai-guvence-N-ayarlar.txt salt okunur örneği açar. Öğrenci kopyası PAFTA_DATA/calisma/ai-guvence-N/ayarlar.json, yalnız ilk kullanımda exclusive-create ile hazırlanır. Göreli PAFTA_DATA proje kökünde çözülür. Çalıştır tam yolu gösterir. Metin editörüyle değişiklik yapılır; yeniden Çalıştır üzerine yazmaz. Kontrol farklı seed/ornek/sigma kullandığından öğrenci fixtureı beklenen cevabı değiştirmez. Parent UI-data kökünde de Run kendi kopyasını oluşturacaktır.

## Sınırlar ve birincil kaynaklar

Açık tohum ve ham skor/girdi/loss/norm izleri öğretim içindir. Bu transkript özel bir üretim yayını değildir; DP-SGD/Opacus sertifikasyonu veya sohbetmodeli gizlilik garantisi iddia edilmez. Epsilon yalnız ideal bağımsız gizli Gaussian rastgelelik varsayımı altında, tek adayın ağırlık mekanizması hesabıdır; ham istatistik yayınları, standart model yayını ve farklı adayları birlikte yayınlama bütçesi değildir. Aynı veri üzerindeki birden çok ağırlık yayını birlikte yapılacaksa rho değerleri ayrıca toplanmalıdır. Altörnekleme indirimi yoktur. Güvenli RNG/üretim accountant denetimi yapılmadı.

- Bun ve Steinke: https://arxiv.org/html/1605.02065v1 — Önerme1.3 dönüşüm;1.6 Gaussian; Lemma1.7 bileşim; bölüm2.2 çokboyutlu mekanizma.
- Mironov: https://arxiv.org/abs/1702.07476 — Gaussian Rényi DP ve bileşim.

## Değişen dosyalar

- sandbox/ai_gercek_ai_guvence_17_20.py
- tracks/ai-guvence/lessons/ai-guvence-17-uyelik-cikarimi-saldirisi-olcumu.md
- tracks/ai-guvence/lessons/ai-guvence-18-asiri-ogrenme-ile-gizlilik-riski-iliskisi.md
- tracks/ai-guvence/lessons/ai-guvence-19-diferansiyel-gizlilik-butcesi-deneyi.md
- tracks/ai-guvence/lessons/ai-guvence-20-gizlilik-iddialarinin-saldiriyla-dogrulanmasi.md
- web/data/ai-guvence-17-ayarlar.txt
- web/data/ai-guvence-18-ayarlar.txt
- web/data/ai-guvence-19-ayarlar.txt
- web/data/ai-guvence-20-ayarlar.txt
- docs/ai-gercek/CODEX-GUVENCE-17-20.md
- outputs/codex-guvence-17-20/* (test betikleri, raporlar, sentetik düzenlenmiş kalıcılık kopyaları ve gerçek JSON kanıtları)

Kalan kabul: Parent tarafından ders ekranı Kontrol/Çalıştır, görünür fixture bağlantısını açma ve Run öğrenci dosyasını doğrulama; ardından tracker denetime-hazir. Bağımsız denetim ayrıca gerekir.

Parent entegrasyon düzeltmesi:17–20starterlarına çözümdeki CALISTIR/goster son eki eklendi. Öğrenci yalnız fonksiyonu tamamlayınca Run gerçek deneyi çalıştırır. Çözüm/test algoritması değiştirilmedi.
