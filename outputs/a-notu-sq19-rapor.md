# 32 · Gerçek uygulama parametre bağlama

27 Ekim 2026 · Codex

SQ19'a iki Python görevi eklendi; motor: python ve dil: python ile mevcut gerçek Python koşucusunu kullanır. Yeni paket kurulmadı. sqlite3.Connection alt sınıfı gerçek execute çağrısını kaydeder ve super().execute ile gerçek SQLite'a iletir; veritabanı taklit edilmez. Test yalnız kodda ? karakterini aramaz, gerçek değerlerin execute ikinci argümanında taşındığını ölçer.

İlk görev ad/None ve 0..100 CPU eşiğini bağlar, izinli sıralamayı ve eşitlikte id'yi korur. Tırnaklı/SQL benzeri ad, ASCII harf duyarlılığı, NULL, boş metin, 79/80/81 ve 100, yeni veri, bool ve bozuk girdi, sorgu öncesi reddetme testleri vardır. Eşitlik sırası eksikliği ters id içeren gerçek indeksle görünür hale getirildi.

İkinci görev literal LIKE önek aramasında backslash/%/_ kaçışını ve LIMIT değerini gerçek parametrelerle bağlar. Boş önek, boş ad, NULL, %/_/backslash/tırnaklı girdiler, ortada geçen metnin önek sanılmaması, 1/20 ve 0/21 komşuları, 20'den büyük veri kümesi sınanır. SQLite LIKE'ın ASCII harf davranışını bütün Unicode'a genellemez.

JV10 JDBC/PreparedStatement, PH08 PDO prepare/execute ve CS10 EF Core FromSqlInterpolated/FromSqlRaw derslerine karşılaştırmalı okuma köprüsü eklendi. Java/PHP/C# bu görevde çalıştırılmış gibi sunulmaz; okuma seviyeleri korunur. SQLite IS ? uzantısı başka motora genellenmez.

Kabul: SQ19 **14 kontrol TEMİZ**; tools/test_sql_python_binding.py, **2 referans geçti, 22 yanlış çözüm reddedildi, 0 geçen**. tam SQL yolu yeni iki ek kontrolle teslimde yeniden doğrulanacak. Öz değerlendirme test24/kapsam24/derinlik22/gerçeklik15/yol10 = **95/A**; eski bağımsız79 korunur. Bağımsız yeniden denetim beklenir. Ortak panel başka ajanda; öneri ayrı dosyadadır.

Kaynaklar kontrol edildi:
- https://docs.python.org/3/library/sqlite3.html#how-to-use-placeholders-to-bind-values-in-sql-queries
- https://www.sqlite.org/lang_expr.html#like
- https://docs.oracle.com/javase/tutorial/jdbc/basics/prepared.html
- https://www.php.net/manual/en/pdo.prepare.php
- https://learn.microsoft.com/en-us/ef/core/querying/sql-queries

Son tam kabul: Windows ve Git Bash, her birinde **22 ders, 250 kontrol TEMİZ**. Loglar a-notu-sql35-windows.log ve a-notu-sql35-git-bash.log; platform özeti a-notu-sql35-platform-kabul.json.
