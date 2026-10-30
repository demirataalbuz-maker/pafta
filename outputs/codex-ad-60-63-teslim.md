# AD 60–63 teslim kaydı

Kapsam: 60 ACL/erişim yolu, 61 gerçek S4U, 62 AD CS, 63 gerçek LDAP TLS/signing/CBT. 64 bu çalışmaya dahil değildir. AD13–AD14 önceki teslimdir; bu teslim AD15–AD23 ekler. Yol altı rütbede 23 derse ulaşır; her derste tahmin vardır.

## Öğrencinin kullanımı

Pafta'nın Çalıştır/Kontrol düğmeleri gerçek Windows Server konuklarına veya Kali LDAP istemcisine gider. VM konsolu açmak ve komut kopyalamak normal ders akışının parçası değildir. Konuklar kapalıysa koşucu başlatır. Bir defalık kurulum `tools/setup_ad_vm.py --provision` ile yapılır; gereksinimler README'dedir.

| Madde | Dersler | Kabulün kapsamı |
|---|---|---|
| 60 | AD13–AD15 | Sentetik sıralı ACE/owner/grup/grafik; ayrıca gerçek svc_sql nesnesi, gerçek kullanıcı token'ı ve Windows AccessCheck ile WriteDacl; gerçek allow/deny ekle-sına-geri al |
| 61 | AD16–AD18 | Normalize yapılandırma/kanıt okuma; gerçek Windows S4U oturumu, KDC biletleri ve SMB dosya erişimi; classic/rbcd başarılı, missing/blocked başarısız |
| 62 | AD19–AD21 | Bit alanları, Enrollment/şablon değiştirme ayrımı; gerçek AD şablonları/CA yayım listesi; gerçek test kullanıcısının CSR'sine issued/pending/denied kararları |
| 63 | AD22–AD23 | Gerçek LDAPS, zorunlu StartTLS, imzalı/imzasız SASL, doğru/eksik/bozuk CBT; CA ve sunucu adı doğrulaması |

## Gerçek ortam

PF-DC01: Windows Server 2025 Standard Evaluation, build 26100; AD DS/DNS/KDC ve Enterprise CA. PF-APP01: ayrı üye sunucu. Her biri 3072 MB RAM/2 CPU/60 GB büyüyen disk. VMware host-only ağ; etki alanı pafta.test. Mevcut VM'ler kullanılmadı; ana Windows'un domain/DNS/firewall ayarları değiştirilmedi.

ISO Microsoft Evaluation Center üzerinden indirildi: https://www.microsoft.com/en-us/evalcenter/download-windows-server-2025 . Yerel ISO SHA256: `7b052573ba7894c9924e3e87ba732ccd354d18cb75a883efa9b900ea125bfd51` (yerelde hesaplanan kayıt; Microsoft'un yayımladığı bir checksum olduğu iddia edilmez). ISO boyutu 8.152.356.864 bayt.

Kali'deki mevcut istemciler: Python 3.14.7, Impacket 0.14.0.dev0, pyOpenSSL 26.4.0, cryptography 49.0.0, OpenLDAP 2.6.14. Yeni pip/apt paketi kurulmadı. Özel parola/config, diskler, sertifika anahtarları ve ISO `%LOCALAPPDATA%/Pafta/labs/ad` altında, Git dışında; rapora parola eklenmedi.

## Gözlenen ürün davranışı

S4U denemelerinde üye sunucunun SYSTEM Kerberos biletleri her denemeden önce temizlenir. Aksi halde önceki politikayla alınmış bilet/önbellek tekrarı bozabiliyordu. Başarısız denemede de gerçek klist çıktısı saklanır. Zaman aralığına göre toplanan 4769 kayıtlarında ön hesap PF-APP01$ ve TransmittedServices görüldü; yalnız pf_s4u_user adına filtrelemek Proxy kanıtını kaçırabiliyor.

CA'nın Running durumu RPC ucunun hazır olduğunu her zaman göstermedi. Yardımcı yalnız 0x800706ba başlangıç hatasını sınırlı tekrar dener; policy/enrollment reddini başarıya dönüştürmez. Legacy issued, Pending pending, Signed/Draft/Editable denied, ServerOnly issued sonucu ölçüldü. ServerOnly'nin düzenlenmesi Client Authentication EKU'suna sahip olduğu anlamına gelmez.

LDAP valid/signed/starttls başarılı; none/wrong/unsigned/bad-ca/bad-name başarısız ölçüldü. TLS CA/ad doğrulaması ile CBT/signing kontrolleri ayrı tutulur. Gerçek çıktılar `ad-live-evidence.json` içindedir.

## Sınırlar ve bakım

- Çevrimdışı kesitler tam AD/KDC/CA taklidi değildir; dersler bunu açıklar. BloodHound CE kurulmadı; grafik görevi normalize kanıtta en kısa inceleme yoludur, gerçek BloodHound taraması iddiası yoktur.
- AccessCheck yardımcı kapsamı WRITE_DAC'tır; conditional ACE/özel extended right'ların genel çözümleyicisi değildir. S4U paketi yakalanmadı; gerçek bilet/SMB/olay kanıtı vardır. RBCD nonforwardable özel durumu bu kabulde ayrıca doğrulanmış değildir.
- Sertifika düzenlenmesiyle KDC'de sertifikalı kullanıcı oturumu eşitlenmez. Güçlü eşleme/PKINIT başarısı iddia edilmez.
- PowerShell laboratuvarda Domain Admin yetkisiyle çalışır; kısıtlı yetki sandbox'ı değildir. Süreç gözetimi gerçek Windows Job Object kullanır. Aynı laboratuvarın kurulum/kanıt toplama betiklerini ders testleriyle eşzamanlı çalıştırmayın.
- Evaluation internet etkinleştirmesi yapılmadı; LicenseStatus=2 gözlendi. Microsoft ilk 10 gün içinde internet etkinleştirmesi ister; Evaluation 180 günle sınırlıdır. Bu ayrı bakım gereksinimi çözülmeden süresiz kullanım vaat edilmez. Kaynak: https://www.microsoft.com/en-us/evalcenter/evaluate-windows-server-2025 .

## Son doğrulama

| Kontrol | Sonuç |
|---|---|
| Windows genel AD taraması | 23 ders / 155 kontrol; tek ACL Options özelliği bulgusu çıktı |
| ACL düzeltmesi + son CA sınırlarının Windows tekrar taraması | AD15/AD21: 2 ders / 9 kontrol temiz; önceki bulgu kapandı |
| Son S4U görev çözümü ve başlangıcı | Doğru çözüm pass, başlangıç fail; gerçek dosya kanıtı değişimi dahil |
| Çevrimdışı ekler | 4 test temiz; 36 mutasyon reddedildi |
| Canlı LDAP ekleri | 4 test temiz; 2 tahmin, doğru/başlangıç görevleri, 5 mutasyon reddi |
| Canlı Windows ekleri | 3 test temiz; 3 tahmin, 5 mutasyon reddi |
| Süreç ömrü ve taşıma | 8 + 1 test temiz; gerçek konukta UTF-8/çıkış/stderr, timeout ve normal çıkışta çocuk kapanması dahil; son gizli pencere değişikliğiyle 6 yerel test tekrar temiz (3 canlı test bu yerel koşuda atlandı) |
| Pafta API | 2 test temiz; ayrı geçici progress.json, gerçek VM ve LDAP yönlendirmesi |
| UTF-8/LF / derleme / diff | 29 kaynak dosya kontrol edildi; py_compile ve git diff --check temiz |
| Git Bash tam AD taraması | 23 ders / 156 kontrol temiz: 39 örnek, 23 tahmin, 47 çözüm, 47 başlangıç |

Toplam 46 kaynak mutasyonu reddedildi (36 + 5 + 5); 11 ek dersin tahmin cevabı gerçek değerlendirmeyle eşleşti. Mevcut 12 dersin tahminleri Windows genel taramasında çalıştırıldı. UTF-8 girdi için IBM437 bozulması gerçek konukta gözlendi ve Console.InputEncoding açıkça UTF-8 yapılarak düzeltildi; yerel ve gerçek konukta iki son test (girdi/çıktı/stderr/çıkış 7) temiz. Sonradan eklenen canlı PowerShell anlatım kutuları için doğrulayıcı adımın dil meta'sını izler.

Bu teslimde bütün uygulamanın diğer yollarına tam tarama yapılmadı; yukarıdaki sayılar AD yolunundur. Gerçek kanıt: `ad-live-evidence.json`; ayrıntı logları `ad-*.log`. Git Bash taraması son ders/test sürümünü kapsar. Windows genel taramasındaki tek bulgu hedefli tekrar ile kapatılmıştır; eski bulgulu log tarihçe olarak korunur.

## Commitler

- Altyapı: `e568caa`.
- UTF-8 girdi düzeltmesi: `b5eda58`.
- Madde 60: `af22836`.
- Madde 61: `df2bc40`.
- Madde 62: `1cd906d`.
- Madde 63: `9832298`.

Takip maddeleri denetime hazır olarak işlenir; Bitti kararı bağımsız denetçinindir. Push yapılmadı.
