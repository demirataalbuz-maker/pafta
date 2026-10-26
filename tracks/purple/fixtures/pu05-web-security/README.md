# PU05 · Web uygulama güvenliği fixture'ı

Bu dersin bütün verileri `sandbox/web_security_lab.py` içinde üretilir; ayrı bir veri dosyası veya indirme gerekmez. Böylece her çalıştırma temiz, sentetik ve tekrarlanabilir kalır.

- HTTP sunucusu yalnız `127.0.0.1` üzerinde dinler. `ayse` ve `can` hesaplarının parolası `pafta-demo`; iki hesap da yalnız bu laboratuvara aittir.
- `WebSecurityLab.reset()` belgeleri ve revizyonu başlangıç değerine döndürür, oturumları kapatır. Ayrıca `POST /_control/reset`, `X-Lab-Control: pu05-reset-only` başlığını ister.
- IDOR/API fixture'ı 1 numaralı Ayşe ve 2 numaralı Can belgesini kullanır. Başka kullanıcının belgesini okuma ve değiştirme `403`, oturumsuz istek `401`, var olmayan belge `404` döndürür. Başarılı PATCH kalıcıdır ve revizyonu artırır.
- SQL fixture'ı her `memory_database()` çağrısında yeni bir bellek içi SQLite veritabanı kurar. Disk veritabanı, harici sunucu veya başka SQL motoru kullanılmaz.
- XSS fixture'ındaki tek canary `<script>window.__paftaCanary=1</script>` dir. Cookie, ağ isteği veya veri aktarımı içermez. Gerçek tarayıcı testi yalnız `PAFTA_WEB_BROWSER=1` ile çalışır; kurulu Edge/Chromium kullanılır, tarayıcı veya paket indirilmez. Opt-in verilmezse test açıkça skip olur ve dersteki güvenli DOM modeli yine çalışır.
- Komut fixture'ı `pafta-durum` ve `pafta-liste` adlı gerçekte var olmayan programlar için allowlist ve argv planlarıdır. Bu planlar hiçbir yerde çalıştırılmaz; kabuk, subprocess, reverse shell veya ana makine komutu yoktur.

Ders dosyası şu anda çalışma kopyasında bağımsız doğrulanır. `tracks/purple/track.json` bu madde kapsamında özellikle değiştirilmediğinden uygulamanın ders listesine kayıt eklenmez.
