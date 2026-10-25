---
id: jv14
title: Serialization · Nesne Grafiği, Geri Çağırmalar ve Filtre Sınırları
summary: Java deserialization nesneyi sınıfın kurucusunu çağırmadan kurar — ama Serializable olmayan ilk üst sınıfın argümansız kurucusu çalışır; readObject'in başında alanlar hâlâ varsayılan değerindedir, defaultReadObject'ten sonra dolar, en sonda readResolve dönen nesneyi değiştirebilir. ObjectInputFilter desenleri sınıf kalıpları ve maxdepth/maxarray gibi sınırlar taşır; sınır değeri dahildir, aşılınca InvalidClassException (REJECTED) gelir ve ilk eşleşen kalıp kararı verir.
---

::: anlat Kurucu çalışmadan kurulan nesne
`JV11`'de yansımayı ve JSON bağlamayı okudun; orada geçen uyarıyı burada somutlaştıracağız. Java'nın yerleşik serileştirmesi bir nesne **grafiğini** baytlara çevirir ve geri okur. Geri okuma sıradan bir nesne yaratma değildir:

- Sınıfın kendi kurucusu **çağrılmaz**. Nesne doğrudan üretilir, alanları akıştan yazılır.
- Buna karşılık, `Serializable` **olmayan** ilk üst sınıfın argümansız kurucusu **çağrılır**.
- Sınıf `readObject`, `readResolve` gibi özel yöntemler tanımlamışsa bunlar belirli bir sırada çalışır.

Bu derste ölçüldü (Kali, OpenJDK **25.0.4**):

| Aşama | Çalışan |
|---|---|
| Yazarken | `Ust()` → `Kayit(String,int)` → `writeObject` |
| Okurken | `Ust()` → `readObject` → *(defaultReadObject)* → `readResolve` |

Okuma sırasında `Kayit`'in kendi kurucusu listede **yok**; `Ust()` ise var. Sınıfın "geçerli bir nesne ancak kurucudan çıkar" varsayımı burada tutmaz: doğrulamayı kurucuya koyduysan deserialization onu atlar.

`readResolve` en sonda çalışır ve **dönen nesneyi değiştirebilir**; tekil (singleton) sınıflar bunu kendi örneklerini korumak için kullanır. Yani `readObject` ile elde edilen nesne, çağırana giden nesne olmayabilir.
:::

::: anlat Filtre: ne kurulabilir, ne kadar derin
Java 9'dan beri `ObjectInputFilter` ile bir akışın neyi kurabileceğini sınırlayabilirsin. Desen, `;` ile ayrılmış parçalardan oluşur ve iki tür parça taşır:

| Parça | Anlamı |
|---|---|
| `maxdepth=N` | grafiğin en çok `N` derinliği |
| `maxarray=N` | en çok `N` elemanlı dizi |
| `maxrefs=N`, `maxbytes=N` | başvuru ve bayt üst sınırı |
| `Sinif` | bu sınıfa **izin ver** |
| `!Sinif` | bu sınıfı **reddet** |
| `*` | her şeyle eşleşen joker |

Ölçülen davranışlar (derinliği 3 olan bir bağlı yapı ve 5 elemanlı bir `int[]` üzerinde):

```text
(filtre yok)     -> OK
maxdepth=2;*     -> InvalidClassException (REJECTED)
maxdepth=3;*     -> OK
maxarray=4;*     -> InvalidClassException (REJECTED)
maxarray=5;*     -> OK
!Dugum;*         -> InvalidClassException (REJECTED)
Dugum;!*         -> OK
```

İki şey buradan okunur. Birincisi **sınır değeri dahildir**: `maxdepth=3`, derinliği tam 3 olan grafiği kabul eder; reddeden `maxdepth=2`'dir. Bir eşik ayarlarken "3'e kadar" ile "3 hariç" arasındaki farkı tahmin etmek yerine komşu değeri denemek gerekir.

İkincisi **ilk eşleşen kalıp karar verir**. `!Dugum;*` önce reddi görür ve reddeder; `Dugum;!*` önce izni görür ve kabul eder. Aynı iki kalıbın sırası değişince sonuç değişir. Hiçbir kalıp eşleşmezse karar "kararsız"dır ve başka bir filtre yoksa nesne kabul edilir.

Reddedilen akış sessizce boş dönmez: `InvalidClassException` fırlatılır ve iletisinde `REJECTED` geçer.

> [!TUZAK] Filtre, güvenilmeyen veriyi güvenli yapmaz
> Bir izin listesi, kurulabilecek sınıf kümesini daraltır — bu gerçek bir kazançtır. Ama akışı hâlâ karşı taraf yazıyor: izin verdiğin sınıfların alanları onun seçtiği değerlerle doluyor ve o sınıfların `readObject`/`readResolve`/`finalize` yöntemleri çalışıyor. Oracle'ın kendi rehberi de birincil öneri olarak filtreyi değil, **güvenilmeyen veriyi Java serileştirmesiyle hiç okumamayı** söyler. Yeni kodda veri biçimi olarak nesne kuran bir format seçme; JSON gibi yalnız veri taşıyan bir biçimde tür seçimi sende kalır.
:::

::: tahmin Hangi kurucu, hangi sırayla?
`Ust` sınıfı `Serializable` **değil**; `Kayit` ondan türüyor ve `Serializable`. Yazıp sonra okuyoruz.

```java
class Ust { Ust() { System.out.println("Ust() kurucu"); } }

class Kayit extends Ust implements Serializable {
    String ad; int sayi;
    Kayit(String ad, int sayi) { this.ad = ad; this.sayi = sayi; System.out.println("Kayit(String,int) kurucu"); }
    private void writeObject(ObjectOutputStream o) throws IOException {
        System.out.println("writeObject"); o.defaultWriteObject();
    }
    private void readObject(ObjectInputStream i) throws IOException, ClassNotFoundException {
        System.out.println("readObject basi: ad=" + ad + " sayi=" + sayi);
        i.defaultReadObject();
        System.out.println("readObject sonu: ad=" + ad + " sayi=" + sayi);
    }
    private Object readResolve() { System.out.println("readResolve"); return this; }
}
// new Kayit("web01", 7) yazilir, sonra geri okunur
```

```gercek
Ust() kurucu
Kayit(String,int) kurucu
writeObject
--- bayt: 72 ---
Ust() kurucu
readObject basi: ad=null sayi=0
readObject sonu: ad=web01 sayi=7
readResolve
sonuc: web01 7
```

???

Yazma tarafı tahmin edilebilir: nesne normal yoldan kurulur (`Ust()`, sonra `Kayit(...)`), sonra `writeObject` çalışır.

Okuma tarafında **`Kayit(String,int)` satırı yok**. Sınıfın kendi kurucusu hiç çağrılmadı; nesne doğrudan üretildi. Buna karşılık `Ust() kurucu` yazıldı: `Serializable` olmayan ilk üst sınıfın argümansız kurucusu çalışır — bu kuralın en sık şaşırtan yanıdır.

`readObject basi: ad=null sayi=0`: yöntemin başında nesne vardır ama **boştur**. Alanlar `defaultReadObject()` çağrısıyla dolar; sonraki satır `ad=web01 sayi=7` der. `readObject` içinde doğrulama yazacaksan bunu `defaultReadObject()`'ten **sonra** yapmalısın, yoksa boş değerleri denetlersin.

En son `readResolve` çalışır. Burada `this` döndürdüğü için sonuç değişmedi, ama başka bir nesne döndürseydi çağırana o giderdi.
:::

::: gorev Geri çağırma sırası
`sira(tanimlar, ustSerializable)` yaz: bir nesnenin **okunması** sırasında hangi adımların, hangi sırayla çalışacağını listele.

- `tanimlar`: sınıfın tanımladığı özel yöntemlerin kümesi (`"readObject"`, `"readResolve"`, `"writeObject"`, `"kurucu"` olabilir).
- `ustSerializable`: üst sınıf `Serializable` mı.

Kurallar (ölçüldü):

- Üst sınıf `Serializable` **değilse** listeye önce `"Ust()"` girer; `Serializable` ise girmez.
- Sınıfın kendi kurucusu okuma sırasında **hiç** çalışmaz; `"kurucu"` tanımlı olsa bile listeye girmez.
- `readObject` tanımlıysa eklenir; tanımlı değilse yerine `"defaultReadObject"` eklenir.
- `readResolve` tanımlıysa en sona eklenir.
- `writeObject` okuma sırasında çalışmaz.

```starter
def sira(tanimlar, ustSerializable):
    adimlar = []
    if "kurucu" in tanimlar:
        adimlar.append("kurucu")
    if "readObject" in tanimlar:
        adimlar.append("readObject")
    return adimlar
```

```test
need("sira")
eq(sira({"kurucu", "writeObject", "readObject", "readResolve"}, False),
   ["Ust()", "readObject", "readResolve"],
   "ölçülen durum: kendi kurucusu yok, Serializable olmayan üstünkü var")
eq(sira({"readObject"}, True), ["readObject"], "üst Serializable ise Ust() çalışmaz")
eq(sira(set(), False), ["Ust()", "defaultReadObject"], "readObject yoksa varsayılan okuma")
eq(sira(set(), True), ["defaultReadObject"], "en yalın durum")
eq(sira({"readResolve"}, True), ["defaultReadObject", "readResolve"], "readResolve en sonda")
eq(sira({"kurucu"}, True), ["defaultReadObject"], "kurucu okuma sırasında hiç çalışmaz")
eq(sira({"writeObject"}, True), ["defaultReadObject"], "writeObject yalnız yazarken çalışır")
eq(sira({"readObject", "readResolve", "writeObject", "kurucu"}, True),
   ["readObject", "readResolve"], "yazma yöntemi ve kurucu listede yok")
```

```solution
def sira(tanimlar, ustSerializable):
    adimlar = []
    if not ustSerializable:
        adimlar.append("Ust()")
    adimlar.append("readObject" if "readObject" in tanimlar else "defaultReadObject")
    if "readResolve" in tanimlar:
        adimlar.append("readResolve")
    return adimlar
```

```hint
Başlangıç kodu kurucuyu listeye koyuyor ve üst sınıfı hiç dikkate almıyor. Okuma sırasında sınıfın kendi kurucusu **asla** çalışmaz; çalışan, `Serializable` olmayan ilk üst sınıfınkidir.
```
:::

::: gorev Filtre kararını ver
`filtre(desen, sinif, derinlik, diziBoyu)` yaz: bir `ObjectInputFilter` deseninin kararını döndür.

`desen`, `;` ile ayrılmış parçalardan oluşur ve soldan sağa değerlendirilir:

- `maxdepth=N`: `derinlik` `N`'den **büyükse** `"ret"`. Sınır değeri dahildir.
- `maxarray=N`: `diziBoyu` `N`'den **büyükse** `"ret"`.
- `!Kalip`: `sinif` kalıba uyuyorsa `"ret"`.
- `Kalip`: `sinif` kalıba uyuyorsa `"izin"`.
- `*` her sınıfa uyar; diğer kalıplar tam ad eşleşmesidir.

Sınırlar her zaman önce denetlenir; sonra sınıf kalıpları sırayla bakılır ve **ilk eşleşen** karar verir. Hiçbiri eşleşmezse `"kararsiz"`.

```starter
def filtre(desen, sinif, derinlik, diziBoyu):
    for parca in desen.split(";"):
        if parca == sinif or parca == "*":
            return "izin"
    return "kararsiz"
```

```test
need("filtre")
eq(filtre("maxdepth=2;*", "Dugum", 3, 0), "ret", "ölçülen: derinlik 3, sınır 2 -> reddedilir")
eq(filtre("maxdepth=3;*", "Dugum", 3, 0), "izin", "ölçülen: sınır değeri dahildir")
eq(filtre("maxdepth=4;*", "Dugum", 3, 0), "izin", "sınırın altında")
eq(filtre("maxarray=4;*", "int[]", 1, 5), "ret", "ölçülen: 5 elemanlı dizi, sınır 4")
eq(filtre("maxarray=5;*", "int[]", 1, 5), "izin", "ölçülen: dizi sınırı da dahil")
eq(filtre("!Dugum;*", "Dugum", 1, 0), "ret", "ölçülen: önce gelen ret kazanır")
eq(filtre("Dugum;!*", "Dugum", 1, 0), "izin", "ölçülen: önce gelen izin kazanır")
eq(filtre("Dugum;!*", "Baska", 1, 0), "ret", "izinli listede olmayan sınıf !* ile reddedilir")
eq(filtre("Dugum", "Baska", 1, 0), "kararsiz", "hiçbir kalıp eşleşmedi")
eq(filtre("maxdepth=2;Dugum", "Dugum", 5, 0), "ret", "sınır kalıptan önce denetlenir")
eq(filtre("*", "Herhangi", 1, 0), "izin", "joker her sınıfa uyar")
```

```solution
def filtre(desen, sinif, derinlik, diziBoyu):
    parcalar = desen.split(";")
    for p in parcalar:
        if p.startswith("maxdepth=") and derinlik > int(p.split("=")[1]):
            return "ret"
        if p.startswith("maxarray=") and diziBoyu > int(p.split("=")[1]):
            return "ret"
    for p in parcalar:
        if p.startswith("max"):
            continue
        red = p.startswith("!")
        kalip = p[1:] if red else p
        if kalip == "*" or kalip == sinif:
            return "ret" if red else "izin"
    return "kararsiz"
```

```hint
İki geçiş yap: önce bütün sınırları denetle (biri bile aşılmışsa `"ret"`), sonra sınıf kalıplarını sırayla gez. İkinci geçişte `max...` parçalarını atla, yoksa onları sınıf adı sanarsın.
```

```hint
`!` öneki kararı tersine çevirir ama eşleşme kuralını değiştirmez: `!*` da her sınıfa uyar, yalnız sonucu `"ret"` olur. İlk eşleşen kalıpta hemen dön; sonrakilere bakma.
```
:::
