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

## Madde 7 · Python · Impacket kullanan Windows/AD protokol betiğini okumak

- **Dersler:** P78–P79 (`b645c80`). Yazar: başka ajan.
- **Denetim:** anlık görüntü `9be539d`; validate (P78, P79, BS29, BS31–BS33 birlikte 52 kontrol) PowerShell ve Git Bash'te temiz; P79 tahmini uyuşuyor. Mutasyon: 67 mutantın 59'u yakalandı. Geçen 8'in 7'si yalnız hata mesajı metni (eşdeğer). **Biri gerçek, küçük bir test boşluğu:** P79 "Kaydedilmiş yanıt başlığını özetle" görevinde üst sınır `2**64 - 1` → `2**65 - 1` gevşetilince test fark etmiyor; `2**64` sınır değeri sınanmıyor.
- **Karşılananlar:** kurulu Impacket'in sürümü ve içe aktarma yolu kaydediliyor (ASAMA2'nin istediği); `LDAP_SID` ile ham SID baytları; `SMB2Packet` / `SMB2Echo` ile sabit kayıt üretmek ve yanıt başlığı alanlarını (komut, bayrak, MessageID, Status) okumak; sürüme bağlı yardımcı sınırları.
- **Eksikler:**
  - ASAMA2 "neden"inde "**örnek betiğin seçeneklerini** ve **bağımlılık sorunlarını** çözmek" var. Hazır bir Impacket örnek betiğinin (ör. `examples/` altındaki araçlar) komut satırı seçeneklerini okumak yalnız bir ipucunda anılıyor; görev yok. Bağımlılık sorunu (eksik/uyuşmaz paket) hiç yok.
  - Yukarıdaki `2**64` sınır testi.
- **Karar:** **Kısmen.**

## Madde 8 · Bash · curl/jq ile API ve JSON araç zinciri

- **Ders:** BS29 (`0362d53`). Yazar: başka ajan.
- **Denetim:** validate iki ortamda temiz; tahmin uyuşuyor. Mutasyon 11 mutantın 9'u yakalandı; geçen 2'si eşdeğer (bir yorum satırındaki sayı; `2> /dev/null`'un bozulması yalnız stderr'i etkiliyor, testler stdout'a bakıyor).
- **Karşılananlar:** curl'ün çıkış kodu ile HTTP durumunun ayrı olması (401'de 0, `--fail` 22, kapalı port 7, zaman aşımı 28), çerez kavanozu, `--json`, güvenli sorgu dizesi; `jq -r`, `@tsv`, `select`, `--arg` ile güvenli değişken geçirmek, `// empty`, bozuk JSON'un `jq empty` ile denetlenmesi.
- **Eksikler:**
  - ASAMA2 açıkça **`jq -e`** istiyor ve dersin özeti de "-e" diyor, ama **derste `jq -e` hiç kullanılmıyor** (`null`/`false` sonucunda sıfır olmayan çıkış kodu). Özet içerikten fazlasını vaat ediyor.
- **Karar:** **Kısmen.**

## Madde 9 · Bash · Linux süreç ve olay verisini kaynağından toplamak

- **Ders:** BS31 (`572363f`; A37 düzeltmesi kapandı). Yazar: başka ajan.
- **Denetim:** validate iki ortamda temiz; 2 tahmin uyuşuyor. Mutasyon 29 mutantın 24'ü yakalandı; geçen 5'i `2> /dev/null` yönlendirmesinin bozulması (yalnız stderr; eşdeğer).
- **Karşılananlar:** `/proc/<pid>` (status, NUL ayrımlı `cmdline` ve `environ`, 15 karakterlik ad, `exec -a` ile sahte argv[0]), `ps -o` ve süreç ağacı, `journalctl --file` ile dağıtılan günlük dosyası, UTC çıktısı, `systemd-journal-remote` ile kendi günlüğünü üretmek; çalışan servis varsayılmıyor.
- **Eksikler:** JSON çıktısı (`-o json`) yalnız bir tabloda anılıyor; hiçbir görevde kullanılmıyor (ASAMA2 "JSON/UTC çıktısı" diyor). Küçük.
- **Karar:** **Kısmen** (küçük).

## Madde 10 · Bash · rwx sonrası POSIX ACL ve Linux capabilities

- **Dersler:** BS32–BS33 (`0348358`). **Yazar 2 — kendi yazdığım dersler, çıkar çatışması.**
- **Denetim:** validate iki ortamda temiz; 2 tahmin uyuşuyor. Mutasyon 34 mutantın 30'u yakalandı; geçen 4'ü `>&2` / `2>/dev/null` yönlendirmesi (yalnız stderr; eşdeğer).
- **Karşılananlar:** adlı kullanıcı/grup girdileri, maske ve `#effective`, erişim denetimi sırası, `chmod`'un maskeyi değiştirmesi, varsayılan ACL ile kalıtım ve umask; capability maskelerini `/proc/PID/status` ve `capsh --decode` ile okumak, dosya capability'leri; **gerçek erişim karşılaştırması** `setpriv` ile başka kimlikle denenerek yapılıyor (ASAMA2'nin istediği).
- **Eksikler:** bulmadım. Kendi işim olduğu için bağımsız bir göz gerekli.
- **Karar:** **Tam** (çıkar çatışması notuyla).

> Madde 11–15 toplu ölçüm: 7 ders, validate iki ortamda temiz (57 denetim), 7 tahminin hepsi uyuşuyor, mutasyonda 165 mutantın 141'i yakalandı. Geçen 24 mutant aşağıda maddesine göre ayrıldı.

## Madde 11 · Bash · OpenSSH istemcisiyle komut ve dosya akışı

- **Dersler:** BS34–BS35 (`698d81e`, `a99aaa9`). **Yazar 2: dersleri ben yazdım, çıkar çatışması var.**
- **Denetim:** validate ve tahmin temiz. Geçen mutantlar:
  - BS34 `hata=1` değerinin değişmesi eşdeğer. Çıkış `$(( hata ? 2 : 0 ))` ile hesaplanıyor; sıfır olmayan her değer 2 veriyor.
  - `2>/dev/null` bozulmaları yalnız stderr'i etkiliyor; eşdeğer.
  - **BS35:5'te iki mutant gerçek boşluk.** `[[ -n $uzak_ozet && ... ]]` içindeki `&&`'nin `||` yapılması ve `uyuşmazlık` dalındaki `exit 1`'in değişmesi testten geçiyor. Yani **özet uyuşmazlığı hiç sınanmıyor**. Görevin adı "uzakta doğrula", ama yanlış özet veren ya da boş özette "tamam" diyen bir çözüm geçiyor.
- **Karşılananlar:**
  - Önce `ssh -G` ile bağlantı kurmadan config okuma (joker blok, `!` ile dışlama, ilk eşleşen değer).
  - Ayrılmış lab uç noktası: `sshd -i` ile ProxyCommand, ders için yazılmış config, önceden doğrulanmış known_hosts, `StrictHostKeyChecking yes`.
  - Gerçek uzak stdout, stderr ve çıkış kodu; 255'in iki anlamı.
  - `scp` ile gerçek dosya aktarımı; boşluklu ad, ikili ve boş dosya, yazılamayan klasör.
- **Eksikler:**
  - Özet uyuşmazlığı dalının testi yok (yukarıda).
  - `sftp` yalnız anlatıda geçiyor, görevde kullanılmıyor (ASAMA2 yalnız "dosya aktarımı" diyor; küçük).
- **Karar:** **Kısmen** (doğrulama dalının testi eksik). Çıkar çatışması notuyla.

## Madde 12 · Bash · ShellCheck ve Bats ile kendi aracını sınamak

- **Ders:** BS30 (`6b53bd0`). Yazar: başka ajan.
- **Denetim:** validate ve tahmin temiz. Geçen mutantlar:
  - BS30:4'te `boyut > enboyut` → `>=`: eşit boyutlu iki dosyada hangisinin yazılacağı sınanmıyor. Görev metni bu durumu da tanımlamıyor; bu yüzden hata değil, **belirsizlik**.
  - BS30:5'teki 6 mutantın tamamı öğrencinin Bats dosyasının içinde: test başlıkları ve aynı anlama gelen bozuk argümanlar (`1`, `1 2 3`, `1 iki`). Eşdeğer.
- **Karşılananlar:** gerçek ShellCheck 0.11 ve Bats 1.13 Linux'ta çalışıyor; `-S` eşiği, `-f gcc/json1`, çıkış kodları; boşluklu ve `-` ile başlayan ad fixture'ları; exit, stdout ve stderr ayrı ayrı denetleniyor; `setup()` kullanılıyor; testler bozuk uygulamalara karşı da çalıştırılıyor.
- **Eksikler:**
  - `teardown` yalnız tabloda anılıyor, hiçbir görevde kullanılmıyor (ASAMA2 "setup/teardown" istiyor).
  - ASAMA2 **"Git Bash ve Linux farkları ayrıca kaydedilir"** diyor. Ders yalnız "gerçek Linux'ta çalışır" diyor; farklar hiçbir yerde kayıtlı değil.
- **Karar:** **Kısmen.**

## Madde 13 · PowerShell · Invoke-RestMethod/WebRequest ile oturumlu API otomasyonu

- **Ders:** PS23 (`dc4cd2e`). Yazar: başka ajan.
- **Denetim:** validate ve tahmin temiz. Geçen mutant: PS23:6'da başarı dalındaki `"200|-"` metni değiştirilince test geçiyor. **2xx yolu hiç sınanmıyor**; testler yalnız 400–599 kodlarını ve geçersiz girdiyi deniyor. Küçük ama gerçek boşluk.
- **Karşılananlar:**
  - Yerel API ve gerçek `-SessionVariable`/`-WebSession` ile çerez.
  - `-Body` ile JSON gövde, sayfalama.
  - 201 + `Location` başlığı.
  - Hata gövdesini `ErrorDetails` ile okumak.
  - Durum kodu sınırları.
  - 5.1 ile 7 arasındaki farklar bir tabloda ayrılmış (`SkipHttpErrorCheck`, `StatusCodeVariable`, başlık okuma).
- **Eksikler:**
  - **Yönlendirme yok.** `-MaximumRedirection`, 3xx ve redirect hiçbir yerde geçmiyor; ASAMA2 açıkça istiyor.
  - **Timeout yalnız tabloda bir satır** (`-TimeoutSec 5`); hiçbir görevde yavaş yanıt ya da zaman aşımı sınanmıyor.
  - Form gövdesi (`-Form` / `application/x-www-form-urlencoded`) yok; NEDEN satırı "form/JSON gövdesi" diyor.
  - 2xx dalının testi yok (yukarıda).
- **Karar:** **Kısmen.**

## Madde 14 · PowerShell · Offline EVTX ve PowerShell 4104 kayıtları

- **Dersler:** PS27–PS28 (`403bd7a`; A37). Yazar: başka ajan.
- **Denetim:** validate ve tahmin temiz. Geçen mutantlar: iki derste de `-Oldest`'in silinmesi testten geçiyor. Bu eşdeğer: PS27 sonucu `Sort-Object Id, Level` ile sıralıyor, PS28 de blokları en küçük RecordId'ye, parçaları sıra numarasına göre sıralıyor. `-Oldest`'in etkisi anlatı ve tahminde gösteriliyor.
- **Karşılananlar:**
  - Gerçek EVTX fixture'larında (`ps_evtx_fixtures.py` ile üretiliyor) `Get-WinEvent -Path` ve `FilterXPath` ile zaman penceresi.
  - `Properties` dizinleri; 4104'ün parçalı blokları (ScriptBlockId, parça sırası, eksik blok işareti).
  - Boş dosya, okunamayan dosya ve eşleşmeyen sorgu tanıkları; sayısal sıralama tuzağı.
- **Eksikler:**
  - **`FilterXml` hiç yok** (ASAMA2 "FilterXPath/FilterXml" diyor). Yalnız `FilterHashtable` anlatılıyor.
  - **`ToXml()` yalnız tabloda bir satır**; hiçbir görevde ham XML'den alan okunmuyor (ASAMA2 açıkça istiyor).
- **Karar:** **Kısmen.**

## Madde 15 · PowerShell · Get-Acl ile NTFS/Registry erişim değerlendirmesi

- **Ders:** PS22 (`e47d743`). Yazar: başka ajan.
- **Denetim:** validate ve tahmin temiz. Geçen mutantlar:
  - PS22:5 döngü sınırı `-lt` → `-le`: döngü bir kez fazla dönüyor ve null satırda hata veriyor, ama karar değişmiyor; testler stderr'e bakmıyor. Küçük boşluk: stderr temizliği sınanmıyor.
  - Devralınan gruplardaki `-and` → `-or` mutantları geçiyor, çünkü hiçbir testte devralınan bir Allow, devralınan bir Deny'dan **önce** yazılmıyor. Kanonik sıranın son iki grubu tam sınanmıyor. Küçük.
- **Karşılananlar:**
  - SDDL'in alanları ve ACE tablosu.
  - Kanonik sıra ve Deny'ın üstünlüğüne göre etkin yetki hesabı.
  - Gerçek nesnelerde `Set-Acl`: geçici klasör ve `HKCU:\Software\PaftaAclGecici` anahtarı, devralma bayrakları, açık kurallar.
  - Temizliğin doğrulanması (`TEMIZ`).
  - Sahiplik ve ACL dışındaki halkalar uyarı notunda anlatılıyor.
- **Eksikler:**
  - ASAMA2 **"ACL nesnesinden rapor ve gerçek erişim sonucunu karşılaştırmak"** istiyor. Derste gerçek erişim **denenmiyor**: Deny kuralı konup okuma/yazma denenmiyor, `UnauthorizedAccessException` gözlenmiyor. Etkin yetki görevi metin girdisi üzerinde bir benzetim. Madde 10'daki `setpriv` denemesinin Windows karşılığı yok.
  - Test boşlukları yukarıda (küçük).
- **Karar:** **Kısmen** (gerçek erişim karşılaştırması eksik).
