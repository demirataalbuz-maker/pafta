# ai-saldiri-21 iyileştirme teslimi

Codex düzeltti; claude-opus denetimi bekleniyor. Puan verilmedi.

Değişenler: tracks/ai-saldiri/lessons/ai-saldiri-21-ai-ssrf.md; tracks/ai-saldiri/fixtures/ai-saldiri-21/{README.md,veri/ssrf-senaryolari.json,veri/http-akisi.txt}; sandbox/ai_gercek_ai_saldiri_21.py. engine/web davranışı değişmedi. Yeni indirme/kurulum veya commit/push yok.

Kapsam doğru korundu: bu ders iki temel görev ve bir birleşik gerçek görev içerir. İlk iki görevin HTTP/socket olayları gerçektir, varsayılan model fixture'dır; özel transport/DNS sınır vakaları kontrollü test verisidir. Üçüncü görev gerçekten yerel model çağırır. İlk tablo+NOT bu ayrımı, yalnız deneye ait loopback origin/portları ve statik test DNS kapsamını açıklar. Önceki model opt-in cümlesi yalnız eski adaptöre ait olacak şekilde düzeltildi; son gerçek görevin bu bayraktan bağımsız zorunlu model kanıtı istediği yazıldı.

Üç göreve mevcut setup korunarak hazirla() eklendi. İlk iki görev görünür sentetik JSON senaryolarını ve HTTP biçim dosyasını okur, sonra dinamik portlu gerçek örnek çalıştırır. Dosyalar elle yazılmış örnek, kaydedilmiş gerçek trafik değildir. Çalıştır ham veriyi ve sonucu gösterir. Örnek kopyası geçicidir ve sonraki çalıştırmada yenilenir; son görevin calisma/ai-saldiri-21/url-notu.txt kopyası ayrı ve kalıcıdır. Gizli testler dosyalardan bağımsızdır.

İş emrindeki üç starter dersin mevcut üç görevine uygulanmıştır; fazladan görev icat edilmedi. Birinci starter modeli iki kez çağırır; ikinci starter origin IP'sini alıp redirect hedefini yeniden doğrulamaz; üçüncü birleşik starter aynı iki kusurlu işlevi içerir ve gerçek Run yoluna bağlanır. Hepsi reddedilir. İlk iki starter Run çıktısı gerçek loopback HTTP ve sunucu olaylarını gösterir.

İlk mutasyonda 32 değişimden üçü geçti; mutasyon-ilk.log korundu. Ham Location'ın başındaki boşluğu urljoin normalleştirmeden reddeden eksik vaka eklendi; TAB/LF/CR başları ve ikinci bağlantı açılmaması da sınanır. Aynı DEL değeri hem ham Location hem yeni URL kontrolünde denetlendiği için bazı değişimler sonuçta maskeleniyordu. Referans çözümde DEL/ASCII dışı karakterler bağlantıdan önce mevcut yeni-URL kontrolünde reddedilir; ham boşluk/kontrol ise normalleştirmeden önce durur. Önceki DEL/128, DNS, origin/port, redirect durum sınıfı ve hop sayısı testleri korunur. Geçerli trafik davranışı ve engellenen bağlantı kümesi korunur; doğru test zayıflatılmadı.

İki mevcut örnek çözüm aynı davranışla zincir_ref/getir_ref adlarıyla ders modülüne çıkarıldı; canlı deney bu referansları çağırmaz. Bunlar açık kopya sondası için gerçek referanslardır. Son test kod_denetimi, ImportFrom takma ad/yıldız ve kanit_yaz korumasını sözleşmelerden önce uygular; ihlalde stop(). Mevcut ok/eq/raises kayıtları sonuç listesine eklenir, özgün karşılaştırma/istisna semantiği korunur. Saf/temel testler başarısızsa gerçek deneye geçilmez. Kanıt kabulü bütün temel ve gerçek kontrollerin all sonucudur. Gerçek model istemleri, tohum/sıcaklık/token ayarları, transport containment ve olay ölçümü değiştirilmedi.

Dört kontrol .ai-venv/Scripts/python.exe -X utf8 ile:
- tools/validate.py ai-saldiri-21: TEMİZ, yedi kontrol (bir tahmin, üç çözüm, üç başlangıç), gerçek model ve HTTP dahil. PAFTA_DATA Desktop/pafta-s21-son-kontrol-20261030.
- docs/denetim/araclar/tahmin.py . ai-saldiri-21: bir tahmin, sıfır şüpheli.
- kirp_gercek.py Desktop/pafta-mutasyon-s21-v2-20261030; kopyadaki mutasyon.py <kopya> --en-cok 1000 ai-saldiri-21: 1+28=29 mutant, sıfır geçen.
- kopya_sonda.py ai-saldiri ai-saldiri-21 "from sandbox.ai_gercek_ai_saldiri_21 import zincir_ref as modelden_araca, getir_ref as guvenli_getir": fail, korunuyor. kopya-sonucu.json hedeflenen Kendi model zincirini guard mesajını ve kabul kanıtı yokluğunu ayrıca doğrular.

Ek olumsuz kontroller olumsuz-bos.json, olumsuz-sabit.json, olumsuz-fazladan-hop.json, olumsuz-location-bosluk.json ve eksik-model.json: hepsi fail, kabul yok. Model yokluğu testinde yalnız kendi süreç ortamında erişilemeyen loopback portu/var olmayan exe kullanıldı; kayıt GercekLabYok hatasını içerir. Kalicilik.json kendi Desktop/pafta-s21-kalici-20261030 kopyasına eklenen notun yeniden açılınca korunduğunu doğrular. Kaynak web/data dosyası ve kullanıcı verisi değiştirilmedi.

Gerçek CLI kanıtı Desktop/pafta-s21-son-kontrol-20261030/ai-kanit/saldiri-21-ssrf-1793354354923.json: doğrudan HTTP/DNS kontrolleri, üç gerçek model zinciri, meşru public okuma, korumalı iç istek yokluğu, kendi HTTP sunucularının kapanışı, model kaynak temizliği ve cihaz kontrolü yedi/yedi doğru. Üç model kolunda (temiz/korumasız/korumalı) canary artışı sıfır; model bu koşuda public /ok URL'sini seçti. Bu, model saldırısının başarılı olduğu iddiası değildir. Ayrı doğrudan korumasız /start kontrolü gerçek redirect ile kendi internal canary'sine bir istek ulaştırdı; korumalı testler bunu bağlantıdan önce durdurdu. Kontrollü DNS değişimi gerçek internet DNS saldırısı diye sunulmaz.

Görünür dosyalar normal runner/setup/Run yolunda iki temel görevde ok: gorunur-dosya-run-1/2.json. Mevcut izole 18800 test sunucusunda normal token/Origin HTTP akışı son denemede Kontrol pass (121 kontrol, gerçek kabul), Run ok (gerçek model/HTTP, kabul=false): http-check.json/http-run.json. Önceki aynı son kaynak denemesinde gerçek yerel HTTP timeout oluştu, kabul ve kanıt yoktu; http-check-timeout.json korundu. Mutasyon taraması bittikten sonraki tekrar geçti; eşzamanlı yük yalnız olası etkendir, kök neden çözülmüş veya kararlılık kanıtlanmış sayılmaz.

CLI/HTTP görsel ders ekranı kabulü yerine sayılmaz. Work tarayıcı erişimi son denemede kapalı bildirildi; görsel kabul YAPILMADI ve denetçiye açık eksiktir. Kullanıcının mevcut sunucusu/Ollama/WSL/Docker süreçleri kapatılmadı; yalnız laboratuvarın kendi servisleri kapanır.
