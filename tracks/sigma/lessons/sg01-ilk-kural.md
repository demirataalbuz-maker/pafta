---
id: sg01
title: Sigma ile İlk Tespit Kuralın
summary: Olay ile kuralın farkı, YAML iskeleti, seçim ve condition; ilk olumlu ve olumsuz örnekler.
---

::: anlat Kural bir davranış sorusudur
Bir olay günlüğü **ne oldu?**, bir tespit kuralı ise **hangi olaylar araştırılmalı?** sorusuna cevap verir. Sigma, bu ikinci soruyu ürünlerden bağımsız bir dosyada ifade etmenin yoludur. Aynı davranış fikri farklı SIEM sorgularına çevrilebilir; alanların ve veri kaynaklarının o ürüne doğru eşlenmesi ayrıca gerekir.

Bu yolda gerçek Sigma YAML yazacaksın. Tezgah, kuralı resmi pySigma ayrıştırıcısıyla okur ve aşağıda anlatılan desteklenen koşulları sentetik JSON olaylarına uygular. Bu, Splunk ya da Sentinel sunucusu değildir; kuralın olay bazındaki mantığını sınadığın yerel çalışma alanıdır.

İlk iskelet üç parçadır: `title` insan için bir ad; `logsource` gereken telemetri; `detection` ise seçimler ve bunları birleştiren `condition`. `selection`, özel bir anahtar sözcük değil, seçime verdiğimiz addır. `condition: selection` o seçimin doğru olmasını ister. YAML'da girinti yapıyı belirler: sekme yerine boşluk kullan.

```sigma
title: Pafta sg01 Ornek
id: 24eb5e04-478d-4789-bb9e-7b186a98a8bd
status: experimental
logsource:
    product: windows
    service: security
detection:
    selection:
        EventID: 4625
    condition: selection
level: medium
```
:::

::: anlat Eşleşme, suç kanıtı değildir
Örnekte tek bir olay numarasını arıyoruz. Bu olayı görmek, tek başına saldırı olduğunu kanıtlamaz. Bir yönetici, otomasyon veya yetkili test aynı kaydı üretebilir. Kuralın amacı araştırma adayı çıkarmaktır; yorum ve bağlam analistin işidir.

Girdi kutusu bir JSON nesnesi, nesne listesi veya satır başına bir JSON olay kabul eder. Alan adları JSON'da nasılsa öyle kullanılmalıdır: `EventID` ile `event_id` farklı alanlardır. Bu yolda olay değerleri yapaydır; makinede bir eylem başlatmıyoruz.

Her görevde hem eşleşmesi gereken hem de eşleşmemesi gereken olaylar var. Yalnız olumlu örneği yakalayan çok geniş bir kural başarılı sayılmaz. Geliştirme döngün: davranışı yaz → en yakın normal örneği ekle → kuralı daralt → eski örnekleri yeniden dene.

Kaynak: [Sigma resmi belgesi](https://sigmahq.io/docs/basics/rules.html).
:::

::: tahmin
Girdi kutusundaki sentetik olaylardan hangilerinin `id` değerleri eşleşir? Kuralı ve olayları birlikte oku. Çıktıda eşleşen kimlikler sırayla gösterilir.

```sigma
title: Pafta sg01 Ornek
id: 24eb5e04-478d-4789-bb9e-7b186a98a8bd
status: experimental
logsource:
    product: windows
    service: security
detection:
    selection:
        EventID: 4625
    condition: selection
level: medium
```

```stdin
[
  {
    "EventID": 4625,
    "User": "deneme",
    "id": "e1"
  },
  {
    "EventID": 4624,
    "User": "deneme",
    "id": "e2"
  }
]
```

???

`e1` eşleşir. `e1`de EventID 4625; `e2`de 4624 var. Bu kural yalnız olay numarasını seçiyor, User değerini değerlendirmiyor.
:::

::: gorev Başarısız oturum açmayı seç
Windows Security olaylarından `EventID` değeri **4625** olanları seç. 4624 başarılı oturum açma olayıdır; onu dahil etme.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg01 Başarısız oturum açmayı seç
id: 97514dd6-af01-42c7-9da1-f63ba8713f19
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
    "TargetUserName": "ayse",
    "id": "g1-1"
  },
  {
    "EventID": 4625,
    "TargetUserName": "test",
    "id": "g1-2"
  },
  {
    "EventID": 4624,
    "TargetUserName": "ayse",
    "id": "g1-3"
  },
  {
    "EventID": 4634,
    "id": "g1-4"
  },
  {
    "id": "g1-5"
  }
]
```

```test
ok(eslesir({'EventID': 4625, 'TargetUserName': 'ayse'}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'EventID': 4625, 'TargetUserName': 'test'}), 'Olumlu ornek 2 eslesmeli')
ok(not eslesir({'EventID': 4624, 'TargetUserName': 'ayse'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'EventID': 4634}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({}), 'Olumsuz ornek 3 disarida kalmali')
```

```solution
title: Pafta sg01 Başarısız oturum açmayı seç
id: e59a9086-acba-4ace-a9a7-7c73f220c338
status: experimental
logsource:
    product: windows
    service: security
detection:
    selection:
        EventID: 4625
    condition: selection
level: medium
```

```hint
Bir selection içinde EventID sayısını yaz; condition aynı seçimin adını kullansın.
```
:::

::: gorev Uygulama eylemi
Uygulamanın `Action` alanı tam olarak `account_disabled` olan olayları yakala. `account_enabled`, `account_disabled_preview` ve alanı olmayan olay eşleşmemeli.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg01 Uygulama eylemi
id: c6db09da-e5a1-4923-bf77-7e3ea87b295e
status: experimental
logsource:
    category: application
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
    "Action": "account_disabled",
    "Actor": "ops",
    "id": "g2-1"
  },
  {
    "Action": "ACCOUNT_DISABLED",
    "id": "g2-2"
  },
  {
    "Action": "account_enabled",
    "id": "g2-3"
  },
  {
    "Action": "account_disabled_preview",
    "id": "g2-4"
  },
  {
    "id": "g2-5"
  }
]
```

```test
ok(eslesir({'Action': 'account_disabled', 'Actor': 'ops'}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'Action': 'ACCOUNT_DISABLED'}), 'Olumlu ornek 2 eslesmeli')
ok(not eslesir({'Action': 'account_enabled'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'Action': 'account_disabled_preview'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({}), 'Olumsuz ornek 3 disarida kalmali')
```

```solution
title: Pafta sg01 Uygulama eylemi
id: d5bf26ed-95d1-441a-b174-475d4d91e0e2
status: experimental
logsource:
    category: application
detection:
    selection:
        Action: 'account_disabled'
    condition: selection
level: medium
```

```hint
Düz bir metin, başına/sonuna * koymadıkça tam değer eşleşmesidir.
```
:::
