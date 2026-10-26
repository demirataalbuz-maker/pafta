# 18 · Gerçek WinRM ve PSSession yaşam döngüsü

27 Ekim 2026 · Codex

PS29'a bir gerçek tahmin ve bir yazma görevi eklendi. Önceki PowerShell 7 UseWindowsPowerShell bölümü korunuyor. Yeni bölüm mevcut yönetilen PF-APP01 Windows Server VM'sinde New-PSSession -ComputerName localhost ile gerçek WSMan/WinRM bağlantısı açar. Ana bilgisayarın WinRM/TrustedHosts/firewall ayarı değiştirilmedi; paket/ISO kurulmadı. Öğrenci yine Pafta'dan Çalıştır'ı kullanır, VM konsolu gerekmez.

Bu, ayrı Windows Server konuk içinde loopback WinRM'dir; iki farklı makine arasında Kerberos, double-hop veya JEA yetki izolasyonu kabulü diye sunulmaz. Gereksinim ve sınır README'de açıkça yazıldı. Ortak engine değişikliği yalnız PowerShell yoluna mevcut ad-vm motorünü açar; AD rotası korunur, Python/Bash/CMD kabul edilmez. Altyapı commit'i 4a88e50.

## Gerçek kabul

- Aynı oturumda üç ayrı komutla kalıcı toplam; ArgumentList, -10/10 dahil sınırlar, sıfır ve geçersiz girdiler.
- Gerçek uzak bilgisayar adı, WSManConnectionInfo, ayrı süreç PID'si, Deserialized.System.Diagnostics.Process ve kayıp Kill metodu.
- Komut throw'u: Opened kalır; tahminde sonraki gerçek komut 42 döndürür.
- Yalnız o uzak oturumun kendi PID'si durdurulur: PSRemotingTransportException ve Broken. Başka süreç hedeflenmez.
- finally yalnız kendi PSSession'ını kaldırır. Get-PSSession'da InstanceId'nin kalmadığı, öğrencinin raporundan bağımsız gerçek New-PSSession nesnesiyle denetlenir.
- Native Windows Server'da Broken nesne Remove sonrasında da Broken kaldı; temizlik State=Closed diye taklit edilmedi.
- PowerShell 5.1 uzak skalerlerine eklenen PSComputerName/RunspaceId notlarının JSON şeklini değiştirdiği görüldü; raporda yeni düz metin/sayı üretimi derste açıklandı.

`tools/test_powershell_winrm.py`: tahmin COMMAND_ERROR/Opened/42/0 birebir; tam ders testleriyle referans geçti, 7 yanlış çözüm reddedildi, 0 geçen. Mutantlar aynı expected(mode,n) kabul koşuluyla tek gerçek guest girdisinde sınandı; bu kapsam JSON'da açık. Oturum temizliğini atlama, kalıcılığı bozma, sınırları dışlama, Broken/Closed ve komut/taşıma hatası yanlış etiketleri reddedildi.

Windows hedefli doğrulama: PS29 1 ders, 8 kontrol TEMİZ. Yol geneli ve Git Bash kabulü son teslim raporunda yer alır. Tek konuk çalışması 90 saniyeyle sınırlı; bütün görev testi mevcut 240 saniye tavanını kullanır. Sınır girdileri gerçek konuk PowerShell süreçlerinde tek taşıma işi içinde ardışık çalıştırılarak VMware kopyalama maliyeti azaltıldı; gerçek cmdlet'ler veya WinRM taklit edilmedi.

Öz değerlendirme: test 24, kapsam 24, derinlik 22, gerçeklik 15, yol 9 = 94/100 (A). Önceki bağımsız 73/100 kaydı korunur; bağımsız yeniden denetim yapılmadı.
