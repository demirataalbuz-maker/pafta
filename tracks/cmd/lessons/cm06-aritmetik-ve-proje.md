---
id: cm06
title: set /a ve Küçük Hesap Projesi
summary: Tamsayı aritmetiği, bölme/kalan, batch içinde yüzde işareti; int32 sarma, sekizlik sayı tuzağı ve blok bütçesi projesi.
---

::: anlat set /a bir hesap ifadesi değerlendirir
`set /a "pafta_toplam=7+5"` sonucu değişkene yazar. İfade içinde başka değişkenleri yüzde ile çevirmeden adlarıyla kullanabilirsin: `set /a "pafta_toplam=pafta_adet*pafta_boyut"`. İfadenin tamamını tırnaklamak kabuk için özel operatörleri tek bir argümanda tutmaya yardım eder. Atanmamış bir isim set /a içinde sıfır gibi davranabildiğinden yazım hatası her zaman açık hata vermez; eğitim adlarını baştan ata.

Bölme tamsayıdır: 7/3 sonucu 2; -7/3 sonucu -2 olur, sıfıra doğru kesilir. Kalan için `%` operatörü vardır; `.cmd` dosyasında yüzdeyi `%%` yazarsın: `set /a "pafta_kalan=7%%3"`. Bu, değişkeni yüzdeyle okuma kuralından farklıdır. Kalanı Python'un negatif mod işlemiyle aynı sanma; bu makinede -7'nin 3'e göre kalanı -1'dir.

Sabit sayıda önek tabanı değiştirebilir: 0x10 onaltılık 16, 010 sekizlik 8. Dolayısıyla 08 ondalık sekiz diye okunmaz; geçersiz sekizlik basamak hatası çıkarabilir. Dışarıdan gelen metni genel bir set /a ifadesine körlemesine verme. Bu görevler canonical ondalık tamsayı sözleşmesiyle sınırlıdır; kullanıcı ifadesi çalıştırma arayüzü yazmıyoruz.
:::

::: anlat Genişlik ve birim hesabını açık tut
Bu Windows cmd.exe aritmetiği işaretli 32 bit sonuçlarla çalışır. Sabit bir probda 2147483647+1, -2147483648'e sarar. Matematikte “arttırdım, büyüdü” diye düşündüğün bir bütçe hesabı, sınırın dışında negatif olabilir. Bu davranışı Python'un sınırsız tamsayısından bekleyemezsin; bu yol gerçek CMD üzerinde sınar.

İkinci görevde bu yüzden girdilerin aralığını küçük tutuyoruz: 0–1000 kayıt, kayıt başına 1–4096 bayt, 16 bayt başlık. Toplam en fazla 4096016 olur ve 32 bit sınırına yaklaşmaz. 512 baytlık blok sayısını yukarı yuvarlamak için `(toplam+511)/512` kullanılır. 511, 512 ve 513 bayt sınırlarını ayrı denemek bir blok eksik hesaplama hatasını yakalar.

Sıfıra bölme veya eksik parametre için kontrollü hata yolu kullan; her şeyi hesabın hata mesajına bırakma. Görevlerin normal girdisi ilk çalıştırmayı 0 koduyla bitirir; beklenen hata kodları calis ile ayrıca incelenir. Aritmetik sonuç, stdout ve süreç çıkış kodu üç farklı şeydir.

Kaynaklar (21 Ekim 2026): [set /a operatörleri ve sayı tabanları](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/set_1), [if sayısal karşılaştırmalar](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/if). Negatif bölme/kalan ve int32 sarma örnekleri bu makinedeki cmd.exe ile ayrıca doğrulandı.
:::

::: tahmin

Aşağıdaki gerçek batch betiğini cmd.exe çalıştıracak. Çıktıyı satır satır tahmin et; komutların kendisini değil, ekrana yazılan metni düşün.

```cmd
@echo off
set /a "pafta_bolum=7/3"
set /a "pafta_kalan=7%%3"
set /a "pafta_sekiz=010"
set /a "pafta_tasan=2147483647+1"
echo %pafta_bolum% %pafta_kalan% %pafta_sekiz% %pafta_tasan%
exit /b 0
```

???

Tek satır `2 1 8 -2147483648`. Bölüm tamsayıdır, kalan 1, 010 sekizlik 8, son toplam 32 bit sınırında sarar. Batch dosyasında aritmetik kalan operatörü için çift yüzde yazıldı.

:::

::: gorev Bölüm ve kalanı raporla

İki argüman canonical ondalık tamsayıdır; -100000..100000 aralığında ve başta gereksiz sıfır yoktur. Birinciyi ikinciye tamsayı böl; iki satır üret: `bolum=<değer>`, `kalan=<değer>`. Bölüm sıfıra doğru kesilir. Eksik/boş parametre veya sıfır bölen için yalnız `HATA: iki sayi ve sifir olmayan bolen gerekli` yazıp kod 2 dön. Diğer geçerli girdiler kod 0. Sözleşme dışı ifadeler verilmez.

```starter
@echo off
echo bolum=0
echo kalan=0
exit /b 0
```

```meta
argv: 7 3
```

```test
eq(out, 'bolum=2\nkalan=1\n', "7 / 3")
for a,b in [(0,1),(1,1),(-1,1),(7,3),(-7,3),(7,-3),(-7,-3),(9,3),(10,3),(11,3),(100000,99999)]:
    q = int(a/b)
    rem = a - q*b
    r = calis(argv=[str(a),str(b)])
    eq(r['kod'], 0, 'geçerli bölme')
    eq(r['cikti'], 'bolum='+str(q)+'\nkalan='+str(rem)+'\n', 'bölüm/kalan '+str((a,b)))
for args in ([],['7'],['','3'],['7',''],['0','0'],['7','0']):
    r = calis(argv=args)
    eq(r['kod'], 2, 'kontrollü giriş hatası')
    eq(r['cikti'], 'HATA: iki sayi ve sifir olmayan bolen gerekli\n', 'tek açık hata')
    eq(r['hata'], '', 'native bölme hatasına düşülmez')
```

```solution
@echo off
if "%~1"=="" goto hata
if "%~2"=="" goto hata
set "pafta_n=%~1"
set "pafta_d=%~2"
if %pafta_d% EQU 0 goto hata
set /a "pafta_bolum=pafta_n/pafta_d"
set /a "pafta_kalan=pafta_n%%pafta_d"
echo bolum=%pafta_bolum%
echo kalan=%pafta_kalan%
exit /b 0
:hata
echo HATA: iki sayi ve sifir olmayan bolen gerekli
exit /b 2
```

```hint
İkinci parametreyi hesaplamadan önce sıfır için denetle; kalan operatörü .cmd içinde %% olur.
```

:::

::: gorev Proje · 512 baytlık blok bütçesi

İlk argüman kayıt adedi 0–1000, ikinci argüman kayıt boyutu 1–4096 bayt olsun. Girdiler canonical ondalık tamsayı; başta gereksiz sıfır ve ifade yok. `toplam = 16 + adet * boyut`; blok sayısı toplam/512 değerinin yukarı yuvarlanmışı. İki satır yaz: `bayt=<toplam>`, `blok=<sayı>`. Eksik/boş veya aralık dışı girdide yalnız `HATA: aralik veya arguman` yazıp kod 2 dön. Normal kod 0. Sıfır kayıt hâlâ 16 bayt başlık taşır.

```starter
@echo off
echo bayt=0
echo blok=0
exit /b 0
```

```meta
argv: 1 496
```

```test
eq(out, 'bayt=512\nblok=1\n', "tam bir blok")
for count,size in [(0,1),(1,1),(1,495),(1,496),(1,497),(2,248),(3,171),(999,4096),(1000,4096)]:
    total = 16 + count*size
    r = calis(argv=[str(count),str(size)])
    eq(r['kod'], 0, 'geçerli bütçe')
    eq(r['cikti'], 'bayt='+str(total)+'\nblok='+str((total+511)//512)+'\n', 'blok sınırı '+str((count,size)))
for args in ([],['1'],['','1'],['1',''],['-1','1'],['1001','1'],['1','0'],['1','-1'],['1','4097']):
    r = calis(argv=args)
    eq(r['kod'], 2, 'eksik veya aralık dışı')
    eq(r['cikti'], 'HATA: aralik veya arguman\n', 'kontrollü hata')
```

```solution
@echo off
if "%~1"=="" goto hata
if "%~2"=="" goto hata
set "pafta_adet=%~1"
set "pafta_boyut=%~2"
if %pafta_adet% LSS 0 goto hata
if %pafta_adet% GTR 1000 goto hata
if %pafta_boyut% LSS 1 goto hata
if %pafta_boyut% GTR 4096 goto hata
set /a "pafta_toplam=16+pafta_adet*pafta_boyut"
set /a "pafta_blok=(pafta_toplam+511)/512"
echo bayt=%pafta_toplam%
echo blok=%pafta_blok%
exit /b 0
:hata
echo HATA: aralik veya arguman
exit /b 2
```

```hint
Önce dört aralık kapısını denetle. Yukarı yuvarlama için +511, sonra tamsayı /512; 512 tam sınırını unutma.
```

:::
