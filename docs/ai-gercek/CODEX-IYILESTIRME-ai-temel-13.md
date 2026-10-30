# ai-temel-13 iyileştirme teslimi

Codex kendi uygulama kontrollerini yaptı; bağımsız denetim ve puan claude-opus'a ait.

İş emri tamamlandı: ilk tablo/NOT, çalıştırılmaz çelişkisinin giderilmesi, görünür sentetik veri ve ilk üç görevde setup/hazirla, üç gerçekçi kusurlu starter, yaklaşık826 sözcük anlatım. document uygulamanın veri/kaynak rolüdür; Ollama API rolü değildir. Gerçek final system/user kurguları kullanır. FastAPI kurulduğu veya XML kaçışının tek başına güvenlik sağladığı iddia edilmez.

Görünür veri tracks/ai-temel/fixtures/ai-temel-13/baglam.json ve README. İlk görev mesajlar, ikinci talimat/belgeler, üçüncü denetim alanlarını aynı veri/baglam.json dosyasından okur. Dosya elle hazırlanmış sentetik örnektir, gerçek model kaydı değildir. Kaynak dosya editörle açılabilir; ders editöründe yüklenen kopya değiştirilerek Run denenebilir. Setup mevcut ai_temel_veri.hazirla ile her çalıştırmada yeni geçici kopya oluşturur; kalıcılık yok. Gizli testler ayrıdır.

Starter1 belgede SYSTEM sözcüğünü görünce veriyi talimat kanalına yükseltir; starter2 belgeleri system/guvenilir=True yapar; starter3 guvenilir=False sistem mesajını ihlal saymaz. Üçü Run'da çalışır ve Check'te reddedilir. Doğru çözümler aynı görünür veriyi ve sonucu gösterir. Temel testlere girdi değiştirmeme ve çıktı sözlüklerinin bağımsızlığı eklendi. Negatif olamayacak liste uzunluklarının gereksiz alt sınırları iki referans çözümden kaldırıldı; kabul edilen girdi kümesi değişmedi, doğru test zayıflatılmadı.

Gerçek final mevcut beş sentetik belgeyi iki kurgu ve iki tohumla20 kez çağırmayı korur. Birleşik yöntem belgeyi sistem metnine ekler; ayrık yöntem user mesajında kaçışlı belge ve sistemde veri kuralı kullanır. Kaçış sırası & sonra < sonra >. Her yöntem için ASR yalnız geçerli saldırı kayıtlarından, kontrol sızıntısı sayısı ayrı, fayda geçerli kayıtlarda numara koruma oranıdır. Bu fayda ölçütü özetin tamamının doğruluğu değildir. Hiç geçerli kayıt veya saldırı yoksa ilgili oran None olur.

Kabul güçlendirildi: önce her iki yöntemde en az bir yanıt yeterliydi; artık20 kayıt ve her yöntemde10 dolu/hatasız yanıt gerekir. Boş model yanıtı hata kaydıdır. Hata-ayrık oran hesabı altyapı eksikliğini kabul ettirmez. Öğrenci deney_ozeti işlevinde hata alanının None ya da str olması açıkça sınanır; boş kayıt kümesi de test edilir. İhlalde stop yapan kod_denetimi + AST takma ad/yıldız import koruması referans_kur, referans_ozet, kacis, fayda_referans, kanit_yaz kullanımını reddeder.

Gerçek deney çalışmamışsa kanıt yazılmaz. Gerçek deney çalışıp çağrı hatası olmuşsa ham kayıtlar kabul=false kanıtta korunur; kabul all(sonuclar) olarak kalır. Başarılı bulgu mesajı yalnız bütün kontroller geçtiğinde verilir. Module sandbox/ai_gercek_ai_temel_13.py gerçek deney kaydına belgelerin tam metnini ve her çağrının gerçek mesaj listesini ekler; önce yalnız belge kimliği/türü/anahtar saklanıyordu. Sızıntı olması veya olmaması kabul şartı değildir. Model/istemler/örnekleme ayarları değiştirilmedi.

Dört zorunlu kontrol (.ai-venv/Scripts/python.exe -X utf8):
- tools/validate.py ai-temel-13: ilk koşu ve son kanıt-koruma düzeltmesi sonrası tekrar TEMİZ9; tahmin1 çözüm4 starter4. Son izole PAFTA_DATA Desktop/pafta-t13-son-kontrol-20261030.
- docs/denetim/araclar/tahmin.py . ai-temel-13: 1 tahmin, sıfır şüpheli.
- kirp_gercek.py Desktop/pafta-mutasyon-t13-20261030 (önce yokluğu doğrulandı); kopyadaki mutasyon.py <kopya> --en-cok1000 ai-temel-13: 11+6+8=25 mutant, sıfır geçen. Son ilk3 starter/solution/test/setup blokları kopyayla aynı; sonraki kanıt koruma değişikliği yalnız final gerçek testtedir.
- kopya_sonda.py ai-temel ai-temel-13 "from sandbox.ai_gercek_ai_temel_13 import referans_kur as mesajlari_kur, referans_ozet as deney_ozeti": fail korunuyor. kopya.json hedef guard mesajını ve kabul kanıtı yokluğunu ayrıca doğrular.

Ek kanıtlar outputs/iyilestirme-codex-ai-temel-13: bos.json, sabit.json, kacissiz.json ve eksik-model.json fail, kabul yok. Kaçışsız sonda geri kalan doğru kodu koruyup belge kaçışını kaldırır. Model yokluğu yalnız kendi süreç ortamında erişilemeyen loopback portu ve olmayan exe ile sınandı. gorunur-dosya-run-1/2/3.json normal runner/setup yolunda ham sentetik veriyi ve sonucu ok gösterir.

Gerçek son CLI kanıtı Desktop/pafta-t13-son-kontrol-20261030/ai-kanit/temel-talimat-veri-1793379156225.json: Qwen3 4B Instruct2507 Q4_K_M,20 dolu gerçek yanıt, yöntem başına10, hata0. İki yöntemde de ASR0.0, kontrol sızıntısı0, numara koruma oranı1.0. Bu dar belge/model koşusunda ayrık yöntemin üstünlüğü gösterilmiş değildir; genel güvenlik veya tam özet doğruluğu çıkarılamaz. Tam belge/mesajlar, tohumlar, sıcaklık, ham yanıtlar, model digest/sürüm/bellek ve cihaz bilgisi kanıtta saklıdır. İlk CLI kanıtı temel-talimat-veri-1793372815459.json ayrıca korunur.

Kendi127.0.0.1:18800 sunucumda normal token/Origin HTTP: http-check.json pass12/12 ve gerçek kabul; http-run.json ok ve on gerçek çağrı/gerçek kabulfalse. Son kanıt-koruma düzeltmesi sonrası ayrıca CLI tekrar ve gerçek ders ekranı kontrolü yapıldı. Tarayıcı bağlantısının eski kimliği kullanılamadı; mevcut uygulama içi bağlantı envanterden seçilerek açıldı, herhangi bir erişim/Work ayarı değiştirilmedi.

Gerçek ders ekranında başlangıç Check7/9 fail ve kanıt yok görüldü. Çözümü göster→Tezgaha al→Kontrol12/12 geçti; UI kanıtı temel-talimat-veri-1793379215702.json.20 çağrı ve yöntem başına10 geçerli yanıt ekranda doğrulandı. Run ve görünür dosya UI sonuçları ek kayda yazılır. Önceki derslerin görsel açıkları bu dersin kabulüyle kapanmış sayılmaz.

Önceki mutasyon başlatma isteği otomatik onay incelemesi kullanım sınırına takıldığı için çalıştırılmamıştı. Kullanıcı devam dediğinde aynı işlem normal onay incelemesinden geçerek çalıştı; onay kontrolü atlanmadı. Bu eski engel test başarısı sayılmadı.

Yalnız kendi18800 test sunucum kapatıldı. Kullanıcının Ollama/WSL/Docker süreçleri kapatılmadı; ortak oturum sahiplik kuralları korunur. Genel engine/web değişikliği, yeni indirme/kurulum, commit/push veya puan yazımı yok.
Görsel ek kabulü: Çalıştır10 gerçek yanıtı ve yöntem başına ASR0/kontrolsızıntı0/numara koruma1.0/hata0 özetini gösterdi; kabulfalse yalnız deneme etiketiyle bitti. UI Run kanıtı temel-talimat-veri-calistir-1793379332817.json. İlk dosyalı görevin Run çıktısı ham sentetik bağlamı ve içindeki SYSTEM metnini yanlış yükselten starter davranışını gösterdi. Diğer iki temel görevin ayrı görsel kabulü yok; CLI Run/validate doğrulandı. Kendi18800 sunucusuna Ctrl+C gönderildi, süreç çıktı.
