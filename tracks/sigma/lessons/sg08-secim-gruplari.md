---
id: sg08
title: 1 of ve all of Seçim Grupları
summary: Seçim adlarını jokerle gruplamak, 1 of/all of koşulları ve gelecekte eklenen filtrelerin mantığa etkisi.
---

::: anlat Seçim adları da bir arayüzdür
Birden çok benzer seçim olduğunda `1 of selection_*`, adı bu kalıba uyan seçimlerden en az birinin doğru olmasını ister. `all of selection_*` hepsini ister. Buradaki yıldız olay değerinde değil, kuralın içindeki seçim adlarındadır.

Örneğin `selection_image`, `selection_parent` ve `selection_args` üç ayrı sinyalse `all of selection_*` bu üçünün aynı olayda gerçekleşmesini arar. Üç ayrı olayın art arda gelmesini anlatmaz. Seçim adlarının rolünü belirgin tut: `selection_` davranış, `filter_` dar normal biçimler olabilir.

`all of them` kısa görünse de sonradan eklediğin bir filtreyi istemeden pozitif şart yapabilir. Okuyucunun hangi gruptan söz edildiğini görmesi için çoğu görevde belirli önekleri kullanacağız.

```sigma
title: Pafta sg08 Ornek
id: 208874d6-6631-4ee7-bc28-c5457e54fe08
status: experimental
logsource:
    category: process_creation
    product: windows
detection:
    selection_a:
        Action: 'disable'
    selection_b:
        Action: 'delete'
    condition: 1 of selection_*
level: medium
```
:::

::: anlat Genişleyen kuralın testi de genişlemeli
Bir kural grubuna yeni seçim eklersen `all of` daha kısıtlayıcı, `1 of` daha geniş hale gelir. Bu bir biçim değişikliği değildir; tespit kapsamını değiştirir. İncelemede yeni seçimin hangi eski örnekleri etkilediğini göster.

Filtreleri `not 1 of filter_*` ile gruplayabilirsin: filtrelerden herhangi biri doğruysa olay dışlanır. Bu, `not all of filter_*` ile aynı değildir; ikincisi tüm filtrelerin aynı anda doğru olmasını bekler. Görevler bu farkı ayrı normal nedenlerle sınar.

Kuralın görevi açıkça OR ise bir liste de kullanılabilir. Seçim gruplarının asıl faydası yalnız kısa yazmak değil, farklı gerekçeleri ayrı adlarla okunabilir tutmaktır.

Kaynak: [Sigma resmi belgesi](https://sigmahq.io/docs/basics/conditions.html).
:::

::: tahmin
Girdi kutusundaki sentetik olaylardan hangilerinin `id` değerleri eşleşir? Kuralı ve olayları birlikte oku. Çıktıda eşleşen kimlikler sırayla gösterilir.

```sigma
title: Pafta sg08 Ornek
id: 208874d6-6631-4ee7-bc28-c5457e54fe08
status: experimental
logsource:
    category: process_creation
    product: windows
detection:
    selection_a:
        Action: 'disable'
    selection_b:
        Action: 'delete'
    condition: 1 of selection_*
level: medium
```

```stdin
[
  {
    "Action": "disable",
    "id": "e1"
  },
  {
    "Action": "delete",
    "id": "e2"
  },
  {
    "Action": "view",
    "id": "e3"
  }
]
```

???

`e1`, `e2` eşleşir. İlk iki olay sırasıyla selection_a ve selection_b ile eşleşir. 1 of grubu için bu yeterlidir. view eylemi ikisine de uymaz.
:::

::: gorev Üç alternatiften biri
`Action` değerlerinden create_token, add_member veya change_policy herhangi biri eşleşsin. Seçimleri selection_ önekiyle adlandır ve condition içinde `1 of selection_*` kullan.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg08 Üç alternatiften biri
id: 14329f35-1fbd-405e-9d87-af63e620f422
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
    "Action": "create_token",
    "id": "g1-1"
  },
  {
    "Action": "add_member",
    "id": "g1-2"
  },
  {
    "Action": "change_policy",
    "id": "g1-3"
  },
  {
    "Action": "view_token",
    "id": "g1-4"
  },
  {
    "Action": "remove_member",
    "id": "g1-5"
  },
  {
    "id": "g1-6"
  }
]
```

```test
ok(eslesir({'Action': 'create_token'}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'Action': 'add_member'}), 'Olumlu ornek 2 eslesmeli')
ok(eslesir({'Action': 'change_policy'}), 'Olumlu ornek 3 eslesmeli')
ok(not eslesir({'Action': 'view_token'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'Action': 'remove_member'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({}), 'Olumsuz ornek 3 disarida kalmali')
ok('1 of selection_*' in src, 'Koşulda seçim grubunu kullan')
```

```solution
title: Pafta sg08 Üç alternatiften biri
id: c7567844-c439-4a2b-b704-70ba30bc1a7a
status: experimental
logsource:
    category: application
detection:
    selection_token:
        Action: 'create_token'
    selection_member:
        Action: 'add_member'
    selection_policy:
        Action: 'change_policy'
    condition: 1 of selection_*
level: medium
```

```hint
Üç seçim aynı öneke sahip olsun; yıldız seçim adlarını toplar.
```
:::

::: gorev Üç sinyal ve iki normal neden
Aynı olayda Image `\audit.exe` ile bitsin, CommandLine `--scope=all` içersin ve IntegrityLevel `High` olsun. Ayrıca User `svc_inventory` ise VEYA Host `lab-workstation` ise dışla. selection_ ve filter_ gruplarını kullan.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg08 Üç sinyal ve iki normal neden
id: ab6beaee-d563-4eb6-a7b5-7afcb40528aa
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
    "Image": "C:\\Tools\\audit.exe",
    "CommandLine": "audit --scope=all",
    "IntegrityLevel": "High",
    "User": "demo",
    "Host": "host01",
    "id": "g2-1"
  },
  {
    "Image": "C:\\Tools\\audit.exe",
    "CommandLine": "audit --scope=all",
    "IntegrityLevel": "Medium",
    "id": "g2-2"
  },
  {
    "Image": "C:\\Tools\\audit.exe",
    "CommandLine": "audit --scope=all",
    "IntegrityLevel": "High",
    "User": "svc_inventory",
    "Host": "host01",
    "id": "g2-3"
  },
  {
    "Image": "C:\\Tools\\audit.exe",
    "CommandLine": "audit --scope=all",
    "IntegrityLevel": "High",
    "User": "demo",
    "Host": "lab-workstation",
    "id": "g2-4"
  }
]
```

```test
ok(eslesir({'Image': 'C:\\Tools\\audit.exe', 'CommandLine': 'audit --scope=all', 'IntegrityLevel': 'High', 'User': 'demo', 'Host': 'host01'}), 'Olumlu ornek 1 eslesmeli')
ok(not eslesir({'Image': 'C:\\Tools\\audit.exe', 'CommandLine': 'audit --scope=all', 'IntegrityLevel': 'Medium'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'Image': 'C:\\Tools\\audit.exe', 'CommandLine': 'audit --scope=all', 'IntegrityLevel': 'High', 'User': 'svc_inventory', 'Host': 'host01'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'Image': 'C:\\Tools\\audit.exe', 'CommandLine': 'audit --scope=all', 'IntegrityLevel': 'High', 'User': 'demo', 'Host': 'lab-workstation'}), 'Olumsuz ornek 3 disarida kalmali')
ok('all of selection_*' in src and '1 of filter_*' in src, 'İki seçim grubunu kullan')
```

```solution
title: Pafta sg08 Üç sinyal ve iki normal neden
id: c7dcd78d-e54d-4eda-821a-a49f4f18c5df
status: experimental
logsource:
    category: process_creation
    product: windows
detection:
    selection_image:
        Image|endswith: '\audit.exe'
    selection_args:
        CommandLine|contains: '--scope=all'
    selection_level:
        IntegrityLevel: 'High'
    filter_service:
        User: 'svc_inventory'
    filter_lab:
        Host: 'lab-workstation'
    condition: all of selection_* and not 1 of filter_*
level: medium
```

```hint
all of selection_* hepsini ister; not 1 of filter_* iki normal nedenden herhangi birini dışlar.
```
:::
