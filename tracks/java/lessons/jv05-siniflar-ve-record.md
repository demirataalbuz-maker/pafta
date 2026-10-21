---
id: jv05
title: Sınıflar, JavaBeans ve record
summary: private/public erişim, kurucular, JavaBean getter/setter sözleşmesi (get/set/is), static alanlar ve modern Java record veri taşıyıcıları.
---

::: anlat Alanlar, `static` ve JavaBean sözleşmesi
Bir Java sınıfında alanlar genellikle `private` tanımlanır ve dışarıya **getter / setter** metotlarıyla açılır. Spring, Jackson ve Hibernate gibi web çerçeveleri JSON veya form verisini bir nesneye bağlarken **alan adına değil, `getXxx` / `setXxx` metotlarına** bakar (**JavaBeans** kuralı):
- `String ad` alanı için: `getAd()` ve `setAd(String ad)`
- `boolean aktif` alanı için: `isAktif()` (veya `getAktif()`) ve `setAktif(boolean aktif)`

```java
public class KullaniciFormu {
    private static int toplamNesne = 0;               #! static: sınıfa aittir, tüm nesneler paylaşır
    private String kullaniciAdi;
    private boolean yonetici = false;                 #! varsayılan değer

    public KullaniciFormu(String kullaniciAdi) {      #! kurucu (constructor): sınıf adıyla aynı
        this.kullaniciAdi = kullaniciAdi;
        toplamNesne++;
    }

    public String getKullaniciAdi() { return kullaniciAdi; }
    public boolean isYonetici() { return yonetici; }
    public void setYonetici(boolean yonetici) {       #! çerçeve JSON'da "yonetici" görürse bunu çağırır!
        this.yonetici = yonetici;
    }
}
```

> [!TUZAK] İstek modelinde açık unutulan `setYonetici` (Toplu Atama / Mass Assignment)
> Bir web denetleyicisi doğrudan veritabanı/model sınıfını istek gövdesi olarak kabul ederse ve sınıfta `public void setYonetici(boolean)` tanımlıysa, JSON ayrıştırıcı istekteki `"yonetici": true` alanını gördüğünde bu setter metodunu otomatik çağırır! İstek kabul etmek için yalnızca dışarıdan alınmasına izin verilen alanları içeren ayrı bir DTO (`record`) kullanılır.
:::

::: anlat `record` · Değişmez veri taşıyıcılar (Java 16+)
Yalnızca veri taşımak için onlarca satırlık `private final` alan, kurucu, getter, `equals`, `hashCode` ve `toString` yazmak yerine modern Java'da **`record`** kullanılır:

```java
public record BiletIstegi(String baslik, int oncelik) {
    public BiletIstegi {                              #! sıkıştırılmış kurucu (compact constructor): doğrulama yeri
        baslik = (baslik == null) ? "" : baslik.trim();
        if (oncelik < 1 || oncelik > 5) {
            oncelik = 3;
        }
    }
}
```

Bir `record` tanımı derlendiğinde Java şunları otomatik üretir:
- Tüm bileşenler `private final` olur (sonradan değiştirilemez, setter **yoktur**).
- Erişim metotları `get` öneki olmadan doğrudan bileşen adıyla çağrılır: `istek.baslik()`, `istek.oncelik()`.
- `equals()` ve `hashCode()` referansa değil, **tüm bileşenlerin değerine** bakar.
- `toString()` metodu `"BiletIstegi[baslik=..., oncelik=...]"` biçiminde okunaklı çıktı üretir.

> [!DERİN] `record` içinde setter olmadığı için değişmezdir
> Sıkıştırılmış kurucu (`public BiletIstegi { ... }`) sonunda `this.baslik = baslik` ataması derleyici tarafından otomatik yapılır; nesne bir kez oluştuktan sonra hiçbir alanı değiştirilemez.
:::

::: tahmin
Java 21 ile çalıştırıldığında bu sınıf ne yazdırır?

```java
public class Ornek {
    record Nokta(String ad, int puan) {
        Nokta {
            ad = ad.trim().toLowerCase();
            if (puan < 0) puan = 0;
        }
    }

    public static void main(String[] args) {
        Nokta n1 = new Nokta("  Web01 ", -5);
        Nokta n2 = new Nokta("web01", 0);
        System.out.println(n1);
        System.out.println(n1.ad() + ":" + n1.puan());
        System.out.println(n1.equals(n2));
    }
}
```

```gercek
Nokta[ad=web01, puan=0]
web01:0
true
```

???

`Nokta[ad=web01, puan=0]`, `web01:0`, `true`. Sıkıştırılmış kurucu `"  Web01 "` metnini `"web01"` yapar ve `-5` puanını `0`'a çeker. `record`'un otomatik `toString()` çıktısı `Nokta[ad=web01, puan=0]` biçimindedir. `n1` ve `n2`'nin her iki bileşeni de (`"web01"` ve `0`) eşit olduğu için `n1.equals(n2)` `true` döner.
:::

::: gorev JavaBean setter bağlayıcı
Bir Java çerçevesinin sınıftaki `public void setXxx(...)` metotlarını bulup gelen JSON sözlüğündeki anahtarları bağlamasını Python'da `bean_bagla(setter_metotlari, gelen_json)` fonksiyonu olarak simüle et:
- Yalnızca `"set"` ile başlayan ve uzunluğu en az 4 olan (`"setA"` gibi) metot adları birer özellik (property) kabul edilir.
- Özellik adı, `"set"` sonrasındaki ilk harfin küçük harfe çevrilmesiyle elde edilir (`"setKullaniciAdi"` → `"kullaniciAdi"`, `"setId"` → `"id"`).
- `gelen_json` sözlüğünde bu özellik adı varsa yeni sonuç sözlüğüne dahil edilir; setter'ı olmayan JSON alanları yok sayılır.

```starter
def bean_bagla(setter_metotlari, gelen_json):
    return dict(gelen_json)
```

```test
need("bean_bagla")
eq(bean_bagla(["setKullaniciAdi", "setDepartman", "getRol", "set", "ayarla"],
              {"kullaniciAdi": "ali", "departman": "BT", "rol": "admin", "set": 1}),
   {"kullaniciAdi": "ali", "departman": "BT"},
   "yalnız geçerli setXxx metotlarına karşılık gelen alanlar bağlanmalı, rol elenmeli")
eq(bean_bagla(["setA", "setB"], {"a": 10, "A": 20}),
   {"a": 10},
   "en kısa geçerli setter 'setA' (uzunluk 4) -> özellik 'a'")
eq(bean_bagla(["set"], {"": 1}), {}, "uzunluğu 3 olan 'set' geçerli bir setter değildir")
```

```solution
def bean_bagla(setter_metotlari, gelen_json):
    izinli = set()
    for m in setter_metotlari:
        if m.startswith("set") and len(m) >= 4:
            ozellik = m[3].lower() + m[4:]
            izinli.add(ozellik)
    return {k: v for k, v in gelen_json.items() if k in izinli}
```

```hint
`m.startswith("set") and len(m) >= 4` kontrolünden geçen her metot için `ozellik = m[3].lower() + m[4:]` hesapla ve yalnızca `izinli` kümesinde bulunan JSON anahtarlarını döndür.
```
:::

::: gorev `record` kurucu doğrulaması ve `toString`
Aşağıdaki Java `record` tanımının sıkıştırılmış kurucusunu ve otomatik `toString()` çıktısını Python'da `istek_kaydi(yol, limit, siralama)` fonksiyonu olarak üret.

```java
public record AramaKaydi(String yol, int limit, String siralama) {
    public AramaKaydi {
        yol = (yol == null || yol.isBlank()) ? "/api/varsayilan" : yol.trim();
        if (limit < 1) {
            limit = 10;
        } else if (limit > 100) {
            limit = 100;
        }
        siralama = "azalan".equalsIgnoreCase(siralama) ? "DESC" : "ASC";
    }
}
```

```starter
def istek_kaydi(yol, limit, siralama):
    return f"AramaKaydi[yol={yol}, limit={limit}, siralama={siralama}]"
```

```test
need("istek_kaydi")
eq(istek_kaydi(" /api/biletler ", 25, "Azalan"),
   "AramaKaydi[yol=/api/biletler, limit=25, siralama=DESC]",
   "normal girdi ve büyük-küçük harf duyarsız azalan")
eq(istek_kaydi("   ", 1, "artan"),
   "AramaKaydi[yol=/api/varsayilan, limit=1, siralama=ASC]",
   "boşluklu yol varsayılana dönmeli, alt sınır limit=1 korunmalı")
eq(istek_kaydi(None, 0, None),
   "AramaKaydi[yol=/api/varsayilan, limit=10, siralama=ASC]",
   "limit=0 (< 1) ise 10'a çekilmeli, null yol ve sıralama varsayılana dönmeli")
eq(istek_kaydi("/ara", 100, "DESC"),
   "AramaKaydi[yol=/ara, limit=100, siralama=ASC]",
   "üst sınır limit=100 korunmalı; 'DESC' metni 'azalan' olmadığı için ASC olmalı")
eq(istek_kaydi("/ara", 101, "azalan"),
   "AramaKaydi[yol=/ara, limit=100, siralama=DESC]",
   "limit=101 (> 100) ise 100'e tavanlanmalı")
```

```solution
def istek_kaydi(yol, limit, siralama):
    if yol is None or not yol.strip():
        temiz_yol = "/api/varsayilan"
    else:
        temiz_yol = yol.strip()
    temiz_limit = 10 if limit < 1 else min(limit, 100)
    temiz_sira = "DESC" if (siralama is not None and siralama.lower() == "azalan") else "ASC"
    return f"AramaKaydi[yol={temiz_yol}, limit={temiz_limit}, siralama={temiz_sira}]"
```

```hint
`limit < 1` ise `10`, `limit > 100` ise `100` yap; `1` ve `100` sınır değerleri olduğu gibi kalmalı. `siralama` yalnızca `"azalan"` (büyük-küçük harf duyarsız) ise `"DESC"`, diğer her durumda `"ASC"` olur.
```
:::
