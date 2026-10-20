---
id: sg14
title: Metadata, Kaynaklar ve Kuralın Yaşam Döngüsü
summary: Title, id, status, description, falsepositives, level ve fields; öncelik ile kesinliği karıştırmamak.
---

::: anlat Bir başkası bu kuralı devralabilmeli
Bir kuralın detection kısmı bilgisayar içindir; açıklaması, kaynakları ve normal senaryoları onu devralacak kişi içindir. `title` davranışı kısa anlatmalı. `description`, hangi kaydı neden seçtiğini ve neyi kanıtlamadığını açıklamalı. `id`, değişiklik ve ilişki takibine yardım eden kalıcı kimliktir.

`status: experimental` henüz operasyon bağlamında olgunlaşmamış içerik için uygundur. `test` ve `stable` etiketleri yalnız sözdizimi hatasız demek değildir; içeriğin kendi ortamında incelenmiş olması gerekir. Bu eğitimde kuralları otomatik olarak üretime hazır ilan etmiyoruz.

`falsepositives`, bilinen normal nedenleri listeler. `fields`, incelemede gösterilmesini istediğin alanları belirtir. `level`, araştırma önceliğine katkı verir; eşleşmenin saldırı olduğuna ilişkin yüzde veya güven skoru değildir. Metadata eklemek detection mantığını daraltmaz.

```sigma
title: Pafta sg14 Ornek
id: 3f6d2d67-33d0-4355-a3b1-dd1aa331278f
status: experimental
logsource:
    category: application
detection:
    selection:
        Action: 'policy_disabled'
    condition: selection
level: medium
```
:::

::: anlat ATT&CK etiketi bir kanıt zincirinin yerini tutmaz
Teknik etiketi davranış fikrini ortak bir dille ilişkilendirmeye yarayabilir. Ama yalnız yaygın bir araç adını gördüğün için çok sayıda teknik etiketi eklemek kapsamı şişirir. Hangi davranışın gözlendiğini ve hangi telemetriye dayanıldığını açıklayabilmelisin.

Kuralı değiştirdiğinde değişikliğin mantık etkisini not et: yeni normal filtre, yeni alan eşlemesi, daha geniş değer listesi gibi. Eski örnekleri yeniden çalıştır. Bir etiketi `high` yapmak, eksik negatif testin veya geniş kullanıcı allowlistinin sorununu çözmez.

Bu görevlerin metadata kontrolleri biçim alanlarının varlığını da inceler; yine de asıl doğrulama aynı olumlu/olumsuz olay davranışıdır. İyi başlık, bozuk condition'ı kurtaramaz.

Kaynak: [Sigma resmi belgesi](https://sigmahq.io/sigma-specification/specification/sigma-rules-specification.html).
:::

::: tahmin
Girdi kutusundaki sentetik olaylardan hangilerinin `id` değerleri eşleşir? Kuralı ve olayları birlikte oku. Çıktıda eşleşen kimlikler sırayla gösterilir.

```sigma
title: Pafta sg14 Ornek
id: 3f6d2d67-33d0-4355-a3b1-dd1aa331278f
status: experimental
logsource:
    category: application
detection:
    selection:
        Action: 'policy_disabled'
    condition: selection
level: medium
```

```stdin
[
  {
    "Action": "policy_disabled",
    "User": "ops",
    "id": "e1"
  },
  {
    "Action": "policy_enabled",
    "User": "ops",
    "id": "e2"
  }
]
```

???

`e1` eşleşir. İlk olay policy_disabled eylemini taşır. İkinci olayda policy_enabled var. level veya falsepositives gibi metadata alanları burada bir olay filtresi olarak çalışmıyor.
:::

::: gorev Devralınabilir bir kural
Başlığı `Pafta Politika Kapatma` yap. Action policy_disabled olayını seç. description, falsepositives ve fields alanlarını ekle; fields listesinde User ve Host bulunsun. status experimental kalsın.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta Politika Kapatma
id: 56e0f667-ea0a-4f77-8add-d10483b71a55
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
    "Action": "policy_disabled",
    "User": "demo",
    "Host": "pc1",
    "id": "g1-1"
  },
  {
    "Action": "policy_enabled",
    "id": "g1-2"
  },
  {
    "Action": "policy_viewed",
    "id": "g1-3"
  },
  {
    "id": "g1-4"
  }
]
```

```test
ok(eslesir({'Action': 'policy_disabled', 'User': 'demo', 'Host': 'pc1'}), 'Olumlu ornek 1 eslesmeli')
ok(not eslesir({'Action': 'policy_enabled'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'Action': 'policy_viewed'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({}), 'Olumsuz ornek 3 disarida kalmali')
import yaml
m = yaml.safe_load(src)
eq(m.get('title'), 'Pafta Politika Kapatma', 'Açık başlık')
eq(m.get('status'), 'experimental', 'Eğitim kuralı experimental')
ok(bool(m.get('description')), 'description gerekli')
ok(isinstance(m.get('falsepositives'), list) and bool(m['falsepositives']), 'Bilinen normal neden listesi')
ok(set(['User','Host']).issubset(m.get('fields', [])), 'İnceleme alanları')
```

```solution
title: Pafta Politika Kapatma
id: 67c4c35a-5a29-450e-aaa8-ca0c3caf5b85
status: experimental
description: 'Sentetik uygulamada politika kapatma olaylarini inceleme adayi yapar.'
falsepositives:
    - 'Onayli bakim ve yetkili test'
fields:
    - User
    - Host
logsource:
    category: application
detection:
    selection:
        Action: 'policy_disabled'
    condition: selection
level: medium
```

```hint
Metadata detection dışında, üst seviyede bulunur; falsepositives kendiliğinden filtre değildir.
```
:::

::: gorev Öncelik davranışı değiştirmez
Action audit_changed ve Enabled false koşullarını yaz. level high, description ve falsepositives ekle. Normal neden olarak bakım yazmak, o olayı otomatik dışlamamalı: bakım bağlamındaki kapatma da eşleşsin.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg14 Öncelik davranışı değiştirmez
id: 33ae64aa-0f12-4f9a-9bbc-75626cb31fb8
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
    "Action": "audit_changed",
    "Enabled": false,
    "id": "g2-1"
  },
  {
    "Action": "audit_changed",
    "Enabled": false,
    "Reason": "maintenance",
    "id": "g2-2"
  },
  {
    "Action": "audit_changed",
    "Enabled": true,
    "id": "g2-3"
  },
  {
    "Action": "audit_viewed",
    "Enabled": false,
    "id": "g2-4"
  }
]
```

```test
ok(eslesir({'Action': 'audit_changed', 'Enabled': False}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'Action': 'audit_changed', 'Enabled': False, 'Reason': 'maintenance'}), 'Olumlu ornek 2 eslesmeli')
ok(not eslesir({'Action': 'audit_changed', 'Enabled': True}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'Action': 'audit_viewed', 'Enabled': False}), 'Olumsuz ornek 2 disarida kalmali')
import yaml
m = yaml.safe_load(src)
eq(m.get('level'), 'high', 'Öncelik high')
ok(bool(m.get('description')) and isinstance(m.get('falsepositives'), list) and bool(m['falsepositives']), 'Açıklama ve normal nedenler')
```

```solution
title: Pafta sg14 Öncelik davranışı değiştirmez
id: e7d0c92e-a720-4301-a1e9-bfd1c4f846bc
status: experimental
description: 'Denetim kapatma davranisini inceleme adayi yapar; niyeti tek basina kanitlamaz.'
falsepositives:
    - 'Onayli bakim'
logsource:
    category: application
detection:
    selection:
        Action: 'audit_changed'
        Enabled: false
    condition: selection
level: high
```

```hint
Metadatayı açıklama için yaz; görevde bakım filtresi istenmiyor.
```
:::
