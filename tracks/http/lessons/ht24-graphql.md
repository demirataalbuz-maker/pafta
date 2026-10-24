---
id: ht24
title: GraphQL — Şema, Değişkenler ve Alan Yetkisi
summary: Gerçek graphql-core ile query/mutation/introspection oku; HTTP 200 içindeki kısmi veri ve errors alanını koru.
---

::: anlat Tek URL, farklı alan izinleri
Bu ders regex ile sorgu tanımaz; `.deps` içindeki **graphql-core 3.3.0** sorguyu ayrıştırır, şemaya göre doğrular ve resolver'ları çalıştırır. Eksikse açık 503 hata verir; otomatik indirme yapmaz. Kullanıcı onayıyla `python -m pip install --target .deps --no-deps -r requirements-http.txt` kurulabilir.

POST /graphql JSON alanları query (metin), variables (nesne), isteğe bağlı operationName'dir. Başarılı HTTP taşıması GraphQL işleminin başarılı olduğu anlamına gelmez: bu laboratuvar GraphQL sonuçlarını HTTP 200 altında `data` ve varsa `errors` ile taşır; bozuk JSON zarfı 400'dür. Tüm üretim GraphQL servislerinin aynı HTTP durum politikasını kullandığını varsayma.

```text
type Item { id: Int!, owner: String!, title: String!, secret: String }
type Query { item(id: Int!): Item, greeting: String! }
type Mutation { rename(id: Int!, title: String!): Item }
```

Uygulamanın **bu API için** politikası: oturum açan iki kullanıcı da public id/owner/title alanlarını okuyabilir; secret ve rename yalnız sahibine açıktır. REST /items politikasından bilinçli olarak farklıdır. Secret nullable olduğundan yasak alanda `secret:null` ve errors oluşur; aynı yanıttaki public alanlar kalır. Resolver yetkisi alanın alias'ına veya fragment içinde bulunmasına göre gevşemez. Introspection şemayı gösterir; veriyi okuma hakkı vermez. Laboratuvar bunu açık tutar.

Burp Repeater'da aynı POST'u yakala. Önce yalnız variables.id'yi değiştir; sonra secret alanını çıkar/ekle; son olarak bir alias ve fragment kullan. Yanıttaki errors.path alias'ı gösterebilir. Query ve mutation'ı birbirinden ayır. Gerçek motor dilin validation kurallarını uygular; HTTP batching, subscription taşıması, yük sınırı/depth bütçesi ve üretim rate limiting bu küçük uygulamada yoktur.

Şema adlarını okumak için JSON zarfının query alanına şunu koy:

```text
{ __schema { queryType { name } mutationType { name } } }
```

`Query` ve `Mutation` adlarını görürsün. Sonraki belge `x` alias'ı ve
`Alanlar` fragment'ını kullanır; variables yine `{"id":2}` olur:

```text
query Oku($id:Int!) { x:item(id:$id) { ...Alanlar } }
fragment Alanlar on Item { id title secret }
```

Ayşe'nin oturumuyla bu sorguda public id/title kalır; secret null ve
`errors[0].path` değeri `["x","secret"]` olur. Alanı başka adla istemek yetkiyi
değiştirmez. `{ item(id:"2") { id } }` ise doğrulama hatasıdır: Int beklenen
yere metin verdin. Sorgu hatasında resolver yazma işlemi yapılmaz.

Kaynaklar: [GraphQL sorgular](https://graphql.org/learn/queries/), [yetkilendirme](https://graphql.org/learn/authorization/), [introspection](https://graphql.org/learn/introspection/), [graphql-core](https://graphql-core-3.readthedocs.io/).
:::

::: tahmin
```python
from http_lab import Lab
with Lab() as lab:
    c=lab.login('ayse')
    query='query Oku($id:Int!){item(id:$id){id title secret}}'
    for no in (1,2):
        r=lab.request('POST','/graphql',{'query':query,'variables':{'id':no}},cookie=c)
        b=r['body']
        print(r['status'],b['data']['item']['secret'],bool(b.get('errors')))
```
???
`200 A-only False` ve `200 None True`. İkinci kayıt public alanlarıyla gelebilir; secret alanına yetki reddedilir. HTTP 200'ü tek başına başarı sayma.
:::

::: gorev Parametreli sorgu belgesi yaz
`okuma_belgesi(no)` `(query, variables)` döndürsün. query adı Oku olan, `$id:Int!` değişkeni kullanan query olmalı; item(id:$id) içinde id, owner, title, secret alanlarını alias olmadan seç. variables `{'id':no}` olsun. Veriyi sorgu metnine birleştirme. no'nun GraphQL Int aralık/tür doğrulamasını gerçek motora bırak.
```starter
def okuma_belgesi(no):
    return ('',{})
```
```test
from http_lab import Lab
from graphql import parse
with Lab() as lab:
    for user,own in (('ayse',1),('berk',2)):
        c=lab.login(user)
        for no in (0,1,2,3):
            q,v=okuma_belgesi(no)
            eq(v,{'id':no},'deger variables icinde')
            ast=parse(q); op=ast.definitions[0]
            eq(op.name.value,'Oku','operation adi')
            eq([x.variable.name.value for x in op.variable_definitions],['id'],'degisken tanimi')
            r=lab.request('POST','/graphql',{'query':q,'variables':v,'operationName':'Oku'},cookie=c)['body']
            if no in (0,3): eq(r['data'],{'item':None},'eksik kayit')
            else:
                item=r['data']['item']; source=lab.snapshot()['items'][no]
                for field in ('id','owner','title'): eq(item[field],source[field],'public alan')
                eq(item['secret'],('A-only' if no==1 else 'B-only') if no==own else None,'alan yetkisi')
                eq(bool(r.get('errors')),no!=own,'kismi hata')
    for no in (True,2147483648,-2147483649):
        q,v=okuma_belgesi(no)
        r=lab.request('POST','/graphql',{'query':q,'variables':v},cookie=c)['body']
        ok(bool(r.get('errors')),'gercek GraphQL Int siniri')
```
```solution
def okuma_belgesi(no):
    return ('query Oku($id:Int!){item(id:$id){id owner title secret}}',{'id':no})
```
```hint
Sorgu sabit, değerler variables içinde kalır. HTTP JSON'daki True, GraphQL Int değildir.
```
:::

::: gorev Mutation yanıtındaki hatayı kaybetme
`adlandir(lab,cookie,no,title)` POST /graphql ile adı Adlandir olan mutation göndersin. id ve title değişkenlerini kullan; rename yanıtından id/title/owner seç. `(HTTP status, data, errors)` döndür; data yoksa None, errors yoksa boş liste. Sunucunun red yanıtını başarılıymış gibi veriyle değiştirme. Başlık sınırı 1..80; yalnız sahip yazabilir.
```starter
def adlandir(lab,cookie,no,title):
    return (200,{},[])
```
```test
from http_lab import Lab
with Lab() as lab:
    a=lab.login('ayse'); b=lab.login('berk')
    for cookie,no in ((a,1),(b,2)):
        for title in ('x','y'*80,'','z'*81):
            before=lab.snapshot(); status,data,errors=adlandir(lab,cookie,no,title)
            valid=1<=len(title)<=80
            eq(status,200,'GraphQL tasimasi')
            eq(bool(errors),not valid,'1..80 siniri')
            eq(lab.snapshot()['revision']-before['revision'],int(valid),'gercek yazma')
            if valid: eq(data['rename'],{'id':no,'owner':before['items'][no]['owner'],'title':title},'yazilan kayit')
    for cookie,no in ((a,2),(b,1),(None,1)):
        before=lab.snapshot()['items']; status,data,errors=adlandir(lab,cookie,no,'yasak')
        ok(bool(errors),'yetki reddi korunur'); eq(data,{'rename':None},'nullable mutation')
        eq(lab.snapshot()['items'],before,'red yazmaz')
class Tanik:
    def request(self,m,p,data=None,cookie=None):
        eq((m,p,cookie),('POST','/graphql','sid=c'),'zarf')
        eq(data['variables'],{'id':7,'title':'x"\ny'},'variables aynen')
        eq(data['operationName'],'Adlandir','operationName')
        return {'status':429,'body':{'errors':[{'message':'limit'}]}}
eq(adlandir(Tanik(),'sid=c',7,'x"\ny'),(429,None,[{'message':'limit'}]),'data yok ve HTTP hata yaniti')
```
```solution
def adlandir(lab,cookie,no,title):
    payload={'query':'mutation Adlandir($id:Int!,$title:String!){rename(id:$id,title:$title){id title owner}}',
             'variables':{'id':no,'title':title},'operationName':'Adlandir'}
    r=lab.request('POST','/graphql',payload,cookie=cookie)
    return r['status'],r['body'].get('data'),r['body'].get('errors',[])
```
```hint
Başlık içinde tırnak veya satır sonu bulunabilir; sorguya interpolate etme. GraphQL metnini sabit tut.
```
:::
