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
- **Güncelleme (2026-10-25, `892ced3`):** kullanıcının isteğiyle eksikler kapatıldı. P75'e iki bölüm eklendi. (1) Sanal ortam ile `--target` paket deposunun (Pafta'nın `.deps`'i) rolleri; tahmin ve görev: `PYTHONPATH`'teki depo, ortamın kendi kopyasının önüne geçiyor. (2) Çakışan bağımlılık (`ResolutionImpossible`) ve çözücünün uyarısız geri izlemesini yakalayan görev. Kali'de ölçüldü (pip 26.1.2). Validate iki kabukta temiz; mutantlar ve elle 4 yanlış çözüm reddedildi. **Bu bölümü ben yazdım; çıkar çatışması var.** **Yeni karar: Tam.**

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
- **Güncelleme (2026-10-25, `892ced3`):** kullanıcının isteğiyle eksikler kapatıldı. P74'e bir anlatı ve dört görev eklendi: form gövdesi (`data=`, özel karakterli parola), kimlikli vekil ve `Via` ile kanıt (yanlış `proxies` anahtarının vekili uyarısız atlaması), ders CA'sıyla HTTPS doğrulaması (tanınmayan CA, ad uyuşmazlığı ve 404'ün ayrılması), kütüphane sürümünü yüklendiği klasörden kaydetmek. Tezgaha `/giris-form`, `vekil_kur()` ve `tls_kur()` eklendi; PS23 ve BS29 temiz. Validate iki kabukta temiz; elle 5 yanlış çözüm reddedildi. **Bu bölümü ben yazdım; çıkar çatışması var.** **Yeni karar: Tam.**

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
- **Güncelleme (2026-10-25, `f834b74`):** kullanıcının isteğiyle eksikler kapatıldı. Yeni `sandbox/ctypes_lab.py` küçük C kaynaklarını Kali'deki gerçek derleyicilerle (i686/x86_64 MinGW, gcc) derliyor. P82'ye öğrencinin kendi test DLL'i eklendi (anlatı, tahmin, görev): `void*` dönüşü artık kaynak metninden değil davranışla sınanıyor. P83'e 32 bit, LLP64 ve LP64 yerleşim görevi eklendi: 32 bit taraf gerçek bir 32 bit programın `sizeof`/`offsetof` ölçümüyle doğrulanıyor. Üç eksik de kapandı. Validate iki kabukta temiz; mutantlar 24/24; elle 9 yanlış çözüm reddedildi. **Bu bölümü ben yazdım; çıkar çatışması var.** **Yeni karar: Tam.**

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

> Madde 16–20 toplu ölçüm: 6 ders, validate iki ortamda temiz (38 denetim), 6 tahminin hepsi uyuşuyor, mutasyonda 121 mutantın 111'i yakalandı. Geçen 10 mutant aşağıda maddesine göre ayrıldı.

## Madde 16 · PowerShell · Authenticode imzasını dosya incelemesine katmak

- **Ders:** PS25 (`c0cdadb`). Yazar: başka ajan.
- **Denetim:** validate ve tahmin temiz. Geçen tek mutant PS25:4'te: `$Girdi[1]` → `$Girdi[2]` değişikliği testten geçiyor. Yayıncı satırının **boş ya da yalnız boşluk** olduğu durum sınanmıyor; yalnız satırın hiç olmadığı durum sınanıyor. Küçük.
- **Karşılananlar:**
  - Yerel örnek dosyalar: geçerli, bozulmuş (`HashMismatch`), imzasız betik (`NotSigned`), Microsoft ve üçüncü taraf yayıncı.
  - `Status` ve yayıncı CN'si; harfe duyarlı tam ad karşılaştırması. Geçerli imza tek başına güven sayılmıyor; beklenen yayıncı da şart.
  - Katalog imzası (`SignatureType`), zaman damgası, `UnknownError`/`NotTrusted`, iptal denetiminin ağa ve kök güven deposuna bağlılığı anlatıda açıkça belirtiliyor (ASAMA2'nin istediği).
- **Eksikler:** boş yayıncı satırının testi (küçük).
- **Karar:** **Tam** (küçük test notuyla).

## Madde 17 · PowerShell · Pester ile kendi testlerini yazmak

- **Ders:** PS26 (`2af3515`; A39). Yazar: başka ajan.
- **Denetim:** validate ve tahmin temiz. PS26:3'te mutasyon aracı mutant üretmedi, çünkü çözüm bir test dosyası. Bunun yerine dersin kendi testi öğrencinin Pester dosyasını **6 bozuk modüle karşı** çalıştırıyor; bu doğru yöntem. PS26:4'teki 5 geçen mutantın hepsi öğrencinin test dosyasındaki sabitler (Mock'lanan tarih, eşik saati). Testin anlamı değişmiyor; eşdeğer.
- **Karşılananlar:**
  - `Describe`/`Context`/`It`/`Should`, `BeforeAll`/`BeforeEach`.
  - `Mock -ModuleName` ve `Should -Invoke`.
  - `TestDrive:` ile geçici dosya; `Should -Throw` ile hata senaryoları.
  - Pester 5.9.0 `-RequiredVersion` ile sabitlenmiş; makinedeki 3.4 farkı not edilmiş.
  - Öğrencinin testlerinin bozuk sürümleri yakalaması şartı.
- **Eksikler:** bulmadım.
- **Karar:** **Tam.**

## Madde 18 · PowerShell · Gerçek PSSession yaşam döngüsü ve uzak çıktı

- **Ders:** PS29. **Yazar 2: dersi ben yazdım, çıkar çatışması var.** DENETIM'de durum hâlâ "denetime hazır"; bağımsız denetimi yapılmadı.
- **Denetim:** validate ve tahmin temiz. PS29:4'te geçen 2 mutant `{ 1 + 1 }` içindeki sayılar. Testler yalnız dönen türün `String` olduğuna bakıyor; eşdeğer.
- **Karşılananlar:**
  - `New-PSSession` → `Invoke-Command -Session` (durum oturumda kalıyor) → `Remove-PSSession` ve `State`.
  - Oturumun ayrı bir süreç olması.
  - Gerçek serileştirme ölçümü: `Deserialized.` türü ve metot kaybı; DateTime'ın sağlam gelmesi; betik bloğunun metne dönmesi.
- **Eksikler:**
  - **Ayrılmış Windows lab endpoint'i yok.** ASAMA2 bunu istiyor. Oturum `-UseWindowsPowerShell` ile yerel bir süreçte açılıyor; WinRM, `-ComputerName`, kimlik bilgisi ve ağ üzerinden bağlantı yok. Bu sınır DENETIM'de "kapsam dışı" olarak yazılmış, ama madde adındaki "gerçek uzak" tam karşılanmıyor.
  - **Hata ve temizlik akışı yok.** NEDEN satırı bunu istiyor. `try/finally` ile hata durumunda da oturumu kapatmak, uzak hatanın yerele nasıl geldiği (`ErrorRecord`, `-ErrorAction`), `Broken` durumu ve `Get-PSSession` ile sızan oturum avı görevlerde yok.
  - Disconnect/Reconnect yok (bilerek dışarıda bırakıldı).
- **Karar:** **Kısmen.** Çıkar çatışması notuyla.

## Madde 19 · PowerShell · CLM, JEA ve AppLocker (8002/8004) olayları

- **Ders:** PS24 (`1f608b9`). Yazar: başka ajan.
- **Denetim:** validate ve tahmin temiz; mutasyonda 46 mutantın hepsi yakalandı.
- **Karşılananlar:**
  - `$ExecutionContext.SessionState.LanguageMode` ile gerçek bir runspace'te CLM deneyi; ayrıştırma anında bağlanma tuzağı.
  - Anlatıda gerçek `.psrc` üretimi (`New-PSRoleCapabilityFile` + `Import-PowerShellDataFile`).
  - JEA risk denetimi ve çoklu rol birleştirme mantığı.
  - AppLocker 8002–8007 kimliklerinin anlamı ve kullanıcı başına korelasyon.
- **Eksikler:**
  - **AppLocker olayları gerçek EVTX değil.** Görev girdisi tek satırlık elle yazılmış XML dizeleri. ASAMA2 "çevrimdışı AppLocker EVTX (8002/8004) kayıtları" istiyor; `Get-WinEvent -Path` hiç kullanılmıyor. Projede EVTX fixture üreticisi (`ps_evtx_fixtures.py`) var, kullanılmamış.
  - **JEA görevleri gerçek `.psrc`/`.pssc` dosyası okumuyor.** Girdi, dosyanın JSON "özeti". `.pssc` yalnız anlatıda anılıyor; `Test-PSSessionConfigurationFile` görevde yok.
- **Karar:** **Kısmen.**

## Madde 20 · CMD · wevtutil ile offline EVTX sorgu ve export

- **Dersler:** CM19–CM20 (`def85ee`). Yazar: başka ajan.
- **Denetim:** validate ve tahmin temiz. Geçen 2 mutant (CM20:3 ve CM20:4) `>nul`'un `>=nul` yapılması; yalnız atılan çıktının gittiği yeri değiştiriyor, eşdeğer.
- **Karşılananlar:**
  - Gerçek EVTX örneklerinde `qe /lf:true`, `/q` XPath ile aralık, `/c` ve `/rd:true` ile en yeni N kayıt.
  - `epl` ile aktarım; `/ow` ile eski hedefin korunması.
  - Aktarılan dosyanın gerçek araçla yeniden açılıp **kayıtlarının tek tek** karşılaştırılması (yalnız sayı değil). `ElfFile` imzası.
  - Kaynağın değişmediğinin kanıtlanması.
  - Boş seçim, bozuk ve eksik kaynak; aşamaya göre ayrı hata kodları.
- **Eksikler:** bulmadım.
- **Karar:** **Tam.**

> Madde 21–30 toplu ölçüm: 14 ders (CM21–CM25, HT16–HT24), validate iki ortamda temiz (74 denetim), 14 tahminin hepsi uyuşuyor, mutasyonda 250 mutantın 211'i yakalandı.
>
> CMD derslerinde geçen mutantların çoğu `2>nul` → `3>nul` ya da `>&2` → `>&3`. Bunlar yalnız stderr'in nereye gittiğini değiştiriyor; eşdeğer sayıldı. Eşdeğer olmayanlar maddesinde ayrıca yazılı.
>
> **Kayıt eksiği:** madde 23, 24, 25, 26, 27, 29 ve 30 için dersler (CM25, HT17–HT24) HEAD'de commit'li. Buna rağmen `DENETIM.md`'de bu maddelerin durumu hâlâ "bekliyor"; madde 29'da "Yazar 2'de filtreye takıldı" yazıyor. Durum sütunu güncel değil.

## Madde 21 · CMD · Servis, zamanlanmış görev ve Registry sorgusu

- **Dersler:** CM21–CM22 (`8a64430`). Yazar: başka ajan.
- **Denetim:** validate ve tahmin temiz. Geçen 3 mutant `2>nul`; eşdeğer.
- **Karşılananlar:**
  - Önce örnek çıktılar, sonra gerçek `sc.exe qc`, `schtasks /query /fo CSV`, `reg query /v` ve `/f /e /c`.
  - Doğrulama yerel `sc.exe` ile bağımsız olarak yapılıyor.
  - Olmayan servis, görev ve değer için hata kodu sınanıyor.
- **Eksikler:** ASAMA2 **"boş/erişilemeyen sonuç"** istiyor. Olmayan kayıt sınanıyor, ama **erişim reddi** (korunan bir anahtar ya da servis; `Access is denied`) hiç sınanmıyor. Küçük.
- **Karar:** **Kısmen** (küçük).

## Madde 22 · CMD · Token, grup, ayrıcalık ve icacls

- **Dersler:** CM23–CM24 (`9ca6432`). Yazar: başka ajan.
- **Denetim:** validate ve tahmin temiz.
  - **CM23'ün hata yolu hiç sınanmıyor.** CM23:3'te 4 mutantın 4'ü geçti. Görev 3, 4 ve 5'te `exit /b 1` → `2` ve `>&2 echo token-hatasi` mutantları geçiyor. `whoami` başarısız olduğunda verilecek çıkış kodu ve mesaj hiçbir testte yok.
  - CM24:4'te geçen 4 mutant `2>nul`; eşdeğer.
- **Karşılananlar:**
  - `whoami /user /groups /priv` CSV olarak; Everyone SID'i.
  - Yönetici grubunun "deny only" ya da etkin olması; bütünlük seviyesi SID'leri.
  - `icacls` ile özel karakterli yol.
  - Gerçek okuma tanığı: `type` ile alınan baytlar kaynakla karşılaştırılıyor.
- **Eksikler:**
  - **Yalnız başarılı erişim tanığı var.** Anlatı `(DENY)`'den bahsediyor, ama hiçbir görevde DENY ACE'li bir dosyanın okunamadığı gösterilmiyor. ASAMA2 "hazır klasör/hesap bağlamları" istiyor; yalnız geçerli hesap kullanılıyor. Madde 15'teki eksikle aynı.
  - CM23 hata yolunun testi yok (yukarıda).
- **Karar:** **Kısmen.**

## Madde 23 · CMD · Sigcheck/Autorunsc ile karşılaştırmalı envanter

- **Ders:** CM25. **Yazar 2: dersi ben yazdım, çıkar çatışması var.** DENETIM durumu güncel değil ("bekliyor").
- **Denetim:** validate ve tahmin temiz. CM25:4'te geçen 2 mutant `type nul > eski_anahtar.txt` / `yeni_anahtar.txt` satırları. Bu dosyaların oluşturulması hiçbir sonucu etkilemiyor; **ölü kod**. Küçük temizlik.
- **Karşılananlar:**
  - Gerçek `sigcheck64.exe` ve `autorunsc64.exe` (`-accepteula`, `-c` CSV).
  - Sürüm notu (2.93).
  - İmzası sorunlu yürütülebilirleri ayırmak; iki başlangıç envanterini karşılaştırmak.
  - Hata kodları sınanıyor. Çevrimiçi (VirusTotal) sorgu yok; ASAMA2 de istemiyor.
- **Eksikler:** sürüm sabitleme yalnız notta; araçlar `.deps`'te değil, kurulum betiği yok (madde 1'deki genel eksikle bağlantılı). Bağımsız gözle bakılmalı.
- **Karar:** **Tam** (çıkar çatışması notuyla).

## Madde 24 · HTTP · Burp Proxy → History → Repeater

- **Ders:** HT17 (Codex). DENETIM durumu güncel değil.
- **Denetim:** validate ve tahmin temiz. HT17:2'de geçen 3 mutant girdi doğrulamasının sınırları (`or`→`and` tür denetimi, karakter kodu 32/33). Küçük test boşlukları.
- **Karşılananlar:**
  - Ders süresince yaşayan ve sıfırlanabilen kalıcı lab sunucusu (`--port 8769`, `reset`); Kali'deki Burp için yönerge.
  - Anlatıda gerçek Burp adımları: Open browser, History, Send to Repeater.
  - Görevlerde aynı oturumla tek değişkeni (hedefi) değiştirip yeniden üretmek; olay kaydıyla kanıt.
- **Eksikler:**
  - **Burp'ün kendisi hiçbir yerde ölçülmüyor.** Ders de bunu açıkça söylüyor ("Burp'un sekmelerini otomatik testler göremez"). Görevler Python `lab.request` ile yapılıyor. `docs/http-lab.md`'deki Burp kabul listesi elle. Madde adındaki "Burp iş akışı" otomatik kanıtla karşılanmıyor; öğrencinin Burp'ü gerçekten kullandığına dair bir tanık (ör. Burp'ten dışa aktarılan istek/yanıt dosyasının ayrıştırılması) yok.
- **Karar:** **Kısmen.**

## Madde 25 · HTTP · curl ile HTTPS, CA ve hostname doğrulaması

- **Ders:** HT18 (Codex). DENETIM durumu güncel değil.
- **Denetim:** validate ve tahmin temiz. HT18:2'de geçen 4 mutant yol doğrulamasındaki karakter sınırları (127/DEL, 32/33). HT18:3'te 24 mutantın hepsi yakalandı.
- **Karşılananlar:**
  - Yerel TLS ucu ve ders sertifikaları (`http_tls_lab.py`); çağrıya özel `--cacert`.
  - Bilinmeyen CA ve yanlış hostname (60), TLS bağlantı hatası (35), başarılı doğrulama, `--resolve`.
  - `-k`/`--insecure` tuzağı; HTTP hatasını TLS hatasından ayırmak.
- **Eksikler:** yalnız yol doğrulamasının sınır testleri (küçük).
- **Karar:** **Tam.**

## Madde 26 · HTTP · Gerçek tarayıcıda CORS/preflight ve oturuma bağlı CSRF

- **Dersler:** HT19–HT20 (Codex). DENETIM durumu güncel değil.
- **Denetim:** validate ve tahmin temiz. HT19:2'de geçen 1 mutant `wildcard_get` sayımındaki `and`→`or`; küçük.
- **Karşılananlar:**
  - **Gerçek tarayıcı:** Edge/Chromium ve playwright-core (`http_browser_lab.py`).
  - İki origin; preflight `OPTIONS` ve okunabilirlik sonucu.
  - Oturuma bağlı CSRF jetonu: başka oturumun jetonu reddediliyor ve revizyon değişmiyor, yani yazma gerçekten durmuş.
  - SameSite deneyi farklı **site** bağlamında yapılıyor (`app.pafta.test` / `evil.other.test`), yalnız farklı port değil.
- **Eksikler:**
  - SameSite gerçek tarayıcıda yalnız **tahmin** adımında gösteriliyor; görevlerde değil. Görevler Python istemcisiyle yapılıyor.
  - "Network gözlemi" sunucu tarafı olay listesinden okunuyor; tarayıcının kendi ağ kaydı (DevTools/HAR) kullanılmıyor. Küçük.
- **Karar:** **Tam** (küçük notlarla).

## Madde 27 · HTTP · İki hesaplı nesne yetkilendirme matrisi

- **Ders:** HT21 (Codex). DENETIM durumu güncel değil.
- **Denetim:** validate ve tahmin temiz; mutantların hepsi yakalandı.
- **Karşılananlar:**
  - A, B ve oturumsuz hesap; farklı sahiplikteki kayıtlarda GET ve PATCH matrisi (12 hücre).
  - "Değişti" bilgisi HTTP kodundan değil durumun kendisinden türetiliyor.
  - Olay kaydı ve revizyon sayısı sınanıyor.
- **Eksikler:** bulmadım.
- **Karar:** **Tam.**

## Madde 28 · HTTP · JWT, imza doğrulama tuzakları ve OAuth2/OIDC

- **Ders:** HT16 (`7ee458e`).
- **Denetim:** validate ve tahmin temiz; mutasyonda 43 mutantın hepsi yakalandı.
- **Karşılananlar:**
  - Katı JWT doğrulayıcı (RFC 7519/8725): `alg`, imzasız token, süresi dolmuş token, yanlış audience.
  - `redirect_uri`/`state` denetçisi ve PKCE S256 (RFC 9700/7636).
  - Yerel sahte IdP ve kaynak sunucusuyla uçtan uca istemci.
- **Eksikler:** bulmadım.
- **Karar:** **Tam.**

## Madde 29 · HTTP · SSRF, URL ayrıştırıcı farkları ve yönlendirme zinciri

- **Ders:** HT22 (Codex). DENETIM durumu güncel değil ("Yazar 2'de filtreye takıldı" yazıyor, ama ders yazılmış).
- **Denetim:** validate ve tahmin temiz. HT22:3'te 22 mutantın 9'u geçti:
  - **`max_redirects=3` → `4` geçiyor:** yönlendirme sınırı hiç sınanmıyor. Sonsuz ya da uzun zincirde durmak SSRF savunmasının parçası.
  - `300 <= status <= 399` sınırları (300 ve 399) sınanmıyor.
  - `Location` içindeki denetim karakteri kontrolü sınanmıyor.
  - HT22:2'de URL karakter sınırları (32/127) sınanmıyor.
- **Karşılananlar:**
  - İki loopback hizmetiyle dış/iç hedef benzetimi.
  - 301/302/307/308 zinciri; her hop'ta yeniden doğrulama; yöntemin bilinçli taşınması.
  - `urllib.parse` farkları (`127.1`, `2130706433`, `\@`, userinfo, `#`).
  - DNS rebinding ve IDNA'nın kapsam dışı olduğu açıkça yazılmış.
- **Eksikler:** yönlendirme sınırının ve durum kodu sınırlarının testi yok (yukarıda).
- **Karar:** **Kısmen** (test boşluğu; içerik tam).

## Madde 30 · HTTP · WebSocket (101) ve GraphQL

- **Dersler:** HT23–HT24 (Codex). DENETIM durumu güncel değil.
- **Denetim:** validate ve tahmin temiz. HT23'te 15 mutantın hepsi yakalandı. HT24'ün çözümleri sorgu metni, bu yüzden mutant üretilmedi. Testler, metni gerçek `graphql-core` motoruna ve lab'e çalıştırarak doğruluyor.
- **Karşılananlar:**
  - Gerçek soket üzerinden el sıkışma ve 101 kanıtı (`Sec-WebSocket-Accept`), maskeli text çerçevesi, `Origin`.
  - GraphQL: parametreli sorgu (değer `variables` içinde), introspection, mutation hatasını `errors` içinden okumak.
  - Alan düzeyinde yetki: `secret` alanının sahibe göre görünmesi.
- **Eksikler:** bulmadım.
- **Karar:** **Tam.**

> Madde 31–40 toplu ölçüm: 10 ders (SQ19–SQ22, KQ22–KQ24, SP21–SP23), validate iki ortamda temiz (87 denetim), 12 tahminin hepsi uyuşuyor. SQL ve KQL mutasyonunda 72 mutantın 70'i yakalandı. SPL mutasyonu her mutantta gerçek Splunk'a yeniden veri yüklediği için saatler sürüyor; sonucu madde 45–48 bölümünün başına eklendi.
>
> **Kayıt eksiği:** 35, 36, 38, 39 ve 40'ın dersleri (KQ23, KQ24, SP21, SP22, SP23) commit'li, ama DENETIM'de durumları "bekliyor". Bu beş ders **benim**; durumu güncellemeyi unutmuşum.

## Madde 31 · SQL · SQLite dışındaki lehçeler gerçek motorlarda

- **Ders:** SQ22 (`05b1a4e`, `aef27d3`, `99b8b97`).
- **Denetim:** validate, tahmin ve mutasyon temiz (2/2).
- **Karşılananlar:** gerçek PostgreSQL ve MariaDB motorları (`motor: postgres` / `mariadb`). `LIMIT`/`FETCH`, `||` ile `CONCAT`, `::` ile `CAST`, `information_schema` farkları. SQLite korunmuş.
- **Eksikler:**
  - ASAMA2 **"MySQL ve SQL Server için sürümü sabit yerel servis/imaj"** istiyor. İkisi de yok; SQL Server'ın `TOP` sözdizimi yalnız anlatıda geçiyor.
  - MariaDB'nin MySQL'den farkı anılıyor, ama gerçek bir MySQL ile karşılaştırma yok.
- **Karar:** **Kısmen.**

## Madde 32 · SQL · Uygulama girdisinden SQL'e veri akışı ve parametre bağlama

- **Ders:** SQ19 (`3234635`).
- **Denetim:** validate, tahmin ve mutasyon temiz. Testler sınır değerlerini (71/72/73), tırnağı, NULL'u ve boş metni tek tek deniyor.
- **Karşılananlar:** formdan metin olarak gelen eşik; `CAST` tuzağı (`'abc'` → 0, `'12abc'` → 12); NULL ve boş değer; izinli sıralama alanı; joker karakterin kaçırılması.
- **Eksikler:**
  - ASAMA2 **"küçük yerel uygulama–DB köprüsü"** istiyor. Görevler saf SQL: "formdan gelen" değer bir tabloya önceden yazılmış olarak duruyor. Uygulama tarafında gerçek parametre bağlama (Python `sqlite3` ile `?`, `execute(sql, params)`) ya da birleştirilmiş metinle bağlanmış parametrenin karşılaştırması bir görevde yok.
  - Java/PHP/C# derslerindeki güvenli sorgulara köprü kurulmamış.
- **Karar:** **Kısmen.**

## Madde 33 · SQL · Veritabanı rolleri ve etkili yetkiler

- **Ders:** SQ21 (`05b1a4e`, `c48f84a`).
- **Denetim:** validate ve tahmin temiz. Çözümler DDL olduğu için mutant üretilmedi. Testler `yapabilir(rol, sql)` ile sorguyu gerçekten o rol olarak çalıştırıyor ve reddedilmesini bekliyor.
- **Karşılananlar:** gerçek PostgreSQL. `LOGIN`/`NOLOGIN`, rol üyeliği ve `INHERIT`/`NOINHERIT`, `GRANT`/`REVOKE`, sütun düzeyi yetki, `PUBLIC`. Sequence yetkisi tuzağı. Yetkisiz okuma, yazma, güncelleme ve silmenin gerçekten reddedilmesi.
- **Eksikler:** bulmadım.
- **Karar:** **Tam.**

## Madde 34 · SQL · SQL içinden JSON kayıtlarını sorgulamak

- **Ders:** SQ20 (`a0290ad`).
- **Denetim:** validate, tahmin ve mutasyon temiz (2/2).
- **Karşılananlar:** SQLite `json_extract`, `->`/`->>`, `json_each`, `json_type`. Olmayan anahtar, JSON null ve SQL NULL ayrımı; bozuk JSON; `"3"` metni ile `3` sayısının farkı.
- **Eksikler:**
  - ASAMA2 **"PostgreSQL jsonb için ayrı görevler"** istiyor. jsonb yalnız bir karşılık tablosunda; ders "burada çalışmaz" diyor. Oysa projede gerçek PostgreSQL motoru var (SQ21–SQ22 kullanıyor). jsonb görevi yok.
- **Karar:** **Kısmen.**

## Madde 35 · KQL · Sentinel/Defender şemaları ve watchlist

- **Ders:** KQ24. **Yazar 2: dersi ben yazdım, çıkar çatışması var.**
- **Denetim:** validate, tahmin ve mutasyon temiz (5/5).
- **Karşılananlar:** gerçek alan adlarıyla anonim `SigninLogs`, `DeviceProcessEvents`, `DeviceNetworkEvents` örnekleri; `_GetWatchlist` karşılığı ve `SearchKey`; yönetici hesapları, Office'ten açılan kabuk, kötü IP listesi.
- **Eksikler:**
  - ASAMA2'nin istediği **canlı doğrulama (tenant/ürün bağlantısı) yok.** Abonelik gerektiği için beklenen bir sınır, ama sorgular gerçek Sentinel'de hiç çalıştırılmadı.
  - Sorgular yerel motorda (SQLite'a çeviri) çalışıyor; gerçek Kusto'da sınanmadı.
- **Karar:** **Kısmen** (canlı doğrulama dış bağımlılık). Çıkar çatışması notuyla.

## Madde 36 · KQL · mv-apply ve bag_unpack

- **Ders:** KQ23. **Yazar 2: dersi ben yazdım, çıkar çatışması var.**
- **Denetim:** validate, tahmin ve mutasyon temiz (11/11).
- **Karşılananlar:** `mv-apply` ile her dizide alt sorgu (en yavaş iki ölçüm); boş dizide kaydı kaybetmemek; `bag_unpack` ve sütunların veriye bağlı olması.
- **Eksikler:**
  - ASAMA2 **"önce KQ21'deki gerçek Kusto bağlantısında görev"** diyor. Ders gerçek Kusto'da değil; SQLite'a çeviren yerel motorda çalışıyor. Ders bunu açıkça yazıyor; alt sorguda yalnız birkaç işleç destekleniyor.
  - Yerel motora eklendiği hâlde ASAMA2'nin istediği **`OutputSchema`** ve **tür uyuşmazlığı** testleri yok. Eksik özellik ve boş dizi var.
- **Karar:** **Kısmen.** Çıkar çatışması notuyla.

## Madde 37 · KQL · Avcılık sorgusundan zamanlanan Sentinel kuralına

- **Ders:** KQ22 (`13fd071`, `e0a8e37`).
- **Denetim:** validate ve tahmin temiz. Mutasyonda 51 mutantın 49'u yakalandı. Geçen 2'si `range ... to` bitiş saatleri; eşdeğer (yeni adım eklemiyor ya da olaysız çalıştırma ekliyor).
- **Karşılananlar:** çalıştırma sıklığı ile lookback'in kurduğu pencere dizisi; kaçan ve iki kez sayılan olaylar; geç gelen kayıt ve `ingestion_time`; eşik.
- **Eksikler:**
  - ASAMA2'nin istediği **gerçek Sentinel'de kural önizlemesi/çıktı karşılaştırması yok** (abonelik gerekiyor). DENETIM'de de "yerel benzetim" olarak not edilmiş.
  - Entity mapping yalnız bir kez anılıyor; görevde yok.
- **Karar:** **Kısmen.**

## Madde 38 · SPL · Gerçek log alımı, olay sınırı ve zaman

- **Ders:** SP21. **Yazar 2: dersi ben yazdım, çıkar çatışması var.**
- **Denetim:** validate ve tahmin temiz; mutasyon sonucu 45–48 bölümünde.
- **Karşılananlar:** gerçek Splunk Enterprise'ta `props.conf`: `LINE_BREAKER`, `SHOULD_LINEMERGE`, `TIME_PREFIX`, `TIME_FORMAT`, `MAX_TIMESTAMP_LOOKAHEAD`, `TZ`. Ham örnek dosyalar; alınan olay sayısının ve `_time`'ın doğrulanması.
- **Eksikler:** bulmadım. Bağımsız gözle bakılmalı.
- **Karar:** **Tam** (çıkar çatışması notuyla).

## Madde 39 · SPL · CIM ve tstats gerçek veri modelinde

- **Ders:** SP23. **Yazar 2: dersi ben yazdım, çıkar çatışması var.**
- **Denetim:** validate ve tahmin temiz; mutasyon sonucu 45–48 bölümünde.
- **Karşılananlar:** gerçek Splunk'ta veri modeli ve `tstats`; `summariesonly` ile ham sonucun karşılaştırılması; hızlandırma ve özet kapsamı; SQLite ile hız iddiası yok.
- **Eksikler:**
  - ASAMA2 **Authentication/Endpoint** verisi istiyor; ders **Web** modelini kullanıyor. Authentication senaryosu yazılırken güvenlik filtresine takıldım ve modeli değiştirdim. Endpoint de yok.
  - (Karşılanan: resmi CIM eklentisi `Splunk_SA_CIM` 8.5.0 laboratuvarda kurulu ve sürümü yazılı.) Eklentinin kurulumu otomatik değil, Splunkbase hesabıyla elle indiriliyor. Başka makinede kurulum için madde 1'deki kurulum betiği eksiğiyle bağlantılı.
- **Karar:** **Kısmen.** Çıkar çatışması notuyla.

## Madde 40 · SPL · Zamanlanan alarm, tetikleme ve bastırma

- **Ders:** SP22. **Yazar 2: dersi ben yazdım, çıkar çatışması var.**
- **Denetim:** validate ve tahmin temiz; mutasyon sonucu 45–48 bölümünde. Önceden bilinen kararsızlık: bir tahmin yaklaşık 8 çalıştırmada bir farklı çıkıyor (yalnız gösterim).
- **Karşılananlar:** gerçek `savedsearches.conf`; `cron_schedule` ile `dispatch.earliest/latest_time`'ın boşluksuz ve çakışmasız pencere dizisi; `counttype`/`relation`/`quantity` ile eşik altı, eşit ve üstü; iki varlık; `alert.suppress` ve `fields` ile varlık başına bastırma.
- **Eksikler:** tahmin kararsızlığı (küçük).
- **Karar:** **Tam** (küçük notla; çıkar çatışması notuyla).

> Madde 41–50 toplu ölçüm:
>
> - **Elastic:** 8 ders (EL20–EL27), gerçek Elasticsearch/Kibana 9.5.5 (Basic). Validate temiz, ama **ilk çalıştırmada EL20 ve EL21 "Yerel Elastic API erişilemiyor: timed out" ile düştü.** O sırada başka bir arka plan işi Splunk'ı yüklüyordu; yeniden denemede ikisi de geçti. Yük altında zaman aşımı kararsızlığı var. 8 tahminin hepsi uyuşuyor; mutasyonda 43 mutantın hepsi yakalandı. EL20, EL21 ve EL27'nin çözümleri JSON/ES|QL belgesi olduğu için genel araç mutant üretmedi; bunlar için projenin kendi `tools/audit_elastic_mutations.py` aracı var.
> - **YARA:** 4 ders (YR19–YR22). Validate temiz, 4 tahminin hepsi uyuşuyor, 38 mutantın hepsi yakalandı.
> - **Sigma:** SG19–SG22. Ölçüm aşağıda maddelerinde.
>
> **Kayıt eksiği:** 41–48 ve 50 için dersler snapshot'ta var. Buna rağmen DENETIM'de durumları "bekliyor".

## Madde 41 · Elastic · Gerçek telemetri alımı, ECS ve ingest eşlemesi

- **Dersler:** EL20–EL21 (Codex).
- **Karşılananlar:**
  - Gerçek Elasticsearch'te dosyadan ingest pipeline; `_simulate`; ECS alanları ve `event.category` sınıflandırması.
  - Hatalı mapping kanıtı: 32 bit sayı taşması, zaman dilimi ve tarih ayrıştırma hatası. Eksik alan.
  - Gerçek üst süreç gözlemi ile telemetri.
- **Eksikler:**
  - **Elastic Agent yok.** Ders Elastic Agent ya da Sysmon olayı olmadığını açıkça söylüyor. ASAMA2 "Elastic Agent **veya** dosya alımı" dediği için şart karşılanıyor, ama ajan tabanlı alım öğretilmiyor.
  - Yük altında zaman aşımı kararsızlığı (yukarıda).
- **Karar:** **Tam** (notlarla).

## Madde 42 · Elastic · EQL işlevleri ve gerçek backend

- **Dersler:** EL22–EL23 (Codex).
- **Karşılananlar:** gerçek `_eql` API'si; `endsWith`, `between`, ayırıcı tuzağı; `sequence`, `until`, `maxspan`, eksik olay (`!`); yerel tezgaha sessiz dönüş yok.
- **Eksikler:** ASAMA2 **"mevcut tahminleri de aynı veri/mapping ile karşılaştıran otomatik denetim"** istiyor. EL13–EL18'deki yerel EQL tahminlerini gerçek Elasticsearch'te çalıştırıp sonucu karşılaştıran bir araç bulamadım. `tools/test_elastic_integration.py` yalnız tahmin çağrısının çalıştığını sınıyor; yerel ile gerçek motoru karşılaştırmıyor.
- **Karar:** **Kısmen.**

## Madde 43 · Elastic · Security tespit kuralı olarak işletmek

- **Dersler:** EL24–EL25 (Codex).
- **Karşılananlar:**
  - Gerçek Kibana'da custom query (`kuery`) ve event correlation (`type: eql`) kuralı.
  - `interval` ile `from` farkı; threshold; gerçek exception list.
  - Lisans açıkça belirtilmiş (Basic, 9.5.5); kural yetkisi ve API anahtarı anlatılıyor.
- **Eksikler:** görevler kuralı **devre dışı** kaydedip tek bir **önizleme** yürütmesiyle ölçüyor. Gerçek zamanlayıcının çalıştırdığı etkin kural ve operational alarm indeksi yalnız "teslim kabul betiği"nde ölçülüyor; öğrenci görevinde değil. Ders bu ayrımı açıkça yazıyor. Küçük.
- **Karar:** **Tam** (küçük notla).

## Madde 44 · Elastic · ES|QL ile toplama ve dönüştürme

- **Dersler:** EL26–EL27 (Codex). ASAMA2'de bu madde için ayrıntılı satır yok.
- **Karşılananlar:** gerçek `_query` API'si; `STATS`, `EVAL`, `KEEP`, `SORT`, `WHERE`; çok değerli alanlar; `null` ile kullanıcı yokluğunun korunması; boş girdi.
- **Eksikler:** `DISSECT`/`GROK` ile metin ayrıştırma yok. ASAMA2 istemiyor; bilgi notu.
- **Karar:** **Tam.**

## Madde 45–48 · Sigma

**SG19–SG22'nin dördünü de ben yazdım; çıkar çatışması var.** Bu eksikleri kullanıcıya daha önce sözlü olarak bildirmiştim; burada kayda geçiriyorum. DENETIM'de dört maddenin durumu da "bekliyor"; güncel değil.

Ölçüm: SG19–SG22 validate'i Git Bash'te temiz (18 denetim); 4 tahminin hepsi uyuşuyor. PowerShell'deki ikinci validate ile SPL/Sigma mutasyonu gerçek Splunk'ta saatler sürüyor; sonuçları bu raporun sonuna ayrı bir ek olarak yazılacak.

Dört maddede ortak eksik: **altyapı testi yok.** `tools/test_sigma_runtime.py` yalnız yerel Sigma eşleştiricisini sınıyor. Splunk'a çeviren koşucu (`SigmaSplunkRunner`: pipeline seçimi, `kural`/`pipeline` girdisi, veri yükleme) için hiçbir test yok.

### Madde 45 · sigma-cli, gerçek backend ve processing pipeline

- **Ders:** SG19 (tek görev).
- **Karşılananlar:** gerçek pySigma Splunk backend'i; `sysmon`, `windows` ve `splunk_windows` pipeline'ları; öğrencinin kendi pipeline'ını yazması. Üretilen sorgu, gerçek Splunk'ta aynı olaylarla sınanıyor.
- **Eksikler:**
  - **sigma-cli hiç kullanılmıyor.** Madde adında ve ASAMA2'de var. Öğrenci `sigma convert` komutunu hiç çalıştırmıyor; dönüşümü tezgah pySigma kütüphanesiyle arka planda yapıyor.
  - **Yalnız Splunk.** NEDEN satırı "Splunk/Elastic/Sentinel" diyor. Projede gerçek Elasticsearch 9.5.5 ve KQL motoru var, ama Elastic ya da Kusto backend'i hiç yok.
- **Karar:** **Kısmen.**

### Madde 46 · Çalıştırılan korelasyon kuralları

- **Ders:** SG20.
- **Karşılananlar:** `event_count` ve `value_count` korelasyonları gerçek Splunk'ta çalışıyor; `group-by`, `timespan`. Splunk backend'inin sabit zaman kutuları kurduğu (kayan pencere değil) ve sınırın iki yanına düşen olayların sayılmadığı gösteriliyor. Aynı adrese yinelenen bağlantılar `value_count` ile ayrılıyor.
- **Eksikler:**
  - **Zamansal korelasyon (`temporal` / `temporal_ordered`) hiç yok.** NEDEN satırı "zamansal ilişkiyi yazıp gerçekten çalıştırmak" diyor; GEREKİR satırı "sıra" testleri istiyor.
- **Karar:** **Kısmen.**

### Madde 47 · Gerçek olaydan kurala telemetri doğrulaması

- **Ders:** SG21.
- **Karşılananlar:** kural sessizse üç nedenin ayrılması: kanal toplanmıyor, alan çıkarılmıyor (`KV_MODE=none` / `INDEXED_EXTRACTIONS`), alan hiç yazılmıyor. Sysmon kuralını 4688 alanlarına uyarlamak; kör noktayı bulan tanık kuralı.
- **Eksikler:**
  - **Gerçek EVTX/XML yok.** Olaylar sentetik JSON. ASAMA2 "sürümü belli EVTX/XML örneklerini normalleştirmek" istiyor. Projede EVTX fixture üreticisi (`ps_evtx_fixtures.py`) var, kullanılmamış.
  - PS21/PS27'deki olay okuma bilgisine köprü kurulmamış.
- **Karar:** **Kısmen.**

### Madde 48 · İleri modifier'lar gerçek hedefte

- **Ders:** SG22.
- **Karşılananlar:** her modifier'ın Splunk'ta neye dönüştüğü ölçülmüş ve tabloya yazılmış. Görevlerde `windash`, `wide|base64offset` (gerçek UTF-16LE PowerShell yükü) ve `cidr` (ağların son adresleri dahil). `fieldref`'in Splunk'ta harfe duyarlı `where`'e dönüşmesi ve `cased`'in desteklenmemesi gösteriliyor.
- **Eksikler:**
  - **`re` ve `fieldref` görevde yok.** `fieldref` yalnız tahmin adımında, `re` yalnız tabloda. Görev sayısı 2.
  - `utf16le`/`utf16be` (NEDEN satırında adı geçiyor) ayrı bir görevde yok; yalnız `wide` kullanılıyor.
- **Karar:** **Kısmen.**


## Madde 49 · YARA · PE import/export ve bölüm özellikleri

- **Dersler:** YR19–YR20 (`b4b7432`).
- **Karşılananlar:** gerçek libyara `pe` modülü; `pe.imports` DLL+işlev çifti (harf büyüklüğü, başka DLL); export adı ve ordinal; `pe.sections` ile bölüm adı, yürütme ve yazma biti, tam eşik.
- **Eksikler:**
  - ASAMA2 **"farklı derleyici/32–64 bit örnekleri"** istiyor. Örnekler `yara_pe_fixtures.pe_fixture()` ile Python'da sentezleniyor. Gerçek bir derleyicinin (MSVC/MinGW) çıktısı yok; `pe.is_32bit`/`is_64bit`/`machine` hiçbir görevde yok.
  - Bozuk başlık tanığı zayıf: "bozuk" yalnız bir kez geçiyor. Eksik import tablosu görevde ayrıca sınanmıyor.
- **Karar:** **Kısmen.**

## Madde 50 · YARA · ELF ve .NET modülleri

- **Dersler:** YR21–YR22. DENETIM durumu güncel değil.
- **Karşılananlar:**
  - `elf` modülü: mimari, `ET_DYN`/`ET_EXEC`, salt okunur bölüm ve sınır. Örnekler gcc ile derlenmiş.
  - `dotnet` modülü: assembly adı ve kapsayıcı sürüm aralığı; namespace dahil sınıf kimliği. Örnekler kurulu .NET 8 SDK ile derlenmiş, çalıştırılmıyor.
  - Native PE ve ELF'in managed sayılmadığı tanıklar.
- **Eksikler:** bulmadım.
- **Karar:** **Tam.**

> Madde 51–60 toplu ölçüm: 15 ders (RX23–RX24, PK19–PK29, AD13–AD14), validate temiz (87 denetim), 15 tahminin hepsi uyuşuyor, mutasyonda **78 mutantın hepsi yakalandı**. Bazı adımlarda mutant üretilmedi; bunlar yalnız desen ya da filtre metninden oluşan çözümler. Bu adımların testleri çözümü gerçek motorda (PCRE2, .NET, Node, TShark) çalıştırıyor.
>
> **Kayıt eksiği:** madde 55–60 için dersler (PK19–PK29, AD13–AD14) snapshot'ta var. Buna rağmen `DENETIM.md`'de durumları "bekliyor".

## Madde 51 · YARA · Dış değişkenler, include ve namespace

- **Ders:** **yok.** YARA yolu YR22'de bitiyor; bu maddeye ait ders yazılmamış. DENETIM'de sahibi Codex, durumu "bekliyor".
- **Eksikler:** maddenin tamamı: `externals`, kaynak sözlüğü ve namespace, ders dosyalarıyla sınırlı include callback, tanımsız değişken ve ad çakışması testleri. Tezgahın `includes=False` sınırı da genişletilmemiş.
- **Karar:** **Eksik.**

## Madde 52 · YARA · Toplu tarama, çıktı ve maliyet ölçümü

- **Ders:** **yok.** DENETIM'de sahibi Codex, durumu "bekliyor".
- **Eksikler:** maddenin tamamı: klasör tarayıcı, dosya/eşleşme raporu, timeout ve uyarı davranışı, küçük/büyük/eşleşmeyen korpusla süre ölçümü.
- **Karar:** **Eksik.**

## Madde 53 · Regex · Lehçe bilgisini gerçek motorlarda sınamak

- **Ders:** RX24 (`6291614`, `94a3b76`, `97ef3e8`). **Yazar 2: DENETIM'de sahibi Yazar 2; çıkar çatışması var.**
- **Denetim:** validate ve tahmin temiz. RX24:4'te 10 mutantın hepsi yakalandı. Desen çözümleri gerçek JavaScript, .NET ve PCRE2 motorlarında çalıştırılıyor.
- **Karşılananlar:** Python `re`, .NET, Node (JavaScript) ve PCRE2 için ayrı adaptörler. `\d` ve `\w`'nun motora göre değişen Unicode kapsamı (JavaScript'te Türkçe kelime, .NET'te yalnız ASCII port), bayrak koyulamayan motorda satır sonu.
- **Eksikler:** ASAMA2 "eşleşme aralığı karşılaştırması" diyor. Testler eşleşen metne bakıyor; aynı korpusta motorlar arasında başlangıç/bitiş konumlarını yan yana karşılaştıran bir görev görmedim. Küçük.
- **Karar:** **Tam** (küçük notla; çıkar çatışması notuyla).

## Madde 54 · Regex · PCRE2 subroutine/recursion ve kontrol fiilleri

- **Ders:** RX23 (`6291614`, `9000f66`). **DENETIM'de sahibi Yazar 2; çıkar çatışması var.**
- **Denetim:** validate ve tahmin temiz. RX23:7'de 5 mutantın hepsi yakalandı. Diğer görevlerin çözümleri desen metni; testler bunları gerçek PCRE2'de çalıştırıyor.
- **Karşılananlar:** `(?R)`, `(?&ad)`, `DEFINE`, branch reset `(?|...)`, `(*SKIP)(*FAIL)`. Yapının Python `re`'de olmadığı söyleniyor, zorla çevrilmiyor.
- **Eksikler:** bulmadım.
- **Karar:** **Tam** (çıkar çatışması notuyla).

## Madde 55 · Packets · PCAPNG ve farklı link-layer türleri

- **Dersler:** PK19–PK20. DENETIM durumu güncel değil.
- **Denetim:** validate, tahmin ve mutasyon temiz.
- **Karşılananlar:** TShark ile PCAPNG; birden çok arayüz (`frame.interface_id`); kesilmiş paket; DLT'ye göre BPF (Ethernet, SLL dahil dört link-layer); `if_tsresol` anılıyor.
- **Eksikler:** zaman çözünürlüğünün (`if_tsresol`) korunduğu yalnız anlatıda geçiyor; hiçbir görev nano/mikro saniye farkını sınamıyor. Küçük.
- **Karar:** **Tam** (küçük notla).

## Madde 56 · Packets · TLS/HTTP2/QUIC ve görünürlük sınırı

- **Dersler:** PK21–PK22. DENETIM durumu güncel değil.
- **Denetim:** validate, tahmin ve mutasyon temiz.
- **Karşılananlar:** ClientHello SNI; sır yok, yanlış sır ve doğru sır durumları ayrı test ediliyor; sırlar geçici TShark profiline veriliyor. "Anahtar yoksa boş sonuç, '201 gönderilmedi' anlamına gelmez" tuzağı. QUIC Initial ve stream yükü.
- **Eksikler:** bulmadım.
- **Karar:** **Tam.**

## Madde 57 · Packets · TCP yeniden birleştirme ve analist iş akışı

- **Dersler:** PK23–PK24. DENETIM durumu güncel değil.
- **Denetim:** validate, tahmin ve mutasyon temiz.
- **Karşılananlar:** retransmission ve out-of-order etiketleri; iki geçişli analiz (`-2`); reassembly tercihleri; Follow Stream; `--export-objects` ile gövdenin baytları. Yeniden birleştirilmiş veri ile tek frame arasındaki fark gösteriliyor.
- **Eksikler:** "kayıp segment" (`tcp.analysis.lost_segment`) görevlerde yok. Küçük.
- **Karar:** **Tam** (küçük notla).

## Madde 58 · Packets · SMB2, Kerberos ve LDAP

- **Dersler:** PK25–PK27. DENETIM durumu güncel değil.
- **Denetim:** validate, tahmin ve mutasyon temiz.
- **Karşılananlar:** SMB2 Tree Connect ve NTSTATUS; Kerberos AS-REQ ve `PREAUTH_FAILED`; LDAP bind hatası 49 ve arama kökü. Şifreli olduğu için görünmeyen alanların tanığı (enc-part, SASL) anlatılıyor.
- **Eksikler:** ASAMA2 "mevcut TShark sürümündeki alan listesiyle doğrulama" (`tshark -G fields`) istiyor; derslerde kullanılmıyor. Küçük.
- **Karar:** **Tam** (küçük notla).

## Madde 59 · Packets · Gerçek CLI ile toplama, alan çıkarma ve özet

- **Dersler:** PK28–PK29. DENETIM durumu güncel değil.
- **Denetim:** validate, tahmin ve mutasyon temiz.
- **Karşılananlar:** `tshark -T fields -e -E`; `-z io,phs` protokol hiyerarşisi; `-w` ile yeni kayıt; tcpdump ile gerçek yakalama, snaplen (`-s 64`), `-c`; dosya döndürme (`-C 1 -W 2`).
- **Eksikler:** süre sınırlı döndürme (`-G` / `-b duration`) yok; yalnız boyut eşiği var. Küçük.
- **Karar:** **Tam** (küçük notla).

## Madde 60 · AD · Nesne ACL'lerinden erişim yolu çıkarmak

- **Dersler:** AD13–AD14 (DENETIM'de sahibi Antigravity, durumu "bekliyor").
- **Denetim:** validate, tahmin ve mutasyon temiz (AD13:3'te 9/9, AD14:2'de 1/1).
- **Karşılananlar:** sıralı DACL'den etkin hak hesabı; GenericAll, WriteDacl ve WriteOwner; sahiplik ve devralma; doğrulanmış kenarlarla en kısa yol.
- **Eksikler:**
  - **BloodHound CE hiç kullanılmıyor.** Ders, "gerçek etki alanında AD12 laboratuvarındaki ACL'leri topla, BloodHound CE verisinde yolu aç" diye **öneriyor**, ama hiçbir görev gerçek BloodHound verisini ya da grafiğini okumuyor. Görevler yerel modelde. ASAMA2 "gerçek grafikte sonucu kontrol eden okuma görevleri" istiyor.
  - AD12 laboratuvarından gerçek ACL çıktısı (`nTSecurityDescriptor`) görevlerde yok. Çalışma ağacında başkasının yarım AD VM işi var (`sandbox/ad_vm*`, AD15–AD19, commit'lenmemiş); bu madde onunla kapanabilir, ama şu an kapalı değil.
- **Karar:** **Kısmen.**

---

> Madde 61–64 toplu ölçüm (26 Ekim 2026, anlık görüntü `9fad633`, **boşluklu yol**): AD yolu validate iki ortamda **temiz** (168 kontrol). 9 tahminin hepsi uyuşuyor. Mutasyon: 50 mutantın 49'u yakalandı (geçen 1'i aşağıda, eşdeğer). Codex 26 Ekim'de gerçek VMware DC laboratuvarını ve AD15–AD25 derslerini commit'ledi; madde 60'ın altındaki "commit'lenmemiş" notu artık geçersiz.
>
> **Canlı görevlerin test sağlamlığı güçlü.** `motor=ad-vm` görevleri (AD18:2, AD21:2/4, AD15:2) gerçek DC'de koşuyor ve sabit cevapla geçilemiyor: test gerçek lab durumunu değiştirip (`run_code(degistir(...))`) kararın buna göre değişmesini şart koşuyor. Bu yüzden bu görevlerde mutant üretilememesi zayıflık değil.
>
> **Ortam bulgusu (gerçek, ama kullanıcının kurulumunu etkilemiyor):** `sandbox/ad_ldap_client.py:24` Windows yolunu `wslpath`'e ters bölü işaretleriyle ve tırnaksız geçiriyor. Yol **boşluk içermezse** `wsl.exe` argümanı ters bölüleri siliyor ve AD22/AD23 "Kali WSL yolu çözümlenemedi" ile düşüyor. Kullanıcının gerçek yolu boşluk ve emoji içerdiği için orada çalışıyor; ama taşınabilir değil (boşluksuz bir yola kurulursa kırılır). Codex'in dosyası; düzeltmeyi ona bırakıyorum.

## Madde 61 · AD · Mevcut devir türlerine gerçek S4U/bilet akışı ve doğrulama

- **Dersler:** AD16, AD17, AD18 (`df2bc40`, Codex). Mevcut AD08 tanıtımını gerçek akışa bağlıyor.
- **Denetim:** validate/tahmin temiz. AD17:3 mutasyonu 19/19. AD18:2 gerçek iki Windows Server konuğunda koşuyor; durum değiştirme testiyle korunuyor.
- **Karşılananlar:** yapılandırma bulgusunu başarılı bilet isteğinden ayırmak (AD16); kendi hizmeti ile arka hizmet biletini ilişkilendirmek ve başarısızı ayırmak (AD17); **gerçek KDC/üye sunucu** arasında klasik ve kaynak tabanlı devir ile dosya erişimi, hassas kullanıcı sınırı (AD18). Hesap özellikleri LDAP'a bağlı; yerel KDC taklidi yok. ASAMA2'nin istediği her şey karşılanıyor.
- **Eksikler:** bulmadım. Gerçek lab, gerçek akış, sağlam test.
- **Karar:** **Tam.**

## Madde 62 · AD · AD CS ve sertifika şablonu/izin denetimi

- **Dersler:** AD19, AD20, AD21 (`1cd906d`, Codex).
- **Denetim:** validate/tahmin temiz. AD20:3 mutasyonu 8/8. AD21:4 gerçek CA'da, durum değiştirme testiyle korunuyor. **Küçük test boşluğu:** AD21:2'de `-band 2` → `-band 3` mutantı geçiyor; canlı şablonun ilgili bitinin değeri bu iki maskeyi ayırt ettirmediği için (yalnızca o canlı şablona bağlı, gizli zayıflık).
- **Karşılananlar:** şablonun konu/kimlik doğrulama amacını bit alanlarından okumak (AD19); **enrollment hakkı ile şablon değiştirme hakkını ayırmak** (AD20); gerçek CA şablon öznitelikleri, yayım listesi ve başvuru kararı (AD21). ASAMA2'nin üç koşulu da (konu/amaç, enrollment, değişiklik) karşılanıyor; gerçek CA kullanılıyor.
- **Eksikler:** AD21:2 küçük test boşluğu (yukarıda).
- **Karar:** **Tam** (küçük test notuyla).

## Madde 63 · AD · Gerçek LDAP bağlantısında TLS, imzalama ve channel binding

- **Dersler:** AD22, AD23 (`9832298`, Codex). `motor=ad-client` ile gerçek DC'ye bağlanıyor.
- **Denetim:** validate/tahmin temiz (boşluklu yolda). AD17 benzeri davranış testleri. **Ortam bulgusu yukarıda:** boşluksuz yolda bu iki ders düşüyor.
- **Karşılananlar:** gerçek DC'ye doğrulanmış LDAPS, StartTLS ve imzalı SASL; **sertifika hatasını LDAP filtresiyle karıştırmamak** (bağlantı katmanı filtreden ayrı — ASAMA2'nin özellikle istediği); geçerli/eksik/bozuk channel binding karşılaştırması ve sunucu olayları. `ldapsearch` anılıyor.
- **Eksikler:**
  - ASAMA2 Windows `RSAT/ldp` de diyor; `ldp.exe` GUI aracı, otomatik sınanamaz (Burp durumuyla aynı). Çekirdek davranış gerçek bağlantıda ölçüldüğü için gerçek boşluk değil, not.
  - Taşınabilirlik hatası (yukarıdaki ortam bulgusu).
- **Karar:** **Tam** (ldp notu + taşınabilirlik hatası).

## Madde 64 · AD · GPO/SYSVOL dosyaları ve LAPS özniteliklerini denetlemek

- **Dersler:** AD24, AD25 (`7fa4b29`, Codex). Tümü yerel; ASAMA2 de "statik SYSVOL örnekleri yeterli" diyor.
- **Denetim:** validate/tahmin temiz. Mutasyon: AD24 8/8 ve 6/6, AD25 2/2 ve 2/2. Hepsi yakalandı.
- **Karşılananlar:** `GptTmpl.inf` (UTF-16 güvenlik şablonu), `Groups.xml` (grup değişiklik tercihi) ve `Registry.pol` (ikili başlık sınırı) — üç dosya biçimi de okunuyor; dosya içeriği ile etkili GPO sonucu ayrılıyor (AD24). Legacy ve Windows LAPS alanları, FILETIME sınırı, **gizli değeri rapora dökmeden** erişim kanıtını sınıflamak (AD25). ASAMA2'nin istediği her şey karşılanıyor.
- **Eksikler:** bulmadım.
- **Karar:** **Tam.**
