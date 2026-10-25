---
id: as16
title: Debugger İzi · Yazmaç Kanıtı ve Dolaylı Çağrı Hedefi
summary: Statik dökümde "call *%rcx" hedefi söylemez; hedef ancak çalışma anındaki yazmaç değeriyle bilinir. GDB ile kesme noktası koyup yazmaçları okumak, info symbol ile adresi sembole çevirmek, stepi ile çağrıya girmek ve finish ile dönüş değerini almak; prolog çalışmadan önce GDB'nin argüman gösteriminin güvenilmemesi (a=0, b=0) ve GDB'nin varsayılan AT&T sözdiziminin objdump -M intel çıktısından farkı.
---

::: anlat Dökümün söylemediği şey
`AS11` ve `AS13`'te statik döküm okudun. Statik dökümün bir sınırı vardır ve en açık göründüğü yer **dolaylı çağrılardır**:

```asm
  40116d:	ff d1                	call   rcx
```

Bu satır "bir yere çağrı yapılıyor" der, nereye olduğunu **söylemez**. Hedef `rcx`'in o andaki değeridir; değer çalışma zamanında belirlenir. Fonksiyon işaretçileri, sanal metot tabloları, eklenti kayıtları ve `GetProcAddress`/`dlsym` ile çözülen semboller hep bu satıra benzer kod üretir.

Eksik bilgiyi **debugger** tamamlar. GDB'yi toplu (batch) kipte, tek bir komut satırından çalıştırabilirsin:

```bash norun
gdb -q -batch -ex 'break *0x40116d' -ex 'run' -ex 'info symbol $rcx' ./f
```

| Komut | Ne verir |
|---|---|
| `break *ADRES` | tam o komutta durur (`break fonksiyon` prologdan sonra durur) |
| `run` | programı başlatır |
| `info args` | geçerli çerçevenin argümanları |
| `info symbol $reg` | yazmaçtaki **adresi sembole** çevirir |
| `x/1i $pc` | o anki komutu gösterir |
| `stepi` | tek makine komutu ilerler |
| `finish` | geçerli fonksiyondan çıkar ve dönüş değerini yazar |

Bu dersin izi, yerelde derlenmiş küçük bir programdan alındı (Kali, gcc 16.2.0 `-no-pie -O0 -g`, GDB 17.2).
:::

::: anlat İzi okumak
Ölçülen izin tamamı aşağıdaki tahminde; önce içindeki üç inceliği ayıralım.

**Hedef yazmaçta durur.** Kesme noktası `call rcx` komutunun üstündeyken `rcx = 0x40113a` ve `info symbol $rcx` bunu `carp` diye çözer. Aynı anda `rdi = 6`, `rsi = 7`: çağrılacak fonksiyonun argümanları çoktan yerleştirilmiş durumda. Yani tek bir duraklamada hem **hedefi** hem **argümanları** görürsün — statik dökümden çıkaramayacağın iki bilgi.

**Sözdizimi değişir.** GDB varsayılan olarak AT&T sözdizimi kullanır ve aynı komutu `call *%rcx` diye yazar; `objdump -M intel` ise `call rcx` der. Aynı bayt (`ff d1`), iki farklı yazım. İzleri karşılaştırırken hangi sözdiziminde olduğunu bilmek gerekir (`set disassembly-flavor intel` ile GDB'yi de Intel'e çevirebilirsin).

> [!TUZAK] Prolog çalışmadan argümanlara bakma
> `stepi` ile çağrının içine girdiğinde GDB `carp (a=0, b=0)` yazar — oysa çağrı `6` ve `7` ile yapıldı. Yanlış olan GDB değil: fonksiyonun ilk komutundasın, prolog henüz çalışmadı, argümanlar yığın çerçevesine yazılmadı. GDB çerçeveyi okuyup olmayan değerleri `0` gösteriyor. Argümanların doğru görünmesi için ya prologdan sonraya geç (`break carp` zaten oraya koyar) ya da değerleri çağıran taraftaki yazmaçlardan oku.

**Dönüş değeri.** `finish` fonksiyondan çıkar ve `Value returned is $1 = 42` satırını basar; aynı değer `rax`'tedir (`6 * 7`). Bir dönüş değerini doğrularken ikisi aynı şeydir: `finish`'in bastığı değer, `rax`'in yorumlanmış hâlidir.
:::

::: tahmin İz ne söylüyor?
`uygula(islem, 6, 7)` çağrılıyor ve `islem` bir fonksiyon işaretçisi. `0x40116d` adresindeki komut `ff d1` (`call rcx`).

```asm
; gdb -q -batch -ex 'break *0x40116d' -ex run \
;   -ex 'printf "rcx=%#lx rdi=%d rsi=%d\n", $rcx, (int)$rdi, (int)$rsi' \
;   -ex 'info symbol $rcx' -ex 'x/1i $pc' -ex stepi \
;   -ex 'info symbol $pc' -ex finish ./f
```

```gercek
Breakpoint 1, 0x000000000040116d in uygula (f=0x40113a <carp>, a=6, b=7) at f.c:4
rcx=0x40113a rdi=6 rsi=7
carp in section .text of /home/demo/pafta-lab/gdb/f
=> 0x40116d <uygula+32>:	call   *%rcx
carp (a=0, b=0) at f.c:3
simdi buradayiz: carp in section .text of /home/demo/pafta-lab/gdb/f
uygula (f=0x40113a <carp>, a=6, b=7) at f.c:4
Value returned is $1 = 42
donus rax=42
```

???

`rcx=0x40113a` ve `info symbol` bunu **`carp`** diye çözüyor: dolaylı çağrının hedefi bu. Statik dökümde `call rcx` satırına bakarak bunu bilemezdin; `topla` da olabilirdi.

`rdi=6 rsi=7`: çağrının argümanları, çağrı yapılmadan hemen önce yerlerinde. Dikkat: `uygula`'ya girerken `rdi` **fonksiyon işaretçisiydi**; burada artık `6`. Yazmaçlar fonksiyon boyunca yeniden kullanılır, bu yüzden "hangi anda baktığın" sorusu değerin kendisi kadar önemlidir.

`=> 0x40116d <uygula+32>:	call   *%rcx`: GDB AT&T sözdizimiyle yazıyor; `objdump -M intel` aynı baytları `call rcx` diye gösterir.

`carp (a=0, b=0)`: `stepi` bizi `carp`'ın ilk komutuna getirdi ama prolog çalışmadığı için GDB argümanları okuyamıyor ve `0` gösteriyor. Değerler kaybolmadı — `rdi` ve `rsi`'de duruyorlar.

`Value returned is $1 = 42`: `finish` ile `carp`'tan çıkıldı; `6 * 7 = 42`, aynı değer `rax`'te. Çarpma olduğu için hedefin `topla` değil `carp` olduğu burada bir kez daha doğrulanıyor.
:::

::: gorev Dolaylı çağrının hedefini çöz
`cagriHedefi(komut, yazmaclar)` yaz: bir çağrı komutundan hedef adresi çıkar.

- `"call *%REG"` (AT&T) ya da `"call REG"` (Intel): hedef `yazmaclar[REG]`'dir; yazmaç tabloda yoksa `None`.
- `"call 0xADRES"`: hedef o sabit adrestir.
- `"call *0xADRES"`: hedef **bellekten** okunacaktır; bu görevde değeri bilinmiyor, `"bellek"` döndür.
- Çağrı olmayan her komut için `None`.

```starter
def cagriHedefi(komut, yazmaclar):
    if not komut.startswith("call"):
        return None
    hedef = komut.split()[1]
    return yazmaclar.get(hedef)
```

```test
need("cagriHedefi")
R = {"rcx": 0x40113a, "rax": 0x401122, "rdx": 0x401100}
eq(cagriHedefi("call *%rcx", R), 0x40113a, "ölçülen iz: AT&T yazımı, hedef rcx'te")
eq(cagriHedefi("call rcx", R), 0x40113a, "objdump -M intel aynı baytı böyle yazar")
eq(cagriHedefi("call *%rax", R), 0x401122, "başka yazmaç")
eq(cagriHedefi("call 0x40113a", R), 0x40113a, "doğrudan çağrı: adres komutun içinde")
eq(cagriHedefi("call *0x404018", R), "bellek", "bellekten dolaylı: değer çalışma anında okunur")
eq(cagriHedefi("call *%rbx", R), None, "yazmaç tabloda yok")
eq(cagriHedefi("mov eax,0x1", R), None, "çağrı değil")
eq(cagriHedefi("ret", R), None, "çağrı değil")
eq(cagriHedefi("jmp *%rcx", R), None, "atlama çağrı sayılmaz")
eq(cagriHedefi("cmp rcx,0x0", R), None, "c ile başlayan başka komutlar çağrı değildir")
eq(cagriHedefi("cqo", R), None, "işlenensiz komut: ayrıştırmaya hiç girilmemeli")
```

```solution
def cagriHedefi(komut, yazmaclar):
    if not komut.startswith("call"):
        return None
    hedef = komut.split(None, 1)[1].strip()
    if hedef.startswith("*0x"):
        return "bellek"
    if hedef.startswith("0x"):
        return int(hedef, 16)
    return yazmaclar.get(hedef.lstrip("*%"))
```

```hint
Üç biçimi ayır: `*0x...` bellekten, `0x...` sabit, geri kalanı yazmaç. Yazmaç adından önce gelen `*` ve `%` işaretlerini temizle (`lstrip("*%")`), yoksa tabloda bulamazsın.
```
:::

::: gorev Adresi sembole çevir
`sembolBul(adres, tablo)` yaz: `info symbol` gibi, bir adresin hangi sembolün içine düştüğünü söyle.

`tablo`, `(ad, baslangic, boyut)` demetlerinden oluşur. Adres `baslangic <= adres < baslangic + boyut` koşulunu sağlayan sembole aittir.

- Tam başlangıçtaysa yalnız `ad` döndür.
- İçerideyse `"ad+N"` döndür; `N` ondalık uzaklık.
- Hiçbir sembole düşmüyorsa `None`.

```starter
def sembolBul(adres, tablo):
    for ad, baslangic, boyut in tablo:
        if adres == baslangic:
            return ad
    return None
```

```test
need("sembolBul")
T = [("topla", 0x401126, 0x14), ("carp", 0x40113a, 0x13), ("uygula", 0x40114d, 0x24)]
eq(sembolBul(0x40113a, T), "carp", "ölçülen iz: rcx tam carp'ın başını gösteriyor")
eq(sembolBul(0x40116d, T), "uygula+32", "ölçülen iz: call komutu uygula+32'de")
eq(sembolBul(0x401126, T), "topla", "sembolün ilk baytı")
eq(sembolBul(0x401127, T), "topla+1", "bir bayt içeride")
eq(sembolBul(0x401139, T), "topla+19", "topla'nın son baytı (boyut 0x14)")
eq(sembolBul(0x401125, T), None, "ilk sembolden önce")
eq(sembolBul(0x401171, T), None, "son sembolden sonra")
eq(sembolBul(0x40113a, []), None, "sembol tablosu boş")
```

```solution
def sembolBul(adres, tablo):
    for ad, baslangic, boyut in tablo:
        if baslangic <= adres < baslangic + boyut:
            uzaklik = adres - baslangic
            return ad if uzaklik == 0 else f"{ad}+{uzaklik}"
    return None
```

```hint
Başlangıç kodu yalnız tam eşleşmeyi buluyor; oysa bir yığın izindeki adreslerin çoğu fonksiyonun ortasına düşer. Aralığı denetle ve uzaklığı `ad+N` biçiminde ekle — `N` onaltılık değil, ondalık yazılır.
```
:::
