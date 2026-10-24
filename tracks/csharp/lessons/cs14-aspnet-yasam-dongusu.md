---
id: cs14
title: Klasik ASP.NET · Uygulama Hattı ve Sayfa Yaşam Döngüsü
summary: ASP.NET Core bilgisini eski System.Web uygulamalarına yanlış taşımamak: Global.asax'taki HttpApplication olayları, Web Forms sayfa yaşam döngüsü (PreInit'ten Unload'a), postback ve IsPostBack, ViewState'in PreLoad'dan önce geri yüklenmesi, kontrol olaylarının Load ile LoadComplete arasında çalışması, ViewState MAC doğrulaması ve web.config. Çıktılar .NET Framework'ün gerçek System.Web'inden.
---

::: anlat Eski kod tabanındaki hat
Kurumsal uygulamaların önemli bir kısmı hâlâ **klasik ASP.NET** (System.Web, .NET Framework) üzerinde çalışır: Web Forms sayfaları (`.aspx`), `Global.asax` ve `web.config`. CS11–CS13'teki ASP.NET Core bilgisi burada yanıltıcı olabilir: ara katman zinciri yoktur, onun yerine **olaylar** vardır.

Bu dersteki her çıktı gerçektir. `tracks/csharp/aspnet_lab/` altındaki sayfalar Windows'taki .NET Framework 4.x'in kendi `System.Web`'iyle, IIS olmadan, süreç içinde çalıştırıldı (`ApplicationHost` ve `HttpRuntime.ProcessRequest`). Aynı çıktıyı `python tools/aspnet_yasam_dongusu.py GET:Sayfa.aspx TIKLA:Sayfa.aspx` ile kendin üretebilirsin.

Bir istek önce **uygulama hattından** geçer. `Global.asax`'ta `Application_<Olay>` adıyla yazılan işleyiciler bu sırayla çalışır (ölçülen sıra):

```csharp
void Application_BeginRequest(object s, EventArgs e)              { /* 1 */ }
void Application_AuthenticateRequest(object s, EventArgs e)       { /* 2: kim? */ }
void Application_AuthorizeRequest(object s, EventArgs e)          { /* 3: izinli mi? */ }
void Application_PreRequestHandlerExecute(object s, EventArgs e)  { /* 4: işleyici (sayfa) başlamak üzere */ }
// ... sayfanın bütün yaşam döngüsü burada ...
void Application_PostRequestHandlerExecute(object s, EventArgs e) { /* 5 */ }
void Application_EndRequest(object s, EventArgs e)                { /* 6 */ }
```

| ASP.NET Core | Klasik ASP.NET |
|---|---|
| `Program.cs`'te kayıtlı ara katman sırası | `Global.asax` olayları ve `web.config`'teki `httpModules` |
| `app.UseAuthentication()` | `AuthenticateRequest` olayı (FormsAuthentication modülü) |
| `appsettings.json` | `web.config` (`<system.web>`, `<appSettings>`, `<authorization>`) |
| Razor Pages / MVC | Web Forms sayfası ve sunucu kontrolleri |

`web.config`'teki `<authorization>` kuralları ve `<pages enableViewStateMac>` gibi ayarlar, kodu hiç değiştirmeden davranışı değiştirir; klasik bir uygulamayı incelerken ilk okunacak dosyadır.

Kaynak: [ASP.NET uygulama yaşam döngüsü](https://learn.microsoft.com/en-us/previous-versions/aspnet/bb470252(v=vs.100)), [Sayfa yaşam döngüsü](https://learn.microsoft.com/en-us/previous-versions/aspnet/ms178472(v=vs.100)).
:::

::: anlat Sayfa yaşam döngüsü ve postback
Bir Web Forms sayfası her istekte **sıfırdan** kurulur ve aynı olay dizisinden geçer. Düğmeye basmak, sayfanın formunu aynı adrese geri göndermektir: **postback**. Formun gizli `__VIEWSTATE` alanı, kontrollerin önceki istekteki durumunu taşır. Ölçülen sıra, bir sayaç etiketi ve bir "Arttır" düğmesi olan sayfa için:

| Olay | İlk istek (GET) | Postback (düğmeye basıldı) |
|---|---|---|
| `PreInit` | ✓ (`IsPostBack` yanlış) | ✓ (`IsPostBack` doğru) |
| `Init`, `InitComplete` | ✓ | ✓ |
| *ViewState geri yüklenir* | — | **burada**: kontroller önceki değerine döner |
| `PreLoad` | sayaç 0 | sayaç önceki değer |
| `Load` | ✓ | ✓ |
| *kontrol olayları* (`Click`) | — | **burada**: Load'dan sonra |
| `LoadComplete`, `PreRender` | ✓ | ✓ |
| *ViewState kaydedilir* (`SaveStateComplete`) | ✓ | ✓ |
| `Render`, `Unload` | ✓ | ✓ |

İki sonuç, klasik Web Forms hatalarının çoğunu açıklar:

- **Kontrol olayları `Load`'dan sonra çalışır.** `Page_Load`'da yapılan bir şey, düğmenin işleyicisinden **önce** olur.
- **ViewState `PreLoad`'dan önce yüklenir.** `Page_Load`'da bir kontrole değer atarsan, ViewState'ten gelen değeri ezersin. Bu yüzden ilk değerler `if (!IsPostBack) { ... }` içinde verilir.

`tracks/csharp/aspnet_lab/Hatali.aspx` bu hatayı içerir: `Page_Load`'da koşulsuz `sayac.Text = "0"`. Ölçülen sonuç: GET 0, birinci tıklama 1, ikinci tıklama **yine 1**. `Sayfa.aspx`'te (`if (!IsPostBack)`) sonuç 0, 1, 2'dir.

> [!GÜVENLİK]
> ViewState istemcide durur; kullanıcı onu değiştirebilir. `enableViewStateMac` (varsayılan ve .NET 4.5.2'den beri kapatılamaz) ViewState'i sunucunun `machineKey`'iyle imzalar: değiştirilmiş bir ViewState sayfaya ulaşmadan reddedilir. Ölçüldü: son altı karakteri değiştirilmiş ViewState'le gelen postback `Validation of viewstate MAC failed` hatası verdi. İmza bütünlüğü korur ama içeriği gizlemez; ViewState'e gizli veri koyma. `machineKey`'in sızması ise imzanın hiçbir şey korumaması demektir; `web.config`'te açık metin bir `machineKey` incelemede kritik bulgudur.
:::

::: tahmin Hatalı sayfada ikinci tıklama
`Hatali.aspx`'in ilgili kısmı aşağıda. Sayfa bir kez açıldı (GET), düğmeye bir kez basıldı (sayaç 1 gösterdi) ve şimdi **ikinci kez** basılıyor. Bu postback'in olay günlüğünde ilk altı satır ne yazar?

```csharp
// Hatali.aspx — her olay günlüğe bir satır yazar; postback'te sonuna " (postback)" ekler
protected override void OnPreLoad(EventArgs e) { Yaz("PreLoad sayac=" + sayac.Text); base.OnPreLoad(e); }
protected override void OnLoad(EventArgs e)    { sayac.Text = "0"; Yaz("Load sayac=" + sayac.Text); base.OnLoad(e); }
protected void Tikla(object s, EventArgs e)    { sayac.Text = (int.Parse(sayac.Text) + 1).ToString(); Yaz("Click sayac=" + sayac.Text); }
// PreInit, Init, InitComplete, LoadComplete, ... da günlüğe yazar
```

```gercek
PreInit (postback)
Init (postback)
InitComplete (postback)
PreLoad sayac=1 (postback)
Load sayac=0 (postback)
Click sayac=1 (postback)
```

???

```text
PreInit (postback)
Init (postback)
InitComplete (postback)
PreLoad sayac=1 (postback)
Load sayac=0 (postback)
Click sayac=1 (postback)
```

Bu, `python tools/aspnet_yasam_dongusu.py GET:Hatali.aspx TIKLA:Hatali.aspx TIKLA:Hatali.aspx` çıktısındaki son postback'in ilk altı satırıdır. ViewState `PreLoad`'dan önce geri yüklendiği için `PreLoad` sayacı önceki istekteki 1 olarak görür. `Load` onu koşulsuz 0'a çeker; `Click` ondan sonra çalışır ve 1 yapar. Kullanıcı ne kadar basarsa bassın sayaç 1'de kalır.
:::

::: gorev Olay sırası
`olaylar(postback, tiklandi)` fonksiyonunu yaz: bir Web Forms sayfasında çalışan sayfa olaylarının adlarını, gerçek sırasıyla bir liste olarak döndürsün. Olay adları: `PreInit`, `Init`, `InitComplete`, `PreLoad`, `Load`, `Click`, `LoadComplete`, `PreRender`, `SaveStateComplete`, `Render`, `Unload`.

- `Click` yalnız **postback'te** ve düğmeye basıldıysa (`tiklandi`) vardır. İlk istekte (GET) düğme olayı çalışmaz.
- Argümanlar `bool` değilse `TypeError`.

Testler, `tools/aspnet_yasam_dongusu.py`'nin gerçek System.Web'den aldığı günlüklerle karşılaştırır.

```starter
def olaylar(postback, tiklandi):
    sira = ["PreInit", "Init", "InitComplete", "PreLoad", "Load", "LoadComplete",
            "PreRender", "SaveStateComplete", "Render", "Unload"]
    if tiklandi:
        sira.append("Click")
    return sira
```

```test
f = need("olaylar")
GET = ["PreInit", "Init", "InitComplete", "PreLoad", "Load", "LoadComplete", "PreRender", "SaveStateComplete", "Render", "Unload"]
TIK = ["PreInit", "Init", "InitComplete", "PreLoad", "Load", "Click", "LoadComplete", "PreRender", "SaveStateComplete", "Render", "Unload"]
eq(f(False, False), GET, "ilk istek: gerçek günlükteki on olay")
eq(f(True, True), TIK, "postback ve tıklama: Click, Load ile LoadComplete arasında")
eq(f(True, False), GET, "tıklamasız postback: kontrol olayı yok")
eq(f(False, True), GET, "GET'te düğme olayı çalışmaz")
ok(f(True, True) is not f(True, True), "her çağrı yeni bir liste")
for kotu in ((1, True), (True, "evet"), (None, False)):
    raises(TypeError, f, *kotu, msg=f"bool olmayan argüman {kotu!r}")
```

```solution
def olaylar(postback, tiklandi):
    if type(postback) is not bool or type(tiklandi) is not bool:
        raise TypeError("postback ve tiklandi bool olmalı")
    sira = ["PreInit", "Init", "InitComplete", "PreLoad", "Load"]
    if postback and tiklandi:
        sira.append("Click")
    sira += ["LoadComplete", "PreRender", "SaveStateComplete", "Render", "Unload"]
    return sira
```

```hint
Kontrol olayları `Load`'dan sonra, `LoadComplete`'ten önce çalışır. Listeyi iki parça hâlinde kur, araya koşullu olarak `Click` ekle.
```

```hint
`type(x) is bool` 1'i ve "evet"i reddeder; `isinstance(1, bool)` yanlıştır ama `bool` olmayan değerleri bu denetimle açıkça ayırmak daha anlaşılırdır.
```
:::

::: gorev Sayaç ne gösterir?
`sayaclar(istekler, korumali)` fonksiyonunu yaz: ders sayfasının (`sayac` etiketi, "Arttır" düğmesi) her istekten sonra gösterdiği sayaç değerlerini döndürsün.

- `istekler`: `"GET"` (sayfayı yeniden açmak; önceki form durumu yoktur) ya da `"TIKLA"` (son yanıtın formuyla postback ve düğmeye basmak) dizisi.
- `korumali=True`: sayfa `Sayfa.aspx` gibidir, `Page_Load` ilk değeri `if (!IsPostBack)` içinde verir. `korumali=False`: `Hatali.aspx` gibidir, `Page_Load` her istekte `sayac.Text = "0"` yapar.
- Yaşam döngüsünü izle: ViewState geri yüklenir, sonra `Load`, sonra `Click`.
- Hiç GET olmadan gelen bir `"TIKLA"` (geri gönderilecek form yok) ya da tanınmayan bir istek: `ValueError`. Boş liste: `[]`.

Testlerin beklenen değerleri `tools/aspnet_yasam_dongusu.py`'nin gerçek ölçümüdür.

```starter
def sayaclar(istekler, korumali):
    sonuc, sayac = [], 0
    for i in istekler:
        if i == "TIKLA":
            sayac += 1
        sonuc.append(sayac)
    return sonuc
```

```test
f = need("sayaclar")
eq(f(["GET", "TIKLA", "TIKLA"], True), [0, 1, 2], "Sayfa.aspx: ölçülen 0, 1, 2")
eq(f(["GET", "TIKLA", "TIKLA"], False), [0, 1, 1], "Hatali.aspx: ölçülen 0, 1, 1")
eq(f(["GET", "TIKLA", "GET", "TIKLA"], True), [0, 1, 0, 1], "yeniden GET form durumunu sıfırlar")
eq(f(["GET", "GET", "TIKLA", "TIKLA", "TIKLA"], True), [0, 0, 1, 2, 3], "art arda GET ve üç tıklama")
eq(f(["GET"] + ["TIKLA"] * 5, False), [0, 1, 1, 1, 1, 1], "korumasız sayfa kaç kez basılsa 1'de kalır")
eq(f([], True), [], "boş liste")
raises(ValueError, f, ["TIKLA"], True, msg="GET olmadan postback")
raises(ValueError, f, ["GET", "POST"], False, msg="tanınmayan istek")
```

```solution
def sayaclar(istekler, korumali):
    sonuc, gorunum = [], None          # gorunum: son yanıtın ViewState'teki sayaç değeri
    for istek in istekler:
        if istek == "GET":
            sayac = 0                  # Text="0" bildirimi; !IsPostBack de 0 verir
        elif istek == "TIKLA":
            if gorunum is None:
                raise ValueError("geri gönderilecek form yok")
            sayac = gorunum            # ViewState geri yüklenir (PreLoad'dan önce)
            if not korumali:
                sayac = 0              # Page_Load koşulsuz sıfırlar
            sayac += 1                 # Click, Load'dan sonra
        else:
            raise ValueError(f"tanınmayan istek: {istek!r}")
        gorunum = sayac
        sonuc.append(sayac)
    return sonuc
```

```hint
Her `TIKLA` için sırayı aynen uygula: önce önceki yanıtın değerini geri yükle (ViewState), sonra `Load` (korumasızsa 0'a çek), sonra `Click` (+1). Yanıtın değeri bir sonraki postback'in ViewState'i olur.
```

```hint
`GET` yeni bir sayfadır: önceki ViewState yoktur, sayaç bildirimdeki ilk değerle (0) başlar. İlk istek GET değilse geri gönderilecek bir form da yoktur.
```
:::
