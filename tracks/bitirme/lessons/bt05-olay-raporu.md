---
id: bt05
title: Yönetici Özeti ve Kanıta Bağlı Olay Raporu
summary: Gözlemi hipotezden ayır; doğrulanabilir referanslar ve ölçülü dil ile teknik raporu karar belgesine dönüştür.
---

::: anlat Raporun okuyucusu karar verecek
Yönetici özeti “hangi komutu çalıştırdık” günlüğü değildir. Vaka, kapsam, doğrulanan etki, belirsizlik, acil karar ve sorumluyu kısa anlatır. Teknik ekte sorgu/kural sürümleri, manifest hash'leri, UTC penceresi, kaynak/sensör kapsamı, ham kanıt referansları ve tekrar üretim adımları bulunur. Hesap ile insanı, etkilenen varlık ile inceleme adayını ayır.

Örnek ölçülü özet: “ws01/alice için 09:00–09:02 UTC aralığında üç başarısız giriş kaydı seçildi. Aynı cihazla ilişkilendirilen bakım betiği isteği ve daha sonra bir süreç kaydı inceleniyor. Yetkisiz kullanım, aynı dosyanın yürütülmesi ve veri sızması bu paketle doğrulanamadı. Olay sorumlusu bakım kaydını doğrulayacak ve uç nokta dosya/oturum kanıtlarını toplayacak.” 200 proxy gözleminden veri sızması, süreç isminden zararlı içerik türetilmez.

Observed = kaynakta doğrudan gördüğün alan; hypothesis = kanıtla uyumlu ama doğrulanmamış açıklama; unknown = eksik veri nedeniyle cevaplayamadığın soru. Referans mevcut olsa da iddiayı gerçekten destekliyor mu insan okumalıdır. Aşağıdaki testler **yapıyı ve referans bütünlüğünü** ölçer; Türkçe metnin doğruluğunu, özgünlüğünü veya yazarlık kalitesini ölçtüğü iddia edilmez. Nihai rapor için ders sonundaki insan incelemesi zorunlu kabul adımıdır. [NIST SP 800-61r3](https://csrc.nist.gov/pubs/sp/800/61/r3/final).
:::

::: tahmin
```python
refs={'endpoint:p-run'}
claim={'kind':'hypothesis','refs':['endpoint:p-run']}
print(set(claim['refs'])<=refs)
print(claim['kind']=='observed')
```

???
`True` ve `False`. Geçerli bir referans, hipotezi otomatik gözleme dönüştürmez.
:::

::: gorev İddia defterini doğrula
`defter(claims,available)` id→iddia sözlüğü döndürsün. Her id benzersiz/dolu, text strip sonrası dolu, kind observed/hypothesis/unknown. refs listesinde yalnız available kimlikleri; observed için en az bir ref zorunlu. Diğer iki tür boş ref taşıyabilir. Bozuk kayıt ValueError. Dönüşte her id için kind/text ve sıralı tekrarsız refs korunsun; metni yeniden yorumlama. available bu vaka için kaynak:id ve vaka.pcap#frame=N kanıt envanteridir.

```starter
def defter(claims,available):
    return {}
```

```test
refs={'auth:a-start','endpoint:p-run','vaka.pcap#frame=1'}
c=[{'id':'c1','kind':'observed','text':'Süreç kaydı görüldü','refs':['endpoint:p-run']*2},{'id':'c2','kind':'hypothesis','text':'Yetkili bakım olabilir','refs':[]},{'id':'c3','kind':'unknown','text':'Dosya özeti bilinmiyor','refs':[]}]
eq(defter(c,refs),{'c1':{'kind':'observed','text':'Süreç kaydı görüldü','refs':['endpoint:p-run']},'c2':{'kind':'hypothesis','text':'Yetkili bakım olabilir','refs':[]},'c3':{'kind':'unknown','text':'Dosya özeti bilinmiyor','refs':[]}},'kanıt ve belirsizlik ayrı')
base=c[0]
for change in ({'id':''},{'text':'  '},{'kind':'confirmed'},{'refs':[]},{'refs':['not-existing']}):
    raises(ValueError,lambda change=change:defter([dict(base,**change)],refs),msg='bozuk iddia')
raises(ValueError,lambda:defter([base,base],refs),msg='iki ayrı iddia aynı id taşımaz')
eq(defter([],refs),{},'boş defter; nihai rapor değil')
```

```solution
def defter(claims,available):
    result={}
    for c in claims:
        refs=set(c['refs'])
        if not c['id'] or c['id'] in result or not c['text'].strip() or c['kind'] not in ('observed','hypothesis','unknown') or not refs<=set(available) or (c['kind']=='observed' and not refs):
            raise ValueError('Geçersiz iddia')
        result[c['id']]={'kind':c['kind'],'text':c['text'],'refs':sorted(refs)}
    return result
```

```hint
Hipotezi reddetme; etiketini koru. Ref'in varlığı ile iddianın doğruluğunu birbirine karıştırma.
```
:::

::: gorev Veri kaybetmeden taşınabilir rapor eki üret
`rapor(v)` raporu UTF-8'e uygun JSON metni olarak döndürsün (ensure_ascii=False); geri okunduğunda girdi aynen korunmalı. Zorunlu alanlar: case, summary, scope, timeline, claims, limitations, recommendations, reproduction. Hepsi var ve truthy olmalı; boş bölüm ValueError. reproduction, queries/tool_versions/manifest_sha256 alt anahtarlarını dolu taşısın. Burada satırları Markdown'a gömmek yerine yapılandırılmış ek üretiyoruz; serbest metinde ham HTML/link yürütülmez. Girdiyi değiştirme.

```starter
def rapor(v):
    return '{}'
```

```test
import json,copy
v={'case':'PF-2026-102','summary':'İnceleme sürüyor','scope':['ws01','alice'],'timeline':[[0,'auth:a-start']],'claims':{'c1':{'kind':'observed','text':'giriş','refs':['auth:a-start']}},'limitations':['disk imajı yok'],'recommendations':[{'owner':'SOC','task':'bakım kaydını doğrula'}],'reproduction':{'queries':{'kql':'olaylar | project id'},'tool_versions':{'backend':'Pafta yerel'},'manifest_sha256':'a'*64}}
before=copy.deepcopy(v)
text=rapor(v)
eq(json.loads(text),v,'tüm içerik geri gelir')
ok('İnceleme' in text,'Türkçe metin kaçışsız taşınır')
eq(v,before,'girdi değiştirilmez')
for key in v:
    raises(ValueError,lambda key=key:rapor({k:x for k,x in v.items() if k!=key}),msg='eksik bölüm '+key)
    raises(ValueError,lambda key=key:rapor(dict(v,**{key:None})),msg='boş bölüm '+key)
for key in v['reproduction']:
    raises(ValueError,lambda key=key:rapor(dict(v,reproduction={k:x for k,x in v['reproduction'].items() if k!=key})),msg='yeniden üretim bilgisi eksik')
changed=dict(v,summary='Yeni kanıt; önceki yorum geri çekildi')
eq(json.loads(rapor(changed))['summary'],changed['summary'],'sabit rapor yazılmaz')
```

```solution
import json

def rapor(v):
    required=('case','summary','scope','timeline','claims','limitations','recommendations','reproduction')
    if any(not v.get(k) for k in required):raise ValueError('Eksik rapor bölümü')
    if any(not v['reproduction'].get(k) for k in ('queries','tool_versions','manifest_sha256')):raise ValueError('Eksik tekrar üretim bilgisi')
    return json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)
```

```hint
JSON eki dosya/kayıt referanslarını taşır; raporun insan tarafından okunması ve iddiaların doğrulanması ayrı iştir.
```
:::

::: anlat Kendi raporunu yaz · insan kabulü
BT04 çıktısını kullanarak yukarıdaki rapor nesnesini **kendi metninle doldur** ve `print(rapor(v))` ile tezgâhta üret; örnek nesneyi nihai teslim sayma. Yönetici özeti bir paragraf, ardından UTC çizelgesi, en az üç gözlem ve iki belirsizlik, tespit boşluğu, sorumlusu belli iki öneri yaz. Sorguların tamamını, kullandığın motorun gerçek sürümünü ve manifest.json dosyasının SHA256'sını reproduction alanına ekle. Otomatik başarı bu yazının tamamlandığını garanti etmez.

İnceleyen kişi şu soruları cevaplasın: Her gözlem ham kayda dönüyor mu? Başarılı auth ve HTTP isteği yetkisiz erişim sayılmış mı? Süreç/dosya bağının bilinmediği yazıyor mu? Kapsam ws01/alice dışına kanıtsız genişliyor mu? İki saniye hata bütçesi belirtilmiş mi? Öneri riski, hizmet etkisi ve sorumlusu belli mi? Aynı sorgu/veriyle sonuç yeniden üretilebiliyor mu? Paket yalnız istek içerirken yanıt görülmüş gibi anlatılmış mı? Bir soruda hata varsa metni düzeltip insan kabulünü tekrar al.
:::
