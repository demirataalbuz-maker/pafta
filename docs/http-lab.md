# HTTP/HTML: gerçek araç laboratuvarı (HT17–HT24)

Bu ek dersler önceki Bilet Masası'nı değiştirmez. HTTP/HTML yolu yine altı
rütbedir; HTML okuma seviyesinde kalır. Aşağıdaki araçlar otomatik indirilmez.

## Gereksinimler

| Deney | Gereken | Bu teslimde ölçülen |
|---|---|---|
| HTTP, Burp hedefi, nesne yetkisi, CSRF, yönlendirme | Python 3.11+ standart kütüphane | Windows Python 3.11 ve Kali Python |
| Burp elle iş akışı | Burp Community veya Professional, kendi tarayıcısı | Kali Burp 2026.8 kurulu; GUI kabulü ayrı kontrol listesidir |
| TLS | curl, Python cryptography | Windows curl Schannel ve cryptography 50.0.1; Kali curl/OpenSSL |
| CORS, SameSite, URL parser | Node, playwright-core, kurulu Edge/Chromium | Kurulu Codex runtime playwright-core + Edge 155.0.4283.62 |
| GraphQL | `.deps` içinde graphql-core 3.3.0 | Kullanıcı onayıyla yalnız bu paket indirildi |
| WebSocket | Python standart kütüphane | Gerçek TCP; açıkça sınırlanmış RFC6455 alt kümesi |

GraphQL kurulumu kullanıcı onayından sonra:

```text
python -m pip install --target .deps --no-deps -r requirements-http.txt
```

TLS için cryptography kurulu değilse durup kurulum gereksinimini çöz. Bu
çalışmada zaten kurulu olan paket kullanıldı; bir CA güven deposuna eklenmedi.
Başka makinede cryptography kurulumu kendi bağımlılıklarını da gerektirebilir.

Tarayıcı yardımcısı öncelikle `PAFTA_HTTP_NODE`, `PAFTA_HTTP_PLAYWRIGHT` (paket
klasörünün tam yolu) ve `PAFTA_HTTP_BROWSER` (exe tam yolu) ayarlarını okur.
Ayarsız durumda PATH'teki Node, repo `.deps/npm/node_modules/playwright-core`,
varsa kurulu Codex runtime ve standart Edge konumları aranır. Codex zorunlu
değildir: bu üç ayarla kendi mevcut kurulumunu seçebilirsin. Eksik araçta
gerçek hata alınır; sahte browser raporu üretilmez. Tarayıcı indirmek gerekmez;
kurulu Edge kullanılır. Yeni makinede Playwright kurulumunu ayrıca onayla:
[resmî kitaplık](https://playwright.dev/docs/library). Global `NODE_PATH`
değiştirilmez. [Playwright executablePath belgesi](https://playwright.dev/docs/api/class-browsertype#browser-type-launch-option-executable-path)
kurulu tarayıcı sürümlerinin uyumluluğunu garanti etmez; teslimde ölçülen Edge
sürümü yukarıda yazılıdır. Headless browser ayrı geçici profille açılır ve kapatılır;
zaman aşımında süreç ağacı sonlandırılır.

## Kalıcı hedef ve Burp kabul listesi

Repo kökünde ayrı terminal:

```text
python sandbox/http_lab.py --port 8769
```

Yalnız 127.0.0.1'e bağlanır. Program URL'yi ve rastgele reset kontrol başlığını
yazdırır. Terminal açık kaldıkça oturumlar/kayıtlar yaşar. `Ctrl+C` kapatır.
`POST /_control/reset` + doğru `X-Lab-Control` bütün oturumları iptal eder ve
ilk kayıtları geri kurar. Kontrol anahtarı kullanıcının login parolası değildir.

Kali Burp kullanılıyorsa hedefi aynı Kali'de başlat. Örneğin repo `sandbox`
klasöründeki `http_lab.py` dosyasını Linux'ta `/tmp/pafta-http/http_lab.py`
konumuna kopyalayıp orada çalıştır. İlk Burp deneyi tek dosyayla çalışır.
WebSocket/GraphQL uç noktalarını da kullanacaksan ilgili `http_*_lab.py`
modüllerini yanına kopyala; GraphQL için aynı Linux Python'unda gerçek motorun
kurulu olması gerekir. Bu teslim Windows `.deps` kurulumunu kullanır; WSL'ye
ek GraphQL paketi kurulmadı. Windows sunucusunun WSL loopback'inden erişimini
varsayma; ağ arayüzlerine geniş bind yapma.

HT17'deki adımlarla aşağıdakileri Burp UI'da elle kaydet:

- Burp browser'dan ayse ile giriş; History'de POST /session ve Cookie'li GET /items/1.
- Repeater'da değişikliksiz tekrar → 200 ve aynı kayıt.
- Yalnız hedef id 1→2 → 403; eski hedefe dön → 200.
- Ayrı deneyde Cookie kaldır → 401.
- Reset'ten sonra eski Cookie → 401; tekrar girişten sonra → 200.
- Rapor: yöntem/hedef/yanıt ve maskelenmiş oturum; canlı tokenları paylaşma.

Otomatik testler gerçek HTTP/TCP'yi ölçer, **Burp'un History/Repeater GUI
tıklamalarının yapıldığını kanıtlamaz**. Teslim raporunda bu ayrım korunur.

## TLS'yi elle tekrar

```text
python sandbox/http_lab.py --tls --port 8770
```

Yazdırılan CA dosyasını yalnız bu çağrıda kullan:

```text
curl.exe --noproxy "*" --cacert CA_DOSYASI --resolve app.pafta.test:8770:127.0.0.1 https://app.pafta.test:8770/
```

Windows Schannel geçici CA'nın CRL hizmetini bulamazsa yalnız bu deneme için
[`--ssl-no-revoke`](https://curl.se/docs/manpage.html#--ssl-no-revoke) ekle;
bu seçenek revocation kontrolünü kapatır, sertifika imzası/hostname doğrulaması kalır. CA'yı
çıkarmak güven hatası, URL/resolve adını `other.pafta.test` yapmak hostname
hatası üretir. `--insecure` kullanma. `/missing` 404'tür; normal curl çıkış 0,
`--fail-with-body` ile çıkış 22. TLS hatası HTTP durum kodu değildir.

## Tarayıcı ağını elle inceleme

`cors_report()` ayrı origin sunucularını, `samesite_report()` farklı siteleri
kurup gerçek tarayıcıya navigasyon/fetch yaptırır. Otomatik çıktı browser
sürümünü de içerir; test sürüme göre sonucu uydurmaz. DevTools Network'te
aynı vakaları incelemek için iki ayrı terminalde kalıcı hedef başlat:

```text
python sandbox/http_lab.py --port 8769
python sandbox/http_lab.py --port 8771 --allow-origin http://127.0.0.1:8769
```

İlk adreste DevTools Console'dan `fetch('http://127.0.0.1:8771/cors')` ve
`fetch('http://127.0.0.1:8771/cors',{method:'POST',headers:{'X-Pafta':'yes'},body:'{}'})`
çalıştır; Network'te OPTIONS/POST'u incele. 8771'yi izinli origin olmadan
yeniden başlatıp aynı deneyi tekrarla: OPTIONS reddinde POST yok, basit GET'te
GET var ama JS okuması reddedilir. `--cors-wildcard` ile ayrı hedef açıp
`credentials:'include'` eklemek wildcard/credential reddini üretir.
CORS için port farkı yeterli;
SameSite için `app.pafta.test` ve `evil.other.test` gerekir. Resolver yalnız
tarayıcı sürecinde bu isimleri loopback'e eşler, hosts dosyasını değiştirmez.
Global web güvenliği kapatılmaz. HTTP Lax/Strict navigasyonları sınanır;
Secure/None ve üçüncü taraf cookie politikalarının tamamı kapsanmaz.

## Diğer sınırlar

- SSRF: iki geçici loopback portu dış/iç rolünü simüle eder; telde gerçek
  HTTP vardır. Taşıma başka hiçbir hedefe çıkamaz. Üretim DNS/IP denetleyicisi
  veya bulut metadata deneyi değildir. 301/302 POST→GET seçilmiş istemci
  politikasıdır; 307 POST/gövdeyi korur. Her hedef bağlantıdan önce doğrulanır.
- WebSocket: gerçek 101 + maskeleme + tek FIN UTF-8 text (en çok 125 bayt).
  Desteklenmeyen çerçeveler açık close koduyla reddedilir. Üretim WS sunucusu
  değildir; compression/fragmentation/binary/ping-pong yoktur.
- GraphQL: gerçek parser/validator/executor, değişken/alias/fragment/şema.
  Public alan ve owner-only secret/rename politikası uygulamanındır, GraphQL
  dilinin kendisi bu izinleri sağlamaz. HTTP 200'de errors/kısmi veri korunur.
  Subscription/batching ve üretim yük denetimleri eklenmedi.

## Kontroller

```text
python -X utf8 tools/test_http_advanced.py
python -X utf8 tools/test_http_kali.py
python -X utf8 tools/validate.py --yol http
```

Testler gerçek yanıtlar, durum değişimi, olay sırası, 0/1/80/81 ve 125/126 bayt
sınırları, yanlış oturum/Origin, native GraphQL validation ve bozulmuş öğrenci
çözümlerini ölçer. Tahminlerin cevapları tam stdout ile ayrıca karşılaştırılır.
Kali testi isteğe bağlıdır: ayarlı WSL dağıtımındaki mevcut Python/cryptography/curl
ile dosyaları Linux `/tmp` altında çalıştırır; paket kurmaz.
