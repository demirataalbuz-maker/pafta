---
id: ph16
title: WordPress · REST Uç Noktası Yetkileri
summary: register_rest_route'un permission_callback argümanı: true/false/WP_Error dönüşlerinin karşılığı ve aynı reddin anonim istekte 401, oturumlu istekte 403 olması (ölçüldü); argüman hiç verilmezse WordPress yalnız geliştirici uyarısı basar ve uç nokta anonime 200 döner; yeteneğin (edit_posts) rolle ilişkisi; nonce'un CSRF kanıtı olduğu, yetki kanıtı olmadığı — geçerli bir nonce ile yetkisiz bir kullanıcı aynı anda var olabilir.
kazanim: ZCPE 4.3, ZCPE 6.3
---

::: anlat Uç noktayı kaydetmek ve izin geri çağrısı
Bir WordPress eklentisi kendi REST uç noktasını `register_rest_route` ile tanıtır. Üç şey verilir: hangi HTTP yöntemi, işi yapan `callback` ve **kimin çağırabileceğini** söyleyen `permission_callback`.

```php norun
register_rest_route('pafta/v1', '/rapor', [
    'methods'             => 'GET',
    'callback'            => 'pafta_raporu_ver',
    'permission_callback' => fn() => current_user_can('edit_posts'),
]);
```

`permission_callback` üç şey döndürebilir:

| Dönüş | Sonuç |
|---|---|
| `true` | istek `callback`'e geçer |
| `false` | reddedilir; durum kodunu WordPress seçer |
| `WP_Error` | reddedilir; **hatanın kendi** `status` değeri kullanılır |

Reddedilen isteğin kodu, isteğin kimliği doğrulanmış olup olmamasına göre değişir. Bu derste ölçüldü (WordPress 7.1.3): `current_user_can('edit_posts')` döndüren aynı geri çağrı için —

| Kullanıcı | `/acik` (`__return_true`) | `/yetenek` (`edit_posts`) | `/wperror` (`WP_Error` 451) |
|---|---|---|---|
| anonim | 200 | **401** `rest_forbidden` | 451 |
| abone | 200 | **403** `rest_forbidden` | 451 |
| editör | 200 | 200 | 451 |

Hata **kodu** ikisinde de `rest_forbidden`'dır, ama durum farklıdır: 401 "kim olduğunu bilmiyorum", 403 "kim olduğunu biliyorum ve yetkin yok" demektir. `WP_Error` döndürdüğünde ise bu ayrım kaybolur; 451 herkese aynı gider. Günlüğe bakan biri 401 ile 403'ü ayırt edebilmelidir.

`edit_posts` bir **yetenektir** (capability), rol değil. Ölçüldü: editör rolünde `edit_posts` `true`, abone rolünde `false`. Denetimi `current_user_can('edit_posts')` ile yetenek üzerinden yaz; `$user->roles` dizisini okuyup `"editor"` aramak rol adları özelleştirildiğinde ya da yetenek elle verildiğinde yanılır.
:::

::: anlat Unutulan izin ve nonce'un sınırı
`permission_callback` **zorunludur**, ama onu unutmak uç noktayı kaydettirmez diye düşünme. Ölçüldü: argüman verilmeden kaydedilen bir rota için WordPress şu uyarıyı üretir —

```text
register_rest_route: The REST API route definition for pafta/v1/eksik is missing the
required permission_callback argument. For REST API routes that are intended to be
public, use __return_true as the permission callback.
```

— ve ardından **anonim istek 200 döner, veri gelir**. Yani uyarı yalnız geliştiriciye bakar (`_doing_it_wrong`, çoğu üretim kurulumunda hiç görünmez); uç nokta herkese açıktır. Kod incelemesinde `register_rest_route` çağrılarını sayıp her birinde bu argümanı aramak bu yüzden tek başına değerli bir denetimdir.

İkinci yaygın karışıklık nonce'tur. Nonce, isteğin **o kullanıcının kendi oturumundan** geldiğini gösterir; siteler arası istek sahteciliğine (CSRF) karşıdır. Ne kimlik doğrular ne de yetki verir. Ölçüldü:

- Abone kullanıcının ürettiği nonce doğrulandığında `wp_verify_nonce` **1** döner (geçerli), ama aynı anda `current_user_can('edit_posts')` **false**'tur. Geçerli nonce + yetkisiz kullanıcı yan yana durabilir.
- Yöneticinin ürettiği bir nonce, geçerli kullanıcı aboneyken doğrulanmaya çalışıldığında **false** döner: nonce kullanıcıya bağlıdır.

> [!TUZAK] Nonce denetimini yetki denetimi yerine koyma
> `if (!wp_verify_nonce($_REQUEST['_wpnonce'], 'pafta')) { ... }` yazıp `permission_callback`'i `__return_true` bırakan bir eklenti, giriş yapmış **her** kullanıcıya o işlemi açar — nonce'u zaten kendi oturumundan üretebilirler. İkisi farklı soruları yanıtlar: nonce "bu isteği bu kullanıcı mı başlattı?", `current_user_can` "bu kullanıcının buna hakkı var mı?". İkisi de gerekir, biri diğerinin yerine geçmez.
:::

::: tahmin Aynı ret, farklı kod
`/yetenek` uç noktasının izni `current_user_can('edit_posts')`; `/wperror` ise `status` değeri 451 olan bir `WP_Error` döndürür. Üç istemci sırayla çağırır.

```php
register_rest_route('pafta/v1', '/yetenek', ['methods' => 'GET',
    'callback' => fn() => ['sonuc' => 'yetenek'],
    'permission_callback' => fn() => current_user_can('edit_posts')]);
register_rest_route('pafta/v1', '/wperror', ['methods' => 'GET',
    'callback' => fn() => ['sonuc' => 'x'],
    'permission_callback' => fn() => new WP_Error('pafta_ret', 'Yetkin yok', ['status' => 451])]);
// anonim, abone ve editör olarak /yetenek ve /wperror çağrılır
```

```gercek
anonim  401 rest_forbidden    451 pafta_ret
abone   403 rest_forbidden    451 pafta_ret
editor  200 yetenek           451 pafta_ret
```

???

`/yetenek` üç istemciye üç farklı kod verir. Anonim istekte geri çağrı `false` döner ve WordPress **401** seçer: kimlik yok. Abone de `false` alır ama kimliği bilindiği için **403**: "seni tanıyorum, bu işi yapamazsın". Editörde `edit_posts` yeteneği olduğu için 200.

Dikkat: anonim ile abonenin hata **kodu** aynı (`rest_forbidden`); ayrım yalnız HTTP durumundadır. Yanıt gövdesine bakıp "ikisi de aynı hata" demek yanlış olur.

`/wperror` ise üçüne de **451** döner. Geri çağrı bir `WP_Error` döndürdüğünde durum kodunu WordPress değil hatanın kendisi belirler; 401/403 ayrımı ortadan kalkar. Editör bile 451 alır — çünkü geri çağrı kullanıcıya hiç bakmadan hata döndürüyor.
:::

::: gorev İzin kararından HTTP durumuna
`durum(oturum_var, izin)` yaz: bir `permission_callback` sonucunun hangi HTTP durumuna dönüştüğünü modelle.

- `oturum_var`: isteğin kimliği doğrulanmış mı.
- `izin`: geri çağrının dönüşü — `True`, `False` ya da `("hata", kod)` biçiminde bir `WP_Error`.

Ölçülen kurallar: `True` → 200. `False` → oturum yoksa 401, varsa 403. `WP_Error` → hatanın kendi kodu, oturum durumundan bağımsız.

```starter
def durum(oturum_var, izin):
    if izin is True:
        return 200
    return 403
```

```test
need("durum")
eq(durum(False, True), 200, "izin verildi")
eq(durum(True, True), 200, "oturumlu ve izinli")
eq(durum(False, False), 401, "ölçülen: anonim ret 401")
eq(durum(True, False), 403, "ölçülen: oturumlu ret 403")
eq(durum(False, ("hata", 451)), 451, "WP_Error kendi kodunu dayatır")
eq(durum(True, ("hata", 451)), 451, "oturum durumu WP_Error'u değiştirmez")
eq(durum(True, ("hata", 404)), 404, "başka bir hata kodu")
ok(durum(False, False) != durum(True, False),
   "anonim ile oturumlu ret aynı koda düşmemeli")
```

```solution
def durum(oturum_var, izin):
    if isinstance(izin, tuple):
        return izin[1]
    if izin is True:
        return 200
    return 403 if oturum_var else 401
```

```hint
Sıra önemlidir: önce `WP_Error` (demet) mi diye bak, sonra `True` mi, en son ret. `if izin:` denetimini demet denetiminden **önce** yazarsan boş olmayan bir demet de doğru sayılır ve `WP_Error` izin vermiş gibi 200 döner. Reddi 401/403 diye ayıran tek şey `oturum_var`'dır.
```
:::

::: gorev Kayıtları denetle
`denetle(rotalar)` yaz: bir eklentinin `register_rest_route` çağrılarını inceleyip her rotayı sınıflandır.

Her rota bir sözlüktür: `yol` anahtarı her zaman vardır; `izin` anahtarı `permission_callback` değerini taşır ve **hiç bulunmayabilir**.

Her rota için sınıf:

- `"acik-kazara"`: `izin` anahtarı yok. WordPress uyarı basar ama uç nokta herkese açıktır.
- `"acik-bilerek"`: `izin` değeri `"__return_true"`.
- `"korumali"`: başka her değer.

Dönüş `(siniflar, kazara_sayisi)`: `siniflar` her rota için `(yol, sinif)` demetlerinden oluşan liste (girdi sırasıyla), `kazara_sayisi` ise `"acik-kazara"` olanların sayısı.

```starter
def denetle(rotalar):
    siniflar = []
    for r in rotalar:
        if r.get("izin") == "__return_true":
            siniflar.append((r["yol"], "acik-bilerek"))
        else:
            siniflar.append((r["yol"], "korumali"))
    return (siniflar, 0)
```

```test
need("denetle")
eq(denetle([{"yol": "/a", "izin": "__return_true"}]), ([("/a", "acik-bilerek")], 0), "bilerek açık")
eq(denetle([{"yol": "/b", "izin": "current_user_can('edit_posts')"}]), ([("/b", "korumali")], 0), "yetenek denetimi")
eq(denetle([{"yol": "/c"}]), ([("/c", "acik-kazara")], 1),
   "ölçülen: izin anahtarı yoksa uç nokta anonime açıktır")
eq(denetle([{"yol": "/d", "izin": "__return_false"}]), ([("/d", "korumali")], 0),
   "__return_false herkesi reddeder, açık değildir")
eq(denetle([{"yol": "/a", "izin": "__return_true"}, {"yol": "/c"}, {"yol": "/b", "izin": "is_user_logged_in()"}]),
   ([("/a", "acik-bilerek"), ("/c", "acik-kazara"), ("/b", "korumali")], 1), "karışık liste, giriş sırası korunur")
eq(denetle([{"yol": "/x"}, {"yol": "/y"}]), ([("/x", "acik-kazara"), ("/y", "acik-kazara")], 2), "iki kazara")
eq(denetle([]), ([], 0), "hiç rota yok")
eq(denetle([{"yol": "/n", "izin": None}]), ([("/n", "korumali")], 0),
   "anahtar var ama değeri None: kazara eksik sayılmaz, okunup incelenmesi gereken bir değerdir")
```

```solution
def denetle(rotalar):
    siniflar = []
    for r in rotalar:
        if "izin" not in r:
            sinif = "acik-kazara"
        elif r["izin"] == "__return_true":
            sinif = "acik-bilerek"
        else:
            sinif = "korumali"
        siniflar.append((r["yol"], sinif))
    return (siniflar, sum(1 for _, s in siniflar if s == "acik-kazara"))
```

```hint
Başlangıç kodu `r.get("izin")` kullanıyor; bu, anahtarın **yokluğu** ile değerinin `None` olmasını birbirine karıştırır. Ayrımı `"izin" not in r` ile yap.
```

```hint
Sayıyı ayrıca saymak yerine sınıflandırmayı bitirip `"acik-kazara"` olanları say; böylece iki yerde aynı kuralı tekrarlamazsın.
```
:::
