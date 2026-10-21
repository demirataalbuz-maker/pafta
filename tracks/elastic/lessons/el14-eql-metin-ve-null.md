---
id: el14
title: EQL · Listeler, Kalıplar ve Opsiyonel Alan
summary: in/in~, like/like~, ?alan ve null; mapping yokluğu ile olay değerinin yokluğunu ayırmak.
---

::: anlat Liste ile kalıbı ayır
`in` bir değer listesidir; `like` metin kalıbıdır. Sona gelen `~` bu iki işlemde harf farkını kaldırır. Metinler çift tırnaklıdır. `*` sıfır veya daha çok, `?` tam bir karakterin yerini tutar:

```eql norun
process where process.name in~ ("cmd.exe", "powershell.exe")
```

```eql norun
process where process.name like "cmd?.exe"
```

İkinci sorgu `cmd1.exe` için doğru, `cmd.exe` ve `cmd12.exe` için yanlıştır. `like` büyük harfli `CMD1.EXE`'yi de seçmez; `like~` seçer. `in ("cmd*.exe")` içindeki yıldızı kalıp sanma. Liste eşitliği ile jokerli karşılaştırma farklı sorulardır.

Python görevi yalnız burada verilen ASCII ad listesini ve sabit `cmd?.exe` kalıbını karşılaştırır. Python'un bütün desen kurallarının EQL ile aynı olduğu iddia edilmiyor; özellikle köşeli parantezli glob kalıplarını bu alıştırmaya taşıma.
:::

::: anlat Mapping'de yok mu, kayıtta değer mi yok?
EQL bir alanın indeks mapping'inde bulunmasını bekler. Mapping'de hiç olmayan alanı normal biçimde kullanmak sorgu hatasıdır. Başına `?` koymak bu durumu opsiyonel yapar. `?user.id != null`, indekslenmiş kullanıcı değeri bulunan olayları; `?user.id == null`, değeri bulunmayanları sorgular.

```eql norun
process where process.name in~ ("cmd.exe", "powershell.exe") and ?user.id != null
```

Bir JSON anahtarının `_source` içinde görünmesi tek başına indekslenmiş alan garantisi değildir. Bu ders, mapping listesini ayrıca verir. Mapping'de olan alanın olayda eksik veya `None` olması ile mapping'in bütünüyle yokluğu ayrı durumlardır. Boş metin `""` ise bu örnekte geçerli bir keyword değeridir; `null` sayılmaz.

Görevler tek değerli alanlar, varsayılan null davranışı ve açık mapping listesiyle sınırlı Python okuma çalışmalarıdır. Mapping hatasını yakalayabilmek, boş sonuçları yanlış yorumlamayı önler.

Kaynak: [EQL listeleri ve opsiyonel alanlar](https://www.elastic.co/docs/reference/query-languages/eql/eql-syntax).
:::

::: tahmin
`event.category`, `process.name`, `user.id` keyword olarak mapped. Alanlar tek değerli, tarihler eşit biçimde UTC; kayıt sırasını koru. Hangi kimlikler seçilir?

```eql
process where process.name in~ ("cmd.exe", "powershell.exe") and ?user.id != null
```

```stdin
[
  {"event.id":"m1","@timestamp":"2026-10-21T10:00:00.000Z","event.category":"process","process.name":"CMD.EXE","user.id":"u1"},
  {"event.id":"m2","@timestamp":"2026-10-21T10:00:01.000Z","event.category":"process","process.name":"cmd.exe","user.id":null},
  {"event.id":"m3","@timestamp":"2026-10-21T10:00:02.000Z","event.category":"process","process.name":"powershell.exe"},
  {"event.id":"m4","@timestamp":"2026-10-21T10:00:03.000Z","event.category":"process","process.name":"PowerShell.Exe","user.id":""},
  {"event.id":"m5","@timestamp":"2026-10-21T10:00:04.000Z","event.category":"file","process.name":"cmd.exe","user.id":"u2"}
]
```

```gercek
m1
m4
```

```test
import json, sys
for e in json.load(sys.stdin):
    ad = e.get("process.name")
    if e.get("event.category") == "process" and isinstance(ad, str) and ad.lower() in ("cmd.exe", "powershell.exe") and e.get("user.id") is not None:
        print(e["event.id"])
```

???

`in~` harf farkını kaldırdığı için `m1` ve `m4`'ün adları uyar. `m4`'ün boş kullanıcı metni null değildir. `m2` null, `m3` eksik değer taşır; `m5` yanlış kategoridedir. Bu yanıt, yazılı mapping varsayımlarına bağlıdır.
:::

::: gorev Dört metin kararını hesapla
`metin_kararlari(ad)` sırasıyla şu dört koşulun boolean listesini döndürsün: `in ("cmd.exe", "powershell.exe")`, `in~` aynı liste, `like "cmd?.exe"`, `like~` aynı kalıp. Girdi ASCII metin veya `None`. `None` için dördü de yanlış. Sorgu ayrıştırıcı yazmıyorsun; yalnız bu sabit koşulları okuyorsun.

```starter
def metin_kararlari(ad):
    return [False, False, False, False]
```

```test
for ad, beklenen in (("cmd.exe", [True,True,False,False]), ("CMD.EXE", [False,True,False,False]),
                     ("cmd1.exe", [False,False,True,True]), ("CMD1.EXE", [False,False,False,True]),
                     ("cmd12.exe", [False,False,False,False]), ("powershell.exe", [True,True,False,False]),
                     ("PowerShell.Exe", [False,True,False,False]), ("cmd*.exe", [False,False,True,True]),
                     ("cmd1.exe.bak", [False,False,False,False]), (None, [False,False,False,False])):
    eq(metin_kararlari(ad), beklenen, repr(ad))
```

```solution
from fnmatch import fnmatchcase

def metin_kararlari(ad):
    if ad is None:
        return [False, False, False, False]
    adlar = ("cmd.exe", "powershell.exe")
    return [ad in adlar, ad.lower() in adlar,
            fnmatchcase(ad, "cmd?.exe"), fnmatchcase(ad.lower(), "cmd?.exe")]
```

```hint
Bu tek sabit kalıp için fnmatchcase kullanılabilir. '?' girişteki bir karakteri tutar; o karakter yıldızın kendisi de olabilir.
```
:::

::: gorev Alanın durumunu doğru adlandır
`alan_durumu(mapping, olay, alan, opsiyonel)` şu etiketlerden birini döndürsün: alan mapping'de yok ve opsiyonel değilse `"mapping_hatasi"`; yok ve opsiyonelse `"null"`; mapped ama olayda eksik veya `None` ise `"null"`; diğer durumda `"deger"`. Mapping alan adlarının kümesidir. Alan mapped değilse `_source` örneğinde görünen değeri kullanma. Boş metin ve 0 geçerli değerlerdir.

```starter
def alan_durumu(mapping, olay, alan, opsiyonel):
    return "deger" if alan in olay else "null"
```

```test
mapped = {"user.id", "process.name"}
for olay, sonuc in (({}, "null"), ({"user.id":None}, "null"), ({"user.id":""}, "deger"),
                    ({"user.id":"u1"}, "deger"), ({"user.id":0}, "deger")):
    eq(alan_durumu(mapped, olay, "user.id", False), sonuc, "mapped alan")
    eq(alan_durumu(mapped, olay, "user.id", True), sonuc, "? mapped değeri değiştirmez")
for olay in ({}, {"user.id":"kaynakta-var"}):
    eq(alan_durumu(set(), olay, "user.id", False), "mapping_hatasi", "mapping yokluğu")
    eq(alan_durumu(set(), olay, "user.id", True), "null", "? mapping hatasını önler")
eq(alan_durumu({"User.ID"}, {"User.ID":"x"}, "user.id", False), "mapping_hatasi", "alan adı harfi değişmez")
```

```solution
def alan_durumu(mapping, olay, alan, opsiyonel):
    if alan not in mapping:
        return "null" if opsiyonel else "mapping_hatasi"
    return "null" if olay.get(alan) is None else "deger"
```

```hint
Önce mapping'e, sonra olay değerine bak. if not deger yazarsan boş metni ve sıfırı yanlışlıkla null yaparsın.
```
:::
