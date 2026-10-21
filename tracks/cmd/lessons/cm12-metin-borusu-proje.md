---
id: cm12
title: Proje · findstr, find ve sort ile Metin Raporu
summary: Literal ile sınırlı regexi ayır; eşleşme yok ile arama hatasını karıştırma, boruda durum kaybını gör.
---

::: anlat Üç aracın işi farklıdır
`find` bir metni içeren satırları bulur; `/c` eşleşen satır sayısını verir. `findstr` literal arama için `/l`, regex için `/r` sunar. Regex desteğini Python re veya PCRE sanma: sınıf, nokta, yıldız ve satır sınırları vardır; `+`, `?`, gruplama gibi alıştığın her yapı aynı biçimde desteklenmez. Bir veya daha çok sınıf öğesi için `[0-9][0-9]*` kalıbını okuyabilirsin.

```cmd
@echo off
>"cm12 ornek.log" echo host1 FAIL
findstr /l /c:"FAIL" "cm12 ornek.log"
find /c "FAIL" <"cm12 ornek.log"
exit /b 0
```

`/c:"iki kelime"` ifadeyi birlikte tutar. Gereken literal davranışı ayrıca `/l` ile açık yaz. Dosya metin kodlaması ve arama aracının Unicode sınırları gerçek veride ayrıca sınanmalıdır; burada UTF-8 fixture ve açık ASCII durum alanları kullanılır. Kaynaklar: [findstr](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/findstr), [find](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/find).

Dinamik arama metni ters bölüyle biterse `/c:"..."` komut satırı argümanının kapanış tırnağıyla etkileşebilir. İlk görev bu ek ayrıştırma katmanından kaçınmak için deseni geçici bir metin dosyasına yazar ve `/g:dosya` ile okur. `/g` dosyadaki her satırı ayrı arama deseni sayar; bizim sözleşmemiz tek satır ve literal `/l` kullanır.
:::

::: anlat Boru bir önceki adımın sonucunu gizleyebilir
`komut | sort` metni ikinci araca aktarır; borunun sonunda gözlediğin hata düzeyi ilk aracın eşleşme durumunu korumayabilir. İlk aracın çıkışını hemen kaydet, sonra sıralamayı yap. FINDSTR 0 ile eşleşme bildirir; 1 eşleşme olmadığında görülür, fakat bazı dosya açma hatalarında da stderr mesajıyla birlikte gelebilir. Bazı komut satırı veya çok uzun arama deseni hataları 2 döndürür. Bu nedenle her 1 kodunu hatasız boş arama sayma; stderr ve dosya bağlamını da incele. Bu ayrımlar gerçek motorla sınanır.

```cmd
@echo off
>"cm12 sirala.txt" (
  echo web02
  echo web01
)
type "cm12 sirala.txt" | sort /l C
exit /b 0
```

`sort /l C` bu ASCII örneklerini sabit karşılaştırma düzeniyle sıralar; sayısal büyüklük sıralaması yaptığını varsayma. Tekrarlı satırlar kendiliğinden silinmez. Projede yalnız geçici metin dosyaları oluşturulur ve native araçlar bunları okur; Python testleri sonucu denetler. Kaynak: [sort ve boru](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sort).
:::

::: tahmin
Betik gerçek cmd.exe üzerinde çalışacak. Çıktıyı satır satır tahmin et; her blokta değişkenin ne zaman açıldığını veya metnin nereye gittiğini izle.

```cmd
@echo off
>"cm12 tahmin.log" (
  echo web02 FAIL
  echo web01 OK
  echo web03 FAIL
  echo web02 FAIL
)
findstr /l /c:" FAIL" "cm12 tahmin.log" | sort /l C
find /c "FAIL" <"cm12 tahmin.log"
exit /b 0
```

???

`web02 FAIL`, `web02 FAIL`, `web03 FAIL`, `3` yazılır. Filtre OK satırını çıkarır, sort iki aynı satırı korur; find eşleşen satırları sayar, ayrı ayrı kelime tekrarlarını değil.
:::

::: gorev Literal filtre ve durum kodu

İlk argüman boş olmayan literal aranacak metin; standart girdi taranacak satırlardır. Eşleşen satırları `sort /l C` ile artan yaz; tekrarları koru. Eşleşme varsa çıkış 0, yoksa 1; findstr hata kodu üretirse o kodu koru. Argüman yoksa işlem yapmadan 0 ile çık. İlk findstr sonucunu sort çalışmadan kaydet; yalnız eşleşme varsa sıralamaya gerek vardır. Veride ve aranan metinde %, !, &, ^ ve sonunda da olmak üzere ters bölü bulunabilir; çift tırnak/CRLF argüman içinde yoktur. Deseni tek satır halinde geçici dosyaya yazıp `/l /g:dosya` kullan. Genel Unicode harf dönüşümü istenmez.

```starter
@echo off
exit /b 0
```

```test
cases = [("FAIL", "", "", 1),
         ("FAIL", "a OK\n", "", 1),
         ("FAIL", "b FAIL\n", "b FAIL\n", 0),
         ("FAIL", "c FAIL\na OK\nb FAIL\nb FAIL\n", "b FAIL\nb FAIL\nc FAIL\n", 0),
         (".", "a.b\naxb\n", "a.b\n", 0),
         ("A&B", "A&B\nA B\n", "A&B\n", 0),
         ("%", "x%y\nx\n", "x%y\n", 0),
         ("!", "tag!\ntag\n", "tag!\n", 0),
         ("^", "x^y\nx\n", "x^y\n", 0),
             ("\\", "a\\b\nplain\n", "a\\b\n", 0),
             ("son\\", "son\\yol\nson/yol\n", "son\\yol\n", 0),
             ("a\\b", "a\\b\naxb\n", "a\\b\n", 0),
         ("FAIL", "Ayşe FAIL\n", "Ayşe FAIL\n", 0)]
for needle,data,wanted,kod in cases:
    r = calis(stdin=data, argv=[needle])
    eq((r["kod"],r["cikti"],r["hata"]), (kod,wanted,""), "literal desen, 0/1/çok sonuç ve çıkış")
for uzunluk in (510, 511, 512):
    r = calis(stdin="kisa satir\n", argv=["X" * uzunluk])
    eq(r["kod"], 1 if uzunluk < 512 else 2, "native literal uzunluk sınırının komşuları")
    eq(r["cikti"], "", "uzun desende eşleşen normal çıktı yok")
    eq(bool(r["hata"]), uzunluk >= 512, "çok uzun desen hatası stderr'de korunmalı")
eq(run(), "", "argümansız ilk çalıştırma")
```

```solution
@echo off
setlocal DisableDelayedExpansion
if "%~1"=="" exit /b 0
set "aranan=%~1"
setlocal EnableDelayedExpansion
>"cm12_deseni.txt" echo(!aranan!
findstr /l /g:"cm12_deseni.txt" >"cm12_eslesen.txt"
set "rc=!errorlevel!"
if "!rc!"=="0" sort /l C "cm12_eslesen.txt"
exit /b !rc!
```

```hint
Deseni echo(!aranan! ile geçici dosyaya yazıp /l /g kullan. Findstr çıktısını başka bir geçici dosyada tut; hemen rc=!errorlevel! al. Yalnız rc sıfırsa sırala, ardından sakladığın rc ile exit /b yap.
```

:::

::: gorev Durum sütunundan rapor

İlk argüman giriş dosyası; yoksa olaylar.log kullan. Satırlar `id;durum;kalan` biçimindedir: id boş olmayan, noktalı virgül içermeyen metin; durum tam `FAIL` ise seç, harf duyarlı ol. Kalan boş veya başka noktalı virgüller içerebilir. Boş id, FAILX, gövdede geçen FAIL ve eksik ikinci ayraç seçilmemeli. Seçilen satırları sort /l C ile yaz, ardından `adet=N`. Tekrarlar kalsın; sıfır sonuçta yalnız adet=0 yaz. Çıkış 0; dosya yoksa stderr dosya_yok ve çıkış 2. Findstr stderr'e okuma hatası yazarsa bunu stderr'de koru, rapor üretmeden kendi çıkışını 2 yap. Rapor hattında type ile sort arasında boru kullanabilirsin; find ile seçilen satır sayısını al.

```starter
@echo off
exit /b 0
```

```setup
from pathlib import Path
Path("olaylar.log").write_text("id;durum;kullanici\nb;FAIL;ali\na;OK;can\nc;FAIL;ayse\n", encoding="utf-8", newline="")
```

```test
from pathlib import Path
cases = [[], ["b;FAIL;ali"], ["c;FAIL;ayse","a;OK;can","b;FAIL;ali","b;FAIL;ali"],
         [";FAIL;u","x;FAILX;u","x;OK;FAIL","x;FAIL","x;fail;u","id;durum;kullanici"],
         ["a;FAIL;","b;FAIL;A&B!%^","c;FAIL;bir;iki"]]
for i,rows in enumerate(cases):
    path = Path(f"cm12 olay {i}.log")
    path.write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8", newline="")
    secilen = []
    for row in rows:
        fields = row.split(";",2)
        if len(fields) == 3 and fields[0] and fields[1] == "FAIL":
            secilen.append(row)
    beklenen = "".join(x + "\n" for x in sorted(secilen)) + f"adet={len(secilen)}\n"
    r = calis(argv=[str(path)])
    eq((r["kod"],r["cikti"],r["hata"]), (0,beklenen,""), "durum alanı tam eşleşmeli, sıralama ve sayı")
eq(run(), "b;FAIL;ali\nc;FAIL;ayse\nadet=2\n", "varsayılan fixture")
r = calis(argv=["olmayan.log"])
eq((r["kod"],r["cikti"],r["hata"]), (2,"","dosya_yok\n"), "dosya yokluğu boş sonuç değildir")
import ctypes
Path("cm12_kilitli.log").write_text("x;FAIL;kayit\n", encoding="utf-8", newline="")
kernel = ctypes.WinDLL("kernel32", use_last_error=True)
kernel.CreateFileW.restype = ctypes.c_void_p
kernel.CreateFileW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
kernel.CloseHandle.argtypes = [ctypes.c_void_p]
# Yalnız bu testin oluşturduğu geçici dosyayı paylaşılmadan aç; finally ile bırak.
handle = kernel.CreateFileW(str(Path("cm12_kilitli.log").resolve()), 0x80000000, 0, None, 3, 0x80, None)
ok(handle not in (None, ctypes.c_void_p(-1).value), "yerel test dosyası için paylaşım kilidi oluşturuldu")
try:
    r = calis(argv=["cm12_kilitli.log"])
    eq(r["kod"], 2, "var olan fakat okunamayan giriş özel hata koduna dönüşmeli")
    eq(r["cikti"], "", "okuma hatası adet=0 raporu üretmemeli")
    ok(bool(r["hata"].strip()), "native okuma hata mesajı stderr'de korunmalı")
finally:
    if handle not in (None, ctypes.c_void_p(-1).value):
        kernel.CloseHandle(handle)
```

```solution
@echo off
setlocal DisableDelayedExpansion
set "dosya=%~1"
if not defined dosya set "dosya=olaylar.log"
if not exist "%dosya%" (
  >&2 echo dosya_yok
  exit /b 2
)
findstr /r /c:"^[^;][^;]*;FAIL;" "%dosya%" >"cm12_secilen.txt" 2>"cm12_hata.txt"
for %%E in ("cm12_hata.txt") do if %%~zE GTR 0 (
  type "cm12_hata.txt" >&2
  exit /b 2
)
type "cm12_secilen.txt" | sort /l C
find /c "FAIL" <"cm12_secilen.txt" >"cm12_adet.txt"
set "adet="
set /p "adet=" <"cm12_adet.txt"
echo adet=%adet%
exit /b 0
```

```hint
^[^;][^;]*;FAIL; başlangıçtaki boş olmayan id ve tam durum alanını sınırlar. find /c çıktısını ayrı dosyadan okuyabilirsin.
```

:::
