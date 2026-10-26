---
id: ad17
title: S4U Bilet Akışını Kanıtla
summary: Kendi hizmetine gelen bilet ile arka hizmet biletini ilişkilendirmek, başarısız isteği ayırmak ve gerçek DC üzerinde kabul kanıtını toplamak.
---

::: anlat İki bilet, üç taraf
Ön hizmetin TGT'si, kullanıcı adına ön hizmete düzenlenen S4U2Self bileti ve kullanıcı adına arka hizmete düzenlenen S4U2Proxy bileti farklı şeylerdir. Proxy isteği ön hizmete ait kullanıcı hizmet biletini ek kanıt olarak taşır; istemci adı kullanıcıyı gösterir. İsteği gönderen ön hizmetin kimliğiyle bunu karıştırma. [MS-SFU örneği](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-sfu/c920c148-8a9c-42e9-b8e9-db5755cd281b).

DC üzerindeki **4769**, TGS isteği kaydıdır; `Status` sıfır değilse isteğin başarısızlığına bakarsın. `ServiceName`, `TargetUserName`, `TransmittedServices`, bilet seçenekleri ve istemci adresi birlikte okunur. 4769'un 2025 güncellemeleriyle yeni sürümleri vardır; alan adlarına göre XML oku. Tek bir 4769, bir HTTP işleminin başarıyla tamamlandığını veya iki isteğin aynı S4U zinciri olduğunu tek başına kanıtlamaz. [Microsoft 4769 alanları](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4769).
:::

::: anlat Gerçek laboratuvar kabulü
Pafta'nın `s4u.json` dosyasındaki `asama`, `id`, `sira`, `evidence_sira` alanları **ders için verilmiş ilişkilendirme bilgisidir**. Bunlar 4769'un XML alanları değildir. Kaynakta yoksa böyle bir ilişkiyi varsayma. Aşağıdaki işlev bilet üretmez; önceden ilişkilendirilmiş bir kanıt listesini denetler.

Gerçek kabulü sonraki **AD18** dersinde Pafta'nın Çalıştır/Kontrol düğmeleriyle yaparsın. Pafta iki sunucuyu arka planda açar; Windows S4U oturumu ve gerçek SMB erişimi sonucunu, ayrıca o oturumun `klist` çıktısını döndürür. `classic`, `rbcd`, `missing`, `blocked` deneylerini ayrı değerlendir. Klasik/RBCD izinleri AD16'daki özelliklerdir; helper bunları yalnız laboratuvar hesaplarında değiştirip temizler.

DC tarafındaki gerçek 4769 XML'i de AD18'in sonundaki Pafta kod kutusundan okunabilir. `TargetUserName`, `ServiceName`, `TransmittedServices` ve zaman aralığıyla incele; normal TGS olaylarını S4U kanıtı sanma. Paket kaydı ek kanıttır; bu görev paket yakalamaz ve her biletin tel üstü akışını doğruladığını iddia etmez. RBCD'de nonforwardable biletin kabulünü her KDC/sürüm için varsayma; o özel durum ayrı bilet incelemesi gerektirir. [MS-SFU şartları](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-sfu/ddb2cafd-1f01-4834-b52a-d4a5b34cd960).

Bu dersteki JSON görevi yalnız kayıt okuma becerisini ölçer. AD18'deki canlı kabulün yerine geçmez.
:::

::: tahmin Başarılı Self, başarısız Proxy
Kod hangi iki satırı yazar? B akışını başarılı devir diye raporlayabilir miyiz?

```python
import json
v = json.load(open("s4u.json", encoding="utf-8"))
for e in v["akislar"]:
    if e["id"] == "B":
        print(e["asama"], e["durum"])
```

???

`S4U2Self 0x0` ve `S4U2Proxy 0xD`. Proxy isteği başarısızdır. Self kaydının başarılı olması, arka hizmet için bilet alındığını kanıtlamaz.

```meta
motor: python
dil: python
```
:::

::: gorev Başarılı ve tutarlı zincirleri seç
`zincirler(v)` işlevi **yalnız bu dosyanın kanıt sözleşmesine göre** tamamlanmış akış kimliklerini sıralı döndürsün. Bir akışta tam bir `S4U2Self` ve tam bir `S4U2Proxy` kaydı bulunmalı; ikisinin `durum` alanı `0x0`, ön hesap ve kullanıcı eşit olmalı. `Self.sira < Proxy.sira` ve `Proxy.evidence_sira == Self.sira` olmalı. Self'in hedefi, `hesaplar`daki ön hesabın SPN'siyle eşit olmalı. Eksik/çelişen/yinelenen kayıtları dışarıda bırak. Yapılandırmadan yeni başarı uydurma; `forwardable` kapalı diye de kayıtta başarılı olan bir RBCD akışını otomatik reddetme.

```starter
import json
veri = json.load(open("s4u.json", encoding="utf-8"))

def zincirler(v):
    return []

print(zincirler(veri))
```

```test
import copy
eq(zincirler(veri), ["A"], "A tamam, B başarısız, C eksik")
for alan, deger in [("durum", "0xD"), ("sira", 10), ("sira", 9), ("evidence_sira", 9), ("kullanici", "yonetici"), ("on_hizmet", "svc_rapor")]:
    v = copy.deepcopy(veri)
    v["akislar"][1][alan] = deger
    eq(zincirler(v), [], "Proxy sınırı: " + alan + "=" + str(deger))
v = copy.deepcopy(veri)
v["akislar"][0]["hedef_spn"] = "HTTP/baska.pafta.local"
eq(zincirler(v), [], "Self yanlış hizmete ait")
v = copy.deepcopy(veri)
v["akislar"].append(copy.deepcopy(v["akislar"][0]))
eq(zincirler(v), [], "yinelenen Self ilişkisi belirsiz")
v = copy.deepcopy(veri)
v["akislar"][0]["forwardable"] = False
eq(zincirler(v), ["A"], "bu işlev KDC politikası değil başarı kanıtı okur")
v = copy.deepcopy(veri)
v["akislar"] = list(reversed(v["akislar"]))
eq(zincirler(v), ["A"], "dosya sırası yerine sira alanı")
v = copy.deepcopy(veri)
v["akislar"][0]["durum"] = "0xD"
eq(zincirler(v), [], "Self de başarılı olmalı")
eq(zincirler({"hesaplar": {}, "akislar": []}), [], "boş kanıt")
```

```solution
import json
veri = json.load(open("s4u.json", encoding="utf-8"))

def zincirler(v):
    gruplar = {}
    for e in v["akislar"]:
        gruplar.setdefault(e["id"], []).append(e)
    sonuc = []
    for kimlik, olaylar in gruplar.items():
        selfler = [e for e in olaylar if e["asama"] == "S4U2Self"]
        proxyler = [e for e in olaylar if e["asama"] == "S4U2Proxy"]
        if len(selfler) != 1 or len(proxyler) != 1:
            continue
        a, b = selfler[0], proxyler[0]
        hesap = v["hesaplar"].get(a["on_hizmet"], {})
        if (a["durum"] == b["durum"] == "0x0"
                and a["on_hizmet"] == b["on_hizmet"]
                and a["kullanici"] == b["kullanici"]
                and a["sira"] < b["sira"]
                and b.get("evidence_sira") == a["sira"]
                and hesap.get("spn") == a["hedef_spn"]):
            sonuc.append(kimlik)
    return sorted(sonuc)

print(zincirler(veri))
```

```hint
Önce akış kimliğine göre grupla; her iki aşamadan tam bir kayıt olmalı. Ardından kullanıcı/hizmet/sıra/kanıt bağlantısını ayrı ayrı karşılaştır.
```

```meta
motor: python
dil: python
```
:::
