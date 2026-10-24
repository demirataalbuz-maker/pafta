---
id: cm19
title: wevtutil · EVTX Dosyasını Sorgula
summary: /lf:true ile dosyadan olay oku; XPath, okuma yönü ve adet sınırını uygula; boş eşleşmeyi bozuk dosyadan ayır ve Unicode XML'i koru.
timeout: 90
---

::: anlat Canlı kanal yerine delil dosyası
CM17'de `wevtutil` komutunu tanıdın. `qe Application` canlı kanal okur; `qe "olaylar.evtx" /lf:true` ise dosya okur. Dosya uzantısı tek başına bu seçimi yapmaz. Boşluklu yolu tırnakla.

Tezgah her çalıştırmada yalnız geçici klasöre **sentetik EVTX** üretir. Belgelenmiş eski EVT kayıtlarını yerel `wevtutil epl` gerçek EVTX'e dönüştürür. Kullanıcının günlükleri okunmaz, olay kanalı veya sağlayıcı kurulmaz. Sağlayıcı `PaftaDemo`, bilgisayar `PAFTA-LAB`; bunlar ders verileridir. Channel alanında geçici EVT yolu bulunur, gerçek bir Windows kanal kimliği değildir.

| RecordID | EventID | Level | Veri |
|---|---|---|---|
| 1 | 100 | 2 | alt-komsu |
| 2 | 101 | 2 | alt-sinir |
| 3 | 102 | 3 | uyari |
| 4 | 102 | 2 | Türkçe & <demo> ! % |
| 5 | 103 | 2 | ust-sinir |
| 6 | 104 | 2 | ust-komsu |
| 7 | 102 | 4 | bilgi |
| 8 | 102 | 2 | son |

EventID sağlayıcıya özgüdür; burada 102'nin evrensel bir güvenlik anlamı yoktur. Level 2 hata, 3 uyarı, 4 bilgi olayını temsil eder.

Kaynak: [wevtutil](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wevtutil), [olay System şeması](https://learn.microsoft.com/en-us/windows/win32/wes/eventschema-systempropertiestype-complextype).
:::

::: anlat XPath'i tırnakla; XML'i XML olarak sakla
```cmd norun
wevtutil qe "olaylar.evtx" /lf:true /q:"*[System[EventID=102]]" /rd:false /f:xml /e:Events /uni:true >"sorgu.xml"
```

`/q` Windows Event Log'un desteklediği XPath alt kümesidir. `and/or` ve parantezler anlamı değiştirir; sorguyu çift tırnak içinde tut ki `<`, `>` ve `&` CMD tarafından yönlendirme olarak ele alınmasın. `/rd:false` ileri, `/rd:true` ters okuma yönünü seçer. `/c:2` en fazla iki olay döndürür, iki olay bulunduğunu garanti etmez.

`/e:Events` XML'e tek kök ekler. Kök olmadan çok sayıda Event düğümü bir belge oluşturmayabilir. XML'deki etiketleri `findstr` ile saymak genel bir XML ayrıştırıcısı değildir; bu dersin testleri XML'i gerçek ayrıştırıcıyla açar.

`/uni:true` yönlendirilmiş çıktıyı **UTF-16LE** yazar; UTF-8 diye açma. Bu makinede `/uni:false` çıktısı, CMD'deki UTF-8 kod sayfasına rağmen Unicode'u kayıpsız taşımadı. Bu yüzden dosyada açık Unicode seçiyoruz; `type` ile dosyayı Pafta'nın UTF-8 çıktı kutusuna dökmek yerine yalnız başarı mesajını yazıyoruz. `/f:text` sağlayıcının mesaj kaynaklarına bağlı olabilir; sabit alanlar için `/f:xml` kullan.

Kaynak: [wevtutil seçenekleri](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wevtutil), [Windows olay sorgularında XPath sınırları](https://learn.microsoft.com/en-us/windows/win32/wes/consuming-events).
:::

::: tahmin Boş eşleşme ile okuma hatası
```setup
import runpy
runpy.run_path("evtx_fixtures.py")["prepare"]()
```
```cmd
@echo off
wevtutil qe "olaylar.evtx" /lf:true /q:"*[System[EventID=999]]" /f:xml /e:Events /uni:true >"bos-sonuc.xml" 2>nul
echo bos-kod=%errorlevel%
wevtutil qe "bozuk.evtx" /lf:true /f:xml >nul 2>nul
if errorlevel 1 echo bozuk-dosya
exit /b 0
```

???

```text
bos-kod=0
bozuk-dosya
```

Eşleşme yokken sorgu başarılıdır; Events kökü boş kalır. Bozuk EVTX okunamadığı için araç sıfırdan farklı kod döndürür. Hata metni Windows dili/sürümüne göre değişebilir; burada metni ezberlemiyoruz. `if errorlevel 1` “1'e eşit” değil, **en az 1** anlamına gelir.
:::

::: gorev İki ucu dahil aralık sorgusu
`olaylar.evtx` içinden **EventID 101–103 dahil ve Level tam 2** olan bütün olayları ileri sırayla seç. `sorgu.xml` dosyasına UTF-16LE, XML biçiminde ve `Events` köküyle yaz. Eski sonuç dosyasının üzerine yaz; kaynağı değiştirme.

Başarıda stdout yalnız `sorgu-hazir`, çıkış 0. Komut başarısızsa stdout boş, stderr `okuma-hatasi`, çıkış 1. Yerelleştirilmiş araç hata metnini bu sabit mesaja dönüştür. Hata durumunda sonuç dosyasının kullanılabileceğini varsayma.

```setup
import runpy
runpy.run_path("evtx_fixtures.py")["prepare"]()
```
```starter
@echo off
wevtutil qe "olaylar.evtx" /lf:true /q:"*[System[EventID=102]]" /f:xml >"sorgu.xml"
echo sorgu-hazir
exit /b 0
```
```test
import runpy
from pathlib import Path
fx = runpy.run_path("evtx_fixtures.py")
source = Path("olaylar.evtx")
def sonuc():
    return fx["events_from_xml"](Path("sorgu.xml").read_bytes().decode("utf-16le"))
eq(out, "sorgu-hazir\n", "Başarı çıktısı")
eq(sonuc(), [(2,101,2,"alt-sinir"),(4,102,2,"Türkçe & <demo> ! %"),(5,103,2,"ust-sinir"),(8,102,2,"son")], "Uçlar, Level ve sıralama")
for rows in (
    tuple((eid, typ, f"{eid}/{typ}") for eid in (100,101,102,103,104) for typ in (1,2,4)),
    ((103,1,"önce"), (101,1,"sonra"), (102,1,"")),
    (), ((999,1,"yok"),)
):
    source.unlink()
    fx["create_evtx"](source, rows)
    once = source.read_bytes()
    r = calis()
    eq((r["kod"],r["cikti"],r["hata"]), (0,"sorgu-hazir\n",""), "Başarı/boş sonuç")
    exp = [(i,eid,{1:2,2:3,4:4}[typ],text) for i,(eid,typ,text) in enumerate(rows,1) if 101 <= eid <= 103 and typ == 1]
    eq(sonuc(),exp,"Bağımsız kayıt matrisi; sıralama dosyadan gelir")
    eq(source.read_bytes(),once,"Kaynak değişmedi")
source.write_bytes(b"bozuk")
r=calis()
eq((r["kod"],r["cikti"],r["hata"]),(1,"","okuma-hatasi\n"),"Bozuk dosya")
source.unlink()
r=calis()
eq((r["kod"],r["cikti"],r["hata"]),(1,"","okuma-hatasi\n"),"Eksik dosya")
```
```solution
@echo off
setlocal DisableDelayedExpansion
(wevtutil qe "olaylar.evtx" /lf:true /q:"*[System[(EventID >= 101 and EventID <= 103) and Level=2]]" /rd:false /f:xml /e:Events /uni:true >"sorgu.xml") 2>nul || goto hata
echo sorgu-hazir
exit /b 0
:hata
>&2 echo okuma-hatasi
exit /b 1
```
```hint
İki eşik aynı System koşulunda and ile birleşir. Level koşulu ayrıca gereklidir. Yönlendirme başarısızlığını da yakalamak için komut grubunun `||` hata dalını kullan.
```
:::

::: gorev En yeni N eşleşmeyi al
İlk argüman kaynak dosya, yok/boşsa `olaylar.evtx`. İkinci argüman N, yok/boşsa `2`; yalnız tam `1`, `2`, `3` metinlerini kabul et. Fazladan argüman veya geçersiz N: stderr `kullanim`, çıkış 2, stdout boş; eski `son.xml` korunmalı.

Geçerli argümanlarla EventID tam 102 olaylarını **ters sırada, en fazla N tane** al. UTF-16LE `son.xml`, kök Events. Başarıda stdout `son-hazir`, çıkış 0; dosya okuma hatasında stderr `okuma-hatasi`, çıkış 1, stdout boş. Boş eşleşme başarıdır. Kaynakta boşluk, Unicode, `& ! ^` bulunabilir; çift tırnak/CR/LF yoktur. Kaynağı değiştirme. Dosya adı `%` içermez: bu Windows’ta wevtutil `%DEGISKEN%` biçimini kendisi genişletebilir; CMD tırnakları bunu engellemez.

```setup
import runpy
runpy.run_path("evtx_fixtures.py")["prepare"]()
```
```starter
@echo off
wevtutil qe "olaylar.evtx" /lf:true /c:2 /f:xml /uni:true >"son.xml"
echo son-hazir
exit /b 0
```
```test
import runpy
from pathlib import Path
fx=runpy.run_path("evtx_fixtures.py")
def sonuc():
    return fx["events_from_xml"](Path("son.xml").read_bytes().decode("utf-16le"))
eq(out,"son-hazir\n","Varsayılan")
eq([x[0] for x in sonuc()],[8,7],"En yeni iki eşleşme")
source=Path("olaylar.evtx")
once=source.read_bytes()
for n in (1,2,3):
    r=calis(argv=["olaylar.evtx",str(n)])
    eq((r["kod"],r["cikti"],r["hata"]),(0,"son-hazir\n",""),"Geçerli N")
    eq([x[0] for x in sonuc()],[8,7,4][:n],"1/2/3 tam sınır ve ters sıra")
eq(source.read_bytes(),once,"Kaynak korunur")
for name in ("iki öğe.evtx","A&B.evtx","x!y.evtx","sona^.evtx"):
    Path(name).write_bytes(once)
    eq(run(argv=[name,"1"]),"son-hazir\n","Dosya adı veri olarak kalır")
    eq([x[0] for x in sonuc()],[8],"Dosya gerçekten sorgulandı")
for rows in ((), ((102,1,"tek"),), ((101,1,"eşleşmez"),)):
    source.unlink(); fx["create_evtx"](source,rows)
    eq(run(argv=["","3"]),"son-hazir\n","Sınırdan az/boş")
    eq(len(sonuc()),sum(eid==102 for eid,_,_ in rows),"Az kayıt tamamlanmaz")
for args in (["olaylar.evtx","0"],["olaylar.evtx","4"],["olaylar.evtx","01"],["olaylar.evtx","1+1"],["olaylar.evtx","abc"],["olaylar.evtx","2",""],["olaylar.evtx","2","fazla"]):
    before=Path("son.xml").read_bytes()
    r=calis(argv=args)
    eq((r["kod"],r["cikti"],r["hata"]),(2,"","kullanim\n"),"Geçersiz kullanım")
    eq(Path("son.xml").read_bytes(),before,"Kullanım hatası yazmadan reddedilir")
eq(run(argv=["",""]),"son-hazir\n","Boş argüman varsayılanları")
for name in ("bozuk.evtx","olmayan.evtx"):
    r=calis(argv=[name])
    eq((r["kod"],r["cikti"],r["hata"]),(1,"","okuma-hatasi\n"),"Okuma hatası")
```
```solution
@echo off
setlocal DisableDelayedExpansion
set "kaynak=%~1"
if not defined kaynak set "kaynak=olaylar.evtx"
set "n=%~2"
if not defined n set "n=2"
if not [%3]==[] goto kullanim
if "%n%"=="1" goto oku
if "%n%"=="2" goto oku
if "%n%"=="3" goto oku
goto kullanim
:oku
(wevtutil qe "%kaynak%" /lf:true /q:"*[System[EventID=102]]" /rd:true /c:%n% /f:xml /e:Events /uni:true >"son.xml") 2>nul || goto hata
echo son-hazir
exit /b 0
:kullanim
>&2 echo kullanim
exit /b 2
:hata
>&2 echo okuma-hatasi
exit /b 1
```
```hint
N'yi doğrudan aritmetik ifadeye çevirmek yerine izin verilen üç metinle karşılaştır. Kaynak yolunu delayed expansion kapalıyken yakala, tırnak içinde kullan ve CALL ile yeniden genişletme.
```
:::
