# ai-guvence-23: indirme onayı bekleniyor

30 Ekim 2026. Kullanıcının açık talimatı: ai-guvence-23'e sıra gelince panoya soru yazıp dur. İş emri Codex üzerinde, ders/lab dosyaları bu emirde henüz değiştirilmedi. Mevcut CPU fake-quant görevi gerçek autograd kullanıyor; gerçek GGUF/LLM nicemleme karşılaştırmasının yerine geçtiği iddia edilemez. Bu kapsam farkı kapatılmadan teslim veya A notu yok.

## Önerilen tek yeni indirme

| Alan | Somut öneri |
|---|---|
| Model/sürüm | qwen3:4b-instruct-2507-q8_0 (Qwen3 4B Instruct 2507, Q8_0) |
| Resmî kaynak | https://ollama.com/library/qwen3:4b-instruct-2507-q8_0 |
| Kayıt özeti | Resmî sayfada aa7252f68dda, 4.02B, Q8_0 |
| Yaklaşık indirme/ek disk | 4.3 GB; model dosyası boyutu VRAM kullanımı değildir |
| Lisans/ücret | Resmî sayfada Apache License 2.0; ücretsiz yerel model, abonelik/ücretli API yok |
| Amaç | Aynı temel modelin mevcut Q4_K_M sürümüyle gerçek GGUF nicemleme seviyelerinde eşli inference ve güvenlik/yetenek regresyonu ölçümü |
| Mevcut eş | qwen3:4b-instruct-2507-q4_K_M kurulu; envanter digest 0edcdef34593..., yaklaşık 2.50 GB; tekrar indirilmez |
| Yeni kurulum | Paket veya uygulama kurulumu önerilmiyor; mevcut Ollama kullanılacak |
| Onay sonrası komut | ollama pull qwen3:4b-instruct-2507-q8_0 |

Bu komut ÇALIŞTIRILMADI; bu kayıt indirme onayı değildir. Kaynak/model boyutu/lisans resmî sayfadan salt okunur doğrulandı. Q8 modelinin gerçek VRAM kullanımı henüz ölçülmedi ve sığacağı garanti edilmedi. Modeller sırayla, sınırlı bağlam ve üretim tavanıyla çalıştırılır; gerçek RAM/VRAM ve hatalar kanıta yazılır. Kurulu model silinmez; kullanıcının sunucusu veya önceden yüklü modelleri kapatılmaz.

## Onay sonrası uygulama kapsamı

Mevcut küçük modelde fake-quant/autograd görevi dürüstçe ayrı öğrenme hedefi olarak kalır. Yanına aynı Qwen3 4B Instruct 2507 temel modelinin Q4_K_M/Q8_0 sürümlerini aynı sentetik görev, tohum ve ayarlarda karşılaştıran gerçek GGUF adımı eklenir. Q8 daha yüksek bitli karşılaştırma koludur; F16/FP32 referans diye sunulmaz. Gerçek modellerin metadatası, digest, nicemleme, sürüm, ham yanıt, token, gecikme ve cihaz kullanımı saklanır. Saldırı başarısı veya bir nicemlemenin daha güvenli çıkması geçme koşulu olmaz.

İlk kabul tasarımı: dört küçük sentetik aritmetik/canary vakası, iki model, iki eşleşmiş tekrar (16 çağrı); istek başına sınırlı çıkış. Bu örneklem genel güvenlik veya hizalama sertifikası değildir. Model çekilemez, yüklenemez veya çağrı başarısız olursa gerçek kabul verilmez. Mevcut öğrenci/veri ayarları korunur; kontroller ayrı PAFTA_DATA kullanır.

İş emrindeki tablo+NOT, görünür fixture/setup, kusurlu başlangıç, derin anlatım, çelişki ve kopya koruması maddelerinin hepsi tamamlanacak. Sonrasında validate TEMİZ, tahmin 0, mutasyon 0 geçen, gerçek referans kopyası reddi ve ders ekranı kabulü koşulacak. Codex puan yazmayacak; claude-opus denetleyecek.

Onay gelene kadar indirme/kurulum veya bu dersin uygulamasına başlanmaz; sıradaki derslere atlanmaz. Kullanıcı bu ders için özellikle durulmasını istedi.

## Onay ve indirme sonucu

Kullanıcı bu sohbette "İndirmeyi onaylıyorum" yanıtını verdi. 30 Ekim 2026 ollama pull başarıyla bitti; SHA256 doğrulandı. Yerel envanter: 4,280,418,281 byte, digest aa7252f68dda4d25dfffa65b3760af6d2c3231a140c0060c78d444686d98a374, GGUF/Q8_0. Mimari Q4 ile aynı: qwen3, 4,022,468,096 parametre, 36 blok, embedding 2560; sohbet şablonu aynı. Varsayılan parametre satırları yalnız sıra bakımından farklı, değerler aynı. Yeni paket/uygulama kurulmadı. Eski bekleme ifadeleri onay öncesi kayıt olarak korunmuştur.
