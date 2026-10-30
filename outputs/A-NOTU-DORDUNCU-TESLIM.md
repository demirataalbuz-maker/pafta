# A notu · Dördüncü teslim

27 Ekim 2026 · Codex · dal: codex/a-notu-104 · push yapılmadı

| Madde | Kapanan açık | Commit | Mutasyon sonucu | Öz değerlendirme |
|---|---|---|---|---|
| 19 | PS24: gerçek EVTX okuyucusu ve native JEA veri dosyaları | 29d583a | 13 reddedildi, 0 geçen | 93/A |
| 21 | CM22: gerçek Registry erişim reddi, hata çıktısı ve temizleme | 91685e1 | 4 reddedildi, 0 geçen | 93/A |
| 22 | CM24: gerçek dosya DENY ACE, ACL sorgusu ile okuma farkı | 2f18ef9 | 4 reddedildi, 0 geçen | 93/A |

Panel kabul commitleri: 9179022 (19), 5ee20f7 (21–22). Önceki bağımsız puanlar, bulgular ve CM23 kabul geçmişi korundu. Yeni notlar Codex öz değerlendirmesidir; bağımsız yeniden denetim beklenir.

Doğrulama:

- PowerShell tam yol, Windows: 29 ders, 287 kontrol TEMİZ.
- PowerShell tam yol, Git Bash: 29 ders, 287 kontrol TEMİZ.
- CMD tam yol, Windows: 25 ders, 146 kontrol TEMİZ.
- CMD tam yol, Git Bash: 25 ders, 146 kontrol TEMİZ.
- Yeni regresyonlar: toplam 21 yanlış çözüm reddedildi, 0 geçen. İki yeni Python dosyası py_compile geçti.
- CMD fixture hata enjeksiyonunda da özgün DACL geri yüklendi; oluşturulan HKCU anahtarı/dosya silindi. Sistem izinleri değiştirilmedi.

Bu teslimde bütün uygulama yeniden doğrulanmadı; değişen PowerShell ve CMD yolları iki ortamda tam doğrulandı. PS24 EVTX içeriği sentetiktir; native AppLocker enforcement veya JEA endpoint yetki testi iddia edilmez.

Güncel panel: **78/104 A**, 26 madde A altında veya puansız. Kapsam kararları: **87 Tam, 16 Kısmen, 1 Bekliyor**; bunlar not dağılımından ayrı göstergelerdir. Sıradaki A altı madde **24, HTTP/Burp dışa aktarımı**. Bu teslimde yarım bırakılmış kod değişikliği yok; kalan maddeler kapanmış sayılmadı.

Kanıtlar: a-notu-ps24-files-kabul.json, a-notu-cm22-deny-kabul.json, a-notu-cm24-deny-kabul.json ve a-notu-cmd-native-denials-kabul.json. Dört tam yol logu bu teslimle kaydedildi.
