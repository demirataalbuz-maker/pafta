# Kutu 28 — ai-saldiri-04 uygulayıcı kabulü

Bağımsız denetim değildir. 29 Ekim 2026. Kullanıcı 28 numaralı kutuyu açıkça Codex'e verdi; eski engelli Claude kaydı bu talimatla devralındı.

## Değişen dosyalar
- tracks/ai-saldiri/lessons/ai-saldiri-04-jailbreak-taksonomisi.md: eski 8 adım korunur; görünür dosya anlatımı ve gerçek görev (index 9) eklendi.
- sandbox/ai_gercek_ai_saldiri_04.py: kalıcı öğrenci dosyası, bağımsız dosya/metrik sözleşmeleri, ortak GPU/CPU ayarına uyan Ollama oturumu ve gerçek sınıflandırma.
- web/data/ai-saldiri-04-vakalar.jsonl ve aynı içeriğin .txt görünümü: elle etiketli altı sentetik ve zararsız vaka. Tarayıcı JSONL uzantısını indirme olarak ele aldığı için okunabilir text/plain görünümü sunulur. İki dosyanın byte eşitliği doğrulandı.
- Ortak engine/server/web uygulama kodu değiştirilmedi; yeni statik veri dosyaları eklendi. Kurulum, commit/push yok.

## Öğrencinin yaptığı iş
Önceki üç işlevi ve yeni JSONL dosya okuyucusunu yazar. Çalıştır ilk kullanımda öğrenci veri alanı/calisma/ai-saldiri-04/vakalar.jsonl dosyasını oluşturur, tam yolunu ve ham içeriğini gösterir. Dosya dış editörden veya Python ile düzenlenebilir; sonraki çalıştırmada üzerine yazılmaz. Bu sürümde uygulama içinde ayrı dosya editörü yoktur. Öğrenci veri alanı değişirse farklı kopya kullanılır.

Sinyal çıkarma, çok etiketli kurallar ve precision/recall/F1 hesapları gerçek yerel model sınıflandırmasıyla karşılaştırılır. Model vaka talimatlarını uygulayan saldırı hedefi olarak kullanılmaz. Bu deney jailbreak başarısını ölçmez; taksonomi sınıflandırmasının kalitesini ölçer. Yeni jailbreak veya zararlı yük üretilmedi.

Modelin düşük puanı kabulü bozmaz. Gerçek yanıt eksikliği, geçersiz JSON/etiket veya yarım üretim ise başarısızlıktır. Her ham model yanıtı, gerçek istek/ayar, sürüm/model/digest, cihaz, bellek ve sahipli sunucu kapanışı kaydedilir. Model CPU'ya zorlanır; kullanıcının sunucusu kapatılmaz veya modeli boşaltılmaz.

## Kabul ve gerçek bulgular
- İlk hedef ders doğrulaması: python -X utf8 tools/validate.py --yol ai-saldiri ai-saldiri-04 — 1 ders / 10 kontrol TEMİZ.
- kabul.py / summary.json: 10/10 senaryo doğru; referans PASS; starter/boş/sabit cevap + tek-etiket, None yerine sıfır, dosyanın ilk satırını okuma, bilinmeyen etiketi yok sayma mutantları FAIL. Çalıştır OK ve kabul=false; eksik Ollama FAIL, kabul kanıtı yok.
- file-contract.json: çalışma kopyası değişikliği korunur, kaynak şablon değişmez. Bu kontrol fixture dosyası kontrolüdür, canlı model kanıtı değildir.
- Son ders ekranı Kontrol: 60/60 PASS; ui-data/ai-kanit/saldiri-04-taksonomi-1793259933330.json. Başlangıç kodu 7/17 ile reddedildi, gerçek kanıt oluşmadı.
- CLI referans koşusunda model Qwen3 4B Instruct Q4_K_M; 6 canlı sınıflandırma. Kurallı sınıflandırıcı F1: tüm sınıflarda 1. Model F1: bağlam 0.667, doğrudan 0.5, dönüştürme 0.667, politika çatışması 0.5. Bunlar yalnız bu küçük sentetik setin bulgularıdır; model güvenliğinin genel puanı değildir.
- Ham .txt dosyası tarayıcıda altı JSONL satırıyla açıldı. Ayrı öğrenci kopyası başlangıç şablonundan ayrıdır. Gizli kabul verisi geçici dosyada yeni kimlik/metin varyantlarıyla sınanır; öğrenci dosyasını değiştirmek beklenen cevabı değiştirmez.

## Regresyon ve kalan kapsam
Tam ai-saldiri regresyon sonucu tamamlandığında ayrıca kaydedilecek. Kendi kontrolü bitti diye tracker bitti yapılmaz; bağımsız denetim gerekir. Windows masaüstü/başka cihaz kabulü yapılmadı; yalnız mevcut bilgisayar denendi.


## Son sürüm: ortak GPU ayarına uyum ve regresyon

Çalışma sırasında ortak OzelCpuOturumu sınıfı varsayılan GPU kipine geçirildi. İlk CPU kabulünün ardından eski sahipli_sunucu_kapandi koşulu artık ortak sunucuda geçerli olmadığı için bir Çalıştır kaydında false görüldü; o kayıt yeni sürüm kabulü sayılmadı (ui-data/ai-kanit/saldiri-04-taksonomi-1793259996306.json).

04 güncel lab.ollama_secenekleri / cihaz_dogrulandi / kaynak_temizlendi yardımcılarına uyarlandı. GPU çağrıları makine genelinde sıraya girer; CPU seçeneği korunur. Son referans kanıtı summary.json/reference.json üzerinden bulunur: GPU kipi, toplam ve VRAM 2.876.160.081 bayt, model_bosaltildi=true, bütün gerçek kontroller true. Bu yalnız deneyin yüklediği modelin boşaltılmasıdır; kullanıcı sunucusu kapatılmadı.

Son ders ekranı Kontrol yeniden 60/60 PASS: ui-data/ai-kanit/saldiri-04-taksonomi-1793260211787.json. Son GPU sürümünde kabul.py tekrarlandı: 10/10. Eksik bağımlılık kontrolünde yalnız olmayan exe ayarlamanın çalışan sunucu varken eksik bağımlılık yaratmadığı görüldü; test kapalı loopback portu + olmayan exe ile izole edildi. Hatalı test kurulumu summary-before-dependency-fixture-fix.json olarak saklandı; uygulama hatası diye sunulmadı.

persistence-cross-process.json: mutlak ve göreli PAFTA_DATA için iki ayrı süreç, iki ayrı geçici çalışma dizininde aynı mutlak öğrenci dosyası kullanıldı; düzenleme korundu. Göreli veri kökü proje köküne göre sabitlenir; geçici koşucu dizinine taşınmaz. Başlangıç dosyası üzerine yazılmaz.

validate-regresyon-final.log: 34 ders / 264 kontrolde 263 geçti. Yalnız ai-saldiri-07:8 gerçek deney, yeni GPU politikasından önceki özel sunucu zorunluluğu yüzünden başarısız. 28/04 ve diğer kontroller geçti. 07 başka ajanın dersi; koduna dokunulmadan ortak panoya uyarı yazıldı. Tam yol TEMİZ olarak sunulmaz. İlk geçiş koşusu validate-regresyon.log (04+07 uyumsuzluğu) da korunur.

Bağımsız denetim henüz yapılmadı; tracker denetime-hazir kullanılır. Yeni kurulum veya commit/push yok.

Son UI Çalıştır: ui-data/ai-kanit/saldiri-04-taksonomi-1793260331470.json; kaynak=gercek, kabul=false (yalnız deneme), bütün deney kontrolleri true. Öğrenci dosyası mutlak kalıcı yolda gösterildi; ham sentetik satırlar ve canlı model JSON yanıtları ayrı yazıldı.
