---
id: ps16
title: Sınıflar ve Enum
summary: PowerShell 5 sınıfları; özellikler, kurucular, yöntemler, statik üyeler, kalıtım, ToString; enum ve [Flags] enum ile bayraklar.
---

::: anlat Kendi türlerin
`[pscustomobject]` hızlı veri taşımak için idealdir. Davranışı (yöntemleri), doğrulaması ve varsayılanları olan bir tür gerektiğinde **sınıf** yazılır:

```powershell
class Sunucu {
    [string]$Ad
    [int]$Cpu
    hidden [string]$Not = ""                 #! listelerde görünmez

    Sunucu([string]$ad, [int]$cpu) {         #! kurucu
        $this.Ad = $ad
        $this.Cpu = $cpu
    }

    [bool] YogunMu() {                       #! yöntem: dönüş türü yazılır
        return $this.Cpu -ge 80
    }

    [string] ToString() {                    #! metne çevrilince ne görünsün
        return "$($this.Ad) (%$($this.Cpu))"
    }
}
$s = [Sunucu]::new("db01", 91)
$s.YogunMu()
"$s"
```

Sınıf yöntemleri fonksiyonlardan farklı davranır: yalnızca `return` ile döndürülen değer döner (PS06'daki "her çıktı dönüş değeridir" kuralı burada **geçerli değil**), değişkenlere `$this` üzerinden erişilir ve dönüş türü bildirilir.

### Statik üyeler ve kalıtım
```powershell
class Sayac {
    static [int]$Toplam = 0
    static [void] Artir() { [Sayac]::Toplam++ }
}
[Sayac]::Artir(); [Sayac]::Artir()
[Sayac]::Toplam

class Varlik {
    [string]$Ad
    Varlik([string]$ad) { $this.Ad = $ad }
    [string] Tanim() { return "varlık: $($this.Ad)" }
}
class Yazici : Varlik {                       #! Varlik'tan türer
    [int]$Kuyruk
    Yazici([string]$ad, [int]$kuyruk) : base($ad) { $this.Kuyruk = $kuyruk }
    [string] Tanim() { return "yazıcı: $($this.Ad), kuyrukta $($this.Kuyruk) iş" }   #! üzerine yaz
}
[Yazici]::new("kat2", 3).Tanim()
```

### enum ve bayraklar
`enum` sabit bir değer kümesini adlandırır. `[Flags()]` ile işaretlenen enum'da değerler bit olarak birleştirilebilir (C05'teki bayrak kalıbının PowerShell karşılığı):

```powershell
enum Seviye { Bilgi = 4; Uyari = 3; Hata = 2; Kritik = 1 }
[Seviye]2
[int][Seviye]::Uyari

[Flags()] enum Izin { Yok = 0; Oku = 1; Yaz = 2; Calistir = 4 }
$i = [Izin]::Oku -bor [Izin]::Yaz
$i
$i.HasFlag([Izin]::Yaz)
```

> [!TUZAK]
> Bir betikte sınıf tanımı **ayrıştırma anında** işlenir: sınıfın kullandığı türler betik çalışmadan önce bilinmelidir. Ayrıca aynı oturumda bir sınıfı değiştirip yeniden tanımlamak, Windows PowerShell'de çoğu zaman yeni oturum ister. Sınıfları modüllerde tutup `using module` ile yüklemek bu sorunları azaltır.
:::

::: tahmin
Üç satır yazar:

```powershell
class Kutu {
    [int]$Deger
    Kutu([int]$d) { $this.Deger = $d }
    [int] Iki() { "bu satır dönmez"; return $this.Deger * 2 }
}
$k = [Kutu]::new(21)
$k.Iki()
[Kutu]::new(5).Deger
([Kutu]::new(1) -is [Kutu])
```

???

`42`, `5`, `True`. Sınıf yöntemlerinde yalnızca `return` ile verilen değer döner; içerideki düz metin satırı (fonksiyonlardan farklı olarak) çıktıya karışmaz. `-is` tür denetimi yapar.
:::

::: gorev Sunucu sınıfı
`Sunucu` sınıfını yaz: `[string]$Ad`, `[int]$Cpu` özellikleri, iki parametreli kurucusu, CPU 80 ve üstündeyse `$true` döndüren `[bool] YogunMu()` yöntemi ve `ad (%cpu)` döndüren `ToString()`. Betiğin alt kısmı aynen kalmalı.

```starter
class Sunucu {
    [string]$Ad
    [int]$Cpu
}
$liste = @([Sunucu]::new("web01", 72), [Sunucu]::new("db01", 91), [Sunucu]::new("cache01", 84))
$liste | Where-Object { $_.YogunMu() } | ForEach-Object { "$_" }
```

```test
eq(out, "db01 (%91)\ncache01 (%84)\n", "iki yoğun sunucu")
ok("class Sunucu" in src, "class Sunucu tanımla")
```

```solution
class Sunucu {
    [string]$Ad
    [int]$Cpu

    Sunucu([string]$ad, [int]$cpu) {
        $this.Ad = $ad
        $this.Cpu = $cpu
    }

    [bool] YogunMu() {
        return $this.Cpu -ge 80
    }

    [string] ToString() {
        return "$($this.Ad) (%$($this.Cpu))"
    }
}
$liste = @([Sunucu]::new("web01", 72), [Sunucu]::new("db01", 91), [Sunucu]::new("cache01", 84))
$liste | Where-Object { $_.YogunMu() } | ForEach-Object { "$_" }
```

```hint
Kurucu sınıfla aynı adı taşır: `Sunucu([string]$ad, [int]$cpu) { $this.Ad = $ad; ... }`.
```

```hint
Yöntemlerde dönüş türü ve `return` zorunlu: `[bool] YogunMu() { return $this.Cpu -ge 80 }`.
```
:::

::: gorev İzin bayrakları
`[Flags()]` bir `Izin` enum'u yaz: `Yok = 0`, `Oku = 1`, `Yaz = 2`, `Calistir = 4`. Girdinin her satırı bir sayı (0–7); her biri için izinleri `rwx` biçiminde (eksik izin `-`) yazdır.

```starter
foreach ($satir in $Girdi) {
    $satir
}
```

```stdin
7
5
0
```

```test
eq(run("7\n5\n0\n6\n"), "rwx\nr-x\n---\n-wx\n", "dört izin (6 = Yaz + Calistir)")
ok("[Flags()]" in src or "[Flags]" in src, "[Flags()] enum kullan")
```

```solution
[Flags()] enum Izin { Yok = 0; Oku = 1; Yaz = 2; Calistir = 4 }
foreach ($satir in $Girdi) {
    $i = [Izin][int]$satir
    $metin = ""
    $metin += if ($i.HasFlag([Izin]::Oku)) { "r" } else { "-" }
    $metin += if ($i.HasFlag([Izin]::Yaz)) { "w" } else { "-" }
    $metin += if ($i.HasFlag([Izin]::Calistir)) { "x" } else { "-" }
    $metin
}
```

```hint
Sayıyı enum'a çevir: `[Izin][int]$satir`; her biti `.HasFlag([Izin]::Oku)` ile sına.
```

```hint
Dikkat: buradaki sıra Unix'teki gibi r=4 değil; bu enum'da `Oku = 1`. Çıktı yine `r`, `w`, `x` sırasıyla yazılır.
```
:::
