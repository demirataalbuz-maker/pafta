---
id: bt01
title: Bitirme · Kanıtı Kabul Et ve Zamanı Sabitle
summary: Aynı vaka paketinde bütünlük, kaynak kimliği, saat dilimi ve tekrarlanan kayıt sorunlarını çöz.
---

::: anlat Vaka PF-2026-102
SOC, ws01 üzerinde alice hesabının başarısız girişlerinden sonra başarılı bir giriş ve bir PowerShell süreç gözlemi gördü. Bakım betiğinin çalıştırılması yetkili olabilir; otomatik olarak ihlal ilan etme. Görevin hazır kanıtları inceleyip doğrulananları ve bilinmeyenleri ayırmak. Saldırı yürütmeyeceksin.

Her çalıştırmada geçici klasöre aynı dört dosya gelir. `olaylar.jsonl` auth/endpoint/proxy kaynaklarının **Pafta tarafından normalize edilmiş sentetik** kayıtlarıdır; Windows Event XML veya EDR ürün şeması değildir. `ts`, vaka başlangıcından itibaren tam saniyedir, epoch değildir. Başlangıç `vaka.json` içindeki `2026-10-26T09:00:00Z`; saat hata bütçesi iki saniyedir. Host/IP envanteri yalnız bu vaka anı için verilmiştir. `vaka.pcap` dört sentetik HTTP isteğidir. `manifest.json` diğer üç dosyanın SHA256 değeridir.

`import vaka_lab as v` ile `v.yukle()` olayları okur. KQL burada **Kusto** dilidir. KQL/SPL mevcut Pafta çeviricileriyle SQLite üzerinde çalışır; gerçek Sentinel veya Splunk sunucusu değildir. Sigma gerçek pySigma ayrıştırıcısı ve mevcut yerel olay backend'ini kullanır; ürün pipeline/routing simüle edilmez. PCAP filtresi ise gerçek TShark `-r/-Y` üzerinde yürür. Desteklenmeyen sorgu hata verir; başka motora sessiz geçiş yoktur. Python/SQL/KQL/SPL/Sigma/paket yollarını bitirmiş olman beklenir.

Bir hash eşitliği eldeki dosyanın referansla aynı olduğunu gösterir; referansın güvenilirliğini veya kaydın gerçeği anlattığını kanıtlamaz. Üretimde orijinal dosya, toplama saati/sahibi, erişim zinciri, bağımsız saklanan manifest ve sorgu sürümü de korunur. Bu eğitim paketi imzalı adli delil değildir. [Python hashlib](https://docs.python.org/3/library/hashlib.html), [NIST olay müdahalesi rehberi](https://csrc.nist.gov/pubs/sp/800/61/r3/final).
:::

::: tahmin
```python
from datetime import datetime
a=datetime.fromisoformat('2026-10-26T12:00:00+03:00')
b=datetime.fromisoformat('2026-10-26T09:00:00+00:00')
print(a==b)
print(a.isoformat()==b.isoformat())
```

???
`True` ve `False`. Aynı anı yazan iki metin farklı olabilir. Metni sıralamak yerine saat dilimli zamanı kullan.
:::

::: gorev Manifesti bütün dosya kümesiyle karşılaştır
`butunluk(manifest, files)` yalnız manifest boş değilse, dosya adları tam aynıysa ve her dosyanın SHA256 hex değeri manifestle eşitse True döndürsün. files değerleri bytes; manifest değerleri küçük harf hex. Boş paket başarı değildir; ekstra veya eksik dosyayı görmezden gelme.

```starter
def butunluk(manifest, files):
    return True
```

```test
import hashlib,json
from pathlib import Path
files={n:Path(n).read_bytes() for n in ('olaylar.jsonl','vaka.pcap','vaka.json')}
m=json.loads(Path('manifest.json').read_text(encoding='utf-8'))
eq(butunluk(m,files),True,'teslim paketi aynı')
eq(butunluk(m,dict(files,**{'vaka.pcap':files['vaka.pcap']+b'X'})),False,'tek bayt değişiklik')
eq(butunluk(m,{k:v for k,v in files.items() if k!='vaka.json'}),False,'eksik dosya')
eq(butunluk(m,dict(files,extra=b'x')),False,'ek dosya')
eq(butunluk({},{}),False,'boş küme geçmez')
eq(butunluk({'x':hashlib.sha256(b'').hexdigest()},{'x':b''}),True,'boş dosya ile boş paket farklı')
```

```solution
import hashlib

def butunluk(manifest,files):
    return bool(manifest) and set(manifest)==set(files) and all(hashlib.sha256(files[n]).hexdigest()==digest for n,digest in manifest.items())
```

```hint
Önce dosya kümesini, sonra her dosyanın baytlarını doğrula. all([]) True olduğundan boş manifesti ayrıca ele al.
```
:::

::: gorev Kaynak kimliğiyle tek UTC zaman çizelgesi
`cizelge(rows,base)` `(utc_iso,source:id,host,user)` satırlarını zaman sonra kanıt kimliğiyle sıralasın. base offsetli ISO; ts tam int (bool değil), host/user küçük harf. Aynı source:id ve aynı ham kayıt tek sayılır; aynı kimlik farklı kayıt ValueError. Başlangıçtan önceki kayıt kaybolmasın. Negatif saniye geçerli geçmiş kayıttır; metin veya bool ts reddedilir.

```starter
def cizelge(rows, base):
    return []
```

```test
r={'id':'x','source':'auth','ts':0,'host':'WS01','user':'Alice'}
eq(cizelge([r,r,dict(r,id='before',ts=-1)],'2026-10-26T12:00:00+03:00'),[('2026-10-26T08:59:59+00:00','auth:before','ws01','alice'),('2026-10-26T09:00:00+00:00','auth:x','ws01','alice')],'UTC ve eşit başlangıç, tekrar')
eq(len(cizelge([r,dict(r,source='endpoint')],'2026-10-26T09:00:00Z')),2,'iki kaynakta aynı id ayrı kanıt')
raises(ValueError,lambda:cizelge([r,dict(r,ts=1)],'2026-10-26T09:00:00Z'),msg='kimlik çakışması')
raises(ValueError,lambda:cizelge([r],'2026-10-26T09:00:00'),msg='saat dilimi zorunlu')
for t in ('0',False):
    raises(ValueError,lambda t=t:cizelge([dict(r,ts=t)],'2026-10-26T09:00:00Z'),msg='saniye türü')
eq(cizelge([],'2026-10-26T09:00:00Z'),[],'boş kayıt')
```

```solution
from datetime import datetime,timedelta,timezone

def cizelge(rows,base):
    start=datetime.fromisoformat(base.replace('Z','+00:00'))
    if start.tzinfo is None:raise ValueError('Saat dilimi yok')
    seen={}
    for r in rows:
        if type(r['ts']) is not int:raise ValueError('Tam saniye zorunlu')
        key=r['source']+':'+r['id']
        if key in seen and seen[key]!=r:raise ValueError('Kimlik çakışması')
        seen[key]=r
    return sorted(((start+timedelta(seconds=r['ts'])).astimezone(timezone.utc).isoformat(),key,r['host'].lower(),r['user'].lower()) for key,r in seen.items())
```

```hint
Kaynak ve id birlikte kimliktir. Saat dönüşümü metin üretmeden önce yapılır.
```
:::
