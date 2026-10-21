---
id: jv01
title: Bir Java Sınıfı ve İlkel Türler
summary: package, import, class ve main yapısı; int/long/double/boolean ilkel türleri, tam sayı bölmesi, 32-bit taşma ve + işlecinin soldan sağa davranışı.
---

::: anlat Her şey bir sınıfın içinde yaşar
Java'da boşta duran fonksiyon yoktur; her metot ve her sabit bir `class` (sınıf) gövdesinin içinde tanımlanır. Bir web uygulamasının kaynak kodunu açtığında dosyanın en üstünde hangi pakete ait olduğunu söyleyen `package` satırını ve kullanılan kütüphaneleri bildiren `import` satırlarını görürsün. Bu yolda Java 21 kodunu okuyacak, çıktısını tahmin edecek ve görevlerde aynı davranışı Python'da kuracaksın.

```java
package tr.pafta.web;

import java.time.Instant;

public class DurumDenetleyici {
    public static final int VARSAYILAN_PORT = 8080;   #! sabit (final): değeri sonradan değiştirilemez

    public static String durumSatiri(String sunucu, int aktifIstek) {
        return sunucu + " :" + VARSAYILAN_PORT + " -> " + aktifIstek;
    }

    public static void main(String[] args) {          #! programın giriş noktası
        System.out.println(durumSatiri("web01", 42));
    }
}
```

### İlkel (Primitive) Türler
Java statik tür sistemine sahiptir; her değişkenin türü derleme zamanında bellidir:

| Tür | Boyut | Aralık / Özellik |
|---|---|---|
| `byte` | 8-bit işaretli | `-128` .. `127` |
| `short` | 16-bit işaretli | `-32_768` .. `32_767` |
| `int` | 32-bit işaretli | `-2_147_483_648` .. `2_147_483_647` (`Integer.MAX_VALUE`) |
| `long` | 64-bit işaretli | sayı sabitinin sonuna `L` konur (`3_000_000_000L`) |
| `double` | 64-bit kayan nokta | ondalıklı sayıların varsayılan türü (`3.5`) |
| `boolean` | mantıksal | yalnızca `true` veya `false` (`0` ya da `1` boolean **değildir**) |
| `char` | 16-bit UTF-16 | tek tırnakla yazılır (`'A'`, sayısal değeri `65`) |

> [!TUZAK] Java'da `if (sayac)` derlenmez
> C, PHP ve Python'dan farklı olarak Java'da `if` ve `while` parantezinin içi **kesinlikle `boolean`** olmalıdır. `if (sayac != 0)` veya `if (metin != null)` şeklinde açık karşılaştırma yazılır.
:::

::: anlat Tam sayı bölmesi, taşma ve `+` birleştirmesi
İki `int` birbirine bölündüğünde sonuç her zaman **sıfıra doğru kırpılan** bir `int` olur: `7 / 2` sonucu `3`, `-7 / 2` sonucu `-3`'tür.

`+` işleci soldan sağa değerlendirilir:
- İki taraf da sayıysa **toplar** (`char` da aritmetikte tam sayı koduna dönüşür: `'A' + 1` → `66`).
- Taraflardan biri `String` olduğu anda geri kalanları metne çevirip **birleştirir**:

```java
System.out.println("HTTP " + 2 + 0 + 0);   #! "HTTP 200": önce "HTTP 2", sonra "HTTP 20", sonra "HTTP 200"
System.out.println(2 + 0 + "0 HTTP");      #! "20 HTTP": önce 2 + 0 = 2 toplanır, sonra "0 HTTP" eklenir
System.out.println(7 / 2 + " ve " + 7 / 2.0); #! "3 ve 3.5"
```

> [!DERİN] 32-bit `int` taşması sessizdir
> Python tam sayıları sınırsız büyürken, Java'da `int` 32-bit ikinin tümleyeni (two's complement) aritmetiğiyle sarar: `Integer.MAX_VALUE + 1` hata vermez, `-2147483648` (`Integer.MIN_VALUE`) olur! Bir web uygulamasında dosya boyutu veya kota hesabı `long` yerine `int` ile yapılmışsa `2 GB` (`2_147_483_647` bayt) sınırı aşıldığında boyut negatif görünüp boyut kontrolünü (`boyut <= maksimum`) yanıltabilir.
:::

::: tahmin
Java 21 ile çalıştırıldığında bu sınıf ne yazdırır?

```java
public class Ornek {
    public static void main(String[] args) {
        int istek = 7;
        int grup = 2;
        System.out.println(istek / grup);
        System.out.println("Sayfa: " + istek + grup);
        System.out.println(istek + grup + ". sayfa");
        int sinir = 2_000_000_000;
        System.out.println(sinir + sinir < 0);
    }
}
```

```gercek
3
Sayfa: 72
9. sayfa
true
```

???

`3`, `Sayfa: 72`, `9. sayfa`, `true`. `7 / 2` tam sayı bölmesidir ve `3` verir. `"Sayfa: " + istek + grup` soldan sağa metin birleştirdiği için `"Sayfa: 72"` olur; `istek + grup + ". sayfa"` ise önce `7 + 2 = 9` toplamasını yapıp `"9. sayfa"` üretir. `2_000_000_000 + 2_000_000_000` toplamı 32-bit `int` üst sınırını (`2_147_483_647`) aştığı için negatif bölgeye taşar (`-294967296`), dolayısıyla `< 0` karşılaştırması `true` döner.
:::

::: gorev Sayfalama özeti
Aşağıdaki Java metodunun davranışını Python'da `sayfa_ozeti(toplam_kayit, sayfa_boyutu, aktif_sayfa)` fonksiyonu olarak kur. Java'daki tam sayı bölmesi ve `+` birleştirme sırasına dikkat et.

```java
public static String sayfaOzeti(int toplamKayit, int sayfaBoyutu, int aktifSayfa) {
    if (sayfaBoyutu <= 0 || toplamKayit < 0) {
        return "GECERSIZ";
    }
    int toplamSayfa = (toplamKayit + sayfaBoyutu - 1) / sayfaBoyutu;
    if (toplamSayfa == 0) {
        toplamSayfa = 1;
    }
    boolean gecerli = aktifSayfa >= 1 && aktifSayfa <= toplamSayfa;
    return "Sayfa " + aktifSayfa + "/" + toplamSayfa + " (gecerli=" + gecerli + ")";
}
```

```starter
def sayfa_ozeti(toplam_kayit, sayfa_boyutu, aktif_sayfa):
    return f"Sayfa {aktif_sayfa}/1 (gecerli=True)"
```

```test
need("sayfa_ozeti")
eq(sayfa_ozeti(25, 10, 1), "Sayfa 1/3 (gecerli=true)", "25 kayıt, 10'luk sayfada 3 sayfa eder")
eq(sayfa_ozeti(20, 10, 2), "Sayfa 2/2 (gecerli=true)", "tam bölünen sınır: 20 kayıt -> 2 sayfa, 2. sayfa geçerli")
eq(sayfa_ozeti(20, 10, 3), "Sayfa 3/2 (gecerli=false)", "üst sınır dışı: 3. sayfa geçersiz")
eq(sayfa_ozeti(20, 10, 0), "Sayfa 0/2 (gecerli=false)", "alt sınır dışı: 0. sayfa geçersiz")
eq(sayfa_ozeti(0, 10, 1), "Sayfa 1/1 (gecerli=true)", "0 kayıtta toplamSayfa 1'e sabitlenir")
eq(sayfa_ozeti(10, 0, 1), "GECERSIZ", "sayfaBoyutu 0 ise GECERSIZ")
eq(sayfa_ozeti(-1, 10, 1), "GECERSIZ", "negatif toplamKayit GECERSIZ")
```

```solution
def sayfa_ozeti(toplam_kayit, sayfa_boyutu, aktif_sayfa):
    if sayfa_boyutu <= 0 or toplam_kayit < 0:
        return "GECERSIZ"
    toplam_sayfa = (toplam_kayit + sayfa_boyutu - 1) // sayfa_boyutu
    if toplam_sayfa == 0:
        toplam_sayfa = 1
    gecerli = 1 <= aktif_sayfa <= toplam_sayfa
    durum = "true" if gecerli else "false"
    return f"Sayfa {aktif_sayfa}/{toplam_sayfa} (gecerli={durum})"
```

```hint
Java'da `boolean` metne çevrilirken küçük harfle `"true"` veya `"false"` yazar. Pozitif sayılarda tam sayı bölmesi Python'da `//` ile aynıdır.
```
:::

::: gorev 32-bit kota hesabı
Aşağıdaki Java metodunda kota kontrolü `long` yerine 32-bit işaretli `int` ile yazıldığı için taşma (overflow) davranışı içeriyor. Aynı 32-bit `int` davranışını Python'da `kota_kontrol(mevcut_bayt, eklenen_bayt, sinir_bayt)` fonksiyonu olarak kur ve `(yeni_toplam_int32, kabul_edildi_mi)` demetini döndür.

```java
public static boolean kotaKontrol(int mevcutBayt, int eklenenBayt, int sinirBayt) {
    if (eklenenBayt <= 0) {
        return false;
    }
    int yeniToplam = mevcutBayt + eklenenBayt;   // 32-bit işaretli toplama!
    return yeniToplam <= sinirBayt;
}
```

```starter
def int32(n):
    n = n & 0xFFFFFFFF
    return n - 0x100000000 if n >= 0x80000000 else n

def kota_kontrol(mevcut_bayt, eklenen_bayt, sinir_bayt):
    toplam = mevcut_bayt + eklenen_bayt
    return toplam, toplam <= sinir_bayt
```

```test
need("kota_kontrol")
eq(kota_kontrol(500, 500, 1000), (1000, True), "tam sınırda (1000 <= 1000) kabul edilmeli")
eq(kota_kontrol(500, 501, 1000), (1001, False), "sınırın 1 üstü reddedilmeli")
eq(kota_kontrol(500, 0, 1000), (500, False), "eklenen 0 ise false dönmeli")
eq(kota_kontrol(500, -10, 1000), (490, False), "negatif eklenen false dönmeli")
eq(kota_kontrol(2_000_000_000, 200_000_000, 1_000_000_000), (-2_094_967_296, True), "32-bit taşma sonucu negatif olur ve <= sinirBayt kontrolünü geçer")
eq(kota_kontrol(2_147_483_647, 1, 1000), (-2_147_483_648, True), "Integer.MAX_VALUE + 1 tam -2147483648 (Integer.MIN_VALUE) sınırına sarar")
```

```solution
def int32(n):
    n = n & 0xFFFFFFFF
    return n - 0x100000000 if n >= 0x80000000 else n

def kota_kontrol(mevcut_bayt, eklenen_bayt, sinir_bayt):
    yeni_toplam = int32(mevcut_bayt + eklenen_bayt)
    if eklenen_bayt <= 0:
        return yeni_toplam, False
    return yeni_toplam, yeni_toplam <= sinir_bayt
```

```hint
Hazır verilen `int32(mevcut_bayt + eklenen_bayt)` fonksiyonuyla 32-bit toplamı hesapla; `eklenen_bayt <= 0` ise `(yeni_toplam, False)`, değilse `(yeni_toplam, yeni_toplam <= sinir_bayt)` döndür.
```
:::
