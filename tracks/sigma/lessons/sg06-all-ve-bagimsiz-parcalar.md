---
id: sg06
title: Liste OR ile contains|all Farkı
summary: Birden fazla parçanın sıradan bağımsız birlikte bulunması; tek parça, tüm parçalar ve ayrı alan koşulları.
---

::: anlat İkisi de mi, herhangi biri mi?
`CommandLine|contains` altında iki değerli liste, komut satırında parçalardan **birinin** bulunmasını yeterli sayar. `CommandLine|contains|all` aynı değerlerin **hepsini** ister. Parçaların sırası sabit değildir; aralarında başka metin bulunabilir.

Bu ayrım, bilinen yönetim komutlarının belirli kullanım biçimlerini tarif ederken önemlidir. Örneğin `--format` tek başına çok yaygınken `--format` ile `--output` birlikte daha belirli bir iş akışına işaret eder. Yine de bu çiftin kötü niyet kanıtı olduğunu söylemeyiz; görevimiz belirtilen davranış biçimini seçmektir.

`all`, iki veya daha çok değerli liste üzerinde anlam kazanır. Tek bir değere `all` ekleyerek aynı alanı ikinci kez yazma sorununu çözmeye çalışma; ayrı seçimler daha okunaklıdır. Bu derste yalnız literal metin parçaları kullanıyoruz.

```sigma
title: Pafta sg06 Ornek
id: edbde5a9-50d9-49e9-ba22-5044d5459c13
status: experimental
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        CommandLine|contains|all:
            - '--format'
            - '--output'
    condition: selection
level: medium
```
:::

::: anlat Sıra bağımlılığı gereksiz kaçırma yaratır
`'--format json --output'` bütününü aramak, seçenekler yer değiştirince kaçırır. İki bağımsız parçayı `all` ile istemek, sıraya duyarlı olmayan gereksinimi daha doğru ifade eder. Buna karşılık seçenek değerinin de önemli olduğu durumda yalnız seçenek adlarını istemek fazla geniş kalır.

Testler bu yüzden sırası değiştirilmiş bir olumlu örneği ve yalnız bir parçayı taşıyan iki olumsuz örneği içerir. Sadece standart komut satırını kopyalayarak yazılan bir kural, bu varyasyonları görmeden güven vermemelidir.

Olayın hem belirli bir uygulamadan gelmesi hem de birkaç metin parçasını taşıması gerekiyorsa `Image` ile `CommandLine|contains|all` aynı seçimde bulunabilir. Alanlar arası AND ile liste içindeki ALL birbirinden farklı iki seviyedir.

Kaynak: [Sigma resmi belgesi](https://sigmahq.io/docs/basics/modifiers.html).
:::

::: tahmin
Girdi kutusundaki sentetik olaylardan hangilerinin `id` değerleri eşleşir? Kuralı ve olayları birlikte oku. Çıktıda eşleşen kimlikler sırayla gösterilir.

```sigma
title: Pafta sg06 Ornek
id: edbde5a9-50d9-49e9-ba22-5044d5459c13
status: experimental
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        CommandLine|contains|all:
            - '--format'
            - '--output'
    condition: selection
level: medium
```

```stdin
[
  {
    "CommandLine": "report --format json --output out.json",
    "id": "e1"
  },
  {
    "CommandLine": "report --output out.json --format json",
    "id": "e2"
  },
  {
    "CommandLine": "report --format json",
    "id": "e3"
  },
  {
    "CommandLine": "report --output out.json",
    "id": "e4"
  }
]
```

???

`e1`, `e2` eşleşir. İlk iki komut satırı iki parçayı da taşır; sıraları farklıdır ama all bunu önemsemez. Son iki kayıt yalnız bir parçayı taşıdığı için elenir.
:::

::: gorev İki alan adı parçası
`Message` içinde hem `account=` hem `result=blocked` bulunmalı; sıraları değişebilir. Yalnız birini taşıyan mesaj yeterli değildir.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg06 İki alan adı parçası
id: 8398af0a-dfc0-4943-b074-6979c2aa560b
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
    "Message": "account=demo result=blocked",
    "id": "g1-1"
  },
  {
    "Message": "result=blocked account=test",
    "id": "g1-2"
  },
  {
    "Message": "account=demo result=allowed",
    "id": "g1-3"
  },
  {
    "Message": "result=blocked",
    "id": "g1-4"
  },
  {
    "Message": "account=demo",
    "id": "g1-5"
  }
]
```

```test
ok(eslesir({'Message': 'account=demo result=blocked'}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'Message': 'result=blocked account=test'}), 'Olumlu ornek 2 eslesmeli')
ok(not eslesir({'Message': 'account=demo result=allowed'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'Message': 'result=blocked'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'Message': 'account=demo'}), 'Olumsuz ornek 3 disarida kalmali')
```

```solution
title: Pafta sg06 İki alan adı parçası
id: cbe9bab6-71c4-4b84-951a-a1f74183fcd5
status: experimental
logsource:
    category: application
detection:
    selection:
        Message|contains|all:
            - 'account='
            - 'result=blocked'
    condition: selection
level: medium
```

```hint
contains listesini varsayılan OR bırakma; |all ekle.
```
:::

::: gorev Uygulama bağlamını da iste
`Image` `\inventory.exe` ile bitsin ve `CommandLine` içinde hem `--scope=hosts` hem `--format=json` olsun. Başka program aynı seçenekleri kullansa da eşleşmesin.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg06 Uygulama bağlamını da iste
id: 14af81e3-7ea1-497a-8fe9-ac25faf09ca7
status: experimental
logsource:
    category: process_creation
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
    "Image": "C:\\Tools\\inventory.exe",
    "CommandLine": "inventory --scope=hosts --format=json",
    "id": "g2-1"
  },
  {
    "Image": "D:\\inventory.exe",
    "CommandLine": "inventory --format=json --scope=hosts",
    "id": "g2-2"
  },
  {
    "Image": "C:\\Tools\\other.exe",
    "CommandLine": "other --scope=hosts --format=json",
    "id": "g2-3"
  },
  {
    "Image": "C:\\inventory.exe",
    "CommandLine": "inventory --scope=hosts",
    "id": "g2-4"
  },
  {
    "Image": "C:\\inventory.exe",
    "CommandLine": "inventory --format=json",
    "id": "g2-5"
  }
]
```

```test
ok(eslesir({'Image': 'C:\\Tools\\inventory.exe', 'CommandLine': 'inventory --scope=hosts --format=json'}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'Image': 'D:\\inventory.exe', 'CommandLine': 'inventory --format=json --scope=hosts'}), 'Olumlu ornek 2 eslesmeli')
ok(not eslesir({'Image': 'C:\\Tools\\other.exe', 'CommandLine': 'other --scope=hosts --format=json'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'Image': 'C:\\inventory.exe', 'CommandLine': 'inventory --scope=hosts'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'Image': 'C:\\inventory.exe', 'CommandLine': 'inventory --format=json'}), 'Olumsuz ornek 3 disarida kalmali')
```

```solution
title: Pafta sg06 Uygulama bağlamını da iste
id: 88bc0861-6d92-4d64-9238-c44af6c681c9
status: experimental
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\inventory.exe'
        CommandLine|contains|all:
            - '--scope=hosts'
            - '--format=json'
    condition: selection
level: medium
```

```hint
Image koşulu ile contains|all listesini aynı selection altında birleştir.
```
:::
