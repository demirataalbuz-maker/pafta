---
id: js10
title: Metin, Sayı ve Tarih Tuzakları
summary: parseInt ile Number farkı, NaN, kayan nokta, varsayılan sort'un metin sıralaması, JavaScript regex'leri (bayraklar, adlı gruplar, matchAll, replace), split ve replace incelikleri, Date'in sıfırdan başlayan ayları ve saat dilimi.
---

::: anlat Sayılar
JavaScript'te tek bir sayı türü vardır (64 bit kayan nokta) ve metinden sayıya dönüşümün birkaç yolu farklı davranır:

| İfade | Sonuç | Neden |
|---|---|---|
| `parseInt("12px")` | 12 | baştan sayı olarak okuyabildiği kadarını alır |
| `Number("12px")` | `NaN` | metnin **tamamı** sayı olmalı |
| `Number("")` | 0 | boş metin 0 sayılır! |
| `parseInt("0x1F")` | 31 | `0x` önekini onaltılık okur |
| `parseInt("08")` | 8 | modern motorlarda onluk; eski kodda `parseInt(x, 10)` görürsün |
| `0.1 + 0.2 === 0.3` | `false` | kayan nokta: 0.30000000000000004 |
| `NaN === NaN` | `false` | NaN hiçbir şeye eşit değildir: `Number.isNaN(x)` kullan |

Tam sayılar `Number.MAX_SAFE_INTEGER`'a (2⁵³ − 1) kadar kesindir. Veritabanı kimlikleri ya da 64 bitlik sayılar bunu aşabilir; JSON'dan gelen büyük bir kimliğin son haneleri sessizce değişebilir. Bunun için `BigInt` (`123n`) vardır.

### sort metin olarak sıralar
`Array.prototype.sort` karşılaştırma fonksiyonu verilmezse elemanları **metne çevirip** sıralar:

```javascript
console.log([10, 9, 1, 100].sort().join(","));                   // 1,10,100,9
console.log([10, 9, 1, 100].sort((a, b) => a - b).join(","));    // 1,9,10,100
```
:::

::: anlat Regex, metin ve tarih
JavaScript regex'leri Regex yolundaki sözdizimini kullanır (RX16: PCRE'ye yakın, `(?<ad>...)` adlı gruplarla):

| Yazım | Anlamı |
|---|---|
| `/desen/g` | bütün eşleşmeler (`g` olmadan yalnızca ilki) |
| `/desen/i`, `/m`, `/s` | büyük-küçük harf, çok satır, nokta satır sonunu da alır |
| `m.groups.ad` | adlı grubun değeri |
| `metin.matchAll(/.../g)` | bütün eşleşmeler, gruplarıyla |
| `metin.replace(/(\d+)-(\d+)/, "$2-$1")` | `$1`, `$<ad>` ile değiştirme |

```javascript
const metin = "09:12 web01 durum=500\n09:15 web02 durum=200";
for (const m of metin.matchAll(/^(?<saat>\S+) (?<sunucu>\S+) durum=(?<durum>\d+)$/gm)) {
  console.log(m.groups.sunucu, Number(m.groups.durum));
}
console.log("aaa".replace("a", "b"), "aaa".replaceAll("a", "b"));   // baa bbb: metinle replace yalnızca ilkini değiştirir
```

### Date
| Tuzak | Ayrıntı |
|---|---|
| aylar **0'dan** başlar | `new Date(2026, 9, 19)` 19 **Ekim**'dir; `getMonth()` 9 döndürür |
| yerel saat ile UTC | `getHours()` makinenin saat dilimine göre, `getUTCHours()` UTC'ye göre |
| metinden ayrıştırma | `new Date("2026-10-19")` UTC gece yarısı, `new Date("2026-10-19T08:00")` yerel saat |

Günlüklerdeki zamanları karşılaştıran kodda her şeyi UTC'de tut: `Date.UTC(...)`, `getUTC...()`, `toISOString()`.
:::

::: tahmin
İki satır yazar:

```javascript
console.log(parseInt("08"), parseInt("0x1F"), parseInt("12px"), Number("12px"), Number(""));
console.log(new Date(2026, 9, 19).getMonth(), [10, 9, 1].sort().join(","));
```

???

`8 31 12 NaN 0` ve `9 1,10,9`. `parseInt` baştan okuyabildiği kadarını alır, `Number` metnin tamamını ister; boş metin ise 0'dır. Ekim ayının indeksi 9'dur. `sort` sayıları metin olarak sıralar: "1" < "10" < "9".
:::

::: gorev Sayısal sıralama
Yanıt sürelerini **küçükten büyüğe** sayısal olarak sırala ve virgülle birleştirip yazdır.

```starter
const sureler = [120, 95, 2300, 40, 850, 1200];
console.log(sureler.sort().join(","));
```

```test
eq(out, "40,95,120,850,1200,2300\n", "sayısal sıralama")
```

```solution
const sureler = [120, 95, 2300, 40, 850, 1200];
console.log(sureler.sort((a, b) => a - b).join(","));
```

```hint
Karşılaştırma fonksiyonu: `(a, b) => a - b`. Negatif dönerse `a` önce gelir.
```
:::

::: gorev Satırları ayrıştır
Aşağıdaki metinden `SS:DD sunucu durum=NNN` biçimindeki satırları `matchAll` ve adlı gruplarla ayrıştır; her satır için `{saat, sunucu, durum}` nesnesi kur (`durum` **sayı** olsun), bozuk satırları atla ve diziyi `JSON.stringify` ile tek satırda yazdır.

```starter
const metin = "09:12 web01 durum=500\n09:15 web02 durum=200\nbozuk satir\n10:42 web02 durum=500";
console.log(JSON.stringify(metin.split("\n")));
```

```test
eq(out, '[{"saat":"09:12","sunucu":"web01","durum":500},{"saat":"09:15","sunucu":"web02","durum":200},{"saat":"10:42","sunucu":"web02","durum":500}]\n', "üç kayıt")
ok("matchAll" in src, "matchAll kullan")
```

```solution
const metin = "09:12 web01 durum=500\n09:15 web02 durum=200\nbozuk satir\n10:42 web02 durum=500";
const desen = /^(?<saat>\d{2}:\d{2}) (?<sunucu>\S+) durum=(?<durum>\d+)$/gm;
const kayitlar = [...metin.matchAll(desen)].map(m => ({ ...m.groups, durum: Number(m.groups.durum) }));
console.log(JSON.stringify(kayitlar));
```

```hint
`^` ve `$`'ın her satırda çalışması için `m`, bütün eşleşmeler için `g` bayrağı: `/^...$/gm`.
```

```hint
`[...metin.matchAll(desen)].map(m => ({ ...m.groups, durum: Number(m.groups.durum) }))`.
```
:::

::: gorev Tarih biçimi
UTC olarak verilen `2026-10-05 08:07` anını `GG.AA.YYYY SS:DD` biçiminde (`05.10.2026 08:07`) yazdır. Başlangıç kodunda iki hata var.

```starter
const t = new Date(Date.UTC(2026, 9, 5, 8, 7));
console.log(`${t.getUTCDate()}.${t.getUTCMonth()}.${t.getUTCFullYear()} ${t.getUTCHours()}:${t.getUTCMinutes()}`);
```

```test
eq(out, "05.10.2026 08:07\n", "iki haneli alanlar, doğru ay")
```

```solution
const t = new Date(Date.UTC(2026, 9, 5, 8, 7));
const p = n => String(n).padStart(2, "0");
console.log(`${p(t.getUTCDate())}.${p(t.getUTCMonth() + 1)}.${t.getUTCFullYear()} ${p(t.getUTCHours())}:${p(t.getUTCMinutes())}`);
```

```hint
Ay 0'dan başlar: `getUTCMonth() + 1`.
```

```hint
Tek haneli değerleri iki haneye tamamla: `String(n).padStart(2, "0")`.
```
:::
