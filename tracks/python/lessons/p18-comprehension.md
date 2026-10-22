---
id: p18
title: Liste, Sözlük ve Küme Üreteçleri
summary: comprehension sözdizimi; filtre, dönüşüm, iç içe yapılar, any/all ve okunabilirlik sınırı.
kazanim: PCEP 3.1, PCAP 5.1
---

::: anlat Döngüyü tek ifadeye sıkıştırmak
"Bir diziyi dolaş, her elemanı dönüştür, bazılarını süz, sonuçları bir listeye topla" kalıbı o kadar yaygındır ki Python'un özel bir sözdizimi vardır: **liste üreteci** (list comprehension).

```python
# klasik döngü
kareler = []
for x in range(10):
    if x % 2 == 0:
        kareler.append(x * x)

# aynısı, tek ifade
kareler = [x * x for x in range(10) if x % 2 == 0]
#          ─────  ──────────────────  ─────────────
#          ifade        döngü           süzgeç
print(kareler)
```

Okuma sırası: "**x için x*x, x range(10)'dan geliyorsa, x çiftse**". Süzgeç (`if`) isteğe bağlıdır.

Aynı sözdizimi sözlük ve küme için de vardır:

```python
portlar = {"ssh": 22, "http": 80, "https": 443}
ters = {p: ad for ad, p in portlar.items()}              #! sözlük üreteci
print(ters)
uzunluklar = {len(k) for k in ["ssh", "ftp", "https"]}   #! küme üreteci
print(uzunluklar)
temiz = [s.strip().lower() for s in ["  Ali ", "VELI", " ayse"]]
print(temiz)
etiket = ["çift" if n % 2 == 0 else "tek" for n in range(4)]   #! koşullu ifade, süzgeç değil
print(etiket)
```

> [!TUZAK]
> Konuma dikkat: sondaki `if` **süzer** (elemanı alır ya da atar). Baştaki `A if koşul else B` ise her elemanı **dönüştürür** (hiçbir elemanı atmaz). `[x for x in l if x > 0]` ile `[x if x > 0 else 0 for x in l]` farklı şeylerdir.

> [!DERİN]
> Üreteçler sadece kısa değil, genelde daha **hızlıdır**: döngüde her turda `kareler.append` niteliği aranır ve çağrılır; üreteç ise doğrudan `LIST_APPEND` bytecode'unu kullanır. Ayrıca Python 3'te üretecin döngü değişkeni dışarı **sızmaz**: üreteç kendi küçük kapsamında çalışır (3.12'den beri satır içine alınmış olarak).
:::

::: tahmin
İki satır:

```python
print([x * x for x in range(6) if x % 2 == 0])
print({k: len(k) for k in ["ssh", "http"]})
```

???

`[0, 4, 16]`, sonra `{'ssh': 3, 'http': 4}`. range(6) içindeki çift sayılar 0, 2, 4'tür; kareleri 0, 4, 16 eder.
:::

::: anlat İç içe üreteçler, any ve all
Birden fazla `for` yazabilirsin. Sıralama, iç içe döngüyü yazacağın sırayla aynıdır:

```python
matris = [[1, 2, 3], [4, 5, 6]]
duz = [x for satir in matris for x in satir]       #! önce dış, sonra iç döngü
print(duz)
ciftler = [(h, p) for h in ["web", "db"] for p in [22, 443]]
print(ciftler)
transpoz = [[satir[i] for satir in matris] for i in range(3)]   #! üreteç içinde üreteç
print(transpoz)
```

**`any`** ve **`all`** ile birleşince güçlü sorgulara dönüşür. Köşeli parantezsiz yazılan `(x for x in ...)` bir **üreteç ifadesidir**: liste kurmadan elemanları tek tek üretir ve `any` sonucu bulduğu an durur.

```python
loglar = ["OK login ali", "FAIL login root", "OK logout ali"]
print(any("FAIL" in s for s in loglar))          #! en az biri FAIL içeriyor mu
print(all(s.startswith(("OK", "FAIL")) for s in loglar))
print(sum(1 for s in loglar if s.startswith("OK")))   #! koşulu sağlayanları say
```

### Ne zaman üreteç YAZMAMALI
Üç `for` ve iki `if` içeren tek satırlık bir üreteç zekice görünür ama **okunmaz**. Kural: bir ifade tek bakışta anlaşılmıyorsa normal döngüye dön. Yan etki için (print gibi) de üreteç kullanma: `[print(x) for x in l]` gereksiz bir `None` listesi üretir.

> [!ZEN]
> Okunabilirlik önemlidir. (*Readability counts.*)
:::

::: tahmin
İki satır:

```python
m = [[1, 2], [3, 4], [5, 6]]
print([x for satir in m for x in satir if x % 3])
print(all(len(s) > 2 for s in ["abc", "de"]))
```

???

`[1, 2, 4, 5]`, sonra `False`. `x % 3` 3'e bölünemeyenlerde sıfırdan farklıdır, yani doğru sayılır; 3 ve 6 elenir. `"de"` 2 karakter olduğu için `all` yanlış döner.
:::

::: gorev Uzun kelimeler
Girdiden boşlukla ayrılmış kelimeler oku. 3 karakterden **uzun** olanları büyük harfe çevirip bir **liste** olarak yazdır. Tek bir liste üreteciyle çöz.

```cikti
['PYTHON', 'GÜÇLÜ']
```

```starter
kelimeler = input().split()

```

```stdin
python çok güçlü bir dil
```

```test
eq(run("python çok güçlü bir dil").strip(), "['PYTHON', 'GÜÇLÜ']", "örnek")
eq(run("a bb ccc").strip(), "[]", "uzun kelime yok → []")
eq(run("tarama rapor log").strip(), "['TARAMA', 'RAPOR']", "log 3 harf, alınmaz")
ok(uses("listcomp"), "Liste üreteci kullan")
ok(not uses("for") or uses("listcomp"), "Düz for döngüsü yerine üreteç")
```

```solution
kelimeler = input().split()
print([k.upper() for k in kelimeler if len(k) > 3])
```

```hint
`[ifade for k in kelimeler if koşul]`
```
:::

::: gorev Çerez ayrıştırıcı
Girdide bir HTTP çerez satırı var: `ad=değer` çiftleri `;` ile ayrılmış. Bunu bir **sözlük üreteciyle** sözlüğe çevirip yazdır. Çiftlerin kenarlarındaki boşlukları temizle.

```cikti
{'oturum': 'abc123', 'dil': 'tr', 'tema': 'koyu'}
```

```starter
satir = input()

```

```stdin
oturum=abc123; dil=tr; tema=koyu
```

```test
eq(run("oturum=abc123; dil=tr; tema=koyu").strip(), "{'oturum': 'abc123', 'dil': 'tr', 'tema': 'koyu'}", "örnek")
eq(run("a=1").strip(), "{'a': '1'}", "tek çift")
eq(run("token=x=y; id=7").strip(), "{'token': 'x=y', 'id': '7'}", "değerin içinde = olabilir (split'i 1 ile sınırla)")
ok(uses("dictcomp"), "Sözlük üreteci kullan")
```

```solution
satir = input()
cerez = {p.split("=", 1)[0].strip(): p.split("=", 1)[1].strip() for p in satir.split(";")}
print(cerez)
```

```hint
Önce `;` ile böl, sonra her parçayı `=` ile **en fazla bir kez** böl: `parca.split("=", 1)`.
```
:::

::: gorev Port birleştir
Girdide host'ların port listeleri var: host'lar `;` ile, portlar `,` ile ayrılmış. Tüm portları **tekrarsız ve küçükten büyüğe** sıralı tam sayı listesi olarak yazdır. İç içe bir üreteç kullan.

```cikti
[22, 80, 443]
```

```starter
satir = input()

```

```stdin
22,80;80,443;22
```

```test
eq(run("22,80;80,443;22").strip(), "[22, 80, 443]", "örnek")
eq(run("9,100;10").strip(), "[9, 10, 100]", "sayısal sıralama")
eq(run("53").strip(), "[53]", "tek port")
ok(uses("comp"), "Üreteç (comprehension) kullan")
```

```solution
satir = input()
print(sorted({int(p) for host in satir.split(";") for p in host.split(",")}))
```

```hint
`{int(p) for host in ... for p in ...}` bir küme üretecidir; sonra `sorted(...)`.
```
:::
