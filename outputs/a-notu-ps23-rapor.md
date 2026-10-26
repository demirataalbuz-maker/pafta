# 13 · PowerShell HTTP sınırları

27 Ekim 2026 · Codex

PS23'e bir gerçek tahmin ve üç yazma görevi eklendi. Önceki Windows PowerShell 5.1 adımları korunuyor; -Form 5.1'de olmadığından yeni adımlar açıkça kurulu PowerShell 7.6.8 motorunda çalışır. Yeni yerel tezgâh yalnız loopback'te rastgele port açar; gerçek HTTP başlıkları, multipart MIME ve dosya baytları okunur, istek tanıkları JSONL'e yazılır.

- Yönlendirme: MaximumRedirection=2; iki hop dahil, üç hop reddedilir. Gerçek zincirde gidilen yollar da denetlenir; 0/5 ve geçersiz girdiler sınanır.
- Multipart: -Form ile gerçek FileInfo, Unicode/özel karakterli not, ikili/boş dosya. Sunucunun gördüğü alanlar, dosya adı, bayt sayısı ve SHA256 doğrulanır; yol metni dosya yerine geçmez.
- Süre: hızlı 100 ms, yavaş 1700 ms ile 1 saniyelik başlık ve gövde bütçeleri ayrı sınanır. Kurulu motor başlıkta TaskCanceledException, gövdede TimeoutException üretti; ikisi derste açıkça yazıldı. HTTP 404 tekrar throw edilir, timeout diye gizlenemez. Tam zaman sınırındaki zamanlayıcı yarışı deterministik bir test olarak sunulmadı.

Doğrulama: Windows ve Git Bash'te PS23 1 ders/17 kontrol TEMİZ. Gerçek tahmin True/302 birebir doğrulandı. `tools/test_powershell_http_edges.py`: 3 referans çözüm geçti; 12 yanlış çözüm reddedildi, 0 geçen. Fail ile çalışma zamanı ÇıkışKodu/error reddi JSON'da ayrı kaydedildi; altyapı hataları kabul sayılmadı. Paket kurulmadı; UTF-8/LF.

Öz değerlendirme: test 24, kapsam 24, derinlik 22, gerçeklik 15, yol 9 = 94/100 (A). Önceki bağımsız 78/100 korunur; bağımsız yeniden denetim yapılmadı.
