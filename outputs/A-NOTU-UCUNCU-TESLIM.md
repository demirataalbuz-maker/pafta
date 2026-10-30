# A notu · üçüncü kapsam teslimi

27 Ekim 2026 · dal: codex/a-notu-104 · push yok.

| Madde | Kapanan açık | Öz değerlendirme | Uygulama commit'i | Reddedilen yanlış çözüm |
|---|---|---|---|---|
| 15 | Gerçek NTFS Deny sonrası UnauthorizedAccess, dar hak karşılaştırması, finally ile geri yükleme | 94/A | 0e1fe6d | 8 |
| 18 | Ayrılmış Windows Server'da gerçek WinRM/ComputerName, kalıcı oturum, Broken ve temizlik | 94/A | 5b199b2 | 7 |

16 ve 17 zaten A olduğundan numara sırasında sonraki A olmayan madde 18'e geçildi. Yeni kurulum/indirme veya host WinRM ayarı gerekmedi; mevcut PF-APP01 kullanıldı. Ortak engine/README bağlantısı 4a88e50'de kendi dalına commit edildi.

## Doğrulama

- Windows ve Git Bash'te tam PowerShell yolu: **29 ders, 283 kontrol TEMİZ**; ham loglar a-notu-dalga3-platform-kabul.json içinde listeli.
- PS22 ayrıca her iki ortamda 1 ders, 11 kontrol temiz; gerçek NTFS referansı, Set-Acl sonrası bağımsız .NET okuması ve hata enjekte edilmiş finally kabulü geçti.
- PS29 hedefli Windows kabulü 1 ders, 8 kontrol temiz; gerçek WinRM tahmini COMMAND_ERROR / Opened / 42 / 0 birebir doğrulandı.
- Toplam 15 yanlış çözüm reddedildi, 0 geçen. WinRM mutantları dersin aynı expected(mode,n) ölçütüyle ilgili gerçek guest girdisinde sınandı; kapsam JSON'da açık. Fail ve beklenmedik çalışma zamanı ÇıkışKodu/error reddi ayrı kaydedilir; altyapı hataları kabul sayılmaz.
- UTF-8/LF, Python sözdizimi, git diff --check ve paneldeki kanıt/rapor bağlantıları doğrulandı.
- Bütün uygulamanın yeniden doğrulandığı iddia edilmiyor; değişen PowerShell yolu iki ortamda tam doğrulandı. Mevcut AD motor rotası korundu; PowerShell'in VM rotası ve ilgisiz yolların reddi ayrıca denetlendi.

## Gerçeklik sınırları

NTFS deneyi geçerli token'ın normal ReadAllBytes açılışıdır; genel etkili erişim/SMB/backup privilege hesabı değildir. Dosya ACL'sinin aslı hata yolunda da geri yüklenir; yalnız görev dosyaları değiştirilir.

WinRM, ayrılmış Windows Server konuk içinde localhost WSMan'dir; iki ayrı bilgisayarın Kerberos/double-hop kabulü değildir. Broken nesne Remove sonrasında da Broken kalabildiği için temizlik Get-PSSession InstanceId kaydıyla doğrulanır. PowerShell 5.1 uzak skalerlerindeki remoting notlarının JSON'a etkisi derste açıklandı. Toplam görev kabulü 240 saniye, tek konuk çalışması 90 saniye sınırındadır; aynı öğrenci kodunun gerçek konuk süreçleri tek taşıma işi içinde sınanarak gereksiz VMware kopyaları azaltıldı.

## Panel ve devam

15 ve 18'in açık notları kapatılıp 94/A Codex öz değerlendirmesi olarak işlendi; eski bağımsız puan ve bulgular korunuyor. Yeni puanlar bağımsız yeniden denetim değildir. Görünüm **75/104 A**; hepsi henüz A değil. Kullanıcının kararı doğrultusunda 100 puan hedefi sonraya bırakıldı.

Sıradaki A olmayan madde **19: CLM, JEA ve AppLocker (8002/8004)**; eksikler gerçek AppLocker EVTX ile .psrc/.pssc yapılandırma okuması. Bu maddeye başlanmadı; yarım iş yok. Yalnız kendi dosyalarımız codex/a-notu-104 dalında; ortak checkout'un aktif dalı değiştirilmedi, diğer ajanın işleri sıfırlanmadı.
