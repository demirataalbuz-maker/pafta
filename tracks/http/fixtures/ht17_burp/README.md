# HT17 · Gerçek Burp dışa aktarımı

27 Ekim 2026, Burp Suite Community Edition 2026.8, Kali WSL.

history.xml: Pafta yerel HTTP laboratuvarına Python http.client ile gerçek Burp Proxy üzerinden dört istek: 200, 403, 200, 401. Tarayıcı kullanılmış gibi sunulmaz.

repeater.xml: ilk History satırı Ctrl+R ile Repeater'a taşındı, Send ile tekrar gönderildi; gerçek 200 yanıtı Save item ile dışarı aktarıldı. Her iki kayıtta Base64 seçeneği açıktı. XML satır sonları LF yapıldı; kodlanmış HTTP baytları değiştirilmedi. İsteklerdeki sid yalnız bu geçici ders sunucusunun rastgele oturumudur, dış hizmet hesabı değildir; sunucu kapandığında geçersizdir.

Bu dosyaları okumak GUI tıklamalarının her öğrenci tarafından yapıldığını kanıtlamaz. Tekrar üretim: HT17'deki yerel sunucuyu başlat, Proxy/History/Repeater adımlarını uygula ve Save items/Save item çıktısını kendi işlevine ver. XML üretici adı ve zaman metni kriptografik kaynak doğrulaması değildir. Burp yerel arşivine kaydedilmiş bu çiftler gerçek ürünün dışa aktarımıdır; testlerde değiştirilen varyantlar ayrı sentetik negatif kontrollerdir.

Resmî kaynaklar:
- https://portswigger.net/burp/documentation/desktop/tools/message-editor (Save item: istek, yanıt ve metadata XML)
- https://portswigger.net/burp/documentation/desktop/tools/context-menu (Save items)
- https://portswigger.net/burp/documentation/desktop/tools/repeater

Dosya hash'leri ve dönüşüm ayrıntısı provenance.json içindedir.
