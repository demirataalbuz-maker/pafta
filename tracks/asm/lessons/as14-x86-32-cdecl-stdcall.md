---
id: as14
title: x86-32 Çağrı Kuralları · cdecl ve stdcall
summary: 32-bit kodda argümanlar yazmaçlarda değil yığında taşınır ve sağdan sola itilir; dönüş eax'tedir. cdecl'de yığını çağıran temizler (çağrının ardından add esp, N) ve callee düz ret ile döner; stdcall'da callee kendisi temizler (ret N) ve çağıranda temizlik satırı bulunmaz. Disassembly'de kuralı bu iki işaretten okursun; iki taraf aynı kuralda anlaşmazsa yığın dengesi bozulur.
---

::: anlat 32 bit: argümanlar yığında
`AS07`'de x86-64'ün iki ABI'sini okudun; ikisinde de ilk birkaç argüman **yazmaçlarda** gider. 32-bit kodda durum farklıdır: klasik kurallarda argümanlar **yığına itilir**.

Ölçülen çağıran taraf (Kali, gcc 16.2.0, `-m32 -O0`):

```asm
  42:	6a 03                	push   0x3
  44:	6a 02                	push   0x2
  46:	6a 01                	push   0x1
  48:	e8 fc ff ff ff       	call   topla
  4d:	83 c4 0c             	add    esp,0xc
```

Üç şeyi aynı anda söyler:

- Argümanlar **sağdan sola** itilir: `3`, `2`, `1` sırasıyla. Böylece `call` anında yığının en üstünde **birinci** argüman durur.
- Her argüman 4 bayt yer kaplar; üç argüman 12 bayt (`0xc`).
- Dönüş değeri `eax`'tedir (burada sonraki satırlar onu kullanır).

`call  topla` satırındaki `e8 fc ff ff ff` kodlamasına takılma: bu bir nesne dosyası ve hedef henüz yazılmamış — `AS13`'teki yer değiştirme kaydı bağlama sırasında burayı dolduracak.
:::

::: anlat Yığını kim temizler?
İtilen 12 baytın çağrıdan sonra geri alınması gerekir. **Bunu kimin yapacağı çağrı kuralının tanımıdır** ve iki klasik seçenek vardır:

| Kural | Temizleyen | Çağıranda görülen | Callee'de görülen |
|---|---|---|---|
| **cdecl** | çağıran | `add esp, N` | düz `ret` |
| **stdcall** | callee | *(hiçbir şey)* | `ret N` |

Aynı kaynak dosyadan ölçülen iki fonksiyonun son satırları:

```asm
; topla  (cdecl)            ; carp  (stdcall)
  1a:	5d       pop  ebp       30:	5d          pop  ebp
  1b:	c3       ret            31:	c2 08 00    ret  0x8
```

`c3` düz dönüştür; `c2 08 00` ise "dön ve yığından 8 bayt daha at" demektir — `carp`'ın iki argümanı. Çağıran tarafta da fark görünür: `topla` çağrısının ardından `add esp,0xc` vardır, `carp` çağrısının ardından **temizlik satırı yoktur**, çünkü işi callee bitirmiştir.

İki işaretten biri bile kuralı söyler. Kaynak kodu olmayan bir ikilide bir fonksiyonun `ret N` ile bitmesi, onun stdcall olduğunu ve N/4 kadar argüman aldığını anlatır.

> [!TUZAK] İki taraf anlaşamazsa yığın kayar
> Kural bir **anlaşmadır** ve derleyici iki tarafı ayrı ayrı derler. Bir başlık dosyasında `__stdcall` yazan bir fonksiyonu `cdecl` sanan bir çağıran, callee zaten temizledikten sonra bir de kendisi `add esp, N` yapar: yığın göstergesi fazladan ilerler. Tersi durumda hiç kimse temizlemez ve her çağrıda biraz yığın sızar. İkisi de hemen çökmeyebilir; hata, çok sonra ilgisiz bir yerde ortaya çıkar. Windows API'lerinin `__stdcall` olması, elle yazılan imzalarda bu uyuşmazlığın klasik kaynağıdır.

Not: bunlar 32-bit kuralıdır. x86-64'te tek bir çağrı kuralı vardır ve `__cdecl`/`__stdcall` anahtar sözcükleri yok sayılır; `AS07`'deki kayıt tabanlı düzen geçerlidir.
:::

::: tahmin Hangi çağrı hangi kural?
`cagir` fonksiyonu iki fonksiyonu çağırıyor. Disassembly'ye bakarak hangisinin cdecl, hangisinin stdcall olduğunu söyle.

```asm
  42:	6a 03                	push   0x3
  44:	6a 02                	push   0x2
  46:	6a 01                	push   0x1
  48:	e8 fc ff ff ff       	call   topla
  4d:	83 c4 0c             	add    esp,0xc
  50:	89 c3                	mov    ebx,eax
  52:	6a 05                	push   0x5
  54:	6a 04                	push   0x4
  56:	e8 fc ff ff ff       	call   carp
  5b:	01 d8                	add    eax,ebx
```

```gercek
topla : 3 arguman itildi, cagiran "add esp,0xc" ile temizledi  -> cdecl
        (topla'nin sonu: c3            = ret)
carp  : 2 arguman itildi, cagirida temizlik YOK                -> stdcall
        (carp'in sonu:   c2 08 00      = ret 0x8)
```

???

`topla` **cdecl**, `carp` **stdcall**.

`topla` çağrısının hemen ardından `add esp,0xc` var: çağıran, ittiği 12 baytı kendisi geri alıyor. Bu cdecl'in imzasıdır ve fonksiyonun kendisi düz `c3` ile döner.

`carp` çağrısından sonra ise doğrudan `add eax,ebx` geliyor — arada **hiçbir temizlik yok**. İtilen 8 bayt kayboldu mu? Hayır: `carp` `c2 08 00`, yani `ret 0x8` ile dönerek onları kendisi attı. Çağıranda temizlik satırının **olmaması** burada bir eksiklik değil, bilgidir.

Aradaki `mov ebx,eax` de okunur: `topla`'nın `eax`'teki sonucu, ikinci çağrı `eax`'i ezmeden önce `ebx`'e saklanıyor; sonunda `add eax,ebx` ikisini topluyor.
:::

::: gorev Çağrı şemasını çıkar
`cagriSemasi(kural, argSayisi)` yaz: bir çağrının disassembly'de nasıl görüneceğini betimle.

Dönüş `(itilenBayt, calleeRet, cagiranTemizlik)`:

- `itilenBayt`: argümanların kapladığı toplam bayt (her argüman 4 bayt).
- `calleeRet`: callee'nin dönüş satırı — cdecl'de `"ret"`, stdcall'da `"ret N"` (N itilen bayt; argüman yoksa yine `"ret"`).
- `cagiranTemizlik`: çağıranın `add esp, N` ile geri aldığı bayt; stdcall'da `0`.

```starter
def cagriSemasi(kural, argSayisi):
    bayt = argSayisi * 4
    return (bayt, "ret", bayt)
```

```test
need("cagriSemasi")
eq(cagriSemasi("cdecl", 3), (12, "ret", 12), "ölçülen topla: 3 argüman, çağıran add esp,0xc")
eq(cagriSemasi("stdcall", 2), (8, "ret 8", 0), "ölçülen carp: ret 0x8, çağıranda temizlik yok")
eq(cagriSemasi("cdecl", 0), (0, "ret", 0), "argümansız cdecl")
eq(cagriSemasi("stdcall", 0), (0, "ret", 0), "argümansız stdcall: atılacak bayt yok, düz ret")
eq(cagriSemasi("cdecl", 1), (4, "ret", 4), "tek argüman")
eq(cagriSemasi("stdcall", 1), (4, "ret 4", 0), "tek argümanlı stdcall")
eq(cagriSemasi("stdcall", 5), (20, "ret 20", 0), "beş argüman")
```

```solution
def cagriSemasi(kural, argSayisi):
    bayt = argSayisi * 4
    if kural == "stdcall":
        return (bayt, f"ret {bayt}" if bayt else "ret", 0)
    return (bayt, "ret", bayt)
```

```hint
İki yerde ayrılıyorlar: callee'nin dönüş satırı ve çağıranın temizliği. Argüman sayısı sıfırken stdcall da düz `ret` yazar — atılacak bayt olmadığı için `ret 0` üretilmez.
```
:::

::: gorev Yığın dengesini izle
`espDengesi(olaylar)` yaz: bir çağrı dizisinde `esp`'nin net değişimini hesapla ve uyuşmazlığı yakala.

Olaylar sırayla uygulanır:

- `("it", n)`: `n` adet dword itilir — `esp` `4*n` **azalır**.
- `("cagri", kural, argSayisi)`: çağrı yapılır. `kural` `"stdcall"` ise callee `4*argSayisi` bayt atar, yani `esp` o kadar **artar**; `"cdecl"` ise çağrı `esp`'yi değiştirmez.
- `("temizle", n)`: çağıran `add esp, n` yapar — `esp` `n` **artar**.

Dönüş: net değişim (bayt). `0` dengeli demektir; negatif değer yığının sızdığını, pozitif değer fazla atıldığını gösterir.

```starter
def espDengesi(olaylar):
    net = 0
    for olay in olaylar:
        if olay[0] == "it":
            net -= olay[1] * 4
        elif olay[0] == "temizle":
            net += olay[1]
    return net
```

```test
need("espDengesi")
eq(espDengesi([("it", 3), ("cagri", "cdecl", 3), ("temizle", 12)]), 0,
   "doğru cdecl: çağıran ittiğini geri alır")
eq(espDengesi([("it", 2), ("cagri", "stdcall", 2)]), 0,
   "doğru stdcall: callee temizler, çağıran karışmaz")
eq(espDengesi([("it", 2), ("cagri", "stdcall", 2), ("temizle", 8)]), 8,
   "uyuşmazlık: stdcall callee'yi cdecl sanmak, iki kez temizlenir")
eq(espDengesi([("it", 3), ("cagri", "cdecl", 3)]), -12,
   "uyuşmazlık: cdecl'de çağıran temizlemeyi unutursa yığın sızar")
eq(espDengesi([("it", 3), ("cagri", "cdecl", 3), ("temizle", 12),
                ("it", 2), ("cagri", "stdcall", 2)]), 0, "ölçülen cagir: iki çağrı da dengeli")
eq(espDengesi([("it", 1), ("cagri", "cdecl", 1), ("temizle", 4)] * 3), 0, "döngüde üç kez, hep dengeli")
eq(espDengesi([("it", 1), ("cagri", "cdecl", 1)] * 3), -12, "her turda 4 bayt sızar")
eq(espDengesi([]), 0, "hiç çağrı yok")
```

```solution
def espDengesi(olaylar):
    net = 0
    for olay in olaylar:
        if olay[0] == "it":
            net -= olay[1] * 4
        elif olay[0] == "cagri":
            if olay[1] == "stdcall":
                net += olay[2] * 4
        elif olay[0] == "temizle":
            net += olay[1]
    return net
```

```hint
Başlangıç kodu `("cagri", ...)` olayını hiç işlemiyor; oysa stdcall çağrısının kendisi `esp`'yi değiştirir. Üç olay türünün üçünü de ele al: itme azaltır, stdcall çağrısı ve temizleme artırır.
```

```hint
Sızıntıyı görmek için net değerin işaretine bak: negatif, itilenin geri alınmadığı (her turda biraz daha kayan bir yığın); pozitif, aynı baytların iki kez atıldığı anlamına gelir. İkisi de hemen çökmez, bu yüzden tehlikelidir.
```
:::
