# pu19 görünür veri
Bu dört dosya sentetik fixture; canlı HTTP yanıtı veya kabul kanıtı değildir.
Setup bunları çalışma alanında `yerel_sqli/` altına yalnız eksikse kopyalar.
`istekler.json` içindeki saldırı girdisini değiştirip tekrar deneyin: `'`,
`' OR 1=1 -- `, yanlış parola ve normal giriş farklı sonuçlar üretir.
Run/Kontrol her seferinde yeni geçici çalışma alanı açar. Çalışma kopyası bu
çağrı içinde düzenlenebilir; sonraki çağrıya kalıcılık vaat edilmez. Kalıcı
notunuzu kendi dosyanıza alın. Lab yalnız kendi geçici DB/server kaynaklarını
kapatır; öğrenci dosyası silmez. Setup mevcut kopyayı ezmez.
Gerçek deney raporu stdout'ta; Kontrol ayrıca bağımsız SQLite audit kayıtlarını
karşılaştırır. Dinamik hesap/parola/canary yalnız sentetik test verisidir.
Bu alt ders yalnız SQLi login bypass ve parameter binding üzerinedir;
XSS/SSTI/XXE, blind/time-based/UNION SQLi, production auth ve Purple M2 bütünü yoktur.
