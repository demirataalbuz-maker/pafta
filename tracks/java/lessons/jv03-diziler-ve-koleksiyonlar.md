---
id: jv03
title: Diziler, Koleksiyonlar ve Kutulama
summary: Sabit boyutlu diziler ile List/Map/Set farkı, List.of değişmezliği, getOrDefault ve Integer (-128..127) önbellek tuzağı.
---

::: anlat Diziler (`T[]`), `List` ve `Map`
Java'da sabit uzunluklu diziler (`String[]`) ile dinamik koleksiyonlar (`List<String>`, `Map<String, Integer>`, `Set<String>`) birlikte kullanılır. Okurken uzunluk ve erişim sözdizimine dikkat et:

| Yapı | Uzunluk | Eleman Okuma | Değiştirilebilirlik |
|---|---|---|---|
| `String[] a` | `a.length` *(alan)* | `a[i]` | Uzunluğu sabittir, elemanları değişir |
| `List<String> l` | `l.size()` *(metot)* | `l.get(i)` | `new ArrayList<>()` değişir; **`List.of(...)` değişmez!** |
| `Map<K, V> m` | `m.size()` *(metot)* | `m.get(k)` | Anahtar yoksa `null` döner (`KeyError` atmaz!) |

```java
import java.util.*;

Map<String, Integer> sayac = new HashMap<>();
sayac.put("web01", 3);
int mevcut = sayac.getOrDefault("db01", 0);        #! anahtar yoksa null yerine 0 döndürür
sayac.put("db01", mevcut + 1);
```

> [!TUZAK] `List.of(...)` ve `Map.of(...)` üzerinde değişiklik yapmak
> Java 9+ ile gelen `List.of("a", "b")` ve `Map.of("k", "v")` **değişmez (unmodifiable)** koleksiyonlar üretir. Üzerlerinde `.add(...)` veya `.put(...)` çağrılırsa çalışma zamanında `UnsupportedOperationException` fırlatılır. Ayrıca `List.of` ve `Map.of` içine `null` eleman veya `null` anahtar/değer konulamaz (`NullPointerException` atar).
:::

::: anlat Kutulama (Autoboxing) ve `Integer` önbellek tuzağı
Java koleksiyonları (`List<Integer>`, `Map<String, Integer>`) ilkel türleri (`int`) doğrudan tutamaz; onları nesne karşılıklarına (`Integer`, `Long`, `Boolean`) otomatik sarar (**autoboxing**).

İki `Integer` nesnesi `==` ile karşılaştırıldığında Java **referans (adres)** karşılaştırması yapar! JVM, yalnızca **`-128` ile `127`** arasındaki `Integer` nesnelerini önbellekte (cache) tutar:

```java
Integer a = 127;
Integer b = 127;
System.out.println(a == b);        #! true  (-128..127 aralığı aynı önbellek nesnesini paylaşır)

Integer x = 128;
Integer y = 128;
System.out.println(x == y);        #! false (128 için iki ayrı Integer nesnesi üretilir!)
System.out.println(x.equals(y));   #! true  (değer karşılaştırması)
```

> [!DERİN] `Integer` ile `int` karşılaştırılırsa ne olur?
> Taraflardan biri ilkel `int` ise (`x == 128`), Java diğer tarafı otomatik kutudan çıkarır (**unboxing**: `x.intValue() == 128`) ve değer karşılaştırması yapar. Ancak `x` o sırada `null` ise `x == 128` ifadesi `false` dönmek yerine **`NullPointerException`** fırlatır!
:::

::: tahmin
Java 21 ile çalıştırıldığında bu sınıf ne yazdırır?

```java
import java.util.*;

public class Ornek {
    public static void main(String[] args) {
        Map<String, Integer> kota = new HashMap<>();
        kota.put("temel", 100);
        kota.put("kurumsal", 500);

        Integer a = kota.get("temel");
        Integer b = 100;
        Integer c = kota.get("kurumsal");
        Integer d = 500;

        System.out.println(a == b);
        System.out.println(c == d);
        System.out.println(c.equals(d));
        System.out.println(kota.getOrDefault("misafir", 25));
    }
}
```

```gercek
true
false
true
25
```

???

`true`, `false`, `true`, `25`. `100` değeri `-128..127` `Integer` önbellek aralığında olduğu için `a` ve `b` aynı nesnedir (`a == b` → `true`). `500` ise önbellek aralığının dışındadır; `c == d` referans karşılaştırması `false`, `c.equals(d)` değer karşılaştırması `true` verir. `"misafir"` anahtarı haritada bulunmadığı için `getOrDefault` varsayılan `25` değerini döndürür.
:::

::: gorev İstek parametre birleştirici
Aşağıdaki Java metodunun davranışını Python'da `parametre_ozeti(varsayilanlar, gelen_ciftler)` fonksiyonu olarak kur. `putIfAbsent` ve `getOrDefault` davranışlarına dikkat et.

```java
public static Map<String, String> parametreOzeti(
        Map<String, String> varsayilanlar,
        List<String> gelenCiftler) {
    Map<String, String> sonuc = new LinkedHashMap<>();
    for (String cift : gelenCiftler) {
        int esit = cift.indexOf('=');
        if (esit <= 0) {
            continue;
        }
        String anahtar = cift.substring(0, esit).trim();
        String deger = cift.substring(esit + 1).trim();
        if (!anahtar.isEmpty()) {
            sonuc.putIfAbsent(anahtar, deger);   // yalnızca ilk gelen değeri korur!
        }
    }
    for (Map.Entry<String, String> e : varsayilanlar.entrySet()) {
        sonuc.putIfAbsent(e.getKey(), e.getValue());
    }
    return sonuc;
}
```

```starter
def parametre_ozeti(varsayilanlar, gelen_ciftler):
    sonuc = dict(varsayilanlar)
    for cift in gelen_ciftler:
        if "=" in cift:
            k, v = cift.split("=", 1)
            sonuc[k.strip()] = v.strip()
    return sonuc
```

```test
need("parametre_ozeti")
eq(parametre_ozeti({"sayfa": "1", "boyut": "20"}, ["sayfa=2", "sayfa=9", "sira=ad"]),
   {"sayfa": "2", "sira": "ad", "boyut": "20"},
   "putIfAbsent aynı anahtarın İLK değerini (sayfa=2) korumalı")
eq(parametre_ozeti({"sayfa": "1"}, ["=deger", "etiketsiz", "  =boş", "filtre="]),
   {"filtre": "", "sayfa": "1"},
   "esit <= 0 veya boş anahtar atlanmalı, boş değer ('filtre=') kabul edilmeli")
```

```solution
def parametre_ozeti(varsayilanlar, gelen_ciftler):
    sonuc = {}
    for cift in gelen_ciftler:
        if "=" not in cift:
            continue
        ham_anahtar, ham_deger = cift.split("=", 1)
        anahtar = ham_anahtar.strip()
        deger = ham_deger.strip()
        if anahtar and anahtar not in sonuc:
            sonuc[anahtar] = deger
    for k, v in varsayilanlar.items():
        if k not in sonuc:
            sonuc[k] = v
    return sonuc
```

```hint
Java'daki `sonuc.putIfAbsent(k, v)` anahtar sözlükte zaten varsa üzerine **yazmaz** (Python'da `sonuc.setdefault(k, v)` veya `if k not in sonuc:`). Ayrıca `esit <= 0` koşulu `=` işareti olmayan (`-1`) ve `=` ile başlayan (`0`) satırları atlar.
```
:::

::: gorev Kusurlu `Integer ==` karşılaştırmasını simüle et
Aşağıdaki Java metodu iki `Integer` nesnesini `.equals()` yerine `==` ile karşılaştırdığı için `-128..127` önbellek aralığı dışında yanlış sonuç üretiyor. Bu Java metodunun davranışını Python'da `kusurlu_esit_mi(a, b)` olarak birebir simüle et (`None` / `null` durumu dahil).

```java
public static boolean kusurluEsitMi(Integer a, Integer b) {
    if (a == null || b == null) {
        return false;
    }
    return a == b;   // KUSUR: .equals() yerine == kullanılmış!
}
```

```starter
def kusurlu_esit_mi(a, b):
    return a == b
```

```test
need("kusurlu_esit_mi")
eq(kusurlu_esit_mi(127, 127), True, "üst sınır 127 önbellekte -> True")
eq(kusurlu_esit_mi(128, 128), False, "128 önbellek dışında -> False")
eq(kusurlu_esit_mi(-128, -128), True, "alt sınır -128 önbellekte -> True")
eq(kusurlu_esit_mi(-129, -129), False, "-129 önbellek dışında -> False")
eq(kusurlu_esit_mi(10, 20), False, "farklı sayılar -> False")
eq(kusurlu_esit_mi(None, None), False, "ikisi de null olduğunda ilk if bloğu false döndürür")
eq(kusurlu_esit_mi(0, None), False, "biri null ise false")
```

```solution
def kusurlu_esit_mi(a, b):
    return a is not None and a == b and -128 <= a <= 127
```

```hint
İki kutulanmış `Integer` nesnesi `a == b` ile karşılaştırıldığında yalnızca değerleri eşitse **ve** `-128 <= a <= 127` aralığındaysa `True` döner.
```
:::
