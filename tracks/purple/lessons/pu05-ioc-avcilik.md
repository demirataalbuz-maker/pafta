---
id: pu05
title: IOC'den Avcılık Sorgusuna
summary: Alan normalleştirme ve tam eşleşme ile gerçek SQLite avcılığı; süre penceresi, parametre bağlama ve bağlamlı sonuç.
---

::: anlat Listeyi sorguya çevirmek
PU04'te seçilen IOC'ler sorgunun girdisidir. Bir domain IOC'si bütün alt alan adlarını veya URL metnindeki her benzer parçayı otomatik eşleştirmez. Bu dersin açık politikası: DNS adı küçük harfe çevrilir, sondaki nokta atılır; alt alanlar ayrı kalır. IPv4/IPv6 adresleri `ipaddress.ip_address` ile kanonikleştirilir. SHA256 64 hex karakter ister ve küçük harfe çevrilir. MD5 veya URL, SHA256/domain diye zorlanmaz. Geçersiz değer hatadır.

Aşağıdaki tezgah gerçek SQLite ile çalışır. Bu bir MISP/Splunk/Kusto simülatörü değildir. Öğrenci sorguyu Python'dan parametrik çalıştırır; IOC'yi SQL metnine eklemez. Girdi olaylarında id/ts/kind/value alanları Pafta'nın normalize **sentetik** gözlem şemasıdır; bulut ürünlerinin ham alanları değildir. IOC'ler PU04 politikaları uygulanmış tür/değer çiftleridir. Zaman penceresi [başlangıç, bitiş) olarak açıkça belirlenir; aynı olay birden çok aynı IOC yüzünden tekrar raporlanmaz.

Bir eşleşmeyi kaydederken olay id'sini, sensörü, ham değeri, sorgu sürümünü ve IOC kaynağını koru. Sonuç sayısını makine/hesap sayısı veya kesin ihlal sayısı diye sunma. Kaydın olmaması sensör kapsamı ve saklama süresi incelenmeden “temiz” anlamına gelmez. Kaynak: [Python sqlite3 parametre bağlama](https://docs.python.org/3/library/sqlite3.html#how-to-use-placeholders-to-bind-values-in-sql-queries), [ipaddress](https://docs.python.org/3/library/ipaddress.html), [MISP formatı](https://www.misp-standard.org/rfc/misp-standard-core.html).
:::

::: tahmin
```python
import sqlite3
with sqlite3.connect(':memory:') as db:
    print(db.execute('SELECT ? = ?', ('x.test', 'sub.x.test')).fetchone()[0])
```

???
`0`. SQL tam eşitliği otomatik alt alan kapsamı üretmez.
:::

::: gorev Türü kaybetmeden IOC'yi normalleştir
`normal(tip,value)` domain için strip/lower ve yalnız sondaki noktaları kaldırır; boş domain ValueError. ip-dst için ipaddress kanonik metin; sha256 tam 64 hex. Diğer tip ValueError. Bu domain işlevi IDNA veya genel DNS doğrulayıcısı değildir.

```starter
def normal(tip, value):
    return value.lower()
```

```test
eq(normal('domain',' X.Test. '),'x.test','harf, boşluk, son nokta')
eq(normal('domain','sub.x.test'),'sub.x.test','alt alanı üst alanla birleştirme')
eq(normal('ip-dst','2001:0db8::1'),'2001:db8::1','IPv6 kanonik')
eq(normal('sha256','A'*64),'a'*64,'hash harf farkı')
for typ,v in [('sha256','a'*63),('sha256','a'*65),('sha256','g'*64),('domain','.'),('ip-dst','999.1.1.1'),('url','https://x.test')]:
    raises(ValueError,lambda typ=typ,v=v:normal(typ,v),msg='yanlış tür veya sınır')
```

```solution
import ipaddress
import re

def normal(tip,value):
    if tip=='domain':
        result=value.strip().lower().rstrip('.')
        if not result:raise ValueError('Boş domain')
        return result
    if tip=='ip-dst':return str(ipaddress.ip_address(value))
    if tip=='sha256' and re.fullmatch('[0-9a-fA-F]{64}',value):return value.lower()
    raise ValueError('Desteklenmeyen veya geçersiz IOC')
```

```hint
Kayıt alanını doğru bağlamda oku; eksik kanıtı başarı veya güvenlik sayma. Görev sözleşmesindeki eşit uçları ayrıca kontrol et.
```
:::

::: gorev Gerçek sorguyu bağlanmış parametrelerle çalıştır
`av(events, iocs, bas, son)` zaten normalleştirilmiş olayları ve IOC çiftlerini bellek içi SQLite'a koysun; kind/value tam eşleşmesi ve bas<=ts<son için id'leri tekrarsız, sıralı döndürsün. IOC veya zamanları SQL metnine ekleme; tablo listeleri executemany ile doldurulsun. Bu görev giriş doğrulamasını önceki işleve bırakır.

```starter
def av(events, iocs, bas, son):
    return []
```

```test
e=[('a',100,'domain','x.test'),('b',159,'domain','x.test'),('c',160,'domain','x.test'),('d',99,'domain','x.test'),('e',110,'domain','sub.x.test'),('f',110,'ip-dst','x.test'),('g',110,'domain',"x' OR 1=1 --")]
eq(av(e,[('domain','x.test')]*2,100,160),['a','b'],'iki sınır, aynı tür ve tekrar')
eq(av(e,[('domain',"x' OR 1=1 --")],100,160),['g'],'tırnak SQL değil veridir')
eq(av(e,[],100,160),[],'boş IOC')
eq(av(e,[('domain','x.test')],100,100),[],'boş pencere')
ok(calls('execute') and calls('executemany'),'gerçek SQLite API kullan')
```

```solution
import sqlite3

def av(events,iocs,bas,son):
    with sqlite3.connect(':memory:') as db:
        db.execute('CREATE TABLE olay(id TEXT, ts INTEGER, kind TEXT, value TEXT)')
        db.execute('CREATE TABLE ioc(kind TEXT, value TEXT)')
        db.executemany('INSERT INTO olay VALUES(?,?,?,?)',events)
        db.executemany('INSERT INTO ioc VALUES(?,?)',iocs)
        return [r[0] for r in db.execute('SELECT DISTINCT o.id FROM olay o JOIN ioc i ON o.kind=i.kind AND o.value=i.value WHERE o.ts>=? AND o.ts<? ORDER BY o.id',(bas,son))]
```

```hint
Kayıt alanını doğru bağlamda oku; eksik kanıtı başarı veya güvenlik sayma. Görev sözleşmesindeki eşit uçları ayrıca kontrol et.
```
:::
