# Madde madde denetim ve eksik analizi

Denetçi: Claude (Denetçi · Yazar 2). Başlangıç: 25 Ekim 2026. Kullanıcının isteğiyle maddeler 1'den 104'e **sırayla** ele alınır ve hiçbir ders, motor ya da test **değiştirilmez**; yalnız bu rapor yazılır.

Her madde için iki soru:

1. **Denetim — çalışıyor mu?** Anlık görüntüde (`git archive HEAD` + `.deps` bağlantısı) `tools/validate.py` hem PowerShell'de hem Git Bash'te; tahmin cevapları gerçek çıktıyla; mutasyon testi (geçen her mutant eşdeğer mi gerçek boşluk mu diye ayrılır); mutantı olmayan ya da az olan görevlerde elle yanlış çözüm.
2. **Eksik analizi — istenen yapıldı mı?** ASAMA2.md'deki satırın "neden" ve "ne gerekir" sütunlarıyla dersin içeriği karşılaştırılır. Karşılanmayan her şey, küçük de olsa, yazılır.

Karar ölçeği: **Tam** (istenen karşılanmış, test sağlam) · **Kısmen** (çalışıyor, ama istenenin bir kısmı yok) · **Eksik** (asıl istenen yok) · **Sorunlu** (çalışmıyor ya da test yanlışı kabul ediyor).

Kendi yazdığım maddelerde (Yazar 2) çıkar çatışması ayrıca belirtilir.

---

## Madde 1 · Python · pip/venv ile betik ortamı ve tekrarlanabilir bağımlılık kurulumu

- **Ders:** P75 (`ebd4157`, altyapı `19fb053`). Yazar: başka ajan.
- **Denetim:** anlık görüntü `9be539d`. Validate 25 kontrol (P74 ile birlikte) PowerShell ve Git Bash'te temiz. Tahmin gerçek çıktıyla uyuşuyor. Mutasyon: 11 mutantın 9'u yakalandı; geçen 2'si eşdeğer (`and`↔`or` değişimleri; iki yolda da pip başarısız olup aynı "HATA"yı veriyor).
- **Karşılananlar:** PEP 668 (sistem Python'u), temiz venv ve sistem paketlerini görmemesi, `pip wheel` ile tekerlek üretmek, `--no-index --find-links` ile çevrimdışı kurulum, sürüm kısıtları ve PEP 440, `requirements` ve `--require-hashes` ile hash'li kilit dosyası. `ModuleNotFoundError`'ın nedeni anlatılıyor.
- **Eksikler:**
  - ASAMA2 "**projenin `.venv`'i ile `.deps` paket deposunun rollerini ayıran** kurulum" istiyor. Derste `.deps` hiç geçmiyor; Pafta'nın kendi iki yerli düzeni öğrenciye anlatılmıyor.
  - "**Çakışan bağımlılığı çözmek**" (iki paketin uyuşmaz sürüm istemesi, pip çözücü hatası) yok. Yalnız eksik paket (`ModuleNotFoundError`) anlatılıyor.
- **Karar:** **Kısmen.**

## Madde 2 · Python · Requests Session ve aiohttp ile HTTP otomasyonu

- **Ders:** P74 (`8f4c9a6`, `5fb8da0`). Yazar: başka ajan.
- **Denetim:** validate iki ortamda temiz; 2 tahmin uyuşuyor. Mutasyon: 25 mutantın 17'si yakalandı; geçen 8'i eşdeğer (`timeout=5`→`6`, yerel sunucu hızlı; gecikme sayıları, `gather` sonucu giriş sırasıyla döndüğü için etkisiz). İlk görevde ("Sayfaları sonuna kadar gez") mutant üretilmediği için elle 4 yanlış çözüm denendi (girişsiz, yalnız ilk sayfa, durum koduna bakmayan, `Session` yerine `requests.get`); dördü de reddedildi.
- **Karşılananlar:** `Session` ile çerezli oturum, `json=` ve `params=`, sayfalama, hata yanıtlarının okunması; `timeout`'un toplam süre olmadığı açıkça anlatılıyor (ASAMA2'nin özellikle istediği uyarı); `aiohttp` ile `Semaphore`'la sınırlı eşzamanlılık ve sunucuda ölçülen en çok eşzamanlı istek; `aiohttp` çerez kavanozunun IP adresli sunucudan gelen çerezi reddetmesi tuzağı.
- **Eksikler:**
  - **Proxy** hiç yok (ASAMA2 "neden" sütununda sayılıyor).
  - **CA doğrulaması** yalnız bir cümle (`verify=False` uyarısı); tezgah HTTP olduğu için görev yok. (HTTP yolundaki HT18 curl/TLS bunu ayrıca kapsıyor olabilir; Python tarafında yok.)
  - **Form gövdesi** (`data=`, `application/x-www-form-urlencoded`) yalnız anılıyor, görevde kullanılmıyor.
  - "**Paket yolu/sürümü kaydedilir**" (hangi `requests`/`aiohttp` sürümüyle çalışıldığını göstermek) hiçbir görevde yok.
- **Karar:** **Kısmen.**

## Madde 3 · Python · Beautiful Soup ile HTML ayrıştırma

- **Ders:** P74 (aynı ders). Denetim yukarıdaki gibi.
- **Karşılananlar:** `select` ve `find`, öznitelik (`tr["data-id"]`) ve `get_text(strip=True)`, olmayan öğenin `None` dönmesi ve buna karşı korunmak, kapanmamış etiketin veriyi sessizce birleştirmesi (bozuk HTML), `html.parser`.
- **Eksikler:** `find_all` yalnız anlatımda; görevlerde hep `select` kullanılıyor. Önemli bir eksik değil.
- **Karar:** **Tam.**
