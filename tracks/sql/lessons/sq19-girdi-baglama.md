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

Burada sorgunun metni sabittir; `?` yerine değer **ayrıştırma bittikten sonra** konur. Değerin içinde ne olursa olsun (tırnak, `OR`, `;`, `--`) bütünüyle tek bir metin değeridir; asla koşul ya da komut olmaz. `x' OR '1'='1` girdisi, adı tam olarak bu girdiyle aynı olan birini arar ve bulamaz.

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


::: anlat Uygulama–veritabanı köprüsü: gerçekten bağla
Önceki SQL görevlerindeki `istek` tablosu girdinin veri olarak kalmasını modeller. Şimdi **Python'un gerçek sqlite3 sürücüsünü** kullan: sorgu metni ve değer tuple'ı `execute(sql, params)` çağrısında ayrıdır. Python görevlerinde motor/dil meta'sı Python'dur; mevcut SQL görevleri SQLite sorgusu olarak kalır. Ek paket gerekmez.

Değer yer tutucusu bir sütun adı, ASC/DESC veya SQL parçası değildir. `ORDER BY ?` sütunu seçmez; her satırda aynı bağlı değeri sıralar. Bu parçaları yalnız sabit izinli listeden seç; serbest girdiyi sorguya ekleme. Parametre bağlamak yetki denetimini veya giriş türü/aralık doğrulamasını kendiliğinden yapmaz. `None` SQL NULL olur; SQLite'a özgü `ad IS ?` NULL ile NULL'u da eşleştirir. Başka motorda eşdeğer NULL eşitlik söz dizimi ayrıca seçilir.

| Okuma köprüsü | Ayrı değer bağlama | İnceleme tuzağı |
|---|---|---|
| Java **JV10 · JDBC** | `prepareStatement("... ad = ?")`, sonra `setString(1, ad)` | prepareStatement çağrısından önce `+ ad` ile metin üretmek bağlama değildir; indeks 1'den başlar |
| PHP **PH08 · PDO** | `$pdo->prepare("... ad = ?")->execute([$ad])` | değerleri `.` ile eklemek yerine execute argümanlarını incele; yer tutucu sütun adı değildir |
| C# **CS10 · EF Core** | `FromSqlInterpolated($"... ad = {ad}")` FormattableString alır | interpolasyonu önce düz string'e dönüştürüp FromSqlRaw'a vermek değer bağlamasını kaybettirir; `FromSqlRaw("... ad = {0}", ad)` ise parametreli olabilir |

Bu köprü okuma düzeyini yükseltmez; diğer yollar okuma yolu kalır. Bu iki görevin kabulü Python sqlite3 içindir, JDBC/PDO/EF Core'un gerçekten çalıştırıldığı iddia edilmez. Oradaki sürücü/ORM davranışı ilgili dersin kendi tezgâhıyla ayrıca doğrulanır.

Kaynaklar: [Python sqlite3 placeholders](https://docs.python.org/3/library/sqlite3.html#how-to-use-placeholders-to-bind-values-in-sql-queries), [JDBC PreparedStatement](https://docs.oracle.com/javase/tutorial/jdbc/basics/prepared.html), [PDO prepare](https://www.php.net/manual/en/pdo.prepare.php), [EF Core SQL queries](https://learn.microsoft.com/en-us/ef/core/querying/sql-queries).
:::

::: gorev Sürücüye değerleri ayrı ver
`personel_ara(db, ad, min_cpu, alan='id', azalan=False)` `(id,ad,cpu)` tuple listesi döndürsün. `ad` str veya None; `min_cpu` bool olmayan int 0..100; `alan` id/ad/cpu; `azalan` tam bool. İhlalde ValueError ve hiç SQL çalıştırma. `ad IS ?` ve `cpu >= ?` değerleri gerçek execute ikinci argümanında bağlansın. Sırayı izinli alan ASC/DESC ile kur, eşitlikte id ASC kullan. Girdiyi kırpma/normalize etme; bağlantıyı kapatma, veri değiştirme. `personel(id,ad,cpu)` hazırdır.

```meta
motor: python
dil: python
```

```starter
def personel_ara(db, ad, min_cpu, alan='id', azalan=False):
    return db.execute('SELECT id,ad,cpu FROM personel').fetchall()
```

```test
import sqlite3
need('personel_ara')
class GercekBaglanti(sqlite3.Connection):
    def execute(self,sql,params=()):
        self.calls.append((sql,params))
        return super().execute(sql,params)
db=sqlite3.connect(':memory:',factory=GercekBaglanti);db.calls=[]
db.execute('CREATE TABLE personel(id INTEGER PRIMARY KEY,ad TEXT,cpu INTEGER)')
db.executemany('INSERT INTO personel VALUES (?,?,?)',[(1,'Ayşe',79),(2,'Ayşe',80),(3,'Ayşe',81),(4,"O'Brien",100),(5,None,0),(6,'Ayşe',80),(7,"x' OR '1'='1",80),(8,'',80)])
db.execute('CREATE INDEX ters_esitlik ON personel(cpu DESC,id DESC)')
for ad,threshold,expected in [('ayşe',0,[]),('Ayşe',80,[(2,'Ayşe',80),(3,'Ayşe',81),(6,'Ayşe',80)]),("O'Brien",100,[(4,"O'Brien",100)]),(None,0,[(5,None,0)]),("x' OR '1'='1",80,[(7,"x' OR '1'='1",80)]),('',80,[(8,'',80)]),('yok',0,[])]:
    db.calls=[]
    eq(personel_ara(db,ad,threshold),expected,'bağlı gerçek değer ve eşik')
    ok(any(tuple(params)==(ad,threshold) for _,params in db.calls),'execute ikinci argümanı gerçek iki değeri taşıyor')
eq(personel_ara(db,'Ayşe',0,'cpu',True),[(3,'Ayşe',81),(2,'Ayşe',80),(6,'Ayşe',80),(1,'Ayşe',79)],'azalan CPU; eşitlikte id artan')
eq(personel_ara(db,'Ayşe',0,'cpu',False),[(1,'Ayşe',79),(2,'Ayşe',80),(6,'Ayşe',80),(3,'Ayşe',81)],'artan CPU')
eq(personel_ara(db,'Ayşe',0,'id',True),[(6,'Ayşe',80),(3,'Ayşe',81),(2,'Ayşe',80),(1,'Ayşe',79)],'azalan id')
eq(personel_ara(db,'Ayşe',0,'ad',False),[(1,'Ayşe',79),(2,'Ayşe',80),(3,'Ayşe',81),(6,'Ayşe',80)],'izinli ad alanı eşitliğinde id')
for args in [('Ayşe',-1),('Ayşe',101),('Ayşe',True),('Ayşe','80'),(123,80),('Ayşe',80,'cpu; DROP TABLE personel'),('Ayşe',80,'CPU'),('Ayşe',80,'id',1)]:
    db.calls=[]
    raises(ValueError,personel_ara,db,*args,msg='bozuk girdi SQL çalıştırmadan reddedilir')
    eq(db.calls,[],'reddedilen girdide execute yok')
eq(db.execute('SELECT COUNT(*) FROM personel').fetchone(),(8,),'girdiler tabloyu değiştirmedi')
db.execute('INSERT INTO personel VALUES (9,?,?)',('Ayşe',100))
eq(personel_ara(db,'Ayşe',100),[(9,'Ayşe',100)],'yeni veri ve üst eşik dahil')
```

```solution
def personel_ara(db, ad, min_cpu, alan='id', azalan=False):
    if (not isinstance(ad,(str,type(None))) or type(min_cpu) is not int
            or not 0<=min_cpu<=100 or alan not in ('id','ad','cpu') or type(azalan) is not bool):
        raise ValueError('Geçersiz arama girdisi')
    direction='DESC' if azalan else 'ASC'
    order=alan+' '+direction+', id ASC'
    return db.execute('SELECT id,ad,cpu FROM personel WHERE ad IS ? AND cpu >= ? ORDER BY '+order,
                      (ad,min_cpu)).fetchall()
```

```hint
İzinli sıra parçasını sabit kümeden seç; gerçek ad/eşik değerlerini SQL metnine koyma. Tek elemanlı parametre tuple'ında virgül gerekeceğini PH08'de karşılaştır.
```
:::

::: gorev Parametre bağlama LIKE jokerini kendiliğinden kaçırmaz
`onek_ara(db, onek, limit)` personel adında **literal önek** arayıp `(id,ad)` satırlarını id sırasında döndürsün. onek str, limit bool olmayan int 1..20; aksi ValueError. `\`, `%`, `_` karakterlerini bu sırayla LIKE için kaçır, sonuna yalnız bir `%` ekle. `LIKE ? ESCAPE '\'` ve `LIMIT ?` kullanarak pattern/limit değerlerini ayrı bağla. Boş önek bütün NULL olmayan adlara uyar. Bu görev SQLite varsayılan LIKE davranışını kullanır: ASCII harfleri harfe duyarsızdır; bütün Unicode harfleri için büyük/küçük eşitliği vaat etmez.

```meta
motor: python
dil: python
```

```starter
def onek_ara(db, onek, limit):
    return db.execute('SELECT id,ad FROM personel WHERE ad LIKE ? ORDER BY id LIMIT ?', (onek+'%',limit)).fetchall()
```

```test
import sqlite3
need('onek_ara')
class GercekBaglanti(sqlite3.Connection):
    def execute(self,sql,params=()):
        self.calls.append((sql,params));return super().execute(sql,params)
db=sqlite3.connect(':memory:',factory=GercekBaglanti);db.calls=[]
db.execute('CREATE TABLE personel(id INTEGER PRIMARY KEY,ad TEXT)')
rows=[(1,'a%b'),(2,'axxb'),(3,'a_b'),(4,r'a\b'),(5,"O'Brien"),(6,None),(7,''),(8,'AYSE'),(9,'a%tail'),(10,'a_tail')]
db.executemany('INSERT INTO personel VALUES (?,?)',rows)
for prefix,expected,pattern in [('a%',[(1,'a%b'),(9,'a%tail')],r'a\%%'),('a_',[(3,'a_b'),(10,'a_tail')],r'a\_%'),('a\\',[(4,r'a\b')],r'a\\%'),("O'",[(5,"O'Brien")],"O'%"),('ayse',[(8,'AYSE')],'ayse%'),("x' OR 1=1 --",[],"x' OR 1=1 --%")]:
    db.calls=[]
    eq(onek_ara(db,prefix,20),expected,'literal önek: '+prefix)
    ok(any(tuple(params)==(pattern,20) for _,params in db.calls),'pattern ve LIMIT ayrı bağlı')
eq(onek_ara(db,'',1),[(1,'a%b')],'limit alt ucu')
eq(onek_ara(db,'',20),[(i,a) for i,a in rows if a is not None],'NULL hariç, boş ad dahil')
db.executemany('INSERT INTO personel VALUES (?,?)',[(n,'extra') for n in range(11,36)])
eq(len(onek_ara(db,'',20)),20,'limit üst ucu gerçekten kırpar')
for prefix,limit in [(None,1),(123,1),('',0),('',21),('',True),('',1.5)]:
    db.calls=[];raises(ValueError,onek_ara,db,prefix,limit,msg='bozuk önek/limit')
    eq(db.calls,[],'bozuk girdide SQL çağrısı yok')
eq(db.execute('SELECT COUNT(*) FROM personel').fetchone(),(35,),'arama veri değiştirmez')
db.execute('INSERT INTO personel VALUES (?,?)',(100,'za%b'))
eq(onek_ara(db,'a%',20),[(1,'a%b'),(9,'a%tail')],'ortada geçen önek değildir')
```

```solution
def onek_ara(db, onek, limit):
    if not isinstance(onek,str) or type(limit) is not int or not 1<=limit<=20:
        raise ValueError('Metin önek ve 1..20 limit gerekli')
    pattern=onek.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')+'%'
    return db.execute("SELECT id,ad FROM personel WHERE ad LIKE ? ESCAPE '\\' ORDER BY id LIMIT ?",
                      (pattern,limit)).fetchall()
```

```hint
Bağlama SQL kodunu ayırır; LIKE içindeki %/_ hâlâ operatördür. Önce kaçış karakterini kaçır, sonra iki jokeri ve en son uygulamanın önek jokerini ekle.
```
:::
