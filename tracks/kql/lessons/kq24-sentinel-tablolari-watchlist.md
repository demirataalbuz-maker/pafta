---
id: kq24
title: Sentinel ve Defender Tabloları · Watchlist ile Avcılık
summary: Gerçek ürünlerin tablo adları ve sütunları (SigninLogs, DeviceProcessEvents, DeviceNetworkEvents); TimeGenerated ile Timestamp farkı; SigninLogs'ta ResultType'ın metin olması; UPN ve dosya adlarında büyük-küçük harf tuzağı (== ile =~, in ile in~, tolower ile birleştirme); _GetWatchlist ile bir listeyi sorguya katmak; tezgahın gerçek şemaların küçük bir alt kümesini öykündüğü, gerçek Sentinel için bir Azure çalışma alanı gerektiği.
kazanim: SC200 3.1, SC200 3.2, SC200 4.3
---

::: anlat Gerçek tabloların adları
Şimdiye kadar `istekler` gibi bu tezgaha özgü tablolarla çalıştın. Microsoft Sentinel ve Defender XDR'da tabloların adları ve sütunları **sabittir**; ilan edilen bir avcılık sorgusunu okuyabilmek için onları tanıman gerekir. Bu derste üç tanesinin küçük bir alt kümesi kurulu:

| Tablo | Nereden gelir | Bu derste kullanılan sütunlar |
|---|---|---|
| `SigninLogs` | Microsoft Entra ID oturum açmaları | `TimeGenerated`, `UserPrincipalName`, `IPAddress`, `ResultType`, `ResultDescription`, `AppDisplayName`, `Location` |
| `DeviceProcessEvents` | Defender for Endpoint: başlayan süreçler | `Timestamp`, `DeviceName`, `AccountName`, `FileName`, `ProcessCommandLine`, `InitiatingProcessFileName`, `SHA256` |
| `DeviceNetworkEvents` | Defender for Endpoint: ağ bağlantıları | `Timestamp`, `DeviceName`, `RemoteIP`, `RemotePort`, `RemoteUrl`, `InitiatingProcessFileName` |

```kql
SigninLogs
| getschema
| project ColumnName, ColumnType
```

Üç ayrıntı her gün karşına çıkar:

- **Zaman sütunu.** Sentinel'de her tablonun zamanı `TimeGenerated`'dır. Defender XDR'ın gelişmiş avcılık ekranında aynı `Device*` tabloları `Timestamp` ile gelir. Bu derste Defender tabloları `Timestamp` taşıyor.
- **`ResultType` metindir.** Başarılı oturum `"0"`, geri kalanı bir Entra hata kodu: `"50126"` yanlış kullanıcı adı ya da parola, `"50053"` kilitli hesap. Karşılaştırmayı tırnakla yaz: `ResultType != "0"`.
- **Harf büyüklüğü.** `UserPrincipalName` aynı kişi için `ayse@...`, `Ayse@...` ya da `AYSE@...` gelebilir; süreç adları `powershell.exe` ya da `PowerShell.exe`. `==`, `in` ve `join` büyük-küçük harfe duyarlıdır.

> [!NOT] Bu tezgah gerçek şema değil
> Tablolar gerçek adlarla kuruldu, ama gerçek tablolarda onlarca sütun daha vardır (ör. `SigninLogs`'ta `DeviceDetail`, `ConditionalAccessStatus`; `Device*` tablolarında `ReportId`, `InitiatingProcessAccountName`). Satırlar da bu ders için yazıldı. Bu sorguları gerçek veride denemek için bir Azure aboneliği ve Sentinel'in açık olduğu bir Log Analytics çalışma alanı gerekir; KQ21'deki ücretsiz küme bu tabloları içermez.

```setup
CREATE TABLE SigninLogs (TimeGenerated TEXT, UserPrincipalName TEXT, IPAddress TEXT, ResultType TEXT, ResultDescription TEXT, AppDisplayName TEXT, Location TEXT);
INSERT INTO SigninLogs VALUES
 ('2026-10-19 08:58','ayse@pafta.example','10.0.1.15','0','','Outlook','TR'),
 ('2026-10-19 09:01','Ayse@pafta.example','203.0.113.50','50126','Invalid username or password','Azure Portal','NL'),
 ('2026-10-19 09:02','Ayse@pafta.example','203.0.113.50','50126','Invalid username or password','Azure Portal','NL'),
 ('2026-10-19 09:03','AYSE@pafta.example','203.0.113.51','50126','Invalid username or password','Azure Portal','NL'),
 ('2026-10-19 09:04','can@pafta.example','203.0.113.50','50126','Invalid username or password','Azure Portal','NL'),
 ('2026-10-19 09:06','mert@pafta.example','10.0.2.8','50053','Account is locked','Teams','TR'),
 ('2026-10-19 09:10','zeynep@pafta.example','10.0.3.4','0','','Azure Portal','TR'),
 ('2026-10-19 09:12','zeynep@pafta.example','198.51.100.9','50126','Invalid username or password','Azure Portal','DE');
CREATE TABLE DeviceProcessEvents (Timestamp TEXT, DeviceName TEXT, AccountName TEXT, FileName TEXT, ProcessCommandLine TEXT, InitiatingProcessFileName TEXT, SHA256 TEXT);
INSERT INTO DeviceProcessEvents VALUES
 ('2026-10-19 09:20','pc-ayse','ayse','powershell.exe','powershell.exe -nop -w hidden -enc SQBFAFgA','WINWORD.EXE','a1'),
 ('2026-10-19 09:21','pc-ayse','ayse','cmd.exe','cmd.exe /c whoami','powershell.exe','b2'),
 ('2026-10-19 09:30','pc-can','can','PowerShell.exe','PowerShell.exe -File yedek.ps1','explorer.exe','c3'),
 ('2026-10-19 09:40','pc-mert','mert','cmd.exe','cmd.exe /c rapor.bat','EXCEL.EXE','d4'),
 ('2026-10-19 09:45','pc-zeynep','zeynep','notepad.exe','notepad.exe not.txt','winword.exe','e5');
CREATE TABLE DeviceNetworkEvents (Timestamp TEXT, DeviceName TEXT, RemoteIP TEXT, RemotePort INTEGER, RemoteUrl TEXT, InitiatingProcessFileName TEXT);
INSERT INTO DeviceNetworkEvents VALUES
 ('2026-10-19 09:22','pc-ayse','198.51.100.66',443,'guncelle.example','powershell.exe'),
 ('2026-10-19 09:23','pc-ayse','198.51.100.66',443,'guncelle.example','powershell.exe'),
 ('2026-10-19 09:25','pc-can','10.0.0.10',445,'','svchost.exe'),
 ('2026-10-19 09:41','pc-mert','192.0.2.200',8080,'','cmd.exe'),
 ('2026-10-19 09:50','pc-zeynep','198.51.100.66',443,'guncelle.example','msedge.exe');
CREATE TABLE watchlist_YoneticiHesaplar (SearchKey TEXT, Rol TEXT);
INSERT INTO watchlist_YoneticiHesaplar VALUES ('ayse@pafta.example','Global Admin'),('zeynep@pafta.example','Güvenlik Yöneticisi');
CREATE TABLE watchlist_KotuIP (SearchKey TEXT, Kaynak TEXT);
INSERT INTO watchlist_KotuIP VALUES ('198.51.100.66','tehdit akışı'),('192.0.2.200','olay 2026-114'),('203.0.113.99','tehdit akışı');
```
:::

::: anlat Watchlist: sorguya bir liste katmak
Bir avcının elinde çoğu zaman bir **liste** vardır: yönetici hesapları, kritik sunucular, bir tehdit akışından gelen kötü IP'ler. Sentinel'de böyle bir listeyi CSV olarak yükleyip **watchlist** yaparsın; yüklerken bir sütunu arama anahtarı seçersin. Sorguda listeyi takma adıyla çağırırsın:

```kql
_GetWatchlist('YoneticiHesaplar')
```

Anahtar sütun `SearchKey` adıyla gelir, öteki sütunlar kendi adlarıyla. Gerçek Sentinel bunlara `_DTItemId`, `LastUpdatedTimeUTC` gibi yönetim sütunları da ekler; bu tezgahta yalnız `SearchKey` ve listenin kendi sütunları var. Listeyi `let` ile bir kez adlandırıp birleştirirsin:

```kql
let kotu = _GetWatchlist('KotuIP') | project RemoteIP = SearchKey, Kaynak;
DeviceNetworkEvents
| join kind=inner kotu on RemoteIP
| project Timestamp, DeviceName, RemoteIP, Kaynak
```

Listeyi sorgunun içine yazmak yerine watchlist'te tutmanın kazancı: liste değişince **sorgu değişmez**. Analitik kurallar her çalıştırmada listenin güncel hâlini görür.

```setup
CREATE TABLE SigninLogs (TimeGenerated TEXT, UserPrincipalName TEXT, IPAddress TEXT, ResultType TEXT, ResultDescription TEXT, AppDisplayName TEXT, Location TEXT);
INSERT INTO SigninLogs VALUES
 ('2026-10-19 08:58','ayse@pafta.example','10.0.1.15','0','','Outlook','TR'),
 ('2026-10-19 09:01','Ayse@pafta.example','203.0.113.50','50126','Invalid username or password','Azure Portal','NL'),
 ('2026-10-19 09:02','Ayse@pafta.example','203.0.113.50','50126','Invalid username or password','Azure Portal','NL'),
 ('2026-10-19 09:03','AYSE@pafta.example','203.0.113.51','50126','Invalid username or password','Azure Portal','NL'),
 ('2026-10-19 09:04','can@pafta.example','203.0.113.50','50126','Invalid username or password','Azure Portal','NL'),
 ('2026-10-19 09:06','mert@pafta.example','10.0.2.8','50053','Account is locked','Teams','TR'),
 ('2026-10-19 09:10','zeynep@pafta.example','10.0.3.4','0','','Azure Portal','TR'),
 ('2026-10-19 09:12','zeynep@pafta.example','198.51.100.9','50126','Invalid username or password','Azure Portal','DE');
CREATE TABLE DeviceProcessEvents (Timestamp TEXT, DeviceName TEXT, AccountName TEXT, FileName TEXT, ProcessCommandLine TEXT, InitiatingProcessFileName TEXT, SHA256 TEXT);
INSERT INTO DeviceProcessEvents VALUES
 ('2026-10-19 09:20','pc-ayse','ayse','powershell.exe','powershell.exe -nop -w hidden -enc SQBFAFgA','WINWORD.EXE','a1'),
 ('2026-10-19 09:21','pc-ayse','ayse','cmd.exe','cmd.exe /c whoami','powershell.exe','b2'),
 ('2026-10-19 09:30','pc-can','can','PowerShell.exe','PowerShell.exe -File yedek.ps1','explorer.exe','c3'),
 ('2026-10-19 09:40','pc-mert','mert','cmd.exe','cmd.exe /c rapor.bat','EXCEL.EXE','d4'),
 ('2026-10-19 09:45','pc-zeynep','zeynep','notepad.exe','notepad.exe not.txt','winword.exe','e5');
CREATE TABLE DeviceNetworkEvents (Timestamp TEXT, DeviceName TEXT, RemoteIP TEXT, RemotePort INTEGER, RemoteUrl TEXT, InitiatingProcessFileName TEXT);
INSERT INTO DeviceNetworkEvents VALUES
 ('2026-10-19 09:22','pc-ayse','198.51.100.66',443,'guncelle.example','powershell.exe'),
 ('2026-10-19 09:23','pc-ayse','198.51.100.66',443,'guncelle.example','powershell.exe'),
 ('2026-10-19 09:25','pc-can','10.0.0.10',445,'','svchost.exe'),
 ('2026-10-19 09:41','pc-mert','192.0.2.200',8080,'','cmd.exe'),
 ('2026-10-19 09:50','pc-zeynep','198.51.100.66',443,'guncelle.example','msedge.exe');
CREATE TABLE watchlist_YoneticiHesaplar (SearchKey TEXT, Rol TEXT);
INSERT INTO watchlist_YoneticiHesaplar VALUES ('ayse@pafta.example','Global Admin'),('zeynep@pafta.example','Güvenlik Yöneticisi');
CREATE TABLE watchlist_KotuIP (SearchKey TEXT, Kaynak TEXT);
INSERT INTO watchlist_KotuIP VALUES ('198.51.100.66','tehdit akışı'),('192.0.2.200','olay 2026-114'),('203.0.113.99','tehdit akışı');
```
:::

::: tahmin
Watchlist'te Ayşe'nin anahtarı küçük harfle kayıtlı: `ayse@pafta.example`. Bu sorgu ne yazar?

```kql
_GetWatchlist('YoneticiHesaplar')
| where SearchKey == "Ayse@pafta.example"
| count
```

???

**`0`.**

`==` büyük-küçük harfe duyarlıdır; `Ayse` ile `ayse` aynı metin değil. `=~` yazsaydın `1` dönerdi. Aynı tuzak `join`'de de var: `SigninLogs`'taki `Ayse@...` satırları, anahtarı küçük harfli bir watchlist'le doğrudan birleşmez. Birleştirmeden önce iki tarafı da `tolower` ile aynı biçime getir.

```setup
CREATE TABLE watchlist_YoneticiHesaplar (SearchKey TEXT, Rol TEXT);
INSERT INTO watchlist_YoneticiHesaplar VALUES ('ayse@pafta.example','Global Admin'),('zeynep@pafta.example','Güvenlik Yöneticisi');
```
:::

::: gorev 1 · Yönetici hesaplarına başarısız girişler
`YoneticiHesaplar` watchlist'indeki hesapların **başarısız** oturum açmalarını (`ResultType` `"0"` olmayan) say. Her hesap için: `upn` (küçük harfli UPN), `Rol`, `basarisiz` (başarısız giriş sayısı), `ip_sayisi` (farklı IP sayısı). `basarisiz`'a göre büyükten küçüğe.

Başlangıç sorgusu doğrudan `UserPrincipalName` üzerinden birleşiyor ve Ayşe'nin bütün başarısız girişlerini kaçırıyor.

```starter
let yoneticiler = _GetWatchlist('YoneticiHesaplar') | project UserPrincipalName = SearchKey, Rol;
SigninLogs
| where ResultType != "0"
| join kind=inner yoneticiler on UserPrincipalName
| summarize basarisiz = count() by UserPrincipalName, Rol
```

```test
eq(sutunlar, ["upn", "Rol", "basarisiz", "ip_sayisi"], "sütunlar")
eq(kullanir("_GetWatchlist"), True, "listeyi sorguya yazma; _GetWatchlist('YoneticiHesaplar') ile al")
eq(sonuc, [("ayse@pafta.example", "Global Admin", 3, 2), ("zeynep@pafta.example", "Güvenlik Yöneticisi", 1, 1)],
   "Ayşe'nin üç başarısız girişi Ayse@ ve AYSE@ biçiminde; can yönetici değil, mert'in kilitli hesabı listede yok")
eq(dene("INSERT INTO watchlist_YoneticiHesaplar VALUES ('mert@pafta.example','Yardım Masası');"
        "INSERT INTO SigninLogs VALUES ('2026-10-19 09:30','ZEYNEP@pafta.example','198.51.100.9','50126','','Azure Portal','DE'),"
        "('2026-10-19 09:31','ayse@pafta.example','10.0.1.15','0','','Outlook','TR');"),
   [("ayse@pafta.example", "Global Admin", 3, 2), ("zeynep@pafta.example", "Güvenlik Yöneticisi", 2, 1),
    ("mert@pafta.example", "Yardım Masası", 1, 1)],
   "watchlist'e eklenen hesap sorgu değişmeden sonuca girer; başarılı giriş (\"0\") sayılmaz")
```

```solution
let yoneticiler = _GetWatchlist('YoneticiHesaplar') | project upn = tolower(SearchKey), Rol;
SigninLogs
| where ResultType != "0"
| extend upn = tolower(UserPrincipalName)
| join kind=inner yoneticiler on upn
| summarize basarisiz = count(), ip_sayisi = dcount(IPAddress) by upn, Rol
| sort by basarisiz desc
```

```hint
Birleştirme anahtarını iki tarafta da küçük harfe çevir: watchlist'te `project upn = tolower(SearchKey), Rol`, oturumlarda `extend upn = tolower(UserPrincipalName)`; sonra `join kind=inner ... on upn`.
```

```hint
Farklı IP sayısı için `dcount(IPAddress)`; sıralama `sort by basarisiz desc`.
```

```setup
CREATE TABLE SigninLogs (TimeGenerated TEXT, UserPrincipalName TEXT, IPAddress TEXT, ResultType TEXT, ResultDescription TEXT, AppDisplayName TEXT, Location TEXT);
INSERT INTO SigninLogs VALUES
 ('2026-10-19 08:58','ayse@pafta.example','10.0.1.15','0','','Outlook','TR'),
 ('2026-10-19 09:01','Ayse@pafta.example','203.0.113.50','50126','Invalid username or password','Azure Portal','NL'),
 ('2026-10-19 09:02','Ayse@pafta.example','203.0.113.50','50126','Invalid username or password','Azure Portal','NL'),
 ('2026-10-19 09:03','AYSE@pafta.example','203.0.113.51','50126','Invalid username or password','Azure Portal','NL'),
 ('2026-10-19 09:04','can@pafta.example','203.0.113.50','50126','Invalid username or password','Azure Portal','NL'),
 ('2026-10-19 09:06','mert@pafta.example','10.0.2.8','50053','Account is locked','Teams','TR'),
 ('2026-10-19 09:10','zeynep@pafta.example','10.0.3.4','0','','Azure Portal','TR'),
 ('2026-10-19 09:12','zeynep@pafta.example','198.51.100.9','50126','Invalid username or password','Azure Portal','DE');
CREATE TABLE watchlist_YoneticiHesaplar (SearchKey TEXT, Rol TEXT);
INSERT INTO watchlist_YoneticiHesaplar VALUES ('ayse@pafta.example','Global Admin'),('zeynep@pafta.example','Güvenlik Yöneticisi');
```
:::

::: gorev 2 · Office'ten açılan kabuk
Bir Word ya da Excel belgesinin PowerShell ya da cmd başlatması, makrolu bir oltalama belgesinin klasik izidir. `DeviceProcessEvents`'te başlatan süreç (`InitiatingProcessFileName`) `winword.exe` ya da `excel.exe`, başlayan süreç (`FileName`) `powershell.exe` ya da `cmd.exe` olan olayları listele. Adlar her büyüklükte gelebilir. Sütunlar: `Timestamp`, `DeviceName`, `AccountName`, `ProcessCommandLine`; zamana göre artan.

```starter
DeviceProcessEvents
| where InitiatingProcessFileName in ("winword.exe", "excel.exe") and FileName in ("powershell.exe", "cmd.exe")
| project Timestamp, DeviceName, AccountName, ProcessCommandLine
```

```test
eq(sutunlar, ["Timestamp", "DeviceName", "AccountName", "ProcessCommandLine"], "sütunlar")
eq(sonuc, [("2026-10-19 09:20", "pc-ayse", "ayse", "powershell.exe -nop -w hidden -enc SQBFAFgA"),
           ("2026-10-19 09:40", "pc-mert", "mert", "cmd.exe /c rapor.bat")],
   "WINWORD.EXE ve EXCEL.EXE büyük harfle geliyor; pc-can'ın PowerShell'ini explorer başlattı, pc-zeynep'te başlayan notepad")
eq(dene("INSERT INTO DeviceProcessEvents VALUES ('2026-10-19 09:50','pc-can','can','CMD.EXE','CMD.EXE /c dir','Excel.exe','f6'),"
        "('2026-10-19 09:55','pc-can','can','powershell_ise.exe','powershell_ise.exe','WINWORD.EXE','g7'),"
        "('2026-10-19 09:56','pc-can','can','cmd.exe','cmd.exe','winword.exe.bak','h8');")[2:],
   [("2026-10-19 09:50", "pc-can", "can", "CMD.EXE /c dir")],
   "iki tarafta da harf büyüklüğü fark etmez; powershell_ise.exe ve winword.exe.bak tam ad değil")
```

```solution
DeviceProcessEvents
| where InitiatingProcessFileName in~ ("winword.exe", "excel.exe") and FileName in~ ("powershell.exe", "cmd.exe")
| project Timestamp, DeviceName, AccountName, ProcessCommandLine
| sort by Timestamp asc
```

```hint
`in` büyük-küçük harfe duyarlıdır; duyarsız karşılığı `in~`. İki koşulda da `in~` kullan.
```

```hint
`contains` ya da `has` kullanma: `powershell_ise.exe` ya da `winword.exe.bak` gibi adları da yakalar. Tam ad eşleşmesi istiyorsun.
```

```setup
CREATE TABLE DeviceProcessEvents (Timestamp TEXT, DeviceName TEXT, AccountName TEXT, FileName TEXT, ProcessCommandLine TEXT, InitiatingProcessFileName TEXT, SHA256 TEXT);
INSERT INTO DeviceProcessEvents VALUES
 ('2026-10-19 09:20','pc-ayse','ayse','powershell.exe','powershell.exe -nop -w hidden -enc SQBFAFgA','WINWORD.EXE','a1'),
 ('2026-10-19 09:21','pc-ayse','ayse','cmd.exe','cmd.exe /c whoami','powershell.exe','b2'),
 ('2026-10-19 09:30','pc-can','can','PowerShell.exe','PowerShell.exe -File yedek.ps1','explorer.exe','c3'),
 ('2026-10-19 09:40','pc-mert','mert','cmd.exe','cmd.exe /c rapor.bat','EXCEL.EXE','d4'),
 ('2026-10-19 09:45','pc-zeynep','zeynep','notepad.exe','notepad.exe not.txt','winword.exe','e5');
```
:::

::: gorev 3 · Kötü IP listesine bağlananlar
`KotuIP` watchlist'indeki adreslere yapılan bağlantıları cihaz ve adres başına özetle: `DeviceName`, `RemoteIP`, `Kaynak` (listedeki kaynak), `baglanti` (bağlantı sayısı), `ilk` (ilk bağlantı zamanı). İlk bağlantıya göre artan.

```starter
DeviceNetworkEvents
| where RemoteIP in ("198.51.100.66", "192.0.2.200")
| summarize baglanti = count() by DeviceName, RemoteIP
```

```test
eq(sutunlar, ["DeviceName", "RemoteIP", "Kaynak", "baglanti", "ilk"], "sütunlar")
eq(kullanir("_GetWatchlist"), True, "adresleri sorguya yazma; _GetWatchlist('KotuIP') ile al")
eq(sonuc, [("pc-ayse", "198.51.100.66", "tehdit akışı", 2, "2026-10-19 09:22"),
           ("pc-mert", "192.0.2.200", "olay 2026-114", 1, "2026-10-19 09:41"),
           ("pc-zeynep", "198.51.100.66", "tehdit akışı", 1, "2026-10-19 09:50")],
   "203.0.113.99 listede ama hiç bağlantı yok; pc-can'ın 10.0.0.10 bağlantısı listede değil")
eq(dene("INSERT INTO watchlist_KotuIP VALUES ('10.0.0.10','iç tarama');"
        "INSERT INTO DeviceNetworkEvents VALUES ('2026-10-19 09:10','pc-mert','203.0.113.99',443,'','curl.exe');"),
   [("pc-mert", "203.0.113.99", "tehdit akışı", 1, "2026-10-19 09:10"),
    ("pc-ayse", "198.51.100.66", "tehdit akışı", 2, "2026-10-19 09:22"),
    ("pc-can", "10.0.0.10", "iç tarama", 1, "2026-10-19 09:25"),
    ("pc-mert", "192.0.2.200", "olay 2026-114", 1, "2026-10-19 09:41"),
    ("pc-zeynep", "198.51.100.66", "tehdit akışı", 1, "2026-10-19 09:50")],
   "listeye eklenen adres sorgu değişmeden sonuca girer; aynı cihazın iki adresi ayrı satırdır")
```

```solution
let kotu = _GetWatchlist('KotuIP') | project RemoteIP = SearchKey, Kaynak;
DeviceNetworkEvents
| join kind=inner kotu on RemoteIP
| summarize baglanti = count(), ilk = min(Timestamp) by DeviceName, RemoteIP, Kaynak
| sort by ilk asc
```

```hint
Listeyi `let kotu = _GetWatchlist('KotuIP') | project RemoteIP = SearchKey, Kaynak;` ile adlandır, `join kind=inner kotu on RemoteIP` ile birleştir.
```

```hint
Kaynağı sonuçta tutmak için `Kaynak`'ı `by` listesine ekle; ilk zaman `min(Timestamp)`.
```

```setup
CREATE TABLE DeviceNetworkEvents (Timestamp TEXT, DeviceName TEXT, RemoteIP TEXT, RemotePort INTEGER, RemoteUrl TEXT, InitiatingProcessFileName TEXT);
INSERT INTO DeviceNetworkEvents VALUES
 ('2026-10-19 09:22','pc-ayse','198.51.100.66',443,'guncelle.example','powershell.exe'),
 ('2026-10-19 09:23','pc-ayse','198.51.100.66',443,'guncelle.example','powershell.exe'),
 ('2026-10-19 09:25','pc-can','10.0.0.10',445,'','svchost.exe'),
 ('2026-10-19 09:41','pc-mert','192.0.2.200',8080,'','cmd.exe'),
 ('2026-10-19 09:50','pc-zeynep','198.51.100.66',443,'guncelle.example','msedge.exe');
CREATE TABLE watchlist_KotuIP (SearchKey TEXT, Kaynak TEXT);
INSERT INTO watchlist_KotuIP VALUES ('198.51.100.66','tehdit akışı'),('192.0.2.200','olay 2026-114'),('203.0.113.99','tehdit akışı');
```
:::
