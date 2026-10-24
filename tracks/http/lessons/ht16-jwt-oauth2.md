---
id: ht16
title: JWT Yapısı, İmza Tuzakları ve OAuth 2.0 / PKCE Akışı
summary: RFC 7519 JWT (Header.Payload.Signature) ve base64url kodlaması, exp/nbf/iss/aud claim denetimi, RFC 8725 imza doğrulama tuzakları (alg:none, RS256→HS256 anahtar karışıklığı, kid), RFC 9700 ve RFC 7636 ile OAuth 2.0 Authorization Code + PKCE (S256), state ve tam eşleşmeli redirect_uri güvenliği.
---

::: anlat JWT'nin üç parçası ve base64url
HT08'de sunucunun bellekte tuttuğu oturum kimliğini çerezle taşıdık; HT09'da ise `Authorization: Bearer <jeton>` başlığını gördük. Modern API'lerde ve tek oturum açma (**SSO**) sistemlerinde bu taşıyıcı jeton çoğu zaman **JWT** (*JSON Web Token*, [RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519)) biçimindedir: sunucu oturumu bir tabloda aramak yerine, kullanıcının kimliğini ve yetkilerini **kriptografik olarak imzalanmış** bir JSON nesnesinin içinden okur.

İmzalı bir JWT (**JWS Compact Serialization**, RFC 7515), nokta (`.`) ile ayrılmış **üç base64url** parçasından oluşur:

```text
eyJhbGciOiJIUzI1NiIsImtpZCI6ImFuYWh0YXItMjAyNiIsInR5cCI6IkpXVCJ9
.
eyJpc3MiOiJodHRwczovL2lkcC5wYWZ0YS50ZXN0Iiwic3ViIjoiYW5hbGlzdCIsImF1ZCI6InBhZnRhLWFwaSIsImV4cCI6MTkwMDAwMDAwMH0
.
4W0m1tG_rE5vL6pX9bK7yQ2nC8sD3fH1jA0zV4uN6mY
```

| Parça | İçeriği | Görevi |
|---|---|---|
| **1. JOSE Header** | `{"alg": "HS256", "kid": "anahtar-2026", "typ": "JWT"}` | Hangi algoritma (`alg`) ve hangi anahtar kimliği (`kid`) ile imzalandığını bildirir |
| **2. JWT Claims Set (Payload)** | `{"iss": "...", "sub": "analist", "aud": "pafta-api", "exp": 1900000000}` | Taşınan iddialar (*claims*): jetonu kimin verdiği, kime ait olduğu, hangi hedef için geçerli olduğu ve ne zaman biteceği |
| **3. JWS Signature** | `HMAC-SHA256(base64url(Header) + "." + base64url(Payload), gizli_anahtar)` | İlk iki parçanın tel üzerinde bir bit bile değiştirilmediğini ve anahtara sahip tarafça üretildiğini kanıtlar |

**Base64url (RFC 7515 Bölüm 2):** Standart base64'teki `+` ve `/` karakterleri URL ve HTTP başlıklarında sorun çıkardığı için **base64url** alfabesinde bunların yerini `-` ve `_` alır; sondaki `=` dolgu (*padding*) karakterleri ise **atılır**. Python'un `base64.urlsafe_b64decode` fonksiyonu dolgu karakteri bekliyor olduğundan, çözmeden önce `b64 + "=" * (-len(b64) % 4)` ile dolguyu tamamlarsın.

**Standart (*Registered*) Claim Alanları (RFC 7519 Bölüm 4.1):**

| Claim | Adı | Doğrulama Kuralı (RFC 7519) |
|---|---|---|
| `iss` | *Issuer* | Jetonu üreten kimlik sunucusu (büyük-küçük harfe duyarlı metin/URI) |
| `sub` | *Subject* | Jetonun temsil ettiği kullanıcı ya da istemci |
| `aud` | *Audience* | Jetonun **hangi alıcı (hedef servis)** için üretildiği. Tek bir metin ya da metin listesi olabilir; alıcı kendi adını `aud` içinde görmüyorsa jetonu **reddetmelidir** |
| `exp` | *Expiration Time* | UTC Epoch saniyesi (`NumericDate`). Geçerli zaman `exp` değerinden **kesin küçük** (`simdi < exp`) olmalıdır; `simdi >= exp` anında ve sonrasında jeton geçersizdir |
| `nbf` | *Not Before* | Jetonun geçerli olmaya başlayacağı Epoch saniyesi. Geçerli zaman `nbf` değerine **eşit veya büyük** (`simdi >= nbf`) olmalıdır |
| `iat` / `jti` | *Issued At* / *JWT ID* | Üretim zamanı ve tekrar oynatmayı (*replay*) önlemek için kullanılan benzersiz jeton kimliği |

```python
import base64, hashlib, hmac, json

def b64url_kodla(veri):
    return base64.urlsafe_b64encode(veri).rstrip(b"=").decode("ascii")

def b64url_coz(metin):
    return base64.urlsafe_b64decode(metin + "=" * (-len(metin) % 4))

baslik = b64url_kodla(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
yuk = b64url_kodla(json.dumps({"sub": "analist", "rol": "mavi"}, separators=(",", ":")).encode())
girdi = f"{baslik}.{yuk}".encode("ascii")
imza = b64url_kodla(hmac.new(b"pafta-gizli-anahtar", girdi, hashlib.sha256).digest())

jeton = f"{baslik}.{yuk}.{imza}"
print("Jeton:", jeton[:42] + "...")
print("Çözülen yük:", json.loads(b64url_coz(jeton.split(".")[1])))
```
:::

::: anlat İmza doğrulama tuzakları (RFC 8725 JWT BCP)
JWT'nin birinci ve ikinci parçası **şifreli değildir**; yalnızca base64url ile kodlanmıştır ve herkes tarafından okunabilir. Güvenliği sağlayan tek şey **üçüncü parçadaki imzanın doğru anahtar ve doğru algoritmayla doğrulanmasıdır**. [RFC 8725](https://datatracker.ietf.org/doc/html/rfc8725) (*JSON Web Token Best Current Practices*), gerçek dünyada en sık görülen JWT zafiyetlerini ve savunma kurallarını listeler:

1. **`alg: "none"` (İmzasız Jeton) Tuzağı (RFC 8725 Bölüm 2.1 ve 3.1):**
   RFC 7519 Bölüm 6, başlığında `{"alg": "none"}` yazan ve imza parçası boş olan (`header.payload.`) "korumasız" JWT'leri tanımlar. Saldırgan bir jetonun `Payload` kısmındaki `"rol": "kullanici"` alanını `"rol": "yonetici"` yapıp başlıktaki `alg` değerini `"none"` olarak değiştirir ve imzayı siler. Doğrulayıcı `alg` alanına körü körüne güveniyorsa imzayı hiç kontrol etmeden jetonu kabul eder!
2. **Algoritma Karışıklığı: `RS256` → `HS256` (RFC 8725 Bölüm 2.1 ve 3.1, CVE-2015-9235):**
   Asimetrik `RS256` (RSA) algoritmasında sunucu jetonu **özel anahtarıyla** (*private key*) imzalar, herkesin erişebildiği **açık anahtarla** (*public key*) doğrular. Simetrik `HS256` (HMAC) algoritmasında ise imzalama ve doğrulama aynı gizli anahtarı kullanır. Saldırgan başlıktaki `"alg": "RS256"` değerini `"HS256"` yapıp jetonu sunucunun herkese açık RSA *public key* metniyle HMAC-SHA256 olarak imzalarsa, anahtarın algoritmasını kontrol etmeyen hatalı bir doğrulayıcı RSA açık anahtarını HMAC sırrı sanarak sahte imzayı onaylar!
3. **Zayıf Simetrik Anahtarlar (RFC 8725 Bölüm 2.2 ve 3.5):**
   `HS256` gibi MAC algoritmalarında insan tarafından hatırlanabilir kısa bir parola kullanılırsa, saldırgan tek bir JWT yakaladığında internet bağlantısı bile olmadan çevrimdışı (*offline*) sözlük/kaba kuvvet saldırısıyla gizli anahtarı kırabilir.
4. **Güvenilmeyen Başlık Alanları: `kid`, `jku`, `x5u` (RFC 8725 Bölüm 2.9 ve 3.10):**
   `kid` (*Key ID*) anahtar tablosunda arama yapmak için kullanılır; doğrulanmadan bir dosya yoluna (`../../dev/null`) veya SQL/LDAP sorgusuna sokulursa enjeksiyon açığı doğurur. `jku` (*JWK Set URL*) ve `x5u` başlıklarının doğrulanmadan takip edilmesi ise sunucunun saldırganın adresine istek atmasına (**SSRF**) ve saldırganın kendi açık anahtarını sunmasına yol açar.
5. **Hedef (`aud`) ve Tür (`typ`) Karışıklığı (RFC 8725 Bölüm 2.7, 2.8, 3.9, 3.11):**
   Aynı kimlik sunucusu (IdP) birden fazla mikroservise jeton üretiyorsa, `A` servisi için alınan geçerli bir jetonun `B` servisinde kullanılmasını (*Substitution Attack*) yalnızca **`aud` (Audience)** ve **`typ`** denetimi engeller.

> [!GÜVENLİK]
> **RFC 8725 Doğrulama Kontrol Listesi:**
> - Başlıktaki `alg` değerini her zaman sunucunun izin verdiği algoritmalar beyaz listesiyle karşılaştır; `"none"` değerini reddet.
> - Her anahtarı **yalnızca kendi algoritmasıyla** eşleştir (`anahtarlar[kid] -> ("HS256", sir)`): bir RSA açık anahtarının `HS256` ile kullanılmasına asla izin verme.
> - İmzayı hesaplarken JSON'u yeniden üretme; telden gelen ham `base64url(Header) + "." + base64url(Payload)` baytlarını ve sabit zamanlı `hmac.compare_digest` karşılaştırmasını kullan.
> - İmza geçerli olsa bile `iss`, `aud`, `exp` (`simdi < exp`) ve varsa `nbf` (`simdi >= nbf`) iddialarını eksiksiz doğrula.
:::

::: anlat OAuth 2.0 yönlendirme akışı, state ve PKCE (RFC 9700 ve RFC 7636)
Bir kullanıcının üçüncü taraf bir uygulamaya parolasını vermeden kimlik sunucusu (**IdP** / *Authorization Server*) üzerinden giriş yapmasını **OAuth 2.0** ve onun kimlik katmanı olan **OpenID Connect (OIDC)** sağlar. [RFC 9700](https://datatracker.ietf.org/doc/html/rfc9700) (*OAuth 2.0 Security Best Current Practice*), jetonu doğrudan URL'de döndüren eski *Implicit Grant* (`response_type=token`) akışını yasaklar ve yerine **PKCE destekli Authorization Code** (`response_type=code`) akışını şart koşar:

1. **İstemci PKCE Çiftini ve `state` Değerini Üretir ([RFC 7636](https://datatracker.ietf.org/doc/html/rfc7636) Bölüm 4.1–4.2):**
   - `state`: Tarayıcı oturumuna bağlanan tek kullanımlık rastgele değerdir; dönüş adresine (`callback`) yapılacak **CSRF** saldırılarını önler.
   - `code_verifier`: `[A-Za-z0-9\-._~]` karakterlerinden oluşan, **en az 43, en fazla 128 karakter** uzunluğunda yüksek entropili rastgele gizli metindir.
   - `code_challenge`: `S256` yöntemiyle `BASE64URL(SHA256(ASCII(code_verifier)))` olarak hesaplanır (RFC 9700 Bölüm 2.1.1'e göre `plain` yöntemi doğrulayıcıyı ağda açık ettiği için `S256` kullanılmalıdır).
2. **Yetkilendirme İsteği (`GET /oauth/authorize`):**
   İstemci tarayıcıyı `client_id`, `redirect_uri`, `response_type=code`, `state`, `code_challenge` ve `code_challenge_method=S256` parametreleriyle IdP'ye yönlendirir.
   - **Kritik Kural (RFC 9700 Bölüm 2.1 ve RFC 6749 Bölüm 4.1.2.1):** IdP, gelen `redirect_uri` değerini önceden kayıtlı adresle **birebir tam metin eşleşmesiyle** (*exact string matching*) karşılaştırmalıdır. `client_id` veya `redirect_uri` eşleşmiyorsa IdP kullanıcıyı o adrese **asla yönlendirmemeli** (`302` dönmemeli), doğrudan `400 Bad Request` hatası göstermelidir; aksi hâlde açık yönlendirme (*open redirect*) ve yetki kodu sızıntısı oluşur.
3. **Yetki Kodu Dönüşü (`302 Found` → `redirect_uri?code=...&state=...`):**
   Kullanıcı onay verdiğinde IdP tek kullanımlık `code` değerini `code_challenge` ile ilişkilendirip kaydeder ve tarayıcıyı `Location: https://uygulama.pafta.test/callback?code=kod-901&state=...` adresine yönlendirir. İstemci önce gelen `state` değerinin kendi gönderdiği `state` ile aynı olduğunu doğrular.
4. **Arka Kanaldan Jeton Takası (`POST /oauth/token`):**
   İstemci `code`, `redirect_uri`, `client_id` ve başlangıçta sakladığı `code_verifier` değerini IdP'ye gönderir. IdP `BASE64URL(SHA256(ASCII(code_verifier))) == code_challenge` eşitliğini doğrular; eşleşmezse `400 Bad Request` ve `{"error": "invalid_grant"}` döner (RFC 7636 Bölüm 4.6). Eşleşirse imzalı JWT erişim jetonunu döndürür.

```python
import base64, hashlib, json
from urllib.parse import parse_qs, urlencode, urlsplit
import tezgah

verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"  # 43 karakter (RFC 7636 Ek B örneği)
challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest()).rstrip(b"=").decode("ascii")
print("PKCE S256 challenge:", challenge)

sorgu = urlencode({
    "client_id": "pafta-web",
    "redirect_uri": "https://uygulama.pafta.test/callback",
    "response_type": "code",
    "state": "st-42",
    "code_challenge": challenge,
    "code_challenge_method": "S256",
})
y1 = tezgah.yanit(f"GET /oauth/authorize?{sorgu} HTTP/1.1\r\nHost: idp.pafta.test\r\n\r\n")
konum = y1.baslik("Location")
kod = parse_qs(urlsplit(konum).query)["code"][0]
print("Authorize:", y1.durum, "code=", kod)

govde = json.dumps({
    "grant_type": "authorization_code",
    "client_id": "pafta-web",
    "redirect_uri": "https://uygulama.pafta.test/callback",
    "code": kod,
    "code_verifier": verifier,
})
y2 = tezgah.yanit(
    f"POST /oauth/token HTTP/1.1\r\nHost: idp.pafta.test\r\n"
    f"Content-Type: application/json\r\nContent-Length: {len(govde)}\r\n\r\n{govde}"
)
jeton = y2.json()["access_token"]
y3 = tezgah.yanit(f"GET /api/kasa HTTP/1.1\r\nHost: api.pafta.test\r\nAuthorization: Bearer {jeton}\r\n\r\n")
print("Kasa:", y3.durum, y3.json())
```
```setup
import base64, hashlib, hmac, json
import tezgah

_G = tezgah.Yanit.__init__.__globals__
_Isleyici = _G["Isleyici"]
_ROTALAR = _G["ROTALAR"]
_SIR = b"pafta-cok-gizli-hmac-anahtari-32b"
_KAYITLI_URI = "https://uygulama.pafta.test/callback"
_KODLAR = {}

def _b64u_e(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")

def _b64u_d(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))

def _jwt_uret(yuk, kid="anahtar-2026"):
    h = _b64u_e(json.dumps({"alg": "HS256", "kid": kid, "typ": "JWT"}, separators=(",", ":")).encode())
    p = _b64u_e(json.dumps(yuk, separators=(",", ":")).encode())
    imza = _b64u_e(hmac.new(_SIR, f"{h}.{p}".encode("ascii"), hashlib.sha256).digest())
    return f"{h}.{p}.{imza}"

def r_oauth_authorize(self):
    cid = self.sorgu.get("client_id", "")
    ruri = self.sorgu.get("redirect_uri", "")
    if cid != "pafta-web" or ruri != _KAYITLI_URI:
        return self._yanit(400, {"error": "invalid_redirect_uri"})
    st = self.sorgu.get("state", "")
    rt = self.sorgu.get("response_type", "")
    cc = self.sorgu.get("code_challenge", "")
    ccm = self.sorgu.get("code_challenge_method", "")
    if rt != "code" or not st or not cc or ccm != "S256":
        return self._yonlendir(302, f"{ruri}?error=invalid_request&state={st}")
    kod = "kod-901"
    _KODLAR[kod] = {"client_id": cid, "redirect_uri": ruri, "challenge": cc, "kullanildi": False}
    return self._yonlendir(302, f"{ruri}?code={kod}&state={st}")

def r_oauth_token(self):
    ham, _ = self._govde_oku()
    if ham is None:
        return
    try:
        v = json.loads(ham.decode("utf-8"))
    except Exception:
        return self._yanit(400, {"error": "invalid_request"})
    kod = v.get("code", "")
    kayit = _KODLAR.get(kod)
    verifier = v.get("code_verifier", "")
    if (not kayit or kayit["kullanildi"]
            or v.get("client_id") != kayit["client_id"]
            or v.get("redirect_uri") != kayit["redirect_uri"]
            or not isinstance(verifier, str) or not (43 <= len(verifier) <= 128)):
        return self._yanit(400, {"error": "invalid_grant"})
    hesaplanan = _b64u_e(hashlib.sha256(verifier.encode("ascii")).digest())
    if not hmac.compare_digest(hesaplanan, kayit["challenge"]):
        return self._yanit(400, {"error": "invalid_grant"})
    kayit["kullanildi"] = True
    jeton = _jwt_uret({
        "iss": "https://idp.pafta.test",
        "sub": "analist",
        "aud": "pafta-api",
        "nbf": 1700000000,
        "exp": 1900000000,
        "rol": "denetci",
    })
    return self._yanit(200, {"access_token": jeton, "token_type": "Bearer"})

def r_api_kasa(self):
    yetki = self.headers.get("Authorization", "")
    sema, _, jeton = yetki.partition(" ")
    if sema.lower() != "bearer" or not jeton:
        return self._yanit(401, {"hata": "jeton gerekli"}, [("WWW-Authenticate", "Bearer")])
    parcalar = jeton.split(".")
    if len(parcalar) != 3:
        return self._yanit(401, {"hata": "bicim"}, [("WWW-Authenticate", 'Bearer error="invalid_token"')])
    try:
        bas = json.loads(_b64u_d(parcalar[0]).decode("utf-8"))
        yuk = json.loads(_b64u_d(parcalar[1]).decode("utf-8"))
    except Exception:
        return self._yanit(401, {"hata": "cozulemedi"}, [("WWW-Authenticate", 'Bearer error="invalid_token"')])
    beklenen_imza = _b64u_e(hmac.new(_SIR, f"{parcalar[0]}.{parcalar[1]}".encode("ascii"), hashlib.sha256).digest())
    simdi = 1800000000
    if (bas.get("alg") != "HS256" or bas.get("kid") != "anahtar-2026"
            or not hmac.compare_digest(parcalar[2], beklenen_imza)
            or yuk.get("iss") != "https://idp.pafta.test"
            or yuk.get("aud") != "pafta-api"
            or not (yuk.get("nbf", 0) <= simdi < yuk.get("exp", 0))):
        return self._yanit(401, {"hata": "gecersiz"}, [("WWW-Authenticate", 'Bearer error="invalid_token"')])
    return self._yanit(200, {"kasa": "acik", "sub": yuk["sub"], "rol": yuk.get("rol")})

_Isleyici.r_oauth_authorize = r_oauth_authorize
_Isleyici.r_oauth_token = r_oauth_token
_Isleyici.r_api_kasa = r_api_kasa
if not any(isim == "oauth_authorize" for _, _, isim in _ROTALAR):
    _ROTALAR.extend([
        (r"/oauth/authorize", ("GET",), "oauth_authorize"),
        (r"/oauth/token", ("POST",), "oauth_token"),
        (r"/api/kasa", ("GET",), "api_kasa"),
    ])
```
:::

::: tahmin
Saldırganın değiştirdiği iki jetonu ve bir yönlendirme isteğini sına. Üç satır:

```python
import base64, hashlib, json

verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
ozet = hashlib.sha256(verifier.encode("ascii")).digest()
print(len(verifier), base64.urlsafe_b64encode(ozet).rstrip(b"=").decode("ascii")[:12])

for simdi in (1799, 1800, 1801):
    exp = 1800
    print(simdi, "gecerli" if simdi < exp else "dolmus")
```

???

Dört satır yazar:
- `43 E9Melhoa2Owv`
- `1799 gecerli`
- `1800 dolmus`
- `1801 dolmus`

RFC 7636 Ek B'deki 32 baytlık rastgele dizinin base64url karşılığı tam `43` karakterdir (asgari PKCE sınırı) ve SHA-256 özetinin base64url başlangıcı `E9Melhoa2Owv` olur. RFC 7519 Bölüm 4.1.4'e göre `exp` zamanı **ve sonrasında** (`simdi >= exp`) jeton kabul edilmez: `1799` geçerlidir, tam `1800`'de ve `1801`'de süresi dolmuştur.
:::

::: gorev 1 · Katı JWT doğrulayıcı (RFC 7519 ve RFC 8725)
`jwt_dogrula(jeton, anahtarlar, beklenen_iss, beklenen_aud, simdi)` fonksiyonunu yaz.

`anahtarlar` sözlüğü `{"kid": (algoritma_adi, gizli_baytlar)}` biçimindedir (ör. `{"k1": ("HS256", b"sir...")}`). Kontrolleri şu sırayla uygula:

1. **Biçim ve JSON (`"bicim_hatasi"`):** `jeton` bir `str` olmalı ve `.` ile ayrılmış **tam 3 boş olmayan** parçadan (`bas_b64`, `yuk_b64`, `imza_b64`) oluşmalıdır. Her parça yalnızca base64url karakterlerinden (`[A-Za-z0-9_-]`, `=` dolgusu olmadan) oluşmalı ve geçerli base64url olarak çözülebilmelidir. İlk iki parça UTF-8 JSON nesnesine (`dict`) çözülebilmelidir.
2. **Algoritma beyaz listesi (`"alg_hatasi"`):** Başlıktaki `alg` alanı yalnızca `"HS256"` olmalıdır (`"none"`, `"RS256"` vb. reddedilir).
3. **Anahtar kimliği ve algoritma bağlama (`"anahtar_hatasi"`):** Başlıktaki `kid` alanı bir `str` olmalı, `anahtarlar` sözlüğünde bulunmalı ve o anahtarın kayıtlı algoritması (`anahtarlar[kid][0]`) `"HS256"` olmalıdır (böylece `RS256` açık anahtarının `HS256` sırrı olarak kullanılması engellenir).
4. **İmza doğrulama (`"imza_hatasi"`):** `f"{bas_b64}.{yuk_b64}".encode("ascii")` verisinin `anahtarlar[kid][1]` ile hesaplanan HMAC-SHA256 imzası (base64url, dolgusuz), `imza_b64` ile `hmac.compare_digest` kullanılarak karşılaştırılmalıdır.
5. **Üretici (`"iss_hatasi"`):** Yükteki `iss` alanı `beklenen_iss` ile birebir aynı olmalıdır.
6. **Hedef kitle (`"aud_hatasi"`):** Yükteki `aud` alanı bir `str` ise `beklenen_aud`'a eşit olmalı; bir `list` ise içindeki **boş olmayan `str`** öğelerden biri `beklenen_aud` olmalıdır (diğer türler veya eşleşmeme durumunda reddedilir).
7. **Süre sonu (`"suresi_dolmus"`):** Yükteki `exp` alanı bir sayı (`int` veya `float`, ama `bool` **değil**) olmalı ve `simdi < exp` koşulunu sağlamalıdır (`simdi >= exp` ise süresi dolmuştur).
8. **Başlangıç zamanı (`"henuz_gecerli_degil"`):** Yükte `nbf` alanı varsa (yoksa atlanır), bir sayı (`int` veya `float`, `bool` değil) olmalı ve `simdi >= nbf` koşulunu sağlamalıdır (`simdi < nbf` ise reddedilir).

Tüm kontroller geçerse `("gecerli", yuk_sozlugu)`, bir kontrolde kalırsa `("<hata_kodu>", None)` döndür.

```starter
import base64, hashlib, hmac, json

def jwt_dogrula(jeton, anahtarlar, beklenen_iss, beklenen_aud, simdi):
    # 1..8 adımlarını sırayla uygula
    return ("bicim_hatasi", None)
```

```test
import base64, hashlib, hmac, json
need("jwt_dogrula")

def _b64u(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")

def _yap(bas, yuk, sir=b"0123456789abcdef0123456789abcdef"):
    h = _b64u(json.dumps(bas, separators=(",", ":")).encode("utf-8"))
    p = _b64u(json.dumps(yuk, separators=(",", ":")).encode("utf-8"))
    if bas.get("alg") == "none":
        return f"{h}.{p}."
    imza = _b64u(hmac.new(sir, f"{h}.{p}".encode("ascii"), hashlib.sha256).digest())
    return f"{h}.{p}.{imza}"

SIR = b"0123456789abcdef0123456789abcdef"
ANAHTARLAR = {
    "k-hs": ("HS256", SIR),
    "k-rsa": ("RS256", b"-----BEGIN PUBLIC KEY-----..."),
}
TEMEL_YUK = {"iss": "https://idp.pafta.test", "sub": "ayse", "aud": "pafta-api", "exp": 2000, "nbf": 1000}

gecerli = _yap({"alg": "HS256", "kid": "k-hs"}, TEMEL_YUK)
durum, veri = jwt_dogrula(gecerli, ANAHTARLAR, "https://idp.pafta.test", "pafta-api", 1000)
eq((durum, veri["sub"]), ("gecerli", "ayse"), "simdi == nbf (1000 == 1000) geçerli")

durum2, _ = jwt_dogrula(gecerli, ANAHTARLAR, "https://idp.pafta.test", "pafta-api", 1999)
eq(durum2, "gecerli", "simdi < exp (1999 < 2000) geçerli")

eq(jwt_dogrula(gecerli, ANAHTARLAR, "https://idp.pafta.test", "pafta-api", 2000),
   ("suresi_dolmus", None), "simdi == exp (2000 == 2000) süresi dolmuş")
eq(jwt_dogrula(gecerli, ANAHTARLAR, "https://idp.pafta.test", "pafta-api", 2001),
   ("suresi_dolmus", None), "simdi > exp (2001 > 2000) süresi dolmuş")
eq(jwt_dogrula(gecerli, ANAHTARLAR, "https://idp.pafta.test", "pafta-api", 999),
   ("henuz_gecerli_degil", None), "simdi < nbf (999 < 1000) henüz geçerli değil")

nbf_yok = _yap({"alg": "HS256", "kid": "k-hs"}, {"iss": "https://idp.pafta.test", "sub": "ali", "aud": ["", 123, "pafta-api"], "exp": 2000})
eq(jwt_dogrula(nbf_yok, ANAHTARLAR, "https://idp.pafta.test", "pafta-api", 1500)[0],
   "gecerli", "nbf olmadan ve liste tipi aud içinde geçerli hedefle kabul edilmeli")

eq(jwt_dogrula(_yap({"alg": "HS256", "kid": "k-hs"}, {**TEMEL_YUK, "aud": ["", 123, "baska-api"]}),
               ANAHTARLAR, "https://idp.pafta.test", "pafta-api", 1500),
   ("aud_hatasi", None), "aud listesinde hedef yoksa aud_hatasi")
eq(jwt_dogrula(_yap({"alg": "HS256", "kid": "k-hs"}, {**TEMEL_YUK, "aud": ""}),
               ANAHTARLAR, "https://idp.pafta.test", "", 1500),
   ("aud_hatasi", None), "boş aud kabul edilmez")
eq(jwt_dogrula(_yap({"alg": "HS256", "kid": "k-hs"}, {**TEMEL_YUK, "iss": "https://sahte.test"}),
               ANAHTARLAR, "https://idp.pafta.test", "pafta-api", 1500),
   ("iss_hatasi", None), "yanlış iss reddedilmeli")

eq(jwt_dogrula(_yap({"alg": "HS256", "kid": "k-rsa"}, TEMEL_YUK, b"-----BEGIN PUBLIC KEY-----..."),
               ANAHTARLAR, "https://idp.pafta.test", "pafta-api", 1500),
   ("anahtar_hatasi", None), "RS256 anahtarı HS256 ile kullanılamaz (algoritma karışıklığı)")
eq(jwt_dogrula(_yap({"alg": "HS256", "kid": "bilinmeyen"}, TEMEL_YUK),
               ANAHTARLAR, "https://idp.pafta.test", "pafta-api", 1500),
   ("anahtar_hatasi", None), "bilinmeyen kid reddedilmeli")
eq(jwt_dogrula(_yap({"alg": "RS256", "kid": "k-hs"}, TEMEL_YUK),
               ANAHTARLAR, "https://idp.pafta.test", "pafta-api", 1500),
   ("alg_hatasi", None), "HS256 dışı alg reddedilmeli")
eq(jwt_dogrula(_yap({"alg": "HS256", "kid": "k-hs"}, TEMEL_YUK, b"yanlis-anahtar-baytlari-12345678"),
               ANAHTARLAR, "https://idp.pafta.test", "pafta-api", 1500),
   ("imza_hatasi", None), "yanlış anahtarla imzalanmış jeton imza_hatasi")

eq(jwt_dogrula(_yap({"alg": "HS256", "kid": "k-hs"}, {**TEMEL_YUK, "exp": True}),
               ANAHTARLAR, "https://idp.pafta.test", "pafta-api", 0),
   ("suresi_dolmus", None), "bool exp sayı olarak kabul edilmemeli")
eq(jwt_dogrula(_yap({"alg": "HS256", "kid": "k-hs"}, {**TEMEL_YUK, "nbf": False}),
               ANAHTARLAR, "https://idp.pafta.test", "pafta-api", 1500),
   ("henuz_gecerli_degil", None), "bool nbf sayı olarak kabul edilmemeli")

for bozuk in (None, "", "a.b", "a.b.c.d", "a.b.", "a..c", ".b.c", "a.b.c=", "!!!.b.c",
              f"{_b64u(b'[]')}.{_b64u(b'{}')}.imza", f"{_b64u(b'{}')}.{_b64u(b'[]')}.imza"):
    eq(jwt_dogrula(bozuk, ANAHTARLAR, "https://idp.pafta.test", "pafta-api", 1500),
       ("bicim_hatasi", None), f"bozuk girdi: {bozuk!r}")
```

```solution
import base64, hashlib, hmac, json, re


def _b64url_coz(parca):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", parca):
        raise ValueError("geçersiz base64url")
    return base64.urlsafe_b64decode(parca + "=" * (-len(parca) % 4))


def _sayi_mi(deger):
    return isinstance(deger, (int, float)) and not isinstance(deger, bool)


def jwt_dogrula(jeton, anahtarlar, beklenen_iss, beklenen_aud, simdi):
    if not isinstance(jeton, str):
        return ("bicim_hatasi", None)
    parcalar = jeton.split(".")
    if len(parcalar) != 3:
        return ("bicim_hatasi", None)
    bas_b64, yuk_b64, imza_b64 = parcalar
    try:
        bas = json.loads(_b64url_coz(bas_b64).decode("utf-8"))
        yuk = json.loads(_b64url_coz(yuk_b64).decode("utf-8"))
        _b64url_coz(imza_b64)
    except Exception:
        return ("bicim_hatasi", None)
    if not isinstance(bas, dict) or not isinstance(yuk, dict):
        return ("bicim_hatasi", None)

    if bas.get("alg") != "HS256":
        return ("alg_hatasi", None)

    kid = bas.get("kid")
    if not isinstance(kid, str) or kid not in anahtarlar:
        return ("anahtar_hatasi", None)
    anahtar_alg, sir = anahtarlar[kid]
    if anahtar_alg != "HS256":
        return ("anahtar_hatasi", None)

    girdi = f"{bas_b64}.{yuk_b64}".encode("ascii")
    beklenen_imza = base64.urlsafe_b64encode(hmac.new(sir, girdi, hashlib.sha256).digest()).rstrip(b"=").decode("ascii")
    if not hmac.compare_digest(imza_b64, beklenen_imza):
        return ("imza_hatasi", None)

    if yuk.get("iss") != beklenen_iss:
        return ("iss_hatasi", None)

    aud = yuk.get("aud")
    if isinstance(aud, str):
        aud_uygun = bool(aud) and aud == beklenen_aud
    elif isinstance(aud, list):
        aud_uygun = any(isinstance(x, str) and x != "" and x == beklenen_aud for x in aud)
    else:
        aud_uygun = False
    if not aud_uygun:
        return ("aud_hatasi", None)

    exp = yuk.get("exp")
    if not _sayi_mi(exp) or simdi >= exp:
        return ("suresi_dolmus", None)

    if "nbf" in yuk:
        nbf = yuk.get("nbf")
        if not _sayi_mi(nbf) or simdi < nbf:
            return ("henuz_gecerli_degil", None)

    return ("gecerli", yuk)
```

```hint
Python'da `isinstance(True, int)` değeri `True` döndürür; `exp` ve `nbf` için `isinstance(x, (int, float)) and not isinstance(x, bool)` kontrolünü kullan. `exp` sınırında `simdi >= exp` geçersizdir; `nbf` sınırında ise `simdi < nbf` geçersizdir.
```
:::

::: gorev 2 · OAuth 2.0 yönlendirme ve PKCE S256 denetçisi (RFC 9700 ve RFC 7636)
İki fonksiyon yaz:

1. `pkce_dogrula(code_verifier, code_challenge, method)`:
   - `method` yalnızca `"S256"` olmalıdır (`"plain"` vb. `False`).
   - `code_verifier` ve `code_challenge` birer `str` olmalıdır.
   - `code_verifier` yalnızca `[A-Za-z0-9\-._~]` karakterlerinden oluşmalı ve uzunluğu **en az 43, en fazla 128** (`43 <= len(code_verifier) <= 128`) olmalıdır.
   - `BASE64URL(SHA256(ASCII(code_verifier)))` değeri `code_challenge` ile eşleşiyorsa `True`, aksi hâlde `False` döndürsün.
2. `yetki_istegi_degerlendir(sorgu, istemciler)`:
   - `istemciler`, `{"client_id": ["https://...", ...]}` biçiminde kayıtlı yönlendirme adreslerini tutar.
   - İlk olarak `sorgu` sözlüğündeki `client_id` ve `redirect_uri` alanlarını kontrol et: `client_id` kayıtlı değilse veya `redirect_uri` o istemcinin listesinde **birebir tam metin olarak** yer almıyorsa `(400, "invalid_redirect_uri")` döndür (RFC 6749 Bölüm 4.1.2.1 gereği asla yönlendirme yapma).
   - `redirect_uri` geçerliyse; `response_type != "code"`, `state` boş/eksik, `code_challenge` boş/eksik veya `code_challenge_method != "S256"` durumlarından biri varsa `(302, f"{redirect_uri}?error=invalid_request&state={state}")` döndür (`state` yoksa boş metin `""`).
   - Hepsi geçerliyse `(302, f"{redirect_uri}?code=kod-100&state={state}")` döndür.

```starter
import base64, hashlib, re

def pkce_dogrula(code_verifier, code_challenge, method):
    return False

def yetki_istegi_degerlendir(sorgu, istemciler):
    return (400, "invalid_redirect_uri")
```

```test
import base64, hashlib
need("pkce_dogrula")
need("yetki_istegi_degerlendir")

def _s256(v):
    return base64.urlsafe_b64encode(hashlib.sha256(v.encode("ascii")).digest()).rstrip(b"=").decode("ascii")

v43 = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"   # tam 43
v42 = v43[:-1]                                          # 42 (< 43)
v128 = "A" * 128                                        # tam 128
v129 = "A" * 129                                        # 129 (> 128)

eq(pkce_dogrula(v43, "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM", "S256"), True, "RFC 7636 Ek B 43 karakter örneği")
eq(pkce_dogrula(v128, _s256(v128), "S256"), True, "üst sınır 128 karakter geçerli")
eq(pkce_dogrula(v42, _s256(v42), "S256"), False, "42 karakter (< 43) reddedilmeli")
eq(pkce_dogrula(v129, _s256(v129), "S256"), False, "129 karakter (> 128) reddedilmeli")
eq(pkce_dogrula("a" * 42 + "+", _s256("a" * 42 + "+"), "S256"), False, "izin verilmeyen karakter (+) reddedilmeli")
eq(pkce_dogrula(v43, v43, "plain"), False, "plain yöntemi reddedilmeli")
eq(pkce_dogrula(v43, _s256(v128), "S256"), False, "yanlış challenge reddedilmeli")
eq(pkce_dogrula(None, "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM", "S256"), False, "None verifier")

ISTEMCILER = {"pafta-web": ["https://uygulama.pafta.test/callback"]}
TAM = {
    "client_id": "pafta-web",
    "redirect_uri": "https://uygulama.pafta.test/callback",
    "response_type": "code",
    "state": "xyz99",
    "code_challenge": _s256(v43),
    "code_challenge_method": "S256",
}
eq(yetki_istegi_degerlendir(TAM, ISTEMCILER),
   (302, "https://uygulama.pafta.test/callback?code=kod-100&state=xyz99"), "geçerli yetkilendirme isteği")

for kotu_uri in ("https://uygulama.pafta.test/callback/../../acik",
                 "https://uygulama.pafta.test/callback?ek=1",
                 "http://uygulama.pafta.test/callback",
                 "https://saldirgan.test/callback", ""):
    eq(yetki_istegi_degerlendir({**TAM, "redirect_uri": kotu_uri}, ISTEMCILER),
       (400, "invalid_redirect_uri"), f"tam eşleşmeyen redirect_uri yönlendirilmemeli: {kotu_uri}")

eq(yetki_istegi_degerlendir({**TAM, "client_id": "bilinmeyen"}, ISTEMCILER),
   (400, "invalid_redirect_uri"), "bilinmeyen client_id 400 döndürmeli")

for alan, deger in [("response_type", "token"), ("state", ""), ("code_challenge", ""), ("code_challenge_method", "plain")]:
    beklenen_st = "" if alan == "state" else "xyz99"
    eq(yetki_istegi_degerlendir({**TAM, alan: deger}, ISTEMCILER),
       (302, f"https://uygulama.pafta.test/callback?error=invalid_request&state={beklenen_st}"),
       f"hatalı {alan} kayıtlı redirect_uri'ye hata ile yönlendirilmeli")
```

```solution
import base64, hashlib, hmac, re


def pkce_dogrula(code_verifier, code_challenge, method):
    if method != "S256" or not isinstance(code_verifier, str) or not isinstance(code_challenge, str):
        return False
    if not (43 <= len(code_verifier) <= 128) or not re.fullmatch(r"[A-Za-z0-9\-._~]+", code_verifier):
        return False
    hesaplanan = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode("ascii")).digest()).rstrip(b"=").decode("ascii")
    return hmac.compare_digest(hesaplanan, code_challenge)


def yetki_istegi_degerlendir(sorgu, istemciler):
    cid = sorgu.get("client_id", "")
    ruri = sorgu.get("redirect_uri", "")
    if cid not in istemciler or ruri not in istemciler[cid]:
        return (400, "invalid_redirect_uri")
    st = sorgu.get("state", "")
    if (sorgu.get("response_type") != "code"
            or not st
            or not sorgu.get("code_challenge")
            or sorgu.get("code_challenge_method") != "S256"):
        return (302, f"{ruri}?error=invalid_request&state={st}")
    return (302, f"{ruri}?code=kod-100&state={st}")
```

```hint
`43 <= len(code_verifier) <= 128` sınırını ve `[A-Za-z0-9\-._~]+` karakter kümesini kontrol et. `yetki_istegi_degerlendir` içinde önce `client_id` ve `redirect_uri` tam eşleşmesine bak; o geçmeden asla `302` döndürme.
```
:::

::: gorev 3 · Uçtan uca OAuth 2.0 + PKCE istemcisi
`oauth_kasa_oku(client_id, redirect_uri, state, code_verifier, takas_verifier=None)` fonksiyonunu yaz. Fonksiyon tezgahtaki yerel sunucuyla (`tezgah.yanit`) üç adımlı OAuth 2.0 + PKCE akışını yürütsün:

1. `code_verifier` (43–128 karakter) üzerinden `S256` ile `code_challenge` hesapla ve `/oauth/authorize` adresine `client_id`, `redirect_uri`, `response_type=code`, `state`, `code_challenge`, `code_challenge_method=S256` sorgu parametreleriyle `GET` gönder.
   - Yanıt durumu `400` ise `("yonlendirme_hatasi", None)` döndür.
   - `302` yanıtındaki `Location` başlığının sorgu parametrelerini ayrıştır: dönen `state` değeri gönderdiğin `state` ile aynı değilse `("state_hatasi", None)` döndür; `code` parametresi yoksa `("yetki_hatasi", None)` döndür.
2. `/oauth/token` adresine `POST` ile JSON gövdesi gönder: `grant_type="authorization_code"`, `client_id`, `redirect_uri`, `code` ve `code_verifier` olarak `takas_verifier or code_verifier` değerini ilet.
   - Yanıt durumu `200` değilse `("takas_hatasi", None)` döndür.
3. Dönen `access_token` değerini `Authorization: Bearer <access_token>` başlığına koyarak `GET /api/kasa` isteği gönder.
   - Yanıt `200` ise `("acik", f"{j['sub']}:{j['rol']}")` döndür.

```starter
import base64, hashlib, json
from urllib.parse import parse_qs, urlencode, urlsplit
import tezgah

def oauth_kasa_oku(client_id, redirect_uri, state, code_verifier, takas_verifier=None):
    # 1. GET /oauth/authorize -> 2. POST /oauth/token -> 3. GET /api/kasa
    return ("yonlendirme_hatasi", None)
```

```test
need("oauth_kasa_oku")
V_DOGRU = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
V_YANLIS = "A" * 43
URI = "https://uygulama.pafta.test/callback"

eq(oauth_kasa_oku("pafta-web", URI, "st-101", V_DOGRU),
   ("acik", "analist:denetci"), "tam OAuth 2.0 + PKCE + Bearer JWT akışı başarılı olmalı")

eq(oauth_kasa_oku("pafta-web", "https://saldirgan.test/cb", "st-101", V_DOGRU),
   ("yonlendirme_hatasi", None), "kayıtsız redirect_uri 400 ile reddedilmeli")

eq(oauth_kasa_oku("pafta-web", URI, "", V_DOGRU),
   ("yetki_hatasi", None), "boş state ile yetki kodu verilmez")

eq(oauth_kasa_oku("pafta-web", URI, "st-101", V_DOGRU, takas_verifier=V_YANLIS),
   ("takas_hatasi", None), "yanlış code_verifier token takasında reddedilmeli")

eq(oauth_kasa_oku("pafta-web", URI, "CSRF_SALDIRI", V_DOGRU),
   ("state_hatasi", None), "dönen state beklenenle uyuşmazsa istemci akışı durdurmalı")
```

```solution
import base64, hashlib, json
from urllib.parse import parse_qs, urlencode, urlsplit
import tezgah


def oauth_kasa_oku(client_id, redirect_uri, state, code_verifier, takas_verifier=None):
    challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode("ascii")).digest()).rstrip(b"=").decode("ascii")
    sorgu = urlencode({
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    })
    y1 = tezgah.yanit(f"GET /oauth/authorize?{sorgu} HTTP/1.1\r\nHost: idp.pafta.test\r\n\r\n")
    if y1.durum == 400:
        return ("yonlendirme_hatasi", None)
    konum = y1.baslik("Location") or ""
    paramlar = parse_qs(urlsplit(konum).query, keep_blank_values=True)
    donen_state = paramlar.get("state", [""])[0]
    if donen_state != state:
        return ("state_hatasi", None)
    if "code" not in paramlar or not paramlar["code"][0]:
        return ("yetki_hatasi", None)
    kod = paramlar["code"][0]

    govde = json.dumps({
        "grant_type": "authorization_code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code": kod,
        "code_verifier": takas_verifier if takas_verifier is not None else code_verifier,
    })
    y2 = tezgah.yanit(
        f"POST /oauth/token HTTP/1.1\r\nHost: idp.pafta.test\r\n"
        f"Content-Type: application/json\r\nContent-Length: {len(govde)}\r\n\r\n{govde}"
    )
    if y2.durum != 200:
        return ("takas_hatasi", None)
    jeton = y2.json()["access_token"]

    y3 = tezgah.yanit(f"GET /api/kasa HTTP/1.1\r\nHost: api.pafta.test\r\nAuthorization: Bearer {jeton}\r\n\r\n")
    j = y3.json()
    return ("acik", f"{j['sub']}:{j['rol']}")
```

```hint
`/oauth/authorize` yanıtındaki `Location` başlığını `urlsplit(konum).query` ve `parse_qs(..., keep_blank_values=True)` ile ayrıştır; önce `state` eşleşmesini, ardından `code` varlığını kontrol et.
```
```setup
import base64, hashlib, hmac, json
import tezgah

_G = tezgah.Yanit.__init__.__globals__
_Isleyici = _G["Isleyici"]
_ROTALAR = _G["ROTALAR"]
_SIR = b"pafta-cok-gizli-hmac-anahtari-32b"
_KAYITLI_URI = "https://uygulama.pafta.test/callback"
_KODLAR = {}

def _b64u_e(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")

def _b64u_d(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))

def _jwt_uret(yuk, kid="anahtar-2026"):
    h = _b64u_e(json.dumps({"alg": "HS256", "kid": kid, "typ": "JWT"}, separators=(",", ":")).encode())
    p = _b64u_e(json.dumps(yuk, separators=(",", ":")).encode())
    imza = _b64u_e(hmac.new(_SIR, f"{h}.{p}".encode("ascii"), hashlib.sha256).digest())
    return f"{h}.{p}.{imza}"

def r_oauth_authorize(self):
    cid = self.sorgu.get("client_id", "")
    ruri = self.sorgu.get("redirect_uri", "")
    if cid != "pafta-web" or ruri != _KAYITLI_URI:
        return self._yanit(400, {"error": "invalid_redirect_uri"})
    st = self.sorgu.get("state", "")
    rt = self.sorgu.get("response_type", "")
    cc = self.sorgu.get("code_challenge", "")
    ccm = self.sorgu.get("code_challenge_method", "")
    donen_st = "bozuk-state" if st == "CSRF_SALDIRI" else st
    if rt != "code" or not st or not cc or ccm != "S256":
        return self._yonlendir(302, f"{ruri}?error=invalid_request&state={donen_st}")
    kod = "kod-901"
    _KODLAR[kod] = {"client_id": cid, "redirect_uri": ruri, "challenge": cc, "kullanildi": False}
    return self._yonlendir(302, f"{ruri}?code={kod}&state={donen_st}")

def r_oauth_token(self):
    ham, _ = self._govde_oku()
    if ham is None:
        return
    try:
        v = json.loads(ham.decode("utf-8"))
    except Exception:
        return self._yanit(400, {"error": "invalid_request"})
    kod = v.get("code", "")
    kayit = _KODLAR.get(kod)
    verifier = v.get("code_verifier", "")
    if (not kayit or kayit["kullanildi"]
            or v.get("client_id") != kayit["client_id"]
            or v.get("redirect_uri") != kayit["redirect_uri"]
            or not isinstance(verifier, str) or not (43 <= len(verifier) <= 128)):
        return self._yanit(400, {"error": "invalid_grant"})
    hesaplanan = _b64u_e(hashlib.sha256(verifier.encode("ascii")).digest())
    if not hmac.compare_digest(hesaplanan, kayit["challenge"]):
        return self._yanit(400, {"error": "invalid_grant"})
    kayit["kullanildi"] = True
    jeton = _jwt_uret({
        "iss": "https://idp.pafta.test",
        "sub": "analist",
        "aud": "pafta-api",
        "nbf": 1700000000,
        "exp": 1900000000,
        "rol": "denetci",
    })
    return self._yanit(200, {"access_token": jeton, "token_type": "Bearer"})

def r_api_kasa(self):
    yetki = self.headers.get("Authorization", "")
    sema, _, jeton = yetki.partition(" ")
    if sema.lower() != "bearer" or not jeton:
        return self._yanit(401, {"hata": "jeton gerekli"}, [("WWW-Authenticate", "Bearer")])
    parcalar = jeton.split(".")
    if len(parcalar) != 3:
        return self._yanit(401, {"hata": "bicim"}, [("WWW-Authenticate", 'Bearer error="invalid_token"')])
    try:
        bas = json.loads(_b64u_d(parcalar[0]).decode("utf-8"))
        yuk = json.loads(_b64u_d(parcalar[1]).decode("utf-8"))
    except Exception:
        return self._yanit(401, {"hata": "cozulemedi"}, [("WWW-Authenticate", 'Bearer error="invalid_token"')])
    beklenen_imza = _b64u_e(hmac.new(_SIR, f"{parcalar[0]}.{parcalar[1]}".encode("ascii"), hashlib.sha256).digest())
    simdi = 1800000000
    if (bas.get("alg") != "HS256" or bas.get("kid") != "anahtar-2026"
            or not hmac.compare_digest(parcalar[2], beklenen_imza)
            or yuk.get("iss") != "https://idp.pafta.test"
            or yuk.get("aud") != "pafta-api"
            or not (yuk.get("nbf", 0) <= simdi < yuk.get("exp", 0))):
        return self._yanit(401, {"hata": "gecersiz"}, [("WWW-Authenticate", 'Bearer error="invalid_token"')])
    return self._yanit(200, {"kasa": "acik", "sub": yuk["sub"], "rol": yuk.get("rol")})

_Isleyici.r_oauth_authorize = r_oauth_authorize
_Isleyici.r_oauth_token = r_oauth_token
_Isleyici.r_api_kasa = r_api_kasa
if not any(isim == "oauth_authorize" for _, _, isim in _ROTALAR):
    _ROTALAR.extend([
        (r"/oauth/authorize", ("GET",), "oauth_authorize"),
        (r"/oauth/token", ("POST",), "oauth_token"),
        (r"/api/kasa", ("GET",), "api_kasa"),
    ])
```
:::
