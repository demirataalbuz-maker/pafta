---
id: cm20
title: wevtutil · Aktar ve Yeniden Aç
summary: epl ile gerçek EVTX üretmek; üzerine yazma kararını açık tutmak; boş dışa aktarımı, bozuk kaynağı ve yeniden açma hatasını ayırt etmek.
timeout: 90
---

::: anlat XML dökmek ile EVTX aktarmak farklıdır
`qe ... > dosya.xml` okunabilir olay XML'i üretir. `epl` ise Windows'un tekrar açabildiği **ikili EVTX** üretir. XML dosyasının uzantısını evtx yapmak biçim dönüşümü değildir.

```cmd norun
wevtutil epl "olaylar.evtx" "secim.evtx" /lf:true /q:"*[System[EventID=102]]" /ow:false
wevtutil qe "secim.evtx" /lf:true /rd:false /f:xml /e:Events /uni:true >"kontrol.xml"
```

İlk komuttaki `/lf:true` **kaynağın dosya** olduğunu söyler; hedef zaten dosya yoludur. `/ow:false` var olan hedefin üstüne yazmaz, `/ow:true` açıkça izin verir. Başarılı çıkıştan sonra hedefi yeniden açıp olayların gerçekten beklenen seçim olduğunu doğrula. Olayların sayısı yanında RecordID/EventID/Level ve veri alanları da karşılaştırılabilir.

Bu dersin EVTX'i CM19'daki sentetik veriden gelir. Kaynak delil sabit tutulur; örnekler yalnız geçici klasöre yeni dosyalar yazar. `epl` kaynak günlükteki olayları silmez. Boş sorgu sonucu da başlığı olan, yeniden açılabilir bir EVTX oluşturabilir; sıfır baytlık dosya değildir.

Kaynak: [wevtutil epl](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wevtutil), [EvtExportLog: boş sonuç ve kopyalama](https://learn.microsoft.com/en-us/windows/win32/api/winevt/nf-winevt-evtexportlog).
:::

::: anlat Mesaj metni ile olay alanını ayır
EVTX olay verisini taşır; `/f:text` ile görüntülenen yerelleştirilmiş açıklama ayrıca sağlayıcının mesaj kaynaklarına ihtiyaç duyabilir. `wevtutil al` bu kaynakları da arşivlemeyi amaçlayan ayrı işlemdir; bu dersin sağlayıcısı sentetik olduğundan kaynak paketi yoktur. Dolayısıyla ders **XML alanlarını** doğrular, gerçek bir sağlayıcının açıklama paketini taşıdığını söylemez.

`/sq:true` yapılandırılmış sorgu dosyası kipidir. Bu Windows'ta `/lf:true` ile aynı anda verilmesi hata üretir; bu ders çevrimdışı dosyalar için açık `/lf:true /q:...` biçimini kullanır. Belgede geçen her seçenek kombinasyonunu destekleniyor varsayma; gerçek komutun kodunu ve çıktısını ölç.

Kaynak: [wevtutil seçenekleri ve archive-log](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wevtutil). Yerel doğrulama: `wevtutil epl /?` ve iki seçeneği birlikte kullanan hata tanığı.
:::

::: tahmin Boş EVTX de gerçek bir dosyadır
```setup
import runpy
runpy.run_path("evtx_fixtures.py")["prepare"]()
```
```cmd
@echo off
wevtutil epl "olaylar.evtx" "secim.evtx" /lf:true /q:"*[System[EventID=999]]" /ow:false >nul 2>nul
echo aktarim=%errorlevel%
wevtutil qe "secim.evtx" /lf:true /f:xml /e:Events /uni:true >"kontrol.xml" 2>nul
echo tekrar-okuma=%errorlevel%
wevtutil epl "olaylar.evtx" "secim.evtx" /lf:true /ow:false >nul 2>nul
if errorlevel 1 echo hedef-zaten-var
exit /b 0
```

???

```text
aktarim=0
tekrar-okuma=0
hedef-zaten-var
```

İlk seçimde olay yok, fakat dosya biçimi geçerlidir. İkinci komut boş dosyayı başarıyla açar. Üçüncü komut var olan hedefi değiştirmeye izin verilmediği için başarısız olur.
:::

::: gorev Seçimi aktar; eski hedefi koru
`olaylar.evtx` içinden EventID tam 102 olaylarının tamamını `secim.evtx` dosyasına aktar. Kaynağı değiştirme; hedef zaten varsa **üzerine yazma**.

Başarıda stdout `aktarildi` ve çıkış 0. Aktarım başarısızsa stdout boş, stderr `aktarim-hatasi` ve çıkış 1. Boş eşleşme başarılıdır; hedef gerçek, yeniden açılabilen EVTX olmalı. Komut kodunu kontrol etmeden başarı mesajı yazma.

```setup
import runpy
runpy.run_path("evtx_fixtures.py")["prepare"]()
```
```starter
@echo off
copy /y "olaylar.evtx" "secim.evtx" >nul
echo aktarildi
exit /b 0
```
```test
import runpy
from pathlib import Path
fx=runpy.run_path("evtx_fixtures.py")
source=Path("olaylar.evtx")
dest=Path("secim.evtx")
eq(out,"aktarildi\n","Başarı")
eq(fx["read_evtx"](dest),[(3,102,3,"uyari"),(4,102,2,"Türkçe & <demo> ! %"),(7,102,4,"bilgi"),(8,102,2,"son")],"Gerçek EVTX seçimi")
before=dest.read_bytes()
r=calis()
eq((r["kod"],r["cikti"],r["hata"]),(1,"","aktarim-hatasi\n"),"Var olan hedef reddedilir")
eq(dest.read_bytes(),before,"Eski hedef baytları aynı")
for rows in ((), ((101,1,"önce"),(102,2,"tam"),(103,1,"sonra")), ((102,1,"a"),), ((999,1,"yok"),)):
    dest.unlink(); source.unlink()
    fx["create_evtx"](source,rows)
    once=source.read_bytes()
    r=calis()
    eq((r["kod"],r["cikti"],r["hata"]),(0,"aktarildi\n",""),"Aktarım veya boş seçim")
    exp=[(i,eid,{1:2,2:3,4:4}[typ],text) for i,(eid,typ,text) in enumerate(rows,1) if eid==102]
    eq(fx["read_evtx"](dest),exp,"Çıktı gerçek araçla yeniden açılır")
    eq(dest.read_bytes()[:8],b"ElfFile\0","EVTX imzası")
    eq(source.read_bytes(),once,"Kaynak değişmedi")
dest.unlink(); source.write_bytes(b"bozuk")
r=calis()
eq((r["kod"],r["cikti"],r["hata"]),(1,"","aktarim-hatasi\n"),"Bozuk kaynak başarısız")
if dest.exists(): dest.unlink()
source.unlink()
r=calis()
eq((r["kod"],r["cikti"],r["hata"]),(1,"","aktarim-hatasi\n"),"Eksik kaynak başarısız")
```
```solution
@echo off
setlocal DisableDelayedExpansion
wevtutil epl "olaylar.evtx" "secim.evtx" /lf:true /q:"*[System[EventID=102]]" /ow:false >nul 2>nul || goto hata
echo aktarildi
exit /b 0
:hata
>&2 echo aktarim-hatasi
exit /b 1
```
```hint
COPY bütün kaydı taşır, XPath seçimi yapmaz. QE ise EVTX üretmez. EPL, /lf:true ve /ow:false seçeneklerini birlikte kullan.
```
:::

::: gorev Proje · EVTX ve doğrulama XML'i hazırla
Çalışma klasöründeki `olaylar.evtx` dosyasından **101–103 dahil EventID ve Level 2** olaylarını `paket.evtx` dosyasına aktar. Bu görevde iki çıktı geçici üretilmiş rapordur: mevcut `paket.evtx` ve `paket.xml` açıkça yenilenecek.

Aktarım başarılıysa **üretilen paket.evtx'i** yeniden `qe` ile açıp ileri sırada bütün olayları UTF-16LE `paket.xml` dosyasına, Events köküyle yaz. Kaynağı değiştirme. XML'i doğrudan kaynaktan sorgulamak yeniden açma doğrulaması sayılmaz.

Her iki aşama başarılıysa stdout `paket-hazir`, çıkış 0. Aktarım hatası: stderr `aktarim-hatasi`, çıkış 1. Yeniden okuma veya XML yönlendirme hatası: stderr `dogrulama-hatasi`, çıkış 2. Hatalarda stdout boş; başarısız çalışmanın çıktı dosyaları kullanılmamalı. Bu görev atomik dosya güncelleme garantisi vermez.

```setup
import runpy
runpy.run_path("evtx_fixtures.py")["prepare"]()
```
```starter
@echo off
wevtutil epl "olaylar.evtx" "paket.evtx" /lf:true /ow:true >nul 2>nul
echo paket-hazir
exit /b 0
```
```test
import runpy
from pathlib import Path
fx=runpy.run_path("evtx_fixtures.py")
source=Path("olaylar.evtx")
xml=Path("paket.xml")
dest=Path("paket.evtx")
def ikisini_oku():
    return (fx["read_evtx"](dest),fx["events_from_xml"](xml.read_bytes().decode("utf-16le")))
eq(out,"paket-hazir\n","İki aşamalı başarı")
expected=[(2,101,2,"alt-sinir"),(4,102,2,"Türkçe & <demo> ! %"),(5,103,2,"ust-sinir"),(8,102,2,"son")]
eq(ikisini_oku(),(expected,expected),"EVTX ve XML aynı seçilmiş kayıtları içerir")
for rows in (
    tuple((eid,typ,str(eid)+"/"+str(typ)) for eid in (100,101,102,103,104) for typ in (1,2,4)),
    ((103,1,"İlk & < >"), (101,1,"ikinci"), (102,4,"bilgi")),
    (), ((999,1,"yok"),)
):
    source.unlink(); fx["create_evtx"](source,rows)
    once=source.read_bytes()
    r=calis()
    eq((r["kod"],r["cikti"],r["hata"]),(0,"paket-hazir\n",""),"Eski raporun üzerine yeni rapor")
    exp=[(i,eid,{1:2,2:3,4:4}[typ],s) for i,(eid,typ,s) in enumerate(rows,1) if 101<=eid<=103 and typ==1]
    eq(ikisini_oku(),(exp,exp),"Boş dahil çıktı yeniden açılıp eşleştirilir")
    eq(source.read_bytes(),once,"Kaynak değişmedi")
# XML yönlendirmesi başarısız: aynı adda dizin. Native stderr sabit hata ile özetlenir.
xml.unlink(); xml.mkdir()
r=calis()
eq((r["kod"],r["cikti"],r["hata"]),(2,"","dogrulama-hatasi\n"),"İkinci aşama ayrı kod")
xml.rmdir()
source.write_bytes(b"bozuk")
r=calis()
eq((r["kod"],r["cikti"],r["hata"]),(1,"","aktarim-hatasi\n"),"İlk aşama ayrı kod")
source.unlink()
r=calis()
eq((r["kod"],r["cikti"],r["hata"]),(1,"","aktarim-hatasi\n"),"Eksik kaynak")
```
```solution
@echo off
setlocal DisableDelayedExpansion
wevtutil epl "olaylar.evtx" "paket.evtx" /lf:true /q:"*[System[(EventID >= 101 and EventID <= 103) and Level=2]]" /ow:true >nul 2>nul || goto aktarim_hata
(wevtutil qe "paket.evtx" /lf:true /rd:false /f:xml /e:Events /uni:true >"paket.xml") 2>nul || goto dogrulama_hata
echo paket-hazir
exit /b 0
:aktarim_hata
>&2 echo aktarim-hatasi
exit /b 1
:dogrulama_hata
>&2 echo dogrulama-hatasi
exit /b 2
```
```hint
İkinci komut paket.evtx'i açmalı. XML yönlendirmesi de başarısız olabilir; komut grubunun dışındaki `2>nul` bu tanıyı susturur, `||` başarısızlık dalını seçer. CMD yönlendirme hatasında önceki ERRORLEVEL değeri kalabildiğinden yalnız `if errorlevel` yeterli olmayabilir.
```
:::
