---
id: sg07
title: Boolean Koşullar ve Dar İstisnalar
summary: and, or, not ve parantezlerle davranışı kurmak; geniş allowlist yerine alanları birlikte sınırlandırmak.
---

::: anlat Seçimlerin adları bir mantık cümlesine dönüşür
Bir kuraldaki seçimler, `condition` içinde `and`, `or` ve `not` ile birleştirilir. `selection and not filter` yaygın bir düzendir: ilgi çekici davranışı bul, bilinen normal biçimi dışla. Ama filtreyi yanlış genişlikte yazarsan aradığın davranışın büyük kısmını da dışarı atarsın.

Filtreye yalnız `User: admin` yazmak, o hesabın bütün etkinliğini görünmez yapar. Beklenen normal iş akışı belirli bir servis hesabı **ve** belirli bir üst süreç ile tanımlanıyorsa, iki alanı aynı filtrede birlikte iste. Bir hesaba güvenmek ile belirli bir davranış biçimini dışlamak aynı şey değildir.

Karışık koşullarda parantez kullan. `(selection_a or selection_b) and not filter` iki ilgi alanına da filtre uygular. Gereksinimi parantezsiz yazıp öncelik kurallarını okuyucuya çözdürmek gereksiz hata ihtimalidir.

```sigma
title: Pafta sg07 Ornek
id: ea652684-9b58-419a-aaf7-a6ac229212b8
status: experimental
logsource:
    category: application
detection:
    selection:
        Action: 'export'
    filter:
        User: 'svc_backup'
        ParentImage: 'backup-agent'
    condition: selection and not filter
level: medium
```
:::

::: anlat Filtreler de test edilmelidir
Bir filtre için en az dört komşu örnek düşün: normal kullanıcı + normal üst süreç; normal kullanıcı + farklı üst süreç; farklı kullanıcı + normal üst süreç; iki alanı da farklı. Yalnız ilk örnek dışlanmalıysa filtrenin bu dört örnek üzerinde bunu yaptığını doğrula.

`not filter`, eksik alanların nasıl davrandığına da bağlıdır. Filtre koşulunun alanı kayıtta yoksa o seçimin eşleşmemesi ve dolayısıyla `not filter`ın doğru olması beklenir. Böyle bir kayıt alarm üretmeli mi? Bu kararı bilinçli ver; eksik telemetriyi otomatik olarak temiz davranış sayma.

> [!TUZAK]
> `filter` sadece seçim adıdır; yazıldığı için kendiliğinden dışlama olmaz. `condition` içinde `not filter` olarak kullanılmadıkça diğer seçimlerden farkı yoktur.

Kaynak: [Sigma resmi belgesi](https://sigmahq.io/docs/basics/conditions.html).
:::

::: tahmin
Girdi kutusundaki sentetik olaylardan hangilerinin `id` değerleri eşleşir? Kuralı ve olayları birlikte oku. Çıktıda eşleşen kimlikler sırayla gösterilir.

```sigma
title: Pafta sg07 Ornek
id: ea652684-9b58-419a-aaf7-a6ac229212b8
status: experimental
logsource:
    category: application
detection:
    selection:
        Action: 'export'
    filter:
        User: 'svc_backup'
        ParentImage: 'backup-agent'
    condition: selection and not filter
level: medium
```

```stdin
[
  {
    "Action": "export",
    "User": "svc_backup",
    "ParentImage": "terminal",
    "id": "e1"
  },
  {
    "Action": "export",
    "User": "svc_backup",
    "ParentImage": "backup-agent",
    "id": "e2"
  }
]
```

???

`e1` eşleşir. `e1` export davranışıdır ama ParentImage terminal olduğu için dar normal filtreyi sağlamaz. `e2` hem svc_backup hem backup-agent değerini taşıdığı için not filter sonucunda dışlanır.
:::

::: gorev Normal yedeklemeyi dar dışla
`Action: export` olaylarını seç; yalnız `User: svc_backup` VE `ParentImage: backup-agent` birlikte olduğunda dışla. svc_backup hesabının terminalden yaptığı export hâlâ eşleşmeli.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg07 Normal yedeklemeyi dar dışla
id: ffcaabac-f5e2-4d1b-8ce3-15eeb44b2f5a
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
    "Action": "export",
    "User": "svc_backup",
    "ParentImage": "terminal",
    "id": "g1-1"
  },
  {
    "Action": "export",
    "User": "analyst",
    "ParentImage": "backup-agent",
    "id": "g1-2"
  },
  {
    "Action": "export",
    "id": "g1-3"
  },
  {
    "Action": "export",
    "User": "svc_backup",
    "ParentImage": "backup-agent",
    "id": "g1-4"
  },
  {
    "Action": "view",
    "User": "analyst",
    "ParentImage": "terminal",
    "id": "g1-5"
  }
]
```

```test
ok(eslesir({'Action': 'export', 'User': 'svc_backup', 'ParentImage': 'terminal'}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'Action': 'export', 'User': 'analyst', 'ParentImage': 'backup-agent'}), 'Olumlu ornek 2 eslesmeli')
ok(eslesir({'Action': 'export'}), 'Olumlu ornek 3 eslesmeli')
ok(not eslesir({'Action': 'export', 'User': 'svc_backup', 'ParentImage': 'backup-agent'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'Action': 'view', 'User': 'analyst', 'ParentImage': 'terminal'}), 'Olumsuz ornek 2 disarida kalmali')
```

```solution
title: Pafta sg07 Normal yedeklemeyi dar dışla
id: a708bbd0-7465-4f6d-ac94-09364ff5540b
status: experimental
logsource:
    category: application
detection:
    selection:
        Action: 'export'
    filter:
        User: 'svc_backup'
        ParentImage: 'backup-agent'
    condition: selection and not filter
level: medium
```

```hint
Filtredeki iki alan aynı sözlükte AND; condition selection and not filter.
```
:::

::: gorev İki eyleme ortak bakım filtresi
`Action` delete veya disable olsun. `ChangeWindow: approved` olan kayıtları iki eylem için de dışla. Diğer eylemleri yakalama.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg07 İki eyleme ortak bakım filtresi
id: dc1fac97-4146-4535-9322-4edc2438b4e4
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
    "Action": "delete",
    "ChangeWindow": "none",
    "id": "g2-1"
  },
  {
    "Action": "disable",
    "ChangeWindow": "none",
    "id": "g2-2"
  },
  {
    "Action": "disable",
    "id": "g2-3"
  },
  {
    "Action": "delete",
    "ChangeWindow": "approved",
    "id": "g2-4"
  },
  {
    "Action": "disable",
    "ChangeWindow": "approved",
    "id": "g2-5"
  },
  {
    "Action": "view",
    "ChangeWindow": "none",
    "id": "g2-6"
  }
]
```

```test
ok(eslesir({'Action': 'delete', 'ChangeWindow': 'none'}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'Action': 'disable', 'ChangeWindow': 'none'}), 'Olumlu ornek 2 eslesmeli')
ok(eslesir({'Action': 'disable'}), 'Olumlu ornek 3 eslesmeli')
ok(not eslesir({'Action': 'delete', 'ChangeWindow': 'approved'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'Action': 'disable', 'ChangeWindow': 'approved'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'Action': 'view', 'ChangeWindow': 'none'}), 'Olumsuz ornek 3 disarida kalmali')
```

```solution
title: Pafta sg07 İki eyleme ortak bakım filtresi
id: ef835421-753f-40f6-87c6-e5a103218549
status: experimental
logsource:
    category: application
detection:
    selection_delete:
        Action: 'delete'
    selection_disable:
        Action: 'disable'
    filter:
        ChangeWindow: 'approved'
    condition: (selection_delete or selection_disable) and not filter
level: medium
```

```hint
İki eylemin OR grubunu paranteze al, sonra ortak not filter ekle.
```
:::
