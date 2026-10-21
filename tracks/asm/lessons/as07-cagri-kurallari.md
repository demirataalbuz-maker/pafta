---
id: as07
title: Çağrı Kuralları (ABI): Windows x64 ve System V
rank: buyuk-orta
order: 7
summary: call/ret mekanizmasını, Windows x64 (rcx, rdx, r8, r9 + gölge alan) ile Linux System V (rdi, rsi, rdx, rcx, r8, r9) argüman aktarımını ve uçucu yazmaçları okumak.
---

::: anlat
Derlenmiş bir ikili dosyada (binary) kaynak kod olmasa bile, bir fonksiyonun **hangi argümanları aldığını** ve **ne döndürdüğünü** işletim sisteminin **ABI (Application Binary Interface / Çağrı Kuralı)** standardı sayesinde kesin olarak okuyabiliriz.

### `call` ve `ret` Ne Yapar?

Bir fonksiyon çağrısı (`call hedef`) ve dönüşü (`ret`), `rip` ve `rsp` yazmaçlarını birlikte günceller:

- **`call hedef`:** `call` komutundan hemen sonraki komutun adresini (**dönüş adresi**) yığına iter (`push rip_sonraki`, yani `rsp -= 8`) ve `rip = hedef` yaparak fonksiyona sıçrar.
- **`ret`:** Yığının en tepesindeki 8 baytlık dönüş adresini çeker (`pop rip`, yani `rsp += 8`) ve çağıran fonksiyona geri döner.
- **Dönüş değeri:** Her iki ABI'de de tam sayı ve işaretçi dönüş değerleri **`rax` / `eax`** yazmacında döner.

### Windows x64 ABI ile System V AMD64 ABI (Linux/macOS) Karşılaştırması

x86-64 dünyasında iki ana çağrı kuralı vardır. Disassembly okurken hedef platformun Windows (`.exe` / `.dll` / PE) mu yoksa Linux/macOS (`ELF` / `Mach-O`) mu olduğuna göre ilk bakacağınız yazmaçlar değişir:

| Özellik | Windows x64 ABI (Microsoft) | System V AMD64 ABI (Linux, macOS, BSD) |
|---|---|---|
| **1. Argüman** | `rcx` (`ecx`) | `rdi` (`edi`) |
| **2. Argüman** | `rdx` (`edx`) | `rsi` (`esi`) |
| **3. Argüman** | `r8` (`r8d`) | `rdx` (`edx`) |
| **4. Argüman** | `r9` (`r9d`) | `rcx` (`ecx`) |
| **5. Argüman** | Yığında: girişte `[rsp + 40]` (`0x28`) | `r8` (`r8d`) |
| **6. Argüman** | Yığında: girişte `[rsp + 48]` (`0x30`) | `r9` (`r9d`) |
| **7. Argüman** | Yığında: girişte `[rsp + 56]` (`0x38`) | Yığında: girişte `[rsp + 8]` (`0x08`) |
| **Dönüş Değeri** | `rax` (`eax`) | `rax` (`eax`) |
| **Gölge Alan (Shadow Space)** | **Zorunlu 32 bayt** (`0x20`): Çağıran her `call` öncesi yığında 32 bayt boşluk bırakır | Yok (bunun yerine yaprak fonksiyonlar için 128 bayt *Red Zone* vardır) |
| **Uçucu (Caller-saved)** | `rax, rcx, rdx, r8, r9, r10, r11` | `rax, rdi, rsi, rdx, rcx, r8, r9, r10, r11` |
| **Kalıcı (Callee-saved)** | `rbx, rbp, rdi, rsi, r12, r13, r14, r15` | `rbx, rbp, r12, r13, r14, r15` |

> [!NOT]
> **Windows x64'te 5. argüman neden `[rsp + 40]` adresindedir?**
> Çağıran fonksiyon 5. argümanı yığına koyduktan sonra alt fonksiyonun kullanabilmesi için **32 baytlık gölge alan (shadow space / home space)** ayırır ve ardından `call` yapar. `call` komutu da yığına **8 baytlık dönüş adresini** iter (`32 + 8 = 40`). Bu yüzden fonksiyonun ilk satırında `[rsp]` dönüş adresidir, `[rsp + 8 .. rsp + 39]` gölge alandır ve **5. argüman `[rsp + 40]` (`[rsp + 0x28]`)** adresindedir.

> [!TUZAK]
> Eğer fonksiyon kendi prologunda `sub rsp, 40` yaparsa, `rsp` 40 bayt aşağı indiği için girişte `[rsp + 40]` adresinde duran 5. argümana artık **`[rsp + 80]`** (`40 + 40`) üzerinden erişilir! Ayrıca `r8` ve `r9` **uçucu (caller-saved)** yazmaçlar olduğundan, içeride başka bir `call` yapılacaksa `call` öncesinde yığına kaydedilmeleri gerekir.

```asm
; Windows x64: int as07_hesapla5(int a, int b, int c, int d, int e)
; Girişte: ecx=a, edx=b, r8d=c, r9d=d, [rsp + 40]=e
as07_ic_carp:
    mov eax, ecx                    #! eax = a
    imul eax, edx                   #! eax = a * b
    ret

as07_hesapla5:
    sub rsp, 40                     #! 32B gölge alan + 8B hizalama = 40B (rsp -= 40)
    mov DWORD PTR [rsp + 32], r8d   #! Uçucu r8d (c) değerini call öncesi yığına sakla
    mov DWORD PTR [rsp + 36], r9d   #! Uçucu r9d (d) değerini call öncesi yığına sakla
    call as07_ic_carp               #! eax = as07_ic_carp(a, b) -> a * b
    add eax, DWORD PTR [rsp + 32]   #! eax += c
    sub eax, DWORD PTR [rsp + 36]   #! eax -= d
    mov edx, DWORD PTR [rsp + 80]   #! 5. argüman e: girişte [rsp+40] idi, sub rsp,40 sonrası [rsp+80]
    add eax, edx                    #! eax += e
    add rsp, 40                     #! Yığını geri topla
    ret
```
:::

::: tahmin
```asm
; Windows x64 ABI (ecx, edx, r8d, r9d, [rsp + 40])
as07_ic_carp:
    mov eax, ecx
    imul eax, edx
    ret

as07_hesapla5:
    sub rsp, 40
    mov DWORD PTR [rsp + 32], r8d
    mov DWORD PTR [rsp + 36], r9d
    call as07_ic_carp
    add eax, DWORD PTR [rsp + 32]
    sub eax, DWORD PTR [rsp + 36]
    mov edx, DWORD PTR [rsp + 80]
    add eax, edx
    add rsp, 40
    ret

; Çağrılar:
; 1) as07_hesapla5(4, 5, 10, 3, 2)
; 2) as07_hesapla5(2, 6, 1, 5, 10)
```

Yukarıdaki `as07_hesapla5` fonksiyonu sırasıyla `(4, 5, 10, 3, 2)` ve `(2, 6, 1, 5, 10)` argümanlarıyla çağrıldığında dönen iki satırlık çıktı nedir?

```gercek
29
18
```

???
Windows x64 ABI'ye göre `ecx = a`, `edx = b`, `r8d = c`, `r9d = d` ve 5. argüman `e` fonksiyon girişinde `[rsp + 40]` adresindedir (`sub rsp, 40` sonrasında `[rsp + 80]`).
Fonksiyon önce `as07_ic_carp(a, b)` çağrısıyla `eax = a * b` hesaplar; ardından sakladığı `c` (`[rsp + 32]`) değerini ekler, `d` (`[rsp + 36]`) değerini çıkarır ve 5. argüman `e` (`[rsp + 80]`) değerini ekler: `a * b + c - d + e`.
1. çağrıda `4 * 5 + 10 - 3 + 2 = 20 + 10 - 3 + 2 = 29` döner.
2. çağrıda `2 * 6 + 1 - 5 + 10 = 12 + 1 - 5 + 10 = 18` döner.
:::

::: gorev Windows x64 ve System V AMD64 argüman konumu çözücü
Verilen `abi` (`"win64"` veya `"sysv"`), argüman sırası `arg_no` (1'den başlayan tam sayı: `1, 2, 3, ...`) ve fonksiyon prologunda yapılan `sub_rsp` miktarı (varsayılan `0`) için argümanın fonksiyon gövdesinde okunduğu konumu döndüren `arguman_konumu(abi, arg_no, sub_rsp=0)` fonksiyonunu yaz:
- `arg_no < 1` veya `sub_rsp < 0` ise `ValueError` fırlat.
- `abi == "win64"`:
  - `1..4` için sırasıyla `"rcx"`, `"rdx"`, `"r8"`, `"r9"` döndür (`sub_rsp` yazmaçtaki argümanı etkilemez).
  - `5` ve üzeri için: fonksiyon girişinde 5. argüman `[rsp + 40]`, 6. argüman `[rsp + 48]` (`40 + (arg_no - 5) * 8`) adresindedir. Prologda `sub rsp, sub_rsp` yapıldıysa ofsete `sub_rsp` eklenir ve `f"[rsp + {ofset}]"` biçiminde döner.
- `abi == "sysv"`:
  - `1..6` için sırasıyla `"rdi"`, `"rsi"`, `"rdx"`, `"rcx"`, `"r8"`, `"r9"` döndür.
  - `7` ve üzeri için: fonksiyon girişinde 7. argüman `[rsp + 8]`, 8. argüman `[rsp + 16]` (`8 + (arg_no - 7) * 8`) adresindedir. Prologda `sub rsp, sub_rsp` yapıldıysa ofsete `sub_rsp` eklenir ve `f"[rsp + {ofset}]"` biçiminde döner.
- Tanınmayan `abi` değerinde `ValueError` fırlat.

```starter
def arguman_konumu(abi, arg_no, sub_rsp=0):
    return "rcx"
```

```test
need("arguman_konumu")
eq(arguman_konumu("win64", 1), "rcx", "win64 1. argüman rcx")
eq(arguman_konumu("win64", 2), "rdx", "win64 2. argüman rdx")
eq(arguman_konumu("win64", 3), "r8", "win64 3. argüman r8")
eq(arguman_konumu("win64", 4, sub_rsp=40), "r9", "win64 4. argüman r9 (sub_rsp etkilemez)")
eq(arguman_konumu("win64", 5), "[rsp + 40]", "win64 5. argüman girişte [rsp + 40]")
eq(arguman_konumu("win64", 5, sub_rsp=40), "[rsp + 80]", "win64 5. argüman sub rsp, 40 sonrası [rsp + 80]")
eq(arguman_konumu("win64", 6, sub_rsp=40), "[rsp + 88]", "win64 6. argüman sub rsp, 40 sonrası [rsp + 88]")
eq(arguman_konumu("sysv", 1), "rdi", "sysv 1. argüman rdi")
eq(arguman_konumu("sysv", 2), "rsi", "sysv 2. argüman rsi")
eq(arguman_konumu("sysv", 3), "rdx", "sysv 3. argüman rdx")
eq(arguman_konumu("sysv", 4), "rcx", "sysv 4. argüman rcx")
eq(arguman_konumu("sysv", 5), "r8", "sysv 5. argüman r8")
eq(arguman_konumu("sysv", 6), "r9", "sysv 6. argüman r9")
eq(arguman_konumu("sysv", 7), "[rsp + 8]", "sysv 7. argüman girişte [rsp + 8]")
eq(arguman_konumu("sysv", 7, sub_rsp=24), "[rsp + 32]", "sysv 7. argüman sub rsp, 24 sonrası [rsp + 32]")
eq(arguman_konumu("sysv", 8, sub_rsp=24), "[rsp + 40]", "sysv 8. argüman sub rsp, 24 sonrası [rsp + 40]")
raises(ValueError, lambda: arguman_konumu("win64", 0, 0), msg="arg_no < 1 için ValueError")
raises(ValueError, lambda: arguman_konumu("sysv", 1, -8), msg="sub_rsp < 0 için ValueError")
raises(ValueError, lambda: arguman_konumu("arm64", 1, 0), msg="bilinmeyen ABI için ValueError")
```

```solution
WIN64_REGS = ("rcx", "rdx", "r8", "r9")
SYSV_REGS = ("rdi", "rsi", "rdx", "rcx", "r8", "r9")


def arguman_konumu(abi, arg_no, sub_rsp=0):
    if arg_no < 1 or sub_rsp < 0:
        raise ValueError("Gecersiz arg_no veya sub_rsp")
    norm = abi.strip().lower()
    if norm == "win64":
        if arg_no <= 4:
            return WIN64_REGS[arg_no - 1]
        ofset = 40 + (arg_no - 5) * 8 + sub_rsp
        return f"[rsp + {ofset}]"
    if norm == "sysv":
        if arg_no <= 6:
            return SYSV_REGS[arg_no - 1]
        ofset = 8 + (arg_no - 7) * 8 + sub_rsp
        return f"[rsp + {ofset}]"
    raise ValueError(f"Bilinmeyen ABI: {abi}")
```

```hint
Windows x64'te ilk 4 argüman `("rcx", "rdx", "r8", "r9")` yazmaçlarında, 5. argüman ise `40 + (arg_no - 5) * 8 + sub_rsp` ofsetindedir. System V'de ilk 6 argüman `("rdi", "rsi", "rdx", "rcx", "r8", "r9")` yazmaçlarında, 7. argüman `8 + (arg_no - 7) * 8 + sub_rsp` ofsetindedir.
```
:::

::: gorev Uçucu (caller-saved) ve kalıcı (callee-saved) yazmaç sınıflandırıcı
Verilen `abi` (`"win64"` veya `"sysv"`) ve 64-bit yazmaç listesi (`yazmaclar`) için hangi yazmaçların alt fonksiyon çağrısında (`call`) bozulabileceğini (**uçucu / caller-saved**), hangilerinin alt fonksiyon tarafından korunmak zorunda olduğunu (**kalıcı / callee-saved**) ayıran `yazmac_siniflandir(abi, yazmaclar)` fonksiyonunu yaz:
- Giriş listesindeki sırayı koruyarak `{"ucucu": [...], "kalici": [...]}` sözlüğü döndür (`rdi` ve `rsi` yazmaçlarının Windows x64'te **kalıcı**, System V'de ise **uçucu** olduğuna dikkat et!).
- Tanınmayan ABI veya yazmaç verilirse `ValueError` fırlat.

```starter
def yazmac_siniflandir(abi, yazmaclar):
    return {"ucucu": [], "kalici": []}
```

```test
need("yazmac_siniflandir")
liste = ["rax", "rcx", "rdi", "rsi", "rbx", "r8", "r12"]
eq(
    yazmac_siniflandir("win64", liste),
    {"ucucu": ["rax", "rcx", "r8"], "kalici": ["rdi", "rsi", "rbx", "r12"]},
    "win64'te rdi ve rsi kalıcıdır (callee-saved)",
)
eq(
    yazmac_siniflandir("sysv", liste),
    {"ucucu": ["rax", "rcx", "rdi", "rsi", "r8"], "kalici": ["rbx", "r12"]},
    "sysv'de rdi ve rsi ilk iki argüman olduğu için uçucudur (caller-saved)",
)
raises(ValueError, lambda: yazmac_siniflandir("win64", ["xmm0"]), msg="bilinmeyen yazmaç için ValueError")
raises(ValueError, lambda: yazmac_siniflandir("mips", ["rax"]), msg="bilinmeyen ABI için ValueError")
```

```solution
WIN64_UCUCU = {"rax", "rcx", "rdx", "r8", "r9", "r10", "r11"}
WIN64_KALICI = {"rbx", "rbp", "rdi", "rsi", "r12", "r13", "r14", "r15"}

SYSV_UCUCU = {"rax", "rdi", "rsi", "rdx", "rcx", "r8", "r9", "r10", "r11"}
SYSV_KALICI = {"rbx", "rbp", "r12", "r13", "r14", "r15"}


def yazmac_siniflandir(abi, yazmaclar):
    norm = abi.strip().lower()
    if norm == "win64":
        ucucu_kume, kalici_kume = WIN64_UCUCU, WIN64_KALICI
    elif norm == "sysv":
        ucucu_kume, kalici_kume = SYSV_UCUCU, SYSV_KALICI
    else:
        raise ValueError(f"Bilinmeyen ABI: {abi}")

    ucucu = []
    kalici = []
    for reg in yazmaclar:
        r = reg.strip().lower()
        if r in ucucu_kume:
            ucucu.append(r)
        elif r in kalici_kume:
            kalici.append(r)
        else:
            raise ValueError(f"Bilinmeyen yazmac: {reg}")
    return {"ucucu": ucucu, "kalici": kalici}
```

```hint
Windows x64 ve System V için uçucu/kalıcı yazmaç kümelerini ayrı tanımla; `rdi` ve `rsi` yalnızca Windows x64'te kalıcıdır.
```
:::
