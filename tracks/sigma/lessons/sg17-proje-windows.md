---
id: sg17
title: Proje · Windows Süreç Davranışı
summary: Görüntü, üst süreç ve seçenek parçalarını birleştiren davranış kuralı; dar bakım filtresi ve varyasyon testleri.
---

::: anlat Araç adına bakmaktan davranışa geç
Bu projede çalıştırılabilir adlar ve seçenekler tamamen sentetik: `inventory.exe` ve onun `--scope=all`, `--format=json` seçenekleri kurumun envanter iş akışını temsil ediyor. Amaç, komut üretmek veya bir sisteme müdahale etmek değil; bir süreç olayındaki bağımsız kanıtları bir araya getirmek.

Gereksinim şu: inventory.exe, bir komut yorumlayıcı üst süreçten, bütün kapsam ve JSON biçimi seçenekleriyle çalışmışsa inceleme adayı çıkar. Dosyanın nerede olduğu değişebilir; seçeneklerin sırası da değişebilir. Bu yüzden tam bir komut satırını sabitlemek yerine dosya adı sonları ve contains|all kullanılır.

Bir saldırı tekniği etiketi koymadan önce gözlediğimiz davranışı açıkça tarif edebiliyoruz. Bu kural normal yönetimde de eşleşebilir; proje bunu saklamak yerine ikinci görevde dar bir bakım istisnası ekletiyor.

```sigma
title: Pafta sg17 Ornek
id: 74607075-94a7-4137-88bd-e23298d8d84c
status: experimental
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\inventory.exe'
        ParentImage|endswith: '\cmd.exe'
        CommandLine|contains|all:
            - '--scope=all'
            - '--format=json'
    condition: selection
level: medium
```
:::

::: anlat Proje kabul ölçütleri
Olumlu örnekler, farklı klasörleri ve seçenek sıralarını içerir. Olumsuz örnekler başka program, farklı üst süreç ve eksik seçenekten oluşur. Bakım istisnasında yalnız servis hesabını dışlamak yasak: servis hesabı ile onaylı iş kimliği birlikte bulunmalıdır.

Bu, kuralın davranışını bir test sözleşmesine dönüştürür. Yeni bir bakım akışı gelirse eski kuralın bütün olumlu örneklerini silmeden eklemelisin. “Gürültü çıktı, hesabı komple filtreleyelim” refleksi yerine normal davranışı daha kesin tanımla.

Çalışmayı bitirdiğinde kuralın açıklamasını kendi cümlenle söyle: hangi olay ailesi, hangi üç sinyal, hangi dar normal biçim ve hangi bilinen sınırlamalar? Söyleyemiyorsan YAML'ı daha kısa yazmak bunu çözmez.

Kaynak: [Sigma resmi belgesi](https://sigmahq.io/docs/basics/conditions.html).
:::

::: tahmin
Girdi kutusundaki sentetik olaylardan hangilerinin `id` değerleri eşleşir? Kuralı ve olayları birlikte oku. Çıktıda eşleşen kimlikler sırayla gösterilir.

```sigma
title: Pafta sg17 Ornek
id: 74607075-94a7-4137-88bd-e23298d8d84c
status: experimental
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\inventory.exe'
        ParentImage|endswith: '\cmd.exe'
        CommandLine|contains|all:
            - '--scope=all'
            - '--format=json'
    condition: selection
level: medium
```

```stdin
[
  {
    "Image": "C:\\Tools\\inventory.exe",
    "ParentImage": "C:\\Windows\\System32\\cmd.exe",
    "CommandLine": "inventory --scope=all --format=json",
    "id": "e1"
  },
  {
    "Image": "C:\\Tools\\inventory.exe",
    "ParentImage": "C:\\Ops\\agent.exe",
    "CommandLine": "inventory --scope=all --format=json",
    "id": "e2"
  }
]
```

???

`e1` eşleşir. İlk olayda doğru program, cmd üst süreci ve iki seçenek birlikte var. İkinci olayda üst süreç agent.exe olduğu için diğer parçalar doğru olsa da eşleşme yok.
:::

::: gorev Üç sinyalli davranış
Image `\inventory.exe` ile bitsin. ParentImage `\cmd.exe` VEYA `\powershell.exe` ile bitsin. CommandLine içinde `--scope=all` ve `--format=json` birlikte bulunsun. Seçenek sırası ve klasörler değişebilir.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg17 Üç sinyalli davranış
id: 1f07e27a-ed76-4057-a207-7d57e67cd84b
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
    "ParentImage": "C:\\Windows\\System32\\cmd.exe",
    "CommandLine": "inventory --scope=all --format=json",
    "id": "g1-1"
  },
  {
    "Image": "D:\\Ops\\INVENTORY.EXE",
    "ParentImage": "C:\\Windows\\powershell.exe",
    "CommandLine": "inventory --format=json --scope=all",
    "id": "g1-2"
  },
  {
    "Image": "C:\\Tools\\other.exe",
    "ParentImage": "C:\\Windows\\cmd.exe",
    "CommandLine": "other --scope=all --format=json",
    "id": "g1-3"
  },
  {
    "Image": "C:\\Tools\\inventory.exe",
    "ParentImage": "C:\\Ops\\agent.exe",
    "CommandLine": "inventory --scope=all --format=json",
    "id": "g1-4"
  },
  {
    "Image": "C:\\Tools\\inventory.exe",
    "ParentImage": "C:\\Windows\\cmd.exe",
    "CommandLine": "inventory --scope=all",
    "id": "g1-5"
  }
]
```

```test
ok(eslesir({'Image': 'C:\\Tools\\inventory.exe', 'ParentImage': 'C:\\Windows\\System32\\cmd.exe', 'CommandLine': 'inventory --scope=all --format=json'}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'Image': 'D:\\Ops\\INVENTORY.EXE', 'ParentImage': 'C:\\Windows\\powershell.exe', 'CommandLine': 'inventory --format=json --scope=all'}), 'Olumlu ornek 2 eslesmeli')
ok(not eslesir({'Image': 'C:\\Tools\\other.exe', 'ParentImage': 'C:\\Windows\\cmd.exe', 'CommandLine': 'other --scope=all --format=json'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'Image': 'C:\\Tools\\inventory.exe', 'ParentImage': 'C:\\Ops\\agent.exe', 'CommandLine': 'inventory --scope=all --format=json'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'Image': 'C:\\Tools\\inventory.exe', 'ParentImage': 'C:\\Windows\\cmd.exe', 'CommandLine': 'inventory --scope=all'}), 'Olumsuz ornek 3 disarida kalmali')
```

```solution
title: Pafta sg17 Üç sinyalli davranış
id: 2b804626-1a69-42a5-a08c-6e8dd272555c
status: experimental
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\inventory.exe'
        ParentImage|endswith:
            - '\cmd.exe'
            - '\powershell.exe'
        CommandLine|contains|all:
            - '--scope=all'
            - '--format=json'
    condition: selection
level: medium
```

```hint
ParentImage listesi OR; CommandLine listesi |all; üç alan aynı seçimde AND.
```
:::

::: gorev Dar bakım istisnası
İlk görevin davranışını koru. Yalnız User `svc_inventory` VE JobId `approved_daily` birlikteyse dışla. Aynı hesabın başka iş kimliği veya farklı hesabın aynı iş kimliği hâlâ eşleşsin.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg17 Dar bakım istisnası
id: 68403232-4d8a-4a0a-8304-20c58b11250a
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
    "ParentImage": "C:\\Windows\\cmd.exe",
    "CommandLine": "inventory --scope=all --format=json",
    "User": "svc_inventory",
    "JobId": "manual",
    "id": "g2-1"
  },
  {
    "Image": "C:\\Tools\\inventory.exe",
    "ParentImage": "C:\\Windows\\powershell.exe",
    "CommandLine": "inventory --format=json --scope=all",
    "User": "analyst",
    "JobId": "approved_daily",
    "id": "g2-2"
  },
  {
    "Image": "C:\\Tools\\inventory.exe",
    "ParentImage": "C:\\Windows\\cmd.exe",
    "CommandLine": "inventory --scope=all --format=json",
    "User": "svc_inventory",
    "JobId": "approved_daily",
    "id": "g2-3"
  },
  {
    "Image": "C:\\Tools\\inventory.exe",
    "ParentImage": "C:\\Windows\\cmd.exe",
    "CommandLine": "inventory --scope=all",
    "User": "analyst",
    "JobId": "manual",
    "id": "g2-4"
  }
]
```

```test
ok(eslesir({'Image': 'C:\\Tools\\inventory.exe', 'ParentImage': 'C:\\Windows\\cmd.exe', 'CommandLine': 'inventory --scope=all --format=json', 'User': 'svc_inventory', 'JobId': 'manual'}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'Image': 'C:\\Tools\\inventory.exe', 'ParentImage': 'C:\\Windows\\powershell.exe', 'CommandLine': 'inventory --format=json --scope=all', 'User': 'analyst', 'JobId': 'approved_daily'}), 'Olumlu ornek 2 eslesmeli')
ok(not eslesir({'Image': 'C:\\Tools\\inventory.exe', 'ParentImage': 'C:\\Windows\\cmd.exe', 'CommandLine': 'inventory --scope=all --format=json', 'User': 'svc_inventory', 'JobId': 'approved_daily'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'Image': 'C:\\Tools\\inventory.exe', 'ParentImage': 'C:\\Windows\\cmd.exe', 'CommandLine': 'inventory --scope=all', 'User': 'analyst', 'JobId': 'manual'}), 'Olumsuz ornek 2 disarida kalmali')
```

```solution
title: Pafta sg17 Dar bakım istisnası
id: c07ae141-e7ca-4eff-9e80-1c23d1a5ffa9
status: experimental
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\inventory.exe'
        ParentImage|endswith:
            - '\cmd.exe'
            - '\powershell.exe'
        CommandLine|contains|all:
            - '--scope=all'
            - '--format=json'
    filter_maintenance:
        User: 'svc_inventory'
        JobId: 'approved_daily'
    condition: selection and not filter_maintenance
level: medium
```

```hint
Bakım filtresinin iki alanı aynı sözlükte; pozitif davranış şartları aynen kalsın.
```
:::
