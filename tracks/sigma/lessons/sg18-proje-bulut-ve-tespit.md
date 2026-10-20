---
id: sg18
title: Proje · Bulut Denetimi ve Tespit Paketi
summary: İki davranış ailesini bağlam ve dar filtreyle birleştirmek; değişken aktörler, sınır değerleri ve son regresyon paketi.
---

::: anlat İki farklı davranışı tek gerekçeyle buluştur
Son projede sentetik bulut denetim kayıtları kullanıyoruz. Birinci davranış, üretim ortamında denetim günlüğünün kapatılmasıdır. İkincisi, üretimde owner rolünün dış danışman hesabına verilmesidir. Bu eylemler aynı kayıtta bir arada olmak zorunda değildir; iki ayrı alternatif olarak OR ile birleşir.

Farklı davranışları tek selection içinde AND yaparsan hiç eşleşmeyen bir kural üretebilirsin. Buna karşılık bütün alanları birbirinden bağımsız OR yaparsan üretimdeki her normal olayı yakalayabilirsin. İki gerekçeyi isimleriyle ayır, her birinin kendi bağlamını birlikte iste.

Kullanıcı ve kaynak IP değişebilir; bunları tek örneğe sabitleme. Kural bir aktör listesi değil, davranış tanımıdır. İkinci görevde dış ağdan yapılan yüksek hacimli export için ayrı bir gereksinim kurarak metin, sayı, CIDR ve dar normal filtreyi birlikte kullanacağız.

```sigma
title: Pafta sg18 Ornek
id: 68207866-2757-4320-b82f-7d3b6a9494b6
status: experimental
logsource:
    category: application
detection:
    selection_audit:
        Environment: 'prod'
        Action: 'audit_disabled'
    selection_role:
        Environment: 'prod'
        Action: 'role_assigned'
        Role: 'owner'
        PrincipalType: 'external'
    condition: selection_audit or selection_role
level: medium
```
:::

::: anlat Bir tespit paketinin bitiş ölçütü
Bir paket, YAML dosyasından fazlasını içerir: davranış tanımı, gereken alanlar, olumlu/olumsuz korpus, bilinen normal senaryolar, dağıtım eşlemesi ve araştırmada bakılacak alanlar. Bu paftanın testleri o paketin yerel mantık katmanını doğrular; gerçek üründeki veri akışı ve alarm dağıtımı ayrıca sınanır.

Kendini sınamak için kurala bakmadan gereksinimden yeni normal ve olumlu örnek üret. Örneği görüp kuralı aynı örneğe yapıştırmak kolaydır; daha önce görmediğin bir varyasyonu doğru sınıflandırmak öğrendiğini daha iyi gösterir.

> [!DERİN]
> Sigma bir tespit tanımlama biçimidir. KQL/SPL sorgulama, SQL veri analizi, Regex metin biçimi, Python ise test ve otomasyon için yanında çalışır. Bu yolun amacı hepsinin yerine tek dil koymak değil, davranış fikrini test edilebilir bir kurala çevirmektir.

Kaynak: [Sigma resmi belgesi](https://sigmahq.io/docs/basics/conditions.html).
:::

::: tahmin
Girdi kutusundaki sentetik olaylardan hangilerinin `id` değerleri eşleşir? Kuralı ve olayları birlikte oku. Çıktıda eşleşen kimlikler sırayla gösterilir.

```sigma
title: Pafta sg18 Ornek
id: 68207866-2757-4320-b82f-7d3b6a9494b6
status: experimental
logsource:
    category: application
detection:
    selection_audit:
        Environment: 'prod'
        Action: 'audit_disabled'
    selection_role:
        Environment: 'prod'
        Action: 'role_assigned'
        Role: 'owner'
        PrincipalType: 'external'
    condition: selection_audit or selection_role
level: medium
```

```stdin
[
  {
    "Environment": "prod",
    "Action": "audit_disabled",
    "id": "e1"
  },
  {
    "Environment": "prod",
    "Action": "role_assigned",
    "Role": "owner",
    "PrincipalType": "external",
    "id": "e2"
  },
  {
    "Environment": "lab",
    "Action": "audit_disabled",
    "id": "e3"
  },
  {
    "Environment": "prod",
    "Action": "role_assigned",
    "Role": "reader",
    "PrincipalType": "external",
    "id": "e4"
  }
]
```

???

`e1`, `e2` eşleşir. İlk olay üretimde audit kapatma, ikinci olay üretimde dış hesaba owner rolü verme alternatifini sağlar. Laboratuvar audit kapatma ve dış hesaba reader rolü verme, ilgili alternatiflerin şartlarını tamamlamaz.
:::

::: gorev İki bulut davranışı
Şu iki alternatiften birini seç: (1) Environment prod VE Action audit_disabled; (2) Environment prod VE Action role_assigned VE Role owner VE PrincipalType external. İç kullanıcı owner ataması, reader ataması ve laboratuvar olayları eşleşmesin.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg18 İki bulut davranışı
id: 81228af4-8a42-479e-83ed-a91652cfe5ee
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
    "Environment": "prod",
    "Action": "audit_disabled",
    "Actor": "ops",
    "id": "g1-1"
  },
  {
    "Environment": "prod",
    "Action": "role_assigned",
    "Role": "owner",
    "PrincipalType": "external",
    "Actor": "other",
    "id": "g1-2"
  },
  {
    "Environment": "lab",
    "Action": "audit_disabled",
    "id": "g1-3"
  },
  {
    "Environment": "prod",
    "Action": "role_assigned",
    "Role": "reader",
    "PrincipalType": "external",
    "id": "g1-4"
  },
  {
    "Environment": "prod",
    "Action": "role_assigned",
    "Role": "owner",
    "PrincipalType": "internal",
    "id": "g1-5"
  },
  {
    "Environment": "prod",
    "Action": "audit_enabled",
    "id": "g1-6"
  }
]
```

```test
ok(eslesir({'Environment': 'prod', 'Action': 'audit_disabled', 'Actor': 'ops'}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'Environment': 'prod', 'Action': 'role_assigned', 'Role': 'owner', 'PrincipalType': 'external', 'Actor': 'other'}), 'Olumlu ornek 2 eslesmeli')
ok(not eslesir({'Environment': 'lab', 'Action': 'audit_disabled'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'Environment': 'prod', 'Action': 'role_assigned', 'Role': 'reader', 'PrincipalType': 'external'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'Environment': 'prod', 'Action': 'role_assigned', 'Role': 'owner', 'PrincipalType': 'internal'}), 'Olumsuz ornek 3 disarida kalmali')
ok(not eslesir({'Environment': 'prod', 'Action': 'audit_enabled'}), 'Olumsuz ornek 4 disarida kalmali')
```

```solution
title: Pafta sg18 İki bulut davranışı
id: c657b79f-2e09-4e43-a9f8-198d07481bd2
status: experimental
logsource:
    category: application
detection:
    selection_audit:
        Environment: 'prod'
        Action: 'audit_disabled'
    selection_role:
        Environment: 'prod'
        Action: 'role_assigned'
        Role: 'owner'
        PrincipalType: 'external'
    condition: selection_audit or selection_role
level: medium
```

```hint
Her alternatif kendi AND koşullarına sahip olsun; condition bunları OR ile birleştirsin.
```
:::

::: gorev Bağlamlı veri dışa aktarma
Environment prod, Action export, DataClass restricted ve BytesSent >= 1000000 olsun; SourceIp alanı bulunsun ve 10.0.0.0/8 içinde olmasın. Yalnız Actor svc_backup VE JobId approved_daily birlikteyse dışla. Diğer aktör/iş kombinasyonları eşleşmeli.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg18 Bağlamlı veri dışa aktarma
id: 45a0117f-3bfa-4e7e-b2d5-3cc090c9c6be
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
    "Environment": "prod",
    "Action": "export",
    "DataClass": "restricted",
    "BytesSent": 1000000,
    "SourceIp": "203.0.113.7",
    "Actor": "demo",
    "JobId": "manual",
    "id": "g2-1"
  },
  {
    "Environment": "prod",
    "Action": "export",
    "DataClass": "restricted",
    "BytesSent": 1000001,
    "SourceIp": "198.51.100.7",
    "Actor": "svc_backup",
    "JobId": "manual",
    "id": "g2-2"
  },
  {
    "Environment": "prod",
    "Action": "export",
    "DataClass": "restricted",
    "BytesSent": 999999,
    "SourceIp": "203.0.113.7",
    "id": "g2-3"
  },
  {
    "Environment": "lab",
    "Action": "export",
    "DataClass": "restricted",
    "BytesSent": 1000000,
    "SourceIp": "203.0.113.7",
    "id": "g2-4"
  },
  {
    "Environment": "prod",
    "Action": "export",
    "DataClass": "public",
    "BytesSent": 1000000,
    "SourceIp": "203.0.113.7",
    "id": "g2-5"
  },
  {
    "Environment": "prod",
    "Action": "export",
    "DataClass": "restricted",
    "BytesSent": 1000000,
    "SourceIp": "10.20.30.40",
    "id": "g2-6"
  },
  {
    "Environment": "prod",
    "Action": "export",
    "DataClass": "restricted",
    "BytesSent": 1000000,
    "SourceIp": "203.0.113.7",
    "Actor": "svc_backup",
    "JobId": "approved_daily",
    "id": "g2-7"
  },
  {
    "Environment": "prod",
    "Action": "export",
    "DataClass": "restricted",
    "BytesSent": 1000000,
    "id": "g2-8"
  }
]
```

```test
ok(eslesir({'Environment': 'prod', 'Action': 'export', 'DataClass': 'restricted', 'BytesSent': 1000000, 'SourceIp': '203.0.113.7', 'Actor': 'demo', 'JobId': 'manual'}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'Environment': 'prod', 'Action': 'export', 'DataClass': 'restricted', 'BytesSent': 1000001, 'SourceIp': '198.51.100.7', 'Actor': 'svc_backup', 'JobId': 'manual'}), 'Olumlu ornek 2 eslesmeli')
ok(not eslesir({'Environment': 'prod', 'Action': 'export', 'DataClass': 'restricted', 'BytesSent': 999999, 'SourceIp': '203.0.113.7'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'Environment': 'lab', 'Action': 'export', 'DataClass': 'restricted', 'BytesSent': 1000000, 'SourceIp': '203.0.113.7'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'Environment': 'prod', 'Action': 'export', 'DataClass': 'public', 'BytesSent': 1000000, 'SourceIp': '203.0.113.7'}), 'Olumsuz ornek 3 disarida kalmali')
ok(not eslesir({'Environment': 'prod', 'Action': 'export', 'DataClass': 'restricted', 'BytesSent': 1000000, 'SourceIp': '10.20.30.40'}), 'Olumsuz ornek 4 disarida kalmali')
ok(not eslesir({'Environment': 'prod', 'Action': 'export', 'DataClass': 'restricted', 'BytesSent': 1000000, 'SourceIp': '203.0.113.7', 'Actor': 'svc_backup', 'JobId': 'approved_daily'}), 'Olumsuz ornek 5 disarida kalmali')
ok(not eslesir({'Environment': 'prod', 'Action': 'export', 'DataClass': 'restricted', 'BytesSent': 1000000}), 'Olumsuz ornek 6 disarida kalmali')
```

```solution
title: Pafta sg18 Bağlamlı veri dışa aktarma
id: 5c96a453-b45d-4bc4-a53a-a26b535191cc
status: experimental
logsource:
    category: application
detection:
    selection:
        Environment: 'prod'
        Action: 'export'
        DataClass: 'restricted'
        BytesSent|gte: 1000000
        SourceIp|exists: true
    filter_internal:
        SourceIp|cidr: '10.0.0.0/8'
    filter_maintenance:
        Actor: 'svc_backup'
        JobId: 'approved_daily'
    condition: selection and not filter_internal and not filter_maintenance
level: medium
```

```hint
Bir pozitif seçim; iç ağ ve dar bakım için iki bağımsız filtre. Sayı sınırına dikkat.
```
:::
