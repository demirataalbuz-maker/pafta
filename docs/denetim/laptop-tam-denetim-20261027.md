# Pafta — bu laptopun kabul raporu

Ölçüm kaydı: 2026-10-27T19:06:45.636274+00:00

**Otomatik tarama tamamlandı; aşağıdaki dış laboratuvar kabulleri açık.**

Kapsam: 23 yol, 543 kayıtlı ders, Windows ve Git Bash çalıştırmaları ve 108 denetim maddesinin bunlara eşlenmesi. Bu bir çalışma kabulüdür; yeni veya bağımsız bir kalite puanlaması değildir. AI-Ek ve model kurulumu Kimi kapsamındadır. Commit/push yapılmadı.

[Laptop durum paneli](LAPTOP_DURUM.html) · [Kalite puan paneli](DENETIM_SAYFASI.html) · [543 ders / 108 madde ham özeti](../../outputs/audit-20261027/summary.json) · [Regresyon denemeleri](../../outputs/audit-20261027/regression-summary.json)

## Sonuçları nasıl okumalı

Kalite JSON’undaki 108 maddenin tamamı A aralığında. Bu tur sayısal puanları değiştirmedi. #60’ın 91, #105’in 91, #108’in 92 puanı önceki yazar öz değerlendirmesidir; bağımsız yeniden puanlama bekler. Kalite panelindeki Kısmen kararları #37, #60 ve #63 için korunur.

| Bu laptopun madde durumu | Adet |
|---|---:|
| Geçti | 90 |
| Referans geçti; test geri bildirimi eksik | 10 |
| Lab/bağımlılık engeli | 5 |
| Canlı kabul kısmen | 3 |

Ders durumları: Geçti: 484, Lab/bağımlılık engeli: 8, Referans geçti; test geri bildirimi eksik: 51.

| Otomatik iş türü | Kaydedilen sonuçlar |
|---|---|
| ornek | {'PASS': 1858, 'BLOCKED': 4} |
| tahmin | {'PASS': 1062, 'BLOCKED': 16, 'DECLARED': 172} |
| starter | {'PASS': 2678, 'BLOCKED': 18, 'ERROR': 150} |
| solution | {'PASS': 2822, 'BLOCKED': 24} |

PASS, ilgili örnek/görev çalıştırmasının veya hatalı başlangıç kodunu reddetme kontrolünün geçtiğidir. BLOCKED işler PASS sayılmadı. DECLARED, koşucunun yeniden çalıştırmadığı hazır tahmin çıktısıdır. C/C#/Java/ASM/PHP okuma yollarındaki Python alıştırması kabulü, o yolun bütün örneklerinin yerel derleyicide yeniden üretimi değildir. JPA, Spring Security, Thymeleaf/FreeMarker ve System.Web için ayrıca gerçek motor kabulü alındı.

## Bu tur giderilen sorunlar

- MySQL ve SQL Server’ın mevcut parolaları ile Pafta yapılandırması uyuşmuyordu. İki sunucuda gerçek SELECT 1 ile doğrulandı; önceki yerel ayar özel yedeğe alındı, veritabanları silinmeden bağlantı düzeltildi. Kimlik doğrulama hatası artık 100 saniyelik hazır olma döngüsünde gizlenmez. [Tanı testi](../../outputs/audit-20261027/extra/laptop_preflight.log).
- Açık Windows oturumunun eski PATH/JAVA_HOME ortamı kurulu Java ve Docker’ı göremiyordu. Pafta başlatıcısı, sunucu ve Java yeniden üretim araçları kayıtlı yolları yalnız kendi süreçlerinde tamamlar; açıkça verilmiş süreç ayarları korunur. Kayıt defterine yazılmaz. [Gerçek uygulama API kabulü](../../outputs/audit-20261027/startup-environment-acceptance.json).
- Kali root altında Bash Röntgen izi boştu. İz öneki betiğin içinde tanımlandı ve satır kayması düzeltildi. Windows/Git Bash × yerel Bash/Kali Bash dört birleşimi geçti. WSL’nin 16 yaşam döngüsü ve alt süreç temizleme testi geçti. [Windows](../../outputs/audit-20261027/trace-windows.json), [Git Bash](../../outputs/audit-20261027/trace-gitbash.json), [WSL](../../outputs/audit-20261027/retries/wsl_runtime-final.log).
- Onaylanan Maven 3.9.16 ve sabit Java bağımlılıkları kuruldu. JPA’nın Türkçe stderr çözümleme hatası giderildi; varsayılanı çevrimdışı yapıldı ve süreç süre sınırları eklendi. JPA/Security/şablon motorları mevcut önbellekle ve eski terminal ortamında tekrar çalıştı. [100 JAR hash manifesti ve JPA/System.Web karşılaştırmaları](../../outputs/audit-20261027/java-native/runtime-manifest.json), [Java CLI kabulü](../../outputs/audit-20261027/java-native/default-environment-acceptance.json).
- #60 için resmi örnek toplama gerçek BloodHound CE 9.9.0’a yüklendi. Üç SID ile MemberOf → WriteDacl kenarları AD14 çözümüyle birebir eşleşti. İmaj digest’leri kayıtlı, API yalnız 127.0.0.1:18080 üzerinde. [Gerçek Cypher yanıtı](../../outputs/audit-20261027/bloodhound-ce/acceptance.json). Bu, gerçek DC AccessCheck kabulünü kapatmaz.
- Eski AD/P78/PU14/PU17 görev sayısı beklentileri yeni kayıtlarla eşlendi. Türkçe Sigcheck yanıtı ders açıklamasına eklendi. Artık desteklenen RAW LINKTYPE 101’i geçersiz sayan BPF testi düzeltildi; desteklenmeyen 147 ve gerçek RAW filtreleme ayrı sınandı.
- Denetçi, eksik AD/CIM motorunda hatalı başlangıç kodunun da PASS sayılmasını engelleyecek şekilde sıkılaştırıldı. Önceki denemeler ve gerçek runner hata kayıtları saklanır. Uzun testlerde ilk 180 saniye sınırına takılanlar yeterli süreyle yeniden çalıştırıldı; zaman aşımı başarı sayılmadı.
- README’deki eski ders sayıları, eksik IDS satırı ve KQL’in artık geçerli olmayan SQLite çevirici açıklaması güncellendi. İçerik kaydı, kalite puanı ve bu makinenin kabulü ayrı bağlantılara bağlandı.

## Açık kalan gerçek gereksinimler

| Madde | Yol / ders | Durum | Kalan |
|---|---|---|---|
| #18 Gerçek PSSession yaşam döngüsü ve uzak çıktı | powershell: ps29 | Lab/bağımlılık engeli | Pafta AD laboratuvarı kurulmamış. tools/setup_ad_vm.py ile bir kez kurun. |
| #37 Avcılık sorgusundan zamanlanan Sentinel kuralına | kql: kq22 | Canlı kabul kısmen | Sentinel çalışma alanında portal Test with current data / Review kabulü yok. |
| #39 CIM ve tstats gerçek veri modelinde | spl: sp23 | Lab/bağımlılık engeli | Error in 'DataModelEvaluator': Data model 'Web' was not found.; Error in 'DataModelEvaluator': Data model 'Web' was not found.; Error in 'DataModelEvaluator': Data model 'Authentication' was not found.; Error in 'DataModelEvaluator': Data model 'Authentication' was not found.; Error in 'DataModelEvaluator': Data model 'Endpoint' was not found.; Error in 'DataModelEvaluator': Data model 'Endpoint' was not found. |
| #45 sigma-cli, gerçek backend ve processing pipeline | sigma: sg19 | Lab/bağımlılık engeli | 400 /services/search/jobs: Error in 'SearchParser': The search specifies a macro 'drop_dm_object_name' that cannot be found. Reasons include: the macro name is misspelled, you do not have "read" permission for the macro, or the macro has not been shared with this application. Click Settings, Advanced search, Search Macros to view macro information. |
| #60 Nesne ACL'lerinden erişim yolu çıkarmak | ad: ad13, ad14, ad15 | Canlı kabul kısmen | Gerçek BloodHound CE yolu doğrulandı; gerçek AD/DC AccessCheck kabulü yok. |
| #61 Mevcut devir türlerine gerçek S4U/bilet akışı ve doğrulama | ad: ad16, ad17, ad18 | Lab/bağımlılık engeli | Pafta AD laboratuvarı kurulmamış. tools/setup_ad_vm.py ile bir kez kurun. |
| #62 AD CS ve sertifika şablonu/izin denetimi | ad: ad19, ad20, ad21 | Lab/bağımlılık engeli | Pafta AD laboratuvarı kurulmamış. tools/setup_ad_vm.py ile bir kez kurun. |
| #63 Gerçek LDAP bağlantısında TLS, imzalama ve channel binding | ad: ad22, ad23 | Canlı kabul kısmen | Gerçek DC LDAP/TLS/signing/CBT ve ldp.exe GUI kabulü yok. |

- **AD/DC/CA/KDC:** Yönetilen AD laboratuvar yapılandırması, VMware vmrun ve gerekli yerel medya hazır değil. AD15/AD18/AD21–23 ve PS29’un canlı bölümleri kabul edilmedi. Mevcut koşucu VMware tabanlıdır. Windows 11 Pro’da Hyper-V seçeneği ayrıca değerlendirilebilir; mevcut koşucu için ayrı uyarlama ve gerçek VM kabulü gerekir. Üretim alanına bağlanılmadı, VM varmış gibi gösterilmedi.
- **Sentinel:** Erişilebilir gerçek çalışma alanı ve portal Test with current data / Review kanıtı doğrulanmadı. Azure CLI/profil bulunmaması hesabın olmadığı kanıtı değildir. Yerel Kusto iki kabukta geçti; ücretli abonelik veya Azure kaynağı oluşturulmadı.
- **CIM:** Yerel CIM arşivi ve Splunk_SA_CIM uygulaması yok. Gerçek Splunk Web veri modeli bu nedenle bulunamadı. Paket `.deps/splunk/splunk-common-information-model-cim_850.tgz` yolunda beklenir; mevcut kurucu 8.5.0 ve kabul edilen SHA-256 `ed93ba614f12805ab428d71d45053ced12ce2ff1198b2f46b48537c0e0d6a412` ile sınırlıdır. Splunkbase indirmesi oturum ister. Listede görünen güncel sürümü sabit 8.5.0’ın yerine otomatik koymadım; bu ayrıca sürüm kabulü gerektirir. Sigma SG19’da eksik çıkan `drop_dm_object_name` da resmi CIM uygulamasının dış makrosudur; [Splunk’ın uygulama bağımlılık bildirimi](https://github.com/splunk/security_content/blob/develop/build.yml) ve [Sigma backend üretimi](https://github.com/SigmaHQ/pySigma-backend-splunk/blob/main/sigma/backends/splunk/splunk.py) bunu doğrular. Makroyu veya veri modelini yerel taklit ile doldurmadım.
- **Gerçek bellek imajı:** PU10’un çevrimdışı fixture/test vektörleri geçti; gerçek bir imaj üzerinde Volatility canlı testi atlandı. Bu yol için canlı bellek kabulü iddia edilmez.

## Test kalitesi ve geliştirme sırası

Bazı başlangıç kodları beklenen biçimi döndürmediğinde test kodu açık bir başarısız kontrol yerine KeyError/TypeError veya eksik çıktı dosyası hatası veriyor. İlgili referans çözümler geçti; bunlar motor kurulumu eksikliği olarak sayılmadı. Durum panelinde WARN ile görünür. Bu geri bildirim kusurları için dönüş şeması/dosya varlığı kontrolleri eklemek uygun bir sonraki kalite işidir.

Test geri bildirimi için işaretlenen Aşama 2 maddeleri (çalışan referans / WARN):

| Madde | Dersler |
|---|---|
| #7 Impacket ile Windows/AD protokol betiğini okumak | p78, p79 |
| #12 ShellCheck ve Bats ile kendi aracını sınamak | bs30 |
| #20 wevtutil ile offline EVTX sorgu ve export | cm19, cm20 |
| #22 Token, grup, ayrıcalık ve icacls | cm23, cm24 |
| #26 Gerçek tarayıcıda CORS/preflight ve CSRF | ht19, ht20 |
| #28 JWT, imza tuzakları ve OAuth2/OIDC | ht16 |
| #59 Gerçek CLI ile toplama, alan çıkarma ve özet | pk28, pk29 |
| #102 Bitirme (savunma): uçtan uca olay incelemesi | bt01, bt02, bt03, bt04 |
| #105 Oltalama e-postası analizi | pu14 |
| #106 Windows adli izleri | pu15 |

1. Resmi CIM 8.5.0 arşivini edinip mevcut doğrulayıcıyla kurmak; yalnız etkilenen SP23/Sigma derslerini yeniden ölçmek. Bu en küçük dış bağımlılık kapanışıdır.
2. İzole gerçek AD laboratuvarını kurmak. Birden çok açık maddeyi birlikte kapatır. Mevcut VMware yolu veya ayrıca geliştirilecek Hyper-V yolu, resmi medya ve lisans koşullarıyla seçilmeli.
3. Erişimi olan mevcut bir Sentinel çalışma alanında KQ22 portal kabulünü tamamlamak. Kusto Emulator bu hizmet adımını üstlenmez.
4. Başlangıç kodu testlerine açık şema/çıktı kontrolleri eklemek; hazır gercek bloklarını sürüm/hash bilgili gerçek yeniden üretim komutlarına bağlamak.
5. Pafta içine motor sağlık göstergesi ve laboratuvar aç/kapat akışı eklemek. Bağımlılık sürüm manifestiyle birlikte bu, yeni bilgisayara aktarımı ve RAM yönetimini kolaylaştırır. Bu yeni ürün akışını bu denetimde eklemedim.

## Yol bazında kanıt

| Yol | Ders | Laptop ders durumları | Windows | Git Bash |
|---|---:|---|---|---|
| ad | 25 | {'PASS': 20, 'BLOCKED': 5} | [JSON](../../outputs/audit-20261027/windows/ad.json) | [JSON](../../outputs/audit-20261027/gitbash/ad.json) |
| asm | 16 | {'PASS': 16} | [JSON](../../outputs/audit-20261027/windows/asm.json) | [JSON](../../outputs/audit-20261027/gitbash/asm.json) |
| bash | 35 | {'PASS': 33, 'WARN': 2} | [JSON](../../outputs/audit-20261027/windows/bash.json) | [JSON](../../outputs/audit-20261027/gitbash/bash.json) |
| bitirme | 7 | {'PASS': 6, 'WARN': 1} | [JSON](../../outputs/audit-20261027/windows/bitirme.json) | [JSON](../../outputs/audit-20261027/gitbash/bitirme.json) |
| c | 17 | {'PASS': 16, 'WARN': 1} | [JSON](../../outputs/audit-20261027/windows/c.json) | [JSON](../../outputs/audit-20261027/gitbash/c.json) |
| cmd | 25 | {'PASS': 20, 'WARN': 5} | [JSON](../../outputs/audit-20261027/windows/cmd.json) | [JSON](../../outputs/audit-20261027/gitbash/cmd.json) |
| csharp | 17 | {'PASS': 17} | [JSON](../../outputs/audit-20261027/windows/csharp.json) | [JSON](../../outputs/audit-20261027/gitbash/csharp.json) |
| elastic | 27 | {'PASS': 27} | [JSON](../../outputs/audit-20261027/windows/elastic.json) | [JSON](../../outputs/audit-20261027/gitbash/elastic.json) |
| http | 24 | {'PASS': 22, 'WARN': 2} | [JSON](../../outputs/audit-20261027/windows/http.json) | [JSON](../../outputs/audit-20261027/gitbash/http.json) |
| ids | 5 | {'PASS': 5} | [JSON](../../outputs/audit-20261027/windows/ids.json) | [JSON](../../outputs/audit-20261027/gitbash/ids.json) |
| java | 16 | {'PASS': 16} | [JSON](../../outputs/audit-20261027/windows/java.json) | [JSON](../../outputs/audit-20261027/gitbash/java.json) |
| javascript | 16 | {'PASS': 16} | [JSON](../../outputs/audit-20261027/windows/javascript.json) | [JSON](../../outputs/audit-20261027/gitbash/javascript.json) |
| kql | 24 | {'PASS': 24} | [JSON](../../outputs/audit-20261027/windows/kql.json) | [JSON](../../outputs/audit-20261027/gitbash/kql.json) |
| packets | 29 | {'PASS': 28, 'WARN': 1} | [JSON](../../outputs/audit-20261027/windows/packets.json) | [JSON](../../outputs/audit-20261027/gitbash/packets.json) |
| php | 16 | {'PASS': 15, 'WARN': 1} | [JSON](../../outputs/audit-20261027/windows/php.json) | [JSON](../../outputs/audit-20261027/gitbash/php.json) |
| powershell | 29 | {'PASS': 28, 'BLOCKED': 1} | [JSON](../../outputs/audit-20261027/windows/powershell.json) | [JSON](../../outputs/audit-20261027/gitbash/powershell.json) |
| purple | 17 | {'PASS': 15, 'WARN': 2} | [JSON](../../outputs/audit-20261027/windows/purple.json) | [JSON](../../outputs/audit-20261027/gitbash/purple.json) |
| python | 83 | {'PASS': 51, 'WARN': 32} | [JSON](../../outputs/audit-20261027/windows/python.json) | [JSON](../../outputs/audit-20261027/gitbash/python.json) |
| regex | 24 | {'PASS': 21, 'WARN': 3} | [JSON](../../outputs/audit-20261027/windows/regex.json) | [JSON](../../outputs/audit-20261027/gitbash/regex.json) |
| sigma | 22 | {'PASS': 21, 'BLOCKED': 1} | [JSON](../../outputs/audit-20261027/windows/sigma.json) | [JSON](../../outputs/audit-20261027/gitbash/sigma.json) |
| spl | 23 | {'PASS': 22, 'BLOCKED': 1} | [JSON](../../outputs/audit-20261027/windows/spl.json) | [JSON](../../outputs/audit-20261027/gitbash/spl.json) |
| sql | 22 | {'PASS': 21, 'WARN': 1} | [JSON](../../outputs/audit-20261027/windows/sql.json) | [JSON](../../outputs/audit-20261027/gitbash/sql.json) |
| yara | 24 | {'PASS': 24} | [JSON](../../outputs/audit-20261027/windows/yara.json) | [JSON](../../outputs/audit-20261027/gitbash/yara.json) |

Ek doğrulama grupları: **66**; son durumlar **{'PASS': 64, 'SKIPPED': 1, 'BLOCKED': 1}**. Son unittest raporlarında 268 test bildirimi, 5 atlanan alt test var. Her grubun eski denemeleri, süre aşımı ve son sonucu [regresyon JSON’unda](../../outputs/audit-20261027/regression-summary.json). Bütün isteğe bağlı test dosyalarının çalıştırıldığı iddia edilmez.

Öne çıkan ek kanıtlar: paket derslerinde 29 ders / 59 görev / 29 tahmin / 313 mutasyon temiz; PU14/PU17’de 20 kasıtlı yanlış çözüm reddi; AD14’te 13 anlamsal yanlış çözüm reddi; Sentinel yerel kuralında 29 ret ve ayrıca raporlanan üç eşdeğer varyant.

## Laptop ve işletim

Windows: Microsoft Windows 11 Pro 10.0.26200; CPU: AMD Ryzen 5 220 w/ Radeon 740M Graphics; RAM: 23.3 GiB. Araç sürümleri [burada](../../outputs/audit-20261027/versions.json). Python bağımlılıkları ve son kaynak hash’leri [envanterde](../../outputs/audit-20261027/runtime-inventory.json). Maven/m2 önbelleği LOCALAPPDATA/Pafta altında; BloodHound yapılandırması/secrets `.deps/bloodhound-ce` içinde Git’ten hariçtir. Bunlar yalnız Git klonuyla başka makineye taşınmaz.

Laboratuvarlar aynı anda açık tutulmak yerine ihtiyaç sırasıyla çalıştırıldı. [Son kaynak kapatma kaydı](../../outputs/audit-20261027/cleanup.json) test sonunda üretilir. Veritabanı/disk/volume silinmez; kişisel ilerleme ve rota dosyaları kabul testlerinde geçici veri dizinlerinden ayrıdır.

Durum HTML’i bağımsız bir ölçüm anı kaydıdır; canlı motor monitörü değildir. Tarayıcı otomasyonunun file:// URL kuralı nedeniyle otomatik görsel önizleme yapılamadı; bu kısıt başka tarayıcı/yolla aşılmadı. Veri/JS/yol kontrolleri ayrı doğrulanır.

## Tekrar üretme

```powershell
python tools/audit_laptop.py --track python --output outputs/audit-20261027/windows/python.json --shell-label windows --workers 4
python tools/report_laptop_audit.py
python tools/report_laptop_regressions.py
python tools/denetim_sayfasi.py
```

Bu komutlar kurulum yapmaz. Docker isteyen yol için Docker Desktop ve gereken laboratuvar önce açılmalı. Splunk işleri ortak indeks kilidiyle seri yürür; diğer motorların kaynak sınırları da korunmalı. Bütün yolların iki kabuklu ilk çalıştırma betikleri ve yerel kurulum/kanıt yardımcıları masaüstündeki `Pafta-Codex-Araclar` klasöründe korunur.

## Resmi kaynaklar

- [SpecterOps CE kurulumu](https://bloodhound.specterops.io/get-started/quickstart/community-edition-quickstart) ve [örnek veri](https://bloodhound.specterops.io/get-started/quickstart/ce-ingest-sample-data).
- [Apache Maven 3.9.16 arşivi ve SHA-512](https://archive.apache.org/dist/maven/maven-3/3.9.16/binaries/).
- [Splunk CIM: resmi paket / Log in to Download](https://splunkbase.splunk.com/app/1621).
- [Microsoft Sentinel gerçek kural kabulü ve gereksinimler](https://learn.microsoft.com/en-us/azure/sentinel/create-analytics-rules).
- [Microsoft LDAP signing / ldp.exe kabulü](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/enable-ldap-signing-in-windows-server).
- [Microsoft Hyper-V kurulumu ve Windows gereksinimleri](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/get-started/install-hyper-v).

## Test sonu kaynak durumu

Çalışan konteynerler (lab durdurma sonrası): `[]`. WSL gözlenen durumları: `{'kali-linux': 'Stopped', 'docker-desktop': 'Stopped'}`. Docker Desktop durdu: `True`. Ölçülen boş fiziksel RAM: **11.4 GiB**.

Kali denetiminde etkileşimli oturum işareti görüldüğünden oturum zorla sonlandırılmadı; son gerçek dağıtım durumu yukarıdaki ayrı gözlemdir. Docker isteyen derse dönmeden önce `docker desktop start` veya Docker Desktop uygulamasını açın. Elastic için ayrıca `python tools/elastic_lab_setup.py --start` gerekir. Kali isteyen dersler dağıtımı otomatik başlatır. Görülen PASS ölçüm anındaki kabulü kaydeder; kapatılmış bir hizmetin şu an açık olduğu iddiası değildir.
