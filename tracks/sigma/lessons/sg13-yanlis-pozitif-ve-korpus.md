---
id: sg13
title: Yanlış Pozitifler ve Regresyon Kümesi
summary: Davranışı çok geniş yazmamak; normal karşı örnekler, değişen değerler ve küçük veri kümesi üzerinde seçim doğruluğu.
---

::: anlat Bir örneği yakalamak kolaydır
Bir olayın bütün alanlarını kopyalarsan o örneği yakalayan bir imza yazmış olursun; davranışı genellemiş sayılmazsın. Tam tersine yalnız araç adı aramak da normal kullanımı alarmla doldurabilir. İyi bir gereksinim, değişebilen ayrıntılar ile davranışa ait işaretleri ayırır.

Bu dersin sentetik uygulamasında dışarı veri verme davranışını `Action: export`, `DataClass: restricted` ve `Approved: false` birlikte tanımlıyor. Kullanıcı adı, makine adı ve dosya adı kuralın tanımında yok; bunların değişmesi eşleşmeyi bozmamalıdır. Onaylanmış export normal karşı örnektir.

Korpus, bu tür etiketlenmiş örnekler kümesidir. En az olumlu, benzer normal ve ilgisiz normal olaylar içersin. Beklenmedik bir eşleşmenin sebebini anlayabilmek için her örneğe benzersiz bir `id` eklemek kullanışlıdır.

```sigma
title: Pafta sg13 Ornek
id: 81ced25d-91b6-4284-9c1d-bba3c0d52b01
status: experimental
logsource:
    category: application
detection:
    selection:
        Action: 'export'
        DataClass: 'restricted'
        Approved: false
    condition: selection
level: medium
```
:::

::: anlat Test başarısı ile ortam başarısı
Bir test kümesinde tüm örnekleri doğru sınıflandırmak, ortamda sıfır yanlış pozitif garantisi vermez. Küme normal iş akışlarını yeterince temsil etmiyor olabilir. Yeni normal örnek geldiğinde onu silmek yerine kümede tut; kural değişikliğinin gelecekte aynı gürültüyü üretmesini önler.

`falsepositives` metadatası normal açıklamaları belgeler; olayları otomatik dışlamaz. Dışlama istiyorsan `detection` ve `condition` içinde yazman gerekir. Kuralın neden çalıştığını, hangi alanlara bağımlı olduğunu ve bilinen kaçırma ihtimallerini de yanında tut.

Bu görevlerde `eslesenler` ile bütün korpusu süzüyoruz. İlk kuralı değiştirince yalnız yeni örneğe bakma; eski olumlu kayıtların da hâlâ yakalandığını göster.

Kaynak: [Sigma resmi belgesi](https://sigmahq.io/sigma-specification/specification/sigma-rules-specification.html).
:::

::: tahmin
Girdi kutusundaki sentetik olaylardan hangilerinin `id` değerleri eşleşir? Kuralı ve olayları birlikte oku. Çıktıda eşleşen kimlikler sırayla gösterilir.

```sigma
title: Pafta sg13 Ornek
id: 81ced25d-91b6-4284-9c1d-bba3c0d52b01
status: experimental
logsource:
    category: application
detection:
    selection:
        Action: 'export'
        DataClass: 'restricted'
        Approved: false
    condition: selection
level: medium
```

```stdin
[
  {
    "id": "e1",
    "Action": "export",
    "DataClass": "restricted",
    "Approved": false
  },
  {
    "id": "e2",
    "Action": "export",
    "DataClass": "restricted",
    "Approved": true
  },
  {
    "id": "e3",
    "Action": "view",
    "DataClass": "restricted",
    "Approved": false
  }
]
```

???

`e1` eşleşir. `e1`de üç davranış şartı birlikte var. `e2` onaylanmış export, `e3` ise export değil view olduğu için benzer alanlar taşısalar da seçilmezler.
:::

::: gorev Örneğe değil davranışa bağlan
Action export, DataClass restricted ve Approved false birlikte olsun. Kullanıcı ve Host değişebilir; bunları belirli tek bir değere bağlama. Onaylı ve public veriyi dışla.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg13 Örneğe değil davranışa bağlan
id: 14e9812e-7f3c-4b77-9b6e-8d42ca348e6f
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
    "DataClass": "restricted",
    "Approved": false,
    "User": "demo",
    "Host": "pc1",
    "id": "g1-1"
  },
  {
    "Action": "export",
    "DataClass": "restricted",
    "Approved": false,
    "User": "other",
    "Host": "pc99",
    "id": "g1-2"
  },
  {
    "Action": "export",
    "DataClass": "restricted",
    "Approved": true,
    "id": "g1-3"
  },
  {
    "Action": "export",
    "DataClass": "public",
    "Approved": false,
    "id": "g1-4"
  },
  {
    "Action": "view",
    "DataClass": "restricted",
    "Approved": false,
    "id": "g1-5"
  }
]
```

```test
ok(eslesir({'Action': 'export', 'DataClass': 'restricted', 'Approved': False, 'User': 'demo', 'Host': 'pc1'}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'Action': 'export', 'DataClass': 'restricted', 'Approved': False, 'User': 'other', 'Host': 'pc99'}), 'Olumlu ornek 2 eslesmeli')
ok(not eslesir({'Action': 'export', 'DataClass': 'restricted', 'Approved': True}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'Action': 'export', 'DataClass': 'public', 'Approved': False}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'Action': 'view', 'DataClass': 'restricted', 'Approved': False}), 'Olumsuz ornek 3 disarida kalmali')
```

```solution
title: Pafta sg13 Örneğe değil davranışa bağlan
id: 01bc0f7d-4766-4929-9e6c-ff358a799518
status: experimental
logsource:
    category: application
detection:
    selection:
        Action: 'export'
        DataClass: 'restricted'
        Approved: false
    condition: selection
level: medium
```

```hint
Davranışın üç alanını seç; User ve Host öğrenme örneğinin değişebilen ayrıntıları.
```
:::

::: gorev Korpusu birlikte süz
Action policy_changed ve Enabled false olanları seç. Bilinen test ortamı Environment lab ise dışla. Kullanıcı adını filtreleme. Korpus sırası korunarak yalnız a ve d eşleşmeli.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg13 Korpusu birlikte süz
id: 0e223a0e-fc12-4d7d-8683-e868982daf43
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
    "id": "a",
    "Action": "policy_changed",
    "Enabled": false,
    "Environment": "prod",
    "User": "admin"
  },
  {
    "id": "d",
    "Action": "policy_changed",
    "Enabled": false,
    "Environment": "prod",
    "User": "service"
  },
  {
    "id": "b",
    "Action": "policy_changed",
    "Enabled": true,
    "Environment": "prod"
  },
  {
    "id": "c",
    "Action": "policy_changed",
    "Enabled": false,
    "Environment": "lab"
  },
  {
    "id": "e",
    "Action": "policy_viewed",
    "Enabled": false,
    "Environment": "prod"
  }
]
```

```test
ok(eslesir({'id': 'a', 'Action': 'policy_changed', 'Enabled': False, 'Environment': 'prod', 'User': 'admin'}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'id': 'd', 'Action': 'policy_changed', 'Enabled': False, 'Environment': 'prod', 'User': 'service'}), 'Olumlu ornek 2 eslesmeli')
ok(not eslesir({'id': 'b', 'Action': 'policy_changed', 'Enabled': True, 'Environment': 'prod'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'id': 'c', 'Action': 'policy_changed', 'Enabled': False, 'Environment': 'lab'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'id': 'e', 'Action': 'policy_viewed', 'Enabled': False, 'Environment': 'prod'}), 'Olumsuz ornek 3 disarida kalmali')
corpus = [{'id':'a','Action':'policy_changed','Enabled':False,'Environment':'prod'}, {'id':'b','Action':'policy_changed','Enabled':True,'Environment':'prod'}, {'id':'c','Action':'policy_changed','Enabled':False,'Environment':'lab'}, {'id':'d','Action':'policy_changed','Enabled':False,'Environment':'prod'}]
eq([e['id'] for e in eslesenler(corpus)], ['a','d'], 'Korpusun yalnız a ve d kayıtları, aynı sırayla')
```

```solution
title: Pafta sg13 Korpusu birlikte süz
id: c5e3d9e3-123d-4840-a69c-4858c4e7fad0
status: experimental
logsource:
    category: application
detection:
    selection:
        Action: 'policy_changed'
        Enabled: false
    filter_lab:
        Environment: 'lab'
    condition: selection and not filter_lab
level: medium
```

```hint
Laboratuvar istisnası ayrı bir filtre; normalleştirilmiş davranış iki alanla tanımlı.
```
:::
