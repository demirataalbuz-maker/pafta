---
id: jv08
title: Dosya Yolları · Path, resolve ve normalize
summary: java.nio.file.Path işlemleri, resolve ve normalize davranışları, kök dizin dışına çıkma (Path Traversal) kontrolünde String.startsWith ile Path.startsWith farkı.
---

::: anlat `Path.of`, `resolve` ve `normalize`
Modern Java web uygulamalarında dosya yolları `java.nio.file.Path` sınıfıyla yönetilir. İki yolu birleştirmek için `taban.resolve(altYol)`, `.` ve `..` bileşenlerini sadeleştirmek için `.normalize()` çağrılır:

```java
import java.nio.file.Path;

Path taban = Path.of("/var/uygulama/raporlar");
Path p1 = taban.resolve("2026/ekim.pdf").normalize();     #! /var/uygulama/raporlar/2026/ekim.pdf
Path p2 = taban.resolve("../ayarlar.conf").normalize();   #! /var/uygulama/ayarlar.conf
Path p3 = taban.resolve("/etc/hosts").normalize();        #! /etc/hosts (mutlak yol tabanı tamamen ezer!)
```

Tabloya dikkatlice bak:
1. `resolve` metoduna **`/` ile başlayan mutlak bir yol** verilirse (`"/etc/hosts"`), Java'da (tıpkı Python `pathlib.Path` gibi) taban dizin **tamamen yok sayılır** ve doğrudan `/etc/hosts` döner!
2. `resolve` tek başına `..` bileşenlerini temizlemez; mutlaka ardından **`.normalize()`** çağrılmalıdır.

> [!TUZAK] `normalize()` çağrılmadan yapılan `startsWith` kontrolü
> `taban.resolve("../../gizli.txt")` ifadesi normalize edilmeden önce `/var/uygulama/raporlar/../../gizli.txt` olarak kalır ve `startsWith(taban)` kontrolünü **geçer**! Dosya sistemi ise yolu açarken `..` bileşenlerini çözüp üst dizine çıkar. Bu yüzden sıra her zaman `taban.resolve(girdi).normalize()` olmalı ve kontrol **normalize edilmiş** yol üzerinde yapılmalıdır.
:::

::: anlat `Path.startsWith(Path)` ile `String.startsWith(String)` farkı
Bir yolun izin verilen kök dizin içinde kalıp kalmadığını denetlerken Java'da iki farklı `startsWith` metodu vardır ve ikisi çok farklı davranır:

```java
Path taban = Path.of("/var/rapor").normalize();
Path kardes = Path.of("/var/rapor_gizli/dosya.txt").normalize();

// YANLIŞ: Metin (String) olarak önek kontrolü!
System.out.println(kardes.toString().startsWith(taban.toString())); // true! ("/var/rapor_gizli..." metni "/var/rapor" ile başlar!)

// DOĞRU: Path bileşeni olarak önek kontrolü!
System.out.println(kardes.startsWith(taban));                       // false! ("rapor_gizli" bileşeni != "rapor")
```

- **`String.startsWith`**: Yalnızca karakter dizisine bakar; `/var/rapor_yedek` dizinini `/var/rapor` dizininin altındaymış gibi kabul eder (**Partial Path Traversal**).
- **`Path.startsWith(Path)`**: Dizin bileşenlerini (`["var", "rapor_gizli"]` ile `["var", "rapor"]`) karşılaştırır ve kardeş dizini reddeder.

> [!GÜVENLİK] Güvenli yol çözümleme kalıbı
> ```java
> Path hedef = taban.resolve(istekYolu).normalize();
> if (!hedef.startsWith(taban) || hedef.equals(taban)) {
>     throw new SecurityException("Geçersiz dosya yolu");
> }
> ```
:::

::: tahmin
Java 21 ile çalıştırıldığında bu sınıf ne yazdırır?

```java
import java.nio.file.Path;

public class Ornek {
    public static void main(String[] args) {
        Path taban = Path.of("/var/rapor").normalize();
        Path a = taban.resolve("2026/../ekim.pdf").normalize();
        Path b = taban.resolve("../rapor_ek/a.pdf").normalize();

        System.out.println(a.toString().replace('\\', '/'));
        System.out.println(a.startsWith(taban));
        System.out.println(b.toString().replace('\\', '/'));
        System.out.println(b.toString().replace('\\', '/').startsWith(taban.toString().replace('\\', '/')));
        System.out.println(b.startsWith(taban));
    }
}
```

```gercek
/var/rapor/ekim.pdf
true
/var/rapor_ek/a.pdf
true
false
```

???

`/var/rapor/ekim.pdf`, `true`, `/var/rapor_ek/a.pdf`, `true`, `false`. `a` yolu normalize edilince `/var/rapor/ekim.pdf` olur ve `taban` içindedir (`true`). `b` yolu ise `/var/rapor_ek/a.pdf` kardeş dizinine çıkar; metin (`String`) olarak `startsWith("/var/rapor")` kontrolü yanıltıcı biçimde `true` dönerken, bileşen bazlı `b.startsWith(taban)` kontrolü doğru olarak `false` döner.
:::

::: gorev Güvenli `Path` çözümleyici
Aşağıdaki Java metodunun davranışını Python'da `guvenli_yol_coz(taban_dizin, kullanici_girdisi)` fonksiyonu olarak kur. POSIX (`/`) yol biçimini kullan; geçerliyse normalize edilmiş tam yolu (`"/var/rapor/2026/a.pdf"` gibi), geçersizse `None` döndür.

```java
public static String guvenliYolCoz(String tabanDizin, String kullaniciGirdisi) {
    if (kullaniciGirdisi == null || kullaniciGirdisi.isBlank() || kullaniciGirdisi.indexOf('\\') != -1) {
        return null;
    }
    Path taban = Path.of(tabanDizin).normalize();
    Path hedef = taban.resolve(kullaniciGirdisi.trim()).normalize();
    if (!hedef.startsWith(taban) || hedef.equals(taban)) {
        return null;
    }
    return hedef.toString().replace('\\', '/');
}
```

```starter
import posixpath

def guvenli_yol_coz(taban_dizin, kullanici_girdisi):
    if not kullanici_girdisi:
        return None
    return posixpath.normpath(posixpath.join(taban_dizin, kullanici_girdisi))
```

```test
need("guvenli_yol_coz")
eq(guvenli_yol_coz("/var/rapor", "2026/ekim.pdf"), "/var/rapor/2026/ekim.pdf", "normal alt dosya")
eq(guvenli_yol_coz("/var/rapor", "alt/../ekim.pdf"), "/var/rapor/ekim.pdf", "taban içinde kalan .. normalize edilmeli")
eq(guvenli_yol_coz("/var/rapor", "../rapor_gizli/x.pdf"), None, "kardeş dizin (/var/rapor_gizli) reddedilmeli!")
eq(guvenli_yol_coz("/var/rapor", "../gizli.txt"), None, "üst dizine çıkış reddedilmeli")
eq(guvenli_yol_coz("/var/rapor", "/etc/passwd"), None, "mutlak yol tabanı ezeceği için reddedilmeli")
eq(guvenli_yol_coz("/var/rapor", "."), None, "hedef.equals(taban) (dizin kendisi) reddedilmeli")
eq(guvenli_yol_coz("/var/rapor", "alt/.."), None, "normalize sonrası tabana eşit olan yol reddedilmeli")
eq(guvenli_yol_coz("/var/rapor", "2026\\ekim.pdf"), None, "ters eğik çizgi reddedilmeli")
eq(guvenli_yol_coz("/var/rapor", "   "), None, "boşluklu girdi reddedilmeli")
eq(guvenli_yol_coz("/var/rapor", None), None, "None reddedilmeli")
```

```solution
import posixpath

def guvenli_yol_coz(taban_dizin, kullanici_girdisi):
    if kullanici_girdisi is None or not kullanici_girdisi.strip() or "\\" in kullanici_girdisi:
        return None
    taban = posixpath.normpath(taban_dizin)
    hedef = posixpath.normpath(posixpath.join(taban, kullanici_girdisi.strip()))
    taban_parcalar = [p for p in taban.split("/") if p]
    hedef_parcalar = [p for p in hedef.split("/") if p]
    if len(hedef_parcalar) <= len(taban_parcalar):
        return None
    if hedef_parcalar[:len(taban_parcalar)] != taban_parcalar:
        return None
    return hedef
```

```hint
`posixpath.normpath(posixpath.join(taban, kullanici_girdisi.strip()))` ile yolu normalize et. Bileşen bazlı `hedef.startsWith(taban) and not hedef.equals(taban)` kontrolü için her iki yolu `"/"` ile parçalayıp `len(hedef_parcalar) > len(taban_parcalar)` ve `hedef_parcalar[:len(taban_parcalar)] == taban_parcalar` şartını kontrol et.
```
:::

::: gorev `.properties` yapılandırma satırı okuyucu
Java uygulamalarında `.properties` dosyaları `anahtar=değer` satırlarından oluşur; `#` veya `!` ile başlayan satırlar yorumdur. Aşağıdaki Java metodunun davranışını Python'da `ozellikleri_oku(metin)` fonksiyonu olarak kur.

```java
public static Map<String, String> ozellikleriOku(String metin) {
    Map<String, String> ayarlar = new LinkedHashMap<>();
    if (metin == null) {
        return ayarlar;
    }
    for (String hamSatir : metin.split("\n")) {
        String satir = hamSatir.trim();
        if (satir.isEmpty() || satir.startsWith("#") || satir.startsWith("!")) {
            continue;
        }
        int ayirici = satir.indexOf('=');
        if (ayirici == -1) {
            ayirici = satir.indexOf(':');
        }
        if (ayirici <= 0) {
            continue;
        }
        String anahtar = satir.substring(0, ayirici).trim();
        String deger = satir.substring(ayirici + 1).trim();
        ayarlar.put(anahtar, deger);
    }
    return ayarlar;
}
```

```starter
def ozellikleri_oku(metin):
    return {}
```

```test
need("ozellikleri_oku")
ornek = """
# yorum.port = 1111
! yedek.ip : 10.0.0.1
sunucu.port = 8080
sunucu.ip : 127.0.0.1
url = http://localhost:9000/api
=gecersiz
:gecersiz2
ayiricisiz_satir
sunucu.port = 9090
"""
eq(ozellikleri_oku(ornek),
   {"sunucu.port": "9090", "sunucu.ip": "127.0.0.1", "url": "http://localhost:9000/api"},
   "# ve ! yorum satırları (içinde = veya : geçse bile) atlanmalı; = varsa : aranmamalı; son değer kazanmalı")
eq(ozellikleri_oku(None), {}, "None girdi boş sözlük dönmeli")
```

```solution
def ozellikleri_oku(metin):
    ayarlar = {}
    if metin is None:
        return ayarlar
    for ham_satir in metin.split("\n"):
        satir = ham_satir.strip()
        if satir.startswith(("#", "!")):
            continue
        ayirici = satir.find("=")
        if ayirici == -1:
            ayirici = satir.find(":")
        if ayirici <= 0:
            continue
        anahtar = satir[:ayirici].strip()
        deger = satir[ayirici + 1:].strip()
        ayarlar[anahtar] = deger
    return ayarlar
```

```hint
Önce `satir.find("=")` dene; yalnızca `-1` dönerse `satir.find(":")` dene (`url = http://...` satırında `=` bulunduğu için `:` aranmaz!). `ayirici <= 0` ise satırı atla.
```
:::
