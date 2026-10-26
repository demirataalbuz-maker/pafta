# 15 · NTFS Deny sonrası gerçek erişim

27 Ekim 2026 · Codex

PS22'ye gerçek dosya erişimi yazma görevi eklendi. Aynı geçerli Windows token'ıyla dosya önce okunur; kullanıcı SID'sine ReadData Deny eklenip Set-Acl uygulandığında File.ReadAllBytes gerçek UnauthorizedAccessException üretir; özgün ACL finally ile geri yüklendikten sonra aynı dosya tekrar okunur. WriteData Deny okumayı engellemez. 256 bayt, sıfır bayt ve boşluk/Unicode adlı 5 bayt dosya sınanır. Yalnız görev dosyaları ve iki dar hak kabul edilir, sistem/registry/üst klasör izinleri değiştirilmez.

Test sarmalayıcısı Set-Acl çağrısını gerçek Microsoft.PowerShell.Security cmdlet'ine iletir ve hemen ardından bağımsız .NET okumasıyla DENIED/OK fiziksel durumunu kaydeder. Bu yetki kararını taklit eden mock değildir. İlk ACL değişiminden sonra hata enjekte edilerek finally'nin hem özgün SDDL'yi hem gerçek okumayı geri getirdiği doğrulanır. Sahte metin raporu geçmez. PowerShell'in MethodInvocationException sarmalı ve iç UnauthorizedAccessException ayrımı anlatıldı; diğer hatalar gizlenmez. Genel etkin erişim, backup privilege veya SMB paylaşım erişimi motoru olduğu iddia edilmiyor.

- Windows ve Git Bash: `validate.py --yol powershell ps22`, 1 ders/11 kontrol TEMİZ.
- `tools/test_powershell_ntfs_deny.py`: gerçek referans ve rollback hata enjeksiyonu geçti; 8 yanlış çözüm reddedildi, 0 geçen.
- Dosya baytları Python ile de açılarak karşılaştırıldı; özgün SDDL geri yüklendi.
- Yeni paket kurulmadı, UTF-8/LF.

Öz değerlendirme: test 24, kapsam 24, derinlik 22, gerçeklik 15, yol 9 = 94/100 (A). Önceki bağımsız 77/100 korunur; bağımsız yeniden denetim yapılmadı.

Son yol geneli kabulü: Windows ve Git Bash, 29 ders/283 kontrol TEMİZ. Ham loglar `a-notu-dalga3-platform-kabul.json`, toplu rapor `A-NOTU-UCUNCU-TESLIM.md`.
