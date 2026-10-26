# A notu · uygulama ve kabul planı

Hedef: 104 maddenin her birinde en az 90/100; gerçek kapsam ve test kanıtı. Kullanıcı 26 Ekim 2026 tarihinde bütün maddeleri A düzeyine yükseltmeyi istedi.

Puan yükseltmek tek başına tamamlanma değildir. Eksikler ders/görev/tezgâh değişikliğiyle kapanır; çalışan çözüm, reddedilen yanlış çözümler ve gerçek araç çıktısı kaydedilir. Codex öz değerlendirmesi bağımsız denetimden ayrı gösterilir. Paket/ürün indirme önceki izin kuralına tabidir.

## Çalışma sırası

| No | Yol | Bugünkü puan | Kalan iş / yeniden kabul | Durum |
|---|---|---|---|---|
| 1 | python | 86 | Kapanan bulgular ve puan ölçütlerini mevcut ders/gerçek kabul kanıtıyla yeniden değerlendir. | bekliyor |
| 3 | python | 80 | Gizli alanı ve form girdilerini HTML ağacından çıkarma (ASAMA2 'neden') yalnız anlatımda; görev yok.; Bağlantı hedeflerini (href) toplayan görev yok. | tamam: P74, 29 kontrol temiz; 17 anlamsal mutant reddedildi |
| 7 | python | 77 | Hazır örnek betiğin komut satırı seçeneklerini okumak yalnız ipucunda; görev yok.; Bağımlılık sorunu (eksik/uyuşmaz paket) hiç yok (ASAMA2 'neden'). | tamam: P78/P79, 17 kontrol temiz; 14 anlamsal mutant reddedildi |
| 8 | bash | 83 | ASAMA2 ve dersin özeti 'jq -e' diyor; derste hiç kullanılmıyor. | tamam: BS29, 13 kontrol temiz; tahmin doğrulandı, 10 mutant reddedildi |
| 9 | bash | 88 | journalctl -o json yalnız tabloda; görevde yok. | tamam: BS31, 17 kontrol temiz; 9 mutant reddedildi |
| 11 | bash | 86 | sftp yalnız anlatıda. | tamam: BS34/BS35, 17 kontrol temiz; gerçek SFTP ve 8 mutant reddedildi |
| 12 | bash | 85 | teardown yalnız tabloda (ASAMA2 setup/teardown).; Git Bash ile Linux farkları kayıtlı değil (ASAMA2 istiyor). | bekliyor |
| 13 | powershell | 78 | Yönlendirme (-MaximumRedirection, 3xx) yok.; Form gövdesi (-Form) yok.; Timeout yalnız tabloda; sınanmıyor. | bekliyor |
| 14 | powershell | 87 | FilterXml hiç yok (ASAMA2 FilterXPath/FilterXml).; ToXml() yalnız tabloda; ham XML'den alan okunmuyor. | bekliyor |
| 15 | powershell | 77 | Gerçek erişim karşılaştırması yok (Deny sonrası okuma denemesi, UnauthorizedAccess). | bekliyor |
| 18 | powershell | 73 | Ayrılmış Windows lab ucu, WinRM ve -ComputerName yok (ASAMA2 istiyor).; Hata ve temizlik akışı (try/finally, Broken durumu, sızan oturum) yok. | bekliyor |
| 19 | powershell | 83 | AppLocker olayları elle yazılmış XML; gerçek EVTX yok (ps_evtx_fixtures.py kullanılmamış).; JEA görevleri gerçek .psrc/.pssc okumuyor. | bekliyor |
| 21 | cmd | 85 | Erişim reddi (korunan anahtar ya da servis) sınanmıyor. | bekliyor |
| 22 | cmd | 79 | DENY ACE'li dosyanın okunamadığı gösterilmiyor. | bekliyor |
| 23 | cmd | 92 | CM25:4'te iki ölü kod satırı.; Araçlar .deps'te değil; kurulum betiği yok. | bekliyor |
| 24 | http | 76 | Burp kullanımına dair otomatik tanık yok (Burp'ten dışa aktarılan istek/yanıtı ayrıştırmak gibi). | bekliyor |
| 26 | http | 94 | SameSite gerçek tarayıcıda yalnız tahminde; görevler Python istemcisiyle. | bekliyor |
| 31 | sql | 82 | MySQL ve SQL Server için sürümü sabit yerel servis yok (ASAMA2 istiyor); TOP yalnız anlatıda. | bekliyor |
| 32 | sql | 79 | Uygulama tarafında gerçek parametre bağlama (Python sqlite3 ile ? ve execute) görevde yok.; Java/PHP/C# güvenli sorgu derslerine köprü yok. | bekliyor |
| 34 | sql | 80 | PostgreSQL jsonb görevi yok; projede gerçek PostgreSQL varken yalnız tabloda. | bekliyor |
| 35 | kql | 79 | Gerçek Sentinel/Kusto'da hiç çalıştırılmadı (abonelik gerekiyor); yerel çeviri motorunda. | bekliyor |
| 36 | kql | 76 | OutputSchema ve tür uyuşmazlığı testleri yok (ASAMA2 istiyor).; Gerçek Kusto bağlantısında görev yok. | bekliyor |
| 37 | kql | 83 | Gerçek Sentinel'de kural önizlemesi yok (abonelik).; Entity mapping yalnız anılıyor; görevde yok. | bekliyor |
| 39 | spl | 82 | ASAMA2 Authentication/Endpoint istiyor; ders Web modelini kullanıyor.; CIM eklentisinin kurulumu otomatik değil. | bekliyor |
| 41 | elastic | 88 | Elastic Agent yok; ajan tabanlı alım öğretilmiyor. | bekliyor |
| 42 | elastic | 86 | Kapanan bulgular ve puan ölçütlerini mevcut ders/gerçek kabul kanıtıyla yeniden değerlendir. | bekliyor |
| 43 | elastic | 93 | Görevler kuralı önizlemeyle ölçüyor; etkin zamanlayıcı yalnız kabul betiğinde. | bekliyor |
| 44 | elastic | 90 | DISSECT/GROK ile metin ayrıştırma (ASAMA2 istemiyor; CDSA'da işe yarar). | bekliyor |
| 45 | sigma | 75 | sigma-cli hiç kullanılmıyor (madde adında var).; Yalnız Splunk; Elastic ve Kusto backend'i yok. | bekliyor |
| 46 | sigma | 79 | Zamansal korelasyon (temporal / temporal_ordered) hiç yok. | bekliyor |
| 47 | sigma | 74 | Gerçek EVTX/XML yok; olaylar sentetik JSON.; PS27/PS21'deki olay okuma bilgisine köprü yok. | bekliyor |
| 48 | sigma | 80 | re ve fieldref görevde yok.; utf16le/utf16be ayrı görevde yok. | bekliyor |
| 49 | yara | 78 | Gerçek derleyici çıktısı (MinGW 32/64) yok; örnekler Python'da sentezleniyor. Projede ctypes_lab ile derleme artık mümkün.; pe.is_32bit/is_64bit/machine görevde yok; bozuk başlık tanığı zayıf. | bekliyor |
| 53 | regex | 91 | Motorlar arası eşleşme aralığı (başlangıç/bitiş) karşılaştırması yok. | bekliyor |
| 55 | packets | 93 | if_tsresol (zaman çözünürlüğü) görevde sınanmıyor. | bekliyor |
| 57 | packets | 96 | tcp.analysis.lost_segment görevde yok. | bekliyor |
| 58 | packets | 95 | tshark -G fields ile sürüm alan listesi doğrulaması yok. | bekliyor |
| 59 | packets | 94 | Süreye göre döndürme (-G / -b duration) yok. | bekliyor |
| 60 | ad | 78 | Gerçek grafik verisini okuyan görev yok (ASAMA2 'gerçek grafikte sonucu kontrol eden okuma'). | bekliyor |
| 62 | ad | 95 | AD21:2'de -band 2 → -band 3 mutantı geçiyor; canlı şablonun bit değeri ikisini ayırt ettirmiyor (gizli zayıflık). | bekliyor |
| 63 | ad | 92 | Windows ldp.exe GUI aracı, otomatik sınanamaz (yalnız anılıyor); çekirdek davranış gerçek bağlantıda ölçüldüğü için not. | bekliyor |
| 69 | csharp | 86 | Kapanan bulgular ve puan ölçütlerini mevcut ders/gerçek kabul kanıtıyla yeniden değerlendir. | bekliyor |
| 72 | csharp | 88 | Kapanan bulgular ve puan ölçütlerini mevcut ders/gerçek kabul kanıtıyla yeniden değerlendir. | bekliyor |
| 83 | javascript | 85 | Kapanan bulgular ve puan ölçütlerini mevcut ders/gerçek kabul kanıtıyla yeniden değerlendir. | bekliyor |
| 92 | purple | — | Kapanan bulgular ve puan ölçütlerini mevcut ders/gerçek kabul kanıtıyla yeniden değerlendir. | bekliyor |
| 93 | purple | 84 | pu02:7 kanit_yolu guard'ları (@37/40/41) ve bütünlük kontrolü (@59 size≠ VEYA hash≠) or→and yaşıyor; pu02:6 de ×2. Güvenlik-kritik; her guard'ı ve 'size ok ama hash yanlış' vakasını pinle. | bekliyor |
| 95 | purple | 85 | pu10:3/4 sınır (<=→<) ve bir mantık (==→!= @49) mutantı yaşıyor; eşik komşularını ve eşitlik kararını pinle. | bekliyor |
| 96 | ids | 83 | id01/02/03/05'te eşik/pencere sayıları (1→2, 60→61, 5→6) mutasyonda yaşıyor (10 geçen); eşik sınır testleri ekle. | bekliyor |
| 98 | purple | 88 | pu06:3 geçiş kapısı eşiği (<=→<, 25→26) mutasyonda yaşıyor; eşik sınırını pinle. | bekliyor |
| 101 | purple | 85 | pu12:4/5 and→or / or→and (@9/27/40) ve sınır (<→<=) mutantları yaşıyor; mantık ve eşik kararlarını pinle. | bekliyor |
| 104 | bitirme | 87 | bt05:2 (<=→<) ve bt06:3 (or→and @4, 25→26 @5) mutantları yaşıyor; kabul kapısı eşik/mantığını pinle. | bekliyor |

## Bağımlılık sınırları

Gerçek Sentinel/Defender aboneliği ve hizmet hesabı, SQL Server/MySQL yerel servisleri, Elastic Agent ve ek Sigma backend bağımlılıkları mevcut kurulumdan doğrulanacak. Eksik ürün/paket onaysız kurulmayacak. Kimi’nin pu13–pu17 yazımına ait dosyalar kontrol edilmeden değiştirilmez.
