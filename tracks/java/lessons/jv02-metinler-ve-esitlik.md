---
id: jv02
title: Metinler · String, == ve equals
summary: String değişmezliği, == referans karşılaştırması ile .equals() içerik karşılaştırması farkı, substring, indexOf ve regex tabanlı split().
---

::: anlat `==` adresi, `.equals()` içeriği karşılaştırır
Java kodunu okurken yapılacak en büyük hata, `a == b` ifadesini Python'daki gibi metin içeriği karşılaştırması sanmaktır. Java'da `String` bir nesnedir (referans türüdür):
- **`a == b`**: İki değişkenin bellekte **aynı nesneyi (adresi)** gösterip göstermediğine bakar.
- **`a.equals(b)`**: İki metnin **karakterlerinin aynı** olup olmadığına bakar.

Derleyici sabit metinleri (`"admin"`) ortak bir **String havuzuna (String Pool)** koyduğu için `"admin" == "admin"` tesadüfen `true` verir. Ancak HTTP isteğinden, veritabanından veya `.substring()` / `.trim()` çağrısından gelen metin bellekte yeni bir nesnedir ve `==` ile karşılaştırıldığında **`false`** döner!

```java
String sabit = "admin";
String gelen = "  admin ".trim();               #! çalışma zamanında yeni bir String nesnesi üretir

System.out.println(sabit == "admin");           #! true  (ikisi de String havuzundaki aynı sabit)
System.out.println(sabit == gelen);             #! false (farklı nesne referansları!)
System.out.println(sabit.equals(gelen));        #! true  (karakter içerikleri aynı)
System.out.println(sabit.equalsIgnoreCase("ADMIN")); #! true
```

> [!TUZAK] `if (rol != "misafir")` ile yazılmış yetki kontrolleri
> Bir Java web uygulamasında `if (istekRolu == "admin")` görürsen o dalın dışarıdan gelen parametreyle neredeyse hiç çalışmayacağını; tersine `if (istekRolu != "misafir")` görürsen `"misafir"` gönderilse bile referanslar farklı olduğu için koşulun her zaman `true` çıkacağını hemen fark etmelisin.
:::

::: anlat Sık kullanılan `String` metotları ve `split` sürprizi
Java `String` nesneleri **değişmezdir (immutable)**: `s.replace(...)` veya `s.trim()` orijinal metni değiştirmez, yeni bir `String` döndürür.

| Metot | Davranışı |
|---|---|
| `s.length()` | karakter sayısı (dikkat: parantezli metottur) |
| `s.substring(bas, son)` | `bas` dahil, `son` hariç dilim (`s[bas:son]`) |
| `s.indexOf("x")` | ilk konum; bulamazsa **`-1`** döner |
| `s.startsWith("x")` / `endsWith("x")` | önek / sonek kontrolü |
| `s.trim()` / `s.strip()` | kenar boşluklarını temizler |
| `s.split(regex)` | **düzenli ifadeye (regex)** göre böler ve sondaki boş parçaları atar |
| `s.split(regex, limit)` | `limit = -1` verilirse sondaki boş parçaları korur |

```java
String dosya = "rapor.2026.pdf";
String[] yanlis = dosya.split(".");             #! "." regex'te "her karakter" demektir -> boş dizi!
String[] dogru  = dosya.split("\\.");           #! ["rapor", "2026", "pdf"]
```

> [!DERİN] `split(",")` ile `split(",", -1)` farkı
> `"a,b,,".split(",")` çağrısı sondaki boş alanları sessizce atar ve 2 elemanlı `["a", "b"]` döndürür. CSV veya başlık ayrıştırırken sondaki boş sütunların korunması için ikinci argüman olarak `-1` (`split(",", -1)`) kullanılır.
:::

::: tahmin
Java 21 ile çalıştırıldığında bu sınıf ne yazdırır?

```java
public class Ornek {
    public static void main(String[] args) {
        String yol = "/api/v1/biletler/";
        String kopya = yol.substring(0, 7);
        System.out.println(kopya);
        System.out.println(kopya == "/api/v1");
        System.out.println(kopya.equals("/api/v1"));
        System.out.println(yol.split("/").length);
        System.out.println(yol.split("/", -1).length);
    }
}
```

```gercek
/api/v1
false
true
4
5
```

???

`/api/v1`, `false`, `true`, `4`, `5`. `substring(0, 7)` yeni bir `String` nesnesi döndürdüğü için `== "/api/v1"` referans karşılaştırması `false`, `.equals("/api/v1")` içerik karşılaştırması `true` verir. `"/api/v1/biletler/"` metninde `split("/")` sondaki boş parçayı atıp `["", "api", "v1", "biletler"]` (`4` eleman) üretirken, `split("/", -1)` sondaki boş parçayı da koruyarak `5` eleman üretir.
:::

::: gorev Bearer jetonu ayıklayıcı
Aşağıdaki Java metodunun davranışını Python'da `bearer_cikar(baslik)` fonksiyonu olarak kur.

```java
public static String bearerCikar(String baslik) {
    if (baslik == null) {
        return null;
    }
    String temiz = baslik.trim();
    if (temiz.length() <= 7) {
        return null;
    }
    String onek = temiz.substring(0, 7);
    if (!onek.equalsIgnoreCase("Bearer ")) {
        return null;
    }
    String jeton = temiz.substring(7).trim();
    if (jeton.isEmpty() || jeton.indexOf(' ') != -1) {
        return null;
    }
    return jeton;
}
```

```starter
def bearer_cikar(baslik):
    if not baslik:
        return None
    return baslik.replace("Bearer ", "").strip()
```

```test
need("bearer_cikar")
eq(bearer_cikar("Bearer tk_9981"), "tk_9981", "standart Bearer başlığı")
eq(bearer_cikar("  bearer   abc.def.ghi  "), "abc.def.ghi", "büyük-küçük harf duyarsız önek ve kenar boşlukları")
eq(bearer_cikar("Bearer "), None, "sınır: yalnızca önek ve boşluk -> None")
eq(bearer_cikar("BearerX"), None, "sınır: uzunluk 7 ama boşluksuz -> None")
eq(bearer_cikar("Bearer x"), "x", "sınır: uzunluk 8 -> 'x'")
eq(bearer_cikar("Bearer    "), None, "yalnızca boşluk içeren jeton -> None")
eq(bearer_cikar("Bearer a b"), None, "içinde boşluk geçen jeton reddedilmeli")
eq(bearer_cikar("Basic dXNlcjpwYXNz"), None, "farklı şema -> None")
eq(bearer_cikar(None), None, "null girdi -> None")
```

```solution
def bearer_cikar(baslik):
    if baslik is None:
        return None
    temiz = baslik.strip()
    if temiz[:7].lower() != "bearer ":
        return None
    jeton = temiz[7:].strip()
    if " " in jeton:
        return None
    return jeton
```

```hint
`temiz = baslik.strip()` sonrasında `len(temiz) <= 7` kontrolü, `temiz[:7].lower() != "bearer "` kontrolü ve `jeton = temiz[7:].strip()` içinde boşluk (`" " in jeton`) kontrolünü sırasıyla uygula.
```
:::

::: gorev Dosya uzantısı denetimi (`split` davranışı)
Aşağıdaki Java metodunun ne döndürdüğünü birebir hesaplayan `uzanti_kontrol(dosya_adi)` fonksiyonunu Python'da yaz.

```java
public static String uzantiKontrol(String dosyaAdi) {
    if (dosyaAdi == null || dosyaAdi.indexOf('/') != -1 || dosyaAdi.indexOf('\\') != -1) {
        return "REDDEDILDI";
    }
    String[] parcalar = dosyaAdi.split("\\.", -1);
    if (parcalar.length < 2) {
        return "UZANTISIZ";
    }
    String ilk = parcalar[0];
    String son = parcalar[parcalar.length - 1].toLowerCase();
    if (ilk.isEmpty() || son.isEmpty()) {
        return "GECERSIZ";
    }
    if (son.equals("png") || son.equals("jpg") || son.equals("pdf")) {
        return "KABUL:" + son;
    }
    return "YASAK:" + son;
}
```

```starter
def uzanti_kontrol(dosya_adi):
    return "KABUL:pdf"
```

```test
need("uzanti_kontrol")
eq(uzanti_kontrol("fatura_2026.PDF"), "KABUL:pdf", "büyük harfli PDF kabul edilmeli")
eq(uzanti_kontrol("arsiv.tar.gz"), "YASAK:gz", "son parça gz yasak")
eq(uzanti_kontrol("README"), "UZANTISIZ", "nokta yoksa parcalar.length == 1 -> UZANTISIZ")
eq(uzanti_kontrol(".env"), "GECERSIZ", "başta nokta varsa ilk parça boş -> GECERSIZ")
eq(uzanti_kontrol("rapor."), "GECERSIZ", "sonda nokta varsa split(-1) ile son parça boş -> GECERSIZ")
eq(uzanti_kontrol("../rapor.pdf"), "REDDEDILDI", "/ içeren yol reddedilmeli")
eq(uzanti_kontrol("alt\\rapor.png"), "REDDEDILDI", "ters eğik çizgi içeren yol reddedilmeli")
eq(uzanti_kontrol(None), "REDDEDILDI", "None -> REDDEDILDI")
```

```solution
def uzanti_kontrol(dosya_adi):
    if dosya_adi is None or "/" in dosya_adi or "\\" in dosya_adi:
        return "REDDEDILDI"
    parcalar = dosya_adi.split(".")
    if len(parcalar) < 2:
        return "UZANTISIZ"
    ilk = parcalar[0]
    son = parcalar[-1].lower()
    if not ilk or not son:
        return "GECERSIZ"
    if son in ("png", "jpg", "pdf"):
        return "KABUL:" + son
    return "YASAK:" + son
```

```hint
Java'daki `dosyaAdi.split("\\.", -1)` çağrısı, Python'daki `dosya_adi.split(".")` ile birebir aynı sonucu üretir (başta veya sonda nokta varsa boş metin `""` bırakır).
```
:::
