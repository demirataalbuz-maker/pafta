---
id: jv13
title: Spring Data JPA · Türetilmiş Sorgular ve @Transactional Proxy'si
summary: JV10'daki JDBC'nin üstündeki katman: arayüzden türetilen repository sorguları (findBy…OrderBy…, countBy, In/Not), JPQL @Query ve @Modifying; @Transactional'ın bir proxy olarak çalışması: commit, RuntimeException'da rollback, denetimli istisnada commit, rollbackFor, readOnly ve aynı sınıf içinden çağrıda (self-invocation) işlemin hiç açılmaması. Çıktılar sürümü kilitli gerçek düzenekten.
---

::: anlat Arayüz yazarsın, sorguyu Spring üretir
JV10'da SQL'i kendin yazıp `PreparedStatement`'la çalıştırdın. Spring uygulamalarının çoğu bunun yerine **Spring Data JPA** kullanır: yalnız bir arayüz yazarsın, Spring çalışma zamanında onu uygulayan bir **proxy** üretir. Yöntemin **adı** sorgunun kendisidir:

```java
interface BiletDeposu extends JpaRepository<Bilet, Long> {
    List<Bilet> findByDurumOrderByIdAsc(String durum);                  // where durum = ?1 order by id asc
    long countByOncelik(String oncelik);                                // select count(*) … where oncelik = ?1
    List<Bilet> findByOncelikInAndDurumNot(List<String> o, String d);   // where oncelik in ?1 and durum <> ?2
    @Query("select b.baslik from Bilet b where b.durum = :durum and b.oncelik = 'kritik' order by b.id")
    List<String> kritikBasliklar(String durum);                         // JPQL: tablo değil varlık adı
    @Modifying @Query("update Bilet b set b.durum = 'kapalı' where b.oncelik = :oncelik")
    int topluKapat(String oncelik);                                     // değişen satır sayısı
}
```

Bu dersteki her çıktı `tracks/java/jpa_lab/` düzeneğinden gelir: **Spring Data JPA 4.1.2**, **Hibernate 7.4.13**, **H2 2.5.252** (bellek içi), JDK 21. Aynı çıktıyı `python tools/jpa_lab.py` ile kendin üretebilirsin. Beş biletlik veride ölçülen sonuçlar:

```text
türetilmiş: [1:Disk dolu/kritik/açık, 2:Yama/yüksek/açık, 4:DNS/düşük/açık, 5:502/kritik/açık]
say kritik: 3
In/Not: [1:Disk dolu/kritik/açık, 4:DNS/düşük/açık, 5:502/kritik/açık]
@Query: [Disk dolu, 502]
depo sınıfı proxy: true
```

Türetilmiş adın parçaları: önek (`find…By`, `count…By`, `exists…By`, `delete…By`), alan adları (varlıktaki alan adıyla birebir), aralarında `And`/`Or`, alanın sonunda işleç (`Not`, `In`, `LessThan`, `GreaterThan`, `IsNull`, `Like`, `Between` …) ve en sonda `OrderBy<Alan>Asc|Desc`. Ad bir alana uymazsa uygulama **açılışta** hata verir; çalışma zamanında sürpriz olmaz. `@Query` ise JPQL'dir: sorgu varlık ve alan adlarıyla yazılır, Hibernate onu SQL'e çevirir.

Kaynak: [Spring Data JPA sorgu yöntemleri](https://docs.spring.io/spring-data/jpa/reference/jpa/query-methods.html).
:::

::: anlat @Transactional bir proxy'dir
`@Transactional` sınıfın içinde değil, Spring'in o sınıfın **önüne** koyduğu bir proxy'de çalışır (ölçüldü: servis nesnesinin sınıfı asıl sınıf değil, bir CGLIB alt sınıfı). Proxy çağrıyı yakalar, işlemi açar, yöntemi çağırır, sonuca göre **commit** ya da **rollback** yapar. Bu tek cümle şaşırtan bütün davranışları açıklar. Düzenekte ölçülen sonuçlar (satır sayısı: önce → sonra):

| Servis yöntemi | Sonuç |
|---|---|
| `@Transactional`, hatasız iki kayıt ekler | commit: 5 → 7 |
| `@Transactional`, ilk kayıttan sonra `IllegalStateException` | **rollback**: 7 → 7 |
| `@Transactional`, kayıttan sonra denetimli bir istisna (`throws OzelHata`) | **commit**: 7 → 8 |
| `@Transactional(rollbackFor = OzelHata.class)`, aynı durum | rollback: 8 → 8 |
| işlemsiz bir yöntemden **aynı sınıfın** `@Transactional` yöntemini çağırmak | `işlem yok` |
| aynı `@Transactional` yöntemi proxy üzerinden (başka bir nesneden) çağırmak | `işlem var` |
| `@Transactional(readOnly = true)` | `işlem var, salt okunur=true` |
| `@Modifying` sorguyu işlem dışında çağırmak | `InvalidDataAccessApiUsageException` |

- **Varsayılan kural:** yalnız `RuntimeException` ve `Error` rollback ettirir. Denetimli istisnalar (checked) işlemi **commit eder**; geri alınması gerekiyorsa `rollbackFor` yazılır.
- **Self-invocation:** bir yöntem aynı sınıfın başka bir yöntemini `this.` üzerinden çağırdığında proxy aradan çıkar; çağrılan yöntemdeki `@Transactional` **hiç uygulanmaz**. İşlem gerektiren mantık ayrı bir bean'e taşınır ya da çağrı dışarıdan yapılır.
- `@Modifying` güncelleme sorguları bir işlem ister; servis katmanında `@Transactional` altında çağrılır.

> [!GÜVENLİK]
> Bu kuralların sessiz ihlali veri bütünlüğü hatasıdır: "para çekildi ama işlem kaydı yazılmadı" gibi yarım işlemler çoğu zaman denetimli bir istisnanın commit ettirmesinden ya da self-invocation yüzünden hiç açılmamış bir işlemden çıkar. Kod incelemesinde `@Transactional` gördüğün her yerde iki soruyu sor: bu yöntem **dışarıdan** mı çağrılıyor, ve fırlatabileceği istisnalar **geri alınıyor** mu?
:::

::: tahmin Dört çağrı, dört sayım
Düzenekte başlangıçta 5 bilet var. `servis` Spring'in verdiği bean'dir (proxy). Hangi dört "önce → sonra" satırı yazılır?

```java
@Transactional public void ikisiniEkle(boolean patlat) {
    depo.save(new Bilet("A", "orta", "açık"));
    if (patlat) throw new IllegalStateException("çalışma zamanı hatası");
    depo.save(new Bilet("B", "orta", "açık"));
}
@Transactional public void denetimliHata() throws OzelHata {          // OzelHata extends Exception
    depo.save(new Bilet("C", "düşük", "açık"));
    throw new OzelHata("denetimli");
}
@Transactional(rollbackFor = OzelHata.class) public void denetimliHataGeriAl() throws OzelHata {
    depo.save(new Bilet("D", "düşük", "açık"));
    throw new OzelHata("denetimli, rollbackFor");
}
// sırayla: ikisiniEkle(false); ikisiniEkle(true); denetimliHata(); denetimliHataGeriAl();
// her çağrının istisnası yakalanır ve ardından depo.count() yazılır
```

```gercek
commit: 5 → 7
RuntimeException rollback: 7 → 7
denetimli istisna: 7 → 8
rollbackFor: 8 → 8
```

???

İlk çağrı iki kayıt ekler ve commit eder. İkincisi `RuntimeException` fırlatır: ilk kayıt da geri alınır, sayı 7'de kalır. Üçüncüsü denetimli bir istisna fırlatır; varsayılan kural yalnız çalışma zamanı istisnalarında rollback yaptığı için `C` kaydı **commit edilir**: 8. Dördüncüsünde `rollbackFor` denetimli istisnayı da geri alma nedeni yapar: 8'de kalır.
:::

::: gorev İşlemin sonu
`islem_sonucu(cagri, istisna, rollback_for=())` fonksiyonunu yaz: `@Transactional` bir yöntemin çağrısından sonra ne olduğunu döndürsün: `"commit"`, `"rollback"` ya da `"işlem yok"`.

- `cagri`: `"proxy"` (başka bir bean'den, proxy üzerinden) ya da `"ic"` (aynı sınıfın içinden, `this.` ile).
- `istisna`: `None` (hatasız), `"runtime"` (bir `RuntimeException`), `"error"` (bir `Error`) ya da denetimli bir istisnanın sınıf adı (örneğin `"OzelHata"`, `"IOException"`).
- `rollback_for`: `rollbackFor` ile listelenen sınıf adları.
- İçeriden çağrıda işlem hiç açılmaz: istisna ne olursa olsun `"işlem yok"`.
- Tanınmayan `cagri`: `ValueError`.

Testlerin ilk dört satırı düzenekte ölçülen sonuçlardır.

```starter
def islem_sonucu(cagri, istisna, rollback_for=()):
    if istisna is None:
        return "commit"
    return "rollback"
```

```test
f = need("islem_sonucu")
eq(f("proxy", None), "commit", "ölçüldü: 5 → 7")
eq(f("proxy", "runtime"), "rollback", "ölçüldü: 7 → 7")
eq(f("proxy", "OzelHata"), "commit", "ölçüldü: denetimli istisna commit eder (7 → 8)")
eq(f("proxy", "OzelHata", ("OzelHata",)), "rollback", "ölçüldü: rollbackFor (8 → 8)")
eq(f("ic", None), "işlem yok", "ölçüldü: self-invocation işlem açmaz")
eq(f("ic", "runtime"), "işlem yok", "içeriden çağrıda rollback da yok")
eq(f("proxy", "error"), "rollback", "Error da rollback ettirir")
eq(f("proxy", "IOException", ("OzelHata",)), "commit", "listede olmayan denetimli istisna commit eder")
eq(f("proxy", "runtime", ("OzelHata",)), "rollback", "rollbackFor varsayılan kuralı kaldırmaz, genişletir")
raises(ValueError, f, "uzak", None, msg="tanınmayan çağrı türü")
```

```solution
def islem_sonucu(cagri, istisna, rollback_for=()):
    if cagri == "ic":
        return "işlem yok"
    if cagri != "proxy":
        raise ValueError(f"tanınmayan çağrı: {cagri!r}")
    if istisna is None:
        return "commit"
    if istisna in ("runtime", "error") or istisna in rollback_for:
        return "rollback"
    return "commit"
```

```hint
Önce çağrı türü: içeriden çağrıda proxy yoktur, işlem de yoktur. Sonra istisna: `RuntimeException` ve `Error` her zaman rollback; denetimli istisna yalnız `rollbackFor`'da listelenmişse.
```
:::

::: gorev Türetilmiş sorguyu oku
`jpql(yontem)` fonksiyonunu yaz: Spring Data'nın türetilmiş sorgu yöntem adını, `Bilet` varlığı (`b`) üzerinde karşılık gelen JPQL'e çevirsin. Desteklenecek alt küme:

- Önek: `findBy` → `select b from Bilet b`, `countBy` → `select count(b) from Bilet b`.
- Koşullar: alan adları büyük harfle başlar (`Durum` → `b.durum`), `And` / `Or` ile bağlanır. Parametreler sırayla `?1`, `?2`, … olur.
- Alan sonundaki işleçler: yok → `= ?n`, `Not` → `<> ?n`, `In` → `in ?n`, `LessThan` → `< ?n`, `GreaterThan` → `> ?n`, `IsNull` → `is null` (parametre almaz).
- En sonda isteğe bağlı `OrderBy<Alan>Asc|Desc` → ` order by b.alan asc|desc`.
- Önek tanınmazsa ya da `By`'dan sonra koşul yoksa `ValueError`.

```starter
def jpql(yontem):
    alan = yontem.replace("findBy", "")
    return f"select b from Bilet b where b.{alan.lower()} = ?1"
```

```test
f = need("jpql")
eq(f("findByDurumOrderByIdAsc"), "select b from Bilet b where b.durum = ?1 order by b.id asc", "düzenekteki ilk yöntem")
eq(f("countByOncelik"), "select count(b) from Bilet b where b.oncelik = ?1", "sayma")
eq(f("findByOncelikInAndDurumNot"), "select b from Bilet b where b.oncelik in ?1 and b.durum <> ?2", "In ve Not, iki parametre")
eq(f("findByAtananIsNullOrOncelik"), "select b from Bilet b where b.atanan is null or b.oncelik = ?1", "IsNull parametre almaz; sıradaki ?1 olur")
eq(f("findByAcilisGreaterThanAndAcilisLessThanOrderByAcilisDesc"),
   "select b from Bilet b where b.acilis > ?1 and b.acilis < ?2 order by b.acilis desc", "aralık ve azalan sıra")
eq(f("findBySunucuAdi"), "select b from Bilet b where b.sunucuAdi = ?1", "çok kelimeli alan: ilk harf küçülür, gerisi aynı kalır")
eq(f("findByNotlar"), "select b from Bilet b where b.notlar = ?1", "Not ile başlayan alan adı işleç sanılmaz")
for kotu in ("getByDurum", "findBy", "findByOrderByIdAsc", "deleteByDurum"):
    raises(ValueError, f, kotu, msg=f"desteklenmeyen ya da koşulsuz: {kotu}")
```

```solution
import re

ISLECLER = [("IsNull", "is null"), ("GreaterThan", ">"), ("LessThan", "<"), ("Not", "<>"), ("In", "in")]


def jpql(yontem):
    m = re.fullmatch(r"(find|count)By(.+?)(?:OrderBy([A-Z]\w*?)(Asc|Desc))?", yontem)
    if not m:
        raise ValueError(f"desteklenmeyen yöntem: {yontem}")
    onek, kosullar, sira_alan, yon = m.groups()
    if kosullar.startswith("OrderBy"):
        raise ValueError(f"By'dan sonra koşul yok: {yontem}")
    bas = "select b from Bilet b" if onek == "find" else "select count(b) from Bilet b"
    parcalar = re.split(r"(And|Or)(?=[A-Z])", kosullar)
    sql, no = [], 0
    for i, parca in enumerate(parcalar):
        if i % 2 == 1:
            sql.append(parca.lower())
            continue
        islec = "="
        for ek, karsilik in ISLECLER:
            if parca.endswith(ek) and len(parca) > len(ek):
                parca, islec = parca[:-len(ek)], karsilik
                break
        alan = "b." + parca[0].lower() + parca[1:]
        if islec == "is null":
            sql.append(f"{alan} is null")
        else:
            no += 1
            sql.append(f"{alan} {islec} ?{no}")
    sorgu = f"{bas} where " + " ".join(sql)
    if sira_alan:
        sorgu += f" order by b.{sira_alan[0].lower() + sira_alan[1:]} {yon.lower()}"
    return sorgu
```

```hint
Adı üç parçaya ayır: önek (`find`/`count`), `By` ile `OrderBy` arasındaki koşullar, isteğe bağlı sıralama. Koşulları `And`/`Or`'dan böl; her parçanın sonunda bir işleç eki var mı bak.
```

```hint
İşleç eklerini uzundan kısaya dene (`IsNull`, `GreaterThan`, `LessThan`, `Not`, `In`) ve ek alanın tamamı olmasın (`Notlar` bir alandır, `Not` işleci değil). `IsNull` parametre sayacını artırmaz.
```
:::
