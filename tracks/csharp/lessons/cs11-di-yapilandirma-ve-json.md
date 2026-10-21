---
id: cs11
title: Bağımlılık Enjeksiyonu (DI), IConfiguration ve System.Text.Json
summary: AddTransient/AddScoped/AddSingleton yaşam süreleri, IConfiguration ezme sırası ve System.Text.Json seçenekleri.
---

::: anlat Servis yaşam süreleri (`Transient`, `Scoped`, `Singleton`) ve durum sızıntısı
ASP.NET Core'da servisler `Program.cs` içinde **Bağımlılık Enjeksiyonu** (*Dependency Injection — DI*) kapsayıcısına üç farklı yaşam süresiyle kaydedilir:
1. **`AddTransient<T>()`:** Her istendiğinde **yepyeni** bir nesne örneği oluşturulur.
2. **`AddScoped<T>()`:** Her **HTTP isteği başına bir kez** oluşturulur; aynı HTTP isteği içindeki tüm sınıflar aynı örneği paylaşır, istek bitince atılır (`DbContext` varsayılan olarak `Scoped`'dur).
3. **`AddSingleton<T>()`:** Uygulama ayağa kalktığında **tek bir kez** oluşturulur ve sunucu kapanana kadar **tüm kullanıcıların tüm HTTP istekleri** aynı nesneyi paylaşır!

> [!GÜVENLİK]
> **Tutsak Bağımlılık (*Captive Dependency*) ve Oturum Sızıntısı:** Eğer `Singleton` olarak kaydedilmiş bir servisin içinde o anki kullanıcıya ait `KullaniciId` veya `Rol` gibi bir alan tutulursa (ya da `Scoped` bir servis `Singleton` içine gömülürse), bir kullanıcının oturum bilgisi aynı anda istek atan başka bir kullanıcıya sızar!
:::

::: anlat `IConfiguration` öncelik sırası ve `System.Text.Json`
ASP.NET Core'da `IConfiguration` ayarları iki nokta (`"Veritabani:Baglanti"`) ile okunur. Aynı anahtar birden fazla kaynakta tanımlıysa **son yüklenen kaynak öncekini ezer**:
1. `appsettings.json` (en düşük öncelik)
2. `appsettings.{Environment}.json` (ör. `appsettings.Production.json`)
3. Ortam değişkenleri (çift alt çizgi `__` iki noktaya `:` karşılık gelir: `VERITABANI__BAGLANTI`)
4. Komut satırı argümanları (en yüksek öncelik)

JSON serileştirmede ise .NET'in varsayılan kütüphanesi **`System.Text.Json`**'dır (`JsonSerializer.Serialize` / `Deserialize`):
- **`System.Text.Json` varsayılan olarak büyük-küçük harfe DUYARLIDIR!** JSON'daki `"kullaniciAdi"` alanı C# sınıfındaki `public string KullaniciAdi { get; set; }` özelliğine `PropertyNameCaseInsensitive = true` açılmadıkça (veya `[JsonPropertyName("kullaniciAdi")]` yazılmadıkça) **bağlanmaz** (`null` kalır)!
- *(Not: ASP.NET Core Web API denetleyicileri web varsayılanı olarak `PropertyNameCaseInsensitive = true` açar, ancak doğrudan `JsonSerializer.Deserialize<T>(json)` çağrılarında varsayılan `false`'tur!)*

```csharp
using System;
using System.Text.Json;
using System.Text.Json.Serialization;

class AyarDto
{
    public string? Ortam { get; set; }
    [JsonPropertyName("port_no")]
    public int Port { get; set; }
    [JsonIgnore]
    public string GizliAnahtar { get; set; } = "sabit";
}

class JsonOrnek
{
    static void Main()
    {
        string json = """{"ortam":"uretim","port_no":8080,"GizliAnahtar":"disaridan"}""";

        var varsayilan = JsonSerializer.Deserialize<AyarDto>(json)!;
        Console.WriteLine(varsayilan.Ortam ?? "NULL");     #! NULL (büyük-küçük harf uyuşmadı!)
        Console.WriteLine(varsayilan.Port);                #! 8080 ([JsonPropertyName] tam eşleşti)
        Console.WriteLine(varsayilan.GizliAnahtar);        #! sabit ([JsonIgnore] dış veriyi yok saydı)
    }
}
```
:::

::: tahmin
```csharp
using System;
using System.Text.Json;
using System.Text.Json.Serialization;

class KullaniciDto
{
    public string? Ad { get; set; }
    [JsonPropertyName("yetki_kodu")]
    public int YetkiKodu { get; set; }
    [JsonIgnore]
    public bool Yonetici { get; set; } = false;
}

class Tahmin
{
    static void Main()
    {
        string girdi = """{"ad":"ali","yetki_kodu":7,"Yonetici":true}""";

        var d1 = JsonSerializer.Deserialize<KullaniciDto>(girdi)!;
        var secenek = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
        var d2 = JsonSerializer.Deserialize<KullaniciDto>(girdi, secenek)!;

        Console.WriteLine((d1.Ad ?? "BOS") + ":" + d1.YetkiKodu + ":" + d1.Yonetici);
        Console.WriteLine((d2.Ad ?? "BOS") + ":" + d2.YetkiKodu + ":" + d2.Yonetici);
    }
}
```

```gercek
BOS:7:False
ali:7:False
```

???

`BOS:7:False` ve `ali:7:False`. İlk `Deserialize` çağrısında `JsonSerializerOptions` verilmediği için `System.Text.Json` büyük-küçük harfe duyarlıdır: JSON'daki `"ad"` C# özelliğindeki `Ad` ile eşleşmez (`null` kalır → `BOS`), `"yetki_kodu"` ise `[JsonPropertyName("yetki_kodu")]` ile birebir eşleştiği için `7` olur. `[JsonIgnore]` olan `Yonetici` özelliği her iki çağrıda da JSON'daki `"Yonetici":true` değerini yok sayar ve `False` kalır. İkinci çağrıda `PropertyNameCaseInsensitive = true` verildiği için `"ad"` özelliği `Ad` alanına bağlanır ve `ali:7:False` üretir.
:::

::: gorev `IConfiguration` katmanlı ayar ve ortam değişkeni (`__`) çözümleyici
ASP.NET Core'un `IConfiguration` birleştirme davranışını Python'da `ayar_oku(temel_json, uretim_json, ortam_degiskenleri, anahtar)` fonksiyonu olarak kur:
- Öncelik sırası (düşükten yükseğe):
  1. `temel_json`: `{"Veritabani:Sunucu": "localhost", ...}` biçiminde sözlük.
  2. `uretim_json`: aynı biçimde sözlük; varsa `temel_json` değerini ezer.
  3. `ortam_degiskenleri`: `{"VERITABANI__SUNUCU": "10.0.0.5", ...}` biçiminde sözlük; içindeki çift alt çizgi `"__"` iki noktaya `":"` çevrilir ve en yüksek öncelikle önceki değerleri ezer!
- Tüm anahtar aramaları **büyük-küçük harf duyarsızdır** (`OrdinalIgnoreCase`).
- `anahtar` bulunduğunda değerini, bulunamadığında `"TANIMSIZ"` döndür.

```starter
def ayar_oku(temel_json, uretim_json, ortam_degiskenleri, anahtar):
    return temel_json.get(anahtar, "TANIMSIZ")
```

```test
need("ayar_oku")
temel = {"Servis:Adres": "http://localhost:5000", "Servis:ZamanAsimi": "30", "Gunluk:Seviye": "Bilgi"}
uretim = {"servis:adres": "https://api.pafta.local", "Gunluk:Seviye": "Uyari"}
ortam = {"SERVIS__ZAMANASIMI": "10", " EK_AYAR__AKTIF ": "true"}

eq(ayar_oku(temel, uretim, ortam, "SERVIS:ADRES"), "https://api.pafta.local", "uretim_json temel_json değerini ezmeli (harf duyarsız)")
eq(ayar_oku(temel, uretim, ortam, "Servis:ZamanAsimi"), "10", "ortam değişkenindeki SERVIS__ZAMANASIMI en yüksek öncelikle ezmeli")
eq(ayar_oku(temel, uretim, {}, "gunluk:seviye"), "Uyari", "uretim_json Gunluk:Seviye değerini ezmeli")
eq(ayar_oku(temel, {}, {}, "Gunluk:Seviye"), "Bilgi", "üst katmanlarda yoksa temel_json değeri dönmeli")
eq(ayar_oku(temel, uretim, ortam, "ek_ayar:aktif"), "true", "tek alt çizgi (_) korunmalı, yalnızca çift alt çizgi (__) iki noktaya (:) dönüşmeli")
eq(ayar_oku(temel, uretim, ortam, "Yok:Anahtar"), "TANIMSIZ", "olmayan anahtar -> TANIMSIZ")
```

```solution
def ayar_oku(temel_json, uretim_json, ortam_degiskenleri, anahtar):
    birlesik = {}
    for k, v in temel_json.items():
        birlesik[k.strip().lower()] = v
    for k, v in uretim_json.items():
        birlesik[k.strip().lower()] = v
    for k, v in ortam_degiskenleri.items():
        norm_k = k.strip().replace("__", ":").lower()
        birlesik[norm_k] = v
    return birlesik.get(anahtar.strip().lower(), "TANIMSIZ")
```

```hint
Önce `temel_json`, sonra `uretim_json`, en son da anahtarlarında `.replace("__", ":")` uyguladığın `ortam_degiskenleri` sözlüğünü küçük harfli anahtarlarla tek bir sözlüğe yaz.
```
:::

::: gorev `System.Text.Json` duyarsızlık ve `[JsonIgnore]` simülatörü
Aşağıdaki C# `JsonSerializer.Deserialize` davranışını Python'da `json_bagla(alan_kurallari, gelen_json, harf_duyarsiz_mi)` fonksiyonu olarak kur:
- `alan_kurallari`: `{"Ad": {"json_adi": None, "ignore": False, "varsayilan": "misafir"}, "Port": {"json_adi": "port_no", "ignore": False, "varsayilan": 80}, ...}` biçiminde sözlüktür.
- Her C# özelliği için:
  1. `"ignore"` `True` ise (`[JsonIgnore]`), JSON'da ne gelirse gelsin özellik `"varsayilan"` değerinde kalır.
  2. `"ignore"` `False` ise aranacak JSON anahtar adı `kural["json_adi"] or ozellik_adi` olur.
  3. `harf_duyarsiz_mi` `False` ise `gelen_json` içinde **tam eşleşen** (büyük-küçük harf duyarlı) anahtar aranır; `True` ise **büyük-küçük harf duyarsız** aranır. Bulunursa JSON'daki değer, bulunamazsa `"varsayilan"` değer atanır.

```starter
def json_bagla(alan_kurallari, gelen_json, harf_duyarsiz_mi):
    return {k: v["varsayilan"] for k, v in alan_kurallari.items()}
```

```test
need("json_bagla")
kurallar = {
    "Kullanici": {"json_adi": None, "ignore": False, "varsayilan": "anonim"},
    "Port": {"json_adi": "servis_portu", "ignore": False, "varsayilan": 8080},
    "Rol": {"json_adi": None, "ignore": True, "varsayilan": "okuyucu"},
}
gelen = {"kullanici": "ali", "SERVIS_PORTU": 9000, "Rol": "admin", "rol": "admin"}

eq(json_bagla(kurallar, gelen, False),
   {"Kullanici": "anonim", "Port": 8080, "Rol": "okuyucu"},
   "harf_duyarsiz_mi=False iken 'kullanici' ve 'SERVIS_PORTU' eşleşmez, Rol ise ignore olduğu için 'okuyucu' kalır")
eq(json_bagla(kurallar, gelen, True),
   {"Kullanici": "ali", "Port": 9000, "Rol": "okuyucu"},
   "harf_duyarsiz_mi=True iken Kullanici ve Port bağlanır, [JsonIgnore] olan Rol yine 'okuyucu' kalır")
eq(json_bagla(kurallar, {"Kullanici": "ayse", "servis_portu": 443}, False),
   {"Kullanici": "ayse", "Port": 443, "Rol": "okuyucu"},
   "tam eşleşen anahtarlar harf_duyarsiz_mi=False iken de bağlanmalı")
```

```solution
def json_bagla(alan_kurallari, gelen_json, harf_duyarsiz_mi):
    gelen_kucuk = {k.lower(): v for k, v in gelen_json.items()}
    sonuc = {}
    for ozellik, kural in alan_kurallari.items():
        varsayilan = kural["varsayilan"]
        if kural["ignore"]:
            sonuc[ozellik] = varsayilan
            continue
        hedef_anahtar = kural["json_adi"] if kural["json_adi"] is not None else ozellik
        if not harf_duyarsiz_mi:
            sonuc[ozellik] = gelen_json.get(hedef_anahtar, varsayilan)
        else:
            sonuc[ozellik] = gelen_kucuk.get(hedef_anahtar.lower(), varsayilan)
    return sonuc
```

```hint
`kural["ignore"]` doğruysa doğrudan `varsayilan` ata. Değilse `hedef_anahtar = kural["json_adi"] or ozellik` belirle ve `harf_duyarsiz_mi` bayrağına göre tam ya da küçük harfli sözlükten oku.
```
:::
