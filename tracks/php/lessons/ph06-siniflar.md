---
id: ph06
title: Sınıflar ve Nesneler
summary: PHP 8 sınıfları; yapıcıda özellik tanıtma (constructor promotion), public/protected/private, $this ve ->, static ve ::, arayüzler ve kalıtım, __toString gibi sihirli metotlar, namespace ve use, Composer'ın otomatik yüklemesi.
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
