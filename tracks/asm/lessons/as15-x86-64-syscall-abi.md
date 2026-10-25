---
id: as15
title: x86-64 syscall ABI'si ve ntdll Şablonu
summary: syscall komutu (0f 05) çekirdeğe doğrudan geçer: numara rax'te, argümanlar rdi, rsi, rdx, r10, r8, r9'da taşınır ve dönüş rax'tedir. Fonksiyon çağrı kuralından tek farkı dördüncü argümandır — orada rcx, burada r10; çünkü syscall dönüş adresini rcx'e, bayrakları r11'e yazar. Gerçek bir Windows ntdll stub'ındaki mov r10,rcx tam olarak bu farkı kapatır; ardından mov eax,<numara> ve syscall gelir.
---

::: anlat Çekirdeğe doğrudan geçmek
`AS07`'de fonksiyon çağrı kurallarını okudun: System V AMD64'te argümanlar `rdi, rsi, rdx, rcx, r8, r9` sırasıyla gider. Bir **sistem çağrısı** da argüman alır ama bir fonksiyon çağrısı değildir: `call` yoktur, yığına dönüş adresi itilmez; tek bir komut işlemciyi çekirdek kipine geçirir.

```asm
0f 05    syscall
```

Ölçülen bir Linux örneği (Kali, nasm 3.01 + objdump):

```asm
   0:	b8 01 00 00 00       	mov    eax,0x1      ; numara: write
   5:	bf 01 00 00 00       	mov    edi,0x1      ; 1. arg: fd
   a:	48 8d 35 11 00 00 00 	lea    rsi,[rip+0x11]  ; 2. arg: tampon
  11:	ba 0d 00 00 00       	mov    edx,0xd      ; 3. arg: uzunluk
  16:	0f 05                	syscall
  18:	b8 3c 00 00 00       	mov    eax,0x3c     ; numara: exit (60)
  1d:	48 31 ff             	xor    rdi,rdi      ; 1. arg: 0
  20:	0f 05                	syscall
```

Kalıp her zaman aynıdır: **numara `rax`'e**, argümanlar sırayla yazmaçlara, sonra `syscall`. Dönüş değeri yine `rax`'tedir; hata durumunda küçük bir negatif değer gelir.

`mov rax, 1` yazsan bile derleyici `b8 01 00 00 00`, yani `mov eax,0x1` üretir: 32-bit bir yazmaca yazmak üst 32 biti sıfırlar, sonuç aynıdır ve kodlama kısadır.
:::

::: anlat Dördüncü argüman neden r10?
Sistem çağrısı argümanları şu sırayla taşınır:

| Sıra | 1 | 2 | 3 | **4** | 5 | 6 |
|---|---|---|---|---|---|---|
| Fonksiyon (SysV) | rdi | rsi | rdx | **rcx** | r8 | r9 |
| Sistem çağrısı | rdi | rsi | rdx | **r10** | r8 | r9 |

Tek fark dördüncü sıradadır ve nedeni donanımdadır: `syscall` komutu dönüş adresini (`RIP`) **`rcx`'e**, bayrakları (`RFLAGS`) **`r11`'e** yazar. Yani `rcx` çağrı anında zaten eziliyor; argüman taşıyamaz. Çekirdek bu yüzden dördüncü argümanı `r10`'da bekler.

Aynı mantık Windows'ta da geçerlidir ve orada gözle görülür bir satıra dönüşür. Gerçek bir `C:\Windows\System32\ntdll.dll` üzerinde ölçülen stub:

```asm
1801618b0:	4c 8b d1                	mov    r10,rcx
1801618b3:	b8 0f 00 00 00          	mov    eax,0xf
1801618b8:	f6 04 25 08 03 fe 7f 01 	test   BYTE PTR ds:0x7ffe0308,0x1
1801618c0:	75 03                   	jne    0x1801618c5
1801618c2:	0f 05                   	syscall
1801618c4:	c3                      	ret
1801618c5:	cd 2e                   	int    0x2e
```

Satır satır: Windows x64 **fonksiyon** kuralında birinci argüman `rcx`'tedir; sistem çağrısı onu `r10`'da ister. `mov r10,rcx` bu köprüyü kurar. `mov eax,0xf` çağrı numarasını (15) koyar. Sonraki `test`/`jne`, `KUSER_SHARED_DATA` içindeki bir bayrağa bakıp eski `int 0x2e` yolunu kullanması gerekip gerekmediğine karar verir. Normal durumda `syscall` çalışır ve `ret` ile dönülür.

> [!TUZAK] Numara sürüme bağlıdır, komut değil
> `0f 05` her x86-64 Linux ve Windows'ta aynıdır, ama `mov eax, 0xf` içindeki **sayı** öyle değildir. Linux'ta numaralar mimariye göre değişir (x86-64'te write 1, exit 60; 32-bit x86'da bambaşka), Windows'ta ise `ntdll` sürümünden sürümüne kayar — sabit bir tablo yoktur. Bir dökümde gördüğün numarayı "şu çağrıdır" diye okurken hangi sürümün tablosuna baktığını da yazmalısın.

Bir ikilide `0f 05` aramak, kodun `libc`/`ntdll` üzerinden değil **doğrudan** çekirdeğe gittiği yerleri bulmanın hızlı yoludur. Sıradan bir uygulamada bu komut neredeyse yalnız `libc`'nin ya da `ntdll`'in içinde bulunur; başka bir modülde görülmesi, o kodun kütüphane katmanını atladığını söyler.
:::

::: tahmin ntdll stub'ı ne yapıyor?
Aşağıdaki yedi satır gerçek bir `ntdll.dll`'den alındı. `rcx`'teki değer çağrıya nasıl ulaşır ve çağrı numarası kaçtır?

```asm
1801618b0:	4c 8b d1                	mov    r10,rcx
1801618b3:	b8 0f 00 00 00          	mov    eax,0xf
1801618b8:	f6 04 25 08 03 fe 7f 01 	test   BYTE PTR ds:0x7ffe0308,0x1
1801618c0:	75 03                   	jne    0x1801618c5
1801618c2:	0f 05                   	syscall
1801618c4:	c3                      	ret
1801618c5:	cd 2e                   	int    0x2e
```

```gercek
1. arguman: rcx -> r10   (fonksiyon kurali rcx, syscall kurali r10)
cagri numarasi: 0xf = 15 (bu ntdll surumunde)
normal yol: syscall (0f 05) ; eski yol: int 0x2e
```

???

Birinci argüman `rcx`'ten **`r10`'a kopyalanır**. Çağıran bu stub'a normal bir Windows x64 fonksiyonu gibi gelmiştir, yani birinci argümanı `rcx`'e koymuştur; ama `syscall` `rcx`'i dönüş adresiyle ezeceği için çekirdek dördüncü argümanı... daha doğrusu **birinci** argümanı da dahil olmak üzere kuralın `r10` kullandığı sırayı bekler. `mov r10,rcx` iki kuralın arasını kapatan tek satırdır.

Çağrı numarası `eax`'e konan **`0xf`**, yani 15. Bu sayı `ntdll` sürümüne bağlıdır; başka bir Windows derlemesinde aynı fonksiyon başka bir numara taşıyabilir.

`test`/`jne` çifti `0x7ffe0308` adresindeki bayrağı yoklar ve gerekirse `int 0x2e`'ye dallanır — `syscall` komutunun kullanılamadığı durumlar için bırakılmış eski yol. Olağan akışta `0f 05` çalışır, çekirdek işi yapar ve `ret` ile çağırana dönülür.

Dikkat: burada `call` yok. Stub'ın kendisi sıradan bir fonksiyondur ve `ret` ile döner, ama içindeki geçiş bir fonksiyon çağrısı değildir.
:::

::: gorev Hangi yazmaç, hangi sıra?
`yazmaclar(abi, argSayisi)` yaz: ilk `argSayisi` argümanın hangi yazmaçlarda taşındığını sırayla döndür.

- `abi` `"fonksiyon"` ise sıra: `rdi, rsi, rdx, rcx, r8, r9`.
- `abi` `"syscall"` ise sıra: `rdi, rsi, rdx, r10, r8, r9`.
- Altıdan fazlası istenirse kalan her argüman için `"yigin"` yaz.

```starter
SIRA = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]

def yazmaclar(abi, argSayisi):
    return SIRA[:argSayisi]
```

```test
need("yazmaclar")
eq(yazmaclar("fonksiyon", 3), ["rdi", "rsi", "rdx"], "ilk üçü iki ABI'de de aynı")
eq(yazmaclar("syscall", 3), ["rdi", "rsi", "rdx"], "ilk üçte fark yok")
eq(yazmaclar("fonksiyon", 4), ["rdi", "rsi", "rdx", "rcx"], "fonksiyon kuralında dördüncü rcx")
eq(yazmaclar("syscall", 4), ["rdi", "rsi", "rdx", "r10"], "syscall kuralında dördüncü r10")
eq(yazmaclar("syscall", 6), ["rdi", "rsi", "rdx", "r10", "r8", "r9"], "altı argüman")
eq(yazmaclar("fonksiyon", 6), ["rdi", "rsi", "rdx", "rcx", "r8", "r9"], "altı argüman, fonksiyon")
eq(yazmaclar("syscall", 8), ["rdi", "rsi", "rdx", "r10", "r8", "r9", "yigin", "yigin"],
   "altıdan sonrası yığına taşar")
eq(yazmaclar("fonksiyon", 0), [], "argümansız")
```

```solution
def yazmaclar(abi, argSayisi):
    sira = ["rdi", "rsi", "rdx", "r10" if abi == "syscall" else "rcx", "r8", "r9"]
    return [sira[i] if i < 6 else "yigin" for i in range(argSayisi)]
```

```hint
İki sıra yalnız dördüncü öğede ayrılır; listeyi `abi`'ye göre o tek konumda değiştir. Altıncıdan sonrası için `"yigin"` üret — dilimleme (`[:n]`) fazlasını sessizce kırpar, oysa argümanlar kaybolmaz.
```
:::

::: gorev Stub'ı çöz
`stubOku(satirlar)` yaz: bir disassembly parçasının sistem çağrısı stub'ı olup olmadığını çözümle.

`satirlar`, `"mov r10,rcx"` gibi komut dizgilerinin listesidir. Dönüş `(numara, r10Kopyalandi, dogrudanSyscall)`:

- `numara`: `syscall` komutundan **önce** `eax` ya da `rax`'e taşınan son sabitin tam sayı değeri; böyle bir satır yoksa `None`. Sabitler `0x` önekiyle onaltılık yazılır.
- `r10Kopyalandi`: `"mov r10,rcx"` satırı var mı.
- `dogrudanSyscall`: `"syscall"` satırı var mı.

`syscall`'dan sonraki satırlar numarayı etkilemez.

```starter
def stubOku(satirlar):
    numara = None
    for s in satirlar:
        if s.startswith("mov eax,"):
            numara = int(s.split(",")[1], 16)
    return (numara, "mov r10,rcx" in satirlar, "syscall" in satirlar)
```

```test
need("stubOku")
NTDLL = ["mov r10,rcx", "mov eax,0xf", "test BYTE PTR ds:0x7ffe0308,0x1", "jne 0x1801618c5",
         "syscall", "ret", "int 0x2e"]
eq(stubOku(NTDLL), (15, True, True), "ölçülen gerçek ntdll stub'ı: numara 0xf, r10 köprüsü, doğrudan syscall")
eq(stubOku(["mov rax,0x3c", "xor rdi,rdi", "syscall"]), (60, False, True),
   "ölçülen Linux exit: rax'e yazılır, r10 köprüsü yoktur")
eq(stubOku(["mov eax,0x1", "mov edi,0x1", "syscall"]), (1, False, True), "Linux write")
eq(stubOku(["mov eax,0x1", "syscall", "mov eax,0x3c", "syscall"]), (1, False, True),
   "ilk syscall'dan sonraki atama numarayı değiştirmez")
eq(stubOku(["mov r10,rcx", "mov eax,0xf", "ret"]), (15, True, False),
   "syscall satırı yok: stub değil")
eq(stubOku(["push rbp", "mov rbp,rsp", "ret"]), (None, False, False), "sıradan fonksiyon")
eq(stubOku(["syscall"]), (None, False, True), "numara yüklenmemiş")
eq(stubOku([]), (None, False, False), "boş liste")
```

```solution
def stubOku(satirlar):
    numara = None
    for s in satirlar:
        if s == "syscall":
            break
        if s.startswith("mov eax,") or s.startswith("mov rax,"):
            numara = int(s.split(",", 1)[1], 16)
    return (numara, "mov r10,rcx" in satirlar, "syscall" in satirlar)
```

```hint
Başlangıç kodu iki şeyi kaçırıyor: `rax`'e yazan satırları hiç görmüyor ve `syscall`'dan sonrasını da tarıyor. Döngüyü ilk `syscall` satırında kes; numara ondan **önceki** son atamadır.
```
:::
