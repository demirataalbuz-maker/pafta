# Yeni katılan AI için ortak çalışma ve öğretim rehberi

Kullanıcı kararı: 29 Ekim 2026. Bu rehber sonraki uygun örnek ve görevlerde uygulanır. Bir öneri veya tamamlandı raporu değildir. Mevcut bütün derslerin bu standarda geçirildiği iddia edilmez.

## 1. Amaç ve öncelik
PAFTA ücretsiz, yerel araçlarla çalışan, öğrencinin kendi bilgisayarında uygulama yaparak öğrendiği bir eğitimdir. AI tarafında temel kavramlar, hücum, savunma ve güvence birlikte öğretilir. Yalnız fonksiyon tarifini ezberleten veya hazır cevabı kabul eden görev yeterli değildir. Gerçek model/araç deneyleri ile anlaşılır, incelenebilir çalışma verileri birbirini tamamlar. Her örneğin model çalıştırması gerekmez; yapılan işin türü açıkça yazılır.

## 2. İşe başlamadan önce
Proje kökündeki AGENTS.md, bu rehber, docs/ai-gercek/AJAN-TALIMATI.md ve docs/ai-gercek-lab.md dosyalarını oku. Yerleşim planının konumu AGENTS.md içindedir. Ardından proje kökünde:
python -X utf8 tools/ai_pano.py acik
python -X utf8 tools/ai_pano.py oku -n 30
python -X utf8 tools/ai_ders_takip.py liste

Geçmiş sohbet, eski renk veya eski görev dağılımını güncel sahiplik sanma. Açık işe ve başka ajanın denetlediği derse müdahale etme. Boş dersi tracker üzerinden al; panoya basladi yaz. Kullanıcı yeni görevi açıkça vermedikçe başka ajana mesaj gönderme veya onun işini üstlenme. Pano ortak kayıt içindir. Bir engel varsa nedeni ve hangi aşamanın yapılmadığını yaz; test edilmemiş işi bitmiş gösterme.

## 3. Yeni örneklerde görünür çalışma dosyaları
Akış, log, belge, veri kümesi veya araç çıktısı işleyen uygun görevlerde öğrenci yalnız tarif görmemeli: açıp okuyabileceği, kopyası üzerinde değişiklik yapabileceği ham örnek dosya da bulmalı. Örneğin akis/openai_sse.txt bir önerilen göreli addır; şu an bütün derslerde mevcut olduğu anlamına gelmez.

Ders açıkça dosyanın nerede olduğunu, nasıl açılacağını, koddan nasıl okunacağını ve nasıl tekrar çalıştırılacağını anlatmalı. İlk adım ham veriyi inceletsin; sonraki adımlar uygunsa aynı veriyi ayrıştırma, yorumlama ve sonuç çıkarma üzerinden ilerlesin. Gereksiz yere her derse dosya dayatma. SSE için yorum satırı, boş satır, [DONE], boşluk farkları ve kesilmiş olay örnekleri görünür veride de bulunsun. Ollama NDJSON ile OpenAI uyumlu SSE aynı protokol gibi anlatılmasın.

Küçük okunabilir örnek + sınır durumları + beklenen davranış açıklaması sun. Öğrencinin yanlış örneği düzelterek veya sağlam örneği bozarak gözlem yapabilmesi hedeflenir. Dosya sunmak gerçek deneyin yerine geçmez.

## 4. Veri kökeni ve gerçeklik etiketi
Her örneği doğru adlandır:
- Sentetik örnek / fixture: eğitim için yazılmış veya kontrollü üretilmiş veri; canlı sunucu yanıtı değildir.
- Kaydedilmiş gerçek çıktı: gerçekten alınmış kayıt; kaynak araç/model sürümü, ilgili ayarlar, kayıt koşulları ve yapılan maskeleme belirtilir. Yeniden dosyadan okumak yeni bir canlı çağrı değildir.
- Canlı gerçek deney: görev çalışırken gerçek yerel araç/model çağrılır; sürüm, model kimliği, ayarlar, giriş, cihaz, gerçek sonuç ve hatalar kanıta yazılır.

Gerçek gibi görünen sentetik dosyayı gerçek sunucu kaydı diye sunma. Örnekler sentetik kimlikler ve canary kullansın; kişisel veri, gerçek sır veya kullanıcının özel dosyası eklenmesin. Ham veri sunulması sırları günlükte açık bırakma izni değildir.

## 5. Öğrenci dosyası, test verisi ve kalıcılık
Öğrencinin düzenlediği çalışma kopyası ile değerlendirmedeki görülmemiş test verisini ayır. Öğrenci örnek dosyayı değiştirerek gizli beklenen cevabı değiştirememeli. Test yalnız tek örneği ezberleyen çözümü kabul etmemeli.

Mevcut Python koşucusu her çalıştırmada geçici çalışma klasörü açar; bazı motorlar ortak dosyaları buraya kopyalar. Proje dizinine dosya eklemek tek başına öğrenciye dosya erişimi sağlamaz. Dosyanın ders ekranından erişimini, koşucuya aktarılmasını ve düzenlemelerin korunmasını gerçekten doğrula. Kalıcılık yoksa açıkça belirt; varmış gibi anlatma. Öğrenci değişikliklerini her çalıştırmada sessizce sıfırlama. Temiz başlangıca dönüş açık bir işlem olsun, kullanıcı verisini silmesin.

Cihaz/kullanıcı mutlak yolunu ders koduna gömme; göreli çalışma yolları kullan. Yol geçişini engelle, kodlama ve satır sonlarını öğretim amacına göre koru. SSE boşluklarını veya CR/LF farklarını yanlışlıkla normalize etme. Dosyalar izole çalışma alanında kalsın. Ortak engine/web değişikliği gerekiyorsa mevcut onay kapsamını kontrol et, ortak dosyayı panoda sahiplen, dar değişiklik yap. Bu rehber platformda dosya editörünün zaten bulunduğunu veya tüm altyapının tamamlandığını söylemez.

## 6. Gerçek deney ve kabul
motor: ai-gercek adımları gerçek araç/model gerektirir. Bağımlılık yokluğu, çağrı hatası veya yapılmamış kabul PASS değildir. Gerçek kanıt kaydı gerekir; fixture kanıtını gerçek diye etiketleme. Referans çözüm geçmeli; boş, sabit cevap ve anlamlı yanlış çözümler reddedilmeli. Görünür dosya dışında farklı geçerli ve bozuk girdilerle sınama yap.

Rastgele model yanıtını sabit bir cümleyle karşılaştırma. Saldırının başarılı olmasını geçme şartı yapma; deneyin doğru yürütülmesini ve ölçümün doğruluğunu denetle. Canary sızıntısı ölçümü bütün jailbreak yeteneklerinin kanıtı değildir. CLI kabulü yanında ders ekranında Kontrol/Çalıştır akışını ve görünür dosyaya erişimi doğrula; uygun regresyonu çalıştır. Eksik kalanları ayrı yaz.

## 7. Ortak kaynaklar ve izinler
Ders ortamı .ai-venv ile araç ortamı .ai-araclar ayrıdır; gelişigüzel paket/sürüm değiştirme. Aynı ortama eşzamanlı kurulum yapma. Kullanıcının önceki kurulum onaylarını kontrol et; aynı onayı yeniden isteme. Yeni kapsam için kaynak/sürüm/boyut/amaç bilgisi gerekir; ücretli abonelik açma. Paylaşılan model/GPU kullanımında panoya bak; denetçi çalışırken ağır testleri koordine et.

Yalnız kendi başlattığın süreçleri kapat. Kullanıcının Ollama sunucusunu, önceden yüklediği modeli, WSL veya Docker Desktop'ı kapatma. Öğrenci verisini/kurulumlarını silme. Ana PAFTA ile AI'yi birleştirmek, ortak giriş ve kapsamlı kaynak yöneticisi bu kararın parçası değildir. Commit/push için kullanıcı yetkisi gerekir.

## 8. Durum, kanıt ve devir
Pano kayıtları tools/ai_pano.py ile yazılır; pano.json veya üretilmiş PANO.html elle düzenlenmez. Kalıcı pano metni üretici araçta yaşar. Ders sahipliği ve kabul durumu tools/ai_ders_takip.py ile yönetilir.

Kendi doğrulaman sonrası tracker: denetime-hazir. Tracker bitti durumunu yalnız bağımsız denetçi verir; kendi testine bağımsız denetim deme. Panodaki bitti iş kaydını kapatır; dersin bağımsız denetimden geçtiği anlamına gelmez.

Devir notunda ders kimliği, değişen dosyalar, görünür veri yolu/kökeni, çalıştırılan komutlar, gerçek sonuç/kanıt yolları, yanlış çözüm kontrolleri, arayüz ve regresyon sonucu, kalan sorunlar bulunsun. Sonraki ajan belgelere ve güncel panoya bakarak devam edebilmeli.

## 9. Mevcut dersler için kapsam
Bu karar ileriye dönük öğretim standardıdır. Eski derslere topluca dönüşüm bu kayıtla tamamlanmış sayılmaz. Eski bir ders ele alındığında görünür veri ihtiyacı değerlendirilir; eksikse somut dosya/arayüz işi olarak kaydedilir. Başka ajanın dersini sessizce yeniden yazma. Ders sayısı, model sürümü ve açık işler değişebilir; güncel kaynak tracker, pano ve gerçek dosyalardır.
