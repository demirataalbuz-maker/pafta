---
id: pu04
title: MISP · IOC Yaşam Döngüsü
summary: MISP özniteliklerini okumak; to_ids, silme, tür ve tazelik kararlarını olay kanıtından ayırmak.
---

::: anlat İstihbaratın birimi ve güven sınırı
Bir IOC dosya özeti, IP, alan adı veya başka bir gözlem olabilir. Bir IOC eşleşmesi olay incelemesi için başlangıçtır; tek başına saldırgan, zararlı dosya veya başarılı ihlal kanıtı değildir. IP'ler paylaşılır, domainler sahip değiştirir, hash yalnız aynı baytları tanır. Kaynak güvenilirliği, ilk/son görülme, bağlam ve geçerlilik kaydedilmeden listeyi engelleme politikasına çevirmek yanlış pozitif üretir.

MISP Event içinde Attribute listesi bulunabilir; bir öznitelik type/value/uuid/timestamp/to_ids/deleted alanları taşır. `to_ids` tespit kullanım niyetidir, kesin kötücüllük veya güven puanı değildir. `disable_correlation` korelasyonla ilgilidir; to_ids ile aynı kontrol değildir. `first_seen/last_seen` gözlem zamanlarıdır, timestamp ise özniteliğin kayıt güncelleme zamanıdır. MISP Objects içinde de Attribute bulunur; aşağıdaki görev yalnız Event.Attribute kesitini destekler. Üretimde Object, pagination, silme güncellemeleri, paylaşım yetkisi ve çekme konumu ayrıca ele alınır.

Ders verisi sentetik JSON kesitidir; MISP sunucusuna bağlanmaz. Bool alanlarda JSON bool ve API'nin 0/1 veya "0"/"1" gösterimleriyle karşılaşılabilir. `bool("0")` Python'da True olduğundan açık normalleştirme gerekir; başka bir gösterim hata olmalıdır. İndikatörü paylaşmadan önce dağıtım/TLP ve kaynak koşullarını değerlendir; bu ders bunlar için otomatik izin vermez.

[MISP core biçimi, proje tarafından yayımlanan çalışma taslağı](https://www.misp-standard.org/rfc/misp-standard-core.html), [resmî MISP API](https://www.misp-project.org/openapi/). Bu belge Internet-Draft'tır; IETF tarafından kesinleştirilmiş standart diye sunulmaz. Aşağıdaki TTL, Pafta'nın açık eğitim politikasıdır; MISP'in native decay puanlaması taklit edilmez.
:::

::: tahmin
```python
print(bool("0"))
print("0" in (True, 1, "1"))
```

???
`True` ve `False`. İlk dönüşüm kullanılmamalı; "0" aktif bayrak değildir.
:::

::: gorev Tespit kullanımına uygun öznitelikleri ayır
`sec(event)` Event.Attribute içindeki yalnız type domain/ip-dst/sha256, to_ids açık ve deleted kapalı kayıtların `(uuid,type,value)` üçlülerini uuid'ye göre sıralasın. UUID başına tek öznitelik varsayılır. Silme verilmemişse kapalı. Bool yalnız True/False, 1/0, "1"/"0"; diğerleri ValueError. Ham değeri değiştirme, nesne içi Attribute kapsam dışı.

```starter
def sec(event):
    return []
```

```test
def a(uid,typ='domain',value='x.test',ids=True,deleted=False): return {'uuid':uid,'type':typ,'value':value,'to_ids':ids,'deleted':deleted}
v={'Event':{'Attribute':[a('d',ids='0'),a('c',ids='1'),a('b',deleted='1'),a('a','ip-dst','192.0.2.1'),a('e','comment','note'),a('f','sha256','ab',ids=1)],'Object':[{'Attribute':[a('hidden')]}]}}
eq(sec(v),[('a','ip-dst','192.0.2.1'),('c','domain','x.test'),('f','sha256','ab')],'tür, silme ve to_ids ayrı')
eq(sec({'Event':{'Attribute':[dict(a('x'),deleted=0)]}}),[('x','domain','x.test')],'0 kapalı')
eq(sec({'Event':{}}),[],'Attribute yok')
raises(ValueError,lambda:sec({'Event':{'Attribute':[a('bad',ids='yes')]}}),msg='belirsiz bool hata')
```

```solution
def sec(event):
    def flag(v):
        if type(v) not in (bool,int,str) or v not in (True,False,0,1,'0','1'):
            raise ValueError('Beklenmeyen bool')
        return v in (True,1,'1')
    rows=[]
    for a in event['Event'].get('Attribute',[]):
        active=flag(a['to_ids'])
        deleted=flag(a.get('deleted',False))
        if a['type'] in ('domain','ip-dst','sha256') and active and not deleted:
            rows.append((a['uuid'],a['type'],a['value']))
    return sorted(rows)
```

```hint
Kayıt alanını doğru bağlamda oku; eksik kanıtı başarı veya güvenlik sayma. Görev sözleşmesindeki eşit uçları ayrıca kontrol et.
```
:::

::: gorev Tazelik kararını eşikte geri çek
`taze(a, now, ttl)` last_seen varsa ISO8601/offset zamanını UTC epoch saniyesine çevirsin; yoksa timestamp decimal epoch. Pafta politikası: ttl>0 ve seen<=now<seen+ttl. Gelecek kayıt, sıfır/negatif ttl veya bozuk zaman için False. Bu işlev to_ids/silme kontrolü yerine geçmez; önceki seçimden sonra uygulanır.

```starter
def taze(a, now, ttl):
    return True
```

```test
eq(taze({'timestamp':'100'},159,60),True,'sona ermeden bir saniye önce')
eq(taze({'timestamp':'100'},160,60),False,'tam sona erme artık geçersiz')
eq(taze({'timestamp':'100'},99,60),False,'gelecek gözlem')
eq(taze({'timestamp':'100'},100,60),True,'tam başlangıç')
eq(taze({'timestamp':'100'},100,0),False,'sıfır TTL')
eq(taze({'timestamp':'1','last_seen':'1970-01-01T01:01:40+01:00'},100,60),True,'offsetli son görülme timestamp üzerine geçer')
eq(taze({'timestamp':'100','last_seen':'bozuk'},100,60),False,'bozuk last_seen sessizce timestamp olmaz')
eq(taze({'last_seen':'1970-01-01T00:01:40'},100,60),False,'saat dilimi belirsiz')
```

```solution
from datetime import datetime

def taze(a, now, ttl):
    try:
        if 'last_seen' in a:
            dt=datetime.fromisoformat(a['last_seen'].replace('Z','+00:00'))
            if dt.tzinfo is None:return False
            seen=dt.timestamp()
        else:
            seen=int(a['timestamp'])
        return ttl>0 and seen<=now<seen+ttl
    except (ValueError,TypeError,KeyError):
        return False
```

```hint
Kayıt alanını doğru bağlamda oku; eksik kanıtı başarı veya güvenlik sayma. Görev sözleşmesindeki eşit uçları ayrıca kontrol et.
```
:::
