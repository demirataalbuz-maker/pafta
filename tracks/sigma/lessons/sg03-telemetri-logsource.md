---
id: sg03
title: Logsource ve Telemetri Sözleşmesi
summary: Category, product, service; gereken günlük ile detection alanlarının farkı ve kaynak koşullarını açık yazmak.
---

::: anlat Görmediğin olayı tespit edemezsin
Bir davranış mantığı doğru olsa bile olay toplanmıyorsa hiçbir sonuç alamazsın. `logsource`, kuralın hangi tür kayıtlar için tasarlandığını belgeler: `product` ürün/platformu, `category` olay ailesini, `service` daha belirli günlük kaynağını anlatır. Her kuralın üç alanı da doldurması gerekmez; kullandığın kaynağa uygun olanlarını seç.

`process_creation` ve `windows` bir süreç oluşturma kaydına ihtiyaç duyulduğunu belirtir. Ama kurumun Sysmon mu, Security 4688 mi, başka EDR mı kullanıyor? `Image`, `ParentImage` ve `CommandLine` değerlerinin nereden geldiği buna bağlıdır. Bu yüzden gerçek kurala veri toplama önkoşulunu ve gerekli alanları da yaz.

Pafta'nın JSON tezgahına verdiğin kayıtların doğru kaynaktan seçildiğini sen sağlarsın. Tezgah `logsource` yazısından gizli bir `EventID` ya da `Channel` filtresi üretmez. Bu tür bir kayıt alanını ayrıca gerektiriyorsan `detection` içinde açıkça yaz.

```sigma
title: Pafta sg03 Ornek
id: 2a84b2c4-7721-48a5-89d6-659d10ca7748
status: experimental
logsource:
    product: windows
    service: security
detection:
    selection:
        Channel: 'Security'
        EventID: 4625
    condition: selection
level: medium
```
:::

::: anlat Kanal bilgisi ile olay numarası
Olay numarası tek başına her yerde aynı anlamı taşımaz. Sentetik örneğimizde `Channel` alanını da denetleyerek aynı sayıyı kullanan başka uygulama kaydını dışarıda bırakabiliriz. Gerçek Sigma dönüşümünde bu ayırma çoğu zaman backend/pipeline üzerinden uygun indeks ve kaynak seçimiyle yapılır.

Kayıtta alan yoksa önce kuralı zayıflatma. Telemetri toplanmamış, normalleştirme farklı veya alan adı yanlış olabilir. Veri kalitesi problemi ile davranışın gerçekten olmamasını ayırmak gerekir. Bu dersin görevleri, gereksinimi bir cümleden iki açık alan koşuluna çevirmeyi çalıştırır.

Kaynakları birleştirirken `EventID` ile `EventCode`, `Image` ile `process.executable` gibi adların kendiliğinden aynı olmadığını hatırla. Alan eşleme, dağıtım dersinde ayrı bir aşama olacak.

Kaynak: [Sigma resmi belgesi](https://sigmahq.io/docs/basics/log-sources.html).
:::

::: tahmin
Girdi kutusundaki sentetik olaylardan hangilerinin `id` değerleri eşleşir? Kuralı ve olayları birlikte oku. Çıktıda eşleşen kimlikler sırayla gösterilir.

```sigma
title: Pafta sg03 Ornek
id: 2a84b2c4-7721-48a5-89d6-659d10ca7748
status: experimental
logsource:
    product: windows
    service: security
detection:
    selection:
        Channel: 'Security'
        EventID: 4625
    condition: selection
level: medium
```

```stdin
[
  {
    "Channel": "Security",
    "EventID": 4625,
    "id": "e1"
  },
  {
    "Channel": "Application",
    "EventID": 4625,
    "id": "e2"
  }
]
```

???

`e1` eşleşir. İki olayın numarası aynı. `e2` Application kanalından geldiği için Channel koşulunda elenir; logsource metadatası bu açık koşulun yerini tutmuyor.
:::

::: gorev Security kanalını açık yaz
`Channel: Security` ve `EventID: 4625` birlikte olsun. Aynı numaralı Application kaydı ve 4624 dışarıda kalsın.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg03 Security kanalını açık yaz
id: 80ff7621-bb82-4330-bd2d-ff39bcd64498
status: experimental
logsource:
    product: windows
    service: security
detection:
    selection:
        # TODO: gorevdeki davranis kosullarini buraya yaz
    Action: 'TODO'
    condition: selection
level: medium
```

```stdin
[
  {
    "Channel": "Security",
    "EventID": 4625,
    "id": "g1-1"
  },
  {
    "Channel": "Application",
    "EventID": 4625,
    "id": "g1-2"
  },
  {
    "Channel": "Security",
    "EventID": 4624,
    "id": "g1-3"
  },
  {
    "EventID": 4625,
    "id": "g1-4"
  }
]
```

```test
ok(eslesir({'Channel': 'Security', 'EventID': 4625}), 'Olumlu ornek 1 eslesmeli')
ok(not eslesir({'Channel': 'Application', 'EventID': 4625}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'Channel': 'Security', 'EventID': 4624}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'EventID': 4625}), 'Olumsuz ornek 3 disarida kalmali')
```

```solution
title: Pafta sg03 Security kanalını açık yaz
id: 14f95020-1724-43e7-bf7c-697f0a1c3840
status: experimental
logsource:
    product: windows
    service: security
detection:
    selection:
        Channel: 'Security'
        EventID: 4625
    condition: selection
level: medium
```

```hint
logsource ürün bilgisidir; Channel şartını selection içine de yaz.
```
:::

::: gorev Ağ olayını işlem kaydından ayır
Sentetik EDR şemasında `EventType: network_connection` ve `Protocol: tcp` olan kayıtları seç. DNS, UDP veya yalnız aynı alanları taşıyan süreç kaydı yeterli değildir.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg03 Ağ olayını işlem kaydından ayır
id: cc6d922e-400a-4a49-b846-fff89c88a284
status: experimental
logsource:
    category: network_connection
    product: windows
detection:
    selection:
        # TODO: gorevdeki davranis kosullarini buraya yaz
    Action: 'TODO'
    condition: selection
level: medium
```

```stdin
[
  {
    "EventType": "network_connection",
    "Protocol": "tcp",
    "DestinationPort": 443,
    "id": "g2-1"
  },
  {
    "EventType": "process_creation",
    "Protocol": "tcp",
    "id": "g2-2"
  },
  {
    "EventType": "network_connection",
    "Protocol": "udp",
    "id": "g2-3"
  },
  {
    "Protocol": "tcp",
    "id": "g2-4"
  }
]
```

```test
ok(eslesir({'EventType': 'network_connection', 'Protocol': 'tcp', 'DestinationPort': 443}), 'Olumlu ornek 1 eslesmeli')
ok(not eslesir({'EventType': 'process_creation', 'Protocol': 'tcp'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'EventType': 'network_connection', 'Protocol': 'udp'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'Protocol': 'tcp'}), 'Olumsuz ornek 3 disarida kalmali')
```

```solution
title: Pafta sg03 Ağ olayını işlem kaydından ayır
id: 5eee44e2-2f41-4f38-8387-d647fc1192ec
status: experimental
logsource:
    category: network_connection
    product: windows
detection:
    selection:
        EventType: 'network_connection'
        Protocol: 'tcp'
    condition: selection
level: medium
```

```hint
İki kayıt alanını aynı seçime koy.
```
:::
