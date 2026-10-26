---
id: ps23
title: Invoke-RestMethod · Oturumlu API İstekleri
summary: Invoke-RestMethod ile JSON, WebSession, durum/hata gövdesi; Windows PowerShell 5.1 temelleri ve gerçek PowerShell 7'de yönlendirme sınırı, multipart FileInfo yüklemesi, başlık/gövde süre iptali ayrımı.
---

::: anlat İki komut, iki ayrı iş
Windows PowerShell 5.1'de HTTP için iki yerleşik komut var ve aynı isteği farklı biçimde verirler:

| | `Invoke-RestMethod` | `Invoke-WebRequest` |
|---|---|---|
| Ne döndürür | Gövdeyi **çözülmüş** olarak: JSON ise nesne, XML ise `[xml]` | Yanıt nesnesi: `StatusCode`, `Headers`, `Content`, `Links` |
| Ne zaman | Bir API'den veri almak | Durum kodu, başlık ya da ham içerik lazımsa |
| Yanıt başlıkları | 5.1'de **okunamaz** | `$y.Headers["Location"]` |

```powershell
$adres = (Get-Content "api_adres.txt" -Raw).Trim()      #! tezgahın adresi (hazırlık bloğu yazar)

$sayfa = Invoke-WebRequest "$adres/sayfa/biletler" -UseBasicParsing
$sayfa.StatusCode                                        #! 200
$sayfa.Headers["Content-Type"]                           #! text/html; charset=utf-8
@($sayfa.Links).Count                                    #! sayfadaki <a> etiketleri
```

> [!TUZAK] `-UseBasicParsing` olmadan Invoke-WebRequest takılabilir
> Windows PowerShell 5.1'de `Invoke-WebRequest` HTML'yi varsayılan olarak Internet Explorer motoruyla ayrıştırmaya çalışır. IE'nin ilk açılış ayarı yapılmamış bir sunucuda ya da Server Core'da komut hata verir veya bekler. `-UseBasicParsing` bu motoru kullanmaz; `Links` yine dolar, ama `ParsedHtml` yoktur. PowerShell 7'de bu parametre artık etkisizdir, her zaman temel ayrıştırma kullanılır.

`Invoke-RestMethod` JSON'u PowerShell nesnesine çevirir; alanlara nokta ile erişirsin, bir dizinin bütün elemanlarının aynı alanını tek seferde alabilirsin:

```powershell norun
$liste = Invoke-RestMethod "$adres/api/biletler?sayfa=1" -WebSession $oturum
$liste.toplam                 # 7
$liste.kayitlar.id            # 101 102 103  (üye sayımı: dizinin her elemanından)
$null -eq $liste.sonraki      # JSON null → $null
```
```setup
import os, runpy, sys, pathlib
_s = os.path.dirname(next(m.__file__ for m in list(sys.modules.values())
                          if getattr(m, "__file__", None) and os.path.basename(m.__file__) == "py_harness.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
pathlib.Path("api_adres.txt").write_text(sys.modules["api"].SUNUCU, encoding="utf-8")
```
:::

::: anlat Oturum: -SessionVariable ve -WebSession
Bir API'ye önce giriş yapıp sonra o oturumla istek atarken çerezi elle taşımazsın. İlk istekte `-SessionVariable oturum` yazarsın (başında `$` **yok**); PowerShell `$oturum` adında bir `WebRequestSession` nesnesi kurar ve gelen çerezleri ona koyar. Sonraki isteklerde `-WebSession $oturum` verirsin:

```powershell
$adres = (Get-Content "api_adres.txt" -Raw).Trim()

$govde = @{ kullanici = "analist"; parola = "pafta123" } | ConvertTo-Json
$giris = Invoke-RestMethod "$adres/giris" -Method Post -SessionVariable oturum `
    -ContentType "application/json; charset=utf-8" -Body $govde
$giris.durum                                             #! açık

$oturum.Cookies.Count                                    #! 1: sunucunun gönderdiği çerez
$liste = Invoke-RestMethod "$adres/api/biletler" -WebSession $oturum
$liste.kayitlar.Count                                    #! 3: çerez kendiliğinden gitti
```

| Parametre | Ne yapar |
|---|---|
| `-Method Post` | Varsayılan `Get`'tir |
| `-Body` | Gövde: metin ya da hashtable (hashtable form kodlanır, JSON değil) |
| `-ContentType` | Gövdenin türünü söyler; JSON için **kendin** yazmalısın |
| `-SessionVariable ad` | Yeni oturum kurar, `$ad` değişkenine koyar |
| `-WebSession $ad` | Var olan oturumu kullanır |
| `-TimeoutSec 5` | Yanıt gelmezse vazgeçer |

> [!TUZAK] Hashtable'ı `-Body`'ye doğrudan verirsen JSON gitmez
> `-Body @{ kullanici = "analist" }` gövdeyi `kullanici=analist` biçiminde **form** olarak gönderir. JSON bekleyen bir API bunu anlamaz. Önce `ConvertTo-Json` ile metne çevir ve `-ContentType "application/json; charset=utf-8"` yaz; `charset` olmadan 5.1 Türkçe karakterleri bozabilir.
```setup
import os, runpy, sys, pathlib
_s = os.path.dirname(next(m.__file__ for m in list(sys.modules.values())
                          if getattr(m, "__file__", None) and os.path.basename(m.__file__) == "py_harness.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
pathlib.Path("api_adres.txt").write_text(sys.modules["api"].SUNUCU, encoding="utf-8")
```
:::

::: anlat 4xx ve 5xx: sonlandıran hata
Python'daki `requests`'in tersine, Windows PowerShell 5.1'de iki komut da 2xx dışındaki her yanıtta **sonlandıran bir hata** fırlatır. Durum kodunu ve sunucunun yazdığı gövdeyi `catch` bloğunda okursun:

```powershell
$adres = (Get-Content "api_adres.txt" -Raw).Trim()
try {
    Invoke-RestMethod "$adres/durum/503" -ErrorAction Stop | Out-Null
} catch {
    [int]$_.Exception.Response.StatusCode                #! 503
    $_.ErrorDetails.Message                              #! sunucunun gövdesi, metin olarak
    ($_.ErrorDetails.Message | ConvertFrom-Json).hata    #! istek
}
```

> [!TUZAK] Hata gövdesini yanıt akışından okumaya çalışma
> İnternetteki eski örnekler `$_.Exception.Response.GetResponseStream()` ile gövdeyi okumayı önerir. Bu tezgahta denendi: `Invoke-RestMethod` akışı hata fırlatmadan önce tükettiği için okuyucu **boş metin** döndürür. Gövde `$_.ErrorDetails.Message` içindedir. PowerShell 7'de ise `-SkipHttpErrorCheck` ile hata hiç fırlatılmaz, `-StatusCodeVariable` durum kodunu verir; bu iki parametre 5.1'de yoktur.

> [!GÜVENLİK]
> Parolayı betiğin içine düz metin yazma; burada tezgahın sabit, zararsız eğitim kullanıcısı kullanılıyor. Gerçek işte `Get-Credential` ya da bir gizli kasası kullan. Sertifika denetimini kapatan `[Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }` satırı bütün oturum için TLS'i etkisiz bırakır; hata ayıklarken bile kalıcı bir çözüm değildir. Tezgahın API'si `127.0.0.1`'de çalışır ve internete çıkmaz.
```setup
import os, runpy, sys, pathlib
_s = os.path.dirname(next(m.__file__ for m in list(sys.modules.values())
                          if getattr(m, "__file__", None) and os.path.basename(m.__file__) == "py_harness.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
pathlib.Path("api_adres.txt").write_text(sys.modules["api"].SUNUCU, encoding="utf-8")
```
:::

::: tahmin
Ne yazar?

```powershell
$adres = (Get-Content "api_adres.txt" -Raw).Trim()

$giris = Invoke-RestMethod "$adres/giris" -Method Post -SessionVariable o `
    -ContentType "application/json; charset=utf-8" `
    -Body (@{ kullanici = "analist"; parola = "pafta123" } | ConvertTo-Json)
"{0} {1}" -f $giris.durum, $giris.kullanici

$liste = Invoke-RestMethod "$adres/api/biletler?sayfa=3" -WebSession $o
"{0} {1} {2}" -f $liste.sayfa, $liste.kayitlar.Count, ($null -eq $liste.sonraki)

$y = Invoke-WebRequest "$adres/sayfa/biletler" -WebSession $o -UseBasicParsing
"{0} {1}" -f $y.StatusCode, $y.Headers["Date"]
```

???

`açık analist`, `3 1 True` ve `200 Mon, 19 Oct 2026 09:00:00 GMT`.

Giriş yanıtı JSON'dur, `Invoke-RestMethod` onu nesneye çevirir ve `durum` ile `kullanici` alanları doğrudan okunur. Yedi kaydın sayfa boyu üç olduğundan üçüncü sayfada **bir** kayıt vardır; tek elemanlı dizide de `.Count` 1 verir. Son sayfanın `sonraki` alanı JSON `null`'dır ve PowerShell'de `$null` olur. Son satırda `Invoke-WebRequest` yanıt nesnesini verir: durum kodu ve tezgahın sabit `Date` başlığı oradan okunur — aynı başlık `Invoke-RestMethod` ile 5.1'de görülemezdi.
```setup
import os, runpy, sys, pathlib
_s = os.path.dirname(next(m.__file__ for m in list(sys.modules.values())
                          if getattr(m, "__file__", None) and os.path.basename(m.__file__) == "py_harness.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
pathlib.Path("api_adres.txt").write_text(sys.modules["api"].SUNUCU, encoding="utf-8")
```
:::

::: gorev Sayfaları sonuna kadar gez
`$Girdi`'nin ilk satırında bir başlangıç sayfa numarası var. Giriş yap, o sayfadan başlayarak **son sayfaya kadar** bütün kayıtları topla ve her satıra bir bilet numarası yazdır. Son sayfayı sunucunun `sonraki` alanından anla: son sayfada `$null` olur.

Satır tam sayı değilse ya da sunucu sayfayı reddederse (`400`) tek satır `HATA` yazdır.

```stdin
1
```

```setup
import os, runpy, sys, pathlib
_s = os.path.dirname(next(m.__file__ for m in list(sys.modules.values())
                          if getattr(m, "__file__", None) and os.path.basename(m.__file__) == "py_harness.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
pathlib.Path("api_adres.txt").write_text(sys.modules["api"].SUNUCU, encoding="utf-8")
```

```starter
$adres = (Get-Content "api_adres.txt" -Raw).Trim()
$null = Invoke-RestMethod "$adres/giris" -Method Post -SessionVariable oturum `
    -ContentType "application/json; charset=utf-8" `
    -Body (@{ kullanici = "analist"; parola = "pafta123" } | ConvertTo-Json)

# $Girdi[0] sayfasından başla, sonraki $null olana kadar ilerle
```

```test
eq(out, "101\n102\n103\n104\n105\n106\n107\n", "yedi kaydın hepsi, sırayla")
eq(run(stdin="3\n"), "107\n", "son sayfada tek kayıt ve sonraki $null")
eq(run(stdin="2\n"), "104\n105\n106\n107\n", "ortadan başlayınca kalan iki sayfa")
eq(run(stdin="4\n"), "", "aralık dışı sayfa boş döner, hata değildir")
eq(run(stdin="0\n"), "HATA\n", "sunucu 0 için 400 verir; sonlandıran hata yakalanmalı")
eq(run(stdin="iki\n"), "HATA\n", "tam sayıya çevrilemeyen girdi HATA")
bos = calis(stdin="")
eq(bos["cikti"], "HATA\n", "hiç girdi yoksa HATA")
eq(bos["hata"].strip(), "", "boş girdide hata akışına bir şey düşmemeli: $Girdi[0] $null olabilir")
ok("sonraki" in src.lower(), "son sayfayı sunucunun sonraki alanından anla")
```

```solution
$adres = (Get-Content "api_adres.txt" -Raw).Trim()
$sayi = 0
if ($Girdi.Count -lt 1 -or -not [int]::TryParse($Girdi[0].Trim(), [ref]$sayi)) { "HATA"; exit 0 }

$null = Invoke-RestMethod "$adres/giris" -Method Post -SessionVariable oturum `
    -ContentType "application/json; charset=utf-8" `
    -Body (@{ kullanici = "analist"; parola = "pafta123" } | ConvertTo-Json)

$sayfa = $sayi
while ($null -ne $sayfa) {
    try {
        $veri = Invoke-RestMethod "$adres/api/biletler?sayfa=$sayfa" -WebSession $oturum -ErrorAction Stop
    } catch {
        "HATA"
        exit 0
    }
    foreach ($kayit in $veri.kayitlar) { $kayit.id }
    $sayfa = $veri.sonraki
}
```

```hint
`[int]::TryParse($metin, [ref]$sayi)` çevirebilirse `$true` döndürür ve sonucu `$sayi`'ya yazar; istisna fırlatmaz.
```

```hint
`400` yanıtı Python'daki gibi bir durum kodu değil, **sonlandıran hatadır**: isteği `try { ... -ErrorAction Stop } catch { "HATA"; exit 0 }` içine al.
```
:::

::: gorev Bilet oluştur ve hatayı oku
`$Girdi`'nin ilk satırı başlık, ikinci satırı önceliktir. Giriş yaptıktan sonra `POST /api/bilet` ile kaydı oluştur.

- Sunucu `201` döndürürse `OLUSTU|<id>|<Location başlığı>` yazdır. `Location` bir yanıt **başlığıdır**: 5.1'de onu ancak `Invoke-WebRequest` verir.
- Sunucu reddederse `<kod>|<yanıttaki hata alanı>` yazdır: boş alan `400|alan`, listede olmayan öncelik `400|oncelik`, aynı başlıkla ikinci kayıt `409|yinelenen`.
- `$Girdi` iki satırdan azsa tek satır `HATA` yazdır.

```stdin
yeni kayit
yüksek
```

```setup
import os, runpy, sys, pathlib
_s = os.path.dirname(next(m.__file__ for m in list(sys.modules.values())
                          if getattr(m, "__file__", None) and os.path.basename(m.__file__) == "py_harness.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
pathlib.Path("api_adres.txt").write_text(sys.modules["api"].SUNUCU, encoding="utf-8")
```

```starter
$adres = (Get-Content "api_adres.txt" -Raw).Trim()
$null = Invoke-RestMethod "$adres/giris" -Method Post -SessionVariable oturum `
    -ContentType "application/json; charset=utf-8" `
    -Body (@{ kullanici = "analist"; parola = "pafta123" } | ConvertTo-Json)

# POST /api/bilet · 201 ise OLUSTU, reddedilirse kod ve hata alanı
```

```test
eq(out, "OLUSTU|108|/api/bilet/108\n", "yeni kayıt 108 numarasını alır, Location başlıktan okunur")
eq(run(stdin="\nyüksek\n"), "400|alan\n", "boş başlık reddedilir")
eq(run(stdin="deneme\n\n"), "400|alan\n", "boş öncelik reddedilir")
eq(run(stdin="yeni kayit\norta\n"), "409|yinelenen\n", "aynı başlıkla ikinci kayıt 409 verir, 400 değil")
eq(run(stdin="deneme\nYüksek\n"), "400|oncelik\n", "öncelik büyük-küçük harfe duyarlıdır")
eq(run(stdin="deneme\nacil\n"), "400|oncelik\n", "listede olmayan öncelik reddedilir")
dusuk = run(stdin="deneme\ndüşük\n").strip()          # aynı sunucuya ikinci kayıt: numara artar
p = dusuk.split("|")
ok(len(p) == 3 and p[0] == "OLUSTU" and p[1].isdigit() and int(p[1]) > 108,
   "sınırdaki geçerli öncelik düşük de kabul edilir ve yeni numara alır")
ok(len(p) == 3 and p[2] == "/api/bilet/" + p[1], "Location oluşan kaydın numarasını taşır")
eq(run(stdin="yalniz baslik\n"), "HATA\n", "tek satırlık girdi HATA")
```

```solution
$adres = (Get-Content "api_adres.txt" -Raw).Trim()
if ($Girdi.Count -lt 2) { "HATA"; exit 0 }

$null = Invoke-RestMethod "$adres/giris" -Method Post -SessionVariable oturum `
    -ContentType "application/json; charset=utf-8" `
    -Body (@{ kullanici = "analist"; parola = "pafta123" } | ConvertTo-Json)

$govde = @{ baslik = $Girdi[0]; oncelik = $Girdi[1] } | ConvertTo-Json
try {
    $y = Invoke-WebRequest "$adres/api/bilet" -Method Post -WebSession $oturum -UseBasicParsing `
        -ContentType "application/json; charset=utf-8" -Body $govde -ErrorAction Stop
    if ($y.StatusCode -eq 201) {
        $kayit = $y.Content | ConvertFrom-Json
        "OLUSTU|{0}|{1}" -f $kayit.id, $y.Headers["Location"]
    }
} catch {
    $kod = [int]$_.Exception.Response.StatusCode
    $hata = ($_.ErrorDetails.Message | ConvertFrom-Json).hata
    "{0}|{1}" -f $kod, $hata
}
```

```hint
Başarılı yanıtta gövde `$y.Content` içinde **metindir**; `ConvertFrom-Json` ile nesneye çevir. Başlık: `$y.Headers["Location"]`.
```

```hint
Reddedilen istek `catch`'e düşer: durum kodu `[int]$_.Exception.Response.StatusCode`, sunucunun gövdesi `$_.ErrorDetails.Message`.
```
:::

::: gorev Durum kodu eşikleri
Tezgahın `/durum/<kod>` ucu istenen HTTP hata kodunu döndürür, ama yalnızca 400 ile 599 arasını kabul eder; aralık dışındaki kod için `400` ve `{"hata": "kod"}` verir.

`$Girdi`'nin ilk satırı bir sayıdır. `/durum/<sayı>` adresine istek at ve `<gelen durum kodu>|<hata alanı>` yazdır. Satır tam sayı değilse ya da hiç girdi yoksa isteği atmadan tek satır `HATA` yazdır.

```stdin
503
```

```setup
import os, runpy, sys, pathlib
_s = os.path.dirname(next(m.__file__ for m in list(sys.modules.values())
                          if getattr(m, "__file__", None) and os.path.basename(m.__file__) == "py_harness.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
pathlib.Path("api_adres.txt").write_text(sys.modules["api"].SUNUCU, encoding="utf-8")
```

```starter
$adres = (Get-Content "api_adres.txt" -Raw).Trim()
$kod = $Girdi[0]

Invoke-RestMethod "$adres/durum/$kod"
```

```test
eq(out, "503|istek\n", "istenen kod olduğu gibi döner")
eq(run(stdin="400\n"), "400|istek\n", "alt sınır 400 kabul edilir")
eq(run(stdin="399\n"), "400|kod\n", "alt sınırın bir altı reddedilir: 400 ve hata=kod")
eq(run(stdin="599\n"), "599|istek\n", "üst sınır 599 kabul edilir")
eq(run(stdin="600\n"), "400|kod\n", "üst sınırın bir üstü reddedilir")
eq(run(stdin="beş yüz\n"), "HATA\n", "tam sayı olmayan girdi istek atılmadan HATA")
bos = calis(stdin="")
eq(bos["cikti"], "HATA\n", "boş girdi HATA")
eq(bos["hata"].strip(), "", "boş girdide hata akışına bir şey düşmemeli")

# /durum üretim fixture'ı yalnız 4xx/5xx verir; 2xx dalını ayrı loopback HTTP tanığıyla ölç.
import http.server,threading
from pathlib import Path
class Success(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length','2');self.end_headers();self.wfile.write(b'{}')
    def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Success)
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
path=Path('api_adres.txt');previous=path.read_bytes()
try:
    path.write_text('http://127.0.0.1:'+str(server.server_port),encoding='utf-8')
    r=calis(stdin='200\n')
    eq((r['kod'],r['cikti'],r['hata']),(0,'200|-\n',''),'gerçek 2xx yanıt başarı dalını çalıştırır')
finally:
    path.write_bytes(previous);server.shutdown();server.server_close();thread.join(timeout=2)

```

```solution
$adres = (Get-Content "api_adres.txt" -Raw).Trim()
$sayi = 0
if ($Girdi.Count -lt 1 -or -not [int]::TryParse($Girdi[0].Trim(), [ref]$sayi)) { "HATA"; exit 0 }

try {
    $null = Invoke-RestMethod "$adres/durum/$sayi" -ErrorAction Stop
    "200|-"
} catch {
    "{0}|{1}" -f [int]$_.Exception.Response.StatusCode, ($_.ErrorDetails.Message | ConvertFrom-Json).hata
}
```

```hint
Aralık denetimini sunucu yapıyor; senin işin gelen kodu ve gövdeyi doğru okumak. 400'ün hangi sebeple geldiğini (`istek` mi `kod` mu) yalnızca gövde söyler.
```
:::


::: anlat Sürüm köprüsü: yönlendirme, multipart ve süre sınırı
Bu yeni bölüm meta motor: pwsh ile kurulu PowerShell 7.6.8'de çalışır. Önceki Windows PowerShell 5.1 görevleri kendi motorunda kalır. `-Form` 5.1'de yoktur: 5.1'de `-Body` hashtable URL-encoded form üretir; 7'de `-Form` multipart/form-data üretir ve FileInfo değeri dosya baytlarını taşır. Dosya yolunu metin olarak vermek dosyayı yüklemekle aynı şey değildir. Boundary içeren Content-Type'ı istemcinin üretmesine izin ver.

`-MaximumRedirection 2` en çok iki yönlendirmeye izin verir: iki hop başarı, üç hop sınır hatasıdır. Bir yönlendirmede host/protokol değişimi, yöntem ve Authorization davranışını ayrıca değerlendir; burada yalnız aynı loopback sunucusunda GET/302 zinciri kullanılır. Genelde yönlendirme hedefini güvenilir varsayma.

PowerShell 7'nin ConnectionTimeoutSeconds ve OperationTimeoutSeconds parametreleri farklı beklemeleri kapsar. Bu tezgâh yanıt başlıklarını geciktiren ve başlıkları hemen gönderip gövdeyi geciktiren iki ayrı uç sağlar. 0 sınırsız bekleme anlamına gelebilir; açık süre sınırını kaldırmak yerine iptali yakala. Görevde 100 ms hızlı, 1700 ms yavaş örneklerle 1 saniye bütçesi ölçülür; tam bir saniyede zamanlayıcı yarışı için deterministik iddia kurulmaz. Kurulu 7.6.8 üzerinde başlık bekleyişinde TaskCanceledException, gövde bekleyişinde TimeoutException (içinde TaskCanceledException) ölçüldü. İkisini de süre iptali olarak ayır; HTTP hatasını timeout diye etiketleme.

Tezgâh yalnız 127.0.0.1'de rastgele portta çalışır; harici sisteme istek gerekmez. Ham istek tanıkları ps_http_requests.jsonl içindedir. Bu bir PowerShell taklidi değil, gerçek cmdlet ile gerçek HTTP alışverişidir. Kaynak: [Microsoft Invoke-RestMethod 7](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-restmethod?view=powershell-7.5), [Microsoft Invoke-WebRequest 5.1](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-webrequest?view=powershell-5.1).
:::

::: tahmin İki hop ile üç hop
```meta
motor: pwsh
timeout: 30
```
```setup
import os,runpy,sys,pathlib
_s=os.path.dirname(next(m.__file__ for m in list(sys.modules.values()) if os.path.basename(getattr(m,"__file__",None) or "")=="py_harness.py"))
runpy.run_path(os.path.join(_s,"ps_http_edges.py"),run_name="__tezgah__")
pathlib.Path("dosya adı.bin").write_bytes(bytes(range(256))+b"\x00\xff")
pathlib.Path("bos.bin").write_bytes(b"")
```
```powershell
$adres=(Get-Content ps_http_adres.txt -Raw).Trim()
(Invoke-RestMethod "$adres/hop/2" -MaximumRedirection 2).ok
try { $null=Invoke-RestMethod "$adres/hop/3" -MaximumRedirection 2 -ErrorAction Stop }
catch { [int]$_.Exception.Response.StatusCode }
```

???
`True` ve `302`. İki yönlendirme tamamlanır; üçüncüde kalan 302 yanıtı hata olur.
:::

::: gorev Yönlendirme sınırının iki tarafı
Girdide 0–5 tam sayı hop adedi var. Gerçek Invoke-RestMethod ile /hop/<adet> iste; MaximumRedirection **2** olsun. Sonuca ulaşılırsa OK; 302 sınır hatasıysa LIMIT yaz. Diğer HTTP/ağ hatalarını yutma. Sayı değilse veya 0–5 dışındaysa istek göndermeden HATA. API adresini ps_http_adres.txt'den oku.
```meta
motor: pwsh
timeout: 30
```
```setup
import os,runpy,sys,pathlib
_s=os.path.dirname(next(m.__file__ for m in list(sys.modules.values()) if os.path.basename(getattr(m,"__file__",None) or "")=="py_harness.py"))
runpy.run_path(os.path.join(_s,"ps_http_edges.py"),run_name="__tezgah__")
pathlib.Path("dosya adı.bin").write_bytes(bytes(range(256))+b"\x00\xff")
pathlib.Path("bos.bin").write_bytes(b"")
```
```stdin
2
```
```starter
'OK'
```
```test
import json,pathlib
log=pathlib.Path('ps_http_requests.jsonl')
def paths():return [json.loads(line)['path'] for line in log.read_text(encoding='utf-8').splitlines()]
eq(out,'OK\n','tam iki yönlendirme dahil')
eq(paths(),['/hop/2','/hop/1','/hop/0'],'gerçek GET zinciri tamamlandı')
for n,text in [(0,'OK'),(1,'OK'),(3,'LIMIT'),(5,'LIMIT')]:
    old=len(paths())
    eq(run(stdin=str(n)+'\n'),text+'\n','hop sınırı')
    expected=['/hop/'+str(n-i) for i in range(min(n,2)+1)]
    eq(paths()[old:],expected,'istemci gerçekten sınırda durdu')
for body in ('-1\n','6\n','x\n',''):
    old=len(paths());eq(run(stdin=body),'HATA\n','girdi sınırı');eq(len(paths()),old,'geçersizde ağ yok')
```
```solution
$adres=(Get-Content ps_http_adres.txt -Raw).Trim()
$n=0
if ($Girdi.Count -lt 1 -or -not [int]::TryParse($Girdi[0],[ref]$n) -or $n -lt 0 -or $n -gt 5) { 'HATA'; exit 0 }
try {
    $null=Invoke-RestMethod "$adres/hop/$n" -MaximumRedirection 2 -ErrorAction Stop
    'OK'
} catch {
    if ($_.Exception.Response -and [int]$_.Exception.Response.StatusCode -eq 302) { 'LIMIT' }
    else { throw }
}
```
:::

::: gorev Form ile gerçek dosyayı yükle
İlk girdi not metni (boş olabilir), ikinci girdi dosya yolu (başındaki/sonundaki boşlukları Trim ile kırp). Dosya yoksa HATA. PowerShell 7 Invoke-RestMethod -Form ile /form'a not ve dosya adlı iki alan gönder; dosya gerçek FileInfo olsun. Sunucunun döndürdüğü note/filename/size/sha256 nesnesini sıkıştırılmış JSON olarak yaz. Dosya hash'ini yerelde uydurarak çıktı üretme; gerçek multipart tanığı da sınanır. Tezgâhın küçük dosyaları kullanılır; hata durumlarını timeout diye gizleme.
```meta
motor: pwsh
timeout: 30
```
```setup
import os,runpy,sys,pathlib
_s=os.path.dirname(next(m.__file__ for m in list(sys.modules.values()) if os.path.basename(getattr(m,"__file__",None) or "")=="py_harness.py"))
runpy.run_path(os.path.join(_s,"ps_http_edges.py"),run_name="__tezgah__")
pathlib.Path("dosya adı.bin").write_bytes(bytes(range(256))+b"\x00\xff")
pathlib.Path("bos.bin").write_bytes(b"")
```
```stdin
a&b=ç
 dosya adı.bin
```
```starter
'{}'
```
```test
import hashlib,json,pathlib
# Girdi kutusundaki yolun başındaki boşluk bu görevde Trim ile kaldırılır.
root=pathlib.Path('.')
def expected(note,file):
    data=root.joinpath(file).read_bytes()
    return {'note':note,'filename':file,'size':len(data),'sha256':hashlib.sha256(data).hexdigest()}
def records():return [json.loads(line) for line in root.joinpath('ps_http_requests.jsonl').read_text(encoding='utf-8').splitlines()]
eq(json.loads(out),expected('a&b=ç','dosya adı.bin'),'Unicode not ve gerçek ikili dosya')
eq(records()[-1]['fields'],{'not':'a&b=ç'},'URL-encoded veya JSON değil gerçek multipart alanı')
for note,file in [('', 'bos.bin'),('not="yeni" & x=2','dosya adı.bin')]:
    old=len(records());eq(json.loads(run(stdin=note+'\n'+file+'\n')),expected(note,file),'boş dosya/not ve özel karakterler')
    eq(len(records()),old+1,'gerçek POST gönderildi')
    eq(records()[-1]['files']['dosya']['size'],expected(note,file)['size'],'sunucunun gördüğü bayt sayısı')
old=len(records());eq(run(stdin='x\nyok.bin\n'),'HATA\n','dosya yok');eq(len(records()),old,'olmayan dosyada istek yok')
eq(run(stdin=''),'HATA\n','eksik girdi')
```
```solution
if ($Girdi.Count -lt 2) { 'HATA'; exit 0 }
$yol=$Girdi[1].Trim()
if (-not (Test-Path -LiteralPath $yol -PathType Leaf)) { 'HATA'; exit 0 }
$adres=(Get-Content ps_http_adres.txt -Raw).Trim()
$yanit=Invoke-RestMethod "$adres/form" -Method Post -Form @{not=$Girdi[0];dosya=(Get-Item -LiteralPath $yol)} -ErrorAction Stop
$yanit | ConvertTo-Json -Compress
```
:::

::: gorev Başlık ve gövde bekleyişini sınırla
İlk satır 0–3000 milisaniye, ikinci satır headers veya body. Gerçek Invoke-RestMethod ile headers için /delay/<ms>, body için /body-delay/<ms> iste. ConnectionTimeoutSeconds ve OperationTimeoutSeconds **1** olsun. Başarıda OK|<sunucunun ms alanı>, TaskCanceledException veya TimeoutException iptalinde TIMEOUT; diğer hatalarda throw. Geçersiz girdide istek göndermeden HATA. PowerShell işleminin başlaması için geçen süre HTTP süre bütçesinden ayrıdır.
```meta
motor: pwsh
timeout: 30
```
```setup
import os,runpy,sys,pathlib
_s=os.path.dirname(next(m.__file__ for m in list(sys.modules.values()) if os.path.basename(getattr(m,"__file__",None) or "")=="py_harness.py"))
runpy.run_path(os.path.join(_s,"ps_http_edges.py"),run_name="__tezgah__")
pathlib.Path("dosya adı.bin").write_bytes(bytes(range(256))+b"\x00\xff")
pathlib.Path("bos.bin").write_bytes(b"")
```
```stdin
100
headers
```
```starter
'OK|100'
```
```test
import json,pathlib
log=pathlib.Path('ps_http_requests.jsonl')
def records():return [json.loads(line) for line in log.read_text(encoding='utf-8').splitlines()]
eq(out,'OK|100\n','hızlı başlık yanıtı')
for ms,mode,text in [(0,'headers','OK|0'),(100,'body','OK|100'),(1700,'headers','TIMEOUT'),(1700,'body','TIMEOUT')]:
    old=len(records());eq(run(stdin=str(ms)+'\n'+mode+'\n'),text+'\n','gerçek HTTP süre bütçesi')
    eq([r['path'] for r in records()[old:]],[('/delay/' if mode=='headers' else '/body-delay/')+str(ms)],'yanıt taklit edilmez, istek tanığı var')
for body in ('-1\nheaders\n','3001\nheaders\n','1\nother\n','x\nheaders\n',''):
    old=len(records());eq(run(stdin=body),'HATA\n','girdi sınırları');eq(len(records()),old,'geçersizde ağ yok')
address=pathlib.Path('ps_http_adres.txt');saved=address.read_text(encoding='utf-8')
try:
    address.write_text(saved+'/missing',encoding='utf-8')
    r=calis(stdin='0\nheaders\n')
    ok(r['kod']!=0,'gerçek 404 tekrar throw edilir')
    ok('TIMEOUT' not in r['cikti'],'HTTP hatası süre iptali değildir')
finally:address.write_text(saved,encoding='utf-8')
```
```solution
$ms=0
if ($Girdi.Count -lt 2 -or -not [int]::TryParse($Girdi[0],[ref]$ms) -or $ms -lt 0 -or $ms -gt 3000 -or $Girdi[1] -notin @('headers','body')) { 'HATA'; exit 0 }
$adres=(Get-Content ps_http_adres.txt -Raw).Trim()
$tip=if ($Girdi[1] -eq 'headers') {'delay'} else {'body-delay'}
try {
    $r=Invoke-RestMethod "$adres/$tip/$ms" -ConnectionTimeoutSeconds 1 -OperationTimeoutSeconds 1 -ErrorAction Stop
    "OK|$($r.ms)"
} catch {
    if ($_.Exception -is [System.Threading.Tasks.TaskCanceledException] -or $_.Exception -is [System.TimeoutException]) { 'TIMEOUT' }
    else { throw }
}
```
:::
