---
id: sp01
title: Aramak
summary: sourcetype ile kaynak seçmek, alan=değer aramaları, joker karakter, serbest metin, AND/OR/NOT ve Splunk'ın şaşırtan öncelik kuralı.
---

::: anlat Bir arama, bir boru hattı
Splunk'ta her şey bir **arama** ile başlar. Aramanın ilk kısmı olayları seçer; ardından `|` ile komutlar gelir ve her komut bir öncekinin sonucunu işler:

```spl
sourcetype=sunucular cpu>70        #! kaynak ve süzgeç
| table ad cpu                     #! alan seç
```

Gerçek Splunk'ta olaylar **index**'lerde durur ve `sourcetype` olayın türünü söyler (ör. `index=web sourcetype=access_combined`). Bu tezgahta SQL yolunun BT operasyonu veritabanını kullanıyoruz: her tablo bir sourcetype'tır (`sunucular`, `biletler`, `personel`, `ekipler`, `olcumler`) ve hepsi `index=ops` içindedir. `index`'i yazmak isteğe bağlı:

```spl
index=ops sourcetype=biletler
| head 3
```

### Arama yazımı
| Yazım | Anlamı |
|---|---|
| `alan=değer` | eşit; **büyük-küçük harfe duyarsız**: `rol=WEB` web'i bulur |
| `alan=web*` | `*` joker karakter |
| `alan!=değer` | eşit değil (**alanı olmayan olayları almaz**) |
| `alan>80`, `<`, `>=`, `<=` | sayısal karşılaştırma |
| `disk` | serbest metin: herhangi bir alanda geçiyorsa |
| `"iki kelime"` | boşluk içeren değer ya da ifade |
| `A B` | ikisi birden (AND örtüktür) |
| `A OR B`, `NOT A` | biri ya da diğeri; değil |

```spl
sourcetype=sunucular rol=web sehir=İstanbul
| table ad sehir cpu

sourcetype=sunucular isletim="Windows*"
| table ad isletim

sourcetype=biletler disk
| table id baslik durum
```

> [!TUZAK]
> `OR`, `AND` ve `NOT` yalnızca **büyük harfle** işleçtir. `durum=açık or oncelik=kritik` yazarsan Splunk "or" kelimesini arayan bir **serbest metin terimi** sanır ve hiçbir şey bulamaz.

> [!TUZAK]
> Splunk'ın `search` komutunda **OR, AND'den önce bağlanır**; SQL'in tam tersi. `durum=açık oncelik=yüksek OR oncelik=kritik` demek `durum=açık AND (oncelik=yüksek OR oncelik=kritik)` demektir. Karışık koşullarda parantez kullan.

> [!DERİN]
> `sehir!=İstanbul` ile `NOT sehir=İstanbul` aynı değildir. `!=` yalnızca `sehir` alanı **olan** olaylara bakar. `NOT` ise alanı hiç olmayanları da getirir. Bu veride bulutta çalışan üç sunucunun şehri yok; ilki 5, ikincisi 8 sunucu döndürür.
:::

::: tahmin
Tek bir sayı:

```spl
sourcetype=biletler durum=açık oncelik=yüksek OR oncelik=kritik
| stats count
```

???

`3`. Splunk'ta OR önce bağlanır: arama "durum açık **ve** (öncelik yüksek **ya da** kritik)" anlamına gelir. Açık yüksek öncelikli üç bilet var (5, 9, 20); kritik biletlerin hepsi çözülmüş. SQL alışkanlığıyla "açık-yüksekler ya da bütün kritikler" diye okusaydın 6 derdin.
:::

::: gorev İstanbul'daki web sunucuları
İstanbul'daki **web** sunucularının yalnızca adını getir.

```starter
sourcetype=sunucular rol=web
| table ad
```

```test
eq(sutunlar, ["ad"], "yalnızca ad alanı")
eq(sorted(r[0] for r in sonuc), ["web01", "web02"], "web01 ve web02")
```

```solution
sourcetype=sunucular rol=web sehir=İstanbul
| table ad
```

```hint
Terimleri yan yana yazmak AND demektir: `rol=web sehir=İstanbul`.
```
:::

::: gorev Ubuntu sunucuları
İşletim sistemi **Ubuntu** ile başlayan sunucuların `ad` ve `isletim` alanlarını getir.

```starter
sourcetype=sunucular isletim=Ubuntu
| table ad isletim
```

```test
eq(sutunlar, ["ad", "isletim"], "alanlar: ad, isletim")
eq(sorted(r[0] for r in sonuc), ["cache01", "izleme01", "test01", "web01", "web02", "web03"], "altı Ubuntu sunucusu")
```

```solution
sourcetype=sunucular isletim="Ubuntu*"
| table ad isletim
```

```hint
`isletim=Ubuntu` tam eşitlik ister; değerler "Ubuntu 24.04" gibi. Joker karakter: `isletim="Ubuntu*"`.
```
:::

::: gorev İstanbul dışındakiler, bulut dahil
Şehri İstanbul **olmayan** bütün sunucuların adını getir; şehri hiç olmayan (bulutta çalışan) sunucular da listede olsun.

```starter
sourcetype=sunucular sehir!=İstanbul
| table ad
```

```test
eq(len(sonuc), 8, "8 sunucu")
ok(("cache01",) in sonuc, "buluttaki cache01 de listede", got=sonuc)
```

```solution
sourcetype=sunucular NOT sehir=İstanbul
| table ad
```

```hint
`!=` şehri olmayan olayları dışarıda bırakır. `NOT sehir=İstanbul` onları da kapsar.
```
:::
