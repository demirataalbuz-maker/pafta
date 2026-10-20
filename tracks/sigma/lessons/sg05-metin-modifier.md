---
id: sg05
title: Metin Eşleşmesi ve Joker Karakterler
summary: Tam eşleşme, yıldız ve soru işareti; contains, startswith, endswith ile niyeti açık yazmak.
---

::: anlat Nerede durduğu da bir koşuldur
Dosyanın tam yolu, dosya adı ve komut satırının içindeki bir sözcük aynı tür bilgi değildir. `Image: 'audit.exe'` tam değeri arar. `Image|endswith: '\audit.exe'` farklı klasörlerdeki aynı dosya adını arar. Yol ayırıcısını da istemek `notaudit.exe` gibi benzer adları ayırır.

`contains` değerin herhangi bir yerinde, `startswith` başında, `endswith` sonunda arar. Bunlar niyetini başa/sona rastgele yıldız koymaktan daha açık anlatır. Normal metin eşleşmesi varsayılan olarak büyük-küçük harfe duyarsızdır. Bu davranış, kayıt alan adlarının kendisini değiştirmez.

Sigma metninde `*` sıfır veya daha çok, `?` tek karakteri temsil eden jokerlerdir. Bu, regex değildir: regex'teki `.` ve `+` anlamlarını burada bekleme. Gerçek bir yıldız karakterini aramak gerektiğinde Sigma'nın kaçış kurallarını dikkate al; jokerle dosya yolu kaçışını birbirine karıştırma.

```sigma
title: Pafta sg05 Ornek
id: a1d6a26f-eab2-4ca0-aa41-de7b1f38eabf
status: experimental
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\audit.exe'
    condition: selection
level: medium
```
:::

::: anlat Çok kısa parçalar çok geniş eşleşir
`CommandLine|contains: 'run'`, `prune` gibi beklemediğin değerlerin içinde de bulunabilir. Aradığın parça bir anahtar mı, seçenek mi, tam dosya adı mı? Gereksinimde bunun sınırını yaz. Yalnız bir adın geçmesi çoğu zaman davranışa özgü değildir; daha sonra birkaç bağımsız sinyali birleştireceğiz.

Jokerleri bir sürü dosya adına körce yaymak da tehlikelidir. `*log*` normal bir klasörü, uygulama adını ve uzantıyı birlikte yakalayabilir. Görevlerde aynı ada benzeyen olumsuz örnekler var; testi geçmek için yalnız olumlu yolu görmen yetmez.

> [!NOT]
> Bu yoldaki yollar sentetiktir. Kural, dosyayı açmaz veya programı çalıştırmaz; olayın içindeki metni karşılaştırır.

Kaynak: [Sigma resmi belgesi](https://sigmahq.io/docs/basics/modifiers.html).
:::

::: tahmin
Girdi kutusundaki sentetik olaylardan hangilerinin `id` değerleri eşleşir? Kuralı ve olayları birlikte oku. Çıktıda eşleşen kimlikler sırayla gösterilir.

```sigma
title: Pafta sg05 Ornek
id: a1d6a26f-eab2-4ca0-aa41-de7b1f38eabf
status: experimental
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\audit.exe'
    condition: selection
level: medium
```

```stdin
[
  {
    "Image": "C:\\Tools\\audit.exe",
    "id": "e1"
  },
  {
    "Image": "D:\\Ops\\AUDIT.EXE",
    "id": "e2"
  },
  {
    "Image": "C:\\Tools\\notaudit.exe",
    "id": "e3"
  },
  {
    "Image": "C:\\Tools\\audit.exe.bak",
    "id": "e4"
  }
]
```

???

`e1`, `e2` eşleşir. İlk iki yol dosya adı olarak audit.exe ile biter; büyük harf farkı normal metin karşılaştırmasında engel değildir. notaudit.exe ve audit.exe.bak, istenen yol sonunu sağlamaz.
:::

::: gorev Dosya adını doğru sınırla
`TargetFilename` alanı `.report.json` ile bitsin. `report.json.bak`, `report.txt` veya alanı olmayan kayıt eşleşmesin.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg05 Dosya adını doğru sınırla
id: 189e15c1-ec76-4cab-866e-8292031a501b
status: experimental
logsource:
    category: file_event
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
    "TargetFilename": "C:\\Logs\\daily.report.json",
    "id": "g1-1"
  },
  {
    "TargetFilename": "weekly.REPORT.JSON",
    "id": "g1-2"
  },
  {
    "TargetFilename": "daily.report.json.bak",
    "id": "g1-3"
  },
  {
    "TargetFilename": "report.txt",
    "id": "g1-4"
  },
  {
    "id": "g1-5"
  }
]
```

```test
ok(eslesir({'TargetFilename': 'C:\\Logs\\daily.report.json'}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'TargetFilename': 'weekly.REPORT.JSON'}), 'Olumlu ornek 2 eslesmeli')
ok(not eslesir({'TargetFilename': 'daily.report.json.bak'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'TargetFilename': 'report.txt'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({}), 'Olumsuz ornek 3 disarida kalmali')
```

```solution
title: Pafta sg05 Dosya adını doğru sınırla
id: 9c84e41c-7bdb-499f-8850-64948fdd4094
status: experimental
logsource:
    category: file_event
    product: windows
detection:
    selection:
        TargetFilename|endswith: '.report.json'
    condition: selection
level: medium
```

```hint
Dosya sonunu anlatan endswith modifierını kullan.
```
:::

::: gorev Başlangıç ve içerik
`UrlPath` `/admin/` ile başlasın ve içinde `/export` geçsin. `/public/admin/export` başlangıç şartını sağlamaz; `/admin/users` içerik şartını sağlamaz.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg05 Başlangıç ve içerik
id: 87111d45-3957-4522-9b2d-fe443d5ded06
status: experimental
logsource:
    category: webserver
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
    "UrlPath": "/admin/reports/export",
    "id": "g2-1"
  },
  {
    "UrlPath": "/ADMIN/export?format=json",
    "id": "g2-2"
  },
  {
    "UrlPath": "/public/admin/export",
    "id": "g2-3"
  },
  {
    "UrlPath": "/admin/users",
    "id": "g2-4"
  },
  {
    "UrlPath": "/administrator/export",
    "id": "g2-5"
  }
]
```

```test
ok(eslesir({'UrlPath': '/admin/reports/export'}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'UrlPath': '/ADMIN/export?format=json'}), 'Olumlu ornek 2 eslesmeli')
ok(not eslesir({'UrlPath': '/public/admin/export'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'UrlPath': '/admin/users'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'UrlPath': '/administrator/export'}), 'Olumsuz ornek 3 disarida kalmali')
```

```solution
title: Pafta sg05 Başlangıç ve içerik
id: f73a6e95-42e4-470d-a350-720c73f8e533
status: experimental
logsource:
    category: webserver
detection:
    selection_prefix:
        UrlPath|startswith: '/admin/'
    selection_piece:
        UrlPath|contains: '/export'
    condition: selection_prefix and selection_piece
level: medium
```

```hint
Aynı alanı iki kez aynı sözlükte yazma; iki selection ve and kullan.
```
:::
