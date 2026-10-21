---
id: jv06
title: Arayüzler, Lambda ve Stream Boru Hattı
summary: interface sözleşmesi, fonksiyonel arayüzler, -> lambda ifadeleri ve Stream API (filter, map, sorted, limit, anyMatch, allMatch).
---

::: anlat `interface` ve Lambda ifadeleri (`->`)
Java'da bir **`interface` (arayüz)**, sınıfların hangi metotları sunacağını belirten bir sözleşmedir. Web uygulamalarında servis katmanı genellikle bir arayüz (`BiletServisi`) olarak tanımlanır, asıl kod ise onu `implements` eden sınıfta (`BiletServisiImpl`) bulunur.

Tek bir soyut metodu olan arayüzlere **fonksiyonel arayüz** denir ve uzun sınıf tanımı yerine **`->` lambda** ifadesiyle yazılır:

| Arayüz | İmza | Lambda Örneği |
|---|---|---|
| `Predicate<T>` | `T -> boolean` | `s -> s.startsWith("/api/")` |
| `Function<T, R>` | `T -> R` | `s -> s.trim().toLowerCase()` |
| `Consumer<T>` | `T -> void` | `s -> System.out.println(s)` |

```java
import java.util.function.Predicate;

Predicate<String> icAgMi = ip -> ip.startsWith("10.") || ip.startsWith("192.168.");
System.out.println(icAgMi.test("10.0.4.12"));     #! true
```

> [!NOT] Metot referansları (`Sinif::metot`)
> `s -> s.trim()` yerine yazılan `String::trim` veya `x -> Integer.parseInt(x)` yerine yazılan `Integer::parseInt` birer **metot referansıdır**; lambda ile birebir aynı işi yapar.
:::

::: anlat Stream API boru hattını okumak
Java 8+ kodunda döngüler yerine çoğu zaman `.stream()` boru hattı görürsün. Okurken ara adımlar ile sonlandırıcı adımı ayır:

```java
import java.util.*;

record Istek(String yol, int sureMs, int durum) {}

List<Istek> kayitlar = List.of(
    new Istek("/api/odeme", 420, 200),
    new Istek("/statik/logo.png", 15, 200),
    new Istek("/api/sepet", 850, 500),
    new Istek("/api/urun", 180, 200)
);

List<String> yavasApi = kayitlar.stream()
    .filter(k -> k.yol().startsWith("/api/"))      #! yalnızca /api/ ile başlayanlar
    .filter(k -> k.sureMs() >= 300)                #! süresi en az 300 ms olanlar
    .sorted(Comparator.comparingInt(Istek::sureMs).reversed()) #! süreden çoktan aza
    .map(k -> k.yol() + " (" + k.sureMs() + "ms)") #! metne dönüştür
    .toList();                                     #! değişmez liste olarak topla
```

Karar metotları (`anyMatch`, `allMatch`, `noneMatch`) ise `boolean` döndürür:
- `stream.anyMatch(kosul)` — Python'daki `any(...)`
- `stream.allMatch(kosul)` — Python'daki `all(...)`
- `stream.noneMatch(kosul)` — Python'daki `not any(...)`

> [!TUZAK] Boş bir Stream üzerinde `allMatch` ve `anyMatch`
> Koleksiyon **boşsa**:
> - `bosListe.stream().anyMatch(...)` → **`false`** döner.
> - `bosListe.stream().allMatch(...)` → **`true`** döner (koşulu bozan hiçbir eleman yoktur — *vacuous truth*)!
> Bir yetki kontrolü `roller.stream().allMatch(r -> r.equals("YONETICI"))` şeklinde yazılmışsa ve kullanıcının rol listesi boşsa (`[]`), `allMatch` **`true`** döndürerek yetki kontrolünü yanlışlıkla geçirebilir!
:::

::: tahmin
Java 21 ile çalıştırıldığında bu sınıf ne yazdırır?

```java
import java.util.*;

public class Ornek {
    public static void main(String[] args) {
        List<String> roller = List.of();
        System.out.println(roller.stream().allMatch(r -> r.equals("ADMIN")));
        System.out.println(roller.stream().anyMatch(r -> r.equals("ADMIN")));

        List<Integer> sureler = List.of(120, 45, 300, 180, 90);
        List<Integer> sonuc = sureler.stream()
            .filter(s -> s >= 100)
            .sorted()
            .limit(2)
            .toList();
        System.out.println(sonuc);
    }
}
```

```gercek
true
false
[120, 180]
```

???

`true`, `false`, `[120, 180]`. Boş listede `allMatch` her zaman `true`, `anyMatch` ise `false` döner. `sureler` listesinde `s >= 100` koşulunu sağlayanlar `120, 300, 180` olur; `.sorted()` bunları `[120, 180, 300]` olarak küçükten büyüğe dizer ve `.limit(2)` ilk ikisini (`[120, 180]`) alır.
:::

::: gorev Stream boru hattı ile uç nokta raporu
Aşağıdaki Java Stream boru hattının ürettiği listeyi döndüren `yavas_uc_noktalar(kayitlar, esik_ms, en_fazla)` fonksiyonunu Python'da yaz. Her kayıt `{"yol": str, "sure_ms": int, "durum": int}` biçiminde bir sözlüktür.

```java
public static List<String> yavasUcNoktalar(List<Kayit> kayitlar, int esikMs, int enFazla) {
    if (enFazla <= 0) {
        return List.of();
    }
    return kayitlar.stream()
        .filter(k -> k.durum() >= 200 && k.durum() < 500)
        .filter(k -> k.sureMs() >= esikMs)
        .sorted(Comparator.comparingInt(Kayit::sureMs).reversed()
                .thenComparing(Kayit::yol))
        .limit(enFazla)
        .map(k -> k.yol() + ":" + k.sureMs())
        .toList();
}
```

```starter
def yavas_uc_noktalar(kayitlar, esik_ms, en_fazla):
    return [f"{k['yol']}:{k['sure_ms']}" for k in kayitlar[:en_fazla]]
```

```test
need("yavas_uc_noktalar")
ornek = [
    {"yol": "/api/b", "sure_ms": 200, "durum": 200},
    {"yol": "/api/a", "sure_ms": 200, "durum": 404},
    {"yol": "/api/c", "sure_ms": 500, "durum": 500},
    {"yol": "/api/d", "sure_ms": 199, "durum": 200},
    {"yol": "/api/e", "sure_ms": 350, "durum": 499},
]
eq(yavas_uc_noktalar(ornek, 200, 5),
   ["/api/e:350", "/api/a:200", "/api/b:200"],
   "durum 200..499 ve sure_ms >= 200 süzülmeli; eşit sürede yol adına göre artan sıralanmalı")
eq(yavas_uc_noktalar(ornek, 200, 2),
   ["/api/e:350", "/api/a:200"],
   "limit(2) en fazla 2 kayıt döndürmeli")
eq(yavas_uc_noktalar(ornek, 200, 0), [], "enFazla 0 ise boş liste")
eq(yavas_uc_noktalar([{"yol": "/x", "sure_ms": 300, "durum": 199}], 200, 5), [], "durum 199 (< 200) elenmeli")
```

```solution
def yavas_uc_noktalar(kayitlar, esik_ms, en_fazla):
    secilen = [
        k for k in kayitlar
        if 200 <= k["durum"] < 500 and k["sure_ms"] >= esik_ms
    ]
    secilen.sort(key=lambda k: (-k["sure_ms"], k["yol"]))
    return [f"{k['yol']}:{k['sure_ms']}" for k in secilen[:en_fazla]]
```

```hint
`200 <= k["durum"] < 500` ve `k["sure_ms"] >= esik_ms` ile süz; `key=lambda k: (-k["sure_ms"], k["yol"])` ile sırala ve `[:en_fazla]` dilimini al.
```
:::

::: gorev `allMatch` boş liste tuzağı ve düzeltmesi
Aşağıdaki iki Java metodunu karşılaştır:
- `kusurluYetki( List<String> izinler )`: yalnızca `izinler.stream().allMatch(s -> s.startsWith("OKU_"))` çağırır.
- `guvenliYetki( List<String> izinler )`: önce `!izinler.isEmpty()` kontrol eder, sonra `allMatch` çağırır.

Python'da `yetki_karsilastir(izinler)` fonksiyonunu yaz ve `(kusurlu_sonuc, guvenli_sonuc)` boolean demetini döndür.

```java
public static boolean kusurluYetki(List<String> izinler) {
    return izinler.stream().allMatch(s -> s.startsWith("OKU_"));
}

public static boolean guvenliYetki(List<String> izinler) {
    return !izinler.isEmpty()
        && izinler.stream().allMatch(s -> s.startsWith("OKU_"));
}
```

```starter
def yetki_karsilastir(izinler):
    return False, False
```

```test
need("yetki_karsilastir")
eq(yetki_karsilastir([]), (True, False), "boş listede kusurlu allMatch True döner, güvenli False döner")
eq(yetki_karsilastir(["OKU_GENEL"]), (True, True), "boş olmayan ve OKU_ ile başlayan listede her ikisi de True döner")
eq(yetki_karsilastir(["OKU_GENEL", "OKU_RAPOR"]), (True, True), "tümü OKU_ ile başlıyorsa (True, True)")
eq(yetki_karsilastir(["OKU_RAPOR", "YAZ_GENEL"]), (False, False), "YAZ_GENEL yüzünden her ikisi de False")
```

```solution
def yetki_karsilastir(izinler):
    kusurlu = all(s.startswith("OKU_") for s in izinler)
    guvenli = bool(izinler) and kusurlu
    return kusurlu, guvenli
```

```hint
Python'daki `all(...)` da tıpkı Java'daki `allMatch(...)` gibi boş liste üzerinde `True` döndürür!
```
:::
