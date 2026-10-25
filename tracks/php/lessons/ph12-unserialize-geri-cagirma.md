---
id: ph12
title: unserialize · Geri Çağırmalar ve Autoload Grafiği
summary: unserialize verinin adını yazdığı sınıflardan nesne kurar: __construct çağrılmaz, özellikler doğrudan yazılır, sonra yaşam döngüsü geri çağırmaları çalışır; __unserialize tanımlıysa __wakeup hiç çalışmaz, __destruct nesne ölünce çalışır; bilinmeyen bir sınıf adı autoload'u tetikler; allowed_classes engellenen sınıfı __PHP_Incomplete_Class'a çevirir ve geri çağırmaları hiç çalıştırmaz; bozuk veri false döner.
kazanim: ZCPE 5.4, ZCPE 6.5
---

::: anlat Veri hangi sınıfın kurulacağını söyler
`serialize` bir değeri metne çevirir, `unserialize` geri okur. Diziler ve skalerler için bu yalnız bir biçim dönüşümüdür. Nesnelerde ise dönüşüm **kod çalıştırır**.

```php norun
serialize(new A());            // 'O:1:"A":1:{s:1:"x";i:1;}'
//          O = object, 1 = ad uzunluğu, "A" = SINIF ADI, 1 = özellik sayısı
```

Metnin içinde sınıf **adı** yazar. `unserialize` o adı okur, sınıfı bulur ve ondan bir nesne kurar. İki ayrıntı önemlidir:

- **`__construct` çağrılmaz.** Nesne kurucusu atlanarak üretilir; sınıfın "geçerli bir nesne ancak kurucudan çıkar" varsayımı burada tutmaz.
- **Özellikler doğrudan yazılır.** `private` ve `protected` olanlar da dahil; setter'lar, tür denetimleri ve iş kuralları devreye girmez.

Sınıf o anda yüklü değilse PHP **otomatik yükleyiciyi** (`spl_autoload_register` ile kayıtlı autoloader) çağırır. Yani veride geçen bir ad, uygulamanın o ana kadar hiç dokunmadığı bir dosyayı yükletebilir. Bu derste ölçüldü: tanımsız `YokOlan` sınıfı için autoloader `YokOlan` adıyla çağrıldı, bulunamayınca nesne `__PHP_Incomplete_Class` oldu.
:::

::: anlat Geri çağırma sırası ve allowed_classes
Nesne kurulduktan sonra sınıfın tanımladığı yaşam döngüsü metotları çalışır:

| Metot | Ne zaman | Notu |
|---|---|---|
| `__unserialize(array $veri)` | özellikler yazılmadan, ham dizi ile | tanımlıysa **özellik yazımının ve `__wakeup`'ın yerine** geçer |
| `__wakeup()` | özellikler yazıldıktan **sonra** | yalnız `__unserialize` yoksa çalışır |
| `__destruct()` | nesne öldüğünde | `unset`, kapsam sonu ya da betiğin sonu |

Ölçüldü: `__wakeup` içinde `$this->x` zaten `42`'dir, yani özellikler önce yazılır. İkisi birden tanımlıysa **yalnız `__unserialize`** çalışır; `__wakeup` hiç çağrılmaz.

`unserialize`'ın ikinci argümanı kurulabilecek sınıfları sınırlar:

```php norun
unserialize($veri, ['allowed_classes' => false]);        // hiçbir sınıf kurulmasın
unserialize($veri, ['allowed_classes' => ['Nokta']]);    // yalnız bu sınıf
```

Engellenen bir sınıf `__PHP_Incomplete_Class`'a dönüşür: özellikleri okumaya kalkmak uyarı verir ve o sınıfın **hiçbir geri çağırması çalışmaz**. Bozuk bir metin verilirse `unserialize` istisna fırlatmaz, `false` döner — ve `false`, başarıyla çözülmüş bir `false` değerinden ayırt edilemez; bu yüzden ciddi kodda ayrıca denetlersin.

> [!TUZAK] `allowed_classes` "güvenilmeyen veri artık güvenli" demek değildir
> Listeyi daraltmak kurulabilecek sınıf kümesini küçültür, ama güvenilmeyen girdinin hâlâ nesne alanlarını istediği değerle doldurduğunu değiştirmez; izin verdiğin sınıfın `__wakeup`/`__destruct`'ı da çalışır. Dışarıdan gelen veriyi nesneye çevirmek zorunda değilsen çevirme: `json_decode` gibi **nesne kurmayan** bir biçim, sınırlanmış bir `unserialize`'dan daha sağlam bir sınırdır.
:::

::: tahmin Hangi geri çağırma çalışır?
```php
<?php
class A { public $x = 1; public function __wakeup(){ echo "A::__wakeup x=$this->x\n"; } }
class B { public $y = 1;
  public function __unserialize(array $d){ echo "B::__unserialize y={$d['y']}\n"; $this->y = $d['y']; }
  public function __wakeup(){ echo "B::__wakeup\n"; } }

$a = unserialize('O:1:"A":1:{s:1:"x";i:42;}');
echo "x=$a->x\n";
$b = unserialize('O:1:"B":1:{s:1:"y";i:7;}');
echo "y=$b->y\n";
var_dump(@unserialize('bu gecerli degil'));
$c = unserialize('O:1:"A":1:{s:1:"x";i:5;}', ['allowed_classes' => false]);
echo get_class($c), "\n";
```

```gercek
A::__wakeup x=42
x=42
B::__unserialize y=7
y=7
bool(false)
__PHP_Incomplete_Class
```

???

`A::__wakeup x=42` — kurucusu hiç çalışmadan kurulan nesnenin `x`'i **zaten 42**: özellikler `__wakeup`'tan önce yazılır. Varsayılan `1` değeri görünmez bile.

`B::__unserialize y=7` ve `B::__wakeup` **yok**: ikisi birden tanımlı olduğunda yalnız `__unserialize` çalışır. Özellikleri de o yazar; yazmasaydı `$b->y` varsayılan `1` kalırdı.

`bool(false)`: bozuk metin istisna değil `false` üretir (uyarıyı `@` bastırdı).

`__PHP_Incomplete_Class`: `allowed_classes => false` ile sınıf kurulmadı. Çıktıda **hiçbir `__wakeup` satırı yok** — engellenen sınıfın geri çağırmaları çalışmaz.
:::

::: gorev Çalışan geri çağırmalar
`cagrilar(tanimlar, sinif)` yaz: `unserialize` bir nesneyi çözerken hangi geri çağırmaların çalışacağını belirle.

- `tanimlar`: sınıf adını, o sınıfın tanımladığı sihirli metot adları kümesine eşleyen sözlük.
- `sinif`: veride yazan sınıf adı.

Dönüş `(acilista, olurken)`:

- `acilista`: `unserialize` sırasında çalışanlar, sırayla. `__unserialize` tanımlıysa yalnız `["__unserialize"]`; değilse `__wakeup` tanımlıysa `["__wakeup"]`; hiçbiri yoksa boş liste.
- `olurken`: nesne öldüğünde çalışanlar — `__destruct` tanımlıysa `["__destruct"]`, yoksa boş liste.

Sınıf `tanimlar`'da hiç yoksa kurulamaz: ikisi de boş liste olur.

```starter
def cagrilar(tanimlar, sinif):
    metotlar = tanimlar.get(sinif, set())
    acilista = []
    if "__wakeup" in metotlar:
        acilista.append("__wakeup")
    if "__unserialize" in metotlar:
        acilista.append("__unserialize")
    return (acilista, [])
```

```test
need("cagrilar")
eq(cagrilar({"A": {"__wakeup"}}, "A"), (["__wakeup"], []), "yalnız __wakeup")
eq(cagrilar({"B": {"__unserialize", "__wakeup"}}, "B"), (["__unserialize"], []),
   "ölçülen kural: __unserialize varsa __wakeup hiç çalışmaz")
eq(cagrilar({"C": {"__unserialize"}}, "C"), (["__unserialize"], []), "yalnız __unserialize")
eq(cagrilar({"D": set()}, "D"), ([], []), "sihirli metot yok")
eq(cagrilar({"E": {"__destruct"}}, "E"), ([], ["__destruct"]), "yıkıcı açılışta değil, ölürken")
eq(cagrilar({"F": {"__wakeup", "__destruct"}}, "F"), (["__wakeup"], ["__destruct"]), "ikisi ayrı anlarda")
eq(cagrilar({"G": {"__construct", "__wakeup"}}, "G"), (["__wakeup"], []),
   "__construct unserialize sırasında çağrılmaz")
eq(cagrilar({}, "Yok"), ([], []), "tanımsız sınıf kurulamaz")
```

```solution
def cagrilar(tanimlar, sinif):
    if sinif not in tanimlar:
        return ([], [])
    metotlar = tanimlar[sinif]
    if "__unserialize" in metotlar:
        acilista = ["__unserialize"]
    elif "__wakeup" in metotlar:
        acilista = ["__wakeup"]
    else:
        acilista = []
    return (acilista, ["__destruct"] if "__destruct" in metotlar else [])
```

```hint
Başlangıç kodu ikisini de listeye ekliyor. İkisi birbirinin alternatifidir: önce `__unserialize`'a bak, yoksa `__wakeup`'a. `__construct` bu listeye hiç girmez.
```
:::

::: gorev Autoload grafiği
`grafik(siniflar, yuklu, izinli)` yaz: bir yükün içinde geçen sınıf adlarını sırayla işleyip `(autoload, kurulan)` döndür.

- `siniflar`: yükte göründükleri sırayla sınıf adları (iç içe nesneler yüzünden aynı ad birden çok kez geçebilir).
- `yuklu`: zaten yüklü sınıf adlarının kümesi.
- `izinli`: `True` (hepsi), `False` (hiçbiri) ya da izin verilen adların listesi.

Kurallar:

- İzin verilmeyen bir ad hiç kurulmaz ve otomatik yükleyiciyi **tetiklemez**; sonuçta `__PHP_Incomplete_Class` olur.
- İzin verilen ve `yuklu` olmayan bir ad için otomatik yükleyici çağrılır; her ad için **en çok bir kez**.
- `autoload`: yükleyicinin çağrıldığı adlar, ilk görülme sırasıyla.
- `kurulan`: her sınıf adı için sonucun ne olduğu — izin verilmişse adın kendisi, verilmemişse `"__PHP_Incomplete_Class"` — yükteki sırayla, tekrarlar dahil.

```starter
def grafik(siniflar, yuklu, izinli):
    autoload = [s for s in siniflar if s not in yuklu]
    return (autoload, list(siniflar))
```

```test
need("grafik")
eq(grafik(["A"], {"A"}, True), ([], ["A"]), "zaten yüklü: autoload yok")
eq(grafik(["A"], set(), True), (["A"], ["A"]), "yüklü değil: autoload çağrılır")
eq(grafik(["A", "B", "A"], set(), True), (["A", "B"], ["A", "B", "A"]),
   "aynı ad ikinci kez autoload tetiklemez ama kurulan listesinde yine görünür")
eq(grafik(["A", "B"], {"B"}, True), (["A"], ["A", "B"]), "yalnız yüklü olmayan ad")
eq(grafik(["A"], set(), False), ([], ["__PHP_Incomplete_Class"]),
   "allowed_classes=false: kurulmaz ve autoload tetiklenmez")
eq(grafik(["A", "B"], set(), ["B"]), (["B"], ["__PHP_Incomplete_Class", "B"]),
   "listede olmayan ad engellenir, olan ad yüklenir")
eq(grafik(["A", "A"], set(), ["A"]), (["A"], ["A", "A"]), "izinli ad da bir kez autoload")
eq(grafik([], set(), True), ([], []), "nesne içermeyen yük")
```

```solution
def grafik(siniflar, yuklu, izinli):
    autoload, kurulan, denenen = [], [], set()
    for sinif in siniflar:
        serbest = izinli is True or (izinli is not False and sinif in izinli)
        if not serbest:
            kurulan.append("__PHP_Incomplete_Class")
            continue
        if sinif not in yuklu and sinif not in denenen:
            autoload.append(sinif)
            denenen.add(sinif)
        kurulan.append(sinif)
    return (autoload, kurulan)
```

```hint
Üç ayrı soru var: izin var mı, yüklü mü, daha önce denendi mi. İzin yoksa diğer ikisine hiç bakılmaz. `izinli` üç türde gelebilir; `True`/`False` ile liste durumunu `is True` / `is False` ile ayır, yoksa `False in [...]` gibi şaşırtıcı karşılaştırmalara düşersin.
```

```hint
`autoload` yalnız **ilk** görülmede büyür, `kurulan` ise her ad için bir giriş alır — bu yüzden iki listenin uzunlukları farklı olabilir.
```
:::
