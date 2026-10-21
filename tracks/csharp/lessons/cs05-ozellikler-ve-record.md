---
id: cs05
title: Özellikler (get/set/init), record ve Desen Eşleme
summary: C# otomatik özellikleri, init erişimcisi, record değer eşitliği, with ifadesi ve switch özellik desenleri.
---

::: anlat Özellikler (`get`, `set`, `init`) ve aşırı bağlama (Over-posting)
Java'da `getRol()` / `setRol(v)` metotları yazılırken, C#'ta **özellikler** (*properties*) birinci sınıf dil yapısıdır:
- **`public string Rol { get; set; } = "okuyucu";`** — hem okunabilir hem her zaman değiştirilebilir.
- **`public string Rol { get; private set; }`** — dışarıdan okunabilir ama yalnızca sınıfın kendi içinden değiştirilebilir!
- **`public string Rol { get; init; }`** (C# 9+) — yalnızca nesne oluşturulurken (`new Kullanici { Rol = ... }` veya kurucu içinde) atanabilir; sonrasında salt okunurdur.
- **`public bool YoneticiMi => Rol == "admin";`** — yalnızca okunan hesaplanan özellik (*expression-bodied property*).

```csharp
using System;

class Hesap
{
    public string Ad { get; init; } = "";
    public string Rol { get; private set; } = "okuyucu";  #! dışarıdan set edilemez!
    public bool Aktif { get; set; } = true;

    public void TerfiEttir() => Rol = "denetci";
}

class OzellikOrnek
{
    static void Main()
    {
        var h = new Hesap { Ad = "ali", Aktif = true };
        Console.WriteLine(h.Ad + ":" + h.Rol);            #! ali:okuyucu
        h.TerfiEttir();
        Console.WriteLine(h.Rol);                         #! denetci
    }
}
```

> [!GÜVENLİK]
> ASP.NET Core model bağlayıcısı gelen JSON gövdesini bir sınıfa bağlarken **`public set`** veya **`public init`** erişimcisi olan tüm özellikleri doldurur! Eğer `Rol` özelliği `private set` yerine `public set` veya `public init` bırakılmışsa ve doğrudan girdi modeli olarak kullanılıyorsa istemci JSON içine `"rol": "admin"` ekleyerek yetki yükseltebilir (*mass assignment / over-posting*).
:::

::: anlat `record`, `with` ifadesi ve `switch` özellik deseni
C# 9+ **`record`** türü, değişmez (*immutable*) veri taşıyıcıları için tasarlanmıştır:
1. **`==` ve `.Equals()` değer bazlıdır:** İki ayrı `record` nesnesinin tüm alanları eşitse `r1 == r2` sonucu **`true`** olur (normal `class` için `false` olurdu).
2. **`with` ifadesi:** Mevcut bir kaydı bozmadan belirli özelliklerini değiştirerek yeni bir kopya üretir (`var r2 = r1 with { Seviye = 2 };`).
3. **Özellik desen eşleme (*property pattern matching*):** `switch` ifadesinde nesnenin alanlarına ve aralıklarına göre doğrudan eşleme yapılabilir (`{ Rol: "admin", Aktif: true } => ...`).

```csharp
using System;

public record Oturum(string Kullanici, string Rol, int RiskPuani);

class DesenOrnek
{
    static string KararVer(Oturum? o) => o switch
    {
        null => "OTURUM_YOK",
        { RiskPuani: >= 80 } => "BLOKLA",
        { Rol: "admin", RiskPuani: < 30 } => "TAM_YETKI",
        { Rol: "admin" } => "IKINCI_FAKTOR",
        _ => "STANDART"
    };

    static void Main()
    {
        var o1 = new Oturum("ali", "admin", 15);
        var o2 = o1 with { RiskPuani = 50 };              #! o1 değişmez, yeni kopya üretilir

        Console.WriteLine(o1 == new Oturum("ali", "admin", 15)); #! True (record değer eşitliği)
        Console.WriteLine(KararVer(o1));                  #! TAM_YETKI
        Console.WriteLine(KararVer(o2));                  #! IKINCI_FAKTOR
    }
}
```
:::

::: tahmin
```csharp
using System;

public record Bilet(string Sunucu, string Durum, int Oncelik);

class Tahmin
{
    static string Sifrele(Bilet b) => b switch
    {
        { Durum: "kapali" } => "ARSIV",
        { Oncelik: >= 4, Durum: "acik" } => "ACIL:" + b.Sunucu,
        { Oncelik: >= 2 } => "NORMAL:" + b.Sunucu,
        _ => "DUSUK:" + b.Sunucu
    };

    static void Main()
    {
        var b1 = new Bilet("web01", "acik", 4);
        var b2 = b1 with { Oncelik = 3 };
        var b3 = b1 with { Durum = "kapali", Oncelik = 5 };

        Console.WriteLine(b1 == new Bilet("web01", "acik", 4));
        Console.WriteLine(Sifrele(b1));
        Console.WriteLine(Sifrele(b2));
        Console.WriteLine(Sifrele(b3));
    }
}
```

```gercek
True
ACIL:web01
NORMAL:web01
ARSIV
```

???

`True`, `ACIL:web01`, `NORMAL:web01`, `ARSIV`. `Bilet` bir `record` olduğu için aynı alan değerlerine sahip iki örnek `==` ile karşılaştırıldığında `True` döner. `b1` için `Oncelik: 4` (`>= 4`) ve `Durum: "acik"` olduğundan ikinci kol eşleşir ve `ACIL:web01` üretir. `b2` `with { Oncelik = 3 }` ile kopyalandığı için üçüncü kola (`Oncelik: >= 2`) düşer ve `NORMAL:web01` verir. `b3` ise `Oncelik = 5` olmasına rağmen `switch` kolları **yukarıdan aşağıya** denendiği için ilk kol (`{ Durum: "kapali" }`) eşleşir ve `ARSIV` döner.
:::

::: gorev C# özellik erişimcilerine (`set` / `init` / `private set`) göre model bağlayıcı
Bir ASP.NET Core uç noktasında JSON gövdesinin bir C# sınıfına bağlanmasını Python'da `model_bagla(ozellik_tanimlari, gelen_json)` fonksiyonu olarak simüle et:
- `ozellik_tanimlari`, `{"Ad": ("set", "misafir"), "Rol": ("private set", "okuyucu"), "Departman": ("init", "genel"), "YoneticiMi": ("get", False)}` biçiminde `{ozellik_adi: (erisimci, varsayilan_deger)}` sözlüğüdür.
- Başlangıçta sonuç sözlüğü tüm özelliklerin varsayılan değerlerini içerir (`"get"` salt okunur hesaplanan özellikler hariç: `"get"` olanlar sonuçta yer almaz).
- `gelen_json` sözlüğündeki anahtarlar büyük-küçük harf duyarsız olarak eşleştirilir; ancak yalnızca erişimcisi **`"set"`** veya **`"init"`** olan özellikler dış JSON verisiyle güncellenebilir (`"private set"` olanlar dışarıdan değiştirilemez, varsayılan değerinde kalır!).

```starter
def model_bagla(ozellik_tanimlari, gelen_json):
    return {k: v[1] for k, v in ozellik_tanimlari.items()}
```

```test
need("model_bagla")
tanim = {
    "KullaniciAdi": ("set", "misafir"),
    "Departman": ("init", "genel"),
    "Rol": ("private set", "okuyucu"),
    "Aktif": ("set", True),
    "Etiket": ("get", "MISAFIR"),
}
eq(model_bagla(tanim, {"kullaniciadi": "ali", "DEPARTMAN": "SOC", "rol": "admin", "bilinmeyen": 1}),
   {"KullaniciAdi": "ali", "Departman": "SOC", "Rol": "okuyucu", "Aktif": True},
   "set ve init güncellenmeli, private set ('Rol') korunmalı, get ('Etiket') ve bilinmeyen alanlar dışarıda kalmalı")
eq(model_bagla(tanim, {}),
   {"KullaniciAdi": "misafir", "Departman": "genel", "Rol": "okuyucu", "Aktif": True},
   "boş JSON geldiğinde varsayılanlar korunmalı")
```

```solution
def model_bagla(ozellik_tanimlari, gelen_json):
    gelen_kucuk = {k.lower(): v for k, v in gelen_json.items()}
    sonuc = {}
    for ad, (erisimci, varsayilan) in ozellik_tanimlari.items():
        if erisimci == "get":
            continue
        if erisimci in ("set", "init") and ad.lower() in gelen_kucuk:
            sonuc[ad] = gelen_kucuk[ad.lower()]
        else:
            sonuc[ad] = varsayilan
    return sonuc
```

```hint
`erisimci == "get"` olanları atla; `erisimci in ("set", "init")` ise ve `ad.lower()` gelen JSON anahtarlarında varsa yeni değeri, aksi hâlde `varsayilan` değeri yaz.
```
:::

::: gorev C# `switch` özellik deseniyle erişim kararı
Aşağıdaki C# `switch` ifadesinin ürettiği kararı birebir döndüren `erisim_karari(istek)` fonksiyonunu Python'da yaz. `istek` değeri `None` veya `{"rol": str, "aktif": bool, "risk": int, "bolge": str}` sözlüğüdür.

```csharp
public static string ErisimKarari(Istek? istek) => istek switch
{
    null => "RED:BOS",
    { Aktif: false } => "RED:PASIF",
    { Risk: >= 90 } => "RED:YUKSEK_RISK",
    { Rol: "admin", Risk: <= 20, Bolge: "TR" } => "KABUL:TAM_YETKI",
    { Rol: "admin", Risk: <= 50 } => "KABUL:MFA_GEREKLI",
    { Rol: "operator", Risk: < 40 } => "KABUL:OPERATOR",
    _ => "RED:YETKISIZ"
};
```

```starter
def erisim_karari(istek):
    if istek is None:
        return "RED:BOS"
    return "RED:YETKISIZ"
```

```test
need("erisim_karari")
eq(erisim_karari(None), "RED:BOS", "null -> RED:BOS")
eq(erisim_karari({"rol": "admin", "aktif": False, "risk": 0, "bolge": "TR"}), "RED:PASIF", "Aktif: false ilk sırada yakalanmalı")
eq(erisim_karari({"rol": "admin", "aktif": True, "risk": 90, "bolge": "TR"}), "RED:YUKSEK_RISK", "Risk=90 (>= 90) -> RED:YUKSEK_RISK")
eq(erisim_karari({"rol": "admin", "aktif": True, "risk": 20, "bolge": "TR"}), "KABUL:TAM_YETKI", "admin, Risk=20 (<= 20), TR -> KABUL:TAM_YETKI")
eq(erisim_karari({"rol": "admin", "aktif": True, "risk": 21, "bolge": "TR"}), "KABUL:MFA_GEREKLI", "admin, Risk=21 (> 20 ve <= 50) -> KABUL:MFA_GEREKLI")
eq(erisim_karari({"rol": "admin", "aktif": True, "risk": 10, "bolge": "EU"}), "KABUL:MFA_GEREKLI", "admin, Risk=10 ama Bolge!=TR -> bir alt kola (MFA_GEREKLI) düşer")
eq(erisim_karari({"rol": "admin", "aktif": True, "risk": 50, "bolge": "EU"}), "KABUL:MFA_GEREKLI", "admin, Risk=50 (<= 50) -> KABUL:MFA_GEREKLI")
eq(erisim_karari({"rol": "admin", "aktif": True, "risk": 51, "bolge": "TR"}), "RED:YETKISIZ", "admin, Risk=51 (> 50 ve < 90) -> RED:YETKISIZ")
eq(erisim_karari({"rol": "operator", "aktif": True, "risk": 39, "bolge": "TR"}), "KABUL:OPERATOR", "operator, Risk=39 (< 40) -> KABUL:OPERATOR")
eq(erisim_karari({"rol": "operator", "aktif": True, "risk": 40, "bolge": "TR"}), "RED:YETKISIZ", "operator, Risk=40 (< 40 değil) -> RED:YETKISIZ")
```

```solution
def erisim_karari(istek):
    if istek is None:
        return "RED:BOS"
    if not istek["aktif"]:
        return "RED:PASIF"
    risk = istek["risk"]
    rol = istek["rol"]
    bolge = istek["bolge"]
    if risk >= 90:
        return "RED:YUKSEK_RISK"
    if rol == "admin" and risk <= 20 and bolge == "TR":
        return "KABUL:TAM_YETKI"
    if rol == "admin" and risk <= 50:
        return "KABUL:MFA_GEREKLI"
    if rol == "operator" and risk < 40:
        return "KABUL:OPERATOR"
    return "RED:YETKISIZ"
```

```hint
C# `switch` kolları yukarıdan aşağıya sırayla denenir. Sınır değerlerine (`>= 90`, `<= 20`, `<= 50`, `< 40`) özellikle dikkat et.
```
:::
