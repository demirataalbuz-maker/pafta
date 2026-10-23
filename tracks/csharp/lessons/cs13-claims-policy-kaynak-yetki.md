---
id: cs13
title: Claims, Policy ve Kaynak Tabanlı (Resource-Based) Yetkilendirme
summary: ClaimsPrincipal hak talepleri, AddPolicy gereksinimleri (VE), çoklu IAuthorizationHandler işleyicileri (VEYA + context.Fail) ve IAuthorizationService ile nesne sahipliği kontrolü.
---

::: anlat Claims (`ClaimsPrincipal`), Poliçeler (`AddPolicy`) ve Gereksinim/İşleyici Mantığı
CS09'da denetleyici ve eylem üzerindeki `[Authorize(Roles = "...")]` bildirimlerini görmüştük. ASP.NET Core'da rol kontrollerinin de altında **hak talebi** (*claim*) ve **poliçe** (*policy*) modeli yatar:

- **`Claim` ve `ClaimsPrincipal`:** Bir kullanıcı oturum açtığında kimlik sağlayıcı kullanıcının kimliğine (`ClaimsIdentity` / `ClaimsPrincipal`) bir veya daha fazla **hak talebi** (*claim*: `Type` ve `Value` çifti) ekler. Microsoft'un resmi *Claim-based authorization in ASP.NET Core* belgesinde vurgulandığı gibi bir *claim*, öznenin ne yapabileceğini değil **ne olduğunu** temsil eder ve bir kimlik aynı türden birden fazla *claim* taşıyabilir (`User.FindFirst`, `User.HasClaim`).
- **`RequireClaim` farkı:**
  - `policy.RequireClaim("PersonelNo")` yalnızca `"PersonelNo"` adlı *claim*'in **varlığını** denetler (değerine bakmaz).
  - `policy.RequireClaim("Birim", "SOC", "CERT")` ise hem *claim*'in varlığını hem de değerinin izin verilen listede (`"SOC"` veya `"CERT"`) olmasını şart koşar.
- **Poliçe içindeki gereksinimler (`Requirements`) = VE (`AND`):** Bir poliçe bir veya daha fazla `IAuthorizationRequirement` nesnesinden oluşur. *Policy-based authorization in ASP.NET Core* belgesine göre bir poliçedeki **tüm gereksinimler** karşılanmadan poliçe başarılı sayılmaz (`context.PendingRequirements` boşalmalıdır).
- **Tek gereksinim için birden fazla işleyici (`IAuthorizationHandler`) = VEYA (`OR`) ve `context.Fail()` sınırı:**
  - Bir işleyici, gereksinimin karşılandığını `context.Succeed(requirement)` çağrısıyla bildirir. Koşul sağlanmadığında işleyici yalnızca `return Task.CompletedTask;` dönerse, aynı gereksinimi dinleyen **başka bir işleyici** `context.Succeed(requirement)` çağırarak gereksinimi geçirebilir (**VEYA** mantığı; örneğin kapıdan giriş için personel kartı **veya** geçici ziyaretçi etiketi).
  - Ancak herhangi bir işleyici **`context.Fail()`** çağırırsa, başka bir işleyici `context.Succeed(requirement)` çağırmış olsa bile yetkilendirme **kesin olarak başarısız olur**!
  - Varsayılan olarak (`InvokeHandlersAfterFailure = true`), bir işleyici `Succeed` veya `Fail` çağırsa bile kayıtlı diğer tüm işleyiciler çalışmaya devam eder ve yetkilendirme işleyicileri kimlik doğrulama başarısız olduğunda dahi çağrılır.

```csharp
using System;
using System.Security.Claims;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.Extensions.DependencyInjection;

public class EnAzSeviyeGereksinimi(int altSinir) : IAuthorizationRequirement
{
    public int AltSinir { get; } = altSinir;
}

public class SeviyeIsleyici : AuthorizationHandler<EnAzSeviyeGereksinimi>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        EnAzSeviyeGereksinimi requirement)
    {
        var claim = context.User.FindFirst("YetkiSeviyesi");
        if (claim is not null && int.TryParse(claim.Value, out int seviye) &&
            seviye >= requirement.AltSinir)
        {
            context.Succeed(requirement);          #! seviye >= AltSinir ise gereksinim karşılandı
        }
        return Task.CompletedTask;
    }
}

class Ornek1
{
    static async Task Main()
    {
        var services = new ServiceCollection();
        services.AddLogging();
        services.AddAuthorizationCore(options =>
        {
            options.AddPolicy("SocAnalistPolicesi", policy =>
            {
                policy.RequireClaim("PersonelNo");
                policy.RequireClaim("Birim", "SOC", "CERT");
                policy.Requirements.Add(new EnAzSeviyeGereksinimi(2));
            });
        });
        services.AddSingleton<IAuthorizationHandler, SeviyeIsleyici>();
        using var sp = services.BuildServiceProvider();
        var auth = sp.GetRequiredService<IAuthorizationService>();

        var tamKullanici = new ClaimsPrincipal(new ClaimsIdentity(new[]
        {
            new Claim("PersonelNo", "P-104"),
            new Claim("Birim", "SOC"),
            new Claim("YetkiSeviyesi", "2")
        }, "Cookie"));

        var eksikClaim = new ClaimsPrincipal(new ClaimsIdentity(new[]
        {
            new Claim("Birim", "SOC"),
            new Claim("YetkiSeviyesi", "3")
        }, "Cookie"));

        Console.WriteLine((await auth.AuthorizeAsync(tamKullanici, null, "SocAnalistPolicesi")).Succeeded);
        Console.WriteLine((await auth.AuthorizeAsync(eksikClaim, null, "SocAnalistPolicesi")).Succeeded);
    }
}
```
:::

::: anlat Neden `[Authorize]` Yetmez? `IAuthorizationService` ve Kaynak Tabanlı Yetkilendirme
Aynı `"Analist"` rolüne sahip iki kullanıcıdan (`ayse` ve `mert`) yalnızca belgenin sahibi olanın veya aynı birimde olup gizlilik sınırı içindekilerin o belgeye erişmesini istediğimizde, sınıf veya metot tepesindeki `[Authorize]` özniteliği **yeterli olmaz**.

Microsoft'un resmi *Resource-based authorization in ASP.NET Core* belgesinde açıklandığı üzere:
- **Öznitelik değerlendirmesi veri bağlamadan (*data binding*) ve kaynağı veritabanından yükleyen metot çalışmadan önce gerçekleşir.** Bu yüzden bildirimsel (*declarative*) `[Authorize]` özniteliği henüz veritabanından çekilmemiş bir `Belge` nesnesinin `Yazar` veya `Gizlilik` alanını göremez.
- Bunun yerine uygulama önce kaynağı yüklemeli, ardından **`IAuthorizationService.AuthorizeAsync(user, resource, ...)`** çağrısıyla **buyruksal yetkilendirme** (*imperative authorization*) yapmalıdır.
- **`AuthorizationHandler<TRequirement, TResource>` ve `OperationAuthorizationRequirement`:**
  - Kaynak tabanlı işleyici hem gereksinim türünü hem de kaynak nesnesinin türünü (`Belge`) tip parametresi olarak alır.
  - CRUD (`Create`, `Read`, `Update`, `Delete`) işlemlerini tek bir işleyicide toplamak için `Microsoft.AspNetCore.Authorization.Infrastructure` ad alanındaki `OperationAuthorizationRequirement` yardımcı sınıfı kullanılır.

```csharp
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Authorization.Infrastructure;

public record Belge(string Id, string Yazar, string Birim, int Gizlilik);

public static class Islemler
{
    public static readonly OperationAuthorizationRequirement Read = new() { Name = nameof(Read) };
    public static readonly OperationAuthorizationRequirement Update = new() { Name = nameof(Update) };
    public static readonly OperationAuthorizationRequirement Delete = new() { Name = nameof(Delete) };
}

public class BelgeYetkiIsleyici : AuthorizationHandler<OperationAuthorizationRequirement, Belge>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        OperationAuthorizationRequirement requirement,
        Belge resource)
    {
        string? ad = context.User.Identity?.Name;
        string? birim = context.User.FindFirst("Birim")?.Value;

        if (requirement.Name == Islemler.Read.Name)
        {
            if (ad == resource.Yazar ||
                (birim != null && birim == resource.Birim && resource.Gizlilik <= 2))
            {
                context.Succeed(requirement);
            }
        }
        else if (requirement.Name == Islemler.Update.Name)
        {
            if (ad == resource.Yazar && resource.Gizlilik < 3)
            {
                context.Succeed(requirement);
            }
        }
        else if (requirement.Name == Islemler.Delete.Name)
        {
            if (context.User.IsInRole("SuperUser") && birim == resource.Birim)
            {
                context.Succeed(requirement);
            }
        }
        return Task.CompletedTask;
    }
}
```

> [!GÜVENLİK]
> Beyaz kutu kod incelemesinde bir denetleyici metodunun başında `[Authorize(Policy = "...")]` görsen bile, metot `id` parametresiyle veritabanından bir kayıt çekip `await _authorizationService.AuthorizeAsync(User, kayit, ...)` (veya eşdeğer bir sahiplik/birim kontrolü) yapmadan doğrudan nesneyi döndürüyorsa **BOLA / IDOR** (*Broken Object Level Authorization*) zafiyeti oluşur!
:::

::: tahmin
```csharp
using System;
using System.Collections.Generic;
using System.Security.Claims;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Authorization.Infrastructure;
using Microsoft.Extensions.DependencyInjection;

public record Belge(string Id, string Yazar, string Birim, int Gizlilik);

public static class Islemler
{
    public static readonly OperationAuthorizationRequirement Read = new() { Name = nameof(Read) };
    public static readonly OperationAuthorizationRequirement Update = new() { Name = nameof(Update) };
    public static readonly OperationAuthorizationRequirement Delete = new() { Name = nameof(Delete) };
}

public class BelgeYetkiIsleyici : AuthorizationHandler<OperationAuthorizationRequirement, Belge>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        OperationAuthorizationRequirement requirement,
        Belge resource)
    {
        string? ad = context.User.Identity?.Name;
        string? birim = context.User.FindFirst("Birim")?.Value;

        if (requirement.Name == Islemler.Read.Name)
        {
            if (ad == resource.Yazar ||
                (birim != null && birim == resource.Birim && resource.Gizlilik <= 2))
            {
                context.Succeed(requirement);
            }
        }
        else if (requirement.Name == Islemler.Update.Name)
        {
            if (ad == resource.Yazar && resource.Gizlilik < 3)
            {
                context.Succeed(requirement);
            }
        }
        else if (requirement.Name == Islemler.Delete.Name)
        {
            if (context.User.IsInRole("SuperUser") && birim == resource.Birim)
            {
                context.Succeed(requirement);
            }
        }
        return Task.CompletedTask;
    }
}

public class AskidaHesapEngelleyici : IAuthorizationHandler
{
    public Task HandleAsync(AuthorizationHandlerContext context)
    {
        if (context.User.HasClaim("HesapDurumu", "Askida"))
        {
            context.Fail();
        }
        return Task.CompletedTask;
    }
}

class Tahmin
{
    static ClaimsPrincipal Kullanici(string ad, string? birim, string rol, bool askida = false)
    {
        var claims = new List<Claim> { new(ClaimTypes.Name, ad), new(ClaimTypes.Role, rol) };
        if (birim != null)
            claims.Add(new("Birim", birim));
        if (askida)
            claims.Add(new("HesapDurumu", "Askida"));
        return new ClaimsPrincipal(new ClaimsIdentity(claims, "Bearer"));
    }

    static async Task Main()
    {
        var services = new ServiceCollection();
        services.AddLogging();
        services.AddAuthorizationCore();
        services.AddSingleton<IAuthorizationHandler, BelgeYetkiIsleyici>();
        services.AddSingleton<IAuthorizationHandler, AskidaHesapEngelleyici>();
        using var sp = services.BuildServiceProvider();
        var auth = sp.GetRequiredService<IAuthorizationService>();

        var normalBelge = new Belge("B-10", "ayse", "SOC", 2);
        var gizliBelge = new Belge("B-20", "ayse", "SOC", 3);

        var ayse = Kullanici("ayse", "SOC", "Analist");
        var mert = Kullanici("mert", "SOC", "Analist");
        var birimsiz = Kullanici("can", null, "Analist");
        var askidaAyse = Kullanici("ayse", "SOC", "SuperUser", askida: true);

        Console.WriteLine($"1:{(await auth.AuthorizeAsync(mert, normalBelge, Islemler.Read)).Succeeded}");
        Console.WriteLine($"2:{(await auth.AuthorizeAsync(mert, gizliBelge, Islemler.Read)).Succeeded}");
        Console.WriteLine($"3:{(await auth.AuthorizeAsync(ayse, gizliBelge, Islemler.Read)).Succeeded}");
        Console.WriteLine($"4:{(await auth.AuthorizeAsync(ayse, gizliBelge, Islemler.Update)).Succeeded}");
        Console.WriteLine($"5:{(await auth.AuthorizeAsync(birimsiz, normalBelge, Islemler.Read)).Succeeded}");
        Console.WriteLine($"6:{(await auth.AuthorizeAsync(askidaAyse, normalBelge, Islemler.Read)).Succeeded}");
    }
}
```

```gercek
1:True
2:False
3:True
4:False
5:False
6:False
```

???

`1:True`, `2:False`, `3:True`, `4:False`, `5:False`, `6:False`.
1. `mert` belgenin yazarı değildir ama `"Birim"` *claim*'i `"SOC"` olduğu ve `normalBelge.Gizlilik <= 2` (`2 <= 2`) sınırını sağladığı için `Read` yetkisi alır (`1:True`).
2. `gizliBelge.Gizlilik` değeri `3` olduğu için (`3 <= 2` yanlış) `mert` aynı birimde olsa bile okuyamaz (`2:False`).
3. `ayse` `gizliBelge`'nin yazarı (`ad == resource.Yazar`) olduğu için gizlilik derecesi `3` olsa da `Read` işleminde `context.Succeed` çalışır (`3:True`).
4. `Update` işleminde yazar olma şartının yanında `resource.Gizlilik < 3` koşulu vardır; `gizliBelge.Gizlilik` `3` olduğu için (`3 < 3` yanlış) `ayse` kendi gizli belgesini güncelleyemez (`4:False`).
5. `birimsiz` kullanıcısında `"Birim"` *claim*'i eksiktir (`FindFirst("Birim")?.Value` `null` döner) ve yazar da değildir (`5:False`).
6. `askidaAyse` belgenin yazarı olmasına ve `BelgeYetkiIsleyici` `context.Succeed(requirement)` çağırmasına rağmen, ikinci işleyici olan `AskidaHesapEngelleyici` `"HesapDurumu" = "Askida"` *claim*'ini görüp `context.Fail()` çağırdığı için sonuç kesin olarak `False` döner (`6:False`).
:::

::: gorev 1 · Poliçe gereksinimleri (VE), çoklu işleyiciler (VEYA) ve `context.Fail()` değerlendiricisi
ASP.NET Core'da bir poliçedeki gereksinimleri (`Requirements`) ve işleyicileri (`IAuthorizationHandler`) değerlendiren `police_degerlendir(kullanici, gereksinimler)` fonksiyonunu Python'da yaz:
- `kullanici` bir `dict` değilse veya `gereksinimler` boş olmayan bir `list` değilse `"400:GECERSIZ_POLITIKA_GIRDISI"` döndür.
- `kullanici.get("kimlik_dogrulandi")` değeri `True` değilse `"401:OTURUM_YOK"` döndür.
- `claims = kullanici.get("claims")` bir `dict` değilse `{}` kabul edilir. Bir *claim* anahtarının değeri tek bir metin (`"SOC"`) veya metin listesi (`["SOC", "CERT"]`) olabilir; karşılaştırmalar büyük-küçük harf duyarlıdır.
- Eğer `claims` içinde `"HesapDurumu"` anahtarının değerlerinden biri `"Askida"` ise (`context.Fail()`), diğer tüm gereksinimler sağlansa bile doğrudan `"403:FAIL_CAGRISI"` döndür.
- `gereksinimler` listesindeki **her** gereksinim sözlüğü sırayla kontrol edilir (**VE** mantığı):
  1. `{"tur": "ClaimVar", "claim": ad}`: `ad` anahtarı `claims` içinde bulunmalı ve en az bir boş olmayan (`len(deger) > 0`) metin değerine sahip olmalıdır.
  2. `{"tur": "ClaimDeger", "claim": ad, "izinli": [...]}`: `ad` *claim*'inin değerlerinden **en az biri** `izinli` listesinde yer almalıdır.
  3. `{"tur": "EnAzSeviye", "alt_sinir": n}`: `claims` içindeki `"YetkiSeviyesi"` değeri tam sayıya çevrilebilmeli ve **`seviye >= alt_sinir`** olmalıdır (`alt_sinir` bir `int` değilse `"400:TANIMSIZ_GEREKSINIM"`).
  4. `{"tur": "BinaGiris"}`: İki ayrı işleyici (**VEYA** mantığı) tarafından değerlendirilir; `claims` içinde boş olmayan `"KartId"` **veya** boş olmayan `"GeciciEtiket"` varsa başarılı sayılır.
  5. Bunların dışındaki bir `"tur"` değeri gelirse `"400:TANIMSIZ_GEREKSINIM"` döndür.
- Herhangi bir gereksinim sağlanmazsa `"403:GEREKSINIM_KARSILANMADI"`, tüm gereksinimler sağlanırsa `"200:POLITIKA_GECTI"` döndür.

```starter
def police_degerlendir(kullanici, gereksinimler):
    return "200:POLITIKA_GECTI"
```

```test
need("police_degerlendir")
tam_k = {
    "kimlik_dogrulandi": True,
    "claims": {
        "PersonelNo": "P-104",
        "Birim": ["SOC", "Analiz"],
        "YetkiSeviyesi": "2",
        "GeciciEtiket": "G-99"
    }
}
pol = [
    {"tur": "ClaimVar", "claim": "PersonelNo"},
    {"tur": "ClaimDeger", "claim": "Birim", "izinli": ["CERT", "SOC"]},
    {"tur": "EnAzSeviye", "alt_sinir": 2},
    {"tur": "BinaGiris"}
]
eq(police_degerlendir(tam_k, pol), "200:POLITIKA_GECTI", "tüm gereksinimler (seviye == 2 eşiği ve GeciciEtiket VEYA işleyicisi) sağlandığında 200:POLITIKA_GECTI")
eq(police_degerlendir({**tam_k, "claims": {**tam_k["claims"], "YetkiSeviyesi": "3"}}, pol), "200:POLITIKA_GECTI", "seviye=3 (> 2 eşik üstü) -> 200:POLITIKA_GECTI")
eq(police_degerlendir({**tam_k, "claims": {**tam_k["claims"], "YetkiSeviyesi": "1"}}, pol), "403:GEREKSINIM_KARSILANMADI", "seviye=1 (< 2 eşik altı) -> 403:GEREKSINIM_KARSILANMADI")
eq(police_degerlendir({**tam_k, "claims": {**tam_k["claims"], "YetkiSeviyesi": "iki"}}, pol), "403:GEREKSINIM_KARSILANMADI", "sayı olmayan YetkiSeviyesi -> 403:GEREKSINIM_KARSILANMADI")
eq(police_degerlendir({"kimlik_dogrulandi": True, "claims": {"KartId": "K-1"}}, [{"tur": "BinaGiris"}]), "200:POLITIKA_GECTI", "BinaGiris için yalnızca KartId (ilk işleyici) yeterli")
eq(police_degerlendir({"kimlik_dogrulandi": True, "claims": {"KartId": ""}}, [{"tur": "BinaGiris"}]), "403:GEREKSINIM_KARSILANMADI", "boş KartId ve GeciciEtiket yok -> 403:GEREKSINIM_KARSILANMADI")
eq(police_degerlendir({"kimlik_dogrulandi": True, "claims": {"PersonelNo": ""}}, [{"tur": "ClaimVar", "claim": "PersonelNo"}]), "403:GEREKSINIM_KARSILANMADI", "boş metinli claim ClaimVar'ı geçemez")
eq(police_degerlendir({"kimlik_dogrulandi": True, "claims": {"PersonelNo": [""]}}, [{"tur": "ClaimVar", "claim": "PersonelNo"}]), "403:GEREKSINIM_KARSILANMADI", "listede yalnız boş metin varsa ClaimVar geçemez")
eq(police_degerlendir({"kimlik_dogrulandi": True, "claims": {"PersonelNo": [5]}}, [{"tur": "ClaimVar", "claim": "PersonelNo"}]), "403:GEREKSINIM_KARSILANMADI", "listede metin olmayan değer claim sayılmaz")
eq(police_degerlendir({"kimlik_dogrulandi": True, "claims": {"PersonelNo": ["", "P-1"]}}, [{"tur": "ClaimVar", "claim": "PersonelNo"}]), "200:POLITIKA_GECTI", "listede en az bir boş olmayan metin yeter")
eq(police_degerlendir({"kimlik_dogrulandi": True, "claims": {"Birim": "IK"}}, [{"tur": "ClaimDeger", "claim": "Birim", "izinli": ["SOC", "CERT"]}]), "403:GEREKSINIM_KARSILANMADI", "izinli listede olmayan claim değeri -> 403")
eq(police_degerlendir({**tam_k, "claims": {**tam_k["claims"], "HesapDurumu": "Askida"}}, pol), "403:FAIL_CAGRISI", "HesapDurumu=Askida varken tüm gereksinimler sağlansa bile 403:FAIL_CAGRISI")
eq(police_degerlendir({"kimlik_dogrulandi": False, "claims": tam_k["claims"]}, pol), "401:OTURUM_YOK", "kimlik_dogrulandi=False -> 401:OTURUM_YOK")
eq(police_degerlendir(None, pol), "400:GECERSIZ_POLITIKA_GIRDISI", "None kullanıcı -> 400:GECERSIZ_POLITIKA_GIRDISI")
eq(police_degerlendir(tam_k, []), "400:GECERSIZ_POLITIKA_GIRDISI", "boş gereksinim listesi -> 400:GECERSIZ_POLITIKA_GIRDISI")
eq(police_degerlendir(tam_k, [{"tur": "Bilinmeyen"}]), "400:TANIMSIZ_GEREKSINIM", "bilinmeyen gereksinim türü -> 400:TANIMSIZ_GEREKSINIM")
```

```solution
import re

def _claim_degerleri(claims, ad):
    if not isinstance(claims, dict) or ad not in claims:
        return []
    ham = claims[ad]
    if isinstance(ham, str):
        return [ham] if ham != "" else []
    if isinstance(ham, list):
        return [x for x in ham if isinstance(x, str) and x != ""]
    return []

def police_degerlendir(kullanici, gereksinimler):
    if not isinstance(kullanici, dict) or not isinstance(gereksinimler, list) or not gereksinimler:
        return "400:GECERSIZ_POLITIKA_GIRDISI"
    if kullanici.get("kimlik_dogrulandi") is not True:
        return "401:OTURUM_YOK"
    claims = kullanici.get("claims")
    if not isinstance(claims, dict):
        claims = {}

    for g in gereksinimler:
        if not isinstance(g, dict):
            return "400:TANIMSIZ_GEREKSINIM"
        tur = g.get("tur")
        if tur not in ("ClaimVar", "ClaimDeger", "EnAzSeviye", "BinaGiris"):
            return "400:TANIMSIZ_GEREKSINIM"
        if tur == "EnAzSeviye" and type(g.get("alt_sinir")) is not int:
            return "400:TANIMSIZ_GEREKSINIM"

    if "Askida" in _claim_degerleri(claims, "HesapDurumu"):
        return "403:FAIL_CAGRISI"

    for g in gereksinimler:
        tur = g["tur"]
        if tur == "ClaimVar":
            if not _claim_degerleri(claims, g.get("claim", "")):
                return "403:GEREKSINIM_KARSILANMADI"
        elif tur == "ClaimDeger":
            izinli = g.get("izinli")
            if not isinstance(izinli, list):
                return "400:TANIMSIZ_GEREKSINIM"
            degerler = _claim_degerleri(claims, g.get("claim", ""))
            if not any(d in izinli for d in degerler):
                return "403:GEREKSINIM_KARSILANMADI"
        elif tur == "EnAzSeviye":
            alt_sinir = g["alt_sinir"]
            degerler = _claim_degerleri(claims, "YetkiSeviyesi")
            if not degerler or not re.fullmatch(r"[+-]?[0-9]+", degerler[0]):
                return "403:GEREKSINIM_KARSILANMADI"
            if int(degerler[0]) < alt_sinir:
                return "403:GEREKSINIM_KARSILANMADI"
        elif tur == "BinaGiris":
            kart_var = bool(_claim_degerleri(claims, "KartId"))
            etiket_var = bool(_claim_degerleri(claims, "GeciciEtiket"))
            if not (kart_var or etiket_var):
                return "403:GEREKSINIM_KARSILANMADI"

    return "200:POLITIKA_GECTI"
```

```hint
Önce girdi yapısını ve gereksinim türlerinin geçerliliğini denetle, ardından `"HesapDurumu"` içinde `"Askida"` varsa (`context.Fail()`) `"403:FAIL_CAGRISI"` döndür. Sonrasında tüm gereksinimleri `for` döngüsüyle (**VE**) kontrol et.
```
:::

::: gorev 2 · `IAuthorizationService.AuthorizeAsync` ile kaynak tabanlı (`Belge`) yetkilendirme
Tahmin adımındaki `BelgeYetkiIsleyici` ve `AskidaHesapEngelleyici` sınıflarının `IAuthorizationService.AuthorizeAsync(user, belge, islem)` davranışını Python'da `kaynak_yetkisi_kontrol(kullanici, belge, islem)` fonksiyonu olarak kur:
- `kullanici` veya `belge` bir `dict` değilse ya da `islem` boş olmayan bir `str` değilse `"400:GECERSIZ_ISTEK"` döndür.
- `belge` içinde `"yazar"` (`str`, boş olmayan), `"birim"` (`str`, boş olmayan) ve `"gizlilik"` (`int`, `bool` hariç!) alanları bulunmalıdır; aksi hâlde `"400:GECERSIZ_ISTEK"` döndür.
- `islem` yalnızca `"Read"`, `"Update"` veya `"Delete"` olabilir; aksi hâlde `"400:GECERSIZ_ISLEM"` döndür.
- `kullanici.get("kimlik_dogrulandi")` `True` değilse veya `kullanici.get("ad")` boş olmayan bir `str` değilse `"401:OTURUM_YOK"` döndür.
- `kullanici.get("askida") is True` ise (`AskidaHesapEngelleyici` → `context.Fail()`) doğrudan `"403:ASKIDA_RET"` döndür.
- İşlem kuralları (`ad = kullanici["ad"]`, `birim = kullanici.get("birim")`, `roller = kullanici.get("roller") or []`):
  - **`"Read"`:** `ad == belge["yazar"]` **veya** (`isinstance(birim, str)` ve `birim == belge["birim"]` ve **`belge["gizlilik"] <= 2`**) ise `"200:IZIN_VERILDI"`, değilse `"403:YETKISIZ"`.
  - **`"Update"`:** (`ad == belge["yazar"]` ve **`belge["gizlilik"] < 3`**) **veya** (`"Admin"` in `roller` ve `isinstance(birim, str)` ve `birim == belge["birim"]` ve **`belge["gizlilik"] <= 3`**) ise `"200:IZIN_VERILDI"`, değilse `"403:YETKISIZ"`.
  - **`"Delete"`:** `"SuperUser"` in `roller` **ve** `isinstance(birim, str)` **ve** `birim == belge["birim"]` **ve** **`belge["gizlilik"] <= 3`** ise `"200:IZIN_VERILDI"`, değilse `"403:YETKISIZ"`.

```starter
def kaynak_yetkisi_kontrol(kullanici, belge, islem):
    return "403:YETKISIZ"
```

```test
need("kaynak_yetkisi_kontrol")
ayse = {"kimlik_dogrulandi": True, "ad": "ayse", "birim": "SOC", "roller": ["Analist"]}
mert = {"kimlik_dogrulandi": True, "ad": "mert", "birim": "SOC", "roller": ["Analist"]}
admin_soc = {"kimlik_dogrulandi": True, "ad": "zeynep", "birim": "SOC", "roller": ["Admin"]}
super_soc = {"kimlik_dogrulandi": True, "ad": "kaan", "birim": "SOC", "roller": ["SuperUser"]}

b_g1 = {"id": "B-1", "yazar": "ayse", "birim": "SOC", "gizlilik": 1}
b_g2 = {"id": "B-2", "yazar": "ayse", "birim": "SOC", "gizlilik": 2}
b_g3 = {"id": "B-3", "yazar": "ayse", "birim": "SOC", "gizlilik": 3}
b_g4 = {"id": "B-4", "yazar": "ayse", "birim": "SOC", "gizlilik": 4}

# Read eşik testleri (gizlilik <= 2: 1, 2, 3) ve yazar ayrıcalığı
eq(kaynak_yetkisi_kontrol(mert, b_g1, "Read"), "200:IZIN_VERILDI", "aynı birim gizlilik=1 (< 2) -> Read 200")
eq(kaynak_yetkisi_kontrol(mert, b_g2, "Read"), "200:IZIN_VERILDI", "aynı birim gizlilik=2 (== 2 sınır) -> Read 200")
eq(kaynak_yetkisi_kontrol(mert, b_g3, "Read"), "403:YETKISIZ", "aynı birim ama gizlilik=3 (> 2 sınır üstü) -> Read 403")
eq(kaynak_yetkisi_kontrol(ayse, b_g4, "Read"), "200:IZIN_VERILDI", "belge yazarı gizlilik=4 olsa bile kendi belgesini okuyabilir")
eq(kaynak_yetkisi_kontrol({"kimlik_dogrulandi": True, "ad": "can", "birim": None, "roller": ["Analist"]}, b_g1, "Read"), "403:YETKISIZ", "birim claim'i olmayan kullanıcı başkasının belgesini okuyamaz")

# Update eşik testleri (yazar için gizlilik < 3: 1, 2 vs 3; Admin için gizlilik <= 3: 2, 3 vs 4)
eq(kaynak_yetkisi_kontrol(ayse, b_g1, "Update"), "200:IZIN_VERILDI", "yazar gizlilik=1 (< 2) belgesini güncelleyebilir")
eq(kaynak_yetkisi_kontrol(ayse, b_g2, "Update"), "200:IZIN_VERILDI", "yazar gizlilik=2 (< 3 sınır altı) belgesini güncelleyebilir")
eq(kaynak_yetkisi_kontrol(ayse, b_g3, "Update"), "403:YETKISIZ", "yazar gizlilik=3 (== 3 sınır) belgesini güncelleyemez")
eq(kaynak_yetkisi_kontrol(mert, b_g1, "Update"), "403:YETKISIZ", "yazar olmayan Analist gizlilik=1 olsa bile güncelleyemez")
eq(kaynak_yetkisi_kontrol(admin_soc, b_g2, "Update"), "200:IZIN_VERILDI", "aynı birim Admin gizlilik=2 (< 3 sınır altı) belgesini güncelleyebilir")
eq(kaynak_yetkisi_kontrol(admin_soc, b_g3, "Update"), "200:IZIN_VERILDI", "aynı birim Admin gizlilik=3 (== 3 sınır) belgesini güncelleyebilir")
eq(kaynak_yetkisi_kontrol(admin_soc, b_g4, "Update"), "403:YETKISIZ", "aynı birim Admin gizlilik=4 (> 3 sınır üstü) belgesini güncelleyemez")
eq(kaynak_yetkisi_kontrol({"kimlik_dogrulandi": True, "ad": "zeynep", "birim": "CERT", "roller": ["Admin"]}, b_g2, "Update"), "403:YETKISIZ", "farklı birimdeki Admin güncelleyemez")

# Delete eşik testleri (SuperUser + aynı birim + gizlilik <= 3: 2, 3 vs 4)
eq(kaynak_yetkisi_kontrol(super_soc, b_g2, "Delete"), "200:IZIN_VERILDI", "aynı birim SuperUser gizlilik=2 (< 3 sınır altı) silebilir")
eq(kaynak_yetkisi_kontrol(super_soc, b_g3, "Delete"), "200:IZIN_VERILDI", "aynı birim SuperUser gizlilik=3 (== 3 sınır) silebilir")
eq(kaynak_yetkisi_kontrol(super_soc, b_g4, "Delete"), "403:YETKISIZ", "aynı birim SuperUser gizlilik=4 (> 3 sınır üstü) silemez")
eq(kaynak_yetkisi_kontrol(ayse, b_g1, "Delete"), "403:YETKISIZ", "SuperUser olmayan yazar silemez")
eq(kaynak_yetkisi_kontrol({"kimlik_dogrulandi": True, "ad": "kaan", "birim": "CERT", "roller": ["SuperUser"]}, b_g1, "Delete"), "403:YETKISIZ", "farklı birimdeki SuperUser silemez")

# Askıda hesap (context.Fail), oturumsuz ve boş/hatalı girdi testleri
eq(kaynak_yetkisi_kontrol({**ayse, "askida": True}, b_g1, "Read"), "403:ASKIDA_RET", "askıda olan yazar context.Fail() ile 403:ASKIDA_RET alır")
eq(kaynak_yetkisi_kontrol({"kimlik_dogrulandi": False, "ad": "ayse"}, b_g1, "Read"), "401:OTURUM_YOK", "oturumsuz kullanıcı -> 401:OTURUM_YOK")
eq(kaynak_yetkisi_kontrol(ayse, b_g1, "Export"), "400:GECERSIZ_ISLEM", "tanımsız işlem -> 400:GECERSIZ_ISLEM")
eq(kaynak_yetkisi_kontrol(None, b_g1, "Read"), "400:GECERSIZ_ISTEK", "None kullanıcı -> 400:GECERSIZ_ISTEK")
eq(kaynak_yetkisi_kontrol(ayse, {"id": "B-1", "yazar": "ayse", "birim": "SOC", "gizlilik": True}, "Read"), "400:GECERSIZ_ISTEK", "bool gizlilik -> 400:GECERSIZ_ISTEK")
```

```solution
def kaynak_yetkisi_kontrol(kullanici, belge, islem):
    if not isinstance(kullanici, dict) or not isinstance(belge, dict):
        return "400:GECERSIZ_ISTEK"
    if not isinstance(islem, str) or not islem.strip():
        return "400:GECERSIZ_ISTEK"

    yazar = belge.get("yazar")
    belge_birim = belge.get("birim")
    gizlilik = belge.get("gizlilik")
    if (not isinstance(yazar, str) or not yazar.strip() or
            not isinstance(belge_birim, str) or not belge_birim.strip() or
            type(gizlilik) is not int):
        return "400:GECERSIZ_ISTEK"

    if islem not in ("Read", "Update", "Delete"):
        return "400:GECERSIZ_ISLEM"

    if kullanici.get("kimlik_dogrulandi") is not True:
        return "401:OTURUM_YOK"
    ad = kullanici.get("ad")
    if not isinstance(ad, str) or not ad.strip():
        return "401:OTURUM_YOK"

    if kullanici.get("askida") is True:
        return "403:ASKIDA_RET"

    birim = kullanici.get("birim")
    ayni_birim = isinstance(birim, str) and birim == belge_birim
    roller = kullanici.get("roller")
    if not isinstance(roller, list):
        roller = []

    if islem == "Read":
        if ad == yazar or (ayni_birim and gizlilik <= 2):
            return "200:IZIN_VERILDI"
    elif islem == "Update":
        if (ad == yazar and gizlilik < 3) or ("Admin" in roller and ayni_birim and gizlilik <= 3):
            return "200:IZIN_VERILDI"
    elif islem == "Delete":
        if "SuperUser" in roller and ayni_birim and gizlilik <= 3:
            return "200:IZIN_VERILDI"

    return "403:YETKISIZ"
```

```hint
Önce girdi doğrulamasını (`type(gizlilik) is not int`), işlem adını (`"Read"`, `"Update"`, `"Delete"`), oturum durumunu ve `askida is True` (`"403:ASKIDA_RET"`) kontrolünü sırayla uygula; ardından her işlem için yazar/birim/gizlilik eşiklerini karşılaştır.
```
:::
