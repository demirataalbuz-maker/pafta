---
id: ht19
title: Gerçek Tarayıcıda CORS ve Preflight
summary: İsteğin gönderilmesini JavaScript'in yanıtı okuyabilmesinden ağ kayıtlarıyla ayır.
timeout: 60
---

::: anlat Origin, site ve ağ kaydı
Origin şema + hostname + porttur. Bu derste iki loopback portu iki **origin** oluşturur. Bunlar farklı **site** değildir; SameSite deneyini sonraki derste farklı alan adlarıyla yapacağız.

`http_browser_lab.cors_report()` kurulu Edge/Chromium'u gerçek Playwright ile açar. CORS'u Python koşullu ifadeleriyle taklit etmez. Beş deney sırayla yapılır:

| No | İstek | Beklenen gözlem |
|---|---|---|
| 0 | İzinli origin, GET | GET gider, JS yanıtı okur |
| 1 | İzinli origin, JSON POST + X-Pafta, credentials include | OPTIONS ve POST gider, JS okur |
| 2 | İzin verilmeyen origin, X-Pafta POST | OPTIONS reddedilir, POST gönderilmez |
| 3 | İzin verilmeyen origin, basit GET | GET gider; JS yanıtı okuyamaz |
| 4 | Ayrı hedefte ACAO `*`, credentials include | GET gider; wildcard credentialed okumaya izin vermez |

Rapor `results`, `target_events`, `wildcard_events` içerir. Bunlar gerçek tarayıcı sonucu ile sunucunun aldığı isteklerdir. JS TypeError tek başına sunucuda işlem yapılmadığının kanıtı değildir. CORS erişim yetkilendirmesi veya genel CSRF savunması değildir. Tarayıcı CORS uygular; curl/Python istemcilerinin aynı yanıtı okuyabilmesi CORS açığı kanıtlamaz.

Tarayıcıya `--disable-web-security` verilmez. Gereksinimler ve elle Network paneliyle tekrar için [laboratuvar rehberi](../../../docs/http-lab.md). Kaynak: [Fetch CORS protokolü ve credential tablosu](https://fetch.spec.whatwg.org/#http-cors-protocol).
:::

::: tahmin
```python
from http_browser_lab import cors_report
r=cors_report()
print([x['readable'] for x in r['results']])
print([x['method'] for x in r['target_events'] if x['path']=='/cors'])
```
???
`[True, True, False, False, False]` ve `['GET', 'OPTIONS', 'POST', 'OPTIONS', 'GET']`. İkinci OPTIONS'un ardından POST yoktur; reddedilen basit GET ise sunucuya ulaşır. Başka tarayıcı sürümünde farklı sonuç varsa çıktıyı gizleme; gereksinimi ve politikayı incele.
:::

::: gorev Gerçek tarayıcı raporundan ağ özeti çıkar
`cors_ozet(rapor)` sözlük döndürsün: `okunabilen` gerçek results indekslerinin listesi; `options`, `post`, `get` yalnız target_events içinde path'i `/cors` olan yöntemlerin sayıları; `wildcard_get` aynı şekilde wildcard_events GET sayısı. Sabit beklenen çıktıyı yazma. Olay sırasını veya ilgisiz yolları sayı sanma.
```starter
def cors_ozet(rapor):
    return {}
```
```test
from http_browser_lab import cors_report
r=cors_report()
eq(cors_ozet(r),{'okunabilen':[0,1],'options':2,'post':1,'get':2,'wildcard_get':1},'gercek browser/ag tanigi')
for readable in ([],[False],[True],[False,True,False,True]):
    for method in ('OPTIONS','GET','POST','PATCH'):
        fake={'results':[{'readable':v} for v in readable], 'target_events':[{'path':'/cors','method':method},{'path':'/cors-baska','method':method}], 'wildcard_events':[]}
        eq(cors_ozet(fake),{'okunabilen':[i for i,v in enumerate(readable) if v],'options':int(method=='OPTIONS'),'post':int(method=='POST'),'get':int(method=='GET'),'wildcard_get':0},'raporu gercekten oku; 0/1 sinirlari')
```
```solution
def cors_ozet(rapor):
    events=[e for e in rapor['target_events'] if e['path']=='/cors']
    return {'okunabilen':[i for i,r in enumerate(rapor['results']) if r['readable']],
            'options':sum(e['method']=='OPTIONS' for e in events),
            'post':sum(e['method']=='POST' for e in events),
            'get':sum(e['method']=='GET' for e in events),
            'wildcard_get':sum(e['path']=='/cors' and e['method']=='GET' for e in rapor['wildcard_events'])}
```
```hint
results JS'in gördüğüdür; events sunucunun aldığıdır. İkisini farklı alanlardan hesapla.
```
:::
