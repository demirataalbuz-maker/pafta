---
id: el24
title: Aramadan Security Kuralına
summary: KQL ve EQL kurallarını gerçek Kibana’da kaydet, zaman penceresiyle önizle.
---

::: anlat Gerçek ürün üzerinde çalışma
Bir Discover aramasının eşleşmesi çalışan tespit kuralı değildir. Kuralda
`type`, `language`, indeks, aralık, risk ve yetki de vardır. Query kuralında
Kibana KQL dil değeri `kuery`, event correlation kuralında `type: eql` ve
`language: eql` kullanılır. Kuralı oluşturan/değiştiren kullanıcının yetkileriyle
API anahtarı üretilir; yetkinin sonradan kaldırılması yürütmeyi bozabilir.

Bu tezgah yazdığın alanlarla gerçek **devre dışı** kural kaydeder; rastgele
indeksi kendisi bağlar. Sonra tek gerçek önizleme yürütmesini verilen
`timeframe_end` anında çalıştırır. Sonuçtaki `preview_alerts` çalışma alarmı
değildir: 9.5.5'in geçici preview indeksinden okunup yalnız bu preview kimliğiyle
temizlenir. Her görevde zamanlayıcı bekleyip sahte hızlandırılmış alarm üretmek
yerine iki aşama açıkça ayrılır. Teslim kabul betiği ayrıca gerçek etkin kuralın
Task Manager tarafından çalıştırılmasını ve operational alarm indeksini ölçer.

`interval: 1m` çalışma sıklığıdır; `from: now-2m` iki dakikalık arama penceresidir.
Bunları aynı kavram sanma. Biraz örtüşme gecikmeye pay bırakır; sınırsız gecikmeyi
telafi etmez. Bu ders `timeframe_end` sabittir; kendi canlı ortamında gerçek
olay zamanı/ingest gecikmesi ve izleme ekranını ayrıca incele.

Bu bölüm **gerçek Elasticsearch/Kibana 9.5.5, Basic lisansı** kullanır; önce
[yerel laboratuvar yönergesini](../README.md) uygula. Girdi kutusunda
`backend: elastic` görünür. Önceki Lucene/yerel EQL motoruna sessiz dönüş yoktur.
Her çalıştırma yeni bir geçici indeks kullanır, iş bitince onu siler. Girdideki
`documents` ders tanıklarıdır; sorgu veya pipeline kodu editörde yazılır.
Alan adı, tür, eksik alan ve zaman aralığı sözleşmenin parçasıdır.

Kaynaklar: [Kural oluşturma](https://www.elastic.co/docs/solutions/security/detect-and-alert/using-the-rule-ui), [Security detections API / authorization](https://www.elastic.co/docs/api/doc/kibana/group/endpoint-security-detections-api), [Preview API](https://www.elastic.co/docs/api/doc/kibana/v9/operation/operation-rulepreview).
:::

::: anlat Kendi kuralını gerçekten zamanla
Görevde yazdığın JSON'u UTF-8 `kuralim.json` dosyasına kaydet. Pafta kökünde
şu komutu çalıştır (birinci görev için task 1, EQL görevi için task 2):

```text
python tools/elastic_rule_live.py --task 1 --code-file kuralim.json
```

Bu komut önce aynı gerçek önizlemeyi doğrular, sonra **yeni etkin kuralı**
gerçek Task Manager'a bırakır; en çok 150 saniye bekler. Eski ders tarihleri
açıkça günümüze yeniden bazlanır, olayların birbirine göre zaman farkı korunur.
Bu canlı deneyde zamanlayıcı gecikmesinin sınır testini bozmasını önlemek için
interval 1m, lookback now-10m kullanılır; asıl görevdeki now-2m sınırı bununla
karıştırılmaz; bu daha geniş pencerede eski d olayı da eşleşir. JSON içindeki query/type/language senin yazdığın haliyle kalır.

Operational alarm indeksi okunur; çıktı `execution: Task Manager / operational`
ile kaynak olay kimliklerini ve alarm sayısını verir. Kural, alarm ve geçici
indeks sonunda temizlenir. Kibana'da bunun karşılığı bir kuralı etkinleştirmek,
Rule monitoring'de başarılı çalışmasını görmek ve Alerts ekranında kaynak
olayla ilişkilendirmektir. Dış bildirim veya response action açılmaz. Bu komut
yalnız öğretim ortamında kendi EL24 kodunu çalıştırır; üretim SIEM'ine bağlanmaz.
:::

::: tahmin Önce çıktıyı düşün
KQL keyword harfi ve [400,500) aralığı hangi preview olaylarını bırakır?

```meta
dil: rule
timeout: 60
```

```rule
{
  "type": "query",
  "language": "kuery",
  "query": "event.category: process AND process.name: cmd.exe AND status >= 400 AND status < 500",
  "interval": "1m",
  "from": "now-2m",
  "to": "now"
}
```

```stdin
{"backend":"elastic","dil":"rule","mapping":{"@timestamp":"date","event.category":"keyword","process.name":"keyword","status":"long","user.name":"keyword"},"documents":[{"id":"a","@timestamp":"2026-01-01T00:08:00Z","event.category":"process","process.name":"cmd.exe","status":400,"user.name":"alice"},{"id":"b","@timestamp":"2026-01-01T00:09:59.999Z","event.category":"process","process.name":"cmd.exe","status":499,"user.name":"bob"},{"id":"c","@timestamp":"2026-01-01T00:10:00Z","event.category":"process","process.name":"cmd.exe","status":500,"user.name":"carol"},{"id":"d","@timestamp":"2026-01-01T00:07:59.999Z","event.category":"process","process.name":"cmd.exe","status":400,"user.name":"dave"},{"id":"e","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","process.name":"CMD.EXE","status":400,"user.name":"erin"},{"id":"ust_ic","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","process.name":"cmd.exe","status":500,"user.name":"alice"},{"id":"alt_ic","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","process.name":"cmd.exe","status":399,"user.name":"alice"},{"id":"kategori","@timestamp":"2026-01-01T00:09:00Z","event.category":"network","process.name":"cmd.exe","status":400,"user.name":"alice"},{"id":"diger","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","process.name":"powershell.exe","status":400,"user.name":"alice"}],"context":{"timeframe_end":"2026-01-01T00:10:00.000Z"}}
```

???
Gerçek API ile doğrulanmış çıktı:

```text
{"preview_alerts":[{"count":null,"groups":[],"ids":["a"]},{"count":null,"groups":[],"ids":["b"]}],"preview_count":2,"rule":{"enabled":false,"from":"now-2m","interval":"1m","language":"kuery","query":"event.category: process AND process.name: cmd.exe AND status >= 400 AND status < 500","to":"now","type":"query"}}
```

:::

::: gorev Zaman pencereli KQL kuralı
query/kuery kuralı yaz: process kategorisi, tam küçük harf cmd.exe, status [400,500). interval 1m, from now-2m, to now.

```meta
dil: rule
timeout: 60
```

```stdin
{"backend":"elastic","dil":"rule","mapping":{"@timestamp":"date","event.category":"keyword","process.name":"keyword","status":"long","user.name":"keyword"},"documents":[{"id":"a","@timestamp":"2026-01-01T00:08:00Z","event.category":"process","process.name":"cmd.exe","status":400,"user.name":"alice"},{"id":"b","@timestamp":"2026-01-01T00:09:59.999Z","event.category":"process","process.name":"cmd.exe","status":499,"user.name":"bob"},{"id":"c","@timestamp":"2026-01-01T00:10:00Z","event.category":"process","process.name":"cmd.exe","status":500,"user.name":"carol"},{"id":"d","@timestamp":"2026-01-01T00:07:59.999Z","event.category":"process","process.name":"cmd.exe","status":400,"user.name":"dave"},{"id":"e","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","process.name":"CMD.EXE","status":400,"user.name":"erin"},{"id":"ust_ic","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","process.name":"cmd.exe","status":500,"user.name":"alice"},{"id":"alt_ic","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","process.name":"cmd.exe","status":399,"user.name":"alice"},{"id":"kategori","@timestamp":"2026-01-01T00:09:00Z","event.category":"network","process.name":"cmd.exe","status":400,"user.name":"alice"},{"id":"diger","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","process.name":"powershell.exe","status":400,"user.name":"alice"}],"context":{"timeframe_end":"2026-01-01T00:10:00.000Z"}}
```

```starter
{
  "type": "query",
  "language": "kuery",
  "query": "status: *",
  "interval": "1m",
  "from": "now-2m",
  "to": "now"
}
```

```test
r=sonuc()
eq(r['preview_alerts'],[{'ids':['a'],'count':None,'groups':[]},{'ids':['b'],'count':None,'groups':[]}], 'gerçek KQL ve iki dakikalık pencere')
eq([r['rule'][k] for k in ['type','language','interval','from','to','enabled']], ['query','kuery','1m','now-2m','now',False], 'gerçek kaydedilmiş kural sözleşmesi')
aday=[dict(d,id='yeni_'+d['id']) for d in korpus['documents']]
eq([a['ids'] for a in sonuc(aday)['preview_alerts']], [['yeni_a'],['yeni_b']], 'kimlik ezberi yok')
```

```solution
{
  "type": "query",
  "language": "kuery",
  "query": "event.category: process AND process.name: cmd.exe AND status >= 400 AND status < 500",
  "interval": "1m",
  "from": "now-2m",
  "to": "now"
}
```

```hint
KQL büyük/küçük harfi keyword mapping belirler; arama penceresi JSON alanıdır.
```

:::

::: gorev Aynı tespiti EQL kuralına taşı
eql/eql kuralı yaz: process kategorisi, cmd.exe harf duyarsız (:), status [400,500). Aynı interval/from/to kullan.

```meta
dil: rule
timeout: 60
```

```stdin
{"backend":"elastic","dil":"rule","mapping":{"@timestamp":"date","event.category":"keyword","process.name":"keyword","status":"long","user.name":"keyword"},"documents":[{"id":"a","@timestamp":"2026-01-01T00:08:00Z","event.category":"process","process.name":"cmd.exe","status":400,"user.name":"alice"},{"id":"b","@timestamp":"2026-01-01T00:09:59.999Z","event.category":"process","process.name":"cmd.exe","status":499,"user.name":"bob"},{"id":"c","@timestamp":"2026-01-01T00:10:00Z","event.category":"process","process.name":"cmd.exe","status":500,"user.name":"carol"},{"id":"d","@timestamp":"2026-01-01T00:07:59.999Z","event.category":"process","process.name":"cmd.exe","status":400,"user.name":"dave"},{"id":"e","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","process.name":"CMD.EXE","status":400,"user.name":"erin"},{"id":"ust_ic","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","process.name":"cmd.exe","status":500,"user.name":"alice"},{"id":"alt_ic","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","process.name":"cmd.exe","status":399,"user.name":"alice"},{"id":"kategori","@timestamp":"2026-01-01T00:09:00Z","event.category":"network","process.name":"cmd.exe","status":400,"user.name":"alice"},{"id":"diger","@timestamp":"2026-01-01T00:09:00Z","event.category":"process","process.name":"powershell.exe","status":400,"user.name":"alice"}],"context":{"timeframe_end":"2026-01-01T00:10:00.000Z"}}
```

```starter
{
  "type": "eql",
  "language": "eql",
  "query": "any where true",
  "interval": "1m",
  "from": "now-2m",
  "to": "now"
}
```

```test
r=sonuc()
eq(sorted(a['ids'] for a in r['preview_alerts']),[['a'],['b'],['e']], 'EQL : harf duyarsız; aralık aynı')
eq([r['rule'][k] for k in ['type','language','interval','from','to','enabled']], ['eql','eql','1m','now-2m','now',False], 'gerçek event correlation kuralı')
aday=[dict(d,id='yeni_'+d['id']) for d in korpus['documents']]
eq(sorted(a['ids'] for a in sonuc(aday)['preview_alerts']), [['yeni_a'],['yeni_b'],['yeni_e']], 'başka olay kimlikleri')
```

```solution
{
  "type": "eql",
  "language": "eql",
  "query": "process where process.name : \"cmd.exe\" and status >= 400 and status < 500",
  "interval": "1m",
  "from": "now-2m",
  "to": "now"
}
```

```hint
type ve language eql; sorgu EQL sözdizimi kullanır.
```

:::
