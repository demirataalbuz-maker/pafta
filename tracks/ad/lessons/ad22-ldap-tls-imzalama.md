---
id: ad22
title: Gerçek LDAP Bağlantısında TLS ve İmzalama
summary: Pafta içinden gerçek DC'ye doğrulanmış LDAPS, StartTLS ve imzalı SASL sorguları; sertifika hatasını LDAP filtresiyle karıştırmamak.
---

::: anlat Filtre doğru, bağlantı neden başarısız?
AD01–AD12 filtre motoru yalnız dizin eşleşmesini ölçer. Bu derste `ad_lab.probe` gerçek ağ istemcisidir: Kali WSL'deki mevcut OpenLDAP/Impacket ile Pafta'nın `PF-DC01` sunucusuna bağlanır. Hedef ve test kimliği laboratuvara sabittir; parola kullanıcı koduna veya çıktı listesine verilmez. Pafta sunucuyu arka planda açar.

**TLS**, sunucu sertifikası ve bağlantı korumasıdır. **LDAP signing**, TLS dışındaki SASL bağlantısında mesaj bütünlüğü sağlar. İmzalama tek başına gizlilikle aynı şey değildir. LDAPS 636'da TLS'yle başlar; StartTLS, LDAP bağlantısını 389'da TLS'ye yükseltir. StartTLS başarısızken açık bağlantıya devam etmemek gerekir. Laboratuvardaki OpenLDAP çağrısı bunu zorunlu `-ZZ` ile yapar. [Microsoft LDAP signing](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/ldap-signing), [LDAPS sertifika gereksinimleri](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/enable-ldap-over-ssl-3rd-certification-authority), [OpenLDAP ldapsearch](https://www.openldap.org/software/man.cgi?query=ldapsearch&sektion=1).

`probe('valid')` güvenilen CA ve doğru sunucu adıyla LDAPS/SASL bağlantısı kurar. `probe('signed')` TLS olmadan imzalı SASL sorgusu yapar. `unsigned` sunucunun imza zorlamasıyla reddedilir. `bad-ca` güvenilmeyen CA, `bad-name` yanlış sunucu adı deneyidir; ikisinde de kimlik doğrulamadan önce sertifika kontrolü durur. `starttls`, gerçek OpenLDAP simple bind'i zorunlu TLS üzerinden yapar. Simple bind'i SASL channel binding deneyi sanma.

Impacket'in TLS taşıması CA/ad doğrulamasını kendisi sağlamadığı için Pafta önce Python TLS ile zincir ve adı doğrular, ardından LDAP bağlantısındaki **aynı leaf sertifikasını** karşılaştırır ve TLS 1.2/1.3 ister. Bu ek doğrulama [kurulu istemcinin davranışını](https://github.com/fortra/impacket/blob/master/impacket/ldap/ldap.py) tamamlar. Test için `CERT_NONE` veya sertifika doğrulamasını kabul eden callback kullanılmaz.
:::

::: tahmin Sertifika ve StartTLS
Üç deneyin başarı alanları ne yazar?

```python
from ad_lab import probe
for mode in ("bad-ca", "bad-name", "starttls"):
    print(mode, probe(mode)["ok"])
```

???

`bad-ca False`, `bad-name False`, `starttls True`. İlk iki deneyde filtreyi değiştirmek çözüm değildir; sertifika güveni ve sunucu adı düzeltilmelidir.

```meta
motor: ad-client
dil: python
timeout: 180
```
:::

::: gorev Gerçek LDAPS sonucunda tam kullanıcıyı ara
`kullanici_var(ad)` işlevi `probe('valid', filtre)` ile **tam sAMAccountName** filtresi yollasın. Yalnız başarılı bağlantıda `ad` gerçek `names` listesinde bulunursa `True` döndür. Girdideki `*`, `(`, `)`, ters eğik çizgi ve NUL'u RFC 4515'e göre kaçır; bir jokerin bütün kullanıcıları eşleştirmesine izin verme. Mevcut kullanıcı adlarını kodda sabitleme. Gerçek ağ sorgularına ek olarak test, beklenmeyen bir istemci sonucunun başka kullanıcıyı veya başarısız bağlantıyı doğru kullanıcı sanmamasını da sınar. [RFC 4515 kaçış kuralı](https://www.rfc-editor.org/rfc/rfc4515#section-3).

```starter
from ad_lab import probe

def kullanici_var(ad):
    return False

print(kullanici_var("ali.kaya"))
```

```test
f = need("kullanici_var")
original = f.__globals__["probe"]
filters = []
def audited(mode, filtre):
    filters.append(filtre)
    return original(mode, filtre)
f.__globals__["probe"] = audited
try:
    eq(kullanici_var("ali.kaya"), True, "gerçek kullanıcı")
    eq(kullanici_var("mehmet.yilmaz"), True, "ikinci gerçek kullanıcı")
    eq(kullanici_var("ali.kay"), False, "eksik son harf")
    eq(kullanici_var("ali.kayaX"), False, "ek son harf")
    eq(kullanici_var("*"), False, "yıldız joker değil düz veri")
    eq(kullanici_var("ali.kaya)(objectClass=*)"), False, "parantez filtreyi değiştirmesin")
    eq(kullanici_var("ali\\kaya"), False, "ters eğik çizgi")
    eq(kullanici_var("ali\0kaya"), False, "NUL filtre verisi olarak kaçırılsın")
finally:
    f.__globals__["probe"] = original
for value in [r"(sAMAccountName=\2a)", r"(sAMAccountName=ali.kaya\29\28objectClass=\2a\29)", r"(sAMAccountName=ali\5ckaya)", r"(sAMAccountName=ali\00kaya)"]:
    ok(value in filters, "sunucuya gerçekten kaçırılmış tam filtre gönder: " + value)
try:
    for result, expected in [({"ok": True, "names": ["mehmet.yilmaz"]}, False), ({"ok": False, "names": ["ali.kaya"]}, False), ({"ok": True, "names": []}, False), ({"ok": True, "names": ["ali.kaya"]}, True)]:
        f.__globals__["probe"] = lambda _mode, _filter, r=result: r
        eq(f("ali.kaya"), expected, "beklenmeyen istemci sonucunda doğru hesabı ve bağlantı başarısını kontrol et")
finally:
    f.__globals__["probe"] = original
eq(original("signed")["ok"], True, "gerçek imzalı SASL")
eq(original("unsigned")["ok"], False, "imzasız SASL sunucuda reddedilir")
```

```solution
from ad_lab import probe

def kullanici_var(ad):
    escapes = {"*": r"\2a", "(": r"\28", ")": r"\29", "\\": r"\5c", "\0": r"\00"}
    value = "".join(escapes.get(ch, ch) for ch in ad)
    result = probe("valid", "(sAMAccountName=" + value + ")")
    return result["ok"] and ad in result.get("names", [])

print(kullanici_var("ali.kaya"))
```

```hint
Kaçışı karakter karakter yap; daha önce ürettiğin ters eğik çizgileri tekrar kaçırma. Bağlantı başarısı ile sorgunun eşleşme üretmesini ayrı kontrol et.
```

```meta
motor: ad-client
dil: python
timeout: 240
```
:::
