---
id: rx18
title: Günlük Biçimleri
summary: Syslog RFC 3164 (BSD) ve RFC 5424 başlıkları, PRI değeri, tek haneli günün çift boşluk tuzağı, isteğe bağlı PID, NIL değer (-) ve yapılandırılmış veri; web sunucusu erişim günlüğünün ilk alanları.
---

::: anlat Syslog: iki kuşak
Linux sunucuları, ağ cihazları ve pek çok uygulama günlüklerini **syslog** biçiminde yazar. Sahada iki kuşağı birlikte görürsün.

### RFC 3164 (BSD syslog)
```text
<30>Oct 19 08:15:02 web01 cron[812]: yedek başladı
└┬─┘└──────┬──────┘ └─┬─┘ └──┬───┘  └─────┬─────┘
PRI      zaman     makine uygulama[PID]  mesaj
```

- **PRI** = tesis × 8 + önem. `<30>` = tesis 3 (daemon) × 8 + önem 6 (info).
- **Zaman**: ay adı, gün, saat. **Yıl ve saat dilimi yoktur.**
- **Gün** tek haneliyse önüne rakam değil **boşluk** konur: `Oct  5`. Bu yüzden ay ile gün arasında iki boşluk olur.
- **PID** isteğe bağlıdır: `kernel:` gibi köşeli parantezsiz uygulama adları da vardır.

| Önem | Ad | Önem | Ad |
|---|---|---|---|
| 0 | emerg | 4 | warning |
| 1 | alert | 5 | notice |
| 2 | crit | 6 | info |
| 3 | err | 7 | debug |

```regex
^<(?P<pri>\d{1,3})>(?P<zaman>[A-Z][a-z]{2} [ \d]\d \d{2}:\d{2}:\d{2}) (?P<makine>\S+) (?P<uygulama>[^\s\[:]+)(?:\[(?P<pid>\d+)\])?: (?P<mesaj>.*)$
---
<30>Oct 19 08:15:02 web01 cron[812]: yedek başladı
```

Günün deseni `[ \d]\d`'dir: ilk karakter boşluk ya da rakam, ikincisi rakam. Uygulama adı `[^\s\[:]+` ile köşeli parantez ya da iki noktaya kadar okunur; PID grubu bütünüyle isteğe bağlıdır.

### RFC 5424
Yeni biçim yılı, saat dilimini ve saniye kesrini içeren bir ISO zaman damgası kullanır ve alanları kesin sıraya koyar:

```text
<165>1 2026-10-19T08:15:02.003Z web01 rapor 4321 ID47 - Rapor üretildi
PRI  sürüm  zaman              makine uyg. PID  MSGID SD mesaj
```

- Bilinmeyen alan boş bırakılmaz, **NIL** değeri `-` yazılır.
- **SD** (yapılandırılmış veri) ya `-` ya da bir veya daha çok köşeli parantezli bloktur: `[meta@32473 boyut="12"]`.
- Mesaj isteğe bağlıdır.

> [!İPUCU]
> Bir günlük biçimini ayrıştırmadan önce **standardını** oku ve kenar durumlarını listele: tek haneli gün, eksik PID, NIL değer, boş mesaj. Çoğu ayrıştırma hatası, desenin yazarının hiç görmediği ama standardın açıkça izin verdiği bir durumdan çıkar.
:::

::: anlat Erişim günlüğü
Apache ve nginx'in varsayılan erişim günlüğü "combined" biçimindedir:

```text
10.0.0.7 - ayse [19/Oct/2026:08:15:02 +0300] "GET /rapor?ay=10 HTTP/1.1" 200 5123 "-" "Mozilla/5.0"
istemci  kimlik kullanıcı  [zaman]           "istek satırı"           durum boyut "yönlendiren" "tarayıcı"
```

Kimlik neredeyse her zaman `-`'dir; kullanıcı yalnızca kimlik doğrulaması yapılan isteklerde doludur. Gövde gönderilmeyen yanıtlarda (304 gibi) boyut `0` değil `-` olabilir.

```regex
^(?P<ip>\S+) \S+ (?P<kullanici>\S+) \[(?P<zaman>[^\]]+)\] "(?P<yontem>[A-Z]+) (?P<yol>\S+) (?P<protokol>[^"]+)" (?P<durum>\d{3}) (?P<boyut>\d+|-)
---
10.0.0.7 - ayse [19/Oct/2026:08:15:02 +0300] "GET /rapor?ay=10 HTTP/1.1" 200 5123 "-" "Mozilla/5.0"
```

Her alan, kendisini çevreleyen işaretin **dışlandığı** bir sınıfla okunur: zaman `[^\]]+`, protokol `[^"]+`. Bu, RX17'deki kuralın aynısıdır. Tırnaklı alanların içindeki kaçışlı tırnaklar ve bozuk istek satırları gibi kenar durumlarını RX21'deki projede ele alacaksın.

> [!NOT]
> Günlük artık JSON olarak yazılıyorsa (`{"seviye":"error",...}`) regex kullanma: Splunk'ta `spath`, KQL'de `parse_json()`, Python'da `json.loads` alanları eksiksiz ve güvenle çıkarır.
:::

::: tahmin
Bu desen iki syslog zaman damgasından hangisini yakalar?

```regex
[A-Z][a-z]{2} \d{1,2} \d{2}:\d{2}
```

```stdin
Oct 19 08:15 | Oct  5 23:59
```

???

Yalnızca `Oct 19 08:15`. İkinci zaman damgasında gün tek haneli olduğu için `Oct` ile `5` arasında **iki** boşluk vardır; desendeki tek boşluktan sonra `\d{1,2}` bir rakam bekler ama ikinci boşlukla karşılaşır. Düzeltme: `[A-Z][a-z]{2} [ \d]\d` ya da `[A-Z][a-z]{2} +\d{1,2}`.
:::

::: gorev Syslog başlığı
RFC 3164 satırlarını `pri`, `zaman`, `makine`, `uygulama`, `pid`, `mesaj` adlı gruplarla ayrıştır. Tek haneli günde çift boşluk olabilir; PID olmayabilir (o zaman `pid` grubu eşleşmesin).

```starter
^<(?P<pri>\d+)>(?P<zaman>\w+ \d+ [\d:]+) (?P<makine>\S+) (?P<uygulama>\w+)\[(?P<pid>\d+)\]: (?P<mesaj>.*)$
```

```test
eq(adli("<30>Oct 19 08:15:02 web01 cron[812]: yedek başladı"),
   {"pri": "30", "zaman": "Oct 19 08:15:02", "makine": "web01", "uygulama": "cron", "pid": "812", "mesaj": "yedek başladı"}, "PID'li satır")
eq(adli("<4>Oct  5 23:59:59 db01 kernel: disk uyarısı"),
   {"pri": "4", "zaman": "Oct  5 23:59:59", "makine": "db01", "uygulama": "kernel", "pid": None, "mesaj": "disk uyarısı"}, "tek haneli gün, PID yok")
eq(adli("<190>Oct 20 00:00:01 app01 rapor-uretici[77]: gece raporu: 3 dosya"),
   {"pri": "190", "zaman": "Oct 20 00:00:01", "makine": "app01", "uygulama": "rapor-uretici", "pid": "77", "mesaj": "gece raporu: 3 dosya"}, "tireli uygulama adı, mesajda iki nokta")
```

```solution
^<(?P<pri>\d{1,3})>(?P<zaman>[A-Z][a-z]{2} [ \d]\d \d{2}:\d{2}:\d{2}) (?P<makine>\S+) (?P<uygulama>[^\s\[:]+)(?:\[(?P<pid>\d+)\])?: (?P<mesaj>.*)$
```

```hint
Gün: `[ \d]\d`. Uygulama adı: köşeli parantez, iki nokta ya da boşluğa kadar `[^\s\[:]+` (tire de içerebilir, `\w+` yetmez).
```

```hint
PID'i köşeli parantezleriyle birlikte isteğe bağlı bir gruba al: `(?:\[(?P<pid>\d+)\])?`.
```
:::

::: gorev RFC 5424 satırı
RFC 5424 satırlarını `pri`, `surum`, `zaman`, `makine`, `uygulama`, `pid`, `msgid`, `sd`, `mesaj` adlı gruplarla ayrıştır. NIL alanlar `-` olarak gelir. `sd` ya `-` ya da bir veya daha çok `[...]` bloğudur (bloklar arasında boşluk yoktur, içlerinde boşluk olabilir). Mesaj olmayabilir.

```starter
^<(?P<pri>\d+)>(?P<surum>\d) (?P<zaman>\S+) (?P<makine>\S+) (?P<uygulama>\S+) (?P<pid>\S+) (?P<msgid>\S+) (?P<sd>\S+) (?P<mesaj>.*)$
```

```test
a = adli("<165>1 2026-10-19T08:15:02.003Z web01 rapor 4321 ID47 - Rapor üretildi")
eq((a["pri"], a["zaman"], a["pid"], a["msgid"], a["sd"], a["mesaj"]), ("165", "2026-10-19T08:15:02.003Z", "4321", "ID47", "-", "Rapor üretildi"), "SD'siz satır")
b = adli('<134>1 2026-10-19T08:16:00Z db01 yedek - - [meta@32473 boyut="12" sure="40"][kaynak@32473 disk="d1"] Yedek tamam')
eq((b["pid"], b["sd"], b["mesaj"]), ("-", '[meta@32473 boyut="12" sure="40"][kaynak@32473 disk="d1"]', "Yedek tamam"), "iki SD bloğu, NIL PID")
c = adli("<14>1 2026-10-19T08:17:00Z web01 izleme - - -")
eq((c["sd"], c["mesaj"]), ("-", None), "mesajsız satır")
```

```solution
^<(?P<pri>\d{1,3})>(?P<surum>\d{1,2}) (?P<zaman>\S+) (?P<makine>\S+) (?P<uygulama>\S+) (?P<pid>\S+) (?P<msgid>\S+) (?P<sd>-|(?:\[[^\]]*\])+)(?: (?P<mesaj>.*))?$
```

```hint
SD alanı boşluk içerebildiği için `\S+` yetmez: ya `-` ya da `(?:\[[^\]]*\])+`.
```

```hint
Mesaj, önündeki boşlukla birlikte isteğe bağlıdır: `(?: (?P<mesaj>.*))?`.
```
:::

::: gorev Erişim günlüğünün ilk alanları
Erişim günlüğü satırlarından `ip`, `kullanici`, `zaman`, `yontem`, `yol`, `durum`, `boyut` adlı grupları çıkar. Boyut bir sayı ya da `-` olabilir.

```starter
^(?P<ip>\S+) - (?P<kullanici>\w+) \[(?P<zaman>.*)\] "(?P<yontem>\w+) (?P<yol>.*) HTTP/1.1" (?P<durum>\d+) (?P<boyut>\d+)
```

```test
a = adli('10.0.0.7 - ayse [19/Oct/2026:08:15:02 +0300] "GET /rapor?ay=10 HTTP/1.1" 200 5123 "-" "Mozilla/5.0"')
eq((a["ip"], a["kullanici"], a["zaman"], a["yontem"], a["yol"], a["durum"], a["boyut"]),
   ("10.0.0.7", "ayse", "19/Oct/2026:08:15:02 +0300", "GET", "/rapor?ay=10", "200", "5123"), "tam satır")
b = adli('10.0.0.9 - - [19/Oct/2026:08:16:44 +0300] "HEAD /saglik HTTP/2.0" 304 - "-" "izleyici/1.2 [test]"')
eq((b["kullanici"], b["zaman"], b["yontem"], b["yol"], b["durum"], b["boyut"]),
   ("-", "19/Oct/2026:08:16:44 +0300", "HEAD", "/saglik", "304", "-"), "anonim kullanıcı, boyutsuz yanıt, HTTP/2.0")
```

```solution
^(?P<ip>\S+) \S+ (?P<kullanici>\S+) \[(?P<zaman>[^\]]+)\] "(?P<yontem>[A-Z]+) (?P<yol>\S+) [^"]+" (?P<durum>\d{3}) (?P<boyut>\d+|-)
```

```hint
Başlangıç kodundaki `.*`'lar açgözlüdür: ikinci satırda zaman, tarayıcı alanındaki `]`'ye kadar uzar. Her alanı, çevreleyen işareti dışlayan bir sınıfla oku: `[^\]]+`, `\S+`, `[^"]+`.
```

```hint
Kullanıcı `-` olabilir (`\S+`), protokol sürümü değişebilir (`[^"]+`), boyut `\d+|-`.
```
:::
