---
id: as13
title: Yükleyici Bağlamı · Dosya Ofseti, RVA ve VA
summary: Bir disassembly satırındaki adresin nereden geldiği: ELF'te bölüm başlığının Address/Off çifti ile LOAD segmentlerinin Offset/VirtAddr eşlemesi, dosya ofsetinden sanal adrese geçiş; nesne dosyasında adresin henüz bulunmaması ve yerini yer değiştirme kaydının tutması; PE'de ImageBase + RVA mantığı ve bölümün ham ofseti; aynı baytın üç farklı sayıyla anılabilmesi.
---

::: anlat Aynı bayt, üç ayrı sayı
`AS11`'de `objdump` çıktısındaki adresleri okudun. O adreslerin nereden geldiğini bilmek, bir ikili dosyayı incelerken şu üç sayıyı birbirine çevirebilmek demektir:

| Ad | Ne anlatır |
|---|---|
| **Dosya ofseti** | baytın diskteki dosyanın kaçıncı baytında olduğu |
| **RVA** (göreli sanal adres) | yüklendikten sonra modülün başından itibaren kaçıncı bayt |
| **VA** (sanal adres) | sürecin adres uzayındaki tam adres |

Üçü de aynı baytı gösterir ama farklı sayılardır. Hangi aracın hangisini bastığını bilmezsen, bir adresi yanlış yerde ararsın.

ELF'te eşlemeyi **program başlıkları** (LOAD segmentleri) yapar. Bu derste ölçüldü (Kali, gcc 16.2.0, `-no-pie`):

```text
  Type   Offset    VirtAddr            FileSiz   Flg
  LOAD   0x000000  0x0000000000400000  0x000488  R
  LOAD   0x001000  0x0000000000401000  0x00011d  R E
  LOAD   0x002000  0x0000000000402000  0x0000f8  R
```

Her satır "dosyanın şu ofsetinden başlayan şu kadar bayt, bellekte şu adrese yüklenecek" der. Bir dosya ofsetini sanal adrese çevirmek bu yüzden şöyle olur:

```text
VA = dosya_ofseti - segment.Offset + segment.VirtAddr
```

Bölüm başlıkları da aynı bilgiyi bölüm bazında verir; ölçülen `.text` için `Address 0x401020`, `Off 0x001020`. İkisi arasındaki fark bu dosyada sabit `0x400000`'dır — ama bu bir kural değil, bu dosyanın yerleşiminin sonucudur.
:::

::: anlat Adresin henüz olmadığı yer ve PE tarafı
Bir **nesne dosyasında** (`.o`) kod vardır ama adres yoktur: bağlayıcı yerleştirmeyi yapmamıştır. Çağrı yerleri boş bırakılır ve yanlarına birer **yer değiştirme** (relocation) kaydı konur. Ölçüldü:

```text
RELOCATION RECORDS FOR [.text]:
OFFSET            TYPE             VALUE
0000000000000019  R_X86_64_PLT32   kare-0x0000000000000004
```

Yani "`.text`'in `0x19` ofsetindeki alana, `kare` sembolünün adresini (eksi 4) yaz". Bu yüzden bir `.o` disassembly'sinde `call` hedefleri anlamsız görünür — `AS14`'te göreceğin `e8 fc ff ff ff` gibi. Hedef, bağlama anında doldurulur.

PE tarafında aynı iş **ImageBase + RVA** ile yapılır. Gerçek bir Windows `ntdll.dll` üzerinde ölçüldü:

```text
Idx Name     Size      VMA                File off
  0 .text    0016b03c  0000000180001000   00001000
```

Burada `VMA` 0x180001000, ham dosya ofseti 0x1000'dir; aradaki fark `0x180000000`, yani modülün **ImageBase**'idir. Demek ki `RVA = VA - ImageBase` ve bu bölümde RVA ile dosya ofseti aynı sayıya denk gelmiş.

> [!TUZAK] RVA ile dosya ofseti her zaman eşit değildir
> Yukarıdaki dosyada ikisi de `0x1000` çıktı; bu bir rastlantıdır, kural değil. Bölümler bellekte ve diskte farklı hizalamalarla yerleşir: bellekte genelde 0x1000, diskte 0x200 katlarına. Üstelik bir bölümün bellekteki boyutu dosyadakinden **büyük** olabilir (sıfırlanmış veri dosyada saklanmaz); o aralıktaki bir RVA'nın dosyada karşılığı yoktur. Dönüşümü her zaman bölüm başlıklarından hesapla, iki sayının bir kez tutmuş olmasına güvenme.

Bir de yer değiştirme/ASLR boyutu vardır: `-no-pie` ile derlenen bu ELF sabit `0x400000`'a yüklenir, ama PIE bir ikili ya da bir DLL çalışma anında başka bir tabana konabilir. O durumda disassembly'deki VA "ImageBase varsayımıyla" yazılmış bir sayıdır; süreçteki gerçek adres farklıdır ve aradaki fark bütün modüle aynı şekilde uygulanır.
:::

::: tahmin Fonksiyon dosyanın neresinde?
`-no-pie` ile derlenmiş ELF'te `kare` fonksiyonunun sanal adresi `0x401106`. Program başlıkları yukarıdaki ölçümdeki gibi. Bu fonksiyonun baytları dosyanın hangi ofsetinde?

```asm
; nm a  ->  0000000000401106 T kare
; objdump -d -M intel --disassemble=kare a
  401106:	0f af ff             	imul   edi,edi
  401109:	89 f8                	mov    eax,edi
  40110b:	c3                   	ret
```

```gercek
VA       = 0x401106
segment  : Offset 0x001000  VirtAddr 0x401000  (R E)
ofset    = 0x401106 - 0x401000 + 0x001000 = 0x1106
```

???

Dosya ofseti **`0x1106`**.

`kare`'nin VA'sı `0x401106`, ve bu adres ikinci LOAD segmentinin (`VirtAddr 0x401000`, `FileSiz 0x11d`) içine düşüyor: `0x401106 - 0x401000 = 0x106`, segmentin başından 262 bayt ileride. Aynı segment dosyada `0x001000` ofsetinden başladığına göre baytlar dosyanın `0x1000 + 0x106 = 0x1106` ofsetinde durur.

Dikkat: `0x401106 - 0x400000` de `0x1106` verir ve bu dosyada doğru sonuca götürür. Ama bu, birinci segmentin tabanının `0x400000` ve segmentlerin 0x1000 hizalı olmasının yan ürünüdür; başka bir yerleşimde tutmaz. Doğru yol her zaman adresin **düştüğü segmenti** bulup o segmentin `Offset`/`VirtAddr` çiftini kullanmaktır.

Üç satırlık fonksiyonun kendisi de okunur: `imul edi,edi` ile argümanın karesi alınır, `mov eax,edi` ile dönüş yazmacına konur, `ret`.
:::

::: gorev Dosya ofsetinden sanal adrese
`vaBul(ofset, segmentler)` yaz: bir dosya ofsetinin sanal adresini hesapla.

`segmentler`, LOAD girdilerinin listesidir; her girdi `(segOfset, vaddr, fileSiz)` demetidir. Bir ofset, `segOfset <= ofset < segOfset + fileSiz` koşulunu sağlayan segmente düşer ve karşılığı `ofset - segOfset + vaddr` olur.

Hiçbir segmente düşmüyorsa `None` döndür. Girdiler çakışmaz.

```starter
def vaBul(ofset, segmentler):
    segOfset, vaddr, fileSiz = segmentler[0]
    return ofset - segOfset + vaddr
```

```test
need("vaBul")
SEG = [(0x0000, 0x400000, 0x488), (0x1000, 0x401000, 0x11d), (0x2000, 0x402000, 0xf8)]
eq(vaBul(0x1106, SEG), 0x401106, "ölçülen kare fonksiyonu: ofset 0x1106 -> VA 0x401106")
eq(vaBul(0x0000, SEG), 0x400000, "ilk segmentin ilk baytı")
eq(vaBul(0x1000, SEG), 0x401000, "ikinci segmentin ilk baytı")
eq(vaBul(0x111c, SEG), 0x40111c, "ikinci segmentin son baytı (FileSiz 0x11d)")
eq(vaBul(0x111d, SEG), None, "segmentin hemen dışı: boşlukta kalır")
eq(vaBul(0x2050, SEG), 0x402050, "üçüncü segment")
eq(vaBul(0x9999, SEG), None, "hiçbir segmente düşmüyor")
eq(vaBul(0x488, SEG), None, "ilk segment 0x488 baytlık: son bayt 0x487")
eq(vaBul(0x1106, []), None, "segment listesi boş")
```

```solution
def vaBul(ofset, segmentler):
    for segOfset, vaddr, fileSiz in segmentler:
        if segOfset <= ofset < segOfset + fileSiz:
            return ofset - segOfset + vaddr
    return None
```

```hint
Başlangıç kodu her ofseti ilk segmentte sanıyor. Önce ofsetin **hangi** segmente düştüğünü bul: `segOfset <= ofset < segOfset + fileSiz`. Hiçbirine düşmüyorsa dosyadaki o bayt belleğe yüklenmiyordur.
```
:::

::: gorev PE: RVA'dan dosya ofsetine
`peOfset(rva, bolumler)` yaz: bir PE modülünde RVA'nın hangi dosya ofsetine karşılık geldiğini bul.

Her bölüm `(bolumRva, sanalBoyut, hamOfset, hamBoyut)` demetidir. RVA, `bolumRva <= rva < bolumRva + sanalBoyut` koşulunu sağlayan bölüme düşer. Bölüm içindeki uzaklık `rva - bolumRva`'dır.

- Uzaklık `hamBoyut`'tan küçükse dosya ofseti `hamOfset + uzaklık`'tır.
- Uzaklık `hamBoyut`'a eşit ya da büyükse o bayt dosyada **saklanmaz** (sıfırlanmış veri): `"dosyada yok"` döndür.
- Hiçbir bölüme düşmüyorsa `None`.

```starter
def peOfset(rva, bolumler):
    for bolumRva, sanalBoyut, hamOfset, hamBoyut in bolumler:
        if bolumRva <= rva < bolumRva + sanalBoyut:
            return hamOfset + (rva - bolumRva)
    return None
```

```test
need("peOfset")
# ölçülen ntdll .text: RVA 0x1000, ham ofset 0x1000, boyut 0x16b03c
B = [(0x1000, 0x16b03c, 0x1000, 0x16b03c), (0x16d000, 0x2b0, 0x16d000, 0x200)]
eq(peOfset(0x1618b0, B), 0x1618b0, "ölçülen ntdll stub'ı: bu bölümde RVA ile ham ofset çakışıyor")
eq(peOfset(0x1000, B), 0x1000, "bölümün ilk baytı")
eq(peOfset(0x16d000, B), 0x16d000, "ikinci bölümün başı")
eq(peOfset(0x16d1ff, B), 0x16d1ff, "ham boyutun son baytı")
eq(peOfset(0x16d200, B), "dosyada yok", "sanal boyut içinde ama ham boyutun dışında: sıfırlanmış veri")
eq(peOfset(0x16d2af, B), "dosyada yok", "sanal boyutun son baytı da dosyada değil")
eq(peOfset(0x16d2b0, B), None, "hiçbir bölüme düşmüyor")
eq(peOfset(0x500, B), None, "ilk bölümden önce: başlık alanı")
KAYIK = [(0x1000, 0x2000, 0x400, 0x2000)]
eq(peOfset(0x1500, KAYIK), 0x900, "RVA ile ham ofset farklıysa fark bölümden hesaplanır")
```

```solution
def peOfset(rva, bolumler):
    for bolumRva, sanalBoyut, hamOfset, hamBoyut in bolumler:
        if bolumRva <= rva < bolumRva + sanalBoyut:
            uzaklik = rva - bolumRva
            if uzaklik >= hamBoyut:
                return "dosyada yok"
            return hamOfset + uzaklik
    return None
```

```hint
Başlangıç kodu sanal boyutla ham boyutu aynı sanıyor. İki boyut ayrıdır: bölüme düşmek `sanalBoyut`'a, dosyada bulunmak `hamBoyut`'a bakar. Aradaki aralık bellekte sıfırlarla doldurulur ve dosyada hiç yer kaplamaz.
```

```hint
Son testteki gibi `bolumRva` ile `hamOfset` farklı olabilir; bu yüzden `rva - bolumRva` uzaklığını hesaplayıp `hamOfset`'e eklemelisin. İki sayının bir dosyada eşit çıkması kural değildir.
```
:::
