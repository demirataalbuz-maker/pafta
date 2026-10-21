# Pafta · Denetim

Son denetim: 2026-10-21, `33ed7f2` (GitHub'daki son hâl; bekleyen commit yok). 12 yol, 271 ders. Bütün ders kimlikleri **yeni numaralardır** (`dcd8375` ile harita sırasına göre yeniden numaralandı); eski raporlardaki kimlikler için [tools/numara_eslemesi.json](tools/numara_eslemesi.json). Bu dosyanın eski, ayrıntılı sürümleri git geçmişinde: `git log -p DENETIM.md`.

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
| A9 | PowerShell · Active Directory | Kullanıcının ilk dil listesinde "AD" vardı, hiç yazılmadı (`Get-ADUser`, `Get-ADGroupMember`, DN/OU yapısı, LDAP filtreleri yok). Tezgahta etki alanı olmadığı için ancak dışa aktarılmış veriyle ya da okuma düzeyinde kurulabilir. Not: aynı rapordaki "Başpehlivan boş", "Security günlüğü yok", "Sysmon yok" bilgileri eskiydi; üçü de `f6241cf` ile PS19–PS21'de var. | AZ-040'ın AD yönetimi çerçevesinde bir köprü ders | düşük öncelik; **kullanıcı kararı** |

## Planlanan yeni yollar

Kullanıcının hedefi THM ve HTB'nin mavi ve kırmızı takım yollarını bitirmek. Bu yollarda karşısına çıkacak ama Pafta'da olmayan diller, kullanıcının çalışma sırasında ne zaman gerekeceğine göre sıralandı. Seviye kararı, konunun en üst sertifika ve kurslarda hangi derinlikte istendiğine göre denetçi tarafından verildi (kullanıcının isteği). Yazarlar: **Codex** CMD/batch, Wireshark/tcpdump, Snort/Suricata, Elastic yükseltmesi ve assembly; **Yazar 1 (Claude)** HTTP/HTML, Java, C# ve LDAP filtreleri (nötr konular; Claude oturumları tespit kuralı ve alt seviye içerikte otomatik güvenlik denetimine takılıyor). İki yazar aynı anda farklı yollarda çalışabilir, ama yeni yolu kaydetmek için ortak dosyalara (`engine/`, `web/`, `README.md`) dokunulacağı zaman önce `git status`: ötekinin commit edilmemiş değişikliği varsa bekle. Her yol bitince durulur, denetçi ölçer, sonra sıradakine geçilir.

| Sıra | Yol | Seviye | Ölçüt | Tezgah | Durum |
|---|---|---|---|---|---|
| — | Kibana KQL, Lucene ve EQL | **net** (yazma) | Elastic Certified Analyst, THM SOC L2 / SAL2: sorgular yazılır | şu an okuma; Codex'in gizli Python modelleri yazılan sorguyu değerlendiren bir tezgaha çevrilecek | yapıldı (`6b0d21a`, okuma); **yazmaya yükseltilecek** |
| 1 | CMD/batch | **net** | Windows olay inceleme kursları ve sertifika sınavlarında komut satırı yazılarak kullanılır | gerçek `cmd.exe` (PowerShell yolu gibi süreç koşucusu) | sıradaki |
| 2 | HTTP ve HTML | HTTP **net**, HTML **okuma** | Web sertifikalarında (HTB CWES, Burp Suite Certified Practitioner) ham istek yazılır, sayfa kaynağı okunur | Python ile gerçek istek ve yanıt | bekliyor |
| 3 | Wireshark görüntü filtreleri ve tcpdump/BPF | **net** | Wireshark Certified Network Analyst ve SANS SEC503'te iki filtre dili de yazılır | görüntü filtreleri gerçek `tshark` 4.6.8 ile örnek kayıt dosyalarında; BPF için gerçeğe sadık değerlendirici (tcpdump kurulu değil) | bekliyor |
| 4 | Java | **okuma** (derin kod okuma) | Beyaz kutu web sertifikalarında (OSWE, HTB CWEE) kaynak kodu okunur, uygulama yazılmaz | okuma yolu (`okuma_dili`), görevler Python'da; JDK kurulmayacak | bekliyor |
| 5 | C# (.NET) | **okuma** (derin kod okuma) | aynı ölçüt | okuma yolu, ama **.NET 8 SDK kurulu** olduğundan tahmin cevapları gerçek çalıştırmayla üretilsin | bekliyor |
| 6 | Snort/Suricata kuralları | **net** | SANS SEC503 ve HTB Detection Engineer yolunda kural yazılır | gerçek Suricata (kullanıcı resmi Windows sürümünü kurarsa, kayıt dosyalarında çevrimdışı); kurulmazsa okuma + değerlendirici | bekliyor |
| 7 | LDAP filtreleri | **net** | AD yönetimi ve AD kurslarında filtre yazılır | standart kütüphaneyle RFC 4515'e sadık değerlendirici | bekliyor |
| 8 | x86/x64 assembly kavramları | **okuma** | THM Red Teaming ve hedeflenen HTB yolları kavram ve okuma düzeyinde ister | okuma yolu | bekliyor |

Mevcut yollara küçük eklemeler (SQL görünümleri, Bash başlangıç dosyaları, KQL `render`, JS `Map`/`Set`, C çok dosyalı programlar, PHP `namespace`/`trait`) kullanıcı birkaç ders bitirdikten sonraya bırakıldı.

## Kapanan bulgular

| Bulgu | Commit | Denetçinin kanıtı |
|---|---|---|
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
