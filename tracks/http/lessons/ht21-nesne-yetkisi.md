---
id: ht21
title: İki Hesaplı Nesne Yetkilendirme Matrisi
summary: A ve B hesaplarının okuma/yazma izinlerini yanıt, kayıt durumu ve olay kaydıyla birlikte ölç.
---

::: anlat Oturum var; bu nesneye izin var mı?
Kimlik doğrulama kullanıcıyı tanır; nesne yetkilendirmesi bu kaydı görme/değiştirme hakkını belirler. Laboratuvarda 1 ayse'ye, 2 berk'e aittir. GET ve PATCH /items/id her istekte sahipliği doğrular. 401 oturum yok, 403 diğerinin kaydı, 404 kayıt yok, 422 kabul edilemeyen başlık; bunlar bu uygulamanın tercihidir. Bazı gerçek sistemler bilgi sızdırmamak için yetkisiz nesneye 404 döndürür.

| Oturum | Kayıt 1 GET/PATCH | Kayıt 2 GET/PATCH |
|---|---|---|
| ayse | 200 / 200 | 403 / 403 |
| berk | 403 / 403 | 200 / 200 |
| yok | 401 / 401 | 401 / 401 |

PATCH JSON gövdesi `{'title':'...'}` alır; kırpılmış başlık 1..80 karakterdir. Bu ders yalnız sahipliği sınar. CSRF deneyini önceki dersin /change uç noktasında yaptık. Her redde kaydın ve revision'ın değişmediğini kontrol et. Yalnız durum kodlarını kaydetmek, 403 dönüp arkada veri değiştiren hatayı kaçırır.

Kaynak: [OWASP API1 — Broken Object Level Authorization](https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization/).
:::

::: tahmin
```python
from http_lab import Lab
with Lab() as lab:
    a,b=lab.login('ayse'),lab.login('berk')
    for c in (a,b,None):
        print([lab.request('GET',f'/items/{i}',cookie=c)['status'] for i in (1,2)])
```
???
`[200, 403]`, `[403, 200]`, `[401, 401]`. Aynı kayıt numarası farklı oturumda farklı yetki kararı verir.
:::

::: gorev Okuma ve yazma matrisini ölç
`yetki_matrisi(lab, hesaplar, ids)` hesaplar sözlüğünü ekleme sırasıyla dolaşsın; her cookie için ids sırasıyla her kayda önce GET, sonra PATCH yapsın. PATCH title değeri `kontrol`. Her çağrıdan önce/sonra snapshot al; `(hesap,id,yontem,status,degisti)` satırları döndür. `degisti` items sözlüğünün gerçekten farklı olup olmadığıdır; HTTP kodundan türetme. İstekleri atlama. Varsayılan veriyle başarılı PATCH'in ikinci çalıştırmada aynı değeri yazması durumu değiştirmeyebilir; bu da doğru gözlemdir.
```starter
def yetki_matrisi(lab, hesaplar, ids):
    return []
```
```test
from http_lab import Lab
with Lab() as lab:
    cs={'A':lab.login('ayse'),'B':lab.login('berk'),'Yok':None}
    got=yetki_matrisi(lab,cs,[1,2])
    expected=[]
    for name,own in [('A',1),('B',2),('Yok',None)]:
        for i in (1,2):
            status=401 if own is None else 200 if i==own else 403
            expected += [(name,i,'GET',status,False),(name,i,'PATCH',status,status==200)]
    eq(got,expected,'12 hucreli matris ve yazma tanigi')
    eq(lab.snapshot()['revision'],2,'yalniz iki kabul edilen yazma')
    eq(len(lab.snapshot()['events']),14,'iki login ve on iki gercek istek')
    tekrar=yetki_matrisi(lab,{'A':cs['A']},[1,0,3])
    eq(tekrar,[('A',1,'GET',200,False),('A',1,'PATCH',200,False),('A',0,'GET',404,False),('A',0,'PATCH',404,False),('A',3,'GET',404,False),('A',3,'PATCH',404,False)],'ayni deger yazma ve komsu eksik kayitlar')
class Tanik:
    def __init__(self): self.state=0; self.calls=[]
    def snapshot(self): return {'items':{'x':self.state}}
    def request(self,m,p,data=None,cookie=None):
        self.calls.append((m,p,data,cookie))
        if m=='GET': self.state+=1
        return {'status':403}
t=Tanik()
eq(yetki_matrisi(t,{'C':'c'},[9]),[('C',9,'GET',403,True),('C',9,'PATCH',403,False)],'403 veri degistirirse yakala')
eq(t.calls,[('GET','/items/9',None,'c'),('PATCH','/items/9',{'title':'kontrol'},'c')],'istek sozlesmesi')
eq(yetki_matrisi(t,{},[1]),[],'bos hesaplar')
eq(yetki_matrisi(t,{'C':'c'},[]),[],'bos kayitlar')
```
```solution
def yetki_matrisi(lab, hesaplar, ids):
    rows=[]
    for name,cookie in hesaplar.items():
        for no in ids:
            for method in ('GET','PATCH'):
                before=lab.snapshot()['items']
                data={'title':'kontrol'} if method=='PATCH' else None
                r=lab.request(method,f'/items/{no}',data,cookie=cookie)
                changed=before!=lab.snapshot()['items']
                rows.append((name,no,method,r['status'],changed))
    return rows
```
```hint
İç içe üç döngü var. Snapshot gerçek kopyadır; iki HTTP çağrısı arasında saklayabilirsin.
```
:::
