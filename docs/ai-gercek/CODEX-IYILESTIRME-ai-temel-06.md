# ai-temel-06 iyileştirme teslimi

Codex kendi kontrollerini yaptı; bağımsız denetim ve puan claude-opus'a ait.

İş emri tamamlandı: ilk anlatımın başına gerçek araç/model, ders temsili ve yorum sınırı tablosu + NOT eklendi; PyTorch çalıştırılmaz çelişkisi görev1–3 sentetik / final gerçek model ayrımıyla giderildi. Yaklaşık796 sözcük anlatım Q/K/V projeksiyonları, RoPE/GQA hazırlığı, ardışık kafa bölme, kafa boyutuyla ölçekleme, softmax öncesi maske, Value karışımı ve birleşik bağlamın modelde nereden yakalandığını açıklar. Attention ağırlığının anlamsal açıklama veya izin denetimi olmadığı, nedensel maskenin prompt injection güvenlik duvarı olmadığı belirtilir.

Görünür veri tracks/ai-temel/fixtures/ai-temel-06/attention.json ve README'de. İlk üç görev mevcut ai_temel_veri.hazirla setup'ı ile aynı veri/attention.json dosyasını okur. Başlık görevi vektör/kafa sayısı, maske ve softmax görevleri skor/pozisyon alanlarını kullanır. Gelecek skor100 bilerek görünürdür; yanlış paydanın etkisi anlaşılır. Dosya elle yazılmış sentetik örnek, model kaydı değildir. Kaynak editörle açılabilir; editörde yüklenen listenin kopyası değiştirilerek Run denenir. Her çalıştırmada geçici kopya yenilenir, kalıcılık yok. Gizli testler ayrıdır.

Starter1 ardışık dilim yerine atlamalı başlık üretir; starter2 geleceği None yerine sıradan sıfır skoruna çevirir; starter3 geleceği softmax paydasına kattıktan sonra sıfırlar. Üçü Run'da çalışır ve Check'te reddedilir. Çözümler aynı dosyayı okur ve ham veri/sonucu gösterir.

Temel sözleşmelere sonlu girişler ve NaN/sonsuz retleri eklendi. Başlık ve maske görevinde bağımsız liste/kopya şartı çıktı değiştirilerek de doğrulanır. Maskeli softmax görevinde geleceğin1000 veya-1000 yapılmasının izinli ağırlıkları değiştirmediği ve girdi listesinin korunması sınanır. Önceki doğru sınır, sıra ve mutant testleri korunur; test zayıflatılmaz.

Mevcut gerçek model modülü sandbox/ai_gercek_ai_temel_06.py ve ortak model yükleyici değiştirilmedi. Son görev gerçek katmanlardan RoPE/GQA hazırlanmış Q/K/V alır; öğrenci bağlamını bağımsız float64 hesapla ve modelin çıkış projeksiyonuna giren gerçek birleşik bağlamla karşılaştırır. Gerçek çıkışta float64 şartı açık test edilir. Boş D boyutu ValueError olarak netleştirildi; D≥1 sözleşmeye yazıldı ve test edildi. Gerçek modelin ortak geçmiş logit farkı için ayrıca kontrol eklendi. Girdi model çağrıları, rastgele katman/metin örnekleri, ölçek/maske/sıra mutantları korunur.

Gerçek test guard'ı referans, katman_girdileri, kafa_ozeti, nedensellik, kanit_yaz, scaled_dot_product_attention ve MultiheadAttention isimlerini kod_denetimi ile korur. ImportFrom takma ad/yıldız importunu da denetler, ihlalde stop. Temel gerçek sözleşme veya model/nedensellik kontrolü başarısızsa kabul kanıtı yazılmadan durur. Gerçek kanıt kabulü bütün sonucların all sonucudur. Boş/sabit/kopya çözümler kendi başlarına model kanıtı oluşturmaz.

Dört zorunlu kontrol (.ai-venv/Scripts/python.exe -X utf8):
- tools/validate.py ai-temel-06: TEMİZ9; tahmin1 çözüm4 starter4; PAFTA_DATA Desktop/pafta-t06-kontrol-20261030.
- docs/denetim/araclar/tahmin.py . ai-temel-06: 1 tahmin, sıfır şüpheli.
- kirp_gercek.py Desktop/pafta-mutasyon-t06-20261030 (önce yokluğu doğrulandı); kopyadaki mutasyon.py <kopya> --en-cok1000 ai-temel-06: 12+12+14=38 mutant, sıfır geçen. Son ilk3 starter/solution/test/setup blokları mutasyon kopyasıyla aynı.
- kopya_sonda.py ai-temel ai-temel-06 "from sandbox.ai_gercek_ai_temel_06 import referans as cok_basli_dikkat": fail korunuyor. kopya.json hedef guard mesajını ve kabul kanıtı yokluğunu ayrıca doğrular.

Ek olumsuz kanıtlar outputs/iyilestirme-codex-ai-temel-06: bos.json, sabit.json, float32.json fail ve kabul yok. Float32 sondası doğru hesabı yapıp çıktıyı yanlış dtype'a çevirir; açık float64 koşuluyla reddedilir. eksik-yorumlayici.json BağımlılıkEksik error, kabul yok; yalnız kendi süreç ortamında olmayan PAFTA_AI_PYTHON seçildi, kurulum değiştirilmedi. gorunur-dosya-run-1/2/3.json normal runner/setup ile sentetik dosyayı ve sonuçları ok gösterir.

Gerçek CLI kanıtı Desktop/pafta-t06-kontrol-20261030/ai-kanit/temel-cok-basli-1793367772153.json. Kurulu SmolLM2-135M modeli, aynı pinli revizyon ve gerçek katman kullanıldı. Dört gerçek vaka model bağlamı farkları yaklaşık3.62e-7,5.73e-8,1.63e-6,5.97e-7; model toleransı1e-4 içinde. Dokuz kafa özetlendi. Son kelime table→chair değişiminde ortak8 geçmiş konumun logit farkı0.0, son konum farkı8.730627. Bu dar model/metin/katman ölçümüdür; dikkat haritası anlamsal önem veya genel güvenlik puanı değildir. Model/sürüm/ağırlık hash/cihaz, girdiler ve çıktılar kanıtta kayıtlı.

Kendi127.0.0.1:18800 sunucumda normal token/Origin HTTP kabulü http-check.json pass12/12, gerçek kabul; http-run.json ok, gerçek kabulfalse. Run kafaların dikkat özetini, model bağlam farkını ve gerçek nedenselliği gösterir. CLI/HTTP görsel kabul yerine sayılmaz. Görsel ekran sonuçları ek kayıtta belirtilir; önceki derslerin açık görsel kabulleri bu dersle kapanmaz.

Yalnız kendi18800 test sunucum kapatıldı. Kullanıcı Ollama/WSL/Docker süreçleri kapatılmadı. Yeni indirme/kurulum, genel engine/web değişikliği, commit/push veya puan yazımı yok.
Görsel ek kabulü: yenileme sonrası ders yüklendi. Başlangıç Check8/9 fail ve gerçek kanıt yok. Çözümü göster/Tezgaha al/Kontrol12/12 geçti; UI kanıtı temel-cok-basli-1793368131194.json. Çalıştır dokuz kafa özetini, model farkını3.62e-7, ortak8 geçmiş konum farkını0 ve son konum farkını8.73 gösterdi; kabulfalse yalnız deneme etiketiyle bitti. UI Run kanıtı temel-cok-basli-calistir-1793368203143.json. Ayrı ilk görünür dosya görsel testi son devamda Work yerel tarayıcı erişimi kapalı bildirildiğinden yapılamadı; ilk3 dosya normal runner CLI Run ile doğrulandı, görsel kabul sayılmaz. Önceki derslerdeki görsel açıklar sürer.

Kapanış doğrulandı: yalnız kendi18800 test sunucusuna Ctrl+C gönderildi, süreç çıktı.
