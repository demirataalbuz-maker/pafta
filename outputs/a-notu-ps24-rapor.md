# 19 · AppLocker EVTX ve gerçek JEA veri dosyaları

27 Ekim 2026 · Codex

PS24'e iki yazma görevi eklendi. İlki Windows wevtutil'in ürettiği gerçek EVTX dosyalarını Get-WinEvent ile okur. 8002/8007 dahil uçlar, ALLOW/AUDIT/BLOCK ayrımı, sağlayıcı, Level eşit ucu, kayıt sırası, değişen dosya/kural/SID, boş dosya, bozuk dosya ve eksik alan ölçülür. Kaynak içerik sentetik klasik EVT kayıtlarıdır; gerçek AppLocker politikasının uygulanması veya native AppLocker manifest şeması diye sunulmaz. Adsız Data dizisinin eğitim sözleşmesi ve gerçek olayda ToXml ile şema kontrolü açıklandı. Önceki elle yazılmış XML örneğinin her AppLocker olayına genellenen anlatımı daraltıldı.

İkinci görev New-PSRoleCapabilityFile/New-PSSessionConfigurationFile ile üretilmiş gerçek .psrc/.pssc dosyalarını Import-PowerShellDataFile ile okur. Test-PSSessionConfigurationFile gerçek oluşturulan yapılandırmayı doğrular; endpoint kayıt edilmez. Grup anahtarı, rol sırası, komut/parametre/ValidateSet, dış komut, sağlayıcı listesi ve virtual account boolean alanları korunur. Değişen rol kısıtı rapora yansır; eksik rol dosyası, yol dışına çıkan ad, metin false ve dinamik veri ifadesi reddedilir. Dinamik dosyanın Set-Content ifadesinin çalışmadığı marker ile ölçülür. Bu, etkin AD grup üyeliği veya JEA endpoint yetki kabulü değildir.

Windows PowerShell 5.1'in ürettiği UTF-16 veri dosyaları, içerikleri korunarak UTF-8/LF'ye dönüştürülür; 5.1 okuyucusu için UTF-8 BOM kullanılır. Kaynak dosyalar UTF-8/LF. Host politika, kanal veya servis değiştirilmez; yeni paket indirilmedi.

- PS24 hedefli: 1 ders, 14 kontrol TEMİZ.
- `tools/test_powershell_applocker_jea_files.py`: 2 gerçek referans geçti, 13 yanlış çözüm reddedildi, 0 geçen. Fail/çıkış kodu reddi kanıtta ayrılır.
- Windows tam PowerShell yolu: 29 ders, 287 kontrol TEMİZ. Git Bash tam yol logu teslim kabulünde ayrıca saklanır.

Öz değerlendirme: test 24/25, kapsam 24/25, derinlik 22/25, gerçeklik 14/15, yol 9/10 = 93/100 (A). Gerçek okuyucu ve native dosya üretimi var; sentetik olay içeriği nedeniyle gerçeklikten bir puan kırıldı. Önceki bağımsız 83/100 korunur. Bağımsız yeniden denetim yapılmadı.
