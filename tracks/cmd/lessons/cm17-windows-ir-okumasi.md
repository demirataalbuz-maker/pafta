---
id: cm17
title: Windows IR · Komutu Seç, Çıktıyı Oku
summary: Yerel inceleme komutlarının seçeneklerini anlamak ve sentetik süreç/ağ çıktısından dar bir soruyu yanıtlamak.
---

::: anlat Hangi soru, hangi komut?
Windows incelemesinde komut seçimi soruya bağlıdır. `where cmd.exe` varsayılan olarak çalışma klasörü ile PATH içinde eşleşen dosya yollarını arar. `tasklist /fi "IMAGENAME eq agent.exe" /fo csv /nh` süreç adını filtreler, CSV üretir ve başlığı kapatır. `whoami /user` mevcut hesabın adını ve SID'sini; `ipconfig /all` adaptörlerin ayrıntılı TCP/IP yapılandırmasını gösterir. Bunlar burada komut yazımını okumak içindir; canlı bilgisayar çıktısı sabit bir alıştırma cevabı olamaz.

`netstat -ano -p tcp` bağlantı/dinleme bilgilerini sayısal adres ve PID ile alır: `-a` dinleyen uçları da kapsar, `-n` ad çözümlemesini önler, `-o` PID ekler, `-p tcp` protokolü seçer. Yerel port ile uzak portu karıştırma. Bir dinleme satırı tek başına kötü amaçlı etkinlik kanıtı değildir; süreç kimliği, zaman ve başka kanıtlarla ilişkilendirilir.

Kaynaklar: [WHERE](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/where), [TASKLIST](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/tasklist), [WHOAMI](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/whoami), [IPCONFIG](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/ipconfig), [NETSTAT](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netstat).
:::

::: anlat Olayları sorgula; biçimin sınırını bil
`wevtutil qe Application /c:3 /rd:true /f:xml`, Application günlüğünden en yeni taraftan en fazla üç olayı XML olarak okuyan bir sorgu örneğidir. `qe` okuma işlemidir; aynı aracın yapılandırma ve günlük temizleme fiilleri farklı işlemlerdir. XML içindeki EventID, sağlayıcı ve zaman alanları anlamlı bağlam taşır; XML'i satırda anahtar sözcük aramasıyla genel olarak ayrıştıramazsın.

Bu dersin görevleri canlı tasklist/netstat çalıştırmaz. Koşucu, geçici klasöre açıkça tanımlanmış sentetik çıktılar hazırlar. İlk iki CSV alanında virgül ve gömülü tırnak bulunmadığında `for /f "tokens=1,2 delims=,"` yeterlidir; bu, genel CSV ayrıştırıcısı değildir. Ağ görevinin başlıkları ve sütunları da sabittir; yerelleştirilmiş bütün Windows sürümlerinin çıktılarını desteklediğini varsayma. Ayrıştırma sözleşmesini yazmak, yanlış olumlu sonuçları azaltır.

Kaynak: [WEVTUTIL](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wevtutil).
:::

::: tahmin
Bu kod kendi sentetik dosyasını oluşturur; bilgisayardaki gerçek süreçleri sorgulamaz. Tam ad eşleşmesi ile büyük/küçük harf karşılaştırmasını izle.

```cmd
@echo off
setlocal DisableDelayedExpansion
>"surecler.csv" echo "agent.exe","120","Console","1","100 K"
>>"surecler.csv" echo "agent1.exe","121","Console","1","100 K"
>>"surecler.csv" echo "AGENT.EXE","122","Console","1","100 K"
for /f "usebackq tokens=1,2 delims=," %%A in ("surecler.csv") do if /i "%%~A"=="agent.exe" echo(%%~B
exit /b 0
```

???

Çıktı `120` ve `122` satırlarıdır. `/i` adın harf durumunu yok sayar; `agent1.exe` tam eşleşme değildir. İkinci CSV alanı PID'dir.
:::

::: gorev Sentetik süreç listesinden PID seç
`surecler.csv` dosyasının ilk iki alanı tırnaklı `imaj_adı,PID` çiftidir; ardından başka alanlar olabilir. Başlık yoktur. İlk iki alanda virgül, gömülü çift tırnak veya satır sonu bulunmaz. İlk argüman aranacak tam imaj adı; yoksa/boşsa `agent.exe` kullan. Büyük/küçük harfi yok sayarak eşleşen satırların PID'lerini dosya sırasıyla yaz; başka çıktı olmasın. Eşleşme yoksa boş çıktı. Adlar boşluk, Unicode, `&`, `%`, `!`, `^` içerebilir. Dosyayı değiştirme; canlı süreç komutu çağırma.

```setup
from pathlib import Path
Path('surecler.csv').write_text('"agent.exe","120","Console","1","1,200 K"\n"agent1.exe","121","Console","1","100 K"\n"AGENT.EXE","122","Console","1","100 K"\n',encoding='utf-8')
```

```starter
@echo off
echo 120
exit /b 0
```

```test
from pathlib import Path
p=Path('surecler.csv')
ilk=p.read_bytes()
eq(out,'120\n122\n','iki tam eşleşme')
eq(p.read_bytes(),ilk,'girdi aynı')
eq(run(argv=['agent1.exe']),'121\n','yakın ada ayrı sorgu')
eq(run(argv=['yok.exe']),'','eşleşme yok')
eq(run(argv=['']),'120\n122\n','boş argüman varsayılan')
for ad in ('iki öğe.exe','A&B.exe','x!y.exe','%PATH%.exe','sona^.exe','&%!^.exe'):
    veri=f'"{ad}","7","Console","1","0 K"\n"x{ad}","8","Console","1","0 K"\n"{ad}","9","Console","1","0 K"\n'
    p.write_text(veri,encoding='utf-8')
    eq(run(argv=[ad]),'7\n9\n','özel karakterler veri ve tam ad')
    eq(p.read_text(encoding='utf-8'),veri,'dosya değiştirilmedi')
p.write_text('',encoding='utf-8')
eq(run(),'','boş dosya')
```

```solution
@echo off
setlocal DisableDelayedExpansion
set "hedef=%~1"
if not defined hedef set "hedef=agent.exe"
for /f "usebackq tokens=1,2 delims=," %%A in ("surecler.csv") do if /i "%%~A"=="%hedef%" echo(%%~B
exit /b 0
```

```hint
İlk iki virgül alanını al, çevre tırnaklarını ~ ile kaldır. Aranan adı SET içinde yakala; CALL ile yeniden genişletme.
```
:::

::: gorev Yerel 443 dinleyicilerini ayır
`tcp.txt`, netstat benzeri sentetik metindir. İlgili satırın beş boşlukla ayrılmış alanı `TCP yerel_uç uzak_uç durum PID` biçiminde. Yalnız protokolü `TCP`, durumu `LISTENING`, yerel portu tam `443` olan satırların PID'sini sırayla yaz. IPv4 `0.0.0.0:443`, IPv6 `[::]:443` gibi verilir; port her zaman son iki noktanın ardından gelir. `1443`, uzak uçtaki 443, başka durum ve UDP eşleşmesin. Başlık/boş satır olabilir. PID tekrar ederse her eşleşen satırı koru; genel tekilleştirme istenmiyor.

```setup
from pathlib import Path
Path('tcp.txt').write_text('Proto Yerel Uzak Durum PID\nTCP 0.0.0.0:443 0.0.0.0:0 LISTENING 40\nTCP [::]:443 [::]:0 LISTENING 41\nTCP 0.0.0.0:1443 0.0.0.0:0 LISTENING 42\nTCP 10.0.0.1:5000 10.0.0.2:443 ESTABLISHED 43\n',encoding='utf-8')
```

```starter
@echo off
echo 40
exit /b 0
```

```test
from pathlib import Path
p=Path('tcp.txt')
eq(out,'40\n41\n','IPv4 ve IPv6')
satirlar=[]
beklenen=[]
pid=100
for proto in ('TCP','UDP'):
    for port in (442,443,444,1443):
        for durum in ('LISTENING','ESTABLISHED','CLOSE_WAIT'):
            satirlar.append(f'{proto} 127.0.0.1:{port} 10.0.0.2:443 {durum} {pid}')
            if proto=='TCP' and port==443 and durum=='LISTENING': beklenen.append(str(pid))
            pid+=1
p.write_text('başlık\n\n'+'\n'.join(satirlar)+'\n',encoding='utf-8')
eq(run(),''.join(x+'\n' for x in beklenen),'portun iki komşusu ve her koşul ayrı')
p.write_text('TCP [2001:db8::1]:443 [::]:0 LISTENING 8\nTCP [::]:443 [::]:0 LISTENING 8\n',encoding='utf-8')
eq(run(),'8\n8\n','IPv6 ve tekrar eden PID')
p.write_text('TCP 0.0.0.0:444 0.0.0.0:443 LISTENING 9\n',encoding='utf-8')
eq(run(),'','uzak port eşleşmesi yeterli değil')
p.write_text('',encoding='utf-8')
eq(run(),'','boş dosya')
```

```solution
@echo off
setlocal DisableDelayedExpansion
for /f "usebackq tokens=1-5" %%A in ("tcp.txt") do (
    set "proto=%%A"
    set "adres=%%B"
    set "durum=%%D"
    set "pid=%%E"
    call :sec
)
exit /b 0
:sec
if not "%proto%"=="TCP" exit /b 0
if not "%durum%"=="LISTENING" exit /b 0
if not "%adres:~-4%"==":443" exit /b 0
echo(%pid%
exit /b 0
```

```hint
Beş alanı ayrı değişkenlere yakala; sabit CALL satırıyla her satırı denetle. Bu dar sözleşmede son dört karakterin :443 olması tam portu ayırır; 1443'ün sonunda iki nokta yoktur.
```
:::
