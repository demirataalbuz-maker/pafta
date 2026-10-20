---
id: p69
title: Proje · Kendi Yorumlayıcın
summary: Jetonlayıcı, özyinelemeli iniş ayrıştırıcı, ağaç değerlendirici ve değişkenli bir hesap dili: Python'un yaptığını kendin yap.
---

::: anlat Son pafta: makineyi kendin kur
69 paftadır Python'un kodunu nasıl okuduğunu, ağaca çevirdiğini ve çalıştırdığını öğrendin (P62). Son projede bunu **kendin** yapacaksın: değişkenleri, dört işlemi, üs almayı ve parantezleri anlayan küçük bir dil.

```text
>>> x = 3 + 4 * 2
11
>>> y = (x - 1) ^ 2 / 4
25.0
>>> -y + x
-14.0
```

Her yorumlayıcının (CPython dahil) üç aşaması vardır:

| Aşama | Girdi → Çıktı | Örnek |
|---|---|---|
| **Jetonlama** (lexing) | metin → jeton listesi | `"3 + x"` → `[("SAYI", 3), ("OP", "+"), ("AD", "x")]` |
| **Ayrıştırma** (parsing) | jetonlar → sözdizimi ağacı | `("ikili", "+", ("sayi", 3), ("ad", "x"))` |
| **Değerlendirme** | ağaç + ortam → değer | `x = 4` iken `7` |

### Dilbilgisi
Öncelik ve birleşme yönünü dilbilgisi belirler. Her kural bir fonksiyon olur (**özyinelemeli iniş**, P67'deki ifade ayrıştırıcının büyük kardeşi):

```text
ifade  := terim (("+" | "-") terim)*          # en düşük öncelik, soldan birleşir
terim  := tekli (("*" | "/") tekli)*
tekli  := "-" tekli | us                      # -2^2 = -(2^2) = -4
us     := atom ("^" tekli)?                   # sağdan birleşir: 2^3^2 = 2^(3^2)
atom   := SAYI | AD | "(" ifade ")"
```

> [!DERİN]
> CPython 3.9'dan beri Python'un kendi ayrıştırıcısı bir **PEG** ayrıştırıcıdır ve dilbilgisi `Grammar/python.gram` dosyasında tam olarak buna benzer kurallarla yazılmıştır. `ast.parse` çağırdığında o kurallardan üretilmiş C kodu çalışır. Yani bu paftayı bitirdiğinde, P62'de baktığın makinenin minyatürünü kendi ellerinle kurmuş olacaksın.

> [!GÜVENLİK]
> "Kullanıcının yazdığı hesap ifadesini değerlendir" ihtiyacına en kolay cevap `eval()`'dir ve en tehlikelisidir (P06, P62, P67). Kendi küçük yorumlayıcın, dilin **sadece izin verdiğin** parçalarını tanır: dosya açamaz, modül yükleyemez, komut çalıştıramaz. Hesap makineleri, formül alanları ve kural dilleri böyle güvenli tutulur.

Ağaç düğümleri düz demetlerdir:

```python norun
("sayi", 3.5)                      # sayı
("ad", "x")                        # değişken
("tekli", "-", alt)                # eksi işareti
("ikili", "+", sol, sag)           # + - * / ^
("atama", "x", ifade)              # x = ifade (sadece en üst düzeyde)
```
:::

::: gorev 1 · Jetonlayıcı
`jetonla(metin)` fonksiyonu metni jeton listesine çevirsin:

- `("SAYI", değer)`: `42` → int `42`, `3.5` → float `3.5`
- `("AD", ad)`: harf ya da `_` ile başlayan, harf/rakam/`_` devam eden isimler
- `("OP", karakter)`: `+ - * / ^ ( ) =`
- Boşlukları atla; tanınmayan bir karakterde `SyntaxError` yükselt (mesajda konum olsun)

```starter
def jetonla(metin):
    pass
```

```test
need("jetonla")
eq(jetonla("x = 3 + 4.5*y"), [("AD", "x"), ("OP", "="), ("SAYI", 3), ("OP", "+"), ("SAYI", 4.5), ("OP", "*"), ("AD", "y")], "karışık ifade")
eq(jetonla("(a_1^2)"), [("OP", "("), ("AD", "a_1"), ("OP", "^"), ("SAYI", 2), ("OP", ")")], "parantez ve üs")
eq(jetonla("   "), [], "sadece boşluk → []")
ok(type(jetonla("7")[0][1]) is int and type(jetonla("7.0")[0][1]) is float, "int ve float ayrımı")
raises(SyntaxError, jetonla, "3 $ 4", msg="tanınmayan karakter → SyntaxError")
eq(jetonla("3."), [("SAYI", 3.0)], "sonda nokta: 3. → float 3.0")
raises(SyntaxError, jetonla, "3 + .", msg="sonda tek başına nokta → SyntaxError (IndexError değil)")
```

```solution
def jetonla(metin):
    jetonlar = []
    i = 0
    while i < len(metin):
        c = metin[i]
        if c.isspace():
            i += 1
        elif c.isdigit() or (c == "." and i + 1 < len(metin) and metin[i + 1].isdigit()):
            j = i
            while j < len(metin) and (metin[j].isdigit() or metin[j] == "."):
                j += 1
            parca = metin[i:j]
            jetonlar.append(("SAYI", float(parca) if "." in parca else int(parca)))
            i = j
        elif c.isalpha() or c == "_":
            j = i
            while j < len(metin) and (metin[j].isalnum() or metin[j] == "_"):
                j += 1
            jetonlar.append(("AD", metin[i:j]))
            i = j
        elif c in "+-*/^()=":
            jetonlar.append(("OP", c))
            i += 1
        else:
            raise SyntaxError(f"konum {i}: beklenmeyen karakter {c!r}")
    return jetonlar
```

```hint
Bir konum (`i`) tutup metni elle tara: rakam görünce rakamlar/nokta bitene kadar ilerle, harf görünce isim bitene kadar ilerle. Regex ile de yapabilirsin: `re.finditer(r"\s+|\d+\.\d+|\d+|[A-Za-z_]\w*|[-+*/^()=]|.", metin)`.
```
:::

::: gorev 2 · Ayrıştırıcı
`ayristir(jetonlar)` fonksiyonu jeton listesini (görev 1'in biçiminde) yukarıdaki **dilbilgisine** göre ağaca çevirsin. Satır `AD = ...` ile başlıyorsa `("atama", ad, ifade)` döndürsün. Hatalı sözdiziminde (`3 +`, `(1`, `2 3`, `=`) `SyntaxError` yükselt. Jetonlayıcı aşağıda hazır.

```starter
import re

def jetonla(metin):
    sonuc = []
    for m in re.finditer(r"\s+|\d+\.\d+|\d+|[A-Za-z_]\w*|[-+*/^()=]|.", metin):
        p = m.group()
        if p.isspace():
            continue
        if re.fullmatch(r"\d+\.\d+", p):
            sonuc.append(("SAYI", float(p)))
        elif p.isdigit():
            sonuc.append(("SAYI", int(p)))
        elif re.fullmatch(r"[A-Za-z_]\w*", p):
            sonuc.append(("AD", p))
        elif p in "+-*/^()=":
            sonuc.append(("OP", p))
        else:
            raise SyntaxError(p)
    return sonuc

def ayristir(jetonlar):
    pass
```

```test
need("ayristir")
A = lambda s: ayristir(jetonla(s))
eq(A("3"), ("sayi", 3), "sayı")
eq(A("1 + 2 * 3"), ("ikili", "+", ("sayi", 1), ("ikili", "*", ("sayi", 2), ("sayi", 3))), "* önce")
eq(A("8 - 3 - 2"), ("ikili", "-", ("ikili", "-", ("sayi", 8), ("sayi", 3)), ("sayi", 2)), "- soldan birleşir")
eq(A("2 ^ 3 ^ 2"), ("ikili", "^", ("sayi", 2), ("ikili", "^", ("sayi", 3), ("sayi", 2))), "^ sağdan birleşir")
eq(A("-2 ^ 2"), ("tekli", "-", ("ikili", "^", ("sayi", 2), ("sayi", 2))), "-2^2 = -(2^2)")
eq(A("(x + 1) * y"), ("ikili", "*", ("ikili", "+", ("ad", "x"), ("sayi", 1)), ("ad", "y")), "parantez")
eq(A("t = 2 * t"), ("atama", "t", ("ikili", "*", ("sayi", 2), ("ad", "t"))), "atama")
eq(A("2 ^ -1"), ("ikili", "^", ("sayi", 2), ("tekli", "-", ("sayi", 1))), "üste eksi")
for kotu in ["3 +", "(1", "2 3", "=", "x = = 1", "1 = x", ")"]:
    raises(SyntaxError, A, kotu, msg=f"sözdizimi hatası: {kotu!r}")
```

```solution
import re

def jetonla(metin):
    sonuc = []
    for m in re.finditer(r"\s+|\d+\.\d+|\d+|[A-Za-z_]\w*|[-+*/^()=]|.", metin):
        p = m.group()
        if p.isspace():
            continue
        if re.fullmatch(r"\d+\.\d+", p):
            sonuc.append(("SAYI", float(p)))
        elif p.isdigit():
            sonuc.append(("SAYI", int(p)))
        elif re.fullmatch(r"[A-Za-z_]\w*", p):
            sonuc.append(("AD", p))
        elif p in "+-*/^()=":
            sonuc.append(("OP", p))
        else:
            raise SyntaxError(p)
    return sonuc

def ayristir(jetonlar):
    konum = 0

    def bak(i=0):
        return jetonlar[konum + i] if konum + i < len(jetonlar) else (None, None)

    def op_mu(deger):
        return bak() == ("OP", deger)

    def al():
        nonlocal konum
        if konum >= len(jetonlar):
            raise SyntaxError("beklenmeyen satır sonu")
        konum += 1
        return jetonlar[konum - 1]

    def ifade():
        dugum = terim()
        while op_mu("+") or op_mu("-"):
            isaret = al()[1]
            dugum = ("ikili", isaret, dugum, terim())
        return dugum

    def terim():
        dugum = tekli()
        while op_mu("*") or op_mu("/"):
            isaret = al()[1]
            dugum = ("ikili", isaret, dugum, tekli())
        return dugum

    def tekli():
        if op_mu("-"):
            al()
            return ("tekli", "-", tekli())
        return us()

    def us():
        taban = atom()
        if op_mu("^"):
            al()
            return ("ikili", "^", taban, tekli())
        return taban

    def atom():
        tur, deger = al()
        if tur == "SAYI":
            return ("sayi", deger)
        if tur == "AD":
            return ("ad", deger)
        if (tur, deger) == ("OP", "("):
            dugum = ifade()
            if not op_mu(")"):
                raise SyntaxError("')' bekleniyordu")
            al()
            return dugum
        raise SyntaxError(f"beklenmeyen jeton: {deger!r}")

    if bak()[0] == "AD" and bak(1) == ("OP", "="):
        ad = al()[1]
        al()
        agac = ("atama", ad, ifade())
    else:
        agac = ifade()
    if konum != len(jetonlar):
        raise SyntaxError(f"fazla jeton: {bak()[1]!r}")
    return agac
```

```hint
Her dilbilgisi kuralı için bir iç fonksiyon (`ifade`, `terim`, `tekli`, `us`, `atom`) ve ortak bir `konum`. Soldan birleşen işleçler için `while` döngüsü, sağdan birleşen `^` için özyineleme (`us` içinde sağ tarafı `tekli()` ile ayrıştır).
```

```hint
Atamayı en başta yakala: ilk jeton AD ve ikincisi `=` ise. Sonunda bütün jetonların tüketildiğini kontrol et; yoksa `2 3` gibi girdiler sessizce geçer.
```
:::

::: gorev 3 · Değerlendirici
`degerlendir(agac, ortam)` fonksiyonu görev 2'nin ürettiği ağacı **özyinelemeyle** değerlendirsin. `ortam` değişken adı → değer sözlüğüdür:

- `("ad", x)`: ortamda yoksa `NameError`
- `/` her zaman float döndürür (Python'daki gibi); sıfıra bölmede `ZeroDivisionError`
- `^` üs alma (`**`)
- `("atama", ad, ifade)`: değeri hesapla, **ortama yaz** ve değeri döndür

```starter
def degerlendir(agac, ortam):
    pass
```

```test
need("degerlendir")
ortam = {"x": 4}
eq(degerlendir(("sayi", 3), ortam), 3, "sayı")
eq(degerlendir(("ikili", "+", ("sayi", 1), ("ikili", "*", ("sayi", 2), ("ad", "x"))), ortam), 9, "1 + 2*x")
eq(degerlendir(("ikili", "/", ("sayi", 7), ("sayi", 2)), ortam), 3.5, "bölme float")
eq(degerlendir(("ikili", "^", ("sayi", 2), ("ikili", "^", ("sayi", 3), ("sayi", 2))), ortam), 512, "2^(3^2)")
eq(degerlendir(("tekli", "-", ("ikili", "^", ("sayi", 2), ("sayi", 2))), ortam), -4, "-(2^2)")
eq(degerlendir(("atama", "y", ("ikili", "-", ("ad", "x"), ("sayi", 1))), ortam), 3, "atama değeri döndürür")
eq(ortam.get("y"), 3, "atama ortama yazar")
raises(NameError, degerlendir, ("ad", "bilinmeyen"), ortam, msg="tanımsız değişken → NameError")
raises(ZeroDivisionError, degerlendir, ("ikili", "/", ("sayi", 1), ("sayi", 0)), ortam, msg="sıfıra bölme")
ok(not calls("eval") and not calls("exec"), "eval/exec kullanmadan")
```

```solution
import operator

ISLEMLER = {"+": operator.add, "-": operator.sub, "*": operator.mul,
            "/": operator.truediv, "^": operator.pow}

def degerlendir(agac, ortam):
    tur = agac[0]
    if tur == "sayi":
        return agac[1]
    if tur == "ad":
        if agac[1] not in ortam:
            raise NameError(f"tanımsız değişken: {agac[1]}")
        return ortam[agac[1]]
    if tur == "tekli":
        return -degerlendir(agac[2], ortam)
    if tur == "ikili":
        _, isaret, sol, sag = agac
        return ISLEMLER[isaret](degerlendir(sol, ortam), degerlendir(sag, ortam))
    if tur == "atama":
        _, ad, ifade = agac
        deger = degerlendir(ifade, ortam)
        ortam[ad] = deger
        return deger
    raise ValueError(f"bilinmeyen düğüm: {tur}")
```

```hint
Düğüm türüne göre dallan (if zinciri ya da `match`, P12). İkili işlemler için `operator` modülü ile bir dağıtım sözlüğü kur: `{"+": operator.add, ...}`.
```

```hint
P12'deki yapısal eşleme burada çok şık durur: `case ("ikili", isaret, sol, sag):`.
```
:::

::: gorev 4 · Etkileşimli yorumlayıcı
Parçaları birleştir: `Yorumlayici` sınıfı kendi ortamını tutsun ve `calistir(satir)` metodu satırı jetonlayıp ayrıştırıp değerlendirerek sonucu döndürsün. Boş satırda `None` döndürsün.

Sonra girdiden satır satır oku (girdi bitene kadar) ve her satırın sonucunu yazdır; hata olursa programı durdurma, `hata: <TürAdı>: <mesaj>` yazdırıp devam et. Önceki üç görevin çözümleri aşağıda hazır.

```starter
import re, operator

def jetonla(metin):
    sonuc = []
    for m in re.finditer(r"\s+|\d+\.\d+|\d+|[A-Za-z_]\w*|[-+*/^()=]|.", metin):
        p = m.group()
        if p.isspace():
            continue
        if re.fullmatch(r"\d+\.\d+", p):
            sonuc.append(("SAYI", float(p)))
        elif p.isdigit():
            sonuc.append(("SAYI", int(p)))
        elif re.fullmatch(r"[A-Za-z_]\w*", p):
            sonuc.append(("AD", p))
        elif p in "+-*/^()=":
            sonuc.append(("OP", p))
        else:
            raise SyntaxError(f"beklenmeyen karakter {p!r}")
    return sonuc

def ayristir(j):
    i = 0
    def bak(k=0):
        return j[i + k] if i + k < len(j) else (None, None)
    def al():
        nonlocal i
        if i >= len(j):
            raise SyntaxError("beklenmeyen satır sonu")
        i += 1
        return j[i - 1]
    def ifade():
        d = terim()
        while bak() in (("OP", "+"), ("OP", "-")):
            d = ("ikili", al()[1], d, terim())
        return d
    def terim():
        d = tekli()
        while bak() in (("OP", "*"), ("OP", "/")):
            d = ("ikili", al()[1], d, tekli())
        return d
    def tekli():
        if bak() == ("OP", "-"):
            al()
            return ("tekli", "-", tekli())
        return us()
    def us():
        t = atom()
        if bak() == ("OP", "^"):
            al()
            return ("ikili", "^", t, tekli())
        return t
    def atom():
        tur, deger = al()
        if tur == "SAYI":
            return ("sayi", deger)
        if tur == "AD":
            return ("ad", deger)
        if (tur, deger) == ("OP", "("):
            d = ifade()
            if bak() != ("OP", ")"):
                raise SyntaxError("')' bekleniyordu")
            al()
            return d
        raise SyntaxError(f"beklenmeyen jeton {deger!r}")
    if bak()[0] == "AD" and bak(1) == ("OP", "="):
        ad = al()[1]; al()
        a = ("atama", ad, ifade())
    else:
        a = ifade()
    if i != len(j):
        raise SyntaxError(f"fazla jeton {bak()[1]!r}")
    return a

ISLEM = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv, "^": operator.pow}

def degerlendir(a, ortam):
    match a:
        case ("sayi", v):
            return v
        case ("ad", ad):
            if ad not in ortam:
                raise NameError(f"tanımsız değişken: {ad}")
            return ortam[ad]
        case ("tekli", "-", alt):
            return -degerlendir(alt, ortam)
        case ("ikili", op, sol, sag):
            return ISLEM[op](degerlendir(sol, ortam), degerlendir(sag, ortam))
        case ("atama", ad, ifade):
            ortam[ad] = degerlendir(ifade, ortam)
            return ortam[ad]

class Yorumlayici:
    pass

# girdiyi satır satır işle

```

```stdin
x = 3 + 4 * 2
y = (x - 1) ^ 2 / 4
-y + x
z * 2
1 / 0
```

```test
Y = need("Yorumlayici", "sınıf")
y = Y()
eq(y.calistir("a = 10"), 10, "atama")
eq(y.calistir("a * 2 + 1"), 21, "değişken kullanımı")
eq(y.calistir("   "), None, "boş satır → None")
eq(Y().calistir("2 ^ 10"), 1024, "her yorumlayıcının ayrı ortamı")
raises(NameError, Y().calistir, "a", msg="yeni yorumlayıcıda a tanımsız")
eq(lines, ["11", "25.0", "-14.0", "hata: NameError: tanımsız değişken: z", "hata: ZeroDivisionError: division by zero"], "oturum çıktısı")
```

```solution
import re, operator

def jetonla(metin):
    sonuc = []
    for m in re.finditer(r"\s+|\d+\.\d+|\d+|[A-Za-z_]\w*|[-+*/^()=]|.", metin):
        p = m.group()
        if p.isspace():
            continue
        if re.fullmatch(r"\d+\.\d+", p):
            sonuc.append(("SAYI", float(p)))
        elif p.isdigit():
            sonuc.append(("SAYI", int(p)))
        elif re.fullmatch(r"[A-Za-z_]\w*", p):
            sonuc.append(("AD", p))
        elif p in "+-*/^()=":
            sonuc.append(("OP", p))
        else:
            raise SyntaxError(f"beklenmeyen karakter {p!r}")
    return sonuc

def ayristir(j):
    i = 0
    def bak(k=0):
        return j[i + k] if i + k < len(j) else (None, None)
    def al():
        nonlocal i
        if i >= len(j):
            raise SyntaxError("beklenmeyen satır sonu")
        i += 1
        return j[i - 1]
    def ifade():
        d = terim()
        while bak() in (("OP", "+"), ("OP", "-")):
            d = ("ikili", al()[1], d, terim())
        return d
    def terim():
        d = tekli()
        while bak() in (("OP", "*"), ("OP", "/")):
            d = ("ikili", al()[1], d, tekli())
        return d
    def tekli():
        if bak() == ("OP", "-"):
            al()
            return ("tekli", "-", tekli())
        return us()
    def us():
        t = atom()
        if bak() == ("OP", "^"):
            al()
            return ("ikili", "^", t, tekli())
        return t
    def atom():
        tur, deger = al()
        if tur == "SAYI":
            return ("sayi", deger)
        if tur == "AD":
            return ("ad", deger)
        if (tur, deger) == ("OP", "("):
            d = ifade()
            if bak() != ("OP", ")"):
                raise SyntaxError("')' bekleniyordu")
            al()
            return d
        raise SyntaxError(f"beklenmeyen jeton {deger!r}")
    if bak()[0] == "AD" and bak(1) == ("OP", "="):
        ad = al()[1]; al()
        a = ("atama", ad, ifade())
    else:
        a = ifade()
    if i != len(j):
        raise SyntaxError(f"fazla jeton {bak()[1]!r}")
    return a

ISLEM = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv, "^": operator.pow}

def degerlendir(a, ortam):
    match a:
        case ("sayi", v):
            return v
        case ("ad", ad):
            if ad not in ortam:
                raise NameError(f"tanımsız değişken: {ad}")
            return ortam[ad]
        case ("tekli", "-", alt):
            return -degerlendir(alt, ortam)
        case ("ikili", op, sol, sag):
            return ISLEM[op](degerlendir(sol, ortam), degerlendir(sag, ortam))
        case ("atama", ad, ifade):
            ortam[ad] = degerlendir(ifade, ortam)
            return ortam[ad]

class Yorumlayici:
    def __init__(self):
        self.ortam = {}

    def calistir(self, satir):
        jetonlar = jetonla(satir)
        if not jetonlar:
            return None
        return degerlendir(ayristir(jetonlar), self.ortam)

if __name__ == "__main__":
    yorumlayici = Yorumlayici()
    while True:
        try:
            satir = input()
        except EOFError:
            break
        try:
            sonuc = yorumlayici.calistir(satir)
        except Exception as e:
            print(f"hata: {type(e).__name__}: {e}")
        else:
            if sonuc is not None:
                print(sonuc)
```

```hint
`Yorumlayici.__init__` boş bir ortam sözlüğü açar; `calistir` üç aşamayı zincirler: `degerlendir(ayristir(jetonla(satir)), self.ortam)`.
```

```hint
Döngü: `input()`'u `EOFError` gelene kadar oku. Her satırı ayrı bir `try` ile çalıştır ki bir hata oturumu bitirmesin. Tebrikler: P01'de `print` yazan sen, şimdi kendi dilinin yorumlayıcısını yazdın. **Başpehlivan.**
```
:::
