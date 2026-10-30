---
id: bt06
title: Purple Team Bulgusu · Boşluk, Öneri ve Yeniden Test
summary: Ölçülen eksikten sorumlu ve süreli iyileştirmeye geç; eşit eşikler ve negatif kontrollerle kabulü denetle.
---

::: anlat Bulguyu kapatan şey yeni kural dosyası değildir
BT03 seçicisi yalnız belirli script metnini görür; farklı dosya adı, kaynak alanının düşmesi veya başka süreç başlatıcısı kapsam dışıdır. Bu vaka “bütün PowerShell saldırıları tespit ediliyor” sonucu vermez. Önce boşluğu sınıflandır: telemetri yok, alan eşlemesi bozuk, kural mantığı dar, alarm yönlendirmesi yok veya müdahale süreci aksıyor. Her birinin düzeltmesi farklıdır.

Bir bulguda beklenen davranış, gözlenen sonuç ve kanıt referansı bulunur. Öneri, sahibi/son tarihi/geri dönüşü ve kabul kriteriyle tamamlanır. Kuralı genişletince bilinen pozitifleri yakalamak yetmez; meşru bakım kayıtlarında FP ve alarm hacmini de ölç. Düzeltilen veri/sorgu/kural sürümünü ve test penceresini sabitle. Replay sonucu sensörün veya alarm kanalının üretimde çalıştığını tek başına göstermez; canlı kontrollü kabul ayrıca gerekir. Bu bölüm saldırı zinciri üretmez, hazır kanıtı yeniden oynatır.

Aşağıdaki 24 saat güncellik, recall=1, precision>=0.95 ve FP<=2 kriterleri **Pafta'nın eğitim teslim politikasıdır**. NIST veya ürün varsayılanı diye sunulmaz. Ölçü tanımı ve kapsamını açık tutma yaklaşımı için [NIST ölçüm rehberi](https://csrc.nist.gov/pubs/sp/800/55/v1/final); olaydan öğrenme ve iyileştirme bağlamı için [SP 800-61r3](https://csrc.nist.gov/pubs/sp/800/61/r3/final).
:::

::: tahmin
```python
tp,fp,fn=19,1,0
print(tp/(tp+fp))
print(tp/(tp+fn))
```

???
`0.95` ve `1.0`. Bu eşit uçları kabul politikasında bilerek test edeceğiz; iki oran tek başına üretim kabulü değildir.
:::

::: gorev Bulguyu teslim edilebilir plana dönüştür
`plan(rows,available)` yalnız şu satırların id'lerini sıralı tekrarsız döndürsün: gap, expected, observed, owner, deadline_utc, rollback, acceptance metinleri strip sonrası dolu; refs boş değil ve tümü available içinde; deadline_utc offsetli ISO. Bozuk/naive zaman satırı dışarıda kalır. Açıklama metninin doğruluğu insan denetimidir; bu işlev yalnız sözleşme kapısıdır. Bu plan değişiklik uygulamaz.

```starter
def plan(rows,available):
    return [r['id'] for r in rows]
```

```test
base={'id':'g1','gap':'script adı dar','expected':'iki ad da incelensin','observed':'ikinci ad kaçtı','owner':'Detection','deadline_utc':'2026-10-27T12:00:00+03:00','rollback':'v1 kuralına dön','acceptance':'etiketli korpusta yeniden test','refs':['endpoint:p-run']}
eq(plan([base,base],{'endpoint:p-run'}),['g1'],'tam plan ve tekrar')
for key in ('gap','expected','observed','owner','deadline_utc','rollback','acceptance'):
    eq(plan([dict(base,**{key:' '})],{'endpoint:p-run'}),[],'boş alan '+key)
for value in ('2026-10-27T09:00:00','bozuk'):
    eq(plan([dict(base,deadline_utc=value)],{'endpoint:p-run'}),[],'belirsiz son tarih')
eq(plan([dict(base,refs=[])],{'endpoint:p-run'}),[],'kanıtsız bulgu')
eq(plan([dict(base,refs=['unknown'])],{'endpoint:p-run'}),[],'yok kanıt')
eq(plan([],set()),[],'boş plan')
```

```solution
from datetime import datetime

def plan(rows,available):
    result=set()
    for r in rows:
        required=('gap','expected','observed','owner','deadline_utc','rollback','acceptance')
        if any(not r.get(k,'').strip() for k in required):continue
        if not r.get('refs') or not set(r['refs'])<=set(available):continue
        try:
            dt=datetime.fromisoformat(r['deadline_utc'].replace('Z','+00:00'))
            if dt.tzinfo is None:continue
        except ValueError:continue
        result.add(r['id'])
    return sorted(result)
```

```hint
Sorumlu, tarih ve geri dönüş olmadan öneri kapatılamaz. Saat dilimsiz tarih için yerel varsayım yapma.
```
:::

::: gorev Yeniden testin kabul kapısı
`kabul(v)` yalnız şu durumda True: tp/fp/fn negatif olmayan tam int (bool değil); pozitif örnek sayısı tp+fn>0 ve negatif örnek sayısı negatives>0; fp<=negatives; fn=0, fp<=2 ve tp/(tp+fp)>=0.95. Ayrıca age_hours 0..24, corpus_reviewed tam True, rollback_tested tam True, tool_version ve rule_sha256 metinleri boş değil. negatives tam int olmalı. Eksik alan False. Bu yalnız korpus replay kabulüdür; üretim dağıtım onayı değildir.

```starter
def kabul(v):
    return True
```

```test
base={'tp':19,'fp':1,'fn':0,'negatives':20,'age_hours':24,'corpus_reviewed':True,'rollback_tested':True,'tool_version':'yerel-1','rule_sha256':'a'*64}
eq(kabul(base),True,'precision tam 0.95 ve yaş tam 24')
eq(kabul(dict(base,tp=18)),False,'0.95 altı')
eq(kabul(dict(base,tp=38,fp=2)),True,'FP tam 2')
eq(kabul(dict(base,tp=38,fp=2,negatives=1)),False,'FP negatif örnek sayısını aşamaz')
eq(kabul(dict(base,age_hours=0)),True,'tam güncel sıfır saat')
eq(kabul(dict(base,tp=100,fp=3)),False,'FP bir üstü')
for key,value in [('fn',1),('tp',0),('fp',-1),('negatives',0),('negatives',False),('tp',True),('age_hours',24.01),('age_hours',-0.01),('corpus_reviewed',False),('rollback_tested',False),('tool_version',''),('rule_sha256','')]:
    eq(kabul(dict(base,**{key:value})),False,'bağımsız kapı '+key)
eq(kabul(dict(base,negatives=0,fp=1)),False,'negatif örnek sayısını aşan FP')
eq(kabul({}),False,'verisiz kabul olmaz')
eq(kabul(dict(base,fp=0,negatives=0)),False,'FP sıfır olsa da negatif örnek yoksa kabul yok')
eq(kabul(dict(base,tp=0,fp=0,fn=0)),False,'pozitif örnek yoksa kabul yok; sıfıra bölme olmaz')
```

```solution
def kabul(v):
    if any(type(v.get(k)) is not int or v[k]<0 for k in ('tp','fp','fn','negatives')):return False
    tp,fp,fn=v['tp'],v['fp'],v['fn']
    if tp+fn==0 or v['negatives']==0 or fp>v['negatives']:return False
    return (fn==0 and fp<=2 and tp/(tp+fp)>=0.95 and 0<=v.get('age_hours',25)<=24 and v.get('corpus_reviewed') is True and v.get('rollback_tested') is True and bool(v.get('tool_version')) and bool(v.get('rule_sha256')))
```

```hint
Oran iyi görünse bile örnek yokluğu, güncellik ve geri dönüş kapıları bağımsızdır. Paydaları bölmeden önce denetle.
```
:::

::: anlat Nihai teslim ve insan kabulü
BT05 raporuna en az bir gerçek kapsam boşluğu ekle: örneğin CommandLine alanı yoksa kuralın kayıt seçememesi. Aynı endpoint kaydından bu alanı kaldırarak önceki kuralı yeniden çalıştır; çıkan kaçırmayı observed'a yaz. Alanı düzeltme ile kuralı genişletmenin farklı işler olduğunu açıkla. Meşru bakım kontrolüyle yanlış pozitif riskini tartış. Sahip/son tarih/geri dönüş ve yeniden test kabulünü yaz; tabloyu yalnız “yeni kural yazılacak” diye kapatma.

İnceleyen kişi sorgu/kural/manifest sürümünü, ham kanıt bağlantılarını, FP/FN tanımlarını, gerçek araç sonucunu ve önerinin gözlenen boşlukla ilişkisini kontrol etsin. Yönetici özetinde bilinmeyen etki veya nedensellik kesinleştirilmişse teslimi geri çevirsin. Otomatik testler bu insan kararının yerine geçmez. Örnek tamamlanmış belge depoda `tracks/bitirme/ornek-rapor.md` içindedir; kendi raporunla karşılaştır, tek doğru ifade kalıbı olarak ezberleme.
:::
