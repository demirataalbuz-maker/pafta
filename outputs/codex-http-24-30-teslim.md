# HTTP/HTML 24–27, 29–30 — Codex teslimi

Tarih: 2026-10-25. 28 (HT16 JWT/OAuth) korunmuştur. HTTP yolu 6 rütbe,
sıralı HT01–HT24; bu teslim 8 ders, 14 görev ve 8 gerçek tahmin ekler.
HTML okuma seviyesindedir. Push yapılmadı. Denetçinin Excel/DENETIM.md
dosyaları değiştirilmedi.

| Pano | Teslim | Ana commit |
|---|---|---|
| 24 | HT17; kalıcı/resetlenebilir loopback hedef, Burp History→Repeater elle akışı, tek hedef değişikliği, aynı oturumla tekrar | a18fda3 |
| 25 | HT18; gerçek curl/TLS, çağrıya özel CA, yanlış CA/hostname, HTTP hata ayrımı | 943e502 |
| 26 | HT19–HT20; gerçek Edge CORS/preflight, farklı site SameSite navigasyonu, oturuma bağlı CSRF | 029ad94 |
| 27 | HT21; iki hesap ve oturumsuz okuma/yazma matrisi, yanıt+durum+olay kanıtı | dd73bae |
| 29 | HT22; gerçek yerel redirect zinciri, her hedefe bağlantıdan önce kontrol, 301/302 ve 307 yöntemi/gövdesi | 4f6ad7d |
| 30 | HT23–HT24; gerçek TCP WebSocket mesajı, gerçek graphql-core query/mutation/introspection, alan yetkisi | 62639c8 |

Ortak entegrasyon ve regresyon: 8f04f43. Linux /tmp kabul betiği: 3bb1259.
GraphQL alias/fragment/introspection okuma örnekleri: 9f54804.
Pafta sunucusuyla port çakışmasını önleyen CLI varsayılanı: a9ceb1f;
Windows CLI kapanışı ve doğrulanmış resmî araç bağlantıları: e86caa0.
`engine/runners.py` yalnız HttpRunner'ın sandbox/.deps import yolları için
değişti; aynı dosyadaki başka ajanın PowerShell satırları `git add -p` ile
dışarıda bırakıldı. Sonraki commit'ler açık dosya listeleriyle oluşturuldu.

## Ölçülen sonuçlar

- Windows HTTP validate: **24 ders, 175 kontrol, temiz**.
- Git Bash HTTP validate: **24 ders, 175 kontrol, temiz**.
- `tools/test_http_advanced.py`: bütün görev çözümleri geçer, başlangıçları
  fail verir; 8 tahminin tam stdout'u cevapla uyuşur; **52 davranış mutasyonu
  fail verir**. İlk denemede GET'e dönen POST'un gövdesi için tanık eksikliği
  bulundu, HT22 testine gerçek wire çağrılarının yöntemi/gövdesi eklendi.
  Yeniden çalıştırma temizdir.
- Gerçek tarayıcı WebSocket istemcisi UTF-8 mesajı alır ve 1000 close görür.
  Maskesiz/RSV, binary/parçalı, extended-length ve bozuk UTF-8 çerçeveleri
  ayrı close kodlarıyla reddedilir.
- Bağımsız CLI hedefi farklı istemciler arasında oturumu korur; yanlış reset
  anahtarı reddedilir; doğru reset eski oturumu iptal eder; kapanınca port kapanır.
- GraphQL alias/fragment ile alan yetkisi, introspection, hatalı sorgu/tür/alan,
  başlık 0/1/80/81 ve başarısız yazmada durumun korunması gerçek motorda ölçüldü.
- Kali WSL: kaynaklar **Linux /tmp** altına taşınıp mevcut Python/cryptography/
  curl ile çalıştırıldı. HTTP 200/403; TLS doğru ad 0/200, bilinmeyen CA ve
  yanlış ad 60/0, fail-with-body 22/404. stderr temiz. Dağıtım adı mevcut
  ayardan okunur; yeni paket kurulmaz.
- Genel Windows/Git Bash validate sonuçları aşağıdaki son kabul bölümündedir.

Loglar bu klasörde `http-advanced-tests.log`, `http-native-tests.log`,
`http-kali-native.log`, `http-validate-windows.log`, `http-validate-gitbash.log`,
`http-full-validate-windows.log`, `http-full-validate-gitbash.log`, `http-cli-test.log`.

`docs/DURUM.html` içindeki üretilmiş veri ayrıca okundu: 24/25/26/27/29/30
`denetime-hazir`, 28 `bitti`. Denetçi onayı yerine yeşil/bitti verilmedi.

## Kurulum ve gerçek araç sınırları

Kullanıcı onayıyla yalnız **graphql-core==3.3.0**, `.deps` içine indirildi;
`requirements-http.txt` sabitler. cryptography 50.0.1, Windows curl.exe,
Kali curl/OpenSSL ve Burp 2026.8 önceden kuruluydu. Tarayıcı için mevcut Node,
Codex runtime'daki playwright-core ve kurulu Edge **155.0.4283.62** kullanıldı;
browser veya yeni Playwright paketi indirilmedi. Başka makinede araç yolları
`PAFTA_HTTP_NODE`, `PAFTA_HTTP_PLAYWRIGHT`, `PAFTA_HTTP_BROWSER` ile seçilebilir.
Codex'e zorunlu bağımlılık yoktur. Tam tarif: `docs/http-lab.md` ve README.

Burp'un GUI'sindeki History/Repeater tıklamalarını otomasyonla yaptığımı
iddia etmiyorum. Kurulu Burp için gerçek kalıcı hedef ve ayrıntılı elle kabul
listesi teslim edildi; otomatik testler HTTP davranışını ve sürekliliği ölçer.
**Burp GUI kabul listesi bağımsız denetimde elle uygulanmalıdır.**

TLS özel CA'sı yalnız çağrıya verilir; sistem güven deposu değişmez.
Schannel'ın bu geçici CA için CRL kontrolü çağrıya özel kapatılır; imza ve
hostname doğrulaması korunur. CORS/global browser güvenliği kapatılmaz.
SameSite deneyi farklı sitelerde explicit Lax/Strict içindir; Secure/None ve
üçüncü taraf cookie politikalarının tamamını kapsamaz.

SSRF taşıması yalnız iki kendi oluşturduğu geçici loopback portuna çıkabilir;
public/internal etiketleri laboratuvar rolüdür. Gerçek LAN/metadata hedefi yok.
DNS rebinding/IP üretim politikası kapsam dışıdır. WebSocket açıkça belgelenmiş
tek kısa text mesajı alt kümesidir; üretim protokol kitaplığı değildir.
GraphQL parser/validation/execution gerçektir; uygulama yetkisi resolver'lardadır.
Subscription/batching ve üretim yük bütçeleri bu derslerin dışında kalır.

## Son kabul

İki genel koşu da tamamlandı. Koşuların kütüphane görüntüsü **481 ders,
3977 kontrol** içeriyordu. Sonuçlar bütün uygulama için temiz değildir:

| Ortam | Geçen | Başarısız | HTTP başarısız |
|---|---:|---:|---:|
| Windows | 3974 | 3 | 0 |
| Git Bash | 3973 | 4 | 0 |

İki ortamda ortak bulgular: `powershell/ps22:6` (gerçek ACL raporu),
`powershell/ps25:3` (imza envanteri), `powershell/ps25:4` (güven kararı).
Git Bash'te ayrıca `spl/sp22:1` gerçek Splunk aramasında **404 Unknown sid**
verdi. Bunların nedeni için kesin bir çıkarım yapmadım; bu teslimde bu
dersler veya motorları değiştirilmedi. Tam hata metinleri genel koşu
loglarındadır. Başka ajanların ortak dosyalardaki eşzamanlı çalışmaları
yerinde bırakıldı; koşuların bütün deponun nihai denetiminin yerine geçtiği
iddia edilmez.

HTTP'ye özel Windows ve Git Bash koşuları **24 ders / 175 kontrol temiz**;
gerçek araç ve 52 mutasyon denetimi de temizdir. Kodda yarım bırakılan HTTP
maddesi yoktur. Burp GUI'nin elle kabulü ve bağımsız denetçinin bitti kararı
beklenir. Bütün kendi kaynak/ders/pano değişiklikleri commit'lidir; push yok.
