---
id: p13
title: Listeler
summary: Sıralı, değiştirilebilir koleksiyon; ekleme, çıkarma, sıralama ve sort/sorted farkı.
kazanim: PCEP 3.1
---

::: anlat Değiştirilebilir sıralı koleksiyon
Liste, köşeli parantez içinde virgülle ayrılmış değerlerdir. Her türden değer tutabilir, iç içe olabilir. İndeksleme ve dilimleme **metinlerdekiyle aynıdır**. Tek fark: listeler **değiştirilebilir** (mutable).

```python
portlar = [22, 80, 443]
print(portlar[0], portlar[-1], portlar[1:])
portlar[1] = 8080            #! metinde yapamazdın; listede serbest
print(portlar, len(portlar), 443 in portlar)
karisik = ["web01", 443, True, [1, 2]]   #! karışık türler ve iç içe liste
print(karisik[3][0])
```

### Eleman ekleme ve çıkarma

| İşlem | Ne yapar |
|---|---|
| `l.append(x)` | sona ekler |
| `l.insert(i, x)` | i konumuna ekler |
| `l.extend(diger)` | başka listenin elemanlarını sona ekler |
| `l.pop()` / `l.pop(i)` | sondakini / i'dekini **çıkarır ve döndürür** |
| `l.remove(x)` | ilk x'i siler (yoksa `ValueError`) |
| `del l[i]` | i'deki elemanı siler |
| `l.index(x)` / `l.count(x)` | konum / kaç tane |

```python
kuyruk = ["tarama", "rapor"]
kuyruk.append("yedek")
kuyruk.insert(0, "acil")
print(kuyruk)
ilk = kuyruk.pop(0)          #! çıkar ve al
print(ilk, kuyruk)
kuyruk.extend(["temizlik", "yedek"])
kuyruk.remove("yedek")       #! sadece İLK yedek silinir
print(kuyruk, kuyruk.count("yedek"))
```

> [!TUZAK]
> `append` ile `extend` farkı: `l.append([1, 2])` listeye **tek bir eleman** (iç liste) ekler, `l.extend([1, 2])` **iki ayrı** eleman ekler.
:::

::: tahmin
Ne yazdırır?

```python
l = [3, 1, 2]
l.append(5)
l.insert(0, 9)
x = l.pop()
print(l, x)
```

???

`[9, 3, 1, 2] 5`. append sona 5 ekler: `[3, 1, 2, 5]`. insert(0, 9) başa 9 koyar: `[9, 3, 1, 2, 5]`. pop() sondaki 5'i çıkarıp döndürür.
:::

::: anlat Sıralama: sort ve sorted
İki yol var ve farkları önemli:

- `liste.sort()` listeyi **yerinde** sıralar ve **`None` döndürür**.
- `sorted(dizi)` **yeni** bir sıralı liste döndürür, orijinale dokunmaz. Her dolaşılabilir şeyle çalışır: metin, demet, küme...

```python
skor = [42, 7, 19, 88]
yeni = sorted(skor)              #! orijinal aynı kalır
print(skor, yeni)
skor.sort(reverse=True)          #! yerinde, büyükten küçüğe
print(skor)
kelimeler = ["Zeytin", "armut", "Elma"]
print(sorted(kelimeler))                 #! büyük harfler önce gelir (Unicode sırası)
print(sorted(kelimeler, key=str.lower))  #! key: her elemanı neye göre karşılaştıracağın
print(sorted(kelimeler, key=len))        #! uzunluğa göre
print(min(skor), max(skor), sum(skor))
```

`key=` parametresine bir **fonksiyon** verirsin: Python her elemanı önce o fonksiyondan geçirir, sıralamayı sonuca göre yapar. Fonksiyonları değer olarak geçirmeyi P23'te derinlemesine göreceğiz.

> [!TUZAK]
> `liste = liste.sort()` yazmak listeyi **yok eder**: sort `None` döndürdüğü için liste ismin artık `None`'ı gösterir. Ya `liste.sort()` ya `liste = sorted(liste)`.

> [!DERİN]
> Python'un sıralama algoritması **Timsort**'tur: Tim Peters 2002'de Python için yazdı, sonra Java ve Android de benimsedi. Gerçek verideki önceden sıralı parçaları ("run") yakalar, bu yüzden neredeyse sıralı veride O(n) kadar hızlıdır. Ayrıca **kararlıdır** (stable): eşit anahtarlı elemanların sırası korunur. Bu yüzden önce ikincil sonra birincil anahtara göre iki kez sıralayarak çok anahtarlı sıralama yapabilirsin.
:::

::: tahmin
İki satır:

```python
a = [3, 1, 2]
b = a.sort()
print(a, b)
c = sorted("pafta")
print(c)
```

???

`[1, 2, 3] None`, sonra `['a', 'a', 'f', 'p', 't']`. `sort` yerinde sıralar ve None döndürür. `sorted` bir metni harflerine ayırıp sıralı **liste** döndürür.
:::

::: gorev Benzersiz IP'ler
Girdiden boşlukla ayrılmış IP adresleri oku. Her IP'yi **ilk görüldüğü sırayla ve bir kez** olacak şekilde virgülle birleştirip yazdır. Kümeleri (set) henüz görmedik; liste ve `not in` ile çöz.

```cikti
10.0.0.1,10.0.0.2,10.0.0.3
```

```starter
ipler = input().split()

```

```stdin
10.0.0.1 10.0.0.2 10.0.0.1 10.0.0.3 10.0.0.2
```

```test
eq(run("10.0.0.1 10.0.0.2 10.0.0.1 10.0.0.3 10.0.0.2").strip(), "10.0.0.1,10.0.0.2,10.0.0.3", "tekrarlar atılır, sıra korunur")
eq(run("1.1.1.1").strip(), "1.1.1.1", "tek IP")
eq(run("b a b a c").strip(), "b,a,c", "ilk görülme sırası")
ok(not calls("set") and not calls("fromkeys"), "Bu görevde set/dict kullanmadan, liste ile çöz")
```

```solution
ipler = input().split()
benzersiz = []
for ip in ipler:
    if ip not in benzersiz:
        benzersiz.append(ip)
print(",".join(benzersiz))
```

```hint
Boş bir liste başlat; her IP için `if ip not in benzersiz: benzersiz.append(ip)`. Sonunda `",".join(...)`.
```
:::

::: gorev En büyük üç
Girdiden boşlukla ayrılmış tam sayılar oku ve **en büyük üçünü** büyükten küçüğe, boşlukla ayırarak yazdır. Üçten az sayı varsa hepsini yazdır.

```cikti
8080 3306 443
```

```starter
sayilar = input().split()

```

```stdin
22 8080 443 21 3306
```

```test
eq(run("22 8080 443 21 3306").split(), ["8080", "3306", "443"], "22 8080 443 21 3306 → 8080 3306 443")
eq(run("5 1").split(), ["5", "1"], "iki sayı → ikisi")
eq(run("100 9 10").split(), ["100", "10", "9"], "sayısal sıralama (metin değil!)")
```

```solution
sayilar = []
for x in input().split():
    sayilar.append(int(x))
enler = sorted(sayilar, reverse=True)[:3]
print(*enler)
```

```hint
Metinleri önce sayıya çevir: "9" > "10" metin olarak doğrudur ama sayı olarak yanlıştır!
```

```hint
`sorted(..., reverse=True)[:3]`. Yazdırırken `print(*liste)` elemanları boşlukla ayırır.
```
:::

::: gorev Listeyi döndür
İlk satırda boşlukla ayrılmış elemanlar, ikinci satırda bir k sayısı var. Listeyi **sola** k adım döndür: baştaki k eleman sona gider. k liste uzunluğundan büyük olabilir. Dilimlemeyle çöz.

```cikti
3 4 5 1 2
```

```starter
l = input().split()
k = int(input())

```

```stdin
1 2 3 4 5
2
```

```test
eq(run("1 2 3 4 5\n2").split(), ["3", "4", "5", "1", "2"], "k=2")
eq(run("1 2 3 4 5\n0").split(), ["1", "2", "3", "4", "5"], "k=0 → aynı")
eq(run("1 2 3 4 5\n7").split(), ["3", "4", "5", "1", "2"], "k=7 → k=2 ile aynı (% kullan)")
eq(run("a b c\n3").split(), ["a", "b", "c"], "k=uzunluk → aynı")
```

```solution
l = input().split()
k = int(input())
k = k % len(l)
print(*(l[k:] + l[:k]))
```

```hint
Döndürme = iki dilimi yer değiştirerek birleştirmek: `l[k:] + l[:k]`
```

```hint
k uzunluğu aşabilir: `k % len(l)` tam turları atar.
```
:::
