---
id: jv04
title: null, NullPointerException ve Optional
summary: null referanslar, sabit.equals(degisken) kalıbı, Objects.equals ve Optional<T> boru hattı (ofNullable, map, filter, orElse).
---

::: anlat `NullPointerException` ve güvenli karşılaştırma
Java'da değeri `null` olan bir referans üzerinden herhangi bir metot çağırmak veya alan okumak anında **`NullPointerException` (NPE)** fırlatır. HTTP başlığı (`request.getHeader("X-Rol")`), sorgu parametresi (`request.getParameter("tip")`) veya harita araması (`map.get("anahtar")`) bulunamadığında `null` döndürür.

Bu yüzden deneyimli Java geliştiricileri `.equals()` çağrısında **sabit metni sola** yazar:

```java
String rol = istek.getHeader("X-Rol");             #! başlık yoksa rol == null

// TEHLİKELİ: rol null ise NullPointerException fırlatır!
// if (rol.equals("yonetici")) { ... }

// GÜVENLİ: "yonetici" sabiti asla null değildir; rol null ise sessizce false döner
if ("yonetici".equals(rol)) {
    System.out.println("Yetkili istek");
}
```

İki değişken de `null` olabiliyorsa `java.util.Objects.equals(a, b)` kullanılır: ikisi de `null` ise `true`, yalnız biri `null` ise `false`, ikisi de doluysa `a.equals(b)` döndürür.

> [!DERİN] Java 14+ anlamlı NPE mesajları
> `a.b().c().d()` gibi zincirleme bir satırda NPE oluştuğunda modern JVM hangi halkada `null` döndüğünü açıkça yazar (`Cannot invoke "B.c()" because the return value of "A.b()" is null`). Yine de üretimde işlenmemiş NPE, HTTP `500 Internal Server Error` üretir.
:::

::: anlat `Optional<T>` zincirini okumak
`null` kontrollerini iç içe `if (x != null)` bloklarıyla yazmak yerine modern Java kodunda **`Optional<T>`** kutusu kullanılır. `Optional` bir değeri (ya da yokluğunu) güvenli bir boru hattından geçirir:

| Metot | Davranışı |
|---|---|
| `Optional.ofNullable(x)` | `x` `null` ise boş (`Optional.empty()`), değilse dolu kutu üretir |
| `.map(fn)` | Kutu doluysa fonksiyonu uygular; `fn` `null` döndürürse kutu **boşalır** |
| `.filter(kosul)` | Kutu doluysa ve koşul `true` ise değeri korur; `false` ise kutu **boşalır** |
| `.orElse(varsayilan)` | Kutu doluysa içindeki değeri, boşsa `varsayilan` değerini döndürür |
| `.orElseThrow(...)` | Kutu boşsa belirtilen istisnayı fırlatır |

```java
import java.util.Optional;

String ham = "  8080 ";
int port = Optional.ofNullable(ham)
    .map(String::trim)                             #! "8080"
    .filter(s -> !s.isEmpty())                     #! boş metinse elenir
    .map(Integer::parseInt)                        #! 8080
    .filter(p -> p >= 1024 && p <= 65535)          #! geçerli aralıkta mı?
    .orElse(3000);                                 #! herhangi bir adım boşalırsa 3000 döner
```

> [!TUZAK] `Optional.of(x)` ile `Optional.ofNullable(x)` farkı
> `Optional.of(x)` argüman olarak `null` kabul **etmez**; `x` `null` ise daha ilk satırda `NullPointerException` fırlatır! Dışarıdan gelen bir değer sarılıyorsa her zaman `Optional.ofNullable(x)` kullanılmalıdır.
:::

::: tahmin
Java 21 ile çalıştırıldığında bu sınıf ne yazdırır?

```java
import java.util.*;

public class Ornek {
    static String temizle(String Girdi) {
        return Optional.ofNullable(Girdi)
            .map(String::trim)
            .filter(s -> s.length() >= 3)
            .map(String::toUpperCase)
            .orElse("VARSAYILAN");
    }

    public static void main(String[] args) {
        System.out.println(temizle("  ab "));
        System.out.println(temizle("  abc "));
        System.out.println(temizle(null));
        System.out.println(Objects.equals(null, null));
    }
}
```

```gercek
VARSAYILAN
ABC
VARSAYILAN
true
```

???

`VARSAYILAN`, `ABC`, `VARSAYILAN`, `true`. `"  ab "` kırpılınca `"ab"` (uzunluk `2`) kalır; `s.length() >= 3` filtresinden geçemediği için kutu boşalır ve `orElse("VARSAYILAN")` döner. `"  abc "` kırpılınca `"abc"` (uzunluk `3`) filtreyi geçer ve `"ABC"` olur. `null` girdi `ofNullable` ile baştan boş kutu üretir. `Objects.equals(null, null)` ise `true` döndürür.
:::

::: gorev `Optional` ile zaman aşımı yapılandırması
Aşağıdaki Java metodunun davranışını Python'da `zaman_asimi_oku(ortam, anahtar, varsayilan)` fonksiyonu olarak kur.

```java
public static int zamanAsimiOku(Map<String, String> ortam, String anahtar, int varsayilan) {
    return Optional.ofNullable(ortam)
        .map(m -> m.get(anahtar))
        .map(String::trim)
        .filter(s -> s.matches("\\d+"))
        .map(Integer::parseInt)
        .filter(n -> n >= 5 && n <= 120)
        .orElse(varsayilan);
}
```

```starter
def zaman_asimi_oku(ortam, anahtar, varsayilan):
    if not ortam or anahtar not in ortam:
        return varsayilan
    return int(ortam[anahtar])
```

```test
need("zaman_asimi_oku")
eq(zaman_asimi_oku({"TIMEOUT": " 30 "}, "TIMEOUT", 15), 30, "geçerli sayı")
eq(zaman_asimi_oku({"TIMEOUT": "5"}, "TIMEOUT", 15), 5, "alt sınır 5 kabul edilmeli")
eq(zaman_asimi_oku({"TIMEOUT": "4"}, "TIMEOUT", 15), 15, "4 alt sınırın altında -> varsayilan")
eq(zaman_asimi_oku({"TIMEOUT": "120"}, "TIMEOUT", 15), 120, "üst sınır 120 kabul edilmeli")
eq(zaman_asimi_oku({"TIMEOUT": "121"}, "TIMEOUT", 15), 15, "121 üst sınırın üstünde -> varsayilan")
eq(zaman_asimi_oku({"TIMEOUT": "-10"}, "TIMEOUT", 15), 15, "negatif metin \\d+ ile eşleşmez -> varsayilan")
eq(zaman_asimi_oku({"TIMEOUT": "30sn"}, "TIMEOUT", 15), 15, "harf içeren metin -> varsayilan")
eq(zaman_asimi_oku({"TIMEOUT": None}, "TIMEOUT", 15), 15, "anahtar değeri None ise -> varsayilan")
eq(zaman_asimi_oku(None, "TIMEOUT", 15), 15, "ortam haritası None ise -> varsayilan")
```

```solution
import re

def zaman_asimi_oku(ortam, anahtar, varsayilan):
    if ortam is None:
        return varsayilan
    deger = ortam.get(anahtar)
    if deger is None:
        return varsayilan
    temiz = deger.strip()
    if not re.fullmatch(r"[0-9]+", temiz):
        return varsayilan
    n = int(temiz)
    if 5 <= n <= 120:
        return n
    return varsayilan
```

```hint
Java'daki `s.matches("\\d+")` tüm metnin (`re.fullmatch(r"[0-9]+", temiz)`) ASCII rakamlardan oluşmasını ister; ardından `5 <= n <= 120` aralığını kontrol et.
```
:::

::: gorev Güvenli profil karşılaştırması (`Objects.equals`)
Aşağıdaki Java metodunun davranışını Python'da `profil_degisti_mi(eski_profil, yeni_profil)` fonksiyonu olarak kur.

```java
public static List<String> profilDegistiMi(Map<String, String> eskiProfil, Map<String, String> yeniProfil) {
    List<String> degisenler = new ArrayList<>();
    for (String alan : List.of("ad", "eposta", "departman")) {
        String eski = eskiProfil.get(alan);
        String yeni = yeniProfil.get(alan);
        String eskiNorm = (eski == null || eski.trim().isEmpty()) ? null : eski.trim();
        String yeniNorm = (yeni == null || yeni.trim().isEmpty()) ? null : yeni.trim();
        if (!Objects.equals(eskiNorm, yeniNorm)) {
            degisenler.add(alan);
        }
    }
    return degisenler;
}
```

```starter
def profil_degisti_mi(eski_profil, yeni_profil):
    return [a for a in ("ad", "eposta", "departman") if eski_profil.get(a) != yeni_profil.get(a)]
```

```test
need("profil_degisti_mi")
eq(profil_degisti_mi({"ad": "Ali", "eposta": "  ", "departman": None},
                     {"ad": " Ali ", "eposta": None}),
   [], "boşluk ve None normalize edildiğinde fark yok")
eq(profil_degisti_mi({"ad": "Ali", "eposta": "a@b.com", "departman": "BT"},
                     {"ad": "Ali", "eposta": "yeni@b.com", "departman": "   "}),
   ["eposta", "departman"], "eposta ve departman değişti")
eq(profil_degisti_mi({}, {"ad": "Ayşe"}), ["ad"], "yalnız ad eklendi")
```

```solution
def _norm(deger):
    if deger is None:
        return None
    t = deger.strip()
    return None if not t else t

def profil_degisti_mi(eski_profil, yeni_profil):
    degisenler = []
    for alan in ("ad", "eposta", "departman"):
        if _norm(eski_profil.get(alan)) != _norm(yeni_profil.get(alan)):
            degisenler.append(alan)
    return degisenler
```

```hint
Her alan için değeri `.strip()` ile kırp; boş metinse `None` yap. Sonra eski ve yeni normalize değerleri `!=` ile karşılaştır.
```
:::
