# 31 · Gerçek MySQL ve SQL Server

27 Ekim 2026 · Codex

Kullanıcı onayıyla MySQL 8.4.8 ve SQL Server 2022 CU23 imajları indirildi; tag ve digest kodda sabittir. Gerçek sürümler MySQL 8.4.8 ve SQL Server 16.0.4236.2. Her iki Pafta konteyneri network none, host portu/klasör bağı olmadan çalışır. SQL Server Developer geliştirme/test içindir. Kurulum otomatik indirme yapmaz; eksik imaj açık hata üretir.

SQ22'ye iki yazma görevi eklendi: MySQL Unicode bayt/karakter ayrımı, NULL/boş soyad ve 59/60/119/120 dakika tam sayı bölümü; SQL Server TOP (2), eşit puanda id sırası, 79/80 eşiği, NULL ve boş sonuç. MySQL sonucu MariaDB diye, MariaDB sonucu MySQL diye sunulmaz. Önceki SQLite/PostgreSQL/MariaDB adımları korunur.

Koşucu her işe özgü salt okuma hesabı/veritabanı kurar. Python test süreci dışarıdan timeout ile durdurulduğunda MySQL aktif sorgusu KILL edilir; SQL Server oturumu rollback ile sonlandırılır. Sonra yalnız işe ait veritabanı/hesap kaldırılır. İki motorda da normal bitiş, kasıtlı istisna ve timeout temizliği; gerçek DELETE yetki reddi ve SQL NULL/0 ayrımı doğrulandı. Yerel parolalar depoya/komut satırına yazılmaz.

Kabul: tools/test_sql_docker_runtime.py, 2 referans geçti, **14 mutant reddedildi, 0 geçen**. Başlangıç çözümleri başarısız, gerçek çözümler başarılı; SQ22 13 kontrol temiz. Windows tam SQL yolu **22 ders, 242 kontrol TEMİZ**. İlk paralel Git Bash doğrulaması SQ21'in mevcut WSL PostgreSQL küme keşfinde geçici boş yanıtla düştü; yeni iki konteyner görevi geçti. Git Bash tam yol tekrarı **22 ders, 242 kontrol TEMİZ** geçti; ilk başarısızlık gizlenmez.

Sınır: tek SELECT/CTE ve farklı alias'lı sütunlar; birden çok sonuç kümesi yok. MySQL XML ve SQL Server FOR JSON PATH son eki gerçek istemci çıktısıdır; sayılar/metinler metin, SQL NULL None olur. dene(ek) aynı işe ait DB'yi değiştirir; SQLite temiz-deneme sözleşmesi varsayılmaz. Bu farklar ders ve README'de yazılıdır. Konteynerler dersler arasında açık kalır; geçici iş veritabanları kalmaz.

Öz değerlendirme: test 24, kapsam 24, derinlik 21, gerçeklik 15, yol 10 = **94/A**. Eski bağımsız 82 korunur; bağımsız yeniden denetim beklenir. Ortak puanlar.json diğer ajanın değişiklikleriyle dolu; panel önerisi ayrı kaydedildi.

Resmî kaynaklar kontrol edildi: https://hub.docker.com/_/mysql , https://hub.docker.com/r/microsoft/mssql-server/ , https://dev.mysql.com/doc/refman/8.4/en/string-functions.html , https://dev.mysql.com/doc/refman/8.4/en/arithmetic-functions.html , https://learn.microsoft.com/en-us/sql/t-sql/queries/top-transact-sql , https://learn.microsoft.com/en-us/sql/relational-databases/json/include-null-values-in-json-include-null-values-option?view=sql-server-ver16 .
