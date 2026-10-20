---
id: sg04
title: Seçimler, AND ve OR Listeleri
summary: Aynı eşlemedeki alanlar AND, değer listesi OR; eşleme listeleriyle iki ayrı olay biçimini ifade etmek.
---

::: anlat Bir seçimdeki alanlar birlikte aranır
Bir seçim altındaki `Image` ve `Action` aynı olayda doğru olmalıdır. Bu, mantıksal AND'dir. Bir alanın değerini liste yaptığında ise normal davranış OR'dur: `Action` listedeki değerlerden herhangi biri olabilir. Böylece iki tarayıcı, birkaç olay numarası veya birkaç yönetim eylemi yazılabilir.

Bu iki mantığı karıştırmak çok yaygın bir hatadır. `Image` listesine iki program eklemek, iki sürecin art arda çalışmasını aramaz; tek olayın Image alanının iki seçenekten biri olmasını arar. Olaylar arası ilişki için ayrı korelasyon gerekir.

Seçimin kendisini eşleme listesi olarak da yazabilirsin. Her liste öğesi ayrı bir alternatif, öğenin içindeki alanlar birlikte şarttır. Bu, bir kaynağın `Action: deny`, diğerinin `Result: blocked` dediği iki biçimi tek kuralda modellemeye yarar.

```sigma
title: Pafta sg04 Ornek
id: 9cfbe027-c354-4818-a548-6a2361ad1a6b
status: experimental
logsource:
    category: firewall
detection:
    selection:
        Action:
            - 'deny'
            - 'block'
        Protocol: 'tcp'
    condition: selection
level: medium
```
:::

::: anlat Yakın ama yanlış olaylarla sınamak
Kural iki eşlemeden oluşuyorsa test kümen en az şu biçimleri içersin: birinci alternatifin tam örneği, ikinci alternatifin tam örneği, birinciden bir alanla ikinciden bir alanın yanlış karışımı ve iki alternatiften de uzak normal olay.

Şartları çok geniş bir düz listeye dökmek bu karışımları yanlışlıkla yakalayabilir. İç içe YAML yapısını bir mantık cümlesine çevir: **(A ve B) veya (C ve D)**. Parantezi yazıyla söyleyemiyorsan kuralı düzenlemeden önce gereksinimi sadeleştir.

Bir listede `null` ile metinleri karıştırarak eksik veri sorununu saklama. Eksik/boş alanları ayrı derste ele alacağız; şu an her alternatifin kendi alanları açık olsun.

Kaynak: [Sigma resmi belgesi](https://sigmahq.io/sigma-specification/specification/sigma-rules-specification.html).
:::

::: tahmin
Girdi kutusundaki sentetik olaylardan hangilerinin `id` değerleri eşleşir? Kuralı ve olayları birlikte oku. Çıktıda eşleşen kimlikler sırayla gösterilir.

```sigma
title: Pafta sg04 Ornek
id: 9cfbe027-c354-4818-a548-6a2361ad1a6b
status: experimental
logsource:
    category: firewall
detection:
    selection:
        Action:
            - 'deny'
            - 'block'
        Protocol: 'tcp'
    condition: selection
level: medium
```

```stdin
[
  {
    "Action": "deny",
    "Protocol": "tcp",
    "id": "e1"
  },
  {
    "Action": "block",
    "Protocol": "tcp",
    "id": "e2"
  },
  {
    "Action": "allow",
    "Protocol": "tcp",
    "id": "e3"
  },
  {
    "Action": "deny",
    "Protocol": "udp",
    "id": "e4"
  }
]
```

???

`e1`, `e2` eşleşir. `e1` ve `e2` listedeki iki eylemden birini ve tcp şartını sağlar. `e3`te allow listede yok; `e4`te deny var ama protokol udp.
:::

::: gorev İki araç, tek eylem
`Image`, `C:\Tools\audit.exe` veya `C:\Tools\inventory.exe` olsun; ayrıca `Action: start` gereksin. Diğer eylemleri ve başka klasörleri dışla.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg04 İki araç, tek eylem
id: 772408e7-6db0-41eb-8372-2e34a8a0c32b
status: experimental
logsource:
    category: firewall
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
    "Image": "C:\\Tools\\audit.exe",
    "Action": "start",
    "id": "g1-1"
  },
  {
    "Image": "C:\\Tools\\inventory.exe",
    "Action": "start",
    "id": "g1-2"
  },
  {
    "Image": "C:\\Tools\\audit.exe",
    "Action": "stop",
    "id": "g1-3"
  },
  {
    "Image": "C:\\Temp\\inventory.exe",
    "Action": "start",
    "id": "g1-4"
  },
  {
    "Action": "start",
    "id": "g1-5"
  }
]
```

```test
ok(eslesir({'Image': 'C:\\Tools\\audit.exe', 'Action': 'start'}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'Image': 'C:\\Tools\\inventory.exe', 'Action': 'start'}), 'Olumlu ornek 2 eslesmeli')
ok(not eslesir({'Image': 'C:\\Tools\\audit.exe', 'Action': 'stop'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'Image': 'C:\\Temp\\inventory.exe', 'Action': 'start'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'Action': 'start'}), 'Olumsuz ornek 3 disarida kalmali')
```

```solution
title: Pafta sg04 İki araç, tek eylem
id: 233c8789-f06b-457e-ab16-21f3ee20ce8c
status: experimental
logsource:
    category: firewall
detection:
    selection:
        Image:
            - 'C:\Tools\audit.exe'
            - 'C:\Tools\inventory.exe'
        Action: 'start'
    condition: selection
level: medium
```

```hint
Image altında iki değerli liste; Action aynı seçimde ayrı alan.
```
:::

::: gorev İki farklı kayıt biçimi
`Source: proxy` ile `Action: deny` birlikte VEYA `Source: firewall` ile `Action: drop` birlikte olsun. proxy/drop ve firewall/deny eşleşmesin.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg04 İki farklı kayıt biçimi
id: 889b3f51-a751-4c91-8379-e6996fa3802a
status: experimental
logsource:
    category: firewall
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
    "Source": "proxy",
    "Action": "deny",
    "id": "g2-1"
  },
  {
    "Source": "firewall",
    "Action": "drop",
    "id": "g2-2"
  },
  {
    "Source": "proxy",
    "Action": "drop",
    "id": "g2-3"
  },
  {
    "Source": "firewall",
    "Action": "deny",
    "id": "g2-4"
  },
  {
    "Source": "proxy",
    "Action": "allow",
    "id": "g2-5"
  }
]
```

```test
ok(eslesir({'Source': 'proxy', 'Action': 'deny'}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'Source': 'firewall', 'Action': 'drop'}), 'Olumlu ornek 2 eslesmeli')
ok(not eslesir({'Source': 'proxy', 'Action': 'drop'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'Source': 'firewall', 'Action': 'deny'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'Source': 'proxy', 'Action': 'allow'}), 'Olumsuz ornek 3 disarida kalmali')
```

```solution
title: Pafta sg04 İki farklı kayıt biçimi
id: 2cecc3a3-c0fa-4cce-998a-9f01217b58f9
status: experimental
logsource:
    category: firewall
detection:
    selection:
        - Source: 'proxy'
          Action: 'deny'
        - Source: 'firewall'
          Action: 'drop'
    condition: selection
level: medium
```

```hint
selection altında iki sözlükten oluşan liste kullan; her sözlük kendi Source ve Action çiftini taşısın.
```
:::
