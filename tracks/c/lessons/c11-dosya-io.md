---
id: c11
title: Dosya Okuma ve Yazma
summary: FILE * akışları, fopen kipleri ve NULL denetimi, fread ile parça parça okuma döngüsü, fgets'in satır sonunu tutması ve tampon boyutu, fgetc ile EOF'un int olması, dönüş değerlerini denetlemek ve fclose.
---

::: anlat Akışlar
C'de dosyalar `FILE *` türünde bir **akış** üzerinden okunur ve yazılır:

```c
FILE *f = fopen("ayar.cfg", "rb");      // r: oku, w: yaz (siler!), a: sona ekle; b: ikili
if (f == NULL) {
    perror("ayar.cfg");                  // nedenini yazar: "No such file or directory"
    return 1;
}
/* ... */
fclose(f);
```

| İşlev | Ne yapar | Dönüşü |
|---|---|---|
| `fread(buf, 1, n, f)` | en fazla n bayt okur | okunan **eleman sayısı**; 0 ise dosya bitti ya da hata |
| `fwrite(buf, 1, n, f)` | n bayt yazar | yazılan eleman sayısı |
| `fgets(satir, boyut, f)` | bir satır okur | `satir` ya da bitti/hata ise `NULL` |
| `fgetc(f)` | bir bayt okur | bayt (0–255) ya da `EOF` (−1) |
| `fseek(f, ofset, SEEK_SET)` | konumu değiştirir | 0 başarı |
| `ftell(f)` | şimdiki konum | bayt cinsinden |

### Parça parça okuma
Büyük bir dosyanın tamamı belleğe alınmaz; sabit boyutlu bir tamponla **döngü içinde** okunur. Son parça genellikle daha kısadır:

```c
unsigned char buf[4096];
size_t n;
while ((n = fread(buf, 1, sizeof buf, f)) > 0) {
    isle(buf, n);              // yalnızca n baytı işle; tamponun geri kalanı eski veridir
}
```

> [!TUZAK]
> `fgetc`'nin dönüşü `int`'tir, `char` değil. `char c = fgetc(f)` yazan kod, 0xFF baytını `EOF` (−1) sanıp dosyanın ortasında durabilir ya da (işaretsiz `char`'lı sistemlerde) `EOF`'u hiç görmeyip sonsuz döngüye girebilir. Doğrusu `int c; while ((c = fgetc(f)) != EOF)`.
:::

::: anlat fgets ve satırlar
`fgets(satir, boyut, f)` en fazla **boyut − 1** karakter okur (son yer `'\0'` için), satır sonuna (`'\n'`) gelince durur ve **satır sonunu da tampona koyar**. Satır tampondan uzunsa, kalanı bir sonraki çağrıda gelir:

```c
// dosya içeriği: "web01\nweb02\n"
char satir[4];
while (fgets(satir, sizeof satir, f) != NULL) {
    /* 1. çağrı "web", 2. "01\n", 3. "web", 4. "02\n" */
}
```

Satır sonunu silmenin yaygın deyimi: `satir[strcspn(satir, "\n")] = '\0';`

### Satır saymak
```c
int c, satir = 0, son = '\n';
while ((c = fgetc(f)) != EOF) {
    if (c == '\n') satir++;
    son = c;
}
if (son != '\n') satir++;      // son satır '\n' ile bitmiyorsa onu da say
```

> [!GÜVENLİK]
> Dosyadan okunan her uzunluk ve ofset **güvenilmez** veridir (C08). Okuyan kod `fread`'in döndürdüğü sayıyı kullanmalı, istediği sayıyı değil: dosya beklenenden kısaysa tamponun sonu eski ya da tanımsız veriyle doludur.
:::

::: tahmin
Dosyanın içeriği `"web01\nweb02\n"`. Çıktı:

```c
FILE *f = fopen("liste.txt", "r");
char satir[4];
int n = 0;
while (fgets(satir, sizeof satir, f) != NULL) {
    n++;
    printf("%c %zu\n", satir[0], strlen(satir));
}
printf("%d\n", n);
fclose(f);
```

```gercek
w 3
0 3
w 3
0 3
4
```

???

`w 3`, `0 3`, `w 3`, `0 3`, sonra `4`. `fgets` her çağrıda en fazla 3 karakter okur. "web01\n" satırı iki parçada gelir: "web" ve "01\n" (satır sonu da tampondadır, uzunluğa dahildir). İkinci satır da aynı biçimde: "web" ve "02\n". Toplam 4 çağrı; her parçanın ilk karakteri ve uzunluğu yazılır.
:::

::: gorev fread döngüsü
`parcalar(veri, boyut)` fonksiyonunu yaz: yukarıdaki `fread` döngüsü `boyut` baytlık bir tamponla `veri`'yi (bir `bytes` nesnesi) okusaydı, her turda `n`'nin alacağı değerleri liste olarak döndürsün.

```starter
def parcalar(veri, boyut):
    return [boyut] * (len(veri) // boyut)
```

```test
need("parcalar")
eq(parcalar(bytes(10), 4), [4, 4, 2], "son parça kısa")
eq(parcalar(bytes(8), 4), [4, 4], "tam bölünüyor")
eq(parcalar(b"", 4096), [], "boş dosya: döngüye hiç girilmez")
eq(parcalar(bytes(3), 4096), [3], "dosya tampondan küçük")
```

```solution
def parcalar(veri, boyut):
    sonuc, konum = [], 0
    while konum < len(veri):
        n = min(boyut, len(veri) - konum)
        sonuc.append(n)
        konum += n
    return sonuc
```

```hint
Başlangıç kodu son, kısa parçayı unutuyor. Her turda okunan, `boyut` ile kalan bayt sayısının küçüğüdür.
```
:::

::: gorev fgets benzetimi
`fgets_benzet(metin, boyut)` fonksiyonunu yaz: `fgets(satir, boyut, f)` döngüsünün her çağrıda tampona koyacağı metinleri liste olarak döndürsün. `boyut` en az 2'dir.

```starter
def fgets_benzet(metin, boyut):
    return metin.splitlines()
```

```test
need("fgets_benzet")
eq(fgets_benzet("web01\nweb02\n", 4), ["web", "01\n", "web", "02\n"], "tahmindeki dosya")
eq(fgets_benzet("ab\ncd", 10), ["ab\n", "cd"], "son satırda satır sonu yok")
eq(fgets_benzet("abc", 2), ["a", "b", "c"], "boyut 2: her çağrıda bir karakter")
eq(fgets_benzet("", 8), [], "boş dosya")
eq(fgets_benzet("\n\n", 8), ["\n", "\n"], "boş satırlar")
```

```solution
def fgets_benzet(metin, boyut):
    sonuc, i = [], 0
    while i < len(metin):
        parca = ""
        while len(parca) < boyut - 1 and i < len(metin):
            parca += metin[i]
            i += 1
            if parca.endswith("\n"):
                break
        sonuc.append(parca)
    return sonuc
```

```hint
Her çağrı: en fazla `boyut - 1` karakter al; bir `"\n"` aldıysan orada dur (onu da parçaya kat).
```
:::

::: gorev Satır sayısı
Yukarıdaki `fgetc` ile satır sayan kodu `satir_say(metin)` olarak yaz.

```starter
def satir_say(metin):
    return metin.count("\n")
```

```test
need("satir_say")
eq(satir_say("a\nb\n"), 2, "satır sonuyla biten iki satır")
eq(satir_say("a\nb"), 2, "son satırda satır sonu yok")
eq(satir_say(""), 0, "boş dosya")
eq(satir_say("\n"), 1, "tek boş satır")
eq(satir_say("tek"), 1, "satır sonu hiç yok")
```

```solution
def satir_say(metin):
    satir, son = 0, "\n"
    for c in metin:
        if c == "\n":
            satir += 1
        son = c
    if son != "\n":
        satir += 1
    return satir
```

```hint
C kodu `son` değişkenine başta `'\n'` koyuyor: dosya boşsa son karakter "satır sonu" sayılır ve fazladan satır eklenmez.
```
:::
