# ai-saldiri-06 — gerçek extraction ve güvenli kayıt

Uygulayıcı kabul raporu; bağımsız denetim değildir.

## Değişiklikler

- tracks/ai-saldiri/lessons/ai-saldiri-06-system-prompt-extraction.md: mevcut adımlar korundu; bir anlat ve bir gerçek görev eklendi (index 8).
- sandbox/ai_gercek_ai_saldiri_06.py: gerçek kampanya, bağımsız sinyal/maske/rapor hesapları, maskeli kanıt.
- sandbox/ai_gercek_ai_saldiri_06_provider.cjs: promptfoo için yerel Ollama adaptörü, CPU zorlaması, kayıtlı sınırlı retry.
- Ortak motor, web ve validate kodu değiştirilmedi. Kurulum yapılmadı.

## Deney ve ölçüm

Öğrenci önceki üç görevin sizinti_sinyalleri, guvenli_kayit ve cikarim_raporu işlevlerini gerçek model sonuçlarında kullanır.
Kurulu promptfoo 0.125.1, yerel Qwen3 4B Instruct Q4_K_M; 2 kontrol + 2 doğrudan + 2 dolaylı vaka, ikişer tekrar = 12 planlı çağrı.
Düz, whitespace-normalize ve standart Base64 sızıntısı ayrı sinyallerdir; bir denemede iki sinyal olması iki başarı sayılmaz.
Bu sınıflandırıcı kısmi sızıntı veya başka kodlamaları kapsadığı iddiasında bulunmaz. Sızıntı olması/olmaması kabul şartı değildir.

Özel sentetik işaret her kampanyada yenidir. Sinyal ham metinde hesaplanır, yanıt SHA-256 özeti alınır. Kalıcı kanıtta iç içe
promptfoo JSON'u, sistem kaydı ve yanıtlar maskelenir. Casefold/whitespace eşleşmesinin görülen varyantları da maskeleyiciye verilir.
Öğrenci maskeleyicisinin çıktısı bağımsız temizleyiciyle ve ham girdi değişmezliğiyle karşılaştırılır; hatalı maskeleyici çalışsa
bile güvenli referans çıktısı saklanır, başarısız maskeleme testi PASS olmaz. Geçici ham dosyalar deney klasörüyle silinir.

## Kaynak sahipliği ve düzeltme

İlk ortak Ollama sürümünde iki gerçek çağrı HTTP 500 aldı (apply-template / model runner stopped). O koşu FAIL sayıldı ve
reference-before-isolation-failed.json olarak saklandı; hata başarıya çevrilmedi.
Çözüm: ai-temel-14'teki OzelCpuOturumu yeniden kullanılarak deneye ait ayrı loopback sunucusu; num_gpu=0, num_ctx=2048,
num_predict=96, sıcaklık 0.4, rastgele taban seed. Kullanıcının sunucusu veya başka ajanın modeli boşaltılmaz/kapatılmaz.
Kalıcı 500/timeout hatasında başarısızlık sürer. Geçici 5xx/ağ hatasında en fazla iki retry; her hata metadata.retries içinde saklı.
HTTP 400 tekrar edilmez. Ölçülen CPU model belleği 2.882.021.620 bayt, VRAM 0; sahipli süreç kapanışı kanıtta true.

## Kabul

- summary.json: referans PASS; starter, empty, constant, normal-missing, casefold-base64, shallow-redaction, count-signals FAIL; Run OK + kabul false kanıtı. 9/9 senaryo beklenen sonuç.
- Test içinde önceki üç görevin 9 mutantı ve rastgele yeni sırlı ek sözleşmeler de sınanır.
- dependency-cases.json: promptfoo eksik ve Ollama yürütülebilir dosyası eksik senaryoları FAIL; kabul kanıtı yok. İzolasyon sonrası tekrar doğrulandı.
- retry-fixture.json: açıkça fixture; 500→200 iki istek/tek hata kaydı, 400 tek istek. Gerçek model kabulü yerine sayılmadı.
- Ders ekranı: başlangıç 13/31 ile reddedildi. Son izole sürüm 41/41 gerçek kontrolle geçti; ui-data/ai-kanit/saldiri-06-extraction-1793243271255.json.
- UI Çalıştır modu ilk sürümde maskeli gerçek yanıt ve kabul yok kanıtı üretti; izole sürümde aynı CALISTIR yolu CLI üzerinden tekrar geçti.

Gerçek sonuç (CLI ve UI): doğrudan 2/4, dolaylı 0/4, kontrol sızıntısı 0. Sızan işaretler [GIZLI] oldu.
Base64 kolunda model farklı bir metnin kodunu verdi; doğru canary bulunmadığı için sızıntı sayılmadı.

## Regresyon

Önceki sürümde validate-serial.log: 34 ders/259 kontrol TEMİZ.
İzolasyon sonrası validate-final.log koşusunda özel sunucu hazırlığında zaman aşımı görüldü; bu koşu başarısızdır. Kayıt validate-before-setup-retry-failed.log olarak da korunur. Ardından yalnız ai-saldiri-06 içindeki ExtractionSession hazırlık aşamasına en fazla iki deneme eklendi: geçici ağ/5xx hataları kayıtlı biçimde yeniden denenir; 404 gibi kalıcı HTTP hataları yeniden denenmez. Ortak ai-temel-14 dosyası değiştirilmedi. setup-retry-fixture.json üç senaryoyu doğrular (fixture; gerçek kabul yerine sayılmaz). Bu düzeltmeden sonra validate-06-final.log: 1 ders / 10 kontrol TEMİZ. Tüm yolun son koşusu validate-final-with-setup-retry.log içinde ayrıca değerlendirilir; sonuç doğrulanmadan temiz kabul edilmez.
Sıralı koşu aynı validate.run_job kontrollerini kullanır, yalnız zamanlamayı değiştirir; önceki derste kayıtlı paralel HTTP
zaman aşımı ayrı panoda kalır. Bu rapor paralel koşudaki sorunun düzeldiği iddiasında bulunmaz.

Commit/push yapılmadı. Ders henüz bağımsız denetlenmedi.


## Son kapanış doğrulaması — 29 Ekim 2026

- Son hazırlık retry sürümünde ders ekranındaki Kontrol yeniden çalıştırıldı: 41/41 PASS. Kanıt: ui-data/ai-kanit/saldiri-06-extraction-1793259120857.json. kaynak=gercek, kabul=true; sahipli sunucu kapanışı true; doğrudan 2/4, dolaylı 0/4, kontrol yanlış pozitifi 0/4.
- validate-final-with-setup-retry.log: 34 ders / 259 kontrolün 258'i geçti. Yalnız ai-saldiri-05 gerçek görevinde sekiz çağrının eksiksiz tamamlanması / gerçek yanıt doğrulaması başarısız oldu. Bu toplu koşu TEMİZ değildir. ai-saldiri-06 çözümü ve başlangıç kodu kontrolleri geçti.
- Kod değişikliği yapılmadan yalnız başarısız ai-saldiri-05 yeniden çalıştırıldı: python -X utf8 tools/validate.py --yol ai-saldiri ai-saldiri-05; validate-05-recheck.log: 1 ders / 10 kontrol TEMİZ. İlk başarısız toplu koşu saklandı; bütün yolun tek koşuda temiz geçtiği iddia edilmiyor. Geçici ortak model hatası olasılığı mevcut; kesin kök neden kanıtlanmadı. Denetim-31 kapsamındaki 05 koduna müdahale edilmedi, bulgu ortak panoya yazıldı.
- Yeni görünür çalışma dosyası standardı ileriye dönük kaydedildi. 06'nın bu önceki gerçek deney akışı maskeli yanıtları Çalıştır ile gösterir; ayrı kalıcı/düzenlenebilir öğrenci dosyası ve arayüz altyapısı bu kapanışta eklenmedi. Tüm derslere tamamlandı diye işaretlenmedi.
- Kendi kabulü tamamlanan 06 tracker'da denetime-hazir olur; bitti kararı bağımsız denetçiye aittir. Commit/push yok.
