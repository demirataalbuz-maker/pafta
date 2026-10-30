# 21 · Registry erişim reddi

27 Ekim 2026 · Codex

Kalan erişim reddi bulgusu gerçek Windows DACL ile sınandı. Öğrencinin çözümü değiştirilmedi; test bloğu ve fixture açıklaması güçlendirildi. Yalnız teste ait yeni HKCU GUID anahtarı üzerinde mevcut kullanıcıya KEY_QUERY_VALUE DENY verilir. Önceden açık WRITE_DAC handle ile özgün DACL geri yüklenir; yalnız oluşturulan nesne silinir. Sistem anahtarı, servis veya sistem dosyası izinleri değiştirilmez.

Önce gerçek reg sorgusu başarılıdır. DENY sırasında bağımsız winreg okuyucusu WinError 5 alır; öğrencinin reg sorgusu anahtar-hatasi, boş stdout ve çıkış 1 üretmelidir. İzin geri yüklenince aynı sorgu tekrar başarılıdır.

Fixture içine kasıtlı Python istisnası verildiğinde de özgün DACL geri yüklenir ve nesne silinir. Yeni paket kurulmadı.

- Referans çözüm geçti; 4 yanlış çözüm reddedildi, **0 geçen**.
- Birleşik regresyon: `python tools/test_cmd_native_denials.py` (iki ders, toplam 8 mutant).
- Tam CMD yolu Windows ve Git Bash: **25 ders, 146 kontrol TEMİZ**. Loglar: `a-notu-denials-cmd-windows.log`, `a-notu-denials-cmd-git-bash.log`.

Öz değerlendirme: test 24/25, kapsam 24/25, derinlik 21/25, gerçeklik 15/15, yol 9/10 = **93/A**. Bu, yeni bağımsız denetim sonucu değildir. Önceki bağımsız 85 puan ve geçmiş kabul kanıtları panelde korunur.
