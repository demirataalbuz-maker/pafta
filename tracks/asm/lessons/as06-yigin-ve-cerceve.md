---
id: as06
title: Yığın (Stack), push/pop ve Fonksiyon Çerçevesi
rank: kucuk-orta
order: 6
summary: Yığının yüksek adresten düşük adrese büyümesini, rsp/rbp yazmaçlarını, LIFO sırasıyla push/pop komutlarını ve fonksiyon prolog/epilog yapısını okumak.
---

::: anlat
x86-64 mimarisinde **yığın (stack)**, geçici değerlerin, yerel değişkenlerin ve fonksiyon dönüş adreslerinin tutulduğu bellek bölgesidir. Yığınla ilgili en temel kural şudur:

- **Yığın aşağı doğru (yüksek adresten düşük adrese) büyür.**
- Yığının en tepesini her zaman **`rsp` (Stack Pointer)** gösterir.
- Yığına yeni bir 64-bit değer eklendiğinde (`push`), `rsp` **8 azalır**; yığından değer çekildiğinde (`pop`), `rsp` **8 artar**.

| İşlem | Assembly Komutu | İşlemcinin Yaptığı Eşdeğer Adımlar | `rsp` Değişimi |
|---|---|---|---|
| Yığına itme | `push rax` | `sub rsp, 8` → `mov QWORD PTR [rsp], rax` | `rsp - 8` |
| Yığından çekme | `pop rbx` | `mov rbx, QWORD PTR [rsp]` → `add rsp, 8` | `rsp + 8` |
| Yerel alan açma | `sub rsp, 32` | Yığında 32 baytlık yerel değişken alanı ayırır | `rsp - 32` |
| Yerel alanı kapama | `add rsp, 32` | Ayrılan 32 baytlık alanı geri bırakır | `rsp + 32` |

> [!TUZAK]
> Yığın **LIFO (Last-In, First-Out / Son Giren İlk Çıkar)** sırasıyla çalışır. Ardışık `push rcx` ve `push rdx` komutlarından sonra `pop rax` çalıştırıldığında `rax` yazmacına ilk itilen `rcx` değil, **en son itilen `rdx`** gelir! İki yazmacı yığın üzerinden birbirine karıştırmadan geri yüklemek için `pop` sırası `push` sırasının **tam tersi** olmalıdır.

### Fonksiyon Çerçevesi (Stack Frame): Prolog ve Epilog

Bir fonksiyon çalışmaya başladığında yerel değişkenlerine sabit ofsetlerle erişebilmek için kendi çerçevesini kurar (**prolog**) ve çıkarken eski haline döndürür (**epilog**):

```asm
as06_ornek:
    ; --- PROLOG (Giriş) ---
    push rbp                        #! 1) Çağıranın taban işaretçisini yığına kaydet (rsp -= 8)
    mov rbp, rsp                    #! 2) Kendi çerçeve tabanımızı sabitle (rbp = rsp)
    sub rsp, 16                     #! 3) Yerel değişkenler için 16 bayt yer aç (rsp -= 16)

    ; --- GÖVDE (Yerel Değişkenler: [rbp - ofset]) ---
    mov DWORD PTR [rbp - 4], ecx    #! 1. yerel değişken (int a) = ecx
    mov DWORD PTR [rbp - 8], edx    #! 2. yerel değişken (int b) = edx
    mov eax, DWORD PTR [rbp - 4]    #! eax = a
    add eax, DWORD PTR [rbp - 8]    #! eax = a + b

    ; --- EPILOG (Çıkış) ---
    mov rsp, rbp                    #! 1) Yerel alanı tek hamlede temizle (veya 'leave' komutu)
    pop rbp                         #! 2) Çağıranın rbp değerini geri yükle (rsp += 8)
    ret                             #! 3) [rsp]'deki dönüş adresini rip'e çek ve dön (rsp += 8)
```

### Çerçeve Belleğinin Haritası

`push rbp` ve `mov rbp, rsp` yapıldıktan sonra `rbp` sabit bir referans noktası olur:

| Bellek Adresi | İçerik | Açıklama |
|---|---|---|
| `[rbp + 8]` | Dönüş adresi (`saved rip`) | `call` komutunun yığına ittiği adres |
| `[rbp]` | Kaydedilmiş `rbp` (`saved rbp`) | `push rbp` ile kaydedilen eski çerçeve tabanı |
| `[rbp - 4]` | 1. yerel `int32` değişken | Fonksiyonun kendi yerel alanı |
| `[rbp - 8]` | 2. yerel `int32` değişken | Fonksiyonun kendi yerel alanı |
| `[rbp - 16]` (`[rsp]`) | Yığının güncel tepesi | `sub rsp, 16` sonrası `rsp` noktası |

> [!DERİN]
> Derleyiciler `-O1` / `-O2` optimizasyonunda veya `-fomit-frame-pointer` bayrağı açıkken `rbp` yazmacını çerçeve tabanı olarak harcamak yerine genel amaçlı yazmaç gibi kullanır ve tüm yerel değişkenlere doğrudan `[rsp + ofset]` üzerinden erişir.
:::

::: tahmin
```asm
; Windows x64: ecx = 1. argüman, edx = 2. argüman
as06_cerceve:
    push rbp
    mov rbp, rsp
    sub rsp, 16
    mov DWORD PTR [rbp - 4], ecx
    mov DWORD PTR [rbp - 8], edx
    push rcx
    push rdx
    pop rax
    pop r8
    sub eax, r8d
    add eax, DWORD PTR [rbp - 4]
    mov rsp, rbp
    pop rbp
    ret

; Çağrılar:
; 1) as06_cerceve(12, 30)
; 2) as06_cerceve(20, 5)
```

Yukarıdaki `as06_cerceve` fonksiyonu sırasıyla `(12, 30)` ve `(20, 5)` argümanlarıyla çağrıldığında dönen iki satırlık çıktı nedir?

```gercek
30
5
```

???
Fonksiyon prologdan sonra `[rbp - 4]` adresine 1. argümanı (`ecx`), `[rbp - 8]` adresine 2. argümanı (`edx`) yazar.
Ardından `push rcx` ve `push rdx` çalıştırılır; yığının en tepesinde artık `rdx` vardır.
LIFO kuralı gereği `pop rax` komutu en son itilen `rdx` değerini `rax`'e, `pop r8` komutu ise daha önce itilen `rcx` değerini `r8`'e çeker.
Böylece `sub eax, r8d` işlemi `edx - ecx` hesabını yapar; hemen ardından `add eax, DWORD PTR [rbp - 4]` komutu `[rbp - 4]` içindeki `ecx` değerini geri ekler: `(edx - ecx) + ecx = edx`.
1. çağrıda `(30 - 12) + 12 = 30`, 2. çağrıda `(5 - 20) + 20 = 5` döner.
:::

::: gorev LIFO `push` / `pop` ve `rsp` simülatörü
Başlangıçtaki `rsp` adresi (`baslangic_rsp`) ve başlangıç yazmaç sözlüğü (`yazmaclar`, ör. `{"rax": 10, "rbx": 20}`) verildiğinde, `komutlar` listesindeki yığın işlemlerini sırasıyla yürüten `yigin_simule_et(baslangic_rsp, yazmaclar, komutlar)` fonksiyonunu yaz:
- Girişteki `yazmaclar` sözlüğünü kopyala (orijinali değiştirme) ve `bellek = {}` (adres → 64-bit QWORD değer) oluştur.
- Desteklenecek komut biçimleri:
  - `"push <reg>"`: `rsp` değerini `8` azaltır; `bellek[rsp] = yazmaclar[reg]` yazar.
  - `"pop <reg>"`: `yazmaclar[reg] = bellek[rsp]` okur (`rsp` adresinde kayıt yoksa `KeyError` fırlatır); ardından `rsp` değerini `8` artırır.
  - `"sub rsp, <sayi>"`: `rsp` değerini `<sayi>` kadar azaltır (`<sayi>` onluk veya `0x` onaltılık olabilir).
  - `"add rsp, <sayi>"`: `rsp` değerini `<sayi>` kadar artırır.
- Sonuç olarak `(guncel_rsp, guncel_yazmaclar, bellek)` üçlüsünü döndür.

```starter
def yigin_simule_et(baslangic_rsp, yazmaclar, komutlar):
    return (baslangic_rsp, dict(yazmaclar), {})
```

```test
need("yigin_simule_et")
rsp0 = 0x1000
regs0 = {"rcx": 12, "rdx": 30, "rax": 0, "r8": 0}
rsp1, regs1, mem1 = yigin_simule_et(
    rsp0,
    regs0,
    ["push rcx", "push rdx", "pop rax", "pop r8"],
)
eq(rsp1, 0x1000, "2 push ve 2 pop sonunda rsp başlangıç değerine dönmeli")
eq(regs1["rax"], 30, "LIFO: ilk pop en son itilen rdx (30) değerini almalı")
eq(regs1["r8"], 12, "LIFO: ikinci pop ilk itilen rcx (12) değerini almalı")
eq(mem1[0xFF8], 12, "ilk push [0x1000 - 8] = 0xFF8 adresine yazmalı")
eq(mem1[0xFF0], 30, "ikinci push [0xFF8 - 8] = 0xFF0 adresine yazmalı")
eq(regs0["rax"], 0, "girişteki yazmaclar sözlüğü yerinde değiştirilmemeli")

rsp2, regs2, mem2 = yigin_simule_et(
    0x2000,
    {"rbp": 0x2050, "rax": 99},
    ["push rbp", "sub rsp, 0x20", "push rax", "pop rax", "add rsp, 32", "pop rbp"],
)
eq(rsp2, 0x2000, "prolog ve epilog sonunda rsp=0x2000 olmalı")
eq(regs2["rbp"], 0x2050, "rbp geri yüklenmeli")
eq(mem2[0x1FD0], 99, "sub rsp, 0x20 sonrası push rax 0x1FD0 adresine yazmalı")
raises(KeyError, lambda: yigin_simule_et(0x1000, {"rax": 1}, ["pop rax"]), msg="boş yığından pop KeyError fırlatmalı")
```

```solution
def yigin_simule_et(baslangic_rsp, yazmaclar, komutlar):
    rsp = baslangic_rsp
    regs = dict(yazmaclar)
    bellek = {}

    for satir in komutlar:
        temiz = satir.split(";")[0].strip()
        if not temiz:
            continue
        parcalar = [p.strip() for p in temiz.replace(",", " ").split()]
        op = parcalar[0].lower()
        if op == "push":
            reg = parcalar[1].lower()
            rsp -= 8
            bellek[rsp] = regs[reg]
        elif op == "pop":
            reg = parcalar[1].lower()
            if rsp not in bellek:
                raise KeyError(f"Yigin adresinde deger yok: {hex(rsp)}")
            regs[reg] = bellek[rsp]
            rsp += 8
        elif op == "sub" and parcalar[1].lower() == "rsp":
            rsp -= int(parcalar[2], 0)
        elif op == "add" and parcalar[1].lower() == "rsp":
            rsp += int(parcalar[2], 0)
        else:
            raise ValueError(f"Desteklenmeyen komut: {satir}")

    return (rsp, regs, bellek)
```

```hint
`push` işleminde önce `rsp -= 8` yapıp sonra `bellek[rsp] = regs[reg]` yaz; `pop` işleminde ise önce `bellek[rsp]` oku, sonra `rsp += 8` yap.
```
:::

::: gorev Fonksiyon çerçevesi ve yerel `[rbp - ofset]` analizi
Bir fonksiyonun assembly satırlarını analiz ederek yığında `sub rsp, N` ile kaç bayt yerel alan açıldığını ve hangi `[rbp - ofset]` yerel değişken ofsetlerine erişildiğini bulan `cerceve_yerel_ofsetler(satirlar)` fonksiyonunu yaz:
- Satırlarda `sub rsp, <N>` varsa `<N>` değerini (`int(N, 0)`) yerel alan boyutu olarak al (yoksa `0`).
- Satırlarda `[rbp - <ofset>]` kalıbıyla geçen tüm pozitif `<ofset>` tam sayılarını (`int(ofset, 0)`) tekrarsız ve **küçükten büyüğe sıralı** bir liste olarak döndür (`[rbp + 16]` gibi pozitif ofsetler parametre olduğu için dahil edilmez).

```starter
import re

def cerceve_yerel_ofsetler(satirlar):
    return (0, [])
```

```test
need("cerceve_yerel_ofsetler")
kod = [
    "push rbp",
    "mov rbp, rsp",
    "sub rsp, 0x20",
    "mov DWORD PTR [rbp - 4], ecx",
    "mov DWORD PTR [rbp - 12], edx",
    "mov eax, DWORD PTR [rbp - 4]",
    "add eax, DWORD PTR [rbp + 16] ; parametre, yerel değil",
]
eq(cerceve_yerel_ofsetler(kod), (32, [4, 12]), "0x20 (32 bayt) yerel alan ve [4, 12] ofsetleri")
eq(cerceve_yerel_ofsetler(["push rbp", "mov rbp, rsp", "pop rbp", "ret"]), (0, []), "sub rsp yoksa (0, [])")
eq(
    cerceve_yerel_ofsetler(["sub rsp, 48", "mov QWORD PTR [rbp - 0x10], rax", "mov DWORD PTR [rbp - 4], ecx"]),
    (48, [4, 16]),
    "hem onluk hem 0x onaltılık ofsetler küçükten büyüğe sıralanmalı",
)
```

```solution
import re


def cerceve_yerel_ofsetler(satirlar):
    alan = 0
    ofsetler = set()
    for satir in satirlar:
        temiz = satir.split(";")[0].strip()
        m_sub = re.search(r"\bsub\s+rsp\s*,\s*(0x[0-9a-fA-F]+|\d+)", temiz, re.IGNORECASE)
        if m_sub:
            alan = int(m_sub.group(1), 0)
        for m_ofs in re.finditer(r"\[\s*rbp\s*-\s*(0x[0-9a-fA-F]+|\d+)\s*\]", temiz, re.IGNORECASE):
            ofsetler.add(int(m_ofs.group(1), 0))
    return (alan, sorted(ofsetler))
```

```hint
Her satırda `;` yorumunu attıktan sonra `sub rsp, <sayi>` ve `\[rbp\s*-\s*<sayi>\]` desenlerini `re` ile yakalayıp `int(yakalanan, 0)` ile tam sayıya çevir.
```
:::
