---
id: ph08
title: Veritabanı ve PDO
summary: PDO ile bağlantı ve hata kipi, prepare/execute ile parametreli sorgular, soru işareti ve adlı yer tutucular, IN listesi için yer tutucu üretmek, fetch kipleri, işlemler (beginTransaction, commit, rollBack) ve sorguya metin eklemenin neden yanlış olduğu.
kazanim: ZCPE 6.2, ZCPE 9.1, ZCPE 9.2
---

::: anlat PDO ile sorgu
PHP uygulamaları veritabanına çoğunlukla **PDO** ile bağlanır. Okuduğun kodda ilk bakman gereken üç şey: bağlantı, hata kipi ve sorguların nasıl kurulduğu:

```php
<?php
$pdo = new PDO("mysql:host=db;dbname=pafta;charset=utf8mb4", $kullanici, $parola, [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,        // hatada istisna fırlat (PHP 8'de varsayılan)
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,   // satırlar ilişkisel dizi olarak
]);

$st = $pdo->prepare("SELECT id, ad, cpu FROM sunucular WHERE rol = ? AND cpu > ?");
$st->execute(["web", 60]);
foreach ($st->fetchAll() as $satir) {
    echo $satir["ad"], " ", $satir["cpu"], "\n";
}

$st = $pdo->prepare("SELECT * FROM personel WHERE ad = :ad");     // adlı yer tutucu
$st->execute(["ad" => $_GET["ad"] ?? ""]);
$kisi = $st->fetch();                                               // tek satır ya da false
```

| Yöntem | Döndürdüğü |
|---|---|
| `$st->fetch()` | sıradaki satır, yoksa `false` |
| `$st->fetchAll()` | bütün satırlar |
| `$st->fetchColumn()` | ilk sütunun değeri: `SELECT COUNT(*)` için |
| `$st->rowCount()` | etkilenen satır sayısı (`UPDATE`, `DELETE`) |
| `$pdo->lastInsertId()` | son eklenen kaydın kimliği |

### Neden yer tutucu?
Sorguya değeri **metin olarak eklemek** (birleştirmek) iki şeyi karıştırır: SQL kodu ve veri. Verinin içinde bir kesme işareti geçtiği anda sorgu bozulur:

```php
<?php
$ad = "O'Brien";
$sql = "SELECT * FROM personel WHERE ad = '" . $ad . "'";
echo $sql;     // SELECT * FROM personel WHERE ad = 'O'Brien'   ← tırnak dengesi bozuldu
```

Kullanıcıdan gelen bir değer aynı yolla sorgunun **yapısını** değiştirebilir; bu, web uygulamalarının en eski ve en yaygın açık sınıfıdır. Yer tutucuyla (`?`, `:ad`) değer sorgudan **ayrı** gönderilir ve hiçbir koşulda kod olarak yorumlanmaz.

> [!GÜVENLİK]
> Kod incelemesinde aranacak kalıp: SQL metninin içinde `.` ile birleştirilen ya da `"... $degisken ..."` ile yerleştirilen her değişken. Tablo ve sütun adları yer tutucuyla verilemez; onlar dışarıdan geliyorsa sabit bir **izin listesinden** seçilmelidir (`in_array($siralama, ["ad", "cpu"], true)`).
:::

::: anlat IN listeleri ve işlemler
Değişken uzunlukta bir `IN (...)` listesi için her değere bir `?` üretilir:

```php
<?php
$idler = [3, 5, 8];
$yerler = implode(",", array_fill(0, count($idler), "?"));    // "?,?,?"
$st = $pdo->prepare("SELECT ad FROM sunucular WHERE id IN ($yerler)");
$st->execute($idler);
```

Birden çok yazma işleminin **ya hepsinin ya hiçbirinin** gerçekleşmesi gerekiyorsa bir işlem (transaction) kullanılır:

```php
<?php
try {
    $pdo->beginTransaction();
    $pdo->prepare("UPDATE kota SET miktar = miktar - ? WHERE ekip = ?")->execute([10, "Ağ"]);
    $pdo->prepare("UPDATE kota SET miktar = miktar + ? WHERE ekip = ?")->execute([10, "Uygulama"]);
    $pdo->commit();
} catch (Throwable $e) {
    $pdo->rollBack();          // ilk güncelleme de geri alınır
    throw $e;
}
```

Görevlerde aynı kalıpları Python'un `sqlite3` modülüyle kuracaksın: PDO'daki `?` yer tutucusu orada da `?`'dir.
:::

::: tahmin
PHP 8 ile çıktı:

```php
<?php
$ad = "O'Brien";
$sql = "SELECT * FROM personel WHERE ad = '" . $ad . "'";
echo $sql, "\n";
echo substr_count($sql, "'"), "\n";
```

```gercek
SELECT * FROM personel WHERE ad = 'O'Brien'
3
```

???

`SELECT * FROM personel WHERE ad = 'O'Brien'` ve `3`. Değer metne olduğu gibi eklendi; isimdeki kesme işaretiyle birlikte sorguda üç tırnak var ve dengesi bozuk: veritabanı `'O'`'dan sonrasını SQL kodu sanıp hata verir. Yer tutucuyla bu sorun hiç oluşmaz.
:::

::: gorev Parametreli arama
`kisi_bul(db, ad)` fonksiyonunu yaz: `personel` tablosundan adı tam olarak `ad` olan kişilerin `(id, ad)` satırlarını `id` sırasıyla döndürsün. **Yer tutucu** kullan.

```starter
def kisi_bul(db, ad):
    return db.execute("SELECT id, ad FROM personel WHERE ad = '" + ad + "' ORDER BY id").fetchall()
```

```test
import sqlite3
need("kisi_bul")
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE personel (id INTEGER PRIMARY KEY, ad TEXT)")
db.executemany("INSERT INTO personel VALUES (?, ?)", [(1, "Ayşe"), (2, "O'Brien"), (3, "Ayşe"), (4, "Can")])
eq(kisi_bul(db, "Ayşe"), [(1, "Ayşe"), (3, "Ayşe")], "iki Ayşe")
eq(kisi_bul(db, "O'Brien"), [(2, "O'Brien")], "kesme işaretli ad sorguyu bozmamalı")
eq(kisi_bul(db, "Zeynep"), [], "olmayan ad")
```

```solution
def kisi_bul(db, ad):
    return db.execute("SELECT id, ad FROM personel WHERE ad = ? ORDER BY id", (ad,)).fetchall()
```

```hint
Değeri sorgu metnine ekleme; `?` yaz ve değeri ikinci argüman olarak ver: `db.execute(sql, (ad,))`.
```
:::

::: gorev IN listesi
`sunucu_adlari(db, idler)` fonksiyonunu yaz: verilen kimliklere sahip sunucuların adlarını `id` sırasıyla döndürsün. Her kimlik için bir `?` üret; liste boşsa **sorgu çalıştırmadan** boş liste döndür (`IN ()` geçersiz SQL'dir).

```starter
def sunucu_adlari(db, idler):
    sql = "SELECT ad FROM sunucular WHERE id IN (" + ",".join(str(i) for i in idler) + ") ORDER BY id"
    return [r[0] for r in db.execute(sql)]
```

```test
import sqlite3
need("sunucu_adlari")
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE sunucular (id INTEGER PRIMARY KEY, ad TEXT)")
db.executemany("INSERT INTO sunucular VALUES (?, ?)", [(1, "web01"), (3, "db01"), (5, "web02"), (8, "yedek01")])
eq(sunucu_adlari(db, [8, 3, 5]), ["db01", "web02", "yedek01"], "üç sunucu")
eq(sunucu_adlari(db, [99]), [], "olmayan kimlik")
eq(sunucu_adlari(db, []), [], "boş liste")
ok("?" in src, "yer tutucu kullan")
```

```solution
def sunucu_adlari(db, idler):
    if not idler:
        return []
    yerler = ",".join("?" * len(idler))
    sql = f"SELECT ad FROM sunucular WHERE id IN ({yerler}) ORDER BY id"
    return [r[0] for r in db.execute(sql, list(idler))]
```

```hint
PHP'deki `implode(",", array_fill(0, count($idler), "?"))`: Python'da `",".join("?" * len(idler))`.
```

```hint
Boş liste için önce `if not idler: return []`.
```
:::

::: gorev Ya hep ya hiç
`kota_aktar(db, kaynak, hedef, miktar)` fonksiyonunu yaz: `kota` tablosunda kaynaktan miktarı düşüp hedefe eklesin. İki güncelleme **tek bir işlemde** olsun: kaynağın kotası yetmiyorsa (sonuç negatif olacaksa) hiçbir değişiklik kalmasın ve fonksiyon `False` döndürsün; başarılıysa `True`.

```starter
def kota_aktar(db, kaynak, hedef, miktar):
    db.execute("UPDATE kota SET miktar = miktar - ? WHERE ekip = ?", (miktar, kaynak))
    db.execute("UPDATE kota SET miktar = miktar + ? WHERE ekip = ?", (miktar, hedef))
    db.commit()
    return True
```

```test
import sqlite3
need("kota_aktar")
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE kota (ekip TEXT PRIMARY KEY, miktar INTEGER NOT NULL)")
db.executemany("INSERT INTO kota VALUES (?, ?)", [("Ağ", 30), ("Uygulama", 10)])
db.commit()
def durum():
    return dict(db.execute("SELECT ekip, miktar FROM kota").fetchall())
eq(kota_aktar(db, "Ağ", "Uygulama", 10), True, "yeterli kota")
eq(durum(), {"Ağ": 20, "Uygulama": 20}, "aktarıldı")
eq(kota_aktar(db, "Uygulama", "Ağ", 50), False, "yetersiz kota")
eq(durum(), {"Ağ": 20, "Uygulama": 20}, "hiçbir şey değişmedi")
eq(kota_aktar(db, "Ağ", "Uygulama", 20), True, "kotanın tamamı aktarılabilir")
eq(durum(), {"Ağ": 0, "Uygulama": 40}, "kaynak sıfıra indi")
```

```solution
def kota_aktar(db, kaynak, hedef, miktar):
    try:
        db.execute("UPDATE kota SET miktar = miktar - ? WHERE ekip = ?", (miktar, kaynak))
        kalan = db.execute("SELECT miktar FROM kota WHERE ekip = ?", (kaynak,)).fetchone()[0]
        if kalan < 0:
            raise ValueError("yetersiz kota")
        db.execute("UPDATE kota SET miktar = miktar + ? WHERE ekip = ?", (miktar, hedef))
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
```

```hint
Python'un `sqlite3` modülü bir yazma işleminde kendiliğinden işlem başlatır; `db.commit()` kalıcılaştırır, `db.rollback()` geri alır.
```

```hint
İlk güncellemeden sonra kaynağın yeni miktarını oku; negatifse `rollback()` ve `False`.
```
:::
