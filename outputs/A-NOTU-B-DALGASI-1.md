# B notları · 24, 31, 32, 34 teslimi

27 Ekim 2026 · Codex · codex/a-notu-104 · push yok.

| Madde | Ders | Commit | Davranış bozan mutant |
|---|---|---|---|
| 24 | HT17 gerçek Burp XML | 1d6297c | 18 reddedildi, 0 geçen |
| 31 | SQ22 gerçek MySQL/SQL Server | cc01e4d (altyapı 134da9e/2f08e31) | 14 reddedildi, 0 geçen |
| 32 | SQ19 gerçek sqlite3 bağlama | ab2cecb (bağlantı da71f2c) | 22 reddedildi, 0 geçen |
| 34 | SQ20 gerçek PostgreSQL JSONB | 0842332 | 15 reddedildi, 0 geçen |

Toplam 69 davranış bozan mutant reddedildi. HT17 standart betiğinin eşdeğer geçen varyantları kendi raporunda ayrı açıklanır; bütün ham mutasyonlar 0 geçti denmez.

HTTP Windows/Git Bash: 24 ders, 177 kontrol temiz. SQL son Windows/Git Bash: 22 ders, 250 kontrol temiz. SQ31 ilk Git Bash denemesinde eski PostgreSQL küme keşfi geçici boş döndü; tekrar ve son kabul temiz. Bu hata gizlenmedi. Native motor sürümleri, salt okuma/timeout/fault temizliği kanıt JSON'larındadır.

Yeni notlar sırasıyla 94,94,95,95 Codex öz değerlendirmesidir; bağımsız yeniden denetim beklenir. Ortak puanlar.json başka ajanın 92/105–108 değişikliklerini içerdiğinden değiştirilmedi. Her madde için ayrı a-notu-*-panel-onerisi.json hazır; canlı panel güncellendi denmez.

Sıradaki 35/36 için kullanıcı Kusto Emulator kurulumunu onayladı. 37'nin gerçek Sentinel kural önizlemesi için çalışma alanı yok; o kısım açık kalacak, yerel motorla aynı şey sayılmayacak. Diğer istenen maddeler henüz bitmedi.
