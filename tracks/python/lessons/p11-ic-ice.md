---
id: p11
title: İç İçe Döngüler ve Döngü-else
summary: Döngü içinde döngü, break'in kapsamı ve Python'a özgü for/while ... else.
---

::: anlat Döngü içinde döngü
Bir döngünün bloğunda başka bir döngü olabilir. İçteki döngü, dıştakinin **her turunda baştan sona** çalışır:

```python
for satir in range(1, 4):
    for sutun in range(1, 4):
        print(satir * sutun, end="\t")   #! \t sekme: sütunları hizalar
    print()                              #! iç döngü bitti → satır sonu
```

Dış döngü 3, iç döngü 3 tur → toplam **9** kez çalışır. 1000 × 1000'lik iç içe döngü bir milyon tur eder: iç içe döngüler hızla pahalılaşır. Bu bedeli P64'te "karmaşıklık" (Big-O) olarak ölçeceğiz.

Tipik kullanımlar: tablo/ızgara dolaşmak, **her çifti** karşılaştırmak, desen çizmek.

```python
kullanicilar = ["ali", "veli", "ali", "ayse"]
for i in range(len(kullanicilar)):
    for j in range(i + 1, len(kullanicilar)):   #! j hep i'den sonra: her çift bir kez
        if kullanicilar[i] == kullanicilar[j]:
            print("tekrar:", kullanicilar[i], "→ konum", i, "ve", j)
```

> [!TUZAK]
> `break` sadece **içinde bulunduğu** döngüden çıkar. İç döngüde `break` dersen dış döngü devam eder. İki döngüden birden çıkmak istiyorsan ya bir bayrak kullan ya da kodu bir fonksiyona koyup `return` et (P20).
:::

::: tahmin
Çıktı üç satır (satır sonlarındaki boşlukları önemseme):

```python
for i in range(1, 4):
    for j in range(1, 4):
        if j > i:
            break
        print(i * j, end=" ")
    print()
```

???

```cikti
1
2 4
3 6 9
```

Her satırda j, i'yi geçince iç döngü kırılır ama dış döngü devam eder. Böylece bir **üçgen** oluşur.
:::

::: anlat Döngü-else: "hiç break olmadıysa"
Python'un pek bilinmeyen bir özelliği: `for` ve `while` döngülerinin de bir `else` dalı olabilir. Bu dal, döngü **break ile kesilmeden** normal biçimde bittiğinde çalışır.

Klasik kullanım **arama**dır: "aradığımı bulursam break; hiç bulamazsam else":

```python
yasakli = ["root", "admin", "test"]
kullanici = "ayse"
for y in yasakli:
    if kullanici == y:
        print("yasaklı kullanıcı adı!")
        break
else:                              #! döngü break'siz bitti = hiç eşleşme yok
    print(kullanici, "kullanılabilir")
```

Döngü-else olmasaydı bir bayrak gerekirdi:

```python norun
bulundu = False
for y in yasakli:
    if kullanici == y:
        bulundu = True
        break
if not bulundu:
    print("kullanılabilir")
```

> [!NOT]
> Bu `else` adı kötü seçilmiştir; Python'un yaratıcısı Guido da bunu kabul eder. Kafanda "**nobreak**" diye oku: `for ... nobreak:`. P09'daki hesap kilidi görevini `while ... else` ile çözdüysen zaten kullandın.
:::

::: tahmin
Ne yazdırır?

```python
for n in [3, 5, 7]:
    if n % 2 == 0:
        print("çift bulundu")
        break
else:
    print("çift yok")
```

???

`çift yok`. Listedeki hiçbir sayı çift olmadığı için `break` hiç çalışmaz; döngü normal biter ve `else` dalı çalışır.
:::

::: gorev Yıldız üçgeni
Girdiden n oku ve n satırlık bir üçgen çiz: 1. satırda 1 yıldız, n. satırda n yıldız. **İç içe döngü** kullan (`"*" * i` hilesi yok).

```cikti
*
**
***
```

```starter
n = int(input())

```

```stdin
3
```

```test
eq(run("3").strip().splitlines(), ["*", "**", "***"], "3 → üç satır")
eq(run("5").strip().splitlines(), ["*" * i for i in range(1, 6)], "5 → beş satır")
ok(sum(1 for node in __import__("ast").walk(tree) if isinstance(node, __import__("ast").For)) >= 2, "İki for döngüsü (iç içe) kullan")
ok('"*" *' not in src and "'*' *" not in src and '* "*"' not in src, "Metin çarpma hilesi olmadan, döngüyle çiz")
```

```solution
n = int(input())
for i in range(1, n + 1):
    for j in range(i):
        print("*", end="")
    print()
```

```hint
Dış döngü satırları (1..n), iç döngü o satırdaki yıldızları basar. Satır sonunda boş `print()`.
```
:::

::: gorev İlk tekrar eden karakter
Girdiden bir metin oku. Soldan sağa bakıldığında, metinde **daha sonra tekrar geçen ilk karakteri** yazdır. Yoksa `yok` yaz. İç içe döngü ve döngü-else kullan.

- `abcdbe` → `b`
- `abccba` → `a` (a sonda tekrar geçiyor)
- `abc` → `yok`

```starter
metin = input()

```

```stdin
abcdbe
```

```test
eq(run("abcdbe").strip(), "b", "abcdbe → b")
eq(run("abccba").strip(), "a", "abccba → a")
eq(run("abc").strip(), "yok", "abc → yok")
eq(run("aa").strip(), "a", "aa → a")
eq(run("x").strip(), "yok", "x → yok")
```

```solution
metin = input()
for i in range(len(metin)):
    for j in range(i + 1, len(metin)):
        if metin[i] == metin[j]:
            break
    else:
        continue
    print(metin[i])
    break
else:
    print("yok")
```

```hint
Her i için, i'den sonraki j'lere bak. Eşleşme bulursan cevabı yazıp **iki döngüden de** çıkman lazım.
```

```hint
Hile: iç döngünün `else: continue` dalı "eşleşme yoksa dış döngüye devam et" der. İç döngü break ile biterse continue atlanır ve alttaki satırlar çalışır.
```
:::

::: gorev Asal listesi
Girdiden n oku ve n'ye kadar (n dahil) bütün asal sayıları aralarında boşlukla tek satırda yazdır. İç içe döngü ve döngü-else kullan.

```cikti
2 3 5 7 11 13 17 19
```

```starter
n = int(input())

```

```stdin
20
```

```test
eq(run("20").split(), ["2", "3", "5", "7", "11", "13", "17", "19"], "20 → 2 3 5 7 11 13 17 19")
eq(run("2").split(), ["2"], "2 → 2")
eq(run("1").split(), [], "1 → boş")
eq(len(run("1000").split()), 168, "1000'e kadar 168 asal var")
```

```solution
n = int(input())
for sayi in range(2, n + 1):
    for b in range(2, int(sayi ** 0.5) + 1):
        if sayi % b == 0:
            break
    else:
        print(sayi, end=" ")
print()
```

```hint
Dış döngü 2..n arası her sayı, iç döngü olası bölenler. İç döngü break'siz biterse (else) sayı asaldır.
```
:::
