# Pafta · Denetim

Son denetim: 2026-10-21, `0780eaf`: 366 ders, 3151 kontrol temiz, hem normal Windows ortamında hem Git Bash'ten. AD yolu (`26ddfbd`) ikinci bir Claude tarafından denetlendi, bulgular A15–A22. Assembly yolu (`f3ff403`) teslim edildi, denetim bekliyor. Elastic yazma yükseltmesi sürüyor (Codex, ara commit `e97a855`).

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
| A15 | `26ddfbd` · kapsam ve imza | Ortak dosyalardaki değişiklikler yolu kaydetmeye yetecek kadar: README satırı; runners, lessons, progress, validate, py_harness, app.js, hl.js ve md.js'te AD girişleri. Değiştirilen satırlarda başkasının içeriği kaybolmamış. İki küçük sapma: `web/app.js`'teki "Okuma yolları" yorumuna AD dışı "Java, C#" eklenmiş; commit "Ajan: Antigravity" imzalı, ama hangi modelin yazdığı belirtilmemiş. | sonraki commit'lerde model adını yaz; AD dışı satıra dokunma | Antigravity |
| A16 | `sandbox/ad_engine.py` `_ps_comparison_to_ldap`; `tracks/ad/lessons/ad05`:0 (tablodaki `-gt` satırı) | `-lt` ve `-gt` `(&(x<=v)(!(x=v)))` ile `(&(x>=v)(!(x=v)))`'e çevriliyor. Microsoft'un about_ActiveDirectory_Filter tablosundaki karşılıklar `(!(x>=v))` ve `(!(x<=v))`. İkisi özniteliği olmayan nesnelerde ayrışır: `badPwdCount`'u olmayan bir kullanıcı `badPwdCount -lt 1`'de motorda gelmiyor, belgedeki biçimde gelir. AD05'in tablosu da motorun çevirisini modülün karşılığı diye öğretiyor. | çeviriyi belgedeki biçime getir, tabloyu düzelt; `-ne` TUZAK'ı gibi bir not ekle | Antigravity |
| A17 | `sandbox/ad_engine.py` `eval_ldap_ast` (1941) | `1.2.840.113556.1.4.1941` yalnızca `member` ve `memberOf`'ta çalışıyor, başka bir DN özniteliğinde sessizce `False` veriyor. AD'de bu kural DN değerli her öznitelikte zinciri izler. Üç kişilik bir `manager` zincirinde `(manager:1.2.840.113556.1.4.1941:=CN=Patron,...)` motorda boş dönüyor; beklenen sonuç Mudur ve Calisan. Dizinde ve derslerde `manager` olmadığı için bugün görünmüyor. | zinciri öznitelikten bağımsız yürüt | Antigravity |
| A18 | `sandbox/ad_engine.py` `translate_ps_filter_to_ldap` | Gerçek modülün `-Filter` işleçlerinden `-band`, `-bor`, `-recursivematch` ve `-approx` desteklenmiyor; dördü de sözdizimi hatası veriyor. | ekle ya da tezgahın sınırı olarak derste söyle | Antigravity |
| A19 | `sandbox/ad_engine.py` Get-AD* katmanı | Üç küçük sadakat farkı: (1) `-SearchScope 1` gibi sayısal değerler reddediliyor; modülde enum değeri olarak geçerli. (2) `-eq '*'` ve `-ne '*'` varlık ve yokluk sorgusuna çevriliyor; belge `-eq`'in joker desteklemediğini söylüyor, gerçek modülde doğrulanmalı. (3) Varsayılan tablo sütunlarında, Get-ADUser'ın varsayılan özellik kümesinde olmayan `userAccountControl` ve `objectCategory` var. | | Antigravity |
| A20 | `sandbox/ad_engine.py` LDAP ayrıştırıcısı | RFC 4515 dilbilgisi dışındaki yazımlar kabul ediliyor: `( cn=x)` ve `(cn =x)` geçerli sayılıyor. Değerin sonundaki boşluk da atılıyor: `(description=AB )` "AB"yi buluyor; bu kısım RFC 4518'in önemsiz boşluk kuralına göre zararsız olabilir. 3.084 filtrelik karşılaştırmada motorla bağımsız değerlendirici arasındaki farkların hepsi bunlar. | boşlukları hata say | Antigravity |
| A21 | `tracks/ad/lessons/ad09`:0 (4625 satırı) | `0xC000006E` "süre kısıtı" diye geçiyor. Bu kod genel hesap kısıtıdır (STATUS_ACCOUNT_RESTRICTION); oturum saati kısıtı `0xC000006F`'dir. | "hesap kısıtı" yaz; saat kısıtı için `0xC000006F` | Antigravity |
| A22 | `tracks/ad/lessons` ad06:3, ad04:5, ad11:3 (testler) | Mutasyon testinde 109 mutantın 96'sı yakalandı. Hayatta kalan 13 mutantın 10'u tek bitlik maskede 803↔804 değişimi: eşdeğer, zararsız. Üç zayıf test var: ad06:3 "Windows 10 ile başlayan" sistemleri istiyor, ama `-like "*Windows 10*"` geçiyor (testte başında başka metin olan bir sistem yok). ad04:5 ve ad11:3'te 804 maskesine görevle ilgisiz bir bit eklemek (4194336 → 4194337, 4718624 → 4718625) yakalanmıyor; testte yalnızca ilgisiz bir biti açık olan etkin bir hesap yok. | sınır nesnelerini `dene(ek=...)` ile ekle | Antigravity |

**AD yolu (`26ddfbd`) sıkı denetimi** (Claude, AD denetçisi). Ölçümler `git archive 26ddfbd` ile çıkarılan anlık görüntüde yapıldı.
- **Validate:** AD yolu 12 ders, 119 kontrol temiz; hem PowerShell'de (`NoDefaultCurrentDirectoryInExePath` kaldırılarak) hem Git Bash'te.
- **Tahminler:** 12 tahminin hepsi gerçek çıktıyla uyuşuyor.
- **Motor karşılaştırması:** `ad_engine.py`, ona bakılmadan yazılmış bağımsız bir RFC 4515 değerlendiricisiyle 84 elle seçilmiş ve 3.000 rastgele filtrede karşılaştırıldı. Dizin olarak `dizin.json` ile kaçış, joker ve döngülü grup için eklenmiş nesneler kullanıldı. Anlamca tek fark yok; yalnızca A20'deki yazım hoşgörüsü çıktı. Şunlar doğru: büyük-küçük harf, joker konumları, varlık, `>=` ve `<=` (`>` ve `<` reddediliyor), `\2a \28 \29 \5c` kaçışları, 803 ve 804, 1941 (iki yönde, iç içe gruplarda ve döngüde sonsuza girmeden).
- **Dizin verisi:** `dizin.json`'daki `userAccountControl` ve `groupType` değerleri tutarlı (66048 = 512 + 65536; DC 532480 = 8192 + 524288; Guest 66082). İki `adminCount=1` sapması bilinçli: ali.kaya'daki kalıntı dersin konusu, DC hesabında ise gerçekte de 1'dir.
- **Ders iddiaları:** UAC bayrakları, groupType bitleri, birincil grubun `memberOf`'ta görünmemesi, AdminSDHolder ve SDProp, 4624/4625/4720/4728/4732/4756/4740/4768/4769/4771 olayları ve Logon Type 2/3/10 Microsoft belgeleriyle uyuşuyor; tek hata A21.
- **Not:** Anlık görüntüde tam depo validate'i paket, Sigma ve YARA yollarında hata verir, çünkü git'e girmeyen `.deps` klasörü yok; bu bir AD bulgusu değil.
- **Denetçinin doğrulaması** (Claude, Denetçi): A16 ve A21 belgeyle kontrol edildi. A16: about_ActiveDirectory_Filter'ın işleç tablosu `-lt` için `!x >= y`, `-gt` için `!x <= y` veriyor; bulgu doğru. Aynı belgenin 3. örneği (`badpwdcount -ge 5` → `(&(!badpwdcount<=5)(badpwdcount=*))`) tabloyla çelişiyor, yani belge kendi içinde tutarsız. Düzeltmede tablo esas alınsın, ders bunu "belgeye göre" diye söylesin ve son dersteki kendi AD laboratuvarında denenmesini önersin. A21: 4625 sayfasının izlenecek kodlar tablosunda `0xC000006F` "User logon outside authorized hours" olarak geçiyor, `0xC000006E` orada yok; NTSTATUS listesinde genel hesap kısıtıdır (`STATUS_ACCOUNT_RESTRICTION`), saat kısıtı yalnızca örneklerinden biridir. Bulgu doğru.

## Planlanan yeni yollar

Kullanıcının hedefi THM ve HTB'nin mavi ve kırmızı takım yollarını bitirmek. Bu yollarda karşısına çıkacak ama Pafta'da olmayan diller, kullanıcının çalışma sırasında ne zaman gerekeceğine göre sıralandı. Seviye kararı, konunun en üst sertifika ve kurslarda hangi derinlikte istendiğine göre denetçi tarafından verildi (kullanıcının isteği). Yazarlar: **Codex** kendi yarım işini (paket yolu PK10–PK18) ve Elastic'in yazmaya yükseltilmesini bitirir; **Antigravity** sırayla C#, Active Directory ve LDAP, assembly ve Snort/Suricata'yı yazar (Java'yı `cae6531` ile kurallara uyarak teslim etti). Yazar 1 (Claude) bu yollarda otomatik güvenlik denetimine takıldığı için yeni yol yazmıyor. Ortak dosyalara (`engine/`, `web/`, `README.md`) dokunmadan önce `git status`: ötekinin commit edilmemiş değişikliği varsa bekle. Her yol bitince durulur, denetçi ölçer, sonra sıradakine geçilir.

| Sıra | Yol | Seviye | Ölçüt | Tezgah | Durum |
|---|---|---|---|---|---|
| — | Kibana KQL, Lucene ve EQL | **net** (yazma) | Elastic Certified Analyst, THM SOC L2 / SAL2: sorgular yazılır | şu an okuma; Codex'in gizli Python modelleri yazılan sorguyu değerlendiren bir tezgaha çevrilecek | yapıldı (`6b0d21a`, okuma); **yazmaya yükseltiliyor** (Codex): motorlar ara commit `e97a855`'te, dersler ve arayüz bağlantısı commit edilmedi |
| 1 | CMD/batch | **net** | Windows olay inceleme kursları ve sertifika sınavlarında komut satırı yazılarak kullanılır | gerçek `cmd.exe` | **yapıldı ve denetlendi** (Codex, `208ec11`): 18 ders, 107 kontrol temiz, 36 görevde zayıf test yok; bkz. A10 |
| 2 | HTTP ve HTML | HTTP **net**, HTML **okuma** | Web sertifikalarında (HTB CWES, Burp Suite Certified Practitioner) ham istek yazılır, sayfa kaynağı okunur | Python ile gerçek istek ve yanıt | **yapıldı ve denetlendi**: HT01–HT13 Yazar 1 (`5e4b604`), HT14–HT15 Codex (`87be609`, `55f94f4`); 15 ders, 130 kontrol temiz; bkz. A13 |
| 3 | Wireshark görüntü filtreleri ve tcpdump/BPF | **net** | Wireshark Certified Network Analyst ve SANS SEC503'te iki filtre dili de yazılır | görüntü filtreleri gerçek `tshark` 4.6.8 ile örnek kayıt dosyalarında; BPF için gerçeğe sadık değerlendirici (tcpdump kurulu değil) | **yapıldı ve denetlendi** (Codex, `cd72585` + `0780eaf`): 18 ders, 126 kontrol temiz; 18 tahmin doğru; 36 görevde zayıf test yok. Görüntü filtreleri gerçek TShark 4.6.8, BPF gerçek libpcap 1.10.6 ile çalışıyor (Npcap gerekmiyor) |
| 4 | Java | **okuma** (derin kod okuma) | Beyaz kutu web sertifikalarında (OSWE, HTB CWEE) kaynak kodu okunur, uygulama yazılmaz | okuma yolu (`okuma_dili`), görevler Python'da; tahmin cevapları gerçek JDK 21 (Android Studio) ile üretildi | **yapıldı ve denetlendi** (Antigravity, `cae6531`): 12 ders, 6 rütbe, 62 kontrol temiz; 12 tahminin 12'si denetçinin gerçek JDK 21 çalıştırmasıyla birebir aynı; 25 görevde zayıf test yok; commit yalnızca izin verilen dosyalara dokunuyor |
| 5 | C# (.NET) | **okuma** (derin kod okuma) | Beyaz kutu web sertifikalarında (OSWE, HTB CWEE) kaynak kodu okunur, uygulama yazılmaz | okuma yolu (`okuma_dili`), görevler Python'da; tahmin cevapları gerçek .NET 8 SDK ile üretildi | **yapıldı ve denetlendi** (Antigravity, `39db1e3`): 12 ders, 6 rütbe, 62 kontrol temiz; 12 tahminin 12'si denetçinin gerçek .NET 8 çalıştırmasıyla birebir aynı; 25 görevde zayıf test yok; commit sınırların içinde |
| 6 | Snort/Suricata kuralları | **net** | SANS SEC503 ve HTB Detection Engineer yolunda kural yazılır | gerçek Suricata (kullanıcı resmi Windows sürümünü kurarsa, kayıt dosyalarında çevrimdışı); kurulmazsa okuma + değerlendirici | bekliyor · **Antigravity**, kullanıcı Npcap ve Suricata'yı kurduktan sonra |
| 7 | **Active Directory ve LDAP** (A9 ile birleşti) | LDAP filtreleri ve `Get-AD*` sorguları **net**, AD kavramları **okuma** | AZ-040'ın AD yönetimi ve AD kurslarında filtre ve sorgu yazılır; amaç, aboneliği olmayan birinin de AD'yi öğrenebilmesi | sahte ama gerçeğe sadık bir dizin (kullanıcı, grup, bilgisayar, OU verisi); üzerinde RFC 4515'e sadık LDAP filtre değerlendiricisi ve `Get-ADUser`/`Get-ADGroup`/`Get-ADGroupMember`/`Get-ADComputer` (`-Filter`, `-LDAPFilter`, `-Properties`, `-SearchBase`) taklidi; içerik yönetim ve savunma tarafında (yapı, sorgu, hesap denetimi, AD günlükleri). Son ders: Windows Server değerlendirme sürümüyle kendi AD laboratuvarını kurmak. Sınırı derste açıkça yazılsın: gerçek Kerberos, GPO ve çoğaltma yok | **yapıldı, denetlendi, düzeltme bekliyor** (Antigravity, `26ddfbd`): 12 ders, 119 kontrol temiz; 12 tahmin doğru; motor bağımsız RFC 4515 değerlendiricisiyle 3.084 filtrede anlamca aynı. Açık bulgular A15–A22 (ikinci Claude denetimi, `546b788`) |
| 8 | x86/x64 assembly kavramları | **okuma** | THM Red Teaming ve hedeflenen HTB yolları kavram ve okuma düzeyinde ister | okuma yolu | **teslim edildi, denetim bekliyor** (Antigravity, `f3ff403`): 12 ders (AS01–AS12); commit'te model adı yok |

Mevcut yollara küçük eklemeler (SQL görünümleri, Bash başlangıç dosyaları, KQL `render`, JS `Map`/`Set`, C çok dosyalı programlar, PHP `namespace`/`trait`) **yapıldı ve denetlendi** (Yazar 1).

## Kapanan bulgular

| Bulgu | Commit | Denetçinin kanıtı |
|---|---|---|
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

Birbirlerine mesaj gönderemezler; kullanıcı aktarır.

- **İmza:** her commit mesajının son satırı ajanın imzası (yukarıdaki tablo).
- **Tek yazar:** aynı yolda ya da aynı dosyada aynı anda tek ajan çalışır. Bir ajan bir görev listesini alınca öteki ajanlar o listedeki dosyalara dokunmaz. Antigravity'nin `f6241cf`'i başka yazarların yollarına (PowerShell, KQL, Python, PHP) ve ortak dosyalara dokundu; içerik denetimden temiz geçti, ama ileride iş bölümü kullanıcıyla netleşmeden başkasının yoluna girilmemeli.
- Ortak dosyalar (`sandbox/py_harness.py`, `engine/*.py`, `web/*.js`, `README.md`, `tracks/sql/ornek.sql`, `tools/validate.py`): düzenlemeden önce `git status`'a bak, bitince hemen commit et.
- `git add -A` ya da `git commit -a` yok: yalnızca kendi dosyalarını ekle.
- Yazarlar bu dosyada bir maddeyi kapatabilir; denetçi bir sonraki denetimde ölçerek onaylar.
