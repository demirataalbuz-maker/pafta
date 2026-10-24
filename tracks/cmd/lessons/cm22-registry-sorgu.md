---
id: cm22
title: reg query · Kayıt Defterinde Tam Değeri Bul
summary: Anahtar, değer adı, veri ve türü ayır; tam eşleşme ile alt dize aramasının farkını gerçek Registry üzerinde gör.
timeout: 90
---

::: anlat Anahtar, değer adı ve veri
`HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion` bir **anahtar yoludur**. `ProductName` ise bu anahtar altındaki **değer adıdır**; `REG_SZ` tür, yanındaki metin veridir. `reg.exe query "..." /v ProductName` yalnız seçilen değeri okur. Yol boşluk içerdiği için tırnak gerekir. Değerin içeriği ve Windows sürümü makineye göre değişebilir; `ProductName` metninden tek başına güncel sürümü veya güvenlik yamalarını çıkarsama.

```cmd norun
reg.exe query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v ProductName
reg.exe query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v CurrentBuildNumber
```

`/reg:32` ve `/reg:64` Registry yönlendirmesinin farklı görünümlerini seçer. Her anahtarda farklı veri olacağı garanti değildir. Bu ders yalnız var olan sistem anahtarını okur, kayıt defterini değiştirmez. Kaynak: [reg query](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg-query).
:::

::: anlat `/f`, `/e` ve `/c` sınırları
`/f` metin arar; `/e` yalnız **tam** eşleşmeyi, `/c` büyük-küçük harf duyarlılığını ister. `/f Product` alt dize araması `ProductName` adını bulabilir; `/f Product /e` bulmaz. Tam ve duyarlı arama yapmak, şüpheli bir adın benzer adlarla karışmasını önler. `reg query` eşleşme bulunmadığında başarısız kod da verebilir; dosya yok veya erişim reddiyle aynı iş mesajını vermeden önce aranan anahtarın okunabildiğini denetle. Kaynak: [reg query parametreleri ve dönüş kodları](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg-query).
:::

::: tahmin Tam eşleşme ile alt dize
```cmd
@echo off
reg.exe query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /f Product /e >nul 2>nul
if errorlevel 1 echo tam-yok
reg.exe query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /f ProductName /e >nul 2>nul
if not errorlevel 1 echo tam-var
exit /b 0
```

???

```text
tam-yok
tam-var
```

`Product`, `ProductName` değer adının alt dizisi olsa da tam adı değildir. `/e` kaldırılırsa ilk arama artık bu kaydı bulabilir. `if not errorlevel 1` burada başarılı (0) sonucu ayırır.
:::

::: gorev İstenen değer adını oku
İlk argüman değer adı; boş/yoksa `ProductName`. `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion` altındaki bu adı `reg.exe query ... /v` ile oku, çıktıyı `deger.txt` dosyasına yaz. Başarıda stdout `deger-hazir`, çıkış 0. Değer yoksa stdout boş, stderr `deger-hatasi`, çıkış 1. Başka anahtarları arama, değişiklik yapma.

```starter
@echo off
reg.exe query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" >"deger.txt"
echo deger-hazir
```
```test
from pathlib import Path
def verify(ad):
    r=calis(argv=[ad])
    eq((r['kod'],r['cikti'],r['hata']),(0,'deger-hazir\n',''),'Var olan değer')
    raw=Path('deger.txt').read_bytes()
    eq(ad.encode() in raw,True,'İstenen değer adı')
    eq(b'REG_SZ' in raw,True,'Gerçek Registry türü')
    eq(b'CurrentVersion' in raw,True,'Doğru anahtar')
    other=b'CurrentBuildNumber' if ad=='ProductName' else b'ProductName'
    eq(other in raw,False,'Yalnız istenen değer; /v olmadan bütün anahtar geçmez')
eq(out,'deger-hazir\n','Varsayılan')
verify('ProductName')
verify('CurrentBuildNumber')
r=calis(argv=['PaftaKesinlikleOlmayanDeger_2026'])
eq((r['kod'],r['cikti'],r['hata']),(1,'','deger-hatasi\n'),'Olmayan değer')
r=calis(argv=['ProductName'])
eq((r['kod'],r['cikti'],r['hata']),(0,'deger-hazir\n',''),'Hata sonrası dönüş')
```
```solution
@echo off
setlocal DisableDelayedExpansion
set "ad=%~1"
if not defined ad set "ad=ProductName"
(reg.exe query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v "%ad%" >"deger.txt") 2>nul || goto hata
echo deger-hazir
exit /b 0
:hata
>&2 echo deger-hatasi
exit /b 1
```
```hint
Anahtarı tırnakla; değer adını /v ile seç. Komutun kodunu kontrol etmeden başarı yazma.
```
:::

::: gorev Tam ve duyarlı ad araması
İlk argüman arama metni; boş/yoksa `ProductName`. İkinci argüman anahtar yolu; boş/yoksa `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion`. Anahtarın altında `reg.exe query ... /f ... /e /c` kullanarak **tam ve büyük-küçük harfe duyarlı** arama yap. Arama çıktısını `arama.txt` dosyasına yaz. Eşleşme varsa stdout `bulundu`, çıkış 0; eşleşme yoksa stdout `yok`, çıkış 0. Anahtar yoksa veya okunamıyorsa stdout boş, stderr `anahtar-hatasi`, çıkış 1. Üzerine yazma yap; eski rapora ekleme yapma. Arama yalnız seçilen anahtarda yapılır, `/s` kullanma.

```starter
@echo off
reg.exe query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /f ProductName >"arama.txt"
echo bulundu
```
```test
from pathlib import Path
eq(out,'bulundu\n','Varsayılan')
def probe(term,expected):
    r=calis(argv=[term])
    eq((r['kod'],r['cikti'],r['hata']),(0,expected+'\n',''),'Tam arama davranışı')
    raw=Path('arama.txt').read_bytes()
    eq(b'End of search:' in raw,True,'Gerçek REG çıktısı')
    if expected=='bulundu':
        eq(b'ProductName' in raw,True,'Seçilen kayıt')
    else:
        eq(b'ProductName    REG_SZ' in raw,False,'Yanlış pozitif yok')
probe('ProductName','bulundu')
probe('Product','yok')
probe('productname','yok')
probe('PaftaKesinlikleOlmayanDeger_2026','yok')
probe('ProductName','bulundu')
eq(Path('arama.txt').read_bytes().count(b'End of search:'),1,'Rapor eklenmedi')
r=calis(argv=['ProductName','HKCU\\Software\\PaftaKesinlikleOlmayanAnahtar_2026'])
eq((r['kod'],r['cikti'],r['hata']),(1,'','anahtar-hatasi\n'),'Olmayan anahtar eşleşmeme değildir')
```
```solution
@echo off
setlocal DisableDelayedExpansion
set "ad=%~1"
if not defined ad set "ad=ProductName"
set "kok=%~2"
if not defined kok set "kok=HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion"
reg.exe query "%kok%" >nul 2>nul || goto hata
(reg.exe query "%kok%" /f "%ad%" /e /c >"arama.txt") 2>nul && goto bulundu
echo yok
exit /b 0
:bulundu
echo bulundu
exit /b 0
:hata
>&2 echo anahtar-hatasi
exit /b 1
```
```hint
Önce anahtarın kendisini sorgula. Aramada /f ile metni ver; /e tamlık, /c harf duyarlılığıdır. Eşleşmeme ile anahtar hatasını ayır.
```
:::
