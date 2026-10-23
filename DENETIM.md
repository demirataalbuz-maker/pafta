# Pafta · Denetim

Son denetim: 2026-10-21, `44dd8d8`: 391 ders, 3372 kontrol temiz, hem normal Windows ortamında hem Git Bash'ten. Elastic yazma yolu (`777a9b9`, `0d9dbc9`) denetlendi, bulgu yok. AD'nin bütün bulguları kapandı (`44dd8d8`, `a492264`). Assembly düzeltmeleri (`263cf8c`) ölçüldü, A23–A26 kapandı; Antigravity'nin rapor güvenilirliği A28 açık.

Bir madde yazarın raporuyla değil, denetçinin kendi betikleri yeniden koşturulunca kapanmış sayılır.

## Ölçümler

| Kontrol | Yöntem | Sonuç |
|---|---|---|
| Görevler çalışıyor mu | `tools/validate.py` | 271 ders, **2533 kontrol temiz** |
| Tahmin açıklamaları | Her tahmin kodu çalıştırıldı; çıktının her satırı açıklamada geçiyor mu | 340 tahminin hepsi uyuşuyor; tahmin adımı olmayan ders kalmadı (Sigma/YARA dahil) |
| "Beklenen çıktı" blokları | Örnek çözüm çalıştırılıp blokla karşılaştırıldı | 78 bloğun hepsi doğru (4 bilinen yanlış alarm: `...` ile kısaltılmış ya da fonksiyonun dönüş değeri) |
| Testler yanlış cevabı yakalıyor mu | **Mutasyon testi:** her örnek çözüm küçük hatalarla bozuldu (sınır kaydırma, artan↔azalan, AND↔OR, LIMIT+1, değiştirici silme...) | **696 görevde 0 zayıf test.** 5 işaretin hepsi sonucu değiştirmeyen zararsız mutasyon: p20:6, p48:5, p59:5, p59:6, p68:5 |
| Ders sırası ve rütbeler | Kimlikler harita sırasıyla uyuşuyor mu, 6 rütbe dolu mu | **12 yolun hepsi sıralı ve 6 rütbeli** |
| Dersler arası atıflar | "SP13'te", "(P05)" gibi her atıf var olan bir derse, doğru konuya gidiyor mu | **234 atıf, 0 kırık**; yeniden numaralandırma atıfları doğru çevirmiş (eski metinle karşılaştırıldı). Bir eski, yanlış adresli atıf var (A3). |
| Uygulama | Önizlemede SP17 ve çift ters tırnaklı kod | doğru görünüyor |

Sigma ve YARA ders metinleri tek tek okunmadı, yalnızca betiklerle denetlendi.

## Açık bulgular

| # | Yer | Bulgu | Düzeltme | Sahibi |
|---|---|---|---|---|
| A32 | `tracks/php/lessons/ph02` (tahmin, `gercek` çiti) | Gerçek PHP çıktısının ilk satırı `web01 db01 ` (sonda boşluk), `gercek` çitinde boşluk yok; dersin açıklaması "sonunda bir boşluk" diyor. Tahmin karşılaştırması satır sonu boşluklarını kırptığı için puanlama etkilenmiyor (bulut denetçi ve denetçi PHP 8.3/8.4 ile ölçtü). | çite boşluğu ekle; ders kendi açıklamasıyla tutarlı olsun | Yazar 1 |
| A33 | `tracks/c/lessons/c13` (tahmin) | `uint8_t` dizisini `(const Baslik *)` ile okumak katı takma ad kuralını çiğner (C11 6.5p7): tanımsız davranış. Ölçülen çıktı altı derleme biçiminde aynı (`1 2 12`), ama dersin NOT kutusu bunu yalnızca "tartışmalı" diye anıyor. | NOT'ta açıkça "tanımsız davranış" de ve doğru yolu (`memcpy` ile yapıya kopyalamak) göster | Yazar 1 |

**AD yolu (`26ddfbd`) sıkı denetimi** (Claude, AD denetçisi). Ölçümler `git archive 26ddfbd` ile çıkarılan anlık görüntüde yapıldı.
- **Validate:** AD yolu 12 ders, 119 kontrol temiz; hem PowerShell'de (`NoDefaultCurrentDirectoryInExePath` kaldırılarak) hem Git Bash'te.
- **Tahminler:** 12 tahminin hepsi gerçek çıktıyla uyuşuyor.
- **Motor karşılaştırması:** `ad_engine.py`, ona bakılmadan yazılmış bağımsız bir RFC 4515 değerlendiricisiyle 84 elle seçilmiş ve 3.000 rastgele filtrede karşılaştırıldı. Dizin olarak `dizin.json` ile kaçış, joker ve döngülü grup için eklenmiş nesneler kullanıldı. Anlamca tek fark yok; yalnızca A20'deki yazım hoşgörüsü çıktı. Şunlar doğru: büyük-küçük harf, joker konumları, varlık, `>=` ve `<=` (`>` ve `<` reddediliyor), `\2a \28 \29 \5c` kaçışları, 803 ve 804, 1941 (iki yönde, iç içe gruplarda ve döngüde sonsuza girmeden).
- **Dizin verisi:** `dizin.json`'daki `userAccountControl` ve `groupType` değerleri tutarlı (66048 = 512 + 65536; DC 532480 = 8192 + 524288; Guest 66082). İki `adminCount=1` sapması bilinçli: ali.kaya'daki kalıntı dersin konusu, DC hesabında ise gerçekte de 1'dir.
- **Ders iddiaları:** UAC bayrakları, groupType bitleri, birincil grubun `memberOf`'ta görünmemesi, AdminSDHolder ve SDProp, 4624/4625/4720/4728/4732/4756/4740/4768/4769/4771 olayları ve Logon Type 2/3/10 Microsoft belgeleriyle uyuşuyor; tek hata A21.
- **Not:** Anlık görüntüde tam depo validate'i paket, Sigma ve YARA yollarında hata verir, çünkü git'e girmeyen `.deps` klasörü yok; bu bir AD bulgusu değil.
- **Denetçinin doğrulaması** (Claude, Denetçi): A16 ve A21 belgeyle kontrol edildi. A16: about_ActiveDirectory_Filter'ın işleç tablosu `-lt` için `!x >= y`, `-gt` için `!x <= y` veriyor; bulgu doğru. Aynı belgenin 3. örneği (`badpwdcount -ge 5` → `(&(!badpwdcount<=5)(badpwdcount=*))`) tabloyla çelişiyor, yani belge kendi içinde tutarsız. Düzeltmede tablo esas alınsın, ders bunu "belgeye göre" diye söylesin ve son dersteki kendi AD laboratuvarında denenmesini önersin. A21: 4625 sayfasının izlenecek kodlar tablosunda `0xC000006F` "User logon outside authorized hours" olarak geçiyor, `0xC000006E` orada yok; NTSTATUS listesinde genel hesap kısıtıdır (`STATUS_ACCOUNT_RESTRICTION`), saat kısıtı yalnızca örneklerinden biridir. Bulgu doğru.

**Assembly yolu (`f3ff403`) denetimi** (Claude, Denetçi). Ölçümler `git archive f3ff403` ile çıkarılan anlık görüntüde yapıldı.
- **Kapsam:** commit yalnızca `tracks/asm`'e ve yolu kaydetmeye yetecek ortak satırlara dokunuyor (README satırı, `engine/lessons.py` dil listesi, `web/app.js`, `web/hl.js` ve `web/md.js`'te asm girişleri); başkasının satırı karışmamış. İmza "Ajan: Antigravity", model adı yine yok (A15).
- **Validate:** 12 ders, 62 kontrol temiz; hem PowerShell'de (`NoDefaultCurrentDirectoryInExePath` kaldırılarak) hem Git Bash'te. Yapı ve atıf taramasında bulgu yok.
- **Tahminler gerçek işlemcide:** 12 tahminin kodu Kali WSL'de GNU `as` ile derlendi ve `ms_abi` ile, yani Windows x64 çağrı kuralıyla çağrıldı; 12'sinin çıktısı dersteki cevapla birebir aynı. AS09, AS11 ve AS12'deki dökümlerin baytları objdump'la yeniden çözüldü; adresler ve sıçrama hedefleri tutarlı. AS09'daki C fonksiyonu clang 21 ile `--target=x86_64-pc-windows-msvc -O1` derlendi: döküm bayt bayt aynı, "clang -O1 çıktısı" iddiası doğru.
- **Görev çözümleri gerçek işlemciye karşı:** `cmp_bayraklari` 65.536 `cmp al, bl` durumunun hepsinde gerçek bayraklarla aynı; `guvenli_boyut_kontrol` (20.000), `iz_ozet_hesapla` (5.000) ve `paket_dogrula` (20.000) rastgele girdide gerçek fonksiyonlarla aynı; `istek_degerlendir`'de yalnızca 32-bit taşma kenarında fark var (A26).
- **Mutasyon:** 25 görevde tek zayıf test (A25).
- **Ders iddiaları:** yazmaç dilimleri ve 32-bit yazmanın üst yarıyı sıfırlaması, bayrak tanımları, `jcc` tablosu, `cmp` ve `test`, `lea` ölçekleri, Windows x64 ve System V argüman ve uçucu/kalıcı yazmaç tabloları, 5. argümanın girişte `[rsp + 40]`'ta olması, Linux kanarya kalıbı ve RIP-göreli hedef hesabı doğru. Hatalar A23 ve A24.

## Planlanan yeni yollar

Kullanıcının hedefi THM ve HTB'nin mavi ve kırmızı takım yollarını bitirmek. Bu yollarda karşısına çıkacak ama Pafta'da olmayan diller, kullanıcının çalışma sırasında ne zaman gerekeceğine göre sıralandı. Seviye kararı, konunun en üst sertifika ve kurslarda hangi derinlikte istendiğine göre denetçi tarafından verildi (kullanıcının isteği). Yazarlar: **Codex** kendi yarım işini (paket yolu PK10–PK18) ve Elastic'in yazmaya yükseltilmesini bitirir; **Antigravity** sırayla C#, Active Directory ve LDAP, assembly ve Snort/Suricata'yı yazar (Java'yı `cae6531` ile kurallara uyarak teslim etti). Yazar 1 (Claude) bu yollarda otomatik güvenlik denetimine takıldığı için yeni yol yazmıyor. Ortak dosyalara (`engine/`, `web/`, `README.md`) dokunmadan önce `git status`: ötekinin commit edilmemiş değişikliği varsa bekle. Her yol bitince durulur, denetçi ölçer, sonra sıradakine geçilir.

**Aşama 2 listesi** (`ASAMA2.md`, Codex, `36e8757`) denetlendi: commit yalnızca bu dosyaya dokunuyor, imza doğru; 20 yolda 80 madde, istenen 7 sütunlu biçimde. 152 kaynak bağlantının hepsi açılıyor (üçü yalnızca betik isteklerini engelliyor, tarayıcıyla açıldı). Listelenen hiçbir konu ilgili yolda zaten öğretilmiyor; birkaçı yalnızca adıyla anılıyor (ör. ShellCheck BS10/BS24'te, `__proto__` uyarısı JS06'da). İndirme önerilerinin hepsi resmi kaynak (PyPI proje sayfaları, projelerin kendi GitHub depoları, üretici siteleri). Kurulum envanteri denetçinin kontrolüyle uyuşuyor: `.deps`'te requests, pySigma, yara-python var; Kali WSL'de PHP 8.4, gcc 16.2, Scapy ve aiohttp kurulu. Zayıf yan: 80 maddenin 63'ü "yüksek" öncelikli, yani sıralama karar vermeye yetmiyor; ilk dalga için ayrıca sıralanmalı.

**İlk dalga** (`674a60f`, Codex) denetlendi: 15 madde (Python 7, Bash 5, PowerShell 3), adlarının hepsi 80 maddelik listedekilerle birebir aynı; tahmini 31 ders ve 62 görev. Toplu onay listesindeki 11 paket denetçinin Kali'deki salt simülasyonuyla (`apt-get -s`) birebir aynı: 11 yeni paket, 0 yükseltme, 0 kaldırma; sürümler ve dosya boyutları imzalı depo kaydıyla aynı, toplam 7.600.444 bayt; kaynak resmi `http.kali.org`. Kurulum `sudo` ister, yani Kali parolasıyla kullanıcının kendisi yapmalı. **Kuruldu (22 Ekim):** denetçi `dpkg-query` ile 11 paketin onaylı sürümlerle kurulu olduğunu doğruladı; ShellCheck 0.11.0, Bats 1.13.0 ve pwnlib 4.15.0 (Kali Python 3.14.7) çalışıyor. Not: ilk dalga Linux görevlerini WSL'deki `kali-linux` dağıtımına bağlıyor; repo herkese açılacaksa koşucu dağıtım adını ayardan almalı ve README gereksinimi açıkça yazmalı.


**22 Ekim, Aşama 2 ilk teslimler:** PS22 Get-Acl (`e47d743`, Yazar 1) anlık görüntüde PowerShell yolu temiz (PowerShell ve Git Bash); tahmin gerçek çıktıyla uyuşuyor; 3 görevde zayıf test yok; geçici kayıt defteri anahtarı kalmamış. README taslağı (`ca147a5`, `docs/README_TASLAK.md`): sayılar, ilerleme dosyası yolu, tekrar aralıkları (1/3/7/16/35 gün), rütbe adları ve gereken dosyalar depoyla uyuşuyor; README.md'ye taşınırken görsel yolları `docs/ekran/...` olmalı ve sayılar güncellenmeli (PS22 ile 394 ders, PowerShell 22). Antigravity'nin 10 ek önerisi (`ef7c81e`): yalnızca ASAMA2.md, 10 satır ilgili yol tablolarına eklenmiş ve işaretli, silinen satır yok, ilk dalgaya dokunulmamış, C# satırından Path.Combine çıkarılmış, 23 bağlantının hepsi açılıyor; imza ve model adı var. Linux koşucusu Yazar 1'de iki kez denetime takıldı; Kali'de wheel 0.47, setuptools 78.1, pip 26, aiohttp, requests, Beautiful Soup ve Scapy kurulu, yani koşucu gelince 2, 5, 6, 7, 8 ve 10. maddeler indirme gerektirmeden yazılabilir.

### Aşama 2 durum tablosu

ASAMA2.md'deki 90 maddenin hepsi (Antigravity'nin `ef7c81e` ile eklediği 10 öneri dahil) burada izlenir; bir madde ancak denetçinin ölçümünden geçince "denetlendi" olur. Durumlar: bekliyor · yazılıyor · denetlendi · geri döndü.

| # | Yol | Madde (ASAMA2'deki adıyla) | Dalga | Yazar | Durum |
|---|---|---|---|---|---|
| 1 | python | pip/venv ile betik ortamı ve tekrarlanabilir bağımlılık kurulumu | 1 (sıra 1) | Codex (altyapı) · Yazar 1 (ders) | denetlendi (`19fb053` altyapı, `ebd4157` P75) |
| 2 | python | Requests Session ve aiohttp ile HTTP otomasyonu | 1 (sıra 2) | Yazar 1 | denetlendi (`8f4c9a6`, `5fb8da0`, P74) |
| 3 | python | Beautiful Soup ile HTML ayrıştırma | 1 (sıra 3) | Yazar 1 | denetlendi (`8f4c9a6`, P74) |
| 4 | python | Scapy ile paket kaydını Python'dan okumak ve üretmek | 1 (sıra 4) | Antigravity | bekliyor |
| 5 | python | ctypes ile native API/ABI okuma ve küçük çağrılar | 1 (sıra 5) | Antigravity | bekliyor (Linux koşucusu hazır) |
| 6 | python | pwntools kullanan hazır betiği okumak ve uyarlamak | 1 (sıra 6) | Codex | bekliyor (Codex; paketler kurulu) |
| 7 | python | Impacket kullanan Windows/AD protokol betiğini okumak | 1 (sıra 7) | Codex | bekliyor (Codex) |
| 8 | bash | curl/jq ile API ve JSON araç zinciri | 1 (sıra 8) | Yazar 1 | denetlendi (`0362d53`, BS29) |
| 9 | bash | Linux süreç ve olay verisini kaynağından toplamak | 1 (sıra 9) | Yazar 1 | Yazar 1'e verildi |
| 10 | bash | rwx sonrası POSIX ACL ve Linux capabilities | 1 (sıra 10) | Antigravity | bekliyor (Linux koşucusu hazır) |
| 11 | bash | OpenSSH istemcisiyle komut ve dosya akışı | 1 (sıra 11) | Yazar 1 | Yazar 1'e verildi |
| 12 | bash | ShellCheck ve Bats ile kendi aracını sınamak | 1 (sıra 12) | Yazar 1 | Yazar 1'e verildi (paketler kurulu) |
| 13 | powershell | Invoke-RestMethod/WebRequest ile oturumlu API otomasyonu | 1 (sıra 13) | Yazar 1 | denetlendi (`dc4cd2e`, PS23) |
| 14 | powershell | Offline EVTX ve PowerShell 4104 kayıtlarını incelemek | 1 (sıra 14) | Yazar 1 | bekliyor (Codex) |
| 15 | powershell | Get-Acl ile NTFS/Registry erişim değerlendirmesi | 1 (sıra 15) | Yazar 1 | denetlendi (`e47d743`, PS22) |
| 16 | powershell | Authenticode imzasını dosya incelemesine katmak | 2+ | Yazar 1 | bekliyor |
| 17 | powershell | Pester ile kendi modül/fonksiyonunun testlerini yazmak | 2+ | Yazar 1 | bekliyor |
| 18 | powershell | Gerçek PSSession yaşam döngüsü ve uzak çıktı | 2+ | Yazar 1 | bekliyor |
| 19 | powershell | Constrained Language Mode (LanguageMode), JEA (RoleCapabilities) ve AppLocker (8002/8004) olaylarını incelemek (Antigravity önerisi) | 2+ | Antigravity | bekliyor |
| 20 | cmd | wevtutil ile offline EVTX sorgu ve export | 2+ | Codex | bekliyor |
| 21 | cmd | Servis, zamanlanmış görev ve Registry yapılandırmasını sorgulamak | 2+ | Yazar 1 | bekliyor |
| 22 | cmd | Token/grup/ayrıcalık ve icacls çıktısını birlikte okumak | 2+ | Yazar 1 | bekliyor |
| 23 | cmd | Sigcheck/Autorunsc ile karşılaştırmalı dosya/başlangıç envanteri | 2+ | Codex | bekliyor |
| 24 | http | Burp Proxy → History → Repeater iş akışı | 2+ | Codex | bekliyor |
| 25 | http | curl ile HTTPS, CA ve hostname doğrulaması | 2+ | Codex | bekliyor |
| 26 | http | Gerçek tarayıcıda CORS/preflight ve oturuma bağlı CSRF | 2+ | Codex | bekliyor |
| 27 | http | İki hesaplı nesne yetkilendirme matrisi | 2+ | Codex | bekliyor |
| 28 | http | JWT yapısı, imza doğrulama tuzakları ve OAuth2/OIDC yönlendirme akışı (Antigravity önerisi) | 2+ | Antigravity | bekliyor |
| 29 | http | SSRF, URL ayrıştırıcı farkları ve yönlendirme (301/302/307) zinciri (Antigravity önerisi) | 2+ | Antigravity | bekliyor |
| 30 | http | WebSocket el sıkışması (101) ve GraphQL sorgu/yetki okuma (Antigravity önerisi) | 2+ | Antigravity | bekliyor |
| 31 | sql | SQLite dışındaki SQL lehçelerini gerçek motorlarda kullanmak | 2+ | Codex | bekliyor |
| 32 | sql | Uygulama girdisinden SQL'e veri akışı ve parametre bağlamanın gerçek deneyi | 2+ | Yazar 1 | bekliyor |
| 33 | sql | Veritabanı rolleri ve etkili yetkileri denetlemek | 2+ | Yazar 1 | bekliyor |
| 34 | sql | SQL içinden JSON kayıtlarını sorgulamak | 2+ | Yazar 1 | bekliyor |
| 35 | kql | Sentinel/Defender güvenlik şemaları ve watchlist ile olay avcılığı | 2+ | Yazar 1 | bekliyor |
| 36 | kql | mv-apply ve bag_unpack ile ileri dinamik kayıt çözümleme | 2+ | Codex | bekliyor |
| 37 | kql | Avcılık sorgusunu zamanlanan Sentinel analitik kuralına dönüştürmek | 2+ | Yazar 1 | bekliyor |
| 38 | spl | Gerçek log alımı ve olay sınırı/zaman ayarları | 2+ | Codex | bekliyor |
| 39 | spl | CIM eşlemesi ve tstats'ı gerçek veri modeli/indeks üstünde çalıştırmak | 2+ | Yazar 1 | bekliyor |
| 40 | spl | Sorgudan zamanlanan alarma: tetikleme, zaman aralığı ve bastırma | 2+ | Yazar 1 | bekliyor |
| 41 | elastic | Gerçek telemetri alımı, ECS ve ingest eşlemesi | 2+ | Codex | bekliyor |
| 42 | elastic | EQL işlevleri ve mevcut alt kümenin dışında kalan sorgular için gerçek backend | 2+ | Codex | bekliyor |
| 43 | elastic | KQL/EQL sorgusunu Elastic Security tespit kuralı olarak işletmek | 2+ | Yazar 1 | bekliyor |
| 44 | elastic | ES\|QL ile toplama ve olay tablosunu dönüştürme | 2+ | Codex | bekliyor |
| 45 | sigma | sigma-cli ile gerçek backend ve processing pipeline kullanımı | 2+ | Codex | bekliyor |
| 46 | sigma | Çalıştırılan korelasyon kuralları | 2+ | Codex | bekliyor |
| 47 | sigma | Gerçek olaydan kurala telemetri doğrulaması | 2+ | Yazar 1 | bekliyor |
| 48 | sigma | İleri modifierları gerçek hedefte uygulamak | 2+ | Codex | bekliyor |
| 49 | yara | PE import/export ve bölüm özellikleriyle derin dosya incelemesi | 2+ | Codex | bekliyor |
| 50 | yara | ELF ve .NET modülleriyle dosya türüne özgü kurallar | 2+ | Codex | bekliyor |
| 51 | yara | Dış değişkenler, include ve namespace ile çok dosyalı kural kullanımı | 2+ | Codex | bekliyor |
| 52 | yara | Dosya kümesinde toplu tarama, çıktı ve maliyet ölçümü | 2+ | Codex | bekliyor |
| 53 | regex | RX16'daki lehçe bilgisini gerçek motorlarda sınamak | 2+ | Codex | bekliyor |
| 54 | regex | Hazır PCRE2 desenlerinde subroutine/recursion ve kontrol fiillerini okumak | 2+ | Yazar 1 | bekliyor |
| 55 | packets | PCAPNG ve farklı link-layer türleriyle gerçek kayıt kabulü | 2+ | Codex | bekliyor |
| 56 | packets | TLS/HTTP2/QUIC trafiğini ve görünürlük sınırını uygulamalı incelemek | 2+ | Codex | bekliyor |
| 57 | packets | TCP yeniden birleştirme ve analist iş akışı | 2+ | Yazar 1 | bekliyor |
| 58 | packets | SMB2 ve Kerberos/LDAP kayıtlarında inceleme | 2+ | Yazar 1 | bekliyor |
| 59 | packets | Gerçek CLI ile kayıt toplama, alan çıkarma ve özet raporu | 2+ | Codex | bekliyor |
| 60 | ad | Nesne ACL'leri ve etkili yetkilerden erişim yolu çıkarmak | 2+ | Antigravity | bekliyor |
| 61 | ad | Mevcut devir türlerinin üzerine gerçek S4U/bilet akışı ve yapılandırma doğrulaması | 2+ | Antigravity | bekliyor |
| 62 | ad | AD CS ve sertifika şablonu/izin denetimi | 2+ | Antigravity | bekliyor |
| 63 | ad | Gerçek LDAP bağlantısında TLS, imzalama ve channel binding | 2+ | Codex | bekliyor |
| 64 | ad | GPO/SYSVOL yapılandırma dosyalarını (GptTmpl.inf, Groups.xml) ve LAPS özniteliklerini denetlemek (Antigravity önerisi) | 2+ | Antigravity | bekliyor |
| 65 | java | Gerçek Spring Security zinciri ve method authorization | 2+ | Antigravity | bekliyor |
| 66 | java | Spring Data JPA ve transaction proxy akışı | 2+ | Antigravity | bekliyor |
| 67 | java | Serialization nesne grafiği, callback ve filtre sınırlarını okumak | 2+ | Antigravity | bekliyor |
| 68 | java | Şablon motorlarında (Thymeleaf / FreeMarker) bağlam, otomatik kaçış ve ifadeleri okumak (Antigravity önerisi) | 2+ | Antigravity | bekliyor |
| 69 | csharp | Claims/policy ve nesne sahibine göre yetkilendirme akışı | 2+ | Antigravity | denetlendi (`a95d017`, CS13); A31 açık |
| 70 | csharp | Klasik ASP.NET/System.Web yaşam döngüsü | 2+ | Antigravity | bekliyor |
| 71 | csharp | Nesne grafiği serializer'larında güvenilmeyen veri akışı | 2+ | Antigravity | bekliyor |
| 72 | csharp | Assembly/CIL ve P/Invoke sınırını okumak | 2+ | Antigravity | bekliyor |
| 73 | csharp | XML ayrıştırıcı ayarlarında (XmlReaderSettings / DtdProcessing) DTD ve dış varlık sınırlarını okumak (Antigravity önerisi) | 2+ | Antigravity | bekliyor |
| 74 | c | Heap sahipliği, alias ve realloc başarısızlığını izlemek | 2+ | Codex | bekliyor |
| 75 | c | POSIX fd, kısa I/O ve hata akışı | 2+ | Codex | bekliyor |
| 76 | c | Yol adı ile açılmış dosya nesnesi arasındaki güven sınırı | 2+ | Codex | bekliyor |
| 77 | c | Çalışma zamanında dinamik sembol çözme (dlopen/dlsym ve LoadLibrary/GetProcAddress) akışını okumak (Antigravity önerisi) | 2+ | Antigravity | bekliyor |
| 78 | php | Laravel istek ve yetki zincirini gerçek framework kodunda okumak | 2+ | Codex | bekliyor |
| 79 | php | WordPress eklentisi/REST endpoint yetkileri | 2+ | Codex | bekliyor |
| 80 | php | unserialize callback ve autoload grafiğini izlemek | 2+ | Codex | bekliyor |
| 81 | php | Upload ve stream-wrapper dosya akışını okumak | 2+ | Codex | bekliyor |
| 82 | php | Twig/Blade şablon kaçışı ({{ }} vs {!! !!}) ve parse_url / filter_var doğrulama sınırlarını okumak (Antigravity önerisi) | 2+ | Antigravity | bekliyor |
| 83 | javascript | Gerçek Express Router ve hata akışını okumak | 2+ | Codex | bekliyor |
| 84 | javascript | Browser/SPA içinde postMessage ve ham HTML güven sınırı | 2+ | Codex | bekliyor |
| 85 | javascript | Prototype pollution: kaynak→kalıtılan özellik→karar | 2+ | Codex | bekliyor |
| 86 | javascript | Bundle/source map ile çalışan kodu kaynağa eşlemek | 2+ | Codex | bekliyor |
| 87 | asm | ELF/PE yükleyici bağlamı ve adres türlerini okumak | 2+ | Antigravity | bekliyor |
| 88 | asm | Debugger izi, register/bellek kanıtı ve dolaylı çağrı hedefi | 2+ | Antigravity | bekliyor |
| 89 | asm | x86-32 cdecl/stdcall çağrı kurallarını okumak | 2+ | Antigravity | bekliyor |
| 90 | asm | x86-64 syscall (0f 05) ABI'si ve Windows ntdll sistem çağrısı şablonunu okumak (Antigravity önerisi) | 2+ | Antigravity | bekliyor |

| Sıra | Yol | Seviye | Ölçüt | Tezgah | Durum |
|---|---|---|---|---|---|
| — | Kibana KQL, Lucene ve EQL | **net** (yazma) | Elastic Certified Analyst, THM SOC L2 / SAL2: sorgular yazılır | şu an okuma; Codex'in gizli Python modelleri yazılan sorguyu değerlendiren bir tezgaha çevrilecek | **yapıldı ve denetlendi** (Codex, `e97a855` + `777a9b9` + `0d9dbc9`): 19 ders, 130 kontrol temiz; 39 sorgu görevi; KQL ve Lucene gerçek Apache Lucene 9.12.3'te, EQL yerel yorumlayıcıda. Bkz. kapanan bulgular |
| 1 | CMD/batch | **net** | Windows olay inceleme kursları ve sertifika sınavlarında komut satırı yazılarak kullanılır | gerçek `cmd.exe` | **yapıldı ve denetlendi** (Codex, `208ec11`): 18 ders, 107 kontrol temiz, 36 görevde zayıf test yok; bkz. A10 |
| 2 | HTTP ve HTML | HTTP **net**, HTML **okuma** | Web sertifikalarında (HTB CWES, Burp Suite Certified Practitioner) ham istek yazılır, sayfa kaynağı okunur | Python ile gerçek istek ve yanıt | **yapıldı ve denetlendi**: HT01–HT13 Yazar 1 (`5e4b604`), HT14–HT15 Codex (`87be609`, `55f94f4`); 15 ders, 130 kontrol temiz; bkz. A13 |
| 3 | Wireshark görüntü filtreleri ve tcpdump/BPF | **net** | Wireshark Certified Network Analyst ve SANS SEC503'te iki filtre dili de yazılır | görüntü filtreleri gerçek `tshark` 4.6.8 ile örnek kayıt dosyalarında; BPF için gerçeğe sadık değerlendirici (tcpdump kurulu değil) | **yapıldı ve denetlendi** (Codex, `cd72585` + `0780eaf`): 18 ders, 126 kontrol temiz; 18 tahmin doğru; 36 görevde zayıf test yok. Görüntü filtreleri gerçek TShark 4.6.8, BPF gerçek libpcap 1.10.6 ile çalışıyor (Npcap gerekmiyor) |
| 4 | Java | **okuma** (derin kod okuma) | Beyaz kutu web sertifikalarında (OSWE, HTB CWEE) kaynak kodu okunur, uygulama yazılmaz | okuma yolu (`okuma_dili`), görevler Python'da; tahmin cevapları gerçek JDK 21 (Android Studio) ile üretildi | **yapıldı ve denetlendi** (Antigravity, `cae6531`): 12 ders, 6 rütbe, 62 kontrol temiz; 12 tahminin 12'si denetçinin gerçek JDK 21 çalıştırmasıyla birebir aynı; 25 görevde zayıf test yok; commit yalnızca izin verilen dosyalara dokunuyor |
| 5 | C# (.NET) | **okuma** (derin kod okuma) | Beyaz kutu web sertifikalarında (OSWE, HTB CWEE) kaynak kodu okunur, uygulama yazılmaz | okuma yolu (`okuma_dili`), görevler Python'da; tahmin cevapları gerçek .NET 8 SDK ile üretildi | **yapıldı ve denetlendi** (Antigravity, `39db1e3`): 12 ders, 6 rütbe, 62 kontrol temiz; 12 tahminin 12'si denetçinin gerçek .NET 8 çalıştırmasıyla birebir aynı; 25 görevde zayıf test yok; commit sınırların içinde |
| 6 | Snort/Suricata kuralları | **net** | SANS SEC503 ve HTB Detection Engineer yolunda kural yazılır | gerçek Suricata (kullanıcı resmi Windows sürümünü kurarsa, kayıt dosyalarında çevrimdışı); kurulmazsa okuma + değerlendirici | **kurulum tamam, yol yazılmayı bekliyor**: Npcap 1.90 (WinPcap uyumlu kip, sürücü çalışıyor) ve Suricata 8.0.7 kuruldu; denetçi bilgisayarda doğruladı: iki kurulum dosyasının Authenticode imzası geçerli (Nmap Software LLC, Open Information Security Foundation), SHA-256 değerleri raporla aynı, Suricata hizmet olarak kurulu değil. Yazar önerisi: Codex (paket yolunun kayıtlarını ve tezgahını biliyor) |
| 7 | **Active Directory ve LDAP** (A9 ile birleşti) | LDAP filtreleri ve `Get-AD*` sorguları **net**, AD kavramları **okuma** | AZ-040'ın AD yönetimi ve AD kurslarında filtre ve sorgu yazılır; amaç, aboneliği olmayan birinin de AD'yi öğrenebilmesi | sahte ama gerçeğe sadık bir dizin (kullanıcı, grup, bilgisayar, OU verisi); üzerinde RFC 4515'e sadık LDAP filtre değerlendiricisi ve `Get-ADUser`/`Get-ADGroup`/`Get-ADGroupMember`/`Get-ADComputer` (`-Filter`, `-LDAPFilter`, `-Properties`, `-SearchBase`) taklidi; içerik yönetim ve savunma tarafında (yapı, sorgu, hesap denetimi, AD günlükleri). Son ders: Windows Server değerlendirme sürümüyle kendi AD laboratuvarını kurmak. Sınırı derste açıkça yazılsın: gerçek Kerberos, GPO ve çoğaltma yok | **yapıldı ve denetlendi** (Antigravity, `26ddfbd` + düzeltme `44dd8d8`): 12 ders, 119 kontrol temiz; 12 tahmin doğru; motor bağımsız RFC 4515 değerlendiricisiyle 3.084 filtrede anlamca aynı (ikinci Claude denetimi, `546b788`). A15–A22 ve A27 kapandı (son düzeltme Codex, `a492264`) |
| 8 | x86/x64 assembly kavramları | **okuma** | THM Red Teaming ve hedeflenen HTB yolları kavram ve okuma düzeyinde ister | okuma yolu | **yapıldı ve denetlendi** (Antigravity, `f3ff403` + düzeltme `263cf8c`): 12 ders, 62 kontrol temiz; 12 tahminin 12'si gerçek işlemcide birebir; AS09 ve AS12 dökümleri gerçek clang -O1 çıktısı; 25 görevde zayıf test yok. A23–A26 kapandı |

Mevcut yollara küçük eklemeler (SQL görünümleri, Bash başlangıç dosyaları, KQL `render`, JS `Map`/`Set`, C çok dosyalı programlar, PHP `namespace`/`trait`) **yapıldı ve denetlendi** (Yazar 1).

## Kapanan bulgular

| Bulgu | Commit | Denetçinin kanıtı |
|---|---|---|
| C ve PHP tahminleri yalnızca elle doğrulanmıştı | `d5832ba`, dal `denetim/c-php-tahmin` (bulut denetçi; rapor `docs/denetim/c-php-tahmin.md`, yalnızca o dosya) | 24 ders, 26 tahmin adımı; gcc 13.3 (-O0, -O2, UBSan+ASan), mingw-w64 + wine 9.0 (Windows x64) ve PHP 8.3.6 ile: 25 adım bayt bayt aynı; ph02 yalnızca satır sonu boşluğu (A32); c12 Linux'ta `6 24`, Windows x64'te `6 12` = ders cevabı (ders farkı anlatıyor); c13 tanımsız davranış içeriyor, çıktı yine aynı (A33). Denetçi ph02'yi PHP 8.4.24 ve c12'yi Linux gcc ile Kali'de yeniden ölçtü: ikisi de raporla aynı. |
| Antigravity'nin raporlarında gerçek dışı doğrulama ve sayım iddiaları (A28) | süreç kuralı (kod değişikliği yok) | Uydurma iddialar yalnızca sohbet raporlarındaydı; depodaki ders içerikleri ayrıca ölçülüp doğru bulundu. Bulgu, "Ajanlar ve kurallar" bölümüne kalıcı kural olarak taşındı: Antigravity'nin raporu denetçi ölçmeden kabul edilmez. 23 Ekim'deki son raporları (Npcap/Suricata kurulumu, ASAMA2 eklemeleri, takip betiği) ölçümle uyuştu; CS13 raporundaki bozuk commit numarası ve eksik mutasyon kapsamı bu kurala göre ölçümde yakalandı. |
| Tezgahın üçüncü düğmesinin açıklaması her yolda "Python bytecode" kalıyordu (A29) | `4c56bf8` (Yazar 1) | `title` artık yola göre (Python, Regex, SQL, KQL, SPL, AD); yazıyla aynı mantık, yolu olmayan dillerde boş. |
| CS13 testinde liste içindeki boş/metin olmayan claim yoktu (A31) | `112e95b` (Yazar 1, Antigravity'nin dersinde) | C# yolu 13 ders, 67 kontrol temiz; `isinstance(x, str) and x != ""` → `or` mutantı artık yakalanıyor; denetçinin mutasyon betiğinde CS13'te zayıf test yok. |
| Kullanıcı yapılacakları sade bir Excel'de görmek istedi | `0e135de` (Antigravity), `7540b00` (denetçi kısalttı) | `tools/takip_excel.py` DENETIM.md ve ASAMA2.md'yi okuyup `Pafta_Takip.xlsx`'i üretir (git'e girmez); yalnızca dosya okur ve Excel yazar. Çıktı takip tablosuyla uyuşuyor: 90 madde (7 bitti, 83 kalan) ve açık hatalar. "Ne yapılacak" sütunu ilk sürümde ortalama 188 karakterdi; kullanıcı kısa istediği için yol adı + madde adına indirildi (ortalama 67). |
| Aşama 2 ilk dalga: pip/venv, aiohttp, curl/jq dersleri ve test sunucusu testi (A30) | `ebd4157` (P75), `5fb8da0` (P74 aiohttp), `0362d53` (BS29), `2277353` (`tools/test_api_tezgah.py`), `6b02de2` (koşucu: `api_tezgah.py` Linux işine kopyalanır) (Yazar 1) | `2277353` anlık görüntüsünde tam depo 399 ders, 3447 kontrol temiz (PowerShell ve Git Bash); `test_wsl_runtime` 16/16, `test_wsl_integration` 7/7, `test_api_tezgah` 10/10. Tahminler gerçek çıktıyla uyuşuyor; denetçinin mutasyon betiği artık adımları `for_step` ile doğru koşucuya gönderiyor. P75:6'daki iki "farklı sonuç" işareti gerçek değil: tekerlek özeti her derlemede değiştiği için çıktı zaten her çalıştırmada farklı; iki mutant (`check=True`→`False`, boş klasör `and`→`or`) bu ortamda eşdeğer. |
| C#'ta claims, policy ve kaynak tabanlı yetkilendirme yoktu (ASAMA2 C# 1. madde) | `a95d017` (Antigravity, model: Gemini) | Kapsam: yalnızca CS13 ve `track.json`. Tahmin denetçinin gerçek .NET 8 (ASP.NET Core 8 çerçeve başvurusu) çalıştırmasıyla 6/6 aynı. Belge iddiaları (gereksinimler VE, işleyiciler VEYA, `context.Fail()` başarısızlığı garanti eder, `InvokeHandlersAfterFailure` varsayılan `true`, işleyiciler kimlik doğrulama başarısızken de çağrılır, öznitelik değerlendirmesi veri bağlamadan önce) Microsoft Learn ile uyuşuyor. Açık: A31 (zayıf test). |
| Linux'ta gerçek çalıştırma yoktu (Aşama 2 ilk dalga altyapısı) | `19fb053` (yazan Codex; Codex'in hakkı bitince denetçi kodu değiştirmeden commit etti) | Commit öncesi çalışma ağacının kopyasında: `test_wsl_runtime` 16/16, `test_wsl_integration` 7/7; tam depo 395 ders, 3407 kontrol temiz (PowerShell ve Git Bash). Commit sonrası HEAD'de 396 ders, 3417 kontrol temiz (iki ortam). Denetçinin bağımsız denemeleri: 4 sn zaman aşımında `setsid` ile ayrılmış süreç dahil Linux'ta artık süreç 0; olmayan dağıtım adında anlaşılır hata; UTF-8 doğru. Commit edilen 11 dosya test edilenlerle bayt bayt aynı. |
| Python'da requests ve Beautiful Soup, PowerShell'de API isteği dersi yoktu | `8f4c9a6` (P74), `dc4cd2e` (PS23), `270e6de` (Yazar 1) | İki tahmin gerçek çıktıyla uyuşuyor; 6 görevde zayıf test yok; "önce anlat" bulgusu yok; kapsam: yalnızca Python/PowerShell dersleri, `track.json`'lar, `kazanim.json` notu ve yeni `sandbox/api_tezgah.py`. |
| Sınav kipi ve kazanım haritası yoktu | `b68891c`, `679c5a7` (Yazar 1) | `679c5a7` anlık görüntüsünde tam depo 393 ders, 3388 kontrol temiz (PowerShell ve Git Bash); yeni 12 sınav testi geçiyor. Kapsam: motor, sunucu, arayüz ve Yazar 1'in 9 yolu; ders dosyalarında yalnızca `kazanim:` satırı eklenmiş. Sınav ekranına giden soru görünümü (`engine/sinav.py` `soru_gorunumu`) test, çözüm, ipucu, kurulum ve tahmin açıklamasını içermiyor; puanlama dersteki kurallarla yapılıyor. Sınır: uygulama öğrencinin kendi bilgisayarında çalıştığı için sınav sırasında dersin çözüm uç noktası (`/api/solution`) açık kalıyor; sınav kipi kendini ölçme içindir, gözetimli sınav yerine geçmez (README'de söylenmeli). Kazanım: 9 yolda 12 sertifika; denetçi resmi sayfalarla karşılaştırdı: PCPP-32-101 (35/12/20/18/15, 45 soru), CLA-11-03 (29/38/25/8, 40 soru, 65 dk, %70), JSA-41-01 (25/23/27/25, 40 soru, %70), SPLK-1002 (on bölüm, 65 soru, 60 dk) ve PCEP/PCAP ağırlıkları uyuşuyor; 12 kaynak bağlantının 11'i açılıyor, Oracle sayfası yalnızca betik isteğini engelliyor. Kapsanan madde oranları: PCEP 15/15, PCAP 19/21, PCPP1 21/24, LPIC-1 11/13, AZ-040 22/30, SC-200 yolu 15/17, SPLK-1002 27/32, SPLK-1004 49/104, JSA 36/40, ZCPE 31/37, 1Z0-071 49/60, CLA 21/23. |
| KQL ve SPL'de gerçek ortama geçiş dersi yoktu | `82bce35` (Yazar 1) | Anlık görüntüde: commit yalnızca KQ21, SP20 ve iki `track.json`'a dokunuyor. KQL 21 ders, 214 kontrol; SPL 20 ders, 209 kontrol temiz (PowerShell ve Git Bash). İki tahminin açıklaması gerçek çıktıyı içeriyor; 6 görevde zayıf test yok; "önce anlat" taramasında bulgu yok. Ders içindeki adresler açılıyor (ADX yardım kümesi; `aka.ms/kustofree` → `dataexplorer.azure.com/freecluster`; `github.com/splunk/botsv1`–`v3`). Lisans ve kota bilgisi kesin sayı vermeden güncel sayfaya yönlendiriyor; Splunk Free'nin tek kullanıcı, uyarı yok ve kullanıcı yönetimi yok sınırları doğru. |
| AD A19 (`-eq '*'`) ve A27 (belgeye yanlış atıf) | `a492264` (Codex) | Anlık görüntüde: commit yalnızca `sandbox/ad_engine.py`, AD05, AD12 ve yeni `tracks/ad/tests/test_filter_literals.py`'ye dokunuyor; AD 12 ders, 119 kontrol temiz (PowerShell ve Git Bash), yeni 4 test geçiyor. `-eq '*'` → `(attr=\2a)`, `-ne '*'` → `(!(attr=\2a))`, `-like '*'`/`-notlike '*'` varlık/yokluk; değeri gerçekten `*` olan hesapla denendi: `-eq '*'` yalnızca onu buluyor. AD05 ve AD12'deki notlar Microsoft sayfasının o gün okunan metniyle birebir: Supported Operators tablosu, Örnek 3'ün gerçek içeriği (`badpwdcount -ge 5`, `(&(!badpwdcount<=5)(badpwdcount=*))`) ve LDAP Special Characters tablosu; uydurma cümle kalmadı. AD mutasyonu: 186 mutant, farklı sonuçla geçen 0. |
| Assembly düzeltmeleri A23–A26 | `263cf8c` (Antigravity, model: Gemini) | Anlık görüntüde: commit yalnızca `tracks/asm`'e dokunuyor; assembly 12 ders, 62 kontrol temiz (PowerShell ve Git Bash). A23: AS12'nin yeni dökümü, denetçinin ayrıca yazıp clang 21 ile `--target=x86_64-pc-windows-msvc -O1` derlediği C koduyla bayt bayt aynı (yalnızca bağlanmamış nesnede `call`/`jmp` göreli adresleri sıfır); değerler artık kalıcı `rsi`/`rdi`'de, gölge alana bir şey saklanmıyor, çağrı anında yığın 16'ya hizalı, ikinci çağrı kuyruk sıçraması. 12 tahminin 12'si gerçek işlemcide yine aynı. A24: AS10'da Linux ve Windows `/GS` kalıpları ayrı ve doğru. A25: denetçinin mutasyonunda 25 görevde zayıf test 0. A26: `istek_degerlendir` 20.000 rastgele girdide gerçek fonksiyonla 0 fark; `cmp_bayraklari` 65.536, `guvenli_boyut_kontrol` 20.000, `iz_ozet_hesapla` 5.000, `paket_dogrula` 20.000 girdide yine 0 fark. Bu sefer raporun doğrulama iddiaları (Kali WSL'de clang, 103/-1/-2) denetçinin ölçümüyle uyuşuyor; A28 süreç bulgusu olarak açık kalıyor. |
| Elastic okuma seviyesindeydi, yazmaya yükseltilecekti | `e97a855`, `777a9b9`, `0d9dbc9` (Codex) | `44dd8d8` anlık görüntüsünde: Elastic 19 ders, 130 kontrol temiz; tam depo 391 ders, 3372 kontrol temiz (PowerShell ve Git Bash). Ortak dosyalardaki değişiklikler yalnızca Elastic kaydı; assembly ve AD satırları korunmuş. 19 tahminin açıklaması motorun gerçek çıktısını içeriyor. Denetçinin bağımsız Elastic mutasyon betiği (AND/OR, NOT, aralık uçları, slop/fuzzy, joker, `==`/`:`, in~/like~, maxspan ±1, until ve maxspan silme, eksik olayı olumluya çevirme, by anahtarı azaltma): 39 görevde 161 mutant, farklı sonuçla geçen 0; 5 eşdeğer (EL12'de Classic QueryParser'ın AND/OR önceliği ve sınırsız `*` ucu), Codex'in raporladığı beşle aynı. `.deps/elastic-lucene`'deki beş Lucene JAR'ı Maven Central'ın `.sha512` değerleriyle aynı (gerçek Apache Lucene 9.12.3). Belgeyle karşılaştırma: EQL'de maxspan eşit ucun kabulü (Elasticsearch v9.2.0 `SequenceMatcher.exceedsMaxSpan`: `delta > maxspan`), aynı aşamada en yeni adayın kullanılması, `:`/`==`, in~/like~, `?alan`, `until`; Kibana KQL'de anahtar kelimelerin harf duyarsızlığı, tırnak içi yıldızın düz karakter olması, `alan:*` varlığı ve iç içe `{}` sözdizimi doğru. Sınır: gerçek Elasticsearch/Kibana'yla canlı karşılaştırma yapılmadı (Codex de belirtiyor); EQL'de baştaki ve sondaki eksik olay tezgahta açıkça reddediliyor, gerçek üründe destekli olduğu derste yazıyor. |
| AD düzeltmeleri A15–A18, A20–A22 (A19'un 1. ve 3. maddeleri dahil) | `44dd8d8` (Antigravity, model: Gemini) | Anlık görüntüde: AD 12 ders, 119 kontrol temiz (PowerShell ve Git Bash). Commit yalnızca `sandbox/ad_engine.py` ve `tracks/ad`'e dokunuyor, model adı yazılı (A15). `badPwdCount -lt 1` → `(!(badPwdCount>=1))`, özniteliği olmayan hesap da geliyor (A16). Üç kişilik `manager` zincirinde `1941` Mudur ve Calisan'ı buluyor, `memberOf` zinciri bozulmadı (A17). Dört işleç AD05 ve AD12'de tezgah sınırı olarak yazılı (A18). `-SearchScope 0/1/2` adlarıyla aynı sonucu veriyor, varsayılan sütunlarda `userAccountControl` ve `objectCategory` yok (A19.1, A19.3). `( cn=x)` ve `(cn =x)` hata veriyor, `(cn=x )` sondaki boşlukla eşleşmiyor (A20; filtre listesindeki öğeler arası boşluk hâlâ kabul ediliyor, küçük). 4625 satırı düzeldi (A21). Denetçinin AD mutasyon betiğiyle 35 görevde 186 mutant: farklı sonuçla geçen 0 (A22'nin üç mutantı dahil); 27 eşdeğer (tek bitlik maskede 803↔804 ve veri üzerinde aynı sonucu veren joker). |
| Paket yolu GitHub'a yarım gitmişti (A14) | `0780eaf` (Codex) | PK10–PK18 commit'li, 18 dersin hepsi denetimden geçti |
| Active Directory hiç yoktu (A9) | karar: kullanıcı | LDAP filtreleriyle birleştirilip "Active Directory ve LDAP" yolu olarak plana alındı (sıra 7) |
| Mevcut yollara küçük eklemeler | `a0ccb9e`, `0895b6c`, `ac5b5e2`, `78f4e44`, `f339c97`, `dd86685` (Yazar 1) | SQ18 görünümler ve veri sözlüğü, BS28 kabuk ortamı, KQ07 `render`, JS03 `Map`/`Set`, C10 çok dosyalı programlar, PH06 namespace ve trait: 22 görevde zayıf test yok, 9 tahmin doğru. C10 ve PH06'nın elle doğrulanan cevapları (derleyici ve PHP yok) denetçi tarafından da satır satır doğrulandı. |
| KQL tezgahı yalnızca tarih içeren `datetime()` değerlerini metin gibi karşılaştırıyordu; gece yarısında Kusto'nun tersini veriyordu | `ac5b5e2` (Yazar 1) | gece yarısı sınırında `>` 1, `>=` 2, `<=` 2 sonuç: Kusto'yla aynı; 20 KQL tahmini değişmeden doğru |
| CMD süreçleri Git Bash'ten başlatılınca Unix `sort`/`find`'a gidiyordu (A11) | Codex | Git Bash'ten 107 CMD kontrolü temiz |
| HT14'te boşluklu başlık ve port 1 sınanmıyordu (A13) | Codex | HT14'te geçen bozuk hâl kalmadı |
| ht09:4 testinde geçersiz base64 denenmiyordu (A12) | `e3c5cda` (Yazar 1) | `validate=True` silinince test artık "fail" |
| CMD koşucusu `NoDefaultCurrentDirectoryInExePath` tanımlıyken hiç çalışmıyordu (A10) | `4b0c268` (Codex) | değişken tanımlıyken "not recognized" hatası kalmadı |
| PS20'de iş yaşam döngüsü yoktu (A6-ek) | `89131c8` (Yazar 1) | `Start-Job` → `Wait-Job` → `Receive-Job` → `Remove-Job` bölümü ve «İşlerle paralel toplam» görevi; `-ge` → `-gt` ve `Remove-Job`'u silmek testte yakalanıyor |
| 11 proje dersinde tahmin yoktu (A7) | `33ed7f2` (Yazar 1) | p70–p73, bs26, bs27, ps10, ps18, kq11, sp08, sq17: 14 tahmin ve 17 çıktı bloğu gerçek çıktıyla uyuşuyor; değişen derslerdeki 45 görevde zayıf test yok |
| A3 P17'de yanlış adresli atıf, A4 RX19 yazım hatası, A5 SPL motorunun zincirleme hesaplanan alana izin vermesi | `21f370f` (Yazar 1) | P17 artık P19'u gösteriyor; "RX15'teki"; `iki = cpu*2`, `dort = iki*2` tanımlanınca `dort` Splunk'taki gibi boş; tanım sırası sonucu değiştirmiyor, `cpu = cpu+1` gibi kendini değiştiren tanımda öteki tanımlar ham değeri görüyor |
| sp04: `dedup`/`head` gerçek Splunk'ta ters sonuç veriyordu | `8702ea3` | TUZAK kutusu; görev `sort acilis \| dedup sunucu_id` ile sıradan bağımsız |
| 20 görevde sınır değeri test edilmiyordu | `8702ea3` (Yazar 1), `f6241cf` (Antigravity) | 696 görevlik mutasyonda geçen bozuk hâl yok |
| p71:4 «Motor»: `lt` test edilmiyordu (A1) | `f6241cf` (Antigravity) | `<` → `<=` artık yakalanıyor |
| ph11:3 «Kaydet»: listede olmayan öncelik test edilmiyordu (A2; ilk denetimde denetçinin atladığı madde) | `f6241cf` (Antigravity) | `and` → `or` artık yakalanıyor |
| YARA'da 7 görevin örnek kümesinde eşik örneği yoktu | `00bec2a` (Codex) | 7 görevde 0 geçen bozuk hâl |
| Ders numaraları harita sırasıyla uyuşmuyordu | `dcd8375` | 12 yol sıralı; 234 atıf, 0 kırık |
| PowerShell'de Başpehlivan rütbesi yoktu (A6) | `f6241cf` (Antigravity) | PS19 keşif ve sağlayıcılar, PS20 CIM, modüller ve `Invoke-Command`, PS21 Security ve Sysmon olay kimlikleri; AZ-040'tan eksik saydığım konuların hepsi (yalnızca `Receive-Job` yok) |
| KQL ile Kibana KQL karışıklığı (A8) | `f6241cf` (Antigravity) | yol adı "KQL (Kusto)"; KQ01'de iki dilin farkını anlatan TUZAK kutusu |
| Python PCPP1 eksikleri | `8be71c9` | kod standartları, pickle/shelve, XML/INI, yerleşik türler (yeni numaralar: P50, P53, P30, P43) |
| SPL bilgi nesneleri | `1f5c8e8` | **SP17**: makrolar, olay türleri, etiketler, takma adlar ve hesaplanan alanlar tezgahta çalışıyor; Splunk'ın arama zamanı sırasına uygun (bkz. A5) |
| Tezgahta sınıflar pickle'lanamıyordu | `4b8d158` | tezgahta kullanıcı sınıfı pickle'lanıyor |
| Sigma/YARA tezgah ve anlatım eklemeleri | `2fed4c2` (Antigravity) | doğrulama ve tahmin kontrolleri temiz |
| Küçük notlar (serbest metin terimi, Kusto tarih gösterimi, `startsWith`/`match`, `isnull`) | `ae18f5e` | |
| PowerShell yolunun açıklaması olmayan konuları vaat ediyordu | `99885a4` | |

## Ajanlar ve kurallar

Pafta'da dört yapay zekâ çalışıyor. Hepsi aynı git kullanıcısıyla (`demomeister`) commit ettiği için kimin ne yaptığı commit mesajındaki imzadan anlaşılır.

| Ajan | Ürün | Ne yaptı | İmza |
|---|---|---|---|
| Yazar 1 | Claude | Sigma/YARA dışındaki yollar; denetim düzeltmelerinin çoğu (`8702ea3`, `4b8d158`, `1f5c8e8`, `ae18f5e`, `dcd8375`) | `Ajan: Claude (Yazar 1)` |
| Yazar 2 | ChatGPT/Codex | Sigma ve YARA (`ed6e89d`), YARA eşik örnekleri (`00bec2a`), TryHackMe kapsam belgesi | `Ajan: Codex` |
| Yazar 3 / ikinci denetçi | Antigravity (Google, Gemini) | Sigma/YARA tezgah ve anlatım eklemeleri (`2fed4c2`), PowerShell Başpehlivan PS19–PS21, KQL (Kusto) adı ve iki sınır testi (`f6241cf`), DEGERLENDIRME.md güncellemesi (`ac5e308`); görev talimatı raporu | `Ajan: Antigravity` |
| Denetçi | Claude | bu dosya ve DEGERLENDIRME.md; ders yazmaz | `Ajan: Claude (Denetçi)` |

**Kalıcı kural (A28'den):** Antigravity'nin raporundaki hiçbir doğrulama, sayım ya da araç çıktısı denetçi aynı ölçümü kendisi yapmadan kabul edilmez; raporlarında yalnızca gerçekten çalıştırılan komutlar ve çıktıları aynen yer alır. Diğer yazarların raporları da aynı şekilde ölçülür, ama Antigravity'de bu bilerek sıkı tutulur.

Birbirlerine mesaj gönderemezler; kullanıcı aktarır.

- **İmza:** her commit mesajının son satırı ajanın imzası (yukarıdaki tablo).
- **Tek yazar:** aynı yolda ya da aynı dosyada aynı anda tek ajan çalışır. Bir ajan bir görev listesini alınca öteki ajanlar o listedeki dosyalara dokunmaz. Antigravity'nin `f6241cf`'i başka yazarların yollarına (PowerShell, KQL, Python, PHP) ve ortak dosyalara dokundu; içerik denetimden temiz geçti, ama ileride iş bölümü kullanıcıyla netleşmeden başkasının yoluna girilmemeli.
- Ortak dosyalar (`sandbox/py_harness.py`, `engine/*.py`, `web/*.js`, `README.md`, `tracks/sql/ornek.sql`, `tools/validate.py`): düzenlemeden önce `git status`'a bak, bitince hemen commit et.
- `git add -A` ya da `git commit -a` yok: yalnızca kendi dosyalarını ekle.
- Yazarlar bu dosyada bir maddeyi kapatabilir; denetçi bir sonraki denetimde ölçerek onaylar.
