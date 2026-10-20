---
id: sg16
title: Tek Olay ve Korelasyonun Sınırı
summary: Base rule, event_count, value_count ve zaman ilişkisi; korelasyona sağlam bir temel olay kuralı sağlamak.
---

::: anlat and iki ayrı kaydı birleştirmez
`selection_failure and selection_success` yazıp birine EventID 4625, diğerine 4624 koymak, önce başarısız sonra başarılı oturum açmayı aramaz. Tek olayın EventID alanının aynı anda iki farklı sayı olması istenir. Birden fazla olayın ilişkisini tanımlamak başka bir katmandır.

Sigma correlation biçiminde temel kurallara ad veya kimlikle referans verilir; sayım ya da zamansal ilişki, gruplama alanı ve zaman penceresiyle tanımlanır. `event_count` olay sayısını, `value_count` belirtilen alanın farklı değerlerini sayma fikridir; temporal türler olay türlerinin zaman ilişkisini ifade eder. Destek, hedef backend ve sürümle doğrulanmalıdır.

Pafta bu derste korelasyonu çalıştırmaz. Çalıştırdığımız görevler, korelasyona girecek doğru **base rule**u yazar. Daha sonra “aynı kullanıcı için beş dakikada eşik” gibi bir sorguya dönüştürülecek girdinin kalitesini burada sınarız.

```sigma
title: Pafta sg16 Ornek
id: 474015a5-5654-4587-b6fc-5ec52e92a92c
status: experimental
logsource:
    product: windows
    service: security
detection:
    selection:
        EventID: 4625
        LogonType: 3
    condition: selection
level: medium
```
:::

::: anlat Zaman ve gruplama açık bir sözleşmedir
“Çok sayıda başarısız giriş” tek başına eksik gereksinimdir: aynı kullanıcı mı, aynı kaynak IP mi, hangi zaman penceresi, kaç olay ve hangi geç gelen veri politikası? Eşiği yalnız base rule'a sayı olarak eklemek bunları çözmez.

Bu dersin ilk görevi yalnız başarısız ağ oturumlarını, ikinci görevi ise yalnız başarılı ağ oturumlarını seçer. Korpus üzerinde bu iki kümenin karışmadığını görmek, sonraki ilişkili aramanın temelini doğrular. Başarısız giriş olayının tek başına parola saldırısını kanıtlamadığını unutma.

Korelasyon için gereken User, SourceIp ve Timestamp gibi alanlar kayıtta yoksa sorgu sonradan bunları üretemez. Telemetri gereksinimini önceden yaz; eksik alanlı kayıtları uygun veri kalitesi incelemesine ayır.

### Korelasyon dosyasını okumak

Bu **çalıştırılmayan okuma örneği**, temel olayı ve onu kullanan event_count kuralını iki YAML belgesi halinde gösterir. `name` referansı, `group-by` anahtarının tireli yazımı ve `timespan` önemlidir. Beş dakikalık sayımın gerçek ürün davranışı seçilen backend ve zaman penceresi uygulamasıyla ayrıca doğrulanır.

```yaml
title: Pafta Failed Network Logon Base
name: pafta_failed_network_logon
logsource:
    product: windows
    service: security
detection:
    selection:
        EventID: 4625
        LogonType: 3
    condition: selection
---
title: Pafta Repeated Network Logon Failures
status: experimental
correlation:
    type: event_count
    rules:
        - pafta_failed_network_logon
    group-by:
        - TargetUserName
        - IpAddress
    timespan: 5m
    condition:
        gte: 5
```

Bu dosyayı Pafta'nın olay bazındaki Sigma koşucusuna vermek, korelasyonun çalıştırılabildiğini göstermez; koşucu desteklemediği korelasyonu hata olarak bildirmelidir. Aşağıdaki iki görev yalnız base rule mantığını çalıştırır.

Olay numaralarının alan anlamı için: [Microsoft 4625 belgesi](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4625).


Kaynak: [Sigma resmi belgesi](https://sigmahq.io/docs/meta/correlations.html).
:::

::: tahmin
Girdi kutusundaki sentetik olaylardan hangilerinin `id` değerleri eşleşir? Kuralı ve olayları birlikte oku. Çıktıda eşleşen kimlikler sırayla gösterilir.

```sigma
title: Pafta sg16 Ornek
id: 474015a5-5654-4587-b6fc-5ec52e92a92c
status: experimental
logsource:
    product: windows
    service: security
detection:
    selection:
        EventID: 4625
        LogonType: 3
    condition: selection
level: medium
```

```stdin
[
  {
    "EventID": 4625,
    "LogonType": 3,
    "TargetUserName": "demo",
    "id": "e1"
  },
  {
    "EventID": 4624,
    "LogonType": 3,
    "id": "e2"
  },
  {
    "EventID": 4625,
    "LogonType": 2,
    "id": "e3"
  }
]
```

???

`e1` eşleşir. İlk olay hem başarısız giriş numarasını hem ağ oturumu türünü taşır. İkinci başarılı giriş, üçüncü etkileşimli oturumdur. İki ayrı kaydı condition içindeki and ile birleştirmiyoruz.
:::

::: gorev Başarısız ağ oturumu base rule
EventID 4625 ve LogonType 3 birlikte olsun. Kullanıcı adı ve IpAddress alanları da mevcut olsun. Diğer oturum türlerini, başarıları ve korelasyon anahtarı eksik olayları dışla.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg16 Başarısız ağ oturumu base rule
id: bcb778b3-0de3-4f50-a7e4-259950f03ac3
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
    "EventID": 4625,
    "LogonType": 3,
    "TargetUserName": "demo",
    "IpAddress": "203.0.113.5",
    "id": "g1-1"
  },
  {
    "EventID": 4625,
    "LogonType": 3,
    "TargetUserName": "test",
    "IpAddress": "198.51.100.8",
    "id": "g1-2"
  },
  {
    "EventID": 4624,
    "LogonType": 3,
    "TargetUserName": "demo",
    "IpAddress": "203.0.113.5",
    "id": "g1-3"
  },
  {
    "EventID": 4625,
    "LogonType": 2,
    "TargetUserName": "demo",
    "IpAddress": "203.0.113.5",
    "id": "g1-4"
  },
  {
    "EventID": 4625,
    "LogonType": 3,
    "TargetUserName": "demo",
    "id": "g1-5"
  },
  {
    "EventID": 4625,
    "LogonType": 3,
    "IpAddress": "203.0.113.5",
    "id": "g1-6"
  }
]
```

```test
ok(eslesir({'EventID': 4625, 'LogonType': 3, 'TargetUserName': 'demo', 'IpAddress': '203.0.113.5'}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'EventID': 4625, 'LogonType': 3, 'TargetUserName': 'test', 'IpAddress': '198.51.100.8'}), 'Olumlu ornek 2 eslesmeli')
ok(not eslesir({'EventID': 4624, 'LogonType': 3, 'TargetUserName': 'demo', 'IpAddress': '203.0.113.5'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'EventID': 4625, 'LogonType': 2, 'TargetUserName': 'demo', 'IpAddress': '203.0.113.5'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'EventID': 4625, 'LogonType': 3, 'TargetUserName': 'demo'}), 'Olumsuz ornek 3 disarida kalmali')
ok(not eslesir({'EventID': 4625, 'LogonType': 3, 'IpAddress': '203.0.113.5'}), 'Olumsuz ornek 4 disarida kalmali')
```

```solution
title: Pafta sg16 Başarısız ağ oturumu base rule
id: 9335c7d9-2c49-4846-a12a-1279d61a167a
status: experimental
logsource:
    product: windows
    service: security
detection:
    selection:
        EventID: 4625
        LogonType: 3
        TargetUserName|exists: true
        IpAddress|exists: true
    condition: selection
level: medium
```

```hint
Bu görev sayım yapmaz; sayılacak doğru olayları ve gereken alanları seçer.
```
:::

::: gorev Başarılı ağ oturumu base rule
Aynı şemada yalnız EventID 4624 ve LogonType 3 olan kayıtları seç. TargetUserName ve IpAddress mevcut olsun. Başarısız olayları eşleştirme; burada önce/sonra ilişkisi kurulmuyor.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg16 Başarılı ağ oturumu base rule
id: 062821c9-649f-4a16-a0fe-f0bfdb63197e
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
    "EventID": 4624,
    "LogonType": 3,
    "TargetUserName": "demo",
    "IpAddress": "203.0.113.5",
    "id": "g2-1"
  },
  {
    "EventID": 4625,
    "LogonType": 3,
    "TargetUserName": "demo",
    "IpAddress": "203.0.113.5",
    "id": "g2-2"
  },
  {
    "EventID": 4624,
    "LogonType": 2,
    "TargetUserName": "demo",
    "IpAddress": "203.0.113.5",
    "id": "g2-3"
  },
  {
    "EventID": 4624,
    "LogonType": 3,
    "TargetUserName": "demo",
    "id": "g2-4"
  }
]
```

```test
ok(eslesir({'EventID': 4624, 'LogonType': 3, 'TargetUserName': 'demo', 'IpAddress': '203.0.113.5'}), 'Olumlu ornek 1 eslesmeli')
ok(not eslesir({'EventID': 4625, 'LogonType': 3, 'TargetUserName': 'demo', 'IpAddress': '203.0.113.5'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'EventID': 4624, 'LogonType': 2, 'TargetUserName': 'demo', 'IpAddress': '203.0.113.5'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'EventID': 4624, 'LogonType': 3, 'TargetUserName': 'demo'}), 'Olumsuz ornek 3 disarida kalmali')
```

```solution
title: Pafta sg16 Başarılı ağ oturumu base rule
id: 6bdeccbb-ff1b-4abc-891e-fa364ef52ca7
status: experimental
logsource:
    product: windows
    service: security
detection:
    selection:
        EventID: 4624
        LogonType: 3
        TargetUserName|exists: true
        IpAddress|exists: true
    condition: selection
level: medium
```

```hint
Bir önceki görevin yalnız başarısız/başarılı olay numarası ayrımını değiştir; varlık koşulları kalsın.
```
:::
