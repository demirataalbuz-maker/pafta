---
id: cs09
title: ASP.NET Core · Ara Katman (Middleware), Denetleyiciler ve Yetki
summary: ASP.NET Core ara katman boru hattı (await next), [ApiController] yönlendirme öznitelikleri ve [Authorize] / [AllowAnonymous] önceliği.
---

::: anlat Ara katman (*Middleware*) boru hattı ve `await next()`
ASP.NET Core'da gelen her HTTP isteği sırayla **ara katman** (*middleware*) zincirinden geçer (`app.Use(...)`):
- Bir ara katman **`await next()`** çağırdığında istek bir sonraki katmana (ve en sonunda denetleyiciye) ilerler; denetleyici bittiğinde akış **ters sırayla** (`next()` satırının altına) geri döner!
- Bir ara katman **`await next()` çağırmadan** `return` ederse boru hattı **kısa devre** (*short-circuit*) yapar ve sonraki katmanlar çalışmaz.
- Ancak `context.Response.StatusCode = 401;` yazıp **`return;` unutularak** `await next()` çağrılırsa (tıpkı Java Servlet filtrelerinde olduğu gibi) yetkisiz istek denetleyiciye ulaşır!

```csharp
using System;
using System.Collections.Generic;

class AraKatmanZinciri
{
    static void Calistir(bool anahtarTamam, List<string> iz)
    {
        iz.Add("Gunluk:Giris");
        if (!anahtarTamam)
        {
            iz.Add("Yetki:401_KisaDevre");
            iz.Add("Gunluk:Cikis");
            return;                               #! kısa devre: denetleyiciye gitmez!
        }
        iz.Add("Yetki:Gecti");
        iz.Add("Denetleyici:200");
        iz.Add("Yetki:Donus");
        iz.Add("Gunluk:Cikis");
    }

    static void Main()
    {
        var iz = new List<string>();
        Calistir(false, iz);
        Console.WriteLine(string.Join(" -> ", iz));
    }
}
```
:::

::: anlat `[ApiController]`, yönlendirme ve `[Authorize]` vs `[AllowAnonymous]`
ASP.NET Core denetleyicilerinde (*Controllers*) yönlendirme ve yetkilendirme **özniteliklerle** (*attributes*, `[...]`) bildirilir:
- **`[Route("api/[controller]")]`:** Sınıf adı `BiletlerController` ise `Controller` سون eki atılır ve taban yol **`/api/biletler`** (büyük-küçük harf duyarsız) olur.
- **`[HttpGet("{id:int}")]` / `[HttpPost("ara")]`:** HTTP yöntemini ve alt yolu belirler.
- **`[FromQuery]`, `[FromRoute]`, `[FromBody]`, `[FromHeader(Name = "X-Hedef")]`:** Parametrenin isteğin neresinden okunacağını belirtir.
- **`[Authorize]` ve `[AllowAnonymous]` önceliği:**
  1. Eylem (*action*) veya sınıf üzerinde **`[AllowAnonymous]`** varsa **`[Authorize]` tamamen geçersiz kılınır** (oturumsuz erişime açılır!).
  2. Sınıf üzerinde `[Authorize(Roles = "admin,operator")]` ve eylem üzerinde ayrıca `[Authorize(Roles = "denetci")]` varsa, her iki `[Authorize]` birlikte (**VE** / kesişim olarak!) uygulanır: kullanıcının hem sınıfın hem de eylemin şartını sağlaması gerekir!

```csharp
// [Route("api/[controller]")]
// [Authorize(Roles = "admin,operator")]
// public class RaporlarController : ControllerBase
// {
//     [HttpGet("acik")]
//     [AllowAnonymous]                          // sınıfın [Authorize] şartını ezer -> herkese açık!
//     public IActionResult AcikOzet() => Ok();
//
//     [HttpDelete("{id:int}")]
//     [Authorize(Roles = "admin")]              // hem (admin VEYA operator) hem de (admin) olmalı!
//     public IActionResult Sil(int id) => NoContent();
// }
```

> [!GÜVENLİK]
> Kod okurken bir denetleyici sınıfının tepesinde `[Authorize]` görmek tüm uç noktaların korunduğu anlamına gelmez: alt metotlardan birine hata ayıklama sırasında eklenip unutulmuş bir `[AllowAnonymous]` o uç noktayı tamamen kimlik doğrulamasız bırakır!
:::

::: tahmin
```csharp
using System;
using System.Collections.Generic;

class Tahmin
{
    static void KatmanA(bool kisaDevre, Action sonraki, List<string> iz)
    {
        iz.Add("A:giris");
        sonraki();
        iz.Add("A:cikis");
    }

    static void KatmanB(bool kisaDevre, Action sonraki, List<string> iz)
    {
        iz.Add("B:giris");
        if (kisaDevre)
        {
            iz.Add("B:403");
            return;
        }
        sonraki();
        iz.Add("B:cikis");
    }

    static string BoruHatti(bool kisaDevre)
    {
        var iz = new List<string>();
        KatmanA(kisaDevre, () =>
            KatmanB(kisaDevre, () =>
                iz.Add("Hedef:200"), iz), iz);
        return string.Join(",", iz);
    }

    static void Main()
    {
        Console.WriteLine(BoruHatti(false));
        Console.WriteLine(BoruHatti(true));
    }
}
```

```gercek
A:giris,B:giris,Hedef:200,B:cikis,A:cikis
A:giris,B:giris,B:403,A:cikis
```

???

`A:giris,B:giris,Hedef:200,B:cikis,A:cikis` ve `A:giris,B:giris,B:403,A:cikis`. `kisaDevre` `false` olduğunda istek `KatmanA` → `KatmanB` → `Hedef:200` sırasıyla içeri girer ve `B:cikis` → `A:cikis` sırasıyla geri çıkar. `kisaDevre` `true` olduğunda `KatmanB` içinde `sonraki()` çağrılmadan `return` edilir; bu yüzden `Hedef:200` ve `B:cikis` hiç çalışmaz ama `KatmanA`'nın `sonraki()` çağrısı tamamlandığı için `A:cikis` yine çalışır!
:::

::: gorev ASP.NET Core `[Authorize]` ve `[AllowAnonymous]` yetki çözümleyici
Bir ASP.NET Core denetleyici eyleminin yetki kurallarını değerlendiren `eylem_yetkisi(sinif_etiketleri, eylem_etiketleri, kullanici_rolleri)` fonksiyonunu Python'da yaz:
- `sinif_etiketleri` ve `eylem_etiketleri`: `["AllowAnonymous"]`, `["Authorize"]` veya `["Authorize:admin,operator"]` gibi metin listeleridir.
- `kullanici_rolleri`: `None` (oturum açmamış / anonim kullanıcı) veya `{"operator", "okuyucu"}` gibi küme/listedir.
- Kurallar:
  1. Sınıf veya eylem etiketlerinden **herhangi birinde** `"AllowAnonymous"` varsa kimlik doğrulama aranmaz, doğrudan `"200:ACIK"` döner.
  2. Sınıf ve eylemdeki tüm `"Authorize..."` etiketleri toplanır. Hiç `"Authorize..."` etiketi yoksa `"200:ACIK"` döner.
  3. En az bir `"Authorize..."` etiketi varsa ve `kullanici_rolleri is None` ise `"401:OTURUM_YOK"` döner.
  4. Her `"Authorize:rol1,rol2"` etiketi için, kullanıcının rollerinden (`kullanici_rolleri`) **en az biri** o etiketin izin verdiği roller arasında (büyük-küçük harf duyarsız) bulunmalıdır (birden fazla `"Authorize:..."` etiketi varsa hepsini ayrı ayrı sağlamalıdır!). Sağlamıyorsa `"403:YETKISIZ"`, sağlıyorsa `"200:YETKILI"` döner. (Yalnızca `"Authorize"` yazıyorsa herhangi bir oturum açmış kullanıcı yeterlidir.)

```starter
def eylem_yetkisi(sinif_etiketleri, eylem_etiketleri, kullanici_rolleri):
    return "200:ACIK"
```

```test
need("eylem_yetkisi")
eq(eylem_yetkisi(["Authorize:admin"], ["AllowAnonymous"], None),
   "200:ACIK", "eylemdeki AllowAnonymous sınıfın Authorize kuralını ezer")
eq(eylem_yetkisi([], [], None), "200:ACIK", "hiç Authorize yoksa anonim kullanıcıya da 200:ACIK")
eq(eylem_yetkisi(["Authorize"], [], None), "401:OTURUM_YOK", "Authorize varken kullanıcı None ise 401:OTURUM_YOK")
eq(eylem_yetkisi(["Authorize"], [], ["izleyici"]), "200:YETKILI", "rol şartsız Authorize için oturum açmış olmak yeterli")
eq(eylem_yetkisi(["Authorize:admin,operator"], ["Authorize:denetci"], ["operator"]),
   "403:YETKISIZ", "sınıf şartı (operator) sağlansa bile eylem şartı (denetci) sağlanmadığı için 403:YETKISIZ")
eq(eylem_yetkisi(["Authorize:admin,operator"], ["Authorize:denetci"], ["Operator", "Denetci"]),
   "200:YETKILI", "hem sınıf hem eylem Authorize şartı sağlandığında 200:YETKILI")
```

```solution
def eylem_yetkisi(sinif_etiketleri, eylem_etiketleri, kullanici_rolleri):
    tum_etiketler = list(sinif_etiketleri) + list(eylem_etiketleri)
    if "AllowAnonymous" in tum_etiketler:
        return "200:ACIK"
    auth_etiketleri = [e for e in tum_etiketler if e == "Authorize" or e.startswith("Authorize:")]
    if not auth_etiketleri:
        return "200:ACIK"
    if kullanici_rolleri is None:
        return "401:OTURUM_YOK"
    sahip_roller = {r.strip().lower() for r in kullanici_rolleri}
    for etiket in auth_etiketleri:
        if etiket.startswith("Authorize:"):
            izinli = {r.strip().lower() for r in etiket.split(":", 1)[1].split(",") if r.strip()}
            if not (sahip_roller & izinli):
                return "403:YETKISIZ"
    return "200:YETKILI"
```

```hint
Önce `"AllowAnonymous" in tum_etiketler` kontrolünü yap. Ardından her `"Authorize:..."` etiketi için `sahip_roller & izinli` kesişiminin boş olup olmadığını denetle.
```
:::

::: gorev `[Route("api/[controller]")]` ve `[HttpGet]` şablon eşleştirici
ASP.NET Core'da bir denetleyici sınıfının adı (ör. `"BiletlerController"`) ve eylem şablonu (ör. `"{id:int}"`) birleştirilerek URL yolu oluşturulur:
- Sınıf adının sonundaki `"Controller"` soneki (büyük-küçük harf duyarsız) kaldırılır ve küçük harfe çevrilir (`"BiletlerController"` → `"biletler"`).
- Taban yol `f"/api/{denetleyici_koku}"` olur.
- `eylem_sablonu` boş değilse taban yola `"/" + eylem_sablonu.strip("/")` eklenir.
- Gelen `istek_yolu` ile şablon parça parça (`"/"` ile bölünerek) karşılaştırılır:
  - `"{ad:int}"` biçimindeki şablon parçası yalnızca tam sayı (`+-` işaretli veya işaretsiz rakamlar) kabul eder ve parametre sözlüğüne `int` olarak kaydedilir.
  - `"{ad}"` biçimindeki şablon parçası boş olmayan herhangi bir metin parçasını `str` olarak kaydeder.
  - Sabit parçalar büyük-küçük harf duyarsız karşılaştırılır.
- Eşleşirse `("ESLESTI", parametre_sozlugu)`, eşleşmezse `("ESLESMEDI", {})` döndür.

Python'da `rota_eslestir(sinif_adi, eylem_sablonu, istek_yolu)` fonksiyonunu yaz.

```starter
def rota_eslestir(sinif_adi, eylem_sablonu, istek_yolu):
    return "ESLESMEDI", {}
```

```test
need("rota_eslestir")
eq(rota_eslestir("BiletlerController", "{id:int}", "/API/biletler/42"),
   ("ESLESTI", {"id": 42}),
   "Controller soneki atılmalı, büyük-küçük harf duyarsız eşleşmeli ve :int tam sayıya çevrilmeli")
eq(rota_eslestir("BiletlerController", "{id:int}", "/api/biletler/kirkiki"),
   ("ESLESMEDI", {}),
   "{id:int} sayı olmayan parçayı reddetmeli")
eq(rota_eslestir("SunucularController", "{bolge}/durum", "/api/sunucular/eu-west/durum"),
   ("ESLESTI", {"bolge": "eu-west"}),
   "{bolge} metin parametresi olarak alınmalı")
eq(rota_eslestir("Saglik", "", "/api/saglik"),
   ("ESLESTI", {}),
   "Controller soneki olmayan sınıfta doğrudan sınıf adı kullanılmalı ve boş eylem şablonu /api/saglik olmalı")
eq(rota_eslestir("SaglikController", "detay", "/api/saglik/detay/fazla"),
   ("ESLESMEDI", {}),
   "parça sayısı tutmuyorsa ESLESMEDI dönmeli")
```

```solution
import re

def rota_eslestir(sinif_adi, eylem_sablonu, istek_yolu):
    kok = sinif_adi[:-10].lower() if sinif_adi.lower().endswith("controller") else sinif_adi.lower()
    tam_sablon = f"/api/{kok}"
    ek = eylem_sablonu.strip("/")
    if ek:
        tam_sablon += "/" + ek

    sablon_p = [p for p in tam_sablon.strip("/").split("/") if p]
    istek_p = [p for p in istek_yolu.strip("/").split("/") if p]
    if len(sablon_p) != len(istek_p):
        return "ESLESMEDI", {}

    parametreler = {}
    for sp, ip in zip(sablon_p, istek_p):
        if re.fullmatch(r"\{[^{}]+\}", sp):
            ic = sp[1:-1]
            if ":" in ic:
                ad, tur = ic.split(":", 1)
                if tur == "int":
                    if not re.fullmatch(r"[+-]?[0-9]+", ip):
                        return "ESLESMEDI", {}
                    parametreler[ad] = int(ip)
            else:
                parametreler[ic] = ip
        else:
            if sp.lower() != ip.lower():
                return "ESLESMEDI", {}
    return "ESLESTI", parametreler
```

```hint
`sinif_adi.lower().endswith("controller")` ise son 10 karakteri (`sinif_adi[:-10]`) kes. Şablon parçalarını ve istek parçalarını `zip` ile eşleştirip `{ad:int}` kısıtlamasını `re.fullmatch(r"[+-]?[0-9]+", ip)` ile doğrula.
```
:::
