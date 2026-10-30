---
id: ad23
title: Channel Binding'i Gerçek Bağlantıda Sınamak
summary: TLS ile SASL kimlik doğrulamasının bağlanması, geçerli/eksik/bozuk CBT karşılaştırması ve sunucu olaylarının yorumu.
---

::: anlat TLS varsa CBT neden var?
Channel binding, SASL kimlik doğrulamasını kullanılan TLS kanalına bağlar. Sunucunun sertifikasını doğrulamakla ve LDAP signing ile aynı kontrol değildir. Microsoft politikasındaki `LdapEnforceChannelBinding`: `0` Never, `1` When supported, `2` Always. Yeni Windows Server 2025 kurulumunda varsayılanın When supported olması, her müşterinin CBT olmadan reddedildiği anlamına gelmez. Bu Pafta laboratuvarı karşılaştırma için **Always (2)** kullanır. [Microsoft CBT politikası](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/ldap-channel-binding).

`probe('valid')`, `probe('none')`, `probe('wrong')` deneylerinin üçünde de TLS sertifikası ve adı doğrulanır. Sonra kurulu Impacket istemcisi sırasıyla doğru, eksik ve değiştirilmiş CBT ile gerçek SASL NTLM bind dener. Bu küçük test eklentisi yalnız istemcinin CBT alanını değiştirir; sunucunun cevabını taklit etmez. [İstemci uygulaması](https://github.com/fortra/impacket/blob/master/impacket/ldap/ldap.py), [tls-server-end-point tanımı](https://www.rfc-editor.org/rfc/rfc5929#section-4).

3039 geçersiz CBT'nin reddini incelemek için önemlidir. 3074/3075 gibi denetim olaylarının koşulları ve tanılama seviyesi sunucu sürümüne bağlıdır. Olay kimliğinin bulunmaması tek başına bağlantının güvenli olduğunu kanıtlamaz. [Microsoft olay tablosu](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/ldap-channel-binding).
:::

::: tahmin Aynı TLS, farklı bind sonucu
Kodun üç satırını tahmin et.

```python
from ad_lab import probe
for mode in ("valid", "none", "wrong"):
    print(mode, probe(mode)["ok"])
```

???

`valid True`, `none False`, `wrong False`. Başarısızlıklar, doğru CA ile kurulmuş TLS bağlantısından sonraki gerçek bind aşamasında oluşur.

```meta
motor: ad-client
dil: python
timeout: 180
```
:::

::: gorev Bağlantının hangi aşamada durduğunu ayır
`asama(mode)` gerçek `probe(mode)` sonucuna göre `basarili`, `sertifika`, `ldap-bind` veya `tasima` döndürsün. `ok=True` ilk durum; başarısız sonuçtaki `category` sırasıyla `certificate`, `ldap` veya başka bir şeydir. Mod adına bakarak sınıflandırma yapma: test, aynı işlevi sunucudan gelen gerçek sonuçlarla ve beklenmeyen hata örnekleriyle sınar.

```starter
from ad_lab import probe

def asama(mode):
    return "tasima"

print(asama("wrong"))
```

```test
eq(asama("valid"), "basarili", "geçerli CBT ile gerçek bind")
eq(asama("none"), "ldap-bind", "CBT yok: sertifika kontrolü geçti")
eq(asama("wrong"), "ldap-bind", "yanlış CBT: gerçek bind ret")
eq(asama("bad-ca"), "sertifika", "CA doğrulaması")
eq(asama("bad-name"), "sertifika", "sunucu adı doğrulaması")
f = need("asama")
original = f.__globals__["probe"]
try:
    for result, expected in [({"ok": False, "category": "transport"}, "tasima"), ({"ok": False}, "tasima"), ({"ok": True, "category": "ldap"}, "basarili"), ({"ok": False, "category": "certificate"}, "sertifika")]:
        f.__globals__["probe"] = lambda _mode, r=result: r
        eq(f("beklenmeyen-mod"), expected, "sonuçtan sınıflandır; mod adını ezberleme")
finally:
    f.__globals__["probe"] = original
```

```solution
from ad_lab import probe

def asama(mode):
    result = probe(mode)
    if result["ok"]:
        return "basarili"
    if result.get("category") == "certificate":
        return "sertifika"
    if result.get("category") == "ldap":
        return "ldap-bind"
    return "tasima"

print(asama("wrong"))
```

```hint
Önce `ok` alanını kontrol et. Başarısızsa gerçek hata kategorisini oku; `wrong` adını görüp doğrudan ret sonucu yazma.
```

```meta
motor: ad-client
dil: python
timeout: 240
```
:::
