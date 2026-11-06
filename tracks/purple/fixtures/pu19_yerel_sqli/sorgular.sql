-- Sentetik eğitim örneği, çalıştırılmış HTTP kaydı değildir.
-- String birleştirme: -- yorumuyla password koşulu devre dışı kalır.
SELECT username, canary FROM accounts WHERE username = '' OR 1=1 -- ' AND password = 'yanlis';
-- Savunma: SQL metni sabit, değerler ayrı execute(sql, (username,password)) ile bağlanır.
SELECT username, canary FROM accounts WHERE username = ? AND password = ?;
