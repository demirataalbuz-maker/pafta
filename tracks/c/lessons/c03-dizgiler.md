---
id: c03
title: Diziler ve Dizgiler
summary: Sabit boyutlu diziler, sizeof, '\0' ile biten karakter dizileri, strlen ile sizeof farkı, karakterler üzerinde döngü ve sınır hataları.
kazanim: CLA 1.2
---

::: anlat Diziler
C dizisi, aynı türden elemanların bellekte **yan yana** durduğu sabit boyutlu bir bloktur. İndeks 0'dan başlar ve C sınırı **denetlemez**:

```c
int olcum[5] = {62, 75, 91, 88, 70};
int toplam = 0;
for (int i = 0; i < 5; i++) {      // 0..4; i <= 5 yazmak dizinin dışına taşar
    toplam += olcum[i];
}
printf("%d\n", toplam);                         // 386
printf("%zu\n", sizeof(olcum) / sizeof(olcum[0]));   // eleman sayısı: 5
```

`sizeof` bir şeyin bellekte kaç **bayt** tuttuğunu verir; `int` genellikle 4 bayttır, dizinin toplam boyutunu eleman boyutuna bölmek eleman sayısını verir.

### Dizgiler: '\0' ile biten karakter dizileri
C'de ayrı bir metin türü yoktur. Metin, sonunda **sıfır baytı** (`'\0'`) olan bir `char` dizisidir:

```c
char ad[] = "web01";      // bellekte: w e b 0 1 \0  → 6 bayt
```

| | Ne sayar | `"web01"` için |
|---|---|---|
| `sizeof(ad)` | dizinin bayt boyutu, `'\0'` dahil | 6 |
| `strlen(ad)` | `'\0'`'a kadar olan karakterler | 5 |

`strlen`, `printf("%s")` ve benzerleri metnin nerede bittiğini **yalnızca** `'\0'`'ı bularak anlar. Ortadaki bir karakteri `'\0'` yapmak metni oradan keser.

```c
const char *s = "Disk doluluğu";
int buyuk = 0;
for (int i = 0; s[i] != '\0'; i++) {     // '\0' görene kadar yürü
    if (s[i] >= 'A' && s[i] <= 'Z') buyuk++;
}
```

> [!TUZAK]
> Türkçe karakterler UTF-8'de **birden çok bayttır**: "ğ" iki bayt tutar. `strlen("doluluğu")` 8 değil 9 döner. C kodu baytlarla çalışır, harflerle değil.

> [!GÜVENLİK]
> C dizinin sınırını denetlemediği için, bir diziye boyutundan uzun veri yazmak **komşu belleğin üzerine yazar**. Bellek hatalarının büyük kısmı bu kalıptan çıkar: döngüde `<=`, `'\0'` için yer ayırmayı unutmak ya da sınır denetimsiz kopyalamak. Kod okurken her dizi yazımında "boyut nerede denetleniyor?" diye sor.
:::

::: tahmin
Çıktı:

```c
char s[] = "pafta";
printf("%zu %zu\n", sizeof(s), strlen(s));
s[2] = '\0';
printf("%s\n", s);
```

```gercek
6 5
pa
```

???

`6 5`, sonra `pa`. Dizi beş harf ve sondaki `'\0'` için 6 bayttır; `strlen` sıfır baytını saymaz. Üçüncü karakter (indeks 2) `'\0'` yapılınca `printf` metni orada bitmiş sayar.
:::

::: gorev Karakter sayımı
Aşağıdaki C fonksiyonunu Python'a `say(s, c)` olarak çevir (Python'un hazır `count` metodunu kullanmadan, aynı döngüyle).

```c
int say(const char *s, char c) {
    int n = 0;
    for (int i = 0; s[i] != '\0'; i++) {
        if (s[i] == c) n++;
    }
    return n;
}
```

```starter
def say(s, c):
    return 0
```

```test
need("say")
eq(say("web01-web02", "w"), 2, "w iki kez")
eq(say("", "a"), 0, "boş metin")
eq(say("aaa", "a"), 3, "aaa")
ok(not calls("count"), "hazır count metodunu kullanma; döngüyle say")
```

```solution
def say(s, c):
    n = 0
    for ch in s:
        if ch == c:
            n += 1
    return n
```

```hint
Python'da metin sonu için `'\0'` yok; `for ch in s` bütün karakterleri dolaşır.
```
:::

::: gorev Kaydırma şifresi
Aşağıdaki C fonksiyonu küçük harfleri alfabede `k` adım kaydırıyor; diğer karakterlere dokunmuyor. Python'da `kaydir(s, k)` olarak yaz (`k` 0 ile 25 arası).

```c
void kaydir(char *s, int k) {
    for (int i = 0; s[i] != '\0'; i++) {
        if (s[i] >= 'a' && s[i] <= 'z') {
            s[i] = 'a' + (s[i] - 'a' + k) % 26;
        }
    }
}
```

```starter
def kaydir(s, k):
    return s
```

```test
need("kaydir")
eq(kaydir("abc", 1), "bcd", "abc +1")
eq(kaydir("xyz", 3), "abc", "sondan başa dolanır")
eq(kaydir("Web-01 sunucu", 2), "Wgd-01 uwpwew", "büyük harf, rakam ve işaretler değişmez")
eq(kaydir("pafta", 0), "pafta", "k = 0")
```

```solution
def kaydir(s, k):
    sonuc = []
    for ch in s:
        if "a" <= ch <= "z":
            ch = chr(ord("a") + (ord(ch) - ord("a") + k) % 26)
        sonuc.append(ch)
    return "".join(sonuc)
```

```hint
C'deki `s[i] - 'a'` Python'da `ord(ch) - ord("a")`; sonucu karaktere çevirmek için `chr(...)`.
```
:::
