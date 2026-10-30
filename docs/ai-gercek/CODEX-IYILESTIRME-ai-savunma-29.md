# ai-savunma-29 iyileştirme teslimi

Codex kendi uygulama kontrollerini yaptı; bağımsız denetim ve puan claude-opus'a ait. Görsel kabul eksiktir; aşağıda açıkça belirtilir.

İş emri tamamlandı: ilk anlatımın başında gerçek araç/model, kullanılan temsil ve ölçüm sınırı tablosu + NOT; model çalıştırılmaz çelişkisi giderildi; yaklaşık815 sözcük anlatımda sürüm karşılaştırılabilirliği, vaka kimliği/kritiklik bütünlüğü, eşik eşitliği, boş paket ve dar canary detector sınırı açıklandı. Son görev tek gerçek Ollama modelini iki defender politika etiketiyle çalıştırır; model sürümü veya Git commit karşılaştırması değildir. Promptfoo/garak çalıştırıldığı iddia edilmez.

Görünür veri tracks/ai-savunma/fixtures/ai-savunma-29/README.md ve veri/surumler.json içinde. İlk üç görev mevcut ai_savunma_veri.hazirla setup'ıyla aynı dosyayı okur: kayıt doğrulama, regresyon bulma, yayın kapısı. Veri elle yazılmış sentetik örnektir; canlı çıktı değildir. Kaynak dosya editörle açılır, ders editöründe yüklenen kopya değiştirilip Run yapılabilir. Kopya geçicidir, her çalıştırmada yenilenir, kalıcılık yok. Gizli testler ayrı girdilerdir.

Starter1 bozuk bool alanlarını doğrulamak yerine dönüştürür; starter2 iyileşmeleri de regresyon sayar; starter3 zip ile satır eşler, kritik eşiği yok sayar ve eşitlikte kapıyı kapatır. Üçü Run'da çalışır ve Check'te reddedilir. Çözümler aynı dosyayı okuyup ham paket/sonuç yazdırır. Temel doğru testler ve referans çözümler korundu.

Gerçek deneydeki temel kabul hatası giderildi: önce v-injection sızıntısının mutlaka oluşması ve kapının kalması isteniyordu. Bu, kullanıcı kabul koşulundaki saldırı başarısını şart yapma yasağıyla çelişiyordu. Artık dört gerçek çağrının dolu ve hatasız olması, ham yanıttan canary sınıflandırmasının tutarlılığı ve öğrencinin raporunun bağımsız referansla aynı olması gerekir. Geçme/kalma/boş paket ve eşik senaryoları üçüncü görevin tüm deterministik sözleşme/mutant testleriyle finalde de sınanır. Gerçek model sızdırmazsa bu ölçülmüş sonuçtur; başarısız deney olarak etiketlenmez. Eksik/boş yanıt veya bağlantı hatası ise savunma başarısı sayılmaz.

sandbox/ai_gercek_ai_savunma_29.py mevcut istemler, tohumlar, sıcaklık0 ve120token ayarlarını korur. Ham baz/aday cevapları, girdiler, tohumlar, model metadata, sistem istemleri ve eşikler artık deney kanıtında saklanır; önce yalnız bool akış özeti vardı. Oturum sonu kaynak temizliği ve bellek bilgisi de kanıtta korunur. Referans kapı işlevi modüle kopya sondası için eklenmiştir. Yeni guard referans/ozet/kanit_yaz ve ImportFrom takma ad/yıldız importunu stop ile reddeder. Saf sözleşme hatasında gerçek deney/kanıt yazılmaz; kabul bütün kontrollerin all sonucudur. Genel engine/web veya ortak ortamlar değiştirilmedi.

Dört kontrol (.ai-venv/Scripts/python.exe -X utf8):
- tools/validate.py ai-savunma-29: TEMİZ9; tahmin1 çözüm4 starter4; PAFTA_DATA Desktop/pafta-v29-kontrol-20261030.
- docs/denetim/araclar/tahmin.py . ai-savunma-29: 1 tahmin, sıfır şüpheli.
- kirp_gercek.py Desktop/pafta-mutasyon-v29-20261030 (önce hedef yokluğu doğrulandı); kopyadaki mutasyon.py <kopya> --en-cok1000 ai-savunma-29: 5+15+25=45 mutant, sıfır geçen. İlk3 starter/solution/test/setup blokları son kaynakla aynı.
- kopya_sonda.py ai-savunma ai-savunma-29 "from sandbox.ai_gercek_ai_savunma_29 import referans as yayin_kapisi": fail korunuyor. kopya.json hedef guard mesajını ve kabul kanıtı yokluğunu ayrıca doğrular.

Ek kanıtlar outputs/iyilestirme-codex-ai-savunma-29: boş/sabit/yanlış-eşik çözümü fail, kabul yok; kopya.json ve eksik-model.json da fail/kabul yok. Model yokluğu yalnız kendi süreç ortamında erişilemeyen loopback portu ve olmayan exe ile sınandı, kullanıcı sunucusu kapatılmadı. gorunur-dosya-run-1/2/3.json normal runner/setup üzerinden görünür paketi ve sonuçları ok gösterir.

Gerçek CLI kanıtı Desktop/pafta-v29-kontrol-20261030/ai-kanit/savunma-regresyon-1793371941695.json: dört dolu gerçek yanıt, iki vaka. Bu koşuda baz her iki vakada canary sızdırmadı, aday her ikisinde sızdırdı: regresyon2/2, kritik1, oran1.0; kapı kaldi, nedenler regresyon_orani_asildi ve kritik_regresyon_asildi. Bu gözlem artık kabul şartı değildir. İkinci vakanın jailbreak etiketi olsa da ölçüm yalnız canary sızıntısıdır; bütün zararlı davranışlar değerlendirilmedi. Aynı modelin iki politikası, bütün model sürümleri veya güvenlik kategorileri için sonuç değildir.

Kendi127.0.0.1:18800 sunucumda normal token/Origin HTTP: http-check.json pass9/9 ve gerçek kabul; http-run.json ok ve gerçek kabulfalse. Ham yanıtlar deney kanıtındadır. CLI/HTTP görsel kabul yerine sayılmaz. CUA son denemede Work yerel tarayıcı erişimi kapalı bildirdi; bu dersin referans, başlangıç ve görünür dosya görsel kabulleri YAPILMADI, PASS sayılmadı. Denetçiye açık kabul eksikliğidir; önceki derslerin görsel başarısı bunun yerine geçmez.

Yalnız kendi18800 test sunucum kapatıldı. Kullanıcının Ollama/WSL/Docker süreçleri kapatılmadı; sahiplik kuralıyla yalnız bu oturumun yüklediği model boşaltılır. Yeni indirme/kurulum, commit/push ve puan yazımı yok.
