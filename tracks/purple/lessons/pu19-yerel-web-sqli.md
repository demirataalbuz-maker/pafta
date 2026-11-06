---
id: pu19
title: Yerel Web SQLi · Gerçek HTTP, Bypass ve Parameter Binding
summary: İzole stdlib HTTP + SQLite uygulamasında login bypass, ham istek dosyaları, parameter binding, normal iş kontrolü ve gerçek DB audit kanıtı.
timeout: 30
---

::: anlat Aynı girdi neden iki endpoint'te farklı çalışır?
Bu ders klasik web ve Purple M2 kapsamının SQLi alt işidir. pu11'deki savunma bilgisini, açık endpoint ile korumalı endpoint üzerinde gerçek HTTP ve SQLite karşılaştırmasına taşır. XSS, SSTI, XXE, Juice Shop, blind/time-based/UNION SQLi ve M2 bütünü bu dersle tamamlanmış değildir.

Setup `yerel_sqli/istekler.json`, `istek.http`, `sorgular.sql`, `README.md` dosyalarını geçici çalışma klasörüne kopyalar. Bunlar sentetik fixture'dır; gerçek sunucu kaydı değildir. Çalıştır'da `Path('yerel_sqli/istek.http').read_text(encoding='utf-8')` ile ham isteği gör. Aynı çalıştırmada dosyayı değiştirerek dene. Bir sonraki Çalıştır yeni geçici kopyadır; kalıcı dosya editörü yoktur. Son görev gerçek yanıtları üretir; örnek dosya sonucun yerine geçmez.

`/vulnerable/login` değerleri SQL metnine birleştirir. `' OR 1=1 -- ` eğitim girdisi yalnız kendi sentetik DB'sinde yanlış parola kontrolünü aşar; yetkisiz canary görülür. `/secure/login` aynı metni `?` parametresi olarak bağlar. Değerin içindeki SQL yazısı veri olarak kalır. Tırnak silmek, `OR` kelimesini yasaklamak veya yalnız arayüzde filtrelemek parameter binding değildir.
:::

::: gorev 1 · Gerçek SQLite sorgusunu parametrele
`guvenli_sorgu(db,u,p)` verilen SQLite bağlantısında `accounts(username,password,canary)` tablosundan tam kullanıcı/parola eşleşmesinin `(username,canary)` satırını, eşleşme yoksa None döndürsün. SQL değerlerini `?` ile bağla; `execute(...).fetchone()` kullan. Meşru kullanıcıda tırnak, parolada noktalı virgül ve `--` olabilir. Tabloyu değiştirme.

```starter
def guvenli_sorgu(db,u,p):
    return None
```

```solution
def guvenli_sorgu(db,u,p):
    return db.execute("SELECT username, canary FROM accounts WHERE username = ? AND password = ?",(u,p)).fetchone()

from pathlib import Path
print(Path("yerel_sqli/sorgular.sql").read_text(encoding="utf-8"))
```

```test
need('guvenli_sorgu')
import sqlite3,secrets
db=sqlite3.connect(':memory:')
try:
    db.execute('CREATE TABLE accounts(username TEXT,password TEXT,canary TEXT)')
    u="O'Reilly_"+secrets.token_hex(4);p='nokta;--';c=secrets.token_hex(8)
    db.execute('INSERT INTO accounts VALUES(?,?,?)',(u,p,c))
    eq(guvenli_sorgu(db,u,p),(u,c),'SQL karakterli meşru girdi korunur')
    eq(guvenli_sorgu(db,u,'yanlis'),None,'yanlış parola ret')
    for a in ("' OR 1=1 -- ","x' OR 'a'='a' -- "):
        eq(guvenli_sorgu(db,a,'yanlis'),None,'bypass parameter binding ile yok')
    eq(db.execute('SELECT COUNT(*) FROM accounts').fetchone()[0],1,'tablo korunur')
finally:db.close()
```

```setup
import sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_sqli_lab import hazirla
hazirla()
```

```hint
Veriyi SQL metnine ekleme; `?` ve tuple kullan. Son görevde yanıtları lab.post üzerinden gerçek çağrıdan al.
```
:::

::: anlat Hata vitrini · 500, 401 ve 200 aynı bulgu değildir
Tek tırnakla bozuk SQL üretmek 500 verir; bu başarılı login bypass değildir. Yanlış parola 401 verir; bu tek başına parameter binding kanıtı değildir. Başarılı saldırı karşılaştırması, açık endpoint'te yanlış parolayla 200 ve sentetik canary, korumalı endpoint'te aynı girdiye 401, doğru parolaya 200 gerektirir. SQL benzeri karakterleri olan meşru hesap da çalışmalıdır. HTTP response ile DB audit ayrı kaynaktan karşılaştırılır; çıktı sözlüğü uydurmak kabul edilmez.

Blue karşılığı: uygulama audit'i route, girdi, HTTP status, SQL metni ve bound parameters kaydeder. Buradaki parolalar tamamen sentetiktir; üretim sisteminde parola loglamak doğru tasarım değildir. SQL hatası artışı araştırma ipucudur, her 500 saldırı değildir. Bu çalışma WAF/SIEM entegrasyonu veya production auth tasarımı yerine geçmez.
:::

::: gorev 2 · Gerçek HTTP ve DB etkisini birlikte ölç
Önceki `guvenli_sorgu` fonksiyonunu ekle. `dene(lab,normal,saldiri)` beş gerçek yanıtı sırayla liste döndürsün:

1. `/vulnerable/login` normal girdi.
2. `/secure/login` aynı normal girdi.
3. `/vulnerable/login` saldırı girdisi.
4. `/secure/login` aynı saldırı girdisi.
5. `/vulnerable/login` için `{'username':"'",'password':'yanlis'}` bozuk SQL girdisi.

`lab.post(route,data)` gerçek localhost HTTP isteği yapar ve `{'status':int,'body':dict}` döndürür. Normal hesap her koşuda değişir. Yanıtı sabitleme; 500 bu laboratuvarda beklenen bozuk SQL kontrolüdür, transport hatası beklenen sonuç sayılmaz. Alttaki calistir satırı gerçek deneyi başlatır; silme. Run deneme kanıtı yazar, Check ayrıca kabul kanıtını yazar. Sürüm, cihaz, ham audit, öğrenci yanıtları, DB hash ve cleanup dosyası yolu stdout'ta görünür.

Her koşu kendi 127.0.0.1 dinleyicisini ve geçici DB'sini açar, yalnız bunları kapatır. Kullanıcı verisi/başka süreç yoktur; paket/model indirilmez. Gerçek hesaplar veya dış hedefler kullanılmaz. Bu laboratuvarda yazma etkisi, DB'de saklanan audit kayıtlarıdır; veri silme/exfiltration deneyi değildir.

```starter
def guvenli_sorgu(db,u,p):return None
def dene(lab,normal,saldiri):return []
```

```solution
def guvenli_sorgu(db,u,p):
    return db.execute("SELECT username, canary FROM accounts WHERE username = ? AND password = ?",(u,p)).fetchone()

def dene(lab,normal,saldiri):
    return [lab.post('/vulnerable/login',normal),
            lab.post('/secure/login',normal),
            lab.post('/vulnerable/login',saldiri),
            lab.post('/secure/login',saldiri),
            lab.post('/vulnerable/login',{'username':"'",'password':'yanlis'})]

from purple_sqli_lab import calistir
calistir(guvenli_sorgu,dene)
```

```test
need('guvenli_sorgu');need('dene')
from purple_sqli_lab import kod_koruma,calistir
ok(kod_koruma(src),'kaynak koruması: oracle/audit/introspection kopyası yok')
if not kod_koruma(src):stop()
need('guvenli_sorgu')
import sqlite3,secrets
db=sqlite3.connect(':memory:')
try:
    db.execute('CREATE TABLE accounts(username TEXT,password TEXT,canary TEXT)')
    u="O'Reilly_"+secrets.token_hex(4);p='nokta;--';c=secrets.token_hex(8)
    db.execute('INSERT INTO accounts VALUES(?,?,?)',(u,p,c))
    eq(guvenli_sorgu(db,u,p),(u,c),'SQL karakterli meşru girdi korunur')
    eq(guvenli_sorgu(db,u,'yanlis'),None,'yanlış parola ret')
    for a in ("' OR 1=1 -- ","x' OR 'a'='a' -- "):
        eq(guvenli_sorgu(db,a,'yanlis'),None,'bypass parameter binding ile yok')
    eq(db.execute('SELECT COUNT(*) FROM accounts').fetchone()[0],1,'tablo korunur')
finally:db.close()

for i in range(2):
    k=calistir(guvenli_sorgu,dene,kabul=True)
    eq(k['kaynak'],'gercek','gerçek HTTP ve SQLite')
    ok(k['kabul'],'gerçek kabul; fixture sayılmaz')
    ok(k['cleanup'],'yalnız kendi HTTP/DB kaynakları kapandı')
```

```setup
import sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_sqli_lab import hazirla
hazirla()
```

```hint
Veriyi SQL metnine ekleme; `?` ve tuple kullan. Son görevde yanıtları lab.post üzerinden gerçek çağrıdan al.
```
:::
