---
id: jv07
title: İstisnalar ve try-with-resources
summary: Denetlenen (checked) ve çalışma zamanı (unchecked) istisnaları, try/catch/finally çalışma sırası, AutoCloseable ve sayfalama girdi doğrulaması.
---

::: anlat Denetlenen (Checked) ve Çalışma Zamanı (Unchecked) İstisnaları
Java'da hatalar `Throwable` kök sınıfından türer ve iki ana gruba ayrılır:

| Grup | Örnek Sınıflar | Derleyici Kuralı |
|---|---|---|
| **Checked (`Exception`)** | `IOException`, `SQLException`, `ParseException` | Metot imzasında **`throws ...`** ile bildirilmek ya da `try/catch` ile yakalanmak **zorundadır** |
| **Unchecked (`RuntimeException`)** | `NullPointerException`, `IllegalArgumentException`, `NumberFormatException`, `IndexOutOfBoundsException` | Bildirilmesi zorunlu değildir; beklenmeyen girdi/mantık hatalarında anında fırlatılır |

```java
public static int portCoz(String girdi) {
    try {
        int port = Integer.parseInt(girdi.trim());     #! sayı değilse NumberFormatException fırlatır
        if (port < 1 || port > 65535) {
            throw new IllegalArgumentException("aralik disi");
        }
        return port;
    } catch (NumberFormatException e) {
        return -1;
    } catch (IllegalArgumentException e) {
        return -2;
    }
}
```

> [!DERİN] `NumberFormatException`, `IllegalArgumentException` sınıfının alt sınıfıdır!
> `catch` blokları yukarıdan aşağıya sırayla denenir. `NumberFormatException` aslında `IllegalArgumentException`'dan türediği için üstteki `catch` bloğuna daha özel olan `NumberFormatException`, alttakine daha genel olan `IllegalArgumentException` yazılır. Tersini yazarsan derleyici `"exception has already been caught"` hatası verir.
:::

::: anlat `finally` sırası ve `try-with-resources`
`finally` bloğu, `try` veya `catch` içinde `return` deyimi bulunsa bile metottan çıkılmadan hemen önce **mutlaka çalışır**. Dosya, soket veya veritabanı bağlantısı gibi `AutoCloseable` kaynakları otomatik kapatmak için ise **`try (...)`** (`try-with-resources`) yapısı kullanılır:

```java
import java.io.*;

public static String ilkSatir(byte[] veri) throws IOException {
    try (var okuyucu = new BufferedReader(new InputStreamReader(new ByteArrayInputStream(veri)))) {
        return okuyucu.readLine();                     #! blok bittiğinde okuyucu.close() otomatik çağrılır
    }
}
```

> [!TUZAK] `finally` içinde `return` yazmak istisnayı yutar!
> `try` bloğu bir istisna fırlatsa bile `finally` bloğunun içinde `return` varsa, fırlatılan istisna **tamamen yutulur (kaybolur)** ve metot `finally` içindeki değeri döndürür. Kod incelerken `finally` içinde `return` görmek ciddi bir mantık kusuru işaretidir.
:::

::: tahmin
Java 21 ile çalıştırıldığında bu sınıf ne yazdırır?

```java
public class Ornek {
    static String islem(String girdi) {
        StringBuilder iz = new StringBuilder();
        try {
            iz.append("A");
            int n = Integer.parseInt(girdi);
            iz.append("B").append(n);
            return iz.toString();
        } catch (NumberFormatException e) {
            iz.append("C");
            return iz.toString();
        } finally {
            System.out.println("finally:" + iz);
        }
    }

    public static void main(String[] args) {
        System.out.println("sonuc:" + islem("12"));
        System.out.println("sonuc:" + islem("12x"));
    }
}
```

```gercek
finally:AB12
sonuc:AB12
finally:AC
sonuc:AC
```

???

`finally:AB12`, `sonuc:AB12`, `finally:AC`, `sonuc:AC`. `islem("12")` çağrısında `return iz.toString()` değeri hazırlanır, metottan dönülmeden hemen önce `finally` bloğu çalışıp `finally:AB12` basar, ardından `main` içinde `sonuc:AB12` yazdırılır. `"12x"` girdisinde `parseInt` `NumberFormatException` fırlatır (`"B"` eklenmez), `catch` bloğu `"C"` ekler, yine önce `finally:AC` sonra `sonuc:AC` basılır.
:::

::: gorev HTTP hata eşleyici (`catch` hiyerarşisi)
Aşağıdaki Java denetleyici metodunun hangi girdide hangi HTTP durum kodu ve mesajı döndürdüğünü Python'da `istek_limit_coz(ham_limit, maksimum)` fonksiyonu olarak kur.

```java
public static String istekLimitCoz(String hamLimit, int maksimum) {
    try {
        if (hamLimit == null) {
            throw new NullPointerException("eksik");
        }
        int deger = Integer.parseInt(hamLimit.trim());
        if (deger <= 0 || deger > maksimum) {
            throw new IllegalArgumentException("sinir");
        }
        return "200:OK:" + deger;
    } catch (NullPointerException e) {
        return "400:EKSIK_PARAMETRE";
    } catch (NumberFormatException e) {
        return "400:SAYI_DEGIL";
    } catch (IllegalArgumentException e) {
        return "422:SINIR_DISI";
    }
}
```

```starter
def istek_limit_coz(ham_limit, maksimum):
    return f"200:OK:{ham_limit}"
```

```test
need("istek_limit_coz")
eq(istek_limit_coz(" 25 ", 50), "200:OK:25", "geçerli sayı")
eq(istek_limit_coz("1", 50), "200:OK:1", "alt sınır 1 kabul edilmeli")
eq(istek_limit_coz("50", 50), "200:OK:50", "üst sınır 50 kabul edilmeli")
eq(istek_limit_coz("0", 50), "422:SINIR_DISI", "0 (deger <= 0) -> 422:SINIR_DISI")
eq(istek_limit_coz("-5", 50), "422:SINIR_DISI", "negatif sayı -> 422:SINIR_DISI")
eq(istek_limit_coz("51", 50), "422:SINIR_DISI", "51 (> maksimum) -> 422:SINIR_DISI")
eq(istek_limit_coz("abc", 50), "400:SAYI_DEGIL", "harf -> NumberFormatException -> 400:SAYI_DEGIL")
eq(istek_limit_coz("   ", 50), "400:SAYI_DEGIL", "boş metin -> NumberFormatException -> 400:SAYI_DEGIL")
eq(istek_limit_coz(None, 50), "400:EKSIK_PARAMETRE", "None -> 400:EKSIK_PARAMETRE")
```

```solution
import re

def istek_limit_coz(ham_limit, maksimum):
    if ham_limit is None:
        return "400:EKSIK_PARAMETRE"
    temiz = ham_limit.strip()
    if not re.fullmatch(r"[+-]?[0-9]+", temiz):
        return "400:SAYI_DEGIL"
    deger = int(temiz)
    if deger <= 0 or deger > maksimum:
        return "422:SINIR_DISI"
    return f"200:OK:{deger}"
```

```hint
Önce `ham_limit is None` kontrolü (`400:EKSIK_PARAMETRE`), sonra tam sayı biçimi kontrolü (`400:SAYI_DEGIL`), en son `deger <= 0 or deger > maksimum` sınır kontrolü (`422:SINIR_DISI`) çalışır.
```
:::

::: gorev `try / catch / finally` yürütme izi
Aşağıdaki Java metodunda üç farklı adım (`adim1`, `adim2`, `kapat`) sırayla çalışıyor ve her biri `(basarili_mi, etiket)` bilgisini iz listesine ekliyor. Bu akışı Python'da `kaynak_calistir(veri, kapasite)` fonksiyonu olarak kur.

```java
public static List<String> kaynakCalistir(String veri, int kapasite) {
    List<String> iz = new ArrayList<>();
    iz.add("ACILDI");
    try {
        if (veri == null) {
            throw new IllegalArgumentException("BOZUK_VERI");
        }
        String temiz = veri.trim();
        if (temiz.length() > kapasite) {
            throw new IllegalStateException("KAPASITE_ASILDI");
        }
        iz.add("ISLENDI:" + temiz.length());
    } catch (IllegalArgumentException e) {
        iz.add("HATA:" + e.getMessage());
    } catch (IllegalStateException e) {
        iz.add("UYARI:" + e.getMessage());
    } finally {
        iz.add("KAPANDI");
    }
    return iz;
}
```

```starter
def kaynak_calistir(veri, kapasite):
    return ["ACILDI", "KAPANDI"]
```

```test
need("kaynak_calistir")
eq(kaynak_calistir("  merhaba ", 7),
   ["ACILDI", "ISLENDI:7", "KAPANDI"],
   "tam kapasite sınırında (7 <= 7) başarılı işlenmeli ve KAPANDI eklenmeli")
eq(kaynak_calistir("  merhaba ", 6),
   ["ACILDI", "UYARI:KAPASITE_ASILDI", "KAPANDI"],
   "kapasite 6 iken uzunluk 7 (> 6) -> UYARI:KAPASITE_ASILDI ve KAPANDI")
eq(kaynak_calistir("", 0),
   ["ACILDI", "ISLENDI:0", "KAPANDI"],
   "boş metin ve 0 kapasitede (0 <= 0) başarılı")
eq(kaynak_calistir(None, 10),
   ["ACILDI", "HATA:BOZUK_VERI", "KAPANDI"],
   "null veride HATA:BOZUK_VERI ve KAPANDI")
```

```solution
def kaynak_calistir(veri, kapasite):
    iz = ["ACILDI"]
    try:
        if veri is None:
            iz.append("HATA:BOZUK_VERI")
        else:
            temiz = veri.strip()
            if len(temiz) > kapasite:
                iz.append("UYARI:KAPASITE_ASILDI")
            else:
                iz.append(f"ISLENDI:{len(temiz)}")
    finally:
        iz.append("KAPANDI")
    return iz
```

```hint
Her durumda ilk eleman `"ACILDI"`, son eleman `"KAPANDI"` olur. Ortadaki eleman `veri is None` ise `"HATA:BOZUK_VERI"`, `len(temiz) > kapasite` ise `"UYARI:KAPASITE_ASILDI"`, değilse `f"ISLENDI:{len(temiz)}"` olur.
```
:::
