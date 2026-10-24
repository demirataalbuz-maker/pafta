---
id: el25
title: Eşik, İstisna ve Kanıt
summary: Gerçek threshold kuralıyla N−1/N/N+1 ve gerçek exception list deneyi yap.
---

::: anlat Gerçek ürün üzerinde çalışma
Threshold kuralı tek olay aramasını grup başına sayıya çevirir. `value: 3`
üç ve daha çok olayı kabul eder; iki olayı kabul etmez. `threshold.field`
hangi varlıkları saydığını belirler. İkinci görev aynı sorguyu gerçek exception
listesiyle çalıştırır: ders girdisindeki `exceptions`, Kibana'da geçici liste ve
öğe olarak oluşturulur, gerçek kuralın `exceptions_list` alanına bağlanır.
Bu örnekte listeyi tezgah hazırlıyor; editörde yazılan kod create-rule alanlarıdır.

İstisna `user.name == svc` olaylarını dışlar. Bu, yalnız benzer isimli kullanıcıya
genel güven vermek değildir. `Svc` aynı keyword değildir. Bir istisna eklemeden
önce olumlu olayı neden güvenilir saydığını belgelemelisin. Buradaki sentetik
svc verisi bir güvenlik kararı önerisi değil, eşleştirme tanığıdır.

Threshold alarmı sentetik bir özet belgedir; her kaynak olayın tüm alanlarını
taşımayabilir. Bu yüzden tezgah rastgele üretilen sentetik kimliği bir kaynak
olay kimliğiymiş gibi sunmaz: `ids: []`, gerçek `groups` ve `count` gösterir.
Normal olay kuralındaki `ids` ise kaynak ancestor kimlikleridir. Grup başına
eşik ile ücretli özellik olabilen alarm suppression aynı özellik değildir;
bu bölüm Basic üzerinde ölçülen threshold ve exception list ile sınırlıdır.

Bu bölüm **gerçek Elasticsearch/Kibana 9.5.5, Basic lisansı** kullanır; önce
[yerel laboratuvar yönergesini](../README.md) uygula. Girdi kutusunda
`backend: elastic` görünür. Önceki Lucene/yerel EQL motoruna sessiz dönüş yoktur.
Her çalıştırma yeni bir geçici indeks kullanır, iş bitince onu siler. Girdideki
`documents` ders tanıklarıdır; sorgu veya pipeline kodu editörde yazılır.
Alan adı, tür, eksik alan ve zaman aralığı sözleşmenin parçasıdır.

Kaynaklar: [Threshold rules](https://www.elastic.co/docs/solutions/security/detect-and-alert/threshold), [Rule exceptions](https://www.elastic.co/docs/solutions/security/detect-and-alert/rule-exceptions).
:::

::: tahmin Önce çıktıyı düşün
İki, üç ve dört olaylı gruplardan hangileri eşik alarmı üretir?

```meta
dil: rule
timeout: 60
```

```rule
{
  "type": "threshold",
  "language": "kuery",
  "query": "status >= 400 AND status < 500",
  "threshold": {
    "field": [
      "user.name"
    ],
    "value": 3
  },
  "interval": "1m",
  "from": "now-2m",
  "to": "now"
}
```

```stdin
{"backend":"elastic","dil":"rule","mapping":{"@timestamp":"date","event.category":"keyword","process.name":"keyword","status":"long","user.name":"keyword"},"documents":[{"id":"alice0","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"alice","status":400},{"id":"alice1","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"alice","status":499},{"id":"bob0","@timestamp":"2026-01-01T00:08:00Z","event.category":"process","user.name":"bob","status":400},{"id":"bob1","@timestamp":"2026-01-01T00:09:59.999Z","event.category":"process","user.name":"bob","status":401},{"id":"bob2","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"bob","status":401},{"id":"carol0","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"carol","status":401},{"id":"carol1","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"carol","status":401},{"id":"carol2","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"carol","status":401},{"id":"carol3","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"carol","status":401},{"id":"svc0","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"svc","status":401},{"id":"svc1","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"svc","status":401},{"id":"svc2","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"svc","status":401},{"id":"noise","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"alice","status":200},{"id":"upper_noise","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"alice","status":500}],"context":{"timeframe_end":"2026-01-01T00:10:00.000Z"}}
```

???
Gerçek API ile doğrulanmış çıktı:

```text
{"preview_alerts":[{"count":3,"groups":[{"field":"user.name","value":"bob"}],"ids":[]},{"count":4,"groups":[{"field":"user.name","value":"carol"}],"ids":[]},{"count":3,"groups":[{"field":"user.name","value":"svc"}],"ids":[]}],"preview_count":3,"rule":{"enabled":false,"from":"now-2m","interval":"1m","language":"kuery","query":"status >= 400 AND status < 500","threshold":{"field":["user.name"],"value":3},"to":"now","type":"threshold"}}
```

:::

::: gorev Üç başarısız olayı say
status [400,500) olaylarını user.name başına sayan threshold/kuery kuralı yaz; eşik 3, interval 1m, from now-2m, to now.

```meta
dil: rule
timeout: 60
```

```stdin
{"backend":"elastic","dil":"rule","mapping":{"@timestamp":"date","event.category":"keyword","process.name":"keyword","status":"long","user.name":"keyword"},"documents":[{"id":"alice0","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"alice","status":400},{"id":"alice1","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"alice","status":499},{"id":"bob0","@timestamp":"2026-01-01T00:08:00Z","event.category":"process","user.name":"bob","status":400},{"id":"bob1","@timestamp":"2026-01-01T00:09:59.999Z","event.category":"process","user.name":"bob","status":401},{"id":"bob2","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"bob","status":401},{"id":"carol0","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"carol","status":401},{"id":"carol1","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"carol","status":401},{"id":"carol2","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"carol","status":401},{"id":"carol3","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"carol","status":401},{"id":"svc0","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"svc","status":401},{"id":"svc1","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"svc","status":401},{"id":"svc2","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"svc","status":401},{"id":"noise","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"alice","status":200},{"id":"upper_noise","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"alice","status":500}],"context":{"timeframe_end":"2026-01-01T00:10:00.000Z"}}
```

```starter
{
  "type": "threshold",
  "language": "kuery",
  "query": "status >= 400 AND status < 500",
  "threshold": {
    "field": [
      "user.name"
    ],
    "value": 1
  },
  "interval": "1m",
  "from": "now-2m",
  "to": "now"
}
```

```test
r=sonuc()
eq([(a['groups'],a['count']) for a in r['preview_alerts']], [([{'field':'user.name','value':'bob'}],3),([{'field':'user.name','value':'carol'}],4),([{'field':'user.name','value':'svc'}],3)], 'eşik altı/eşit/üst, kullanıcıya göre grup')
eq(r['rule']['threshold'], {'field':['user.name'],'value':3}, 'eşik sözleşmesi')
eq([r['rule'][k] for k in ['interval','from','to']], ['1m','now-2m','now'], 'kaydedilmiş zamanlama sözleşmesi')
aday=[dict(d,**{'user.name':'x_'+d['user.name']},id='x_'+d['id']) for d in korpus['documents']]
eq(sorted(a['count'] for a in sonuc(aday)['preview_alerts']),[3,3,4], 'grup adları ezberlenmez')
```

```solution
{
  "type": "threshold",
  "language": "kuery",
  "query": "status >= 400 AND status < 500",
  "threshold": {
    "field": [
      "user.name"
    ],
    "value": 3
  },
  "interval": "1m",
  "from": "now-2m",
  "to": "now"
}
```

```hint
threshold field listesi ve value tam sınırı belirler.
```

:::

::: gorev Gerçek istisna listesiyle tekrar ölç
Aynı threshold kuralını yaz. Girdideki svc exception listesi tezgahça gerçek ürüne bağlanır; sorgudan farklı kullanıcıları keyfî çıkartma.

```meta
dil: rule
timeout: 60
```

```stdin
{"backend":"elastic","dil":"rule","mapping":{"@timestamp":"date","event.category":"keyword","process.name":"keyword","status":"long","user.name":"keyword"},"documents":[{"id":"alice0","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"alice","status":400},{"id":"alice1","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"alice","status":499},{"id":"bob0","@timestamp":"2026-01-01T00:08:00Z","event.category":"process","user.name":"bob","status":400},{"id":"bob1","@timestamp":"2026-01-01T00:09:59.999Z","event.category":"process","user.name":"bob","status":401},{"id":"bob2","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"bob","status":401},{"id":"carol0","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"carol","status":401},{"id":"carol1","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"carol","status":401},{"id":"carol2","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"carol","status":401},{"id":"carol3","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"carol","status":401},{"id":"svc0","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"svc","status":401},{"id":"svc1","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"svc","status":401},{"id":"svc2","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"svc","status":401},{"id":"noise","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"alice","status":200},{"id":"upper_noise","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","user.name":"alice","status":500}],"context":{"timeframe_end":"2026-01-01T00:10:00.000Z"},"exceptions":[[{"field":"user.name","type":"match","operator":"included","value":"svc"}]]}
```

```starter
{
  "type": "threshold",
  "language": "kuery",
  "query": "status >= 400",
  "threshold": {
    "field": [
      "user.name"
    ],
    "value": 3
  },
  "interval": "1m",
  "from": "now-2m",
  "to": "now"
}
```

```test
r=sonuc()
eq([(a['groups'],a['count']) for a in r['preview_alerts']], [([{'field':'user.name','value':'bob'}],3),([{'field':'user.name','value':'carol'}],4)], 'gerçek exception list svc grubunu dışlar')
eq(r['rule']['threshold'], {'field':['user.name'],'value':3}, 'eşik sözleşmesi')
eq([r['rule'][k] for k in ['interval','from','to']], ['1m','now-2m','now'], 'kaydedilmiş zamanlama sözleşmesi')
aday=[dict(d,id='y_'+d['id']) for d in korpus['documents']]
aday += [dict(korpus['documents'][0],id='Svc'+str(i),**{'user.name':'Svc','status':401}) for i in range(3)]
r=sonuc(aday)
eq(sorted(a['groups'][0]['value'] for a in r['preview_alerts']), ['Svc','bob','carol'], 'exception match harf duyarlı, Svc ayrı kalır')
```

```solution
{
  "type": "threshold",
  "language": "kuery",
  "query": "status >= 400 AND status < 500",
  "threshold": {
    "field": [
      "user.name"
    ],
    "value": 3
  },
  "interval": "1m",
  "from": "now-2m",
  "to": "now"
}
```

```hint
İstisna listesi hazır; sayısal üst ucu ve threshold grubunu koru.
```

:::
