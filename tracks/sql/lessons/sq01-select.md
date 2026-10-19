---
id: sq01
title: SELECT ve FROM
summary: Tablo, satır, sütun; sütun seçmek, ifadeler ve takma adlar, DISTINCT, metin birleştirme.
---

::: anlat Veritabanı bir tablolar topluluğudur
İlişkisel veritabanında veri **tablolarda** durur. Her **satır** bir kayıttır (bir sunucu, bir bilet), her **sütun** o kaydın bir özelliğidir (ad, CPU, şehir). Bu yolun bütün sorguları aynı örnek veritabanında çalışır: küçük bir şirketin BT operasyonu.

| Tablo | İçinde ne var |
|---|---|
| `ekipler` | 5 ekip: ad, vardiya |
| `personel` | 10 çalışan: ad, ekip, unvan, yöneticisi, işe giriş tarihi |
| `sunucular` | 12 sunucu: ad, rol, işletim sistemi, şehir, CPU (%), RAM, sorumlusu |
| `biletler` | 20 destek bileti: başlık, sunucu, açan, atanan, öncelik, durum, açılış/kapanış |
| `olcumler` | 3 sunucunun saatlik CPU ölçümleri |

Veritabanı her çalıştırmada sıfırdan kurulur; bir şeyi bozmaktan korkma.

```sql
SELECT ad, rol, cpu            #! hangi sütunlar
FROM sunucular;                #! hangi tablodan
```

`SELECT *` bütün sütunları getirir. Keşif için iyidir ama gerçek sorgularda sütunları adıyla yaz: tablo değişince sorgun sessizce başka bir şey döndürmesin.

```sql
SELECT * FROM ekipler;
```

> [!NOT]
> SQL **bildirimsel** bir dildir: *ne* istediğini söylersin, *nasıl* bulunacağına (hangi sırayla okunacak, indeks kullanılacak mı) veritabanı karar verir. Anahtar kelimeler büyük-küçük harfe duyarsızdır (`select` = `SELECT`); okunurluk için büyük yazmak gelenektir. `;` bir ifadeyi bitirir.
:::

::: anlat İfadeler, takma adlar, DISTINCT
SELECT listesinde sütunların yanında **ifadeler** de olabilir. `AS` ile sonuca bir ad verirsin:

```sql
SELECT ad,
       cpu,
       100 - cpu AS bos_yuzde,              #! hesaplanmış sütun
       ad || ' (' || rol || ')' AS etiket   #! || metinleri birleştirir
FROM sunucular;
```

`DISTINCT` tekrar eden satırları teke indirir:

```sql
SELECT DISTINCT rol FROM sunucular;
```

`FROM` olmadan da SELECT yazılabilir; SQL'i hesap makinesi gibi denemek için kullanışlıdır:

```sql
SELECT 2 + 3 * 4, 'Pafta' || '!', length('veritabanı'), upper('sql');
```

> [!TUZAK]
> İki tam sayının bölümü **tam sayıdır**: `7 / 2` sonucu `3`'tür. Ondalıklı sonuç için en az bir tarafı ondalık yap: `7 / 2.0` ya da `7 * 1.0 / 2`. Ortalama ve yüzde hesaplarken bu sık yapılan bir hatadır.

> [!NOT]
> Aynı fikir başka dillerde: KQL'de `sunucular | project ad, rol, cpu`, Splunk SPL'de `... | table ad rol cpu`. SQL'de öğrendiğin seç-süz-grupla düşüncesi log sorgu dillerinin hepsinde aynıdır.
:::

::: tahmin
Sonucu yaz (tek satır, sütunlar `|` ile ayrık):

```sql
SELECT 7 / 2, 7 / 2.0, 'Pafta' || '-' || 2026, length('SQL');
```

???

`3|3.5|Pafta-2026|3`. Tam sayı bölmesi küsuratı atar; `2.0` ondalık olduğu için ikinci bölme `3.5` verir. `||` sayıyı da metne çevirip birleştirir. `length` karakter sayısını verir.
:::

::: gorev Sunucu listesi
Bütün sunucuların yalnızca **adını** ve **işletim sistemini** (`isletim`) getir.

```starter
SELECT * FROM sunucular;
```

```test
eq(sutunlar, ["ad", "isletim"], "yalnızca ad ve isletim sütunları")
eq(len(sonuc), 12, "12 sunucunun hepsi")
eq(sorted(sonuc), sorted(sorgu("SELECT ad, isletim FROM sunucular")), "değerler doğru")
```

```solution
SELECT ad, isletim
FROM sunucular;
```

```hint
`SELECT` sonrasına sütun adlarını virgülle yaz: `SELECT ad, isletim FROM ...`
```
:::

::: gorev Boş kapasite
Her sunucunun adını ve CPU'da kalan boş yüzdeyi `bos` adlı bir sütun olarak getir (`100 - cpu`).

```starter
SELECT ad, cpu
FROM sunucular;
```

```test
eq(sutunlar, ["ad", "bos"], "sütunlar: ad, bos")
eq(sorted(sonuc), sorted(sorgu("SELECT ad, 100 - cpu FROM sunucular")), "bos = 100 - cpu")
```

```solution
SELECT ad, 100 - cpu AS bos
FROM sunucular;
```

```hint
Hesaplanmış sütuna `AS` ile ad ver: `100 - cpu AS bos`.
```
:::

::: gorev İşletim sistemleri
Sunucularda kullanılan işletim sistemlerini, **her biri bir kez** görünecek şekilde listele.

```starter
SELECT isletim
FROM sunucular;
```

```test
eq(sorted(sonuc), sorted(sorgu("SELECT DISTINCT isletim FROM sunucular")), "her işletim sistemi bir kez")
eq(len(sonuc), 5, "5 farklı işletim sistemi")
```

```solution
SELECT DISTINCT isletim
FROM sunucular;
```

```hint
Tekrarları atmak için `SELECT` ile sütun arasına `DISTINCT` yaz.
```
:::
