---
id: ht18
title: curl — TLS, CA ve Hostname
summary: Gerçek curl ile CA güveni, sertifika adı ve HTTP hata durumlarını birbirinden ayır.
---

::: anlat TCP bağlantısı kurulması güvenin kurulması değildir
`--resolve app.pafta.test:PORT:127.0.0.1` DNS sonucunu bu çağrı için değiştirir. URL'deki hostname TLS doğrulamasında kullanılmaya devam eder. `--cacert DOSYA` yalnız bu çağrıya bir CA verir; işletim sisteminin güven deposunu değiştirmez. `-k/--insecure` bu deneyin çözümü değildir.

`http_tls_lab.TLSLab` geçici bir CA ve yalnız `app.pafta.test` SAN'ı bulunan sertifika üretir; HTTPS gerçekten Python ssl ile taşınır. Windows'ta mevcut cryptography ve curl.exe, Kali'de cryptography ve curl gerekir. Eksik paket otomatik kurulmaz. Schannel için yardımcı yalnız bu çağrıda `--ssl-no-revoke` kullanır: geçici CA'nın CRL hizmeti yoktur; CA imzası ve hostname denetimi sürer. Bu revocation deneyi değildir.

curl'ün çıkış kodu ile HTTP kodu ayrı kanıttır. Normal curl için HTTP 404, aktarım başarılıysa çıkış 0 olabilir. `--fail-with-body` aynı HTTP yanıtını çıkış 22 yapar. Sertifika doğrulama hatasında tipik çıkış 60'tır; bir HTTP yanıtı oluşmaz. stderr metni TLS arka ucuna göre değişir; metni sabitleyerek karar verme.

Kaynaklar: [curl sertifika doğrulaması](https://curl.se/docs/sslcerts.html), [curl seçenekleri](https://curl.se/docs/manpage.html#--fail-with-body), [--resolve](https://curl.se/docs/manpage.html#--resolve).
:::

::: tahmin
```python
from http_tls_lab import TLSLab
with TLSLab() as lab:
    for opts in ({}, {'trust':False}, {'hostname':'other.pafta.test'}, {'path':'/missing'}, {'path':'/missing','fail_http':True}):
        r=lab.curl(**opts)
        print(r['exit'],r['http'])
```
???
`0 200`, `60 0`, `60 0`, `0 404`, `22 404`. Yanlış hostname deneyi doğru CA'yı kullanır; iki farklı hata nedenini birbirine karıştırmayız.
:::

::: gorev Güvenli curl çağrısını kur
`curl_argv(exe, ca, host, port, path)` argv listesi döndürsün. Sıra: exe, `--disable`, `--silent`, `--show-error`, `--noproxy`, `*`, `--max-time`, `4`, `--cacert`, ca, `--resolve`, `host:port:127.0.0.1`, `--write-out`, `\n%{http_code}`, URL. URL `https://host:port/path` biçimindedir. Bu görevde host yalnız `app.pafta.test` veya yanlış-ad deneyi için `other.pafta.test`; port bool olmayan int ve 1..65535; path `/` ile başlamalı, `//` ile başlamamalı, ASCII olmalı, boşluk/kontrol veya `#` içermemeli. İhlalde ValueError. Kabuk komut dizgesi üretme.
```starter
def curl_argv(exe, ca, host, port, path):
    return []
```
```test
import shutil, subprocess
from http_tls_lab import TLSLab
exe=shutil.which('curl.exe') or shutil.which('curl')
for p in (1,65535):
    a=curl_argv(exe,'ca file.pem','app.pafta.test',p,'/x?q=%20')
    eq(a,[exe,'--disable','--silent','--show-error','--noproxy','*','--max-time','4','--cacert','ca file.pem','--resolve',f'app.pafta.test:{p}:127.0.0.1','--write-out','\n%{http_code}',f'https://app.pafta.test:{p}/x?q=%20'],'argv ve sinir portu')
for host,p,path in [('bad.test',80,'/'),('app.pafta.test',0,'/'),('app.pafta.test',65536,'/'),('app.pafta.test',True,'/'),('app.pafta.test',1,'//bad'),('app.pafta.test',1,'/a b'),('app.pafta.test',1,'/a\tb'),('app.pafta.test',1,'/a#b'),('app.pafta.test',1,'/\u011f')]:
    try: curl_argv(exe,'ca',host,p,path)
    except ValueError: pass
    else: ok(False,'gecersiz hedef')
with TLSLab() as lab:
    for host,expected in [('app.pafta.test',0),('other.pafta.test',60)]:
        argv=curl_argv(exe,lab.ca,host,lab.server.server_port,'/missing')
        if 'Schannel' in subprocess.run([exe,'--version'],capture_output=True,text=True).stdout:
            argv.insert(1,'--ssl-no-revoke')
        r=subprocess.run(argv,capture_output=True,text=True,timeout=8)
        eq(r.returncode,expected,'gercek curl TLS sonucu')
        eq(r.stdout.rsplit('\n',1)[-1],'404' if expected==0 else '000','HTTP var/yok')
```
```solution
def curl_argv(exe, ca, host, port, path):
    if host not in ('app.pafta.test','other.pafta.test') or type(port) is not int or not 1<=port<=65535:
        raise ValueError('host/port')
    if not isinstance(path,str) or not path.startswith('/') or path.startswith('//') or '#' in path or any(ord(c)<=32 or ord(c)>=127 for c in path):
        raise ValueError('path')
    return [exe,'--disable','--silent','--show-error','--noproxy','*','--max-time','4','--cacert',ca,'--resolve',f'{host}:{port}:127.0.0.1','--write-out','\n%{http_code}',f'https://{host}:{port}{path}']
```
```hint
Host başlığı eklemek sertifikanın adına yönelik bir deney değildir. URL'deki adı değiştir, --resolve ile aynı loopback'e bağla.
```
:::

::: gorev HTTP hatasını TLS hatasından ayır
`sinifla(exit_code, http_code)` aşağıdaki sözleşmeyle metin döndürsün. bool olmayan int değerler kabul edilir; exit negatif olamaz, http 0 veya 100..599 olmalı; aksi ValueError. exit 60 ve http 0 → `sertifika`; exit 0 ve http 100..399 → `basarili`; exit 0 veya 22 ve http 400..599 → `http-hatasi`; exit başka pozitif ve http 0 → `tasima`; kalan birleşimler → `tutarsiz`. Bu dar curl rapor sözleşmesidir; her TLS hatasının 60 olduğunu iddia etmez.
```starter
def sinifla(exit_code, http_code):
    return 'basarili'
```
```test
for x,h,e in [(60,0,'sertifika'),(35,0,'tasima'),(7,0,'tasima'),(28,0,'tasima'),(0,100,'basarili'),(0,399,'basarili'),(0,400,'http-hatasi'),(0,599,'http-hatasi'),(22,400,'http-hatasi'),(22,599,'http-hatasi'),(0,0,'tutarsiz'),(22,200,'tutarsiz'),(60,200,'tutarsiz'),(35,500,'tutarsiz')]:
    eq(sinifla(x,h),e,'cikis/HTTP bagimsizligi')
for x,h in [(-1,0),(0,99),(0,600),(True,200),(0,False),(0,'200')]:
    try: sinifla(x,h)
    except ValueError: pass
    else: ok(False,'rapor araligi')
from http_tls_lab import TLSLab
with TLSLab() as lab:
    for opts,e in [({},'basarili'),({'trust':False},'sertifika'),({'hostname':'other.pafta.test'},'sertifika'),({'path':'/missing'},'http-hatasi'),({'path':'/missing','fail_http':True},'http-hatasi')]:
        r=lab.curl(**opts); eq(sinifla(r['exit'],r['http']),e,'gercek TLS raporu')
```
```solution
def sinifla(exit_code, http_code):
    if type(exit_code) is not int or type(http_code) is not int or exit_code<0 or not (http_code==0 or 100<=http_code<=599):
        raise ValueError('rapor')
    if exit_code==60 and http_code==0: return 'sertifika'
    if exit_code==0 and 100<=http_code<=399: return 'basarili'
    if exit_code in (0,22) and 400<=http_code<=599: return 'http-hatasi'
    if exit_code>0 and http_code==0: return 'tasima'
    return 'tutarsiz'
```
```hint
399/400 ve 599/600 sınırlarını ayır. HTTP 000 curl'ün bir HTTP yanıtı almadığını gösteren rapor değeridir.
```
:::
