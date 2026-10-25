---
id: ph15
title: Laravel · İstek ve Yetki Zinciri
summary: Bir isteğin gerçek Laravel'de izlediği sıra: servis sağlayıcı boot (süreç başına bir kez), ara katmanın önce ve sonra evreleri, rota, denetleyici ve Gate/Policy; yetkinin nereye konduğunun işlemin çalışıp çalışmamasını belirlemesi (denetleyici içinde Gate::authorize ile rotaya bağlı can ara katmanının ölçülmüş farkı); konuk kullanıcıda yetenek geri çağırmasının hiç çağrılmadan reddedilmesi; 403'te ara katmanın sonra evresinin yine çalışması.
kazanim: ZCPE 4.3, ZCPE 5.1
---

::: anlat Bir istek hangi sırayla ilerler
`PH06`'da adı geçen framework'lerde kod bir yığın halkanın içinden geçer. Laravel 13'te sıra şudur:

1. **Servis sağlayıcılar** (`AppServiceProvider::boot`) — uygulama ayağa kalkarken bağlamalar ve `Gate` tanımları yapılır.
2. **Ara katmanlar** (middleware) — isteği sırayla sarar: her biri önce kendi işini yapar, sonra `$sonraki($istek)` ile halkanın içine geçer.
3. **Rota** eşleşir ve **denetleyici** (controller) çalışır.
4. **Yetki** (Gate / Policy) kararı verilir.
5. Ara katmanlar, yanıt dönerken **ters sırada** kendi "sonra" evrelerini çalıştırır.

```php norun
// app/Http/Middleware/Iz.php
public function handle(Request $istek, Closure $sonraki) {
    echo "ara-katman-once\n";
    $yanit = $sonraki($istek);      // halkanın içi: rota + denetleyici
    echo "ara-katman-sonra\n";
    return $yanit;
}
```

Sağlayıcı `boot`'u **süreç başına bir kez** çalışır, istek başına değil. Bu derste ölçüldü: arka arkaya üç istek işlendiğinde `saglayici-boot` satırı yalnız birincisinde göründü. Bir sağlayıcıda istek verisine göre karar vermek bu yüzden yanlıştır — o kod ikinci istekte yeniden çalışmaz.
:::

::: anlat Yetkiyi nereye koyduğun sonucu değiştirir
Yetki iki yere konabilir ve ikisi aynı şey değildir:

```php norun
// A: denetleyicinin İÇİNDE
Route::get('/ic/{id}', function ($id) {
    echo "denetleyici\n";
    Gate::authorize('rapor-gor', [$id]);   // buraya gelene kadar gövde çalıştı
    return "ic $id";
});

// B: ROTAYA bağlı (can ara katmanı)
Route::get('/dis/{id}', function ($id) {
    echo "denetleyici\n";
    return "dis $id";
})->middleware('can:rapor-gor,id');        // gövdeye hiç girilmez
```

Ölçülen fark (yetkisiz istek, ikisi de 403):

| Rota | `denetleyici` satırı | Durum |
|---|---|---|
| `/ic/2` (içeride) | **yazıldı** | 403 |
| `/dis/2` (rotada) | **yazılmadı** | 403 |

İkisi de aynı HTTP durumunu döndürür, ama `A`'da denetleyici gövdesi çalışmaya başlamıştır. `authorize` çağrısından **önce** yazılmış her satır — bir günlük kaydı, bir sayaç artırımı, bir dış servis çağrısı — yetkisiz kullanıcı için de gerçekleşmiştir. Bu yüzden yetki, korunan işlemin mümkün olduğunca önüne konur.

> [!TUZAK] Konukta yetenek geri çağrısı hiç çağrılmaz
> `Gate::define('rapor-gor', function ($kullanici, $id) { return $id === "1"; })` yazdığında `$kullanici` parametresi `null` kabul etmiyordur. Oturum açmamış bir istekte Laravel geri çağrıyı **hiç çalıştırmadan** reddeder. Ölçüldü: `/rapor/1` konuk olarak 403, aynı adres oturumlu kullanıcıyla 200 döndü — `id` ikisinde de `"1"`di. Yani "yetenek mantığım bunu zaten kabul ederdi" diye düşünmek yanıltır; konuğu istiyorsan parametreyi `?User $kullanici` diye yazman gerekir.

Bir ayrıntı daha ölçüldü: yetki reddedildiğinde bile ara katmanın **sonra** evresi çalışır. `Gate::authorize`'ın fırlattığı `AuthorizationException` boru hattının içinde yakalanıp 403 yanıtına çevrilir; dolayısıyla `$sonraki($istek)` dışarıya istisna atmaz, bir yanıt döndürür. "Yetki hatası varsa benim sonra kodum atlanır" varsayımı tutmaz.
:::

::: tahmin Gövde çalıştı mı?
`rapor-gor` yeteneği yalnız `id === "1"` için izin verir; her iki istek de oturumlu `ayse` ile yapılır.

```php
// A: Gate::authorize denetleyicinin içinde
Route::get('/ic/{id}', function ($id) {
    echo "3-denetleyici-basi\n";
    Gate::authorize('rapor-gor', [$id]);
    echo "4-yetki-gecti\n";
    return "ic $id";
})->middleware([SahteGiris::class, Iz::class]);

// B: yetki rotaya bağlı
Route::get('/dis/{id}', function ($id) {
    echo "3-denetleyici-basi\n";
    return "dis $id";
})->middleware([SahteGiris::class, Iz::class, 'can:rapor-gor,id']);

// istekler: /ic/2?kullanici=ayse  ve  /dis/2?kullanici=ayse
```

```gercek
=== /ic/2?kullanici=ayse
1-saglayici-boot
1-ara-katman-giris: ayse
2-ara-katman-once
3-denetleyici-basi
5-ara-katman-sonra
durum=403
=== /dis/2?kullanici=ayse
1-ara-katman-giris: ayse
2-ara-katman-once
5-ara-katman-sonra
durum=403
```

???

İkisi de **403** döner, ama `/ic/2`'de `3-denetleyici-basi` yazılır, `/dis/2`'de yazılmaz.

`A`'da istek denetleyiciye ulaştı, gövde çalışmaya başladı ve ancak `Gate::authorize` satırında durdu; `4-yetki-gecti` yazılmadı. `B`'de `can` ara katmanı rotadan önce karar verdiği için gövdeye hiç girilmedi.

Her iki durumda da `5-ara-katman-sonra` yazılıyor: yetki reddi bir istisna olarak dışarı sızmaz, boru hattının içinde 403 yanıtına dönüşür, dolayısıyla `Iz` ara katmanının `$sonraki($istek)` çağrısı normal şekilde geri döner.

`1-saglayici-boot` yalnız **birinci** isteğin başında görünür: sağlayıcılar süreç ayağa kalkarken bir kez boot edilir, istek başına değil.

Dışarıdan bakan biri iki rotayı ayırt edemez — ikisi de 403'tür. Farkı yalnız kodu okuyarak görürsün.
:::

::: gorev Zincirin akışı
`akis(yetki_yeri, yetkili)` yaz: bir isteğin hangi adımları çalıştırdığını ve hangi durumu döndürdüğünü modelle.

- `yetki_yeri`: `"rota"` (can ara katmanı) ya da `"denetleyici"` (`Gate::authorize` gövdede).
- `yetkili`: yetki kararı olumlu mu.

Dönüş `(adimlar, durum)`:

- `adimlar`: sırayla çalışan adımlar; `"ara-katman-once"`, `"denetleyici"` ve `"ara-katman-sonra"` arasından.
- `durum`: `200` ya da `403`.

Kurallar (ölçüldü): ara katmanın her iki evresi de **her durumda** çalışır. Yetki rotadaysa ve reddedilmişse denetleyici hiç çalışmaz; denetleyicideyse gövdeye girilir ve adım listesine yazılır.

```starter
def akis(yetki_yeri, yetkili):
    adimlar = ["ara-katman-once", "denetleyici", "ara-katman-sonra"]
    return (adimlar, 200 if yetkili else 403)
```

```test
need("akis")
eq(akis("denetleyici", False),
   (["ara-katman-once", "denetleyici", "ara-katman-sonra"], 403),
   "ölçülen: yetki gövdedeyse denetleyici yetkisizken de çalışır")
eq(akis("rota", False),
   (["ara-katman-once", "ara-katman-sonra"], 403),
   "ölçülen: yetki rotadaysa gövdeye hiç girilmez")
eq(akis("rota", True),
   (["ara-katman-once", "denetleyici", "ara-katman-sonra"], 200), "izinli istek gövdeye girer")
eq(akis("denetleyici", True),
   (["ara-katman-once", "denetleyici", "ara-katman-sonra"], 200), "izinliyken iki yerleşim aynı")
eq(akis("rota", False)[1], akis("denetleyici", False)[1],
   "dışarıdan iki yerleşim ayırt edilemez: ikisi de 403")
ok("ara-katman-sonra" in akis("rota", False)[0], "403'te de ara katmanın sonra evresi çalışır")
```

```solution
def akis(yetki_yeri, yetkili):
    adimlar = ["ara-katman-once"]
    if yetkili or yetki_yeri == "denetleyici":
        adimlar.append("denetleyici")
    adimlar.append("ara-katman-sonra")
    return (adimlar, 200 if yetkili else 403)
```

```hint
Dört durumdan yalnız biri denetleyiciyi atlar: yetki **rotada** ve karar **ret**. Diğer üçünde gövdeye girilir. Durum kodu ise yalnız `yetkili`'ye bağlıdır, yerleşime değil.
```
:::

::: gorev Konuk mu, yetkisiz mi?
`karar(kullanici, yetenek)` yaz: `Gate`'in kararını ve yetenek geri çağrısının çalışıp çalışmadığını modelle.

- `kullanici`: oturum açmış kullanıcının adı ya da konuk için `None`.
- `yetenek`: geri çağrı **çalışsaydı** döndüreceği değer (`True`/`False`).

Geri çağrının `$kullanici` parametresi `null` kabul etmiyor. Dönüş `(sonuc, cagrildi)`: `sonuc` `"izin"` ya da `"ret"`, `cagrildi` geri çağrının çalışıp çalışmadığı.

```starter
def karar(kullanici, yetenek):
    return ("izin" if yetenek else "ret", True)
```

```test
need("karar")
eq(karar(None, True), ("ret", False),
   "ölçülen: konukta geri çağrı hiç çağrılmaz, izin verecek olsa bile reddedilir")
eq(karar(None, False), ("ret", False), "konuk her durumda reddedilir")
eq(karar("ayse", True), ("izin", True), "oturumlu ve yetenek olumlu")
eq(karar("ayse", False), ("ret", True), "oturumlu ama yetenek olumsuz")
eq(karar(None, True)[0], karar("ayse", False)[0],
   "iki ret aynı görünür ama nedenleri farklıdır")
eq(karar(None, True)[1], False, "konukta geri çağrı çalışmadığı için mantığı denenmemiştir")
```

```solution
def karar(kullanici, yetenek):
    if kullanici is None:
        return ("ret", False)
    return ("izin" if yetenek else "ret", True)
```

```hint
Konuk denetimi yetenek sonucundan **önce** gelir ve geri çağrıyı hiç çalıştırmaz. `yetenek` değeri konuk durumunda sonucu etkilemez.
```
:::
