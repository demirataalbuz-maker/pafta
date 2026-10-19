---
id: bs16
title: Süreçler, İşler ve Sinyaller
summary: & ile arka plan, wait ve $!, paralel işler, sinyaller ve trap, EXIT ile temizlik, timeout ve xargs -P.
---

::: anlat Arka planda çalıştırmak
Bir komutun sonuna `&` koymak onu **arka planda** başlatır; kabuk beklemeden sonraki satıra geçer. `$!` son arka plan işinin süreç numarasını (PID), `wait` arka plan işlerinin bitmesini bekler:

```bash
( sleep 0.3; echo "yavaş iş bitti" ) &
pid=$!
echo "ana betik devam ediyor (iş: $pid)"
wait "$pid"
echo "dönüş kodu: $?"
```

Birbirinden bağımsız işleri aynı anda başlatıp hepsini beklemek, toplam süreyi en uzun işin süresine indirir:

```bash
for ad in web01 db01 cache01; do
    ( sleep 0.2; echo "$ad denetlendi" > "sonuc-$ad.txt" ) &
done
wait                                 #! bütün arka plan işlerini bekle
cat sonuc-*.txt
```

`xargs -P N` aynı işi listedeki her eleman için en fazla N paralel süreçle çalıştırır: `printf '%s\n' a b c d | xargs -P 2 -I{} sh -c 'echo işleniyor: {}'`.

### Sinyaller ve trap
Sinyal, işletim sisteminin bir sürece gönderdiği kısa bir bildirimdir:

| Sinyal | Ne zaman | Varsayılan |
|---|---|---|
| `INT` (2) | Ctrl+C | sonlandır |
| `TERM` (15) | `kill PID` | sonlandır (nazikçe) |
| `KILL` (9) | `kill -9 PID` | hemen sonlandır, **yakalanamaz** |
| `HUP` (1) | terminal kapandı; servislerde "ayarı yeniden oku" | sonlandır |

`trap 'komutlar' SİNYAL` bir sinyal geldiğinde ne yapılacağını söyler. Özel bir "sinyal" olan `EXIT`, betik **nasıl biterse bitsin** (normal sonu, `exit`, hata, Ctrl+C) çalışır; temizlik işleri için idealdir:

```bash
gecici=$(mktemp)
trap 'rm -f "$gecici"; echo "temizlendi"' EXIT
echo "veri" > "$gecici"
echo "işlem sürüyor"
```

`timeout SÜRE komut` komutu süre dolunca sonlandırır ve **124** koduyla döner; asılı kalabilecek her dış çağrıyı (ağ, disk) sınırlamak için kullanılır.

> [!TUZAK]
> `kill -9` temizlik şansı vermez: geçici dosyalar, kilitler, yarım yazılmış dosyalar geride kalır. Bir süreci durdururken önce `kill` (TERM) gönder, ancak yanıt vermezse `-9`'a geç.
:::

::: tahmin
Satırlar hangi sırayla yazılır?

```bash
( sleep 0.3; echo B ) &
echo A
wait
echo C
```

???

`A`, `B`, `C`. Arka plan işi 0,3 saniye beklerken ana betik hemen `A` yazar. `wait` arka plan işi bitene kadar bekler; iş `B` yazar, ardından `C` gelir.
:::

::: gorev Paralel denetim
Başlangıçtaki `denetle` fonksiyonu bir sunucuyu yavaşça "denetleyip" sonucu yazıyor. Üç sunucuyu (`web01 db01 cache01`) **paralel** denetle, sonuçları `sonuc-<ad>.txt` dosyalarına yazdır, hepsinin bitmesini bekle ve dosyaları **web01, db01, cache01** sırasıyla ekrana bas.

```starter
denetle() { sleep 0.3; echo "$1: tamam"; }
for ad in web01 db01 cache01; do
    denetle "$ad"
done
```

```test
eq(out, "web01: tamam\ndb01: tamam\ncache01: tamam\n", "üç sonuç, istenen sırayla")
ok("&" in src and "wait" in src, "işleri & ile başlatıp wait ile bekle")
```

```solution
denetle() { sleep 0.3; echo "$1: tamam"; }
for ad in web01 db01 cache01; do
    denetle "$ad" > "sonuc-$ad.txt" &
done
wait
for ad in web01 db01 cache01; do
    cat "sonuc-$ad.txt"
done
```

```hint
Her işin çıktısını kendi dosyasına yönlendirip `&` ile başlat. Paralel işlerin çıktısı karışık sırayla biter; sırayı dosyaları sonradan okuyarak sen belirle.
```
:::

::: gorev Her durumda temizlik
Betik çalışma klasöründe `is.tmp` adlı geçici bir dosya oluşturuyor ve `işlendi` yazdırıyor. 1. argüman `hata` ise burada **3** koduyla çıkıyor, değilse `bitti` yazdırıyor. İki durumda da `is.tmp` sonunda silinmiş olmalı.

```starter
gecici="is.tmp"
echo "ara veri" > "$gecici"
echo "işlendi"
if [[ ${1:-} == hata ]]; then
    exit 3
fi
echo "bitti"
rm -f "$gecici"
```

```test
import os
r = calis()
eq((r["kod"], r["cikti"]), (0, "işlendi\nbitti\n"), "normal yol")
ok(not os.path.exists("is.tmp"), "normal yolda is.tmp silinmiş olmalı")
r = calis(argv=["hata"])
eq((r["kod"], r["cikti"]), (3, "işlendi\n"), "hata yolu: kod 3")
ok(not os.path.exists("is.tmp"), "hata yolunda da is.tmp silinmiş olmalı")
ok("trap" in src, "trap ... EXIT kullan")
```

```solution
gecici="is.tmp"
trap 'rm -f "$gecici"' EXIT
echo "ara veri" > "$gecici"
echo "işlendi"
if [[ ${1:-} == hata ]]; then
    exit 3
fi
echo "bitti"
```

```hint
Sondaki `rm` erken `exit`'te hiç çalışmaz. `trap 'rm -f "$gecici"' EXIT` satırını dosyayı oluşturmadan **önce** yaz; `exit 3`'te de tetiklenir.
```
:::

::: gorev Zaman aşımı
Betik 1. argümanda verilen saniye kadar `sleep` etsin ama bunu **en fazla 1 saniye** beklesin. Süre dolduysa `zaman aşımı`, dolmadıysa `bitti` yazdırsın.

```starter
sleep "$1"
echo "bitti"
```

```meta
argv: 3
timeout: 20
```

```test
eq(out, "zaman aşımı\n", "3 saniyelik iş 1 saniyede kesilir")
eq(run(argv=["0"]), "bitti\n", "anında biten iş")
ok("timeout" in src, "timeout kullan")
```

```solution
timeout 1 sleep "$1"
if [[ $? -eq 124 ]]; then
    echo "zaman aşımı"
else
    echo "bitti"
fi
```

```hint
`timeout 1 komut` süre dolunca komutu keser ve **124** koduyla döner.
```
:::
