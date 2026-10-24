---
id: el20
title: Dosyadan Gerçek ECS Ingest
summary: Alt süreç kaydını NDJSON dosyasından gerçek ingest pipeline ile indeksle.
---

::: anlat Gerçek ürün üzerinde çalışma
`captures/process.ndjson`, Python'un gerçekten başlatıp beklediği üç zararsız
alt süreçten üretildi. `pid`, bitiş zamanı ve `returncode` işletim sisteminden
gelir. Bu bir **üst süreç gözlemi**dir; Sysmon, 4688 veya Elastic Agent olayı
olduğu iddia edilmez. Üretici `tools/capture_elastic_telemetry.py`dir. Yeni
kayıt almak istersen kendi dosyana çalıştır; hazır ders korpusunu değiştirme.

İlk kez NDJSON → `_bulk?pipeline=...&refresh=true` zinciri kurulur. Simülasyon
ayrıştırmayı gösterir; başarılı `_simulate`, strict mapping'e yazılabileceğini
kanıtlamaz. Burada hem simülasyon hem gerçek bulk öğe durumları okunur.
`rc` metin olduğundan `convert long` gerekir. `rename`, hedef alan zaten varsa
ürün kurallarına göre hata verebilir; bir alan adını değiştirmek türünü dönüştürmez.
`remove`, mapping'de olmayan ham alanları kaldırır. ECS `event.category` ve
`event.type` alanlarını dizi biçiminde kur. Çıkış kodu tek başına kötü niyet kanıtı
değildir; `event.kind: alert` yazmak da bir Security alarmı üretmez.

Bu bölüm **gerçek Elasticsearch/Kibana 9.5.5, Basic lisansı** kullanır; önce
[yerel laboratuvar yönergesini](../README.md) uygula. Girdi kutusunda
`backend: elastic` görünür. Önceki Lucene/yerel EQL motoruna sessiz dönüş yoktur.
Her çalıştırma yeni bir geçici indeks kullanır, iş bitince onu siler. Girdideki
`documents` ders tanıklarıdır; sorgu veya pipeline kodu editörde yazılır.
Alan adı, tür, eksik alan ve zaman aralığı sözleşmenin parçasıdır.

Kaynaklar: [Ingest pipelines](https://www.elastic.co/docs/manage-data/ingest/transform-enrich/ingest-pipelines), [ECS event alanları](https://www.elastic.co/docs/reference/ecs/ecs-event), [ECS process alanları](https://www.elastic.co/docs/reference/ecs/ecs-process).
:::

::: tahmin Önce çıktıyı düşün
Pipeline işlemcileri sırayla uygulanınca belge biçimi ve bulk durumları ne olur?

```meta
dil: ingest
timeout: 60
```

```ingest
{
  "processors": [
    {
      "rename": {
        "field": "at",
        "target_field": "@timestamp"
      }
    },
    {
      "rename": {
        "field": "exe",
        "target_field": "process.name"
      }
    },
    {
      "convert": {
        "field": "pid",
        "target_field": "process.pid",
        "type": "long"
      }
    },
    {
      "convert": {
        "field": "rc",
        "target_field": "process.exit_code",
        "type": "long"
      }
    },
    {
      "remove": {
        "field": [
          "pid",
          "rc"
        ]
      }
    },
    {
      "set": {
        "field": "event.kind",
        "value": "event"
      }
    },
    {
      "set": {
        "field": "event.category",
        "value": [
          "process"
        ]
      }
    },
    {
      "set": {
        "field": "event.type",
        "value": [
          "end"
        ]
      }
    }
  ]
}
```

```stdin
{"backend":"elastic","dil":"ingest","mapping":{"@timestamp":"date","process.name":"keyword","process.pid":"long","process.exit_code":"long","event.category":"keyword","event.kind":"keyword","event.type":"keyword"},"documents":[{"id":"proc-0","at":"2026-10-24T13:13:10.142Z","exe":"python.exe","pid":"42716","rc":"0"},{"id":"proc-1","at":"2026-10-24T13:13:10.287Z","exe":"python.exe","pid":"41344","rc":"1"},{"id":"proc-2","at":"2026-10-24T13:13:10.432Z","exe":"python.exe","pid":"40896","rc":"2"}]}
```

???
Gerçek API ile doğrulanmış çıktı:

```text
{"documents":[{"@timestamp":"2026-10-24T13:13:10.142Z","event":{"category":["process"],"kind":"event","type":["end"]},"id":"proc-0","process":{"exit_code":0,"name":"python.exe","pid":42716}},{"@timestamp":"2026-10-24T13:13:10.287Z","event":{"category":["process"],"kind":"event","type":["end"]},"id":"proc-1","process":{"exit_code":1,"name":"python.exe","pid":41344}},{"@timestamp":"2026-10-24T13:13:10.432Z","event":{"category":["process"],"kind":"event","type":["end"]},"id":"proc-2","process":{"exit_code":2,"name":"python.exe","pid":40896}}],"items":[{"error":null,"id":"proc-0","status":201},{"error":null,"id":"proc-1","status":201},{"error":null,"id":"proc-2","status":201}],"simulation":[{"source":{"@timestamp":"2026-10-24T13:13:10.142Z","event":{"category":["process"],"kind":"event","type":["end"]},"id":"proc-0","process":{"exit_code":0,"name":"python.exe","pid":42716}}},{"source":{"@timestamp":"2026-10-24T13:13:10.287Z","event":{"category":["process"],"kind":"event","type":["end"]},"id":"proc-1","process":{"exit_code":1,"name":"python.exe","pid":41344}}},{"source":{"@timestamp":"2026-10-24T13:13:10.432Z","event":{"category":["process"],"kind":"event","type":["end"]},"id":"proc-2","process":{"exit_code":2,"name":"python.exe","pid":40896}}}]}
```

:::

::: gorev Ham kaydı ECS alanlarına taşı
at→@timestamp, exe→process.name; pid ve rc metinlerini long türündeki process.pid/process.exit_code alanlarına dönüştür. Ham dört alan kalmasın.

```meta
dil: ingest
timeout: 60
```

```stdin
{"backend":"elastic","dil":"ingest","mapping":{"@timestamp":"date","process.name":"keyword","process.pid":"long","process.exit_code":"long","event.category":"keyword","event.kind":"keyword","event.type":"keyword"},"documents":[{"id":"proc-0","at":"2026-10-24T13:13:10.142Z","exe":"python.exe","pid":"42716","rc":"0"},{"id":"proc-1","at":"2026-10-24T13:13:10.287Z","exe":"python.exe","pid":"41344","rc":"1"},{"id":"proc-2","at":"2026-10-24T13:13:10.432Z","exe":"python.exe","pid":"40896","rc":"2"}]}
```

```starter
{
  "processors": []
}
```

```test
r=sonuc()
eq([i['status'] for i in r['items']], [201,201,201], 'üç gerçek kayıt indekslendi')
eq([alan(d,'process.exit_code') for d in r['documents']], [0,1,2], 'gerçek returncode değerleri')
ok(all(type(alan(d,'process.exit_code')) is int for d in r['documents']), 'exit_code tamsayı olmalı')
ok(all(type(alan(d,'process.pid')) is int and alan(d,'process.pid')>0 for d in r['documents']), 'pid tamsayı')
ok(all('@timestamp' in d and alan(d,'process.name') is not None and not any(k in d for k in ['at','exe','pid','rc']) for d in r['documents']), 'ECS yolları ve ham alan temizliği')
aday=[dict(korpus['documents'][0],id='sinir'+str(i),rc=str(v),pid=str(2147483648+i)) for i,v in enumerate([-1,0,1,2147483648])]
r=sonuc(aday)
eq([alan(d,'process.exit_code') for d in r['documents']],[-1,0,1,2147483648], 'long; sabit kod veya 32 bit daraltma yok')
eq([alan(d,'process.pid') for d in r['documents']], [2147483648,2147483649,2147483650,2147483651], 'pid girdiden gelir')
```

```solution
{
  "processors": [
    {
      "rename": {
        "field": "at",
        "target_field": "@timestamp"
      }
    },
    {
      "rename": {
        "field": "exe",
        "target_field": "process.name"
      }
    },
    {
      "convert": {
        "field": "pid",
        "target_field": "process.pid",
        "type": "long"
      }
    },
    {
      "convert": {
        "field": "rc",
        "target_field": "process.exit_code",
        "type": "long"
      }
    },
    {
      "remove": {
        "field": [
          "pid",
          "rc"
        ]
      }
    }
  ]
}
```

```hint
rename, convert target_field ve remove sırasını kur.
```

:::

::: gorev Olay sınıflandırmasını tamamla
İlk sözleşmeyi koru; event.kind event, event.category [process], event.type [end] olsun. Bunlar alarm değil süreç bitiş gözlemidir.

```meta
dil: ingest
timeout: 60
```

```stdin
{"backend":"elastic","dil":"ingest","mapping":{"@timestamp":"date","process.name":"keyword","process.pid":"long","process.exit_code":"long","event.category":"keyword","event.kind":"keyword","event.type":"keyword"},"documents":[{"id":"proc-0","at":"2026-10-24T13:13:10.142Z","exe":"python.exe","pid":"42716","rc":"0"},{"id":"proc-1","at":"2026-10-24T13:13:10.287Z","exe":"python.exe","pid":"41344","rc":"1"},{"id":"proc-2","at":"2026-10-24T13:13:10.432Z","exe":"python.exe","pid":"40896","rc":"2"}]}
```

```starter
{
  "processors": [
    {
      "rename": {
        "field": "at",
        "target_field": "@timestamp"
      }
    },
    {
      "rename": {
        "field": "exe",
        "target_field": "process.name"
      }
    },
    {
      "convert": {
        "field": "pid",
        "target_field": "process.pid",
        "type": "long"
      }
    },
    {
      "convert": {
        "field": "rc",
        "target_field": "process.exit_code",
        "type": "long"
      }
    },
    {
      "remove": {
        "field": [
          "pid",
          "rc"
        ]
      }
    }
  ]
}
```

```test
r=sonuc()
eq([i['status'] for i in r['items']], [201,201,201], 'üç gerçek kayıt indekslendi')
eq([alan(d,'process.exit_code') for d in r['documents']], [0,1,2], 'gerçek returncode değerleri')
ok(all(type(alan(d,'process.exit_code')) is int for d in r['documents']), 'exit_code tamsayı olmalı')
ok(all(type(alan(d,'process.pid')) is int and alan(d,'process.pid')>0 for d in r['documents']), 'pid tamsayı')
ok(all('@timestamp' in d and alan(d,'process.name') is not None and not any(k in d for k in ['at','exe','pid','rc']) for d in r['documents']), 'ECS yolları ve ham alan temizliği')
aday=[dict(korpus['documents'][0],id='sinir'+str(i),rc=str(v),pid=str(2147483648+i)) for i,v in enumerate([-1,0,1,2147483648])]
r=sonuc(aday)
eq([alan(d,'process.exit_code') for d in r['documents']],[-1,0,1,2147483648], 'long; sabit kod veya 32 bit daraltma yok')
eq([alan(d,'process.pid') for d in r['documents']], [2147483648,2147483649,2147483650,2147483651], 'pid girdiden gelir')
for r in [sonuc(),sonuc(aday)]:
    ok(all(alan(d,'event.kind')=='event' and alan(d,'event.category')==['process'] and alan(d,'event.type')==['end'] for d in r['documents']), 'ECS kategori alanları dizi, kind event')
```

```solution
{
  "processors": [
    {
      "rename": {
        "field": "at",
        "target_field": "@timestamp"
      }
    },
    {
      "rename": {
        "field": "exe",
        "target_field": "process.name"
      }
    },
    {
      "convert": {
        "field": "pid",
        "target_field": "process.pid",
        "type": "long"
      }
    },
    {
      "convert": {
        "field": "rc",
        "target_field": "process.exit_code",
        "type": "long"
      }
    },
    {
      "remove": {
        "field": [
          "pid",
          "rc"
        ]
      }
    },
    {
      "set": {
        "field": "event.kind",
        "value": "event"
      }
    },
    {
      "set": {
        "field": "event.category",
        "value": [
          "process"
        ]
      }
    },
    {
      "set": {
        "field": "event.type",
        "value": [
          "end"
        ]
      }
    }
  ]
}
```

```hint
set işlemcisinde value bir JSON dizisi olabilir.
```

:::
