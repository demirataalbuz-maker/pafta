---
id: sq19
title: Girdi Veridir: Parametre Bağlama ve İzinli Alanlar
summary: Uygulama girdisinin SQL'e nasıl ulaştığı; metin birleştirmenin girdiyi koda çevirmesi, bağlanan parametrenin her zaman tek bir değer kalması; tırnak, NULL ve metin olarak gelen sayılar; bağlanamayan sütun adları için izinli liste; LIKE jokerlerini kaçırmak.
kazanim: 1Z0071 3.2, 1Z0071 5.2, 1Z0071 13.1, 1Z0071 13.4, 1Z0071 14.2
---

::: anlat Girdi koda karışınca
Bir web uygulaması formdan gelen değeri sorguya iki yoldan koyabilir. İlki metin birleştirmektir:

```python
ad = istek.form["ad"]                                   # kullanıcı ne yazdıysa
db.execute("SELECT id FROM personel WHERE ad = '" + ad + "'")
```

Kullanıcı `Kerem` yazarsa sorgu beklenen sorgudur. `x' OR '1'='1` yazarsa veritabanına giden metin şudur:

```sql
SELECT id FROM personel WHERE ad = 'x' OR '1'='1'
```

Girdideki tırnak, metni kapatıp yeni bir **koşul** açtı: `OR '1'='1'` her satırda doğrudur, sorgu bütün personeli verir. Veritabanı hangi parçanın uygulamadan, hangisinin kullanıcıdan geldiğini bilmez; ona yalnızca bir metin ulaşır. SQL enjeksiyonunun kökü budur.

İkinci yol **parametre bağlamaktır** (parameter binding, hazır ifade):

```python
db.execute("SELECT id FROM personel WHERE ad = ?", (ad,))
```

Burada sorgunun metni sabittir; `?` yerine değer **ayrıştırma bittikten sonra** konur. Değerin içinde ne olursa olsun (tırnak, `OR`, `;`, `--`) bütünüyle tek bir metin değeridir; asla koşul ya da komut olmaz. `x' OR '1'='1` girdisi, adı tam olarak bu dokuz karakter olan birini arar ve bulamaz.

SQL içinde aynı farkı ölçebilirsin: birleştirilmiş metindeki tırnak kodun parçası olur; tırnağı ikilenmiş (`''`) bir değişmez ise tek bir değerdir. SQLite'ın `quote(x)` fonksiyonu bir değeri güvenli bir SQL değişmezi olarak yazar; bağlanan bir parametrenin veritabanı için anlamı tam olarak budur:

| İfade | Sonuç |
|---|---|
| `quote('O''Brien')` | `'O''Brien'` |
| `quote(NULL)` | `NULL` |
| `quote(5)` | `5` |
| `quote('5')` | `'5'` |

> [!GÜVENLİK]
> Tırnakları elle ikilemek (`replace(ad, '''', '''''')`) bağlamanın yerini tutmaz: sayı alanlarında tırnak bile yoktur (`WHERE id = 1 OR 1=1`), karakter kümesi ve sürücü farkları atlatma yolu açar. Kural: **değerler bağlanır, hiçbir zaman birleştirilmez.** (OWASP SQL Injection Prevention Cheat Sheet, 1. savunma: parametreli sorgular.)
:::

::: anlat Bağlanan değer neye dönüşür
Bağlama girdiyi zararsız yapar ama değerin **türünü** uygulama belirler. HTTP formundan gelen her şey metindir: kullanıcı `72` yazsa da sürücüye `'72'` metni gider. Bu derste uygulamanın gönderdiği değerler `istek(ad, deger)` adlı bir tabloda durur; sorgun değeri `(SELECT deger FROM istek WHERE ad = 'esik')` ile okur. Bu, bağlanmış bir `?` ile aynı şeydir: değer sorguya veri olarak girer, metni koda dönüşmez.

SQLite'ta karşılaştırmanın sonucu sütunun **tür eğilimine** (affinity) bağlıdır. `sunucular.cpu` sütunu `INTEGER`'dır; böyle bir sütun türsüz ya da metin bir değerle karşılaştırılınca SQLite önce değeri sayıya çevirmeyi dener:

| Gelen `esik` | `cpu >= esik` olan sunucu sayısı | Neden |
|---|---|---|
| `'72'` | 3 | sayıya çevrilir; 72 eşiğe eşit, dahil |
| `'73'` | 2 | 72 artık dışarıda |
| `'50.5'` | 5 | ondalık da çevrilir |
| `'abc'` | 0 | sayıya benzemez, metin kalır; SQLite'ta her sayı her metinden küçüktür |
| `''` | 0 | boş metin de metin kalır |
| `NULL` | 0 | `cpu >= NULL` bilinmez, hiçbir satır geçmez |

Bu kural yalnızca sütun doğrudan karşılaştırılınca işler. `cpu + 0 >= '50'` gibi bir ifadenin tür eğilimi yoktur: sayı metinle karşılaştırılır ve sonuç her satırda yanlıştır.

Tuzak `CAST`'tadır: `CAST('abc' AS INTEGER)` ve `CAST('' AS INTEGER)` hata vermez, **0** döner; `CAST('12abc' AS INTEGER)` ise 12. Bozuk bir eşik böylece "0'dan büyük olan her şey" anlamına gelir ve bütün satırlar döner. Girdiyi çevirmeden önce sayı olduğunu doğrula ya da tür eğiliminin işini yapmasına izin ver.

`NULL` da ayrı düşünülür: kullanıcı alanı boş bıraktığında uygulamanın `NULL` mu `''` mı gönderdiği sonucu değiştirir. `WHERE ad = ?` sorgusuna `NULL` bağlanırsa satır gelmez (`= NULL` bilinmezdir); "değeri olmayanları bul" denmek isteniyorsa `IS ?` gerekir.
:::

::: anlat Bağlanamayan yerler: izinli liste
Yalnızca **değerler** bağlanabilir. Tablo adı, sütun adı, `ORDER BY` alanı ve `ASC`/`DESC` sorgunun yapısıdır; `ORDER BY ?` yazıp `'cpu'` bağlarsan SQLite sabit bir metne göre sıralar, yani hiç sıralamaz. Uygulamalar bu yüzden "sırala=cpu" gibi bir girdiyi sorgu metnine eklemeye kalkar; enjeksiyonun en sık kalan kapısı burasıdır.

Doğru çözüm **izinli listedir** (allowlist): girdi, önceden yazılmış sabit seçeneklerden biriyle karşılaştırılır ve sorguya kullanıcının metni değil, seçilen sabit sütun girer. Listede olmayan her şey varsayılana düşer:

```sql
CREATE TABLE istek (ad TEXT PRIMARY KEY, deger);
INSERT INTO istek (ad, deger) VALUES ('sirala', 'cpu');

SELECT id, ad FROM sunucular
ORDER BY CASE (SELECT deger FROM istek WHERE ad = 'sirala')
           WHEN 'ad'  THEN ad
           WHEN 'cpu' THEN cpu
         END,
         id;
```

Girdi `ad` ya da `cpu` değilse `CASE` her satırda `NULL` verir, eşitlik `id` ile bozulur: varsayılan sıra. `cpu DESC`, `CPU`, `sehir` ya da `1; DROP TABLE sunucular` listede olmadığı için hepsi aynı sonucu verir. Uygulama kodunda aynı fikir bir sözlüktür: `{"ad": "ad", "cpu": "cpu"}.get(girdi, "id")`; sorguya sözlüğün **değeri** yazılır, girdinin kendisi asla.

Bağlamanın korumadığı bir yer daha vardır: `LIKE` deseni. `ad LIKE '%' || ? || '%'` güvenlidir (değer hâlâ veridir) ama kullanıcının yazdığı `%` ve `_` deseni joker olarak genişletir: `_` aramak her adı bulur. Jokerleri kaçırıp kaçış karakterini `ESCAPE` ile bildirirsin:

```sql
WITH istek(q) AS (VALUES ('_'))
SELECT ad FROM sunucular, istek
WHERE ad LIKE '%' || replace(replace(replace(q, '\', '\\'), '%', '\%'), '_', '\_') || '%' ESCAPE '\';
```

Örnekte aranan `_`'dir; hiçbir sunucunun adında alt çizgi olmadığı için sonuç boştur. Kaçırma olmadan aynı desen on iki sunucunun hepsini verirdi.

Önce kaçış karakterinin kendisi ikilenir, sonra `%` ve `_` kaçırılır. SQLite'ta `LIKE` ASCII harflerde büyük-küçük harfe duyarsızdır.
:::

::: tahmin
Üç sonuç. Hangileri?

```sql
SELECT 'SELECT ad FROM personel WHERE ad = ''' || 'x'' OR ''1''=''1' || '''' AS giden_metin;

SELECT COUNT(*) FROM personel WHERE ad = 'x'' OR ''1''=''1';

SELECT COUNT(*) FROM personel WHERE ad = 'x' OR '1'='1';
```

???

`SELECT ad FROM personel WHERE ad = 'x' OR '1'='1'`, `0` ve `10`. İlk satır birleştirmenin veritabanına gönderdiği metindir: girdideki tırnak değeri kapatmış, ardından gelen `OR '1'='1'` koşul olmuştur. İkinci sorguda aynı karakterler tek bir değişmezdir (tırnaklar ikilenmiş, bağlanan parametre gibi): adı tam olarak `x' OR '1'='1` olan kimse yok, 0. Üçüncüsü birleştirilmiş metnin kendisidir: `'1'='1'` her satırda doğru, on personelin hepsi gelir.
:::

::: gorev Formdan gelen eşik
Uygulama, izleme ekranındaki "CPU en az" kutusunun değerini `istek` tablosuna `esik` adıyla yazıyor. Değer formdan geldiği için **metindir**; kutu boş bırakılırsa `''`, alan hiç gönderilmezse `NULL` olur.

`cpu` değeri eşiğe **eşit ya da büyük** olan sunucuların `ad` ve `cpu` sütunlarını, `cpu` büyükten küçüğe (eşitlikte `ad` sırasıyla) getir. Eşik bir sayı değilse, boşsa ya da `NULL`'sa hiç satır gelmesin. Eşiği sorguya kendin yazma: `istek` tablosundan oku.

```setup
CREATE TABLE istek (ad TEXT PRIMARY KEY, deger);
INSERT INTO istek (ad, deger) VALUES ('esik', '60');
```

```starter
SELECT ad, cpu
FROM sunucular
WHERE cpu >= 60
ORDER BY cpu DESC, ad;
```

```test
def esik(v):
    deger = "NULL" if v is None else "'" + v.replace("'", "''") + "'"
    return dene("UPDATE istek SET deger = " + deger + " WHERE ad = 'esik';")

eq(sonuc, [("db01", 91), ("cache01", 84), ("web01", 72), ("web02", 65)], "eşik '60': dört sunucu, cpu büyükten küçüğe")
eq(sutunlar, ["ad", "cpu"], "sütunlar: ad, cpu")
eq([r[0] for r in esik("72")], ["db01", "cache01", "web01"], "eşiğe eşit olan dahil (72)")
eq([r[0] for r in esik("73")], ["db01", "cache01"], "eşiğin bir altı dışarıda (73)")
eq([r[0] for r in esik("71")], ["db01", "cache01", "web01"], "eşiğin bir üstü dahil (71)")
eq(len(esik("50.5")), 5, "ondalık eşik de sayı olarak karşılaştırılır")
eq(esik("abc"), [], "sayı olmayan eşik hiç satır getirmez (CAST onu 0 yapar, bütün sunucular gelirdi)")
eq(esik(""), [], "boş kutu hiç satır getirmez")
eq(esik(None), [], "gönderilmeyen alan (NULL) hiç satır getirmez")
eq(esik("0 OR 1=1"), [], "girdi koşul olmaz: '0 OR 1=1' bir sayı değildir")
eq([r[0] for r in esik("90")], ["db01"], "tek sunucu kalan eşik")
```

```solution
SELECT ad, cpu
FROM sunucular
WHERE cpu >= (SELECT deger FROM istek WHERE ad = 'esik')
ORDER BY cpu DESC, ad;
```

```hint
Sabit `60` yerine alt sorgu: `(SELECT deger FROM istek WHERE ad = 'esik')`. `cpu` bir `INTEGER` sütunu olduğu için `'72'` metni karşılaştırmada sayıya çevrilir.
```

```hint
`CAST(... AS INTEGER)` kullanma: `'abc'` ve `''` sessizce 0 olur ve bütün sunucular gelir. Sütunu alt sorguyla doğrudan karşılaştırmak yeterli.
```
:::

::: gorev İzinli sıralama alanı
Sunucu listesi ekranı `istek` tablosundaki `sirala` değerine göre sıralanıyor. Yalnızca üç alan izinli: `ad`, `cpu` ve `devreye`. Değer bunlardan biriyle **birebir** aynıysa o alana göre küçükten büyüğe sırala; eşitlikte `id` sırası. Değer başka herhangi bir şeyse (büyük harfli yazım, `cpu DESC`, izinli olmayan bir sütun, boş, `NULL`) liste `id` sırasıyla gelir.

`id` ve `ad` sütunlarını getir. Sorgu metnine kullanıcının yazdığı alanı koyamazsın; her izinli alanı kendin yaz.

```setup
CREATE TABLE istek (ad TEXT PRIMARY KEY, deger);
INSERT INTO istek (ad, deger) VALUES ('sirala', 'cpu');
```

```starter
SELECT id, ad
FROM sunucular
ORDER BY id;
```

```test
def sirala(v):
    deger = "NULL" if v is None else "'" + v.replace("'", "''") + "'"
    return [r[0] for r in dene("UPDATE istek SET deger = " + deger + " WHERE ad = 'sirala';")]

varsayilan = list(range(1, 13))
eq([r[0] for r in sonuc], [12, 9, 3, 7, 6, 11, 5, 10, 2, 1, 8, 4], "sirala='cpu': cpu küçükten büyüğe")
eq(sutunlar, ["id", "ad"], "sütunlar: id, ad")
eq(sirala("ad"), [8, 4, 5, 6, 7, 10, 12, 11, 1, 2, 3, 9], "sirala='ad': ada göre")
eq(sirala("devreye"), [9, 7, 3, 4, 6, 1, 2, 5, 10, 8, 11, 12], "sirala='devreye': eşit tarihlerde id sırası (web01, web02)")
eq(sirala("sehir"), varsayilan, "gerçek ama izinli olmayan sütun: varsayılan sıra")
eq(sirala("CPU"), varsayilan, "izinli liste birebir karşılaştırılır: 'CPU' değil 'cpu'")
eq(sirala("cpu DESC"), varsayilan, "yön eklenmiş girdi listede yok")
eq(sirala("1; DROP TABLE sunucular"), varsayilan, "girdi komut olmaz")
eq(sirala(""), varsayilan, "boş değer: varsayılan sıra")
eq(sirala(None), varsayilan, "NULL: varsayılan sıra")
```

```solution
SELECT id, ad
FROM sunucular
ORDER BY CASE (SELECT deger FROM istek WHERE ad = 'sirala')
           WHEN 'ad'      THEN ad
           WHEN 'cpu'     THEN cpu
           WHEN 'devreye' THEN devreye
         END,
         id;
```

```hint
`ORDER BY CASE (SELECT deger FROM istek WHERE ad = 'sirala') WHEN 'ad' THEN ad ... END, id`. Listede olmayan girdide `CASE` her satırda `NULL` verir ve sırayı ikinci terim olan `id` belirler.
```
:::

::: gorev Joker kaçırılmış arama
Sunucu arama kutusundaki değer `istek` tablosunda `q` adıyla duruyor. Adında bu metni **düz metin olarak** içeren sunucuların `ad` sütununu ada göre sıralı getir. Kullanıcının yazdığı `%` ve `_` joker değil, sıradan karakterdir; `\` de öyle. Arama kutusu boşsa (`''`) ya da değer `NULL`'sa hiç satır gelmesin.

```setup
CREATE TABLE istek (ad TEXT PRIMARY KEY, deger);
INSERT INTO istek (ad, deger) VALUES ('q', 'db');
```

```starter
SELECT ad
FROM sunucular
WHERE ad LIKE '%' || (SELECT deger FROM istek WHERE ad = 'q') || '%'
ORDER BY ad;
```

```test
def ara(v, ek=""):
    deger = "NULL" if v is None else "'" + v.replace("'", "''") + "'"
    return [r[0] for r in dene(ek + "UPDATE istek SET deger = " + deger + " WHERE ad = 'q';")]

yeni = ("INSERT INTO sunucular (ad, rol, isletim, cpu, devreye) VALUES "
        "('test_02', 'test', 'Debian 12', 1, '2026-10-01'), ('yuk%100', 'test', 'Debian 12', 1, '2026-10-01'), "
        "('eski\\yedek', 'yedek', 'Debian 12', 1, '2026-10-01');")
eq(sonuc, [("db01",), ("db02",)], "q='db': db01 ve db02")
eq(ara("01"), ["cache01", "db01", "dc01", "izleme01", "test01", "vpn01", "web01", "yedek01"], "q='01': adında 01 geçenler")
eq(ara("WEB"), ["web01", "web02", "web03"], "SQLite LIKE ASCII harflerde büyük-küçük ayırmaz")
eq(ara("_", yeni), ["test_02"], "'_' joker değil: yalnızca adında alt çizgi olan")
eq(ara("t_0", yeni), ["test_02"], "'t_0' test01'i bulmamalı (_ tek karakter jokeri olurdu)")
eq(ara("%", yeni), ["yuk%100"], "'%' joker değil: yalnızca adında yüzde olan")
eq(ara("\\", yeni), ["eski\\yedek"], "ters bölü de düz karakter")
eq(ara("x' OR '1'='1"), [], "girdi koşul olmaz")
eq(ara(""), [], "boş arama hiç satır getirmez")
eq(ara(None), [], "NULL arama hiç satır getirmez")
ok(kullanir("escape"), "LIKE ... ESCAPE kullan")
```

```solution
SELECT ad
FROM sunucular
WHERE (SELECT deger FROM istek WHERE ad = 'q') <> ''
  AND ad LIKE '%' || replace(replace(replace(
          (SELECT deger FROM istek WHERE ad = 'q'),
          '\', '\\'), '%', '\%'), '_', '\_') || '%' ESCAPE '\'
ORDER BY ad;
```

```hint
Önce `\`'yi `\\` yap, sonra `%`'yi `\%`, `_`'yi `\_`. Desenin sonuna `ESCAPE '\'` ekle: SQLite `\%`'yi düz yüzde olarak okur.
```

```hint
`'%' || '' || '%'` deseni `%%` olur ve her şeyi bulur. Boş aramayı ayrıca `<> ''` ile ele; `NULL` zaten `||` ile `NULL` desen verir ve hiçbir satır geçmez.
```
:::
