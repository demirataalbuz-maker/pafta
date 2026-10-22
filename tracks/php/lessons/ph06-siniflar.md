---
id: ph06
title: Sınıflar ve Nesneler
summary: PHP 8 sınıfları; yapıcıda özellik tanıtma (constructor promotion), public/protected/private, $this ve ->, static ve ::, arayüzler ve kalıtım, __toString gibi sihirli metotlar, namespace ve use ile adların çözülmesi, trait'ler ve öncelik sırası, Composer'ın otomatik yüklemesi.
kazanim: ZCPE 1.3, ZCPE 5.1, ZCPE 5.2, ZCPE 5.3, ZCPE 5.4
---

::: anlat PHP 8 sınıfı
Modern PHP uygulamaları (Laravel, Symfony, WordPress eklentileri) sınıflarla yazılır. PHP 8'in kısa yazımı:

```php
<?php
class Sunucu {
    public function __construct(
        public string $ad,            // yapıcıda tanıtılan özellik: $this->ad
        private int $cpu = 0,         // sınıf dışından erişilemez
    ) {}

    public function durum(): string {
        return $this->cpu > 80 ? "yüksek" : "normal";
    }

    public function __toString(): string {    // echo $s yazınca çağrılır
        return "{$this->ad}({$this->cpu})";
    }

    public static function bos(string $ad): static {
        return new static($ad);       // static: sınıfın kendisi (alt sınıftan çağrılırsa alt sınıf)
    }
}

$s = new Sunucu("db01", 91);
echo $s, " ", $s->durum(), "\n";
```

| Yazım | Anlamı |
|---|---|
| `$nesne->alan`, `$nesne->metot()` | örnek üyesi |
| `Sinif::metot()`, `Sinif::SABIT` | statik üye, sınıf sabiti |
| `$this` | metodun içinde nesnenin kendisi |
| `self::`, `static::`, `parent::` | bu sınıf, çağrılan sınıf, üst sınıf |
| `public` / `protected` / `private` | herkes / sınıf ve alt sınıflar / yalnızca bu sınıf |
| `readonly` | PHP 8.1: yalnızca bir kez atanabilir |

### Sihirli metotlar
Çift alt çizgiyle başlayan metotlar PHP tarafından **kendiliğinden** çağrılır:

| Metot | Ne zaman |
|---|---|
| `__construct` | `new` |
| `__toString` | nesne metin olarak kullanılınca |
| `__get($ad)`, `__set($ad, $v)` | olmayan bir özellik okunup yazılınca |
| `__call($ad, $argumanlar)` | olmayan bir metot çağrılınca |
| `__destruct` | nesne yok edilirken |

Kod okurken `__get` ve `__call` gördüğünde dikkat: `$nesne->herhangiBirSey()` gibi bir çağrının nerede tanımlandığını ararken bulamıyorsan cevap muhtemelen buradadır.
:::

::: anlat Arayüzler, namespace ve otomatik yükleme
```php
<?php
namespace Pafta\Izleme;               // sınıfların tam adı: Pafta\Izleme\Olcer

interface Olcer {
    public function olc(): float;     // gövdesiz: uygulayan sınıf yazmak zorunda
}

final class CpuOlcer implements Olcer {
    public function olc(): float { return 72.5; }
}
```

Büyük projelerde her sınıf ayrı bir dosyadadır. Dosyaları tek tek `require` etmek yerine **Composer**'ın otomatik yükleyicisi kullanılır: `require __DIR__ . '/vendor/autoload.php';` satırından sonra bir sınıf ilk kez kullanıldığında, adına karşılık gelen dosya (`Pafta\Izleme\CpuOlcer` → `src/Izleme/CpuOlcer.php`) kendiliğinden yüklenir. Bir PHP projesini okumaya `composer.json`'daki `autoload` bölümünden başlamak, hangi klasörün hangi namespace olduğunu gösterir.

> [!NOT]
> `use Pafta\Izleme\CpuOlcer;` satırı bir şeyi **çalıştırmaz** ya da yüklemez; yalnızca dosyanın geri kalanında kısa adı kullanabilmeni sağlayan bir takma addır.
:::

::: tahmin
PHP 8 ile çıktı:

```php
<?php
class Sunucu {
    public function __construct(public string $ad, private int $cpu = 0) {}
    public function durum(): string { return $this->cpu > 80 ? "yüksek" : "normal"; }
    public function __toString(): string { return "{$this->ad}({$this->cpu})"; }
    public static function bos(string $ad): static { return new static($ad); }
}
$s = new Sunucu("db01", 91);
echo $s, " ", $s->durum(), "\n";
$b = Sunucu::bos("test01");
echo $b, " ", $b->durum(), "\n";
echo $s->ad, "\n";
```

```gercek
db01(91) yüksek
test01(0) normal
db01
```

???

`db01(91) yüksek`: `echo $s` `__toString`'i çağırır; 91 > 80. `test01(0) normal`: `bos` yapıcıyı yalnızca adla çağırır, `$cpu` varsayılan 0'ı alır. `db01`: `$ad` `public` olduğu için dışarıdan okunabilir; `$s->cpu` yazılsaydı `private` olduğu için hata verirdi.
:::

::: anlat Adların çözülmesi ve trait'ler
Bir namespace içinde yazılan her sınıf adı, PHP tarafından bir **tam ada** (fully qualified name) çevrilir. Kurallar:

| Kodda | Tam adı | Neden |
|---|---|---|
| `\DateTime` | `DateTime` | `\` ile başlayan ad zaten tamdır (global alan) |
| `Olcer` (dosyada `namespace Pafta\Izleme;`) | `Pafta\Izleme\Olcer` | nitelenmemiş ad, dosyanın namespace'ine göre çözülür |
| `CpuOlcer` (dosyada `use Pafta\Izleme\Cpu\CpuOlcer;`) | `Pafta\Izleme\Cpu\CpuOlcer` | ilk parça bir `use` takma adıyla eşleşir |
| `Olcum\Disk` (dosyada `use Pafta\Izleme as Olcum;`) | `Pafta\Izleme\Disk` | yalnızca **ilk parça** takma ada bakılır |

Namespace ve sınıf adları büyük-küçük harfe **duyarsızdır**: `use ... as Olcum;`'dan sonra `olcum\Disk` de aynı sınıfı gösterir.

> [!TUZAK]
> Bir namespace içinde `new DateTime()` yazmak `Pafta\Izleme\DateTime`'ı arar ve bulamaz: **sınıflar** için global alana geri dönülmez. `\DateTime` ya da dosyanın başında `use DateTime;` yazılmalı. **Fonksiyonlar ve sabitler** için ise geri dönüş vardır: `strlen(...)` önce `Pafta\Izleme\strlen`'i, bulamazsa global `strlen`'i çağırır.

`use` satırının biçimleri:

```php
use Pafta\Izleme\CpuOlcer;                  // kısa adı CpuOlcer
use Pafta\Izleme\CpuOlcer as Olcer;         // takma adla
use Pafta\Izleme\{CpuOlcer, DiskOlcer};     // gruplu
use function Pafta\Yardim\yuvarla;          // bir fonksiyon
use const Pafta\Ayar\SURUM;                 // bir sabit
```

`Olcer::class` bir sınıfın tam adını metin olarak verir; çözümleme derleme sırasında yapılır, sınıfın var olması gerekmez.

### Trait'ler
**Trait**, birden çok sınıfa kopyalanan bir metot ve özellik paketidir. PHP'de bir sınıfın tek bir ebeveyni olabilir; ortak davranışı ebeveynden bağımsız olarak paylaşmanın yolu trait'tir. Sınıfın **içindeki** `use` satırı trait ekler (dosya başındaki `use`'dan bambaşka bir şeydir):

```php
trait ZamanDamgali {
    private array $kayitlar = [];
    public function kaydet(string $olay): void { $this->kayitlar[] = $olay; }
    public function kayitSayisi(): int { return count($this->kayitlar); }
}

class BiletServisi extends Servis {
    use ZamanDamgali;
}
```

Aynı adlı bir metot birden çok yerde varsa öncelik sırası: **sınıfın kendi metodu > trait'in metodu > ebeveynden gelen metot**. İki trait aynı adı taşıyorsa hangisinin kullanılacağı açıkça seçilir: `use A, B { A::selam insteadof B; B::selam as bSelam; }`. Trait'teki özellikler her nesnede ayrıdır; `static::class` ve `$this`, trait'i kullanan sınıfı gösterir.
:::

::: tahmin
PHP 8 ile çıktı:

```php
<?php
namespace Pafta\Izleme;

trait Etiketli {
    public function etiket(): string { return "trait:" . static::class; }
    public function selam(): string { return "trait"; }
}
class Taban {
    public function selam(): string { return "taban"; }
    public function ad(): string { return "taban"; }
}
class Sunucu extends Taban {
    use Etiketli;
    public function ad(): string { return "sunucu"; }
}

$s = new Sunucu();
echo $s->selam(), " ", $s->ad(), "\n";
echo $s->etiket(), "\n";
echo strlen("abc"), " ", \strlen("abcd"), "\n";
echo Sunucu::class, "\n";
```

```gercek
trait sunucu
trait:Pafta\Izleme\Sunucu
3 4
Pafta\Izleme\Sunucu
```

???

`trait sunucu`, `trait:Pafta\Izleme\Sunucu`, `3 4` ve `Pafta\Izleme\Sunucu`. `selam` hem ebeveynde hem trait'te var; trait ebeveynden önce gelir. `ad` sınıfın kendisinde tanımlı; sınıf trait'ten de ebeveynden de önce gelir. `static::class` trait'i kullanan sınıfın **tam** adını verir. Nitelenmemiş `strlen` namespace'te bulunamayınca global fonksiyona düşer; `\strlen` doğrudan globaldir. `Sunucu::class` dosyanın namespace'iyle birlikte yazılır.
:::

::: gorev PHP sınıfını Python'a çevir
Aşağıdaki PHP sınıfını Python'a çevir. `__toString` Python'da `__str__`'dir; `static` yapıcı bir `classmethod` olur.

```php
class Bilet {
    public function __construct(public int $id, public string $oncelik = "orta") {}
    public function acil(): bool { return in_array($this->oncelik, ["yüksek", "kritik"], true); }
    public function __toString(): string { return "#{$this->id} [{$this->oncelik}]"; }
    public static function kritik(int $id): static { return new static($id, "kritik"); }
}
```

```starter
class Bilet:
    pass
```

```test
need("Bilet", "sınıf")
b = Bilet(12)
eq(str(b), "#12 [orta]", "varsayılan öncelik")
eq(b.acil(), False, "orta acil değil")
k = Bilet.kritik(7)
eq(str(k), "#7 [kritik]", "kritik yapıcı")
eq(k.acil(), True, "kritik acil")
eq(Bilet(3, "yüksek").acil(), True, "yüksek acil")
```

```solution
class Bilet:
    def __init__(self, id, oncelik="orta"):
        self.id = id
        self.oncelik = oncelik

    def acil(self):
        return self.oncelik in ("yüksek", "kritik")

    def __str__(self):
        return f"#{self.id} [{self.oncelik}]"

    @classmethod
    def kritik(cls, id):
        return cls(id, "kritik")
```

```hint
Yapıcıdaki tanıtılan özellikler Python'da `__init__` içinde `self.id = id` atamalarıdır.
```

```hint
`new static(...)` → `@classmethod def kritik(cls, id): return cls(id, "kritik")`.
```
:::

::: gorev Olmayan özellik: __get
Aşağıdaki PHP sınıfı ayarları bir dizide tutar ve olmayan özellik okunduğunda `__get` ile o diziye bakar; anahtar yoksa `null` döner. Python'da aynı davranışı `__getattr__` ile kur.

```php
class Ayar {
    private array $degerler;
    public function __construct(array $degerler) { $this->degerler = $degerler; }
    public function __get(string $ad) { return $this->degerler[$ad] ?? null; }
}
$a = new Ayar(["port" => 8443, "tema" => "koyu"]);
// $a->port → 8443, $a->dil → null
```

```starter
class Ayar:
    def __init__(self, degerler):
        self.degerler = degerler
```

```test
need("Ayar", "sınıf")
a = Ayar({"port": 8443, "tema": "koyu"})
eq(a.port, 8443, "var olan ayar")
eq(a.tema, "koyu", "var olan ayar")
eq(a.dil, None, "olmayan ayar: None")
```

```solution
class Ayar:
    def __init__(self, degerler):
        self.degerler = degerler

    def __getattr__(self, ad):
        return self.degerler.get(ad)
```

```hint
Python'da `__getattr__(self, ad)`, normal yollarla bulunamayan bir özellik okununca çağrılır: PHP'deki `__get`'in karşılığı.
```
:::

::: gorev Sınıf adını çöz
`sinif_adi(namespace, uselar, ad)` fonksiyonu PHP'nin **sınıf** adı çözümleme kuralını uygulasın ve tam adı (başında `\` olmadan) döndürsün:

- `namespace`: dosyanın namespace'i (`""` global alan demek)
- `uselar`: `{takma_ad: tam_ad}` sözlüğü (dosyanın `use` satırlarından)
- `ad`: kodda yazılan sınıf adı

Kurallar sırasıyla:

1. `ad` `\` ile başlıyorsa tamdır: baştaki `\` atılır
2. adın **ilk parçası** (ilk `\`'e kadar olan kısım) bir takma adla büyük-küçük harfe duyarsız eşleşiyorsa o parça tam adla değiştirilir
3. değilse, namespace boş değilse başına `namespace\` eklenir (sınıflar için global alana geri dönüş yoktur)

```starter
def sinif_adi(namespace, uselar, ad):
    return namespace + "\\" + ad
```

```test
need("sinif_adi")
eq(sinif_adi(r"Pafta\Izleme", {}, "Olcer"), r"Pafta\Izleme\Olcer", "nitelenmemiş ad: namespace'e göre")
eq(sinif_adi(r"Pafta\Izleme", {"CpuOlcer": r"Pafta\Izleme\Cpu\CpuOlcer"}, "CpuOlcer"), r"Pafta\Izleme\Cpu\CpuOlcer", "use ile")
eq(sinif_adi(r"Pafta\Izleme", {"CpuOlcer": r"Pafta\Izleme\Cpu\CpuOlcer"}, "cpuolcer"), r"Pafta\Izleme\Cpu\CpuOlcer",
   "takma ad büyük-küçük harfe duyarsız")
eq(sinif_adi(r"Pafta\Api", {"Olcum": r"Pafta\Izleme"}, r"Olcum\Disk"), r"Pafta\Izleme\Disk", "yalnızca ilk parça takma ada bakılır")
eq(sinif_adi(r"Pafta\Api", {"Disk": r"X\Disk"}, r"Olcum\Disk"), r"Pafta\Api\Olcum\Disk", "son parça takma adla eşleşse de sayılmaz")
eq(sinif_adi(r"Pafta\Api", {}, "\\DateTime"), "DateTime", "baştaki \\ tam ad demek")
eq(sinif_adi(r"Pafta\Api", {}, "DateTime"), r"Pafta\Api\DateTime", "sınıflar için global alana dönülmez")
eq(sinif_adi("", {}, "DateTime"), "DateTime", "global alanda önek yok")
eq(sinif_adi(r"Pafta\Api", {"Olcer": r"Pafta\Izleme\CpuOlcer"}, "OlcerFabrikasi"), r"Pafta\Api\OlcerFabrikasi",
   "takma ad bütün bir parça olmalı, önek yetmez")
eq(sinif_adi("", {"Log": r"Pafta\Gunluk\Log"}, r"Log\Kayit"), r"Pafta\Gunluk\Log\Kayit", "global alanda use")
```

```solution
def sinif_adi(namespace, uselar, ad):
    if ad.startswith("\\"):
        return ad[1:]
    ilk, ayrac, kalan = ad.partition("\\")
    for takma, tam in uselar.items():
        if takma.lower() == ilk.lower():
            return tam + ayrac + kalan
    return f"{namespace}\\{ad}" if namespace else ad
```

```hint
`ad.partition("\\")` ilk parçayı ve geri kalanı ayırır (Python'da ters eğik çizgi `"\\"` diye yazılır). Takma adları dolaşırken ikisini de `.lower()` ile karşılaştır.
```
:::

::: gorev Trait'i Python'a çevir
Aşağıdaki PHP kodunun davranışını Python'da kur. Python'da trait'in karşılığı bir **karışım sınıfıdır** (mixin): sınıfın tabanları arasında ebeveynden **önce** yazılır, böylece PHP'deki öncelik sırası (sınıf > trait > ebeveyn) korunur.

```php
trait Sayacli {
    private int $sayac = 0;
    public function arttir(): int { return ++$this->sayac; }
    public function selam(): string { return "sayaçlı"; }
}
class Taban {
    public function selam(): string { return "taban"; }
    public function tur(): string { return "taban"; }
}
class Servis extends Taban {
    use Sayacli;
    public function tur(): string { return "servis"; }
}
```

Python'da `Sayacli`, `Taban` ve `Servis` sınıfları olsun; `Servis` hem `Sayacli`'den hem `Taban`'dan türesin.

```starter
class Sayacli:
    def arttir(self):
        return 0


class Taban:
    def selam(self):
        return "taban"


class Servis(Taban):
    pass
```

```test
S = need("Servis", "sınıf"); T = need("Taban", "sınıf"); K = need("Sayacli", "sınıf")
s = S()
eq((s.arttir(), s.arttir(), s.arttir()), (1, 2, 3), "++$sayac: önce artırır, sonra döndürür; ilk çağrı 1")
eq(S().arttir(), 1, "sayaç her nesnede ayrı")
eq(s.selam(), "sayaçlı", "trait ebeveynden önce gelir")
eq(s.tur(), "servis", "sınıfın kendi metodu trait'ten ve ebeveynden önce gelir")
eq((T().selam(), T().tur()), ("taban", "taban"), "Taban'ın kendisi değişmez")
ok(issubclass(S, T) and issubclass(S, K), "Servis hem Taban'dan hem Sayacli'den türer")
ok(not hasattr(T(), "arttir"), "trait yalnızca onu kullanan sınıfa eklenir")
```

```solution
class Sayacli:
    def arttir(self):
        self._sayac = getattr(self, "_sayac", 0) + 1
        return self._sayac

    def selam(self):
        return "sayaçlı"


class Taban:
    def selam(self):
        return "taban"

    def tur(self):
        return "taban"


class Servis(Sayacli, Taban):
    def tur(self):
        return "servis"
```

```hint
Python yöntemleri tabanların yazılış sırasına göre arar (MRO): `class Servis(Sayacli, Taban)` önce `Servis`'e, sonra `Sayacli`'ye, sonra `Taban`'a bakar.
```

```hint
Sayaç her nesnede ayrı olmalı: bir yapıcı yazmadan `getattr(self, "_sayac", 0) + 1` ile başlayabilirsin. `++$x` değeri önce artırır, sonra döndürür.
```
:::
