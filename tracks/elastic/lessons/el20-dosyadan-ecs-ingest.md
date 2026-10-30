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
timeout: 120
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
timeout: 120
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
timeout: 120
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

::: anlat Aynı işi ajan yapınca: Elastic Agent standalone
Şimdiye kadar belgeyi `_bulk` ile sen gönderdin. Sahada bunu çoğunlukla **Elastic Agent** yapar: dosyayı okur, satıra böler, kenarda (ajanda) ayrıştırır ve süzer, sonra bir **veri akışına** (data stream) yazar. Fleet'e bağlı değilse ajan **standalone** çalışır ve politikasını `elastic-agent.yml` dosyasından okur. Konteynerde `FLEET_ENROLL` verilmezse ajan standalone açılır. Dosyadaki `${ELASTICSEARCH_API_KEY}` gibi değerler ortam değişkeninden doldurulur; kimlik bilgisi dosyaya yazılmaz.

Politikanın dört katmanı var:

| Katman | Ne belirler | Bu görevde |
|---|---|---|
| `outputs.default` | Nereye, hangi kimlikle | `hosts` ve `api_key` ortam değişkeni |
| `inputs[].type: filestream` | Hangi dosyalar okunur | `paths` glob'u; `erisim.ndjson.1` döndürülmüş eski dosyadır, `diger.log` başka bir uygulamanın düz metni |
| `parsers` | Satır nasıl olaya dönüşür | `ndjson`: `target: ""` alanları köke koyar; `overwrite_keys: true` olmadan `@timestamp` satırın değil **okuma anının** zamanı olur; `add_error_key: true` bozuk satırı `error.message` ile işaretler |
| `processors` | Kenarda neyin düşeceği | `drop_event` + koşul; ayrıştırmadan sonra çalışır, yani JSON alanına bakabilir |

Veri akışının adı `logs-<dataset>-<namespace>` kuralıyla kurulur: dataset `pafta.erisim`, namespace `lab` ise akış `logs-pafta.erisim-lab` olur. İkisinde de tire olmaz. Elasticsearch'teki hazır `logs` şablonu `logs-*-*` akışlarına ECS eşlemesi uygular. Bu yüzden `source.ip` alanı metin değil `ip` türünde, `http.response.status_code` da `long` olur. Ajan her olaya kendi izini de ekler: `agent.type` (filebeat bileşeni), `input.type`, `log.file.path`, `log.offset` (satırın bayt konumu), `data_stream.*`, `host.*`.

Bozuk bir satır kaybolmaz ama tehlikelidir. Ham metin `message`'da kalır, zamanı **okuma anıdır**. Onu zaman çizelgesine koyan analist, olayı yanlış güne yerleştirir; `error.type: json` ile ayıkla.

**Laboratuvarın sınırı:** Koşucu (`motor: elastic-agent`) gerçek Elastic Agent 9.5.5 konteynerini yalnız `pafta-elastic` ağında başlatır. Dosyaları klasör bağlamadan konteynere kopyalar. 5 dakikalık ve yalnız `logs-pafta.*-*` akışlarına yazabilen bir API anahtarı verir. Namespace'e her çalıştırmada görünmeyen bir ek koyar; iş bitince konteyneri, veri akışını ve anahtarı siler. Politikada yalnız `filestream` girdisi, `ndjson`/`multiline` ayrıştırıcıları ve zararsız işlemciler kabul edilir. İzleme (`agent.monitoring`) kapalı olmalı: ajanın kendi günlüklerini yazacak yetkisi yok. Fleet, entegrasyon paketleri ve Kibana varlıkları bu görevin dışında. İmaj `docker pull docker.elastic.co/elastic-agent/elastic-agent:9.5.5` ile bir kez indirilir; koşucu kendiliğinden indirmez.

Kaynaklar: [standalone ajan](https://www.elastic.co/docs/reference/fleet/install-standalone-elastic-agent), [girdi yapılandırması](https://www.elastic.co/docs/reference/fleet/elastic-agent-input-configuration), [ajan işlemcileri](https://www.elastic.co/docs/reference/fleet/agent-processors), [filestream ve ndjson](https://www.elastic.co/docs/reference/beats/filebeat/filebeat-input-filestream), [veri akışı adlandırma](https://www.elastic.co/docs/reference/fleet/data-streams), [konteynerde ajan](https://www.elastic.co/docs/reference/fleet/elastic-agent-container).
:::

::: gorev Erişim günlüğünü gerçek ajanla al
`/pafta/girdi/` klasöründe üç dosya var: uygulamanın güncel JSON erişim günlüğü `erisim.ndjson`, dünkü döndürülmüş kopyası `erisim.ndjson.1` ve başka bir uygulamanın düz metin günlüğü `diger.log`. Standalone `elastic-agent.yml` politikasını yaz:

- Çıktı `default`: `elasticsearch`, `hosts` `${ELASTICSEARCH_HOSTS}`, `api_key` `${ELASTICSEARCH_API_KEY}`. Kullanıcı adı ya da parola yazma. `agent.monitoring.enabled: false`.
- Tek bir `filestream` girdisi yalnız **güncel** `.ndjson` dosyasını okusun. Veri akışı `logs-pafta.erisim-lab` olsun.
- Satırlar JSON'dur: alanlar köke gelsin, olay zamanı JSON'daki `@timestamp` olsun, bozuk satır işaretlensin.
- Yük dengeleyicinin `/saglik` istekleri ajanda düşsün.

Koşucu politikayı denetler, gerçek ajanı başlatır ve gelen belgeleri, veri akışını ve alan türlerini gerçek Elasticsearch'ten okur (yaklaşık 35 saniye). Çalıştır düğmesi doğrulama hatalarını ve gelen belgelerin özetini gösterir.

```meta
motor: elastic-agent
timeout: 180
```

```setup
{"dosyalar": {
 "erisim.ndjson": "{\"@timestamp\":\"2026-10-19T09:01:00.000Z\",\"source\":{\"ip\":\"203.0.113.7\"},\"user\":{\"name\":\"ayse\"},\"url\":{\"path\":\"/giris\"},\"http\":{\"request\":{\"method\":\"POST\"},\"response\":{\"status_code\":401}},\"event\":{\"outcome\":\"failure\"}}\n{\"@timestamp\":\"2026-10-19T09:01:05.000Z\",\"source\":{\"ip\":\"10.0.0.5\"},\"url\":{\"path\":\"/saglik\"},\"http\":{\"request\":{\"method\":\"GET\"},\"response\":{\"status_code\":200}},\"event\":{\"outcome\":\"success\"}}\n{\"@timestamp\":\"2026-10-19T09:01:10.000Z\",\"source\":{\"ip\":\"203.0.113.7\"},\"user\":{\"name\":\"ayse\"},\"url\":{\"path\":\"/giris\"},\"http\":{\"request\":{\"method\":\"POST\"},\"response\":{\"status_code\":200}},\"event\":{\"outcome\":\"success\"}}\n{\"@timestamp\":\"2026-10-19T09:01:20.000Z\",\"source\":{\"ip\":\"198.51.100.4\"},\"user\":{\"name\":\"can\"\n{\"@timestamp\":\"2026-10-19T09:01:30.000Z\",\"source\":{\"ip\":\"10.0.0.5\"},\"url\":{\"path\":\"/saglik\"},\"http\":{\"request\":{\"method\":\"GET\"},\"response\":{\"status_code\":200}},\"event\":{\"outcome\":\"success\"}}\n{\"@timestamp\":\"2026-10-19T09:02:00.000Z\",\"source\":{\"ip\":\"2001:db8::7\"},\"user\":{\"name\":\"berk\"},\"url\":{\"path\":\"/api/rapor\"},\"http\":{\"request\":{\"method\":\"GET\"},\"response\":{\"status_code\":403}},\"event\":{\"outcome\":\"failure\"}}\n",
 "erisim.ndjson.1": "{\"@timestamp\":\"2026-10-18T23:59:00.000Z\",\"source\":{\"ip\":\"203.0.113.99\"},\"user\":{\"name\":\"eski\"},\"url\":{\"path\":\"/giris\"},\"http\":{\"request\":{\"method\":\"POST\"},\"response\":{\"status_code\":200}},\"event\":{\"outcome\":\"success\"}}\n",
 "diger.log": "2026-10-19 09:00:00 DEBUG zamanlayici basladi\n2026-10-19 09:05:00 DEBUG kuyruk bos\n"
}}
```

```starter
outputs:
  default:
    type: elasticsearch
    hosts: '${ELASTICSEARCH_HOSTS}'
    username: elastic
    password: changeme
inputs:
  - id: pafta-erisim
    type: filestream
    data_stream:
      namespace: default
    streams:
      - id: pafta-erisim-dosya
        data_stream:
          dataset: pafta.genel
        paths:
          - /pafta/girdi/*
        parsers:
          - ndjson:
              target: ""
```

```test
eq(hatalar, [], 'politika sözleşmesi: kimlik bilgisi yalnız ortam değişkeninde, izleme kapalı, yalnız filestream')
eq(akislar, ['logs-pafta.erisim-lab'], 'veri akışı adı logs-<dataset>-<namespace>')
eq(sorted({alan(b, 'log.file.path') for b in belgeler}), ['/pafta/girdi/erisim.ndjson'],
   'yalnız güncel dosya: döndürülmüş erisim.ndjson.1 ve diger.log okunmaz')
eq([alan(b, 'url.path') for b in belgeler], ['/giris', '/giris', None, '/api/rapor'],
   'iki /saglik isteği ajanda düşer; kalanlar dosyadaki sırayla (log.offset)')
eq([alan(b, 'user.name') for b in belgeler], ['ayse', 'ayse', None, 'berk'], 'JSON alanları köke ayrıştırılır (target "")')
eq([alan(b, '@timestamp') for b in belgeler if alan(b, 'error.type') is None],
   ['2026-10-19T09:01:00.000Z', '2026-10-19T09:01:10.000Z', '2026-10-19T09:02:00.000Z'],
   "olay zamanı JSON'dan gelir, okuma anından değil (overwrite_keys)")
bozuk = [b for b in belgeler if alan(b, 'error.type') == 'json']
eq(len(bozuk), 1, 'yarım kalan satır error.type: json ile işaretlenir (add_error_key)')
ok(bool(bozuk) and '198.51.100.4' in (alan(bozuk[0], 'message') or ''), 'bozuk satırın ham metni message alanında kalır', bozuk)
eq({k: alan_turleri.get(k) for k in ('@timestamp', 'source.ip', 'http.response.status_code', 'user.name')},
   {'@timestamp': 'date', 'source.ip': 'ip', 'http.response.status_code': 'long', 'user.name': 'keyword'},
   'logs-*-* şablonunun ECS eşlemesi: IPv6 dahil source.ip türü ip')
eq(({alan(b, 'input.type') for b in belgeler}, {alan(b, 'data_stream.dataset') for b in belgeler}, {alan(b, 'agent.type') for b in belgeler}),
   ({'filestream'}, {'pafta.erisim'}, {'filebeat'}), 'ajanın eklediği iz: girdi türü, veri kümesi, filebeat bileşeni')
```

```solution
outputs:
  default:
    type: elasticsearch
    hosts: '${ELASTICSEARCH_HOSTS}'
    api_key: '${ELASTICSEARCH_API_KEY}'
agent.monitoring.enabled: false
inputs:
  - id: pafta-erisim
    type: filestream
    use_output: default
    data_stream:
      namespace: lab
    streams:
      - id: pafta-erisim-dosya
        data_stream:
          dataset: pafta.erisim
        paths:
          - /pafta/girdi/*.ndjson
        prospector.scanner.check_interval: 1s
        parsers:
          - ndjson:
              target: ""
              overwrite_keys: true
              add_error_key: true
        processors:
          - drop_event:
              when:
                equals:
                  url.path: /saglik
```

```hint
Önce Çalıştır'a bas: kullanıcı adı/parola yerine `api_key: '${ELASTICSEARCH_API_KEY}'` yaz ve `agent.monitoring.enabled: false` ekle. Doğrulama geçince ajan gerçekten çalışır ve gelen belgeleri gösterir.
```

```hint
`/pafta/girdi/*` üç dosyayı da okur. `*.ndjson` döndürülmüş `erisim.ndjson.1`'i dışarıda bırakır. Akış adı dataset ve namespace'ten kurulur: `pafta.erisim` ve `lab`.
```

```hint
`ndjson` ayrıştırıcısında `overwrite_keys: true` ve `add_error_key: true` gerekir. Sağlık kontrolleri için `processors` altında `drop_event` ve `when.equals` ile `url.path: /saglik` koşulunu yaz.
```
:::
