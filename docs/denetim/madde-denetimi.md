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

## Madde 4 · Python · Scapy ile paket kaydını Python'dan okumak ve üretmek

- **Dersler:** P80 okuma (`9128368`, **Yazar 2 — kendi yazdığım ders, çıkar çatışması**), P81 üretme (`fc11f0d`, Yazar 1).
- **Denetim:** anlık görüntü `9be539d`. Validate (P76–P83 birlikte 48 kontrol) PowerShell ve Git Bash'te temiz. P80 tahmini uyuşuyor; mutasyon P80'de 7/7 yakalandı. P81 25 Ekim'de ayrıca denetlendi (3 yanlış çözümün 3'ü reddedildi).
- **Karşılananlar:** `rdpcap` ve `PcapReader`, katman yığını ve `haslayer`, alan okuma, başlık alanı ile çözülmüş katman farkı, snaplen kırpması (`caplen`/`wirelen`) ile kesik kayıt; P81'de katman katman paket kurmak, hesaplanan alanlar, `wrpcap` ve geri okuma, sağlamanın Scapy'de ve TShark'ta doğrulanması.
- **Eksikler:** yok (Windows `.deps`'e Scapy taşımak ASAMA2'de "sonraki dalga seçeneği", zorunlu değil).
- **Karar:** **Tam.** P80 için bağımsız bir gözün bakması iyi olur.

## Madde 5 · Python · ctypes ile native API/ABI okuma ve küçük çağrılar

- **Dersler:** P82–P83 (`fc11f0d`, Yazar 1). 25 Ekim denetiminde A40 bulundu ve düzeltildi (`7814a3e`).
- **Denetim:** validate iki ortamda temiz; tahminler uyuşuyor; mutasyon 6/6.
- **Karşılananlar:** `argtypes`/`restype` ve verilmezse 64 bitlik handle'ın kırpılması (ölçüldü), `c_wchar_p` ve UTF-16 kod birimi, `use_last_error` ve `GetLastError`, `Structure`, hizalama ve `_pack_`, `sizeof`/offset, `byref` ile Win32'ye yapı doldurtmak, `from_buffer_copy`.
- **Eksikler:**
  - ASAMA2 "**32–64 bit boyut testleri**" istiyor. Laboratuvarda yalnız 64 bit Python var; 32 bit taraf yalnız anlatımda (kırpılma örneğiyle), sınanmıyor.
  - "Yerel **test kitaplığı**" yerine Windows'un `kernel32`'si kullanılıyor; zararsız ve gerçek, ama öğrencinin kendi derlediği bir kitaplıkla imza uyuşmazlığını görmesi yok.
  - P82 ikinci görevde `c_void_p` hâlâ kaynak metninden denetleniyor (A40 notu); davranışla ayırt etmek görevin dönüş biçimini değiştirmeyi gerektirir.
- **Karar:** **Kısmen** (küçük eksikler).

## Madde 6 · Python · pwntools kullanan hazır betiği okumak ve uyarlamak

- **Dersler:** P76–P77 (`312e90b`). Yazar: başka ajan.
- **Denetim:** validate iki ortamda temiz; 2 tahmin uyuşuyor. Mutasyon 28 mutantın 25'i yakalandı; geçen 3'ü yalnız hata mesajındaki sayıyı değiştiriyor ("32 bit", "16 bayt"), testler mesaj metnine bakmadığı için eşdeğer.
- **Karşılananlar:** `context` ve endian, `p16`/`p32`/`u16`/`u32` işaretli ve işaretsiz paketleme, uzunluk denetimi; yerel bir oyuncak süreçle `process`/tube akışı, satır sınırı, `recvn` ile tam uzunluk, zaman aşımı ve EOF'un ayrılması; hazır bir paketleyiciyi uyarlama görevi.
- **Eksikler:** yok.
- **Karar:** **Tam.**
