---
id: rx12
title: Değiştirme ve Bölme Ustalığı
summary: Değiştirme metni bir şablondur; \g<ad>, \g<0>, \g<1>0 belirsizliği, sıfır genişlikli eşleşmeyle araya ekleme, araçlara göre şablon sözdizimi ve ayıracı koruyarak bölmek.
---

::: anlat Değiştirme metni bir şablondur
RX05'te `\1` ile grupları yeniden sıraladın. Değiştirme metni küçük bir şablon dilidir; Python'da tam takımı şudur:

| Şablonda | Anlamı |
|---|---|
| `\1` … `\99` | numaralı grubun metni |
| `\g<1>` | aynısı, ama sınırı açık: `\g<1>0` "1. grup ve ardından 0" demektir; `\10` ise 10. grup |
| `\g<ad>` | adlı grubun metni |
| `\g<0>` | eşleşmenin tamamı |
| `\\` | düz ters eğik çizgi |

```python
import re
re.sub(r"(?P<gun>\d{2})\.(?P<ay>\d{2})\.(?P<yil>\d{4})", r"\g<yil>-\g<ay>-\g<gun>", "19.10.2026")  # '2026-10-19'
re.sub(r"\d+", r"[\g<0>]", "port 80 ve 443")                                                   # 'port [80] ve [443]'
```

Adlı gruplar değiştirmede de okunurluk kazandırır: `\3-\2-\1` yerine `\g<yil>-\g<ay>-\g<gun>` neyin nereye gittiğini söyler.

### Her araçta aynı fikir, farklı yazım
| Araç | Grup | Adlı grup | Eşleşmenin tamamı |
|---|---|---|---|
| Python `re.sub` | `\1`, `\g<1>` | `\g<ad>` | `\g<0>` |
| sed | `\1` | yok | `&` |
| PowerShell `-replace` | `$1` | `${ad}` | `$0` |
| JavaScript `replace` | `$1` | `$<ad>` | `$&` |
| Splunk `rex mode=sed` | `\1` | yok | `&` |

```bash
echo 19.10.2026 | sed -E 's/([0-9]{2})\.([0-9]{2})\.([0-9]{4})/\3-\2-\1/'   # 2026-10-19
```

```powershell
'port 80 ve 443' -replace '\d+', '[$0]'     # port [80] ve [443]
```

> [!TUZAK]
> PowerShell'de değiştirme metnini **tek tırnakla** yaz. Çift tırnak içinde `$1` PowerShell değişkeni sanılır ve boş metne dönüşür; regex onu hiç görmez.
:::

::: anlat Sıfır genişlikli eşleşmeyle araya eklemek
Bakınmalar karakter tüketmediği için bir **konum** eşleşir. Konumu değiştirmek, oraya bir şey **eklemek** demektir. Binlik ayırıcı klasik örnektir: "solunda rakam olan ve sağında üçün katı kadar rakam kalan" her konuma nokta koy:

```python
re.sub(r"(?<=\d)(?=(?:\d{3})+\b)", ".", "Toplam 1500 TL ve 1000000 TL")
# 'Toplam 1.500 TL ve 1.000.000 TL'
```

`(?=(?:\d{3})+\b)` sağda 3, 6, 9… rakam kalıp ardından kelime sınırı gelmesini ister; `(?<=\d)` sayının en başına nokta konmasını engeller.

### Bölmek
`re.split` deseni ayırıcı olarak kullanır. Ayırıcı bir **yakalayan grup** içindeyse, ayırıcılar da sonuca girer:

```python
re.split(r"\s*[,;]\s*", "a, b;c ,d")   # ['a', 'b', 'c', 'd']
re.split(r"([,;])", "a,b;c")          # ['a', ',', 'b', ';', 'c']
```

Ayırıcıyı korumak istemiyorsan grubu `(?:...)` yap; istiyorsan yakala.

> [!NOT]
> Boş eşleşebilen bir desen her konumda eşleşir: `re.sub("x*", "-", "abc")` sonucu `-a-b-c-` olur. Değiştirme ya da bölme beklenmedik yerlere bir şey koyuyorsa, desenin boş metni eşleyip eşlemediğine bak.
:::

::: tahmin
Bu desen `degistir(metin, "***")` ile port numaralarını gizlemek için kullanılacak. Önce neleri yakalar?

```regex
(?<=:)\d+
```

```stdin
web:80 db:5432 cache
```

???

`80` ve `5432`. Geriye bakınma iki noktayı eşleşmeye katmaz, bu yüzden değiştirince iki nokta yerinde kalır: `web:*** db:*** cache`. `cache`'in ardında iki nokta ve rakam olmadığı için ona dokunulmaz.
:::

::: gorev Adlı gruplarla tarih çevir
Testler `degistir(metin, r"\g<yil>-\g<ay>-\g<gun>")` çağıracak. `GG.AA.YYYY` ya da `GG/AA/YYYY` biçimindeki tarihleri yakalayan, `gun`, `ay`, `yil` adlı grupları olan bir desen yaz. İki ayırıcı **aynı** olmalı: `19/10.2026` bir tarih sayılmaz ve olduğu gibi kalır.

```starter
(\d{2})[./](\d{2})[./](\d{4})
```

```test
ok({"gun", "ay", "yil"} <= set(rx.groupindex), "gun, ay, yil adlı grupları olmalı")
eq(degistir("19.10.2026", r"\g<yil>-\g<ay>-\g<gun>"), "2026-10-19", "noktalı tarih")
eq(degistir("Kayıt 01/02/2025, bitiş 31.12.2024", r"\g<yil>-\g<ay>-\g<gun>"), "Kayıt 2025-02-01, bitiş 2024-12-31", "iki biçim bir arada")
eq(degistir("hatalı 19/10.2026", r"\g<yil>-\g<ay>-\g<gun>"), "hatalı 19/10.2026", "karışık ayırıcı değişmez")
```

```solution
(?P<gun>\d{2})(?P<ayr>[./])(?P<ay>\d{2})(?P=ayr)(?P<yil>\d{4})
```

```hint
Grupları adlandır: `(?P<gun>\d{2})`. Ayırıcıyı da bir gruba al ki ikinci kez aynısını isteyebilesin.
```

```hint
RX06'daki geri başvuru: ilk ayırıcı `(?P<ayr>[./])`, ikinci ayırıcı `(?P=ayr)`.
```
:::

::: gorev Binlik ayırıcı
Testler `degistir(metin, ".")` çağıracak. Dört ve daha uzun basamaklı sayılara binlik ayırıcı ekleyecek bir desen yaz: desen hiçbir karakter tüketmemeli, yalnızca noktanın konacağı **konumları** eşlemeli.

```starter
\d{3}
```

```test
eq(degistir("1234567", "."), "1.234.567", "yedi basamak")
eq(degistir("Toplam 1500 TL, 999 TL ve 1000000 TL", "."), "Toplam 1.500 TL, 999 TL ve 1.000.000 TL", "metin içinde")
eq(bul("12345"), [""], "tek bir konum, sıfır genişlikli")
```

```solution
(?<=\d)(?=(?:\d{3})+\b)
```

```hint
Bir konum eşleyeceksin: solunda rakam olsun `(?<=\d)`, sağında üçlü gruplar ve ardından sayı bitsin.
```

```hint
Sağ taraf: `(?=(?:\d{3})+\b)`.
```
:::

::: gorev Ayıracı koruyarak böl
Testler `bol(metin)` çağıracak. Bir derleme hattındaki komutları `&&`, `||` ve `;` işleçlerinden böl; **işleçler de sonuçta kalsın**, çevrelerindeki boşluklar kalmasın.

```starter
\s*(?:&&|\|\||;)\s*
```

```test
eq(bol("derle && test || geri_al ; temizle"), ["derle", "&&", "test", "||", "geri_al", ";", "temizle"], "komutlar ve işleçler")
eq(bol("a&&b"), ["a", "&&", "b"], "boşluksuz")
```

```solution
\s*(&&|\|\||;)\s*
```

```hint
`re.split`, ayırıcı bir yakalayan grubun içindeyse onu da sonuca koyar. `(?:...)` grubunu yakalayan grup yap.
```
:::
