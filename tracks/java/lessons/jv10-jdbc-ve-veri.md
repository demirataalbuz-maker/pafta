---
id: jv10
title: Veritabanı · JDBC, PreparedStatement ve İşlemler
summary: JDBC Connection, Statement ile PreparedStatement farkı, 1 tabanlı ? parametre indeksleri, ORDER BY beyaz listesi ve setAutoCommit(false) işlemleri.
---

::: anlat `Statement` ve `PreparedStatement`
Java'nın standart veritabanı arayüzü **JDBC (Java Database Connectivity)**'dir. Bir sorguyu çalıştırmanın iki yolu vardır:
1. **`conn.createStatement()`**: Sorgu metnini doğrudan çalıştırır; kullanıcı girdisi `+` ile sorguya birleştirilirse sorgu yapısı bozulur.
2. **`conn.prepareStatement(sql)`**: Sorgu iskeletini `?` yer tutucularıyla derler; değerler `ps.setString(indeks, deger)`, `ps.setInt(indeks, deger)` ile ayrı gönderilir.

```java
String sql = "SELECT id, baslik FROM biletler WHERE bolum = ? AND oncelik >= ?";
try (PreparedStatement ps = conn.prepareStatement(sql)) {
    ps.setString(1, bolum);                        #! DİKKAT: JDBC parametre indeksleri 1'den başlar!
    ps.setInt(2, minOncelik);
    try (ResultSet rs = ps.executeQuery()) {
        while (rs.next()) {                        #! her çağrı imleci bir sonraki satıra ilerletir
            int id = rs.getInt("id");
            String baslik = rs.getString("baslik");
        }
    }
}
```

> [!TUZAK] `prepareStatement` içinde bile `+` ile metin birleştirmek!
> Kodda `PreparedStatement` adını görmek tek başına sorgunun güvenli olduğu anlamına gelmez:
> ```java
> // YANLIŞ: PreparedStatement kullanılmış ama değer hâlâ + ile birleştirilmiş!
> PreparedStatement ps = conn.prepareStatement("SELECT * FROM kullanicilar WHERE ad = '" + ad + "'");
> ```
> Okurken her zaman `?` yer tutucularının kullanıldığını ve değişkenlerin `setString` / `setInt` ile bağlandığını doğrula.
:::

::: anlat `ORDER BY` beyaz listesi ve İşlemler (`setAutoCommit(false)`)
SQL'de tablo ve sütun adları (`ORDER BY sutun_adi`) `?` parametresi olarak **verilemez**. Bu yüzden dinamik sıralama gereken yerlerde kullanıcıdan gelen değer mutlaka sabit bir **beyaz listeyle (allowlist)** eşlenir:

```java
String siraSutunu = switch (istekSira) {
    case "oncelik" -> "oncelik DESC";
    case "tarih"   -> "olusturma_zamani DESC";
    default        -> "id ASC";                    #! listede olmayan her girdi güvenli varsayılana düşer
};
```

Birden fazla `executeUpdate()` çağrısının ya hep birlikte kaydedilmesi ya da hata anında geri alınması için işlem (**transaction**) yönetimi kullanılır:

```java
conn.setAutoCommit(false);                         #! otomatik kaydı kapat
try {
    // 1. güncelleme ...
    // 2. güncelleme ...
    conn.commit();                                 #! her şey yolundaysa kalıcı yap
} catch (SQLException e) {
    conn.rollback();                               #! hata olursa tüm değişiklikleri geri al
    throw e;
}
```

> [!DERİN] `rs.getInt(...)` ve SQL `NULL` davranışı
> JDBC'de bir sayı sütunu veritabanında `NULL` ise `rs.getInt("puan")` çağrısı `null` değil **`0`** döndürür! Değerin gerçekten `0` mı yoksa `NULL` mu olduğunu ayırt etmek için hemen ardından `rs.wasNull()` kontrol edilir veya `rs.getObject("puan", Integer.class)` kullanılır.
:::

::: tahmin
Java 21 ile çalıştırıldığında bu JDBC sıralama ve sonuç simülasyonu ne yazdırır?

```java
public class Ornek {
    static String siraSec(String girdi) {
        if (girdi == null) return "id ASC";
        return switch (girdi.trim().toLowerCase()) {
            case "ad" -> "ad ASC";
            case "puan" -> "puan DESC";
            default -> "id ASC";
        };
    }

    public static void main(String[] args) {
        System.out.println(siraSec(" PUAN "));
        System.out.println(siraSec("puan; DROP TABLE x"));
        int[] degerler = {15, 0};
        boolean[] nullMi = {false, true};
        for (int i = 0; i < degerler.length; i++) {
            String cikti = nullMi[i] ? "NULL" : String.valueOf(degerler[i]);
            System.out.println("satir" + (i + 1) + ":" + cikti);
        }
    }
}
```

```gercek
puan DESC
id ASC
satir1:15
satir2:NULL
```

???

`puan DESC`, `id ASC`, `satir1:15`, `satir2:NULL`. `" PUAN "` kırpılıp küçültüldüğünde `"puan"` dalıyla eşleşir ve `"puan DESC"` döner. Beyaz listede olmayan `"puan; DROP TABLE x"` girdisi `default` dalına düşerek güvenli `"id ASC"` üretir. Döngüde ilk satır `15`, ikinci satır `wasNull` (`nullMi[1] == true`) olduğu için `NULL` yazdırır.
:::

::: gorev Beyaz listeli ve parametreli sunucu arama (SQLite)
Aşağıdaki Java DAO (Data Access Object) metodunun davranışını Python'da (bellek içi `sqlite3` bağlantısı `db` üzerinde) `sunucu_ara(db, rol, min_cpu, siralama)` fonksiyonu olarak kur ve `(id, ad, cpu)` demetlerinin listesini döndür.

```java
private static final Map<String, String> SIRA_HARITASI = Map.of(
    "ad", "ad ASC, id ASC",
    "cpu_artan", "cpu ASC, id ASC",
    "cpu_azalan", "cpu DESC, id ASC"
);

public static List<Sunucu> sunucuAra(Connection conn, String rol, int minCpu, String siralama)
        throws SQLException {
    String orderBy = SIRA_HARITASI.getOrDefault(
        siralama == null ? "" : siralama.trim(),
        "id ASC"
    );
    String sql = "SELECT id, ad, cpu FROM sunucular WHERE rol = ? AND cpu >= ? ORDER BY " + orderBy;
    try (PreparedStatement ps = conn.prepareStatement(sql)) {
        ps.setString(1, rol == null ? "" : rol.trim());
        ps.setInt(2, minCpu);
        // çalıştır ve listeyi döndür
    }
}
```

```starter
def sunucu_ara(db, rol, min_cpu, siralama):
    return db.execute("SELECT id, ad, cpu FROM sunucular").fetchall()
```

```test
import sqlite3
need("sunucu_ara")
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE sunucular (id INTEGER PRIMARY KEY, ad TEXT, rol TEXT, cpu INTEGER)")
db.executemany("INSERT INTO sunucular VALUES (?, ?, ?, ?)", [
    (1, "web02", "web", 70),
    (2, "web01", "web", 85),
    (3, "web03", "web", 50),
    (4, "db01", "db", 95),
])
eq(sunucu_ara(db, " web ", 70, "ad"), [(2, "web01", 85), (1, "web02", 70)], "min_cpu=70 sınır değeri dahil, ada göre sıralı")
eq(sunucu_ara(db, "web", 71, "ad"), [(2, "web01", 85)], "min_cpu=71 olduğunda 70 elenmeli")
eq(sunucu_ara(db, "web", 50, "cpu_azalan"), [(2, "web01", 85), (1, "web02", 70), (3, "web03", 50)], "cpu_azalan sırası")
eq(sunucu_ara(db, "web", 50, "cpu DESC; DROP TABLE sunucular"), [(1, "web02", 70), (2, "web01", 85), (3, "web03", 50)], "bilinmeyen sıralama güvenli 'id ASC' varsayılanına düşmeli")
eq(sunucu_ara(db, "web' OR '1'='1", 0, None), [], "parametreli sorguda tırnaklı rol eşleşmemeli")
```

```solution
SIRA_HARITASI = {
    "ad": "ad ASC, id ASC",
    "cpu_artan": "cpu ASC, id ASC",
    "cpu_azalan": "cpu DESC, id ASC",
}

def sunucu_ara(db, rol, min_cpu, siralama):
    anahtar = "" if siralama is None else siralama.strip()
    order_by = SIRA_HARITASI.get(anahtar, "id ASC")
    temiz_rol = "" if rol is None else rol.strip()
    sql = f"SELECT id, ad, cpu FROM sunucular WHERE rol = ? AND cpu >= ? ORDER BY {order_by}"
    return db.execute(sql, (temiz_rol, min_cpu)).fetchall()
```

```hint
Sıralama sütununu `SIRA_HARITASI.get(anahtar, "id ASC")` ile beyaz listeden seç; `rol` ve `min_cpu` değerlerini ise `?` yer tutucularıyla `(temiz_rol, min_cpu)` demeti olarak `db.execute` metoduna ver.
```
:::

::: gorev Atomik kota aktarımı (`commit` ve `rollback`)
Aşağıdaki Java işlem (`transaction`) metodunun davranışını Python'da `kota_aktar(db, kaynak_id, hedef_id, miktar)` fonksiyonu olarak kur. İşlem başarılıysa `True`, herhangi bir kural ihlalinde veritabanını eski haline döndürüp (`rollback`) `False` döndürsün.

```java
public static boolean kotaAktar(Connection conn, int kaynakId, int hedefId, int miktar)
        throws SQLException {
    if (miktar <= 0 || kaynakId == hedefId) {
        return false;
    }
    conn.setAutoCommit(false);
    try {
        // 1. Kaynak hesabın kotasını miktar kadar düş (yalnızca mevcut kota >= miktar ise)
        // 2. Hedef hesabın kotasını miktar kadar artır (hedef hesap mevcutsa)
        // İki güncellemeden herhangi biri 1 satır etkilemediyse conn.rollback() yap ve false dön!
        conn.commit();
        return true;
    } catch (SQLException e) {
        conn.rollback();
        return false;
    }
}
```

```starter
def kota_aktar(db, kaynak_id, hedef_id, miktar):
    db.execute("UPDATE ekipler SET kota = kota - ? WHERE id = ?", (miktar, kaynak_id))
    db.execute("UPDATE ekipler SET kota = kota + ? WHERE id = ?", (miktar, hedef_id))
    db.commit()
    return True
```

```test
import sqlite3
need("kota_aktar")
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE ekipler (id INTEGER PRIMARY KEY, kota INTEGER NOT NULL)")
db.executemany("INSERT INTO ekipler VALUES (?, ?)", [(1, 100), (2, 40)])

eq(kota_aktar(db, 1, 2, 100), True, "tam bakiye (100) aktarılabilmeli")
eq(db.execute("SELECT id, kota FROM ekipler ORDER BY id").fetchall(), [(1, 0), (2, 140)], "aktarım sonrası kotalar 0 ve 140")

eq(kota_aktar(db, 2, 1, 141), False, "yetersiz kotada (141 > 140) False dönmeli")
eq(db.execute("SELECT id, kota FROM ekipler ORDER BY id").fetchall(), [(1, 0), (2, 140)], "başarısız aktarımda kotalar değişmemeli")

eq(kota_aktar(db, 2, 99, 50), False, "olmayan hedef hesapta (id=99) rollback yapılmalı ve False dönmeli")
eq(db.execute("SELECT id, kota FROM ekipler ORDER BY id").fetchall(), [(1, 0), (2, 140)], "kaynak hesaptan düşülen 50 geri alınmış olmalı!")

eq(kota_aktar(db, 2, 1, 0), False, "miktar=0 reddedilmeli")
eq(kota_aktar(db, 2, 2, 10), False, "aynı hesaba aktarım reddedilmeli")
```

```solution
def kota_aktar(db, kaynak_id, hedef_id, miktar):
    if miktar <= 0 or kaynak_id == hedef_id:
        return False
    try:
        c1 = db.execute(
            "UPDATE ekipler SET kota = kota - ? WHERE id = ? AND kota >= ?",
            (miktar, kaynak_id, miktar),
        )
        if c1.rowcount != 1:
            db.rollback()
            return False
        c2 = db.execute(
            "UPDATE ekipler SET kota = kota + ? WHERE id = ?",
            (miktar, hedef_id),
        )
        if c2.rowcount != 1:
            db.rollback()
            return False
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
```

```hint
İlk `UPDATE` sorgusunda `WHERE id = ? AND kota >= ?` koşulunu kullan ve `c1.rowcount != 1` ise `db.rollback()` çağırıp `False` dön. İkinci `UPDATE` sorgusunda da hedef satır bulunamazsa (`c2.rowcount != 1`) yine `db.rollback()` çağırarak ilk sorgunun yaptığı düşümü geri al!
```
:::
