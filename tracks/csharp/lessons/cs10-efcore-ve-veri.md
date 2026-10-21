---
id: cs10
title: Veritabanı · Entity Framework Core, IQueryable ve Parametreli Sorgular
summary: EF Core DbContext, LINQ ile parametreli sorgu, FromSqlInterpolated ile FromSqlRaw farkı ve SaveChanges işlemi.
---

::: anlat `DbContext`, `DbSet<T>` ve `IQueryable` vs `IEnumerable`
.NET uygulamalarında veritabanı erişimi çoğunlukla **Entity Framework Core (EF Core)** ORM katmanıyla yapılır:
- **`db.Biletler.Where(b => b.Durum == durum).Take(10).ToListAsync()`** gibi bir LINQ zinciri bellekte değil, **`IQueryable<T>`** üzerinden **parametreli bir SQL sorgusuna** (`WHERE Durum = @p0 LIMIT 10`) çevrilerek veritabanında çalıştırılır!
- Salt okunur sorgularda performans için **`.AsNoTracking()`** eklenir; böylece EF Core nesneleri değişiklik izleme belleğine almaz.

```csharp
// Güvenli LINQ sorgusu: durum değişkeni SQL parametresi (@__durum_0) olarak bağlanır
// var liste = await db.Biletler
//     .AsNoTracking()
//     .Where(b => b.Durum == durum && b.Oncelik >= minOncelik)
//     .OrderByDescending(b => b.Id)
//     .Take(20)
//     .ToListAsync();
```
:::

::: anlat `FromSqlInterpolated` (Güvenli) vs `FromSqlRaw` (Tehlikeli!)
EF Core'da doğrudan SQL yazılması gerektiğinde iki metot birbirine çok benzer görünür ama güvenlik açısından gece ile gündüz kadar farklıdır:

1. **`FromSqlInterpolated($"SELECT * FROM Biletler WHERE Sunucu = {sunucu}")`** (ve EF Core 7+ **`FromSql($"...")`**):
   `$"..."` ifadesini `FormattableString` olarak alır ve `{sunucu}` değişkenini metne yapıştırmak yerine **`@p0` SQL parametresine** dönüştürür (**GÜVENLİ**).
2. **`FromSqlRaw($"SELECT * FROM Biletler WHERE Sunucu = '{sunucu}'")`** (veya `+` ile birleştirme):
   Önce C# tarafında düz `string` oluşturur ve veritabanına ham SQL olarak gönderir — **`sunucu` kullanıcıdan geliyorsa doğrudan SQL enjeksiyonuna (SQLi) açıktır!**
   (`FromSqlRaw` yalnızca `FromSqlRaw("SELECT * FROM Biletler WHERE Sunucu = {0}", sunucu)` biçiminde yer tutucu argümanla çağrılırsa parametreli olur.)

```csharp
using System;

class SqlFarki
{
    // FormattableString kabul eden metot (FromSqlInterpolated gibi)
    static string InterpolatedOzet(FormattableString fs)
        => $"SQL={fs.Format} | ParamSayisi={fs.ArgumentCount}";

    // Düz string kabul eden metot (FromSqlRaw($"...") gibi)
    static string RawOzet(string sql)
        => $"HAM_SQL={sql}";

    static void Main()
    {
        string girdi = "web01' OR '1'='1";
        Console.WriteLine(InterpolatedOzet($"SELECT * FROM Sunucular WHERE Ad = {girdi}"));
        Console.WriteLine(RawOzet($"SELECT * FROM Sunucular WHERE Ad = '{girdi}'"));
    }
}
```

> [!GÜVENLİK]
> C# kod denetiminde `FromSqlRaw($"...")` veya `ExecuteSqlRaw($"...")` içinde `$` enterpolasyonu ya da `+` birleştirmesi görürsen bu doğrudan bir **SQL Enjeksiyonu** bulgusudur!
:::

::: tahmin
```csharp
using System;

class Tahmin
{
    static string SorguIncele(FormattableString fs)
    {
        return $"Sablon:{fs.Format}|Arg:{fs.ArgumentCount}|Ilk:{fs.GetArgument(0)}";
    }

    static void Main()
    {
        string kullanici = "ali";
        int altPuan = 50;
        Console.WriteLine(SorguIncele($"SELECT Id FROM Hesaplar WHERE Ad = {kullanici} AND Puan >= {altPuan}"));

        string ham = $"SELECT Id FROM Hesaplar WHERE Ad = '{kullanici}'";
        Console.WriteLine(ham);
    }
}
```

```gercek
Sablon:SELECT Id FROM Hesaplar WHERE Ad = {0} AND Puan >= {1}|Arg:2|Ilk:ali
SELECT Id FROM Hesaplar WHERE Ad = 'ali'
```

???

`Sablon:SELECT Id FROM Hesaplar WHERE Ad = {0} AND Puan >= {1}|Arg:2|Ilk:ali` ve `SELECT Id FROM Hesaplar WHERE Ad = 'ali'`. C#'ta bir `$"..."` ifadesi `FormattableString` parametresine (`FromSqlInterpolated` gibi) verildiğinde derleyici metni birleştirmez; `{0}`, `{1}` yer tutuculu şablonu ve argüman dizisini ayrı ayrı taşır (`Arg:2`, `Ilk:ali`). Aynı ifade `string` değişkenine (`ham`) veya `FromSqlRaw(string)` parametresine verildiğinde ise değer doğrudan metnin içine gömülür.
:::

::: gorev EF Core SQL çağrısı güvenlik denetleyicisi (`FromSqlRaw` vs `FromSqlInterpolated`)
Bir C# kaynak kodundaki EF Core ham SQL çağrılarını sınıflandıran `ef_sorgu_denetle(metot_adi, arguman_metni, ek_arguman_sayisi)` fonksiyonunu Python'da yaz:
- `metot_adi`: `"FromSqlInterpolated"`, `"FromSql"`, `"FromSqlRaw"` veya `"ExecuteSqlRaw"`.
- `arguman_metni`: metodun ilk argümanının kaynak kodundaki yazılışı (ör. `'$"SELECT * FROM T WHERE Id = {id}"'` veya `'"SELECT * FROM T WHERE Id = {0}"'`).
- Kurallar:
  1. `metot_adi` `"FromSqlInterpolated"` veya `"FromSql"` ise ve `arguman_metni.strip()` `'$"'` ile başlıyorsa `"GUVENLI:PARAMETRELI_INTERPOLATION"` döndür.
  2. `metot_adi` `"FromSqlRaw"` veya `"ExecuteSqlRaw"` ise:
     - `arguman_metni` içinde `'$"'` geçiyorsa veya `'+'` karakteri varsa (metin birleştirme) `"TEHLIKELI:SQL_ENJEKSIYONU"` döndür!
     - Sabit dizgede `"{0}"` yer tutucusu varsa ve `ek_arguman_sayisi >= 1` ise `"GUVENLI:YER_TUTUCULU_RAW"` döndür.
     - Sabit dizgede değişken birleştirme yoksa ve `ek_arguman_sayisi == 0` ise `"GUVENLI:SABIT_SORGU"` döndür.
  3. Diğer tüm durumlarda `"BELIRSIZ"` döndür.

```starter
def ef_sorgu_denetle(metot_adi, arguman_metni, ek_arguman_sayisi):
    return "BELIRSIZ"
```

```test
need("ef_sorgu_denetle")
eq(ef_sorgu_denetle("FromSqlInterpolated", '$"SELECT * FROM Biletler WHERE Id = {id}"', 0),
   "GUVENLI:PARAMETRELI_INTERPOLATION", "FromSqlInterpolated + $\"...\" güvenlidir")
eq(ef_sorgu_denetle("FromSql", '  $"SELECT * FROM Biletler WHERE Id = {id}" ', 0),
   "GUVENLI:PARAMETRELI_INTERPOLATION", "EF Core 7+ FromSql + $\"...\" güvenlidir")
eq(ef_sorgu_denetle("FromSqlRaw", '$"SELECT * FROM Biletler WHERE Ad = \'{ad}\'"', 0),
   "TEHLIKELI:SQL_ENJEKSIYONU", "FromSqlRaw içinde $\"...\" doğrudan SQLi zafiyetidir!")
eq(ef_sorgu_denetle("ExecuteSqlRaw", '"DELETE FROM Biletler WHERE Id = " + id', 0),
   "TEHLIKELI:SQL_ENJEKSIYONU", "ExecuteSqlRaw içinde + birleştirmesi doğrudan SQLi zafiyetidir!")
eq(ef_sorgu_denetle("FromSqlRaw", '"SELECT * FROM Biletler WHERE Id = {0}"', 1),
   "GUVENLI:YER_TUTUCULU_RAW", "{0} yer tutucusu ve ek argüman ile FromSqlRaw güvenlidir")
eq(ef_sorgu_denetle("FromSqlRaw", '"SELECT * FROM Biletler WHERE Id = {0}"', 0),
   "BELIRSIZ", "{0} var ama ek argüman 0 ise BELIRSIZ")
eq(ef_sorgu_denetle("FromSqlRaw", '"SELECT * FROM Biletler"', 0),
   "GUVENLI:SABIT_SORGU", "parametresiz sabit sorgu güvenlidir")
eq(ef_sorgu_denetle("BilinmeyenMetot", '"SELECT 1"', 0),
   "BELIRSIZ", "tanınmayan metot -> BELIRSIZ")
```

```solution
def ef_sorgu_denetle(metot_adi, arguman_metni, ek_arguman_sayisi):
    temiz = arguman_metni.strip()
    if metot_adi in ("FromSqlInterpolated", "FromSql"):
        if temiz.startswith('$"'):
            return "GUVENLI:PARAMETRELI_INTERPOLATION"
        return "BELIRSIZ"
    if metot_adi in ("FromSqlRaw", "ExecuteSqlRaw"):
        if '$"' in temiz or "+" in temiz:
            return "TEHLIKELI:SQL_ENJEKSIYONU"
        if "{0}" in temiz and ek_arguman_sayisi >= 1:
            return "GUVENLI:YER_TUTUCULU_RAW"
        if "{0}" not in temiz and ek_arguman_sayisi == 0:
            return "GUVENLI:SABIT_SORGU"
        return "BELIRSIZ"
    return "BELIRSIZ"
```

```hint
`FromSqlRaw` veya `ExecuteSqlRaw` çağrısında `'$"' in temiz or "+" in temiz` kontrolünü ilk sırada yap; çünkü C#'ta `string` parametresine verilen `$"..."` ifadesi SQL parametresine dönüştürülmez!
```
:::

::: gorev EF Core LINQ filtre ve işlem (`SaveChanges`) simülasyonu
Aşağıdaki C# EF Core servis metodunun davranışını gerçek `sqlite3` bağlantısı (`db`) üzerinde Python'da `biletleri_kapat(db, sunucu_adi, maks_oncelik)` fonksiyonu olarak kur:
- Tablo şeması: `biletler (id INTEGER PRIMARY KEY, sunucu TEXT, oncelik INTEGER, durum TEXT)`.
- `sunucu == sunucu_adi.strip()` ve `durum == 'acik'` olan tüm biletleri seç.
- Seçilen biletlerden **herhangi birinin** `oncelik` değeri `maks_oncelik` değerinden **büyükse** (`oncelik > maks_oncelik`), hiçbir kaydı kalıcı olarak güncellemeden (`rollback` yaparak veya hiç `UPDATE` etmeden) `("IPTAL_KRITIK_BILET", 0)` döndür.
- Seçilen biletlerin tümü `oncelik <= maks_oncelik` koşulunu sağlıyorsa hepsinin `durum` alanını `'kapali'` olarak güncelle (`commit`) ve `("KAPATILDI", guncellenen_satir_sayisi)` döndür.

```starter
def biletleri_kapat(db, sunucu_adi, maks_oncelik):
    return "KAPATILDI", 0
```

```test
import sqlite3
need("biletleri_kapat")
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE biletler (id INTEGER PRIMARY KEY, sunucu TEXT, oncelik INTEGER, durum TEXT)")
db.executemany(
    "INSERT INTO biletler (id, sunucu, oncelik, durum) VALUES (?, ?, ?, ?)",
    [
        (1, "web01", 2, "acik"),
        (2, "web01", 3, "acik"),
        (3, "web01", 5, "kapali"),
        (4, "db01", 2, "acik"),
        (5, "db01", 4, "acik"),
    ],
)
db.commit()

eq(biletleri_kapat(db, " db01 ", 3), ("IPTAL_KRITIK_BILET", 0), "db01'de oncelik=4 (> 3) olan açık bilet yüzünden işlem iptal edilmeli")
eq(db.execute("SELECT COUNT(*) FROM biletler WHERE sunucu='db01' AND durum='acik'").fetchone()[0], 2, "db01'deki açık biletler değişmemiş olmalı")
eq(biletleri_kapat(db, "web01", 3), ("KAPATILDI", 2), "web01'deki açık biletlerin önceliği 2 ve 3 (<= 3); kapalı olan oncelik=5 engel olmamalı")
eq(db.execute("SELECT COUNT(*) FROM biletler WHERE sunucu='web01' AND durum='acik'").fetchone()[0], 0, "web01'de açık bilet kalmamalı")
```

```solution
def biletleri_kapat(db, sunucu_adi, maks_oncelik):
    hedef = sunucu_adi.strip()
    satirlar = db.execute(
        "SELECT id, oncelik FROM biletler WHERE sunucu = ? AND durum = 'acik'",
        (hedef,),
    ).fetchall()
    if any(oncelik > maks_oncelik for _, oncelik in satirlar):
        return "IPTAL_KRITIK_BILET", 0
    cur = db.execute(
        "UPDATE biletler SET durum = 'kapali' WHERE sunucu = ? AND durum = 'acik'",
        (hedef,),
    )
    db.commit()
    return "KAPATILDI", cur.rowcount
```

```hint
Yalnızca `durum = 'acik'` olan satırları kontrol et (zaten `'kapali'` olan yüksek öncelikli biletler işlemi engellememeli). `any(oncelik > maks_oncelik ...)` doğruysa güncelleme yapmadan `("IPTAL_KRITIK_BILET", 0)` döndür.
```
:::
