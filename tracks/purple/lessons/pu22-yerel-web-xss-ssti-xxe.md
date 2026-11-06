---
id: pu22
title: Yerel Web · XSS, Şablon Enjeksiyonu ve XXE — Gerçek HTTP ile Açık ve Düzeltme
summary: Kendi 127.0.0.1 sunucusunda üç açık/korumalı uç çifti; yansıyan XSS'i kaçışla, str.format şablon enjeksiyonunu alan doğrulamayla, XXE'yi DTD reddiyle kapat; meşru isteklerin çalıştığını ve gizli değerin yalnız açık uçlardan sızdığını gerçek yanıtlarla kanıtla.
timeout: 30
---

::: anlat Üç açık, aynı kök neden
| Sahada ne olur | Bu ders ne kullanır | Ne söyleyemez? |
|---|---|---|
| Web uygulamalarında kullanıcı girdisi kod gibi yorumlanır: HTML'de (XSS), şablon motorunda (SSTI), XML ayrıştırıcıda (XXE) | Kendi `127.0.0.1` sunucusu (yalnız standart kütüphane), rastgele gizli değerler, 13 gerçek istek | Gerçek bir uygulamayı, tarayıcıda betik çalışmasını, Jinja2 gibi motorlarda kod çalıştırmayı ya da Juice Shop'u göstermez |
| Python `str.format` kullanıcıdan gelen şablonda nesne özniteliğine ve sözlük anahtarına erişebilir | `/vulnerable/selam` kullanıcı şablonunu `format` ile işler | Bu, kod çalıştıran bir SSTI değildir; veri sızdıran bir **biçim dizisi enjeksiyonu**dur |
| Dış varlıkları açan XML ayrıştırıcı yerel dosya okuyabilir | `xml.sax` dış genel varlık özelliği **bilerek** açık (Python'da varsayılan kapalı) | Ağ üzerinden SSRF ya da "billion laughs" gibi XXE türlerini göstermez |

> [!NOT]
> İlk üç görev `web/ornekler.json` dosyasını okur; girdiler **sentetiktir**, hiçbir sunucuya gönderilmez. Setup her Çalıştır/Kontrol Et adımında eksik dosyaları kopyalar; **kalıcılık yoktur**. Dosyayı görmek için başlangıç kodundaki `print` satırlarını kullan. Son görev yalnız kendi açtığı sunucuya bağlanır; okunan "gizli dosya" o koşuda geçici klasörde üretilmiş rastgele bir değerdir. Koşu sonunda sunucu ve klasör kapanır. Dış hedef, gerçek hesap, paket ya da indirme yoktur.

**Kök neden: veri ile kodu karıştırmak.** pu19'da SQL metnine eklenen girdi sorgunun parçası oldu. Burada aynı hata üç yerde tekrar eder. **Yansıyan XSS:** arama kutusuna yazılan metin HTML'e ham konur; `<b id="...">` gibi bir etiket sayfanın parçası olur. Tarayıcıda bu, saldırganın betiğinin kurbanın oturumunda çalışması demektir. **Şablon enjeksiyonu:** uygulama kullanıcının yazdığı metni şablon olarak işler. Python'da `"{u.ayar[GIZLI]}".format(u=kullanici)` nesnenin özniteliğine ve sözlüğüne erişir; gizli ayar yanıta düşer. **XXE:** XML ayrıştırıcı, belgenin DTD'sinde tanımlanan bir dış varlığı (`SYSTEM "file:..."`) açarsa sunucunun yerel dosyası yanıta karışır.

**Saldırgan ne dener?** Girdiyi, uygulamanın onu **yorumladığı** bir bağlama sokmaya çalışır: HTML etiketi, şablon alanı, DTD bildirimi. Filtreleri aşmak için de kodlamayı değiştirir (UTF-16 XML), ayracı kaçışlar (`{{`), yorum ya da CDATA içine saklanmış gibi görünen yazılar kullanır.

**Savunma neden kırılır?** Çünkü sık sık metin aranır: "içinde `<script>` var mı", "`{` sonrası bir kelime var mı", "baytlarda `<!ENTITY` geçiyor mu". Bu aramalar kodlamayı, sırayı ve sözdizimini bilmez. Doğru düzeltme bağlamın kendi kuralıyla çalışır. **XSS:** çıktı HTML'e girerken beş karakteri kaçışla (`&` önce). **Şablon:** kullanıcı girdisini şablon olarak işleme. İşlemek zorundaysan Python'un kendi ayrıştırıcısıyla alanları çöz ve yalnız izinli, düz adlara izin ver. **XXE:** DTD içeren belgeyi reddet; ayrıştırıcının olaylarına güven, baytlara değil.

**Blue karşılığı.** Sunucu her isteği denetim kaydına yazar. Kayıt, yanıtın gizli değeri sızdırıp sızdırmadığını da tutar. Bir WAF ya da log kuralı "girdide `<`, `{u.`, `<!DOCTYPE` var" diye uyarı üretebilir, ama yanlış alarmı da çoktur: "Ali <3" meşru bir aramadır. Asıl kanıt, açık ve korumalı ucun aynı girdiye verdiği farklı yanıttır.

Kaynaklar: [OWASP · Cross Site Scripting Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html), [OWASP · XML External Entity Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html), [Python · Format String Syntax](https://docs.python.org/3/library/string.html#format-string-syntax), [Python · XML vulnerabilities](https://docs.python.org/3/library/xml.html#xml-vulnerabilities). Bu dersteki bütün sayılar yalnız yerel kanıttan gelir.

Purple bağı: pu11 web savunmasını anlatır, pu19 aynı kök nedeni SQL'de gerçek HTTP ile kanıtlar; bu ders onu HTML, şablon ve XML bağlamlarına taşır. pu20 aynı tür kanıtı rapora çevirir.
:::

::: tahmin Sıra ve öznitelik
Çıktıyı tahmin et, sonra Çalıştır ile karşılaştır.
```python
s = "<b>&lt;"
print(s.replace("<", "&lt;").replace("&", "&amp;"))
print(s.replace("&", "&amp;").replace("<", "&lt;"))
print("{u.ad}".format(u=type("K", (), {"ad": "Deniz"})))
```
???
```cikti
&amp;lt;b>&amp;lt;
&lt;b>&amp;lt;
Deniz
```
Tahmininle gerçek çıktı arasındaki farkı tezgâhta yorum satırı olarak yaz: ilk satırda `<` neden iki kez kaçışlandı? Üçüncü satırda şablon nesnenin özniteliğine nasıl ulaştı? Sonra üç kusurlu başlangıç kodunu çalıştır. Hangisi `&`'yi en sona bırakıp tırnakları kaçışlamıyor, hangisi düzenli ifadeyle `{u.ayar[...]}`'nın yalnız başını görüp `{{ad}}`'ı alan sanıyor, hangisi baytlarda `<!ENTITY` arayıp dış DTD'yi, UTF-16'yı ve yorumu yanlış değerlendiriyor? Önce kendin teşhis et; açıklama çözümün ardından gelir.
:::

::: gorev 1 · HTML çıktısını kaçışla
`guvenli_html(metin)`: `metin` string olmalı; değilse `ValueError`. Beş karakteri HTML varlıklarına çevir: `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`, `"` → `&quot;`, `'` → `&#x27;`. Diğer bütün karakterler (Türkçe harfler, emoji, satır sonu) aynen kalır. Girdideki `&lt;` gibi hazır bir varlık da **metindir**; o da kaçışlanır (`&amp;lt;`). Bu görevde `html` modülü kullanılmaz; gerçek uygulamada `html.escape` ya da şablon motorunun otomatik kaçışı kullanılır.

```starter
# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def guvenli_html(metin):
    return metin.replace("<","&lt;").replace(">","&gt;").replace("&","&amp;")

import json
from pathlib import Path
v=json.loads(Path("web/ornekler.json").read_text(encoding="utf-8"))
for m in v["html"]:print(repr(m),"→",repr(guvenli_html(m)))
```

```solution
def guvenli_html(metin):
    if not isinstance(metin,str):raise ValueError("metin")
    return metin.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;").replace("'","&#x27;")

import json
from pathlib import Path
v=json.loads(Path("web/ornekler.json").read_text(encoding="utf-8"))
for m in v["html"]:print(repr(m),"→",repr(guvenli_html(m)))
```

```test
need('guvenli_html')
def sinama1(f):
    try:
        V=[("",""),("düz metin","düz metin"),("a&b","a&amp;b"),("<","&lt;"),(">","&gt;"),("&lt;","&amp;lt;"),("<a href=\"x\">'</a>","&lt;a href=&quot;x&quot;&gt;&#x27;&lt;/a&gt;"),
           ("Ayşe & Ali <3","Ayşe &amp; Ali &lt;3"),("\"'\"","&quot;&#x27;&quot;"),("&amp;amp;","&amp;amp;amp;"),("<<>>","&lt;&lt;&gt;&gt;"),("🙂&","🙂&amp;"),("x\n<y>","x\n&lt;y&gt;")]
        for g,b in V:
            if f(g)!=b:return False
        for bad in (None,b"<",5,["<"]):
            try:f(bad);return False
            except ValueError:pass
        return True
    except Exception:return False
ok(sinama1(guvenli_html),"beş karakter, & önce, Unicode korunur, geçersiz girdi")
for ad,mut in [("tek tırnak kaçışlanmıyor",lambda m:guvenli_html(m).replace("&#x27;","'")),("çift tırnak kaçışlanmıyor",lambda m:guvenli_html(m).replace("&quot;",'"')),("& en son",lambda m:guvenli_html(m).replace("&amp;lt;","&lt;").replace("&amp;gt;","&gt;"))]:
    ok(not sinama1(mut),"mutant reddedildi: "+ad)
```

```setup
import sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_web_lab import hazirla
hazirla()
```

```hint
Sıra önemli: önce `&`. Sonra eklenen `&lt;` içindeki `&` tekrar kaçışlanmamalı.
```
:::

::: anlat Şablon bir programdır
Kullanıcıya şablon yazdırmak, ona küçük bir programlama dili vermektir. Python'un `str.format` dili bile nokta ile özniteliğe, köşeli parantezle anahtara, `!r` ile `repr`'a erişir. Jinja2 gibi motorlarda aynı kapı kod çalıştırmaya kadar gider. Bu yüzden ilk tercih kullanıcı girdisini **değer** olarak vermektir, şablon olarak değil. Ürün gereği şablon kabul edilecekse izinli alan listesi dar tutulur ve her alan dilin kendi ayrıştırıcısıyla denetlenir.
:::

::: gorev 2 · Şablon alanlarını doğrula
`sablon_dogrula(sablon, izinli)`: `sablon` string; `izinli` string'lerden oluşan liste ya da demet. Aksi hâlde `ValueError`. `string.Formatter().parse` ile şablonu çöz (bozuk şablonda bu çağrı `ValueError` verir). Her alan adı `izinli` içinde **birebir** bulunmalı; nokta, köşeli parantez, boş ya da sayı alanı izinli değildir. Dönüşüm (`!r`, `!s`) ve biçim belirteci (`:>10`) olan alan reddedilir; boş belirteç (`{ad:}`) zararsızdır. `{{` ve `}}` alan değil, düz metindir. Kurallardan biri bozulursa `ValueError`. Kullanılan alan adlarını tekrarsız ve sıralı liste olarak döndür.

```starter
import re
# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def sablon_dogrula(sablon,izinli):
    alanlar=re.findall(r"\{(\w+)",sablon)
    for a in alanlar:
        if a not in izinli:raise ValueError("izinsiz alan: "+a)
    return alanlar

import json
from pathlib import Path
v=json.loads(Path("web/ornekler.json").read_text(encoding="utf-8"))
for s,i in v["sablonlar"]:
    try:print(repr(s),"→",sablon_dogrula(s,i))
    except ValueError as e:print(repr(s),"→ ValueError:",e)
```

```solution
from string import Formatter
def sablon_dogrula(sablon,izinli):
    if not isinstance(sablon,str) or not isinstance(izinli,(list,tuple)) or any(not isinstance(a,str) for a in izinli):raise ValueError("tür")
    alanlar=set()
    for _,ad,bicim,donusum in Formatter().parse(sablon):
        if ad is None:continue
        if ad not in izinli or bicim or donusum:raise ValueError("izinsiz alan: "+repr(ad))
        alanlar.add(ad)
    return sorted(alanlar)

import json
from pathlib import Path
v=json.loads(Path("web/ornekler.json").read_text(encoding="utf-8"))
for s,i in v["sablonlar"]:
    try:print(repr(s),"→",sablon_dogrula(s,i))
    except ValueError as e:print(repr(s),"→ ValueError:",e)
```

```test
need('sablon_dogrula')
def sinama2(f):
    try:
        V=[(("Merhaba {ad}!",("ad",)),["ad"]),(("{{ad}} {ad}",["ad"]),["ad"]),(("{soyad}{ad}{soyad}",("ad","soyad")),["ad","soyad"]),(("sabit",("ad",)),[]),(("",["ad"]),[]),
           (("{{{ad}}}",("ad",)),["ad"]),(("{ad:}",("ad",)),["ad"]),(("{{}}",()),[]),(("{ad}",["ad","x"]),["ad"])]
        for a,b in V:
            if f(*a)!=b:return False
        for s,i in (("{u.ayar[GIZLI]}",("ad",)),("{ad.__class__}",("ad",)),("{ad[0]}",("ad",)),("{ad!r}",("ad",)),("{ad!s}",("ad",)),("{ad:>10}",("ad",)),("{ad:{ad}}",("ad",)),
                    ("{}",("ad",)),("{0}",("ad",)),("{ad",("ad",)),("}",("ad",)),("{soyad}",("ad",)),("{Ad}",("ad",)),("{ad}",()),(None,("ad",)),(5,("ad",)),("{ad}","ad"),("{ad}",None),("{ad}",[1]),("{ad}",{"ad"})):
            try:f(s,i);return False
            except ValueError:pass
        return True
    except Exception:return False
ok(sinama2(sablon_dogrula),"izinli basit alanlar, kaçışlı süslü parantez, öznitelik/indeks/dönüşüm/biçim reddi, bozuk şablon")
def _bos(s,i):
    try:return sablon_dogrula(s,i)
    except ValueError:return []
for ad,mut in [("izinsiz alanda boş liste",_bos),("sırasız",lambda s,i:list(reversed(sablon_dogrula(s,i)))),("tekrarlı",lambda s,i:sablon_dogrula(s,i)+sablon_dogrula(s,i)[:1])]:
    ok(not sinama2(mut),"mutant reddedildi: "+ad)
```

```setup
import sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_web_lab import hazirla
hazirla()
```

```hint
Düzenli ifade `{{ad}}`'ı alan sanır, `{u.ayar[...]}`'nın yalnız başını görür. Python'un kendi ayrıştırıcısını kullan.
```
:::

::: anlat DTD'yi neden tümden reddederiz?
XXE'nin yolu DTD'den geçer: dış varlık, dış DTD, parametre varlıkları ve iç içe varlıklar. Uygulamanın gerçekten DTD'ye ihtiyacı yoksa (çoğu API'nin yoktur) en sağlam kural "DTD varsa reddet"tir. Bu karar baytlara bakarak değil, ayrıştırıcının "DOCTYPE başladı" olayıyla verilir. Böylece UTF-16 ile kodlanmış bir belge de, yorumun içine yazılmış masum bir metin de doğru değerlendirilir. Python'da `xml.sax` dış genel varlıkları 3.7.1'den beri varsayılan olarak açmaz. Bu labdaki açık uç bu korumayı **bilerek** kapatır.
:::

::: gorev 3 · XML'de DTD var mı?
`dtd_var_mi(belge)`: `belge` `bytes` olmalı (str ya da `bytearray` değil); değilse `ValueError`. `xml.parsers.expat.ParserCreate()` ile bir ayrıştırıcı kur; `StartDoctypeDeclHandler` işleyicisini ata ve belgeyi tek seferde ayrıştır (`Parse(belge, True)`). Belge bozuksa (`ExpatError`) `ValueError`. Bir DOCTYPE bildirimi görüldüyse (varlık bildirimleri yalnız DOCTYPE içinde olabilir) `True`, aksi hâlde `False` döndür. Belgenin kodlamasını (UTF-8, UTF-16) ayrıştırıcı çözer; yorum ya da CDATA içindeki `<!ENTITY` yazısı bildirim değildir. Bu işlev hiçbir dış kaynağı açmaz.

```starter
# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def dtd_var_mi(belge):
    return b"<!ENTITY" in belge

import json
from pathlib import Path
v=json.loads(Path("web/ornekler.json").read_text(encoding="utf-8"))
for x in v["xml"]:
    try:print(repr(x),"→",dtd_var_mi(x.encode("utf-8")))
    except ValueError as e:print(repr(x),"→ ValueError:",e)
```

```solution
import xml.parsers.expat
def dtd_var_mi(belge):
    if not isinstance(belge,bytes):raise ValueError("bayt")
    p=xml.parsers.expat.ParserCreate();bulundu=[]
    p.StartDoctypeDeclHandler=lambda *a:bulundu.append("doctype")
    try:p.Parse(belge,True)
    except xml.parsers.expat.ExpatError as e:raise ValueError("bozuk XML: "+str(e))
    return bool(bulundu)

import json
from pathlib import Path
v=json.loads(Path("web/ornekler.json").read_text(encoding="utf-8"))
for x in v["xml"]:
    try:print(repr(x),"→",dtd_var_mi(x.encode("utf-8")))
    except ValueError as e:print(repr(x),"→ ValueError:",e)
```

```test
need('dtd_var_mi')
def sinama3(f):
    try:
        V=[(b"<siparis><urun>kalem</urun></siparis>",False),(b'<!DOCTYPE r [<!ENTITY x "y">]><r>&x;</r>',True),(b'<!DOCTYPE r SYSTEM "dis.dtd"><r/>',True),(b"<!DOCTYPE r><r/>",True),
           (b'<?xml version="1.0"?>\n<!DOCTYPE r [\n  <!ELEMENT r ANY>\n]>\n<r/>',True),(b"<r><!-- <!ENTITY sahte> --></r>",False),(b"<r><![CDATA[<!DOCTYPE x>]]></r>",False),
           ('<?xml version="1.0" encoding="UTF-16"?><!DOCTYPE r [<!ENTITY x "y">]><r>&x;</r>'.encode("utf-16"),True),('<?xml version="1.0" encoding="UTF-16"?><r>ç</r>'.encode("utf-16"),False),
           ("<r>ç</r>".encode("utf-8"),False),(b"<r a='&amp;'/>",False)]
        for g,b in V:
            if f(g) is not b:return False
        for bad in (b"<r>",b"",b"<r></x>",b"<!DOCTYPE r [<!ENTITY x 'y'>]><r>&z;</r>",b"<r>&x;</r>","<r/>",None,5,bytearray(b"<r/>")):
            try:f(bad);return False
            except ValueError:pass
        return True
    except Exception:return False
ok(sinama3(dtd_var_mi),"iç ve dış DTD, yorum/CDATA içi metin, UTF-16, bozuk XML")
def _yanlis(b):
    try:return dtd_var_mi(b)
    except ValueError:return False
for ad,mut in [("bozuk XML güvenli sayılıyor",_yanlis),("yalnız ENTITY",lambda b:dtd_var_mi(b) and b"ENTITY" in b),("ters karar",lambda b:not dtd_var_mi(b))]:
    ok(not sinama3(mut),"mutant reddedildi: "+ad)
```

```setup
import sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_web_lab import hazirla
hazirla()
```

```hint
Bayt içinde metin aramak UTF-16'yı ve dış DTD'yi kaçırır, yorumdaki yazıyı da bildirim sanır. Ayrıştırıcının olaylarına güven.
```
:::

::: anlat Hata vitrini · yazar koşusu
Yazar son görevi referans işlevlerle çalıştırdı; sunucu Python 3.13 ve expat 2.8.1 ile koştu.

- **Açık uçlar gerçekten açıktı.** `/vulnerable/ara` işaret etiketini ham döndürdü. `/vulnerable/selam` `{u.ayar[GIZLI]}` için o koşuda üretilen gizli ayarı yazdı. `/vulnerable/xml` dış varlıkla geçici klasördeki gizli dosyanın içeriğini döndürdü.
- **Korumalı uçlar durdurdu, meşruyu bozmadı.** `/secure/ara` aynı etiketi `&lt;b id=&quot;…` olarak gösterdi, "Ayşe & Ali <3" aramasını doğru kaçışladı. `/secure/selam` saldırı şablonuna 400 verdi, "Merhaba {ad}!"'e "Merhaba Deniz!" dedi. `/secure/xml` iki DTD'li belgeye (UTF-8 ve UTF-16) 400 verdi, meşru siparişi okudu.
- Denetim kaydında gizli değer **yalnız iki yanıtta** sızdı: açık şablon ucu ve açık XML ucu. XSS'in "sızıntısı" sunucuda değil tarayıcıda olur; bu yüzden XSS kanıtı yanıt gövdesindeki ham etikettir.

Kendi cümlenle açıkla: "girdide `<` var" diyen bir log kuralı, bu labdaki meşru "Ayşe & Ali <3" aramasında ne yapardı?
:::

::: gorev Gerçek deney · Yerel sunucuda üç açık, üç düzeltme
Üç işlevi birleştir. Alttaki `calistir` satırı gerçek deneyi başlatır; silme. Her koşu kendi `127.0.0.1` sunucusunu ve geçici klasöründe rastgele bir gizli dosya açar. Üç uç çifti vardır: `/vulnerable/ara` girdiyi HTML'e ham koyar, `/secure/ara` senin `guvenli_html`'inle; `/vulnerable/selam` kullanıcının şablonunu `str.format` ile işler, `/secure/selam` önce senin `sablon_dogrula`'nla denetler; `/vulnerable/xml` dış varlıkları açan bir SAX ayrıştırıcıyla okur, `/secure/xml` önce senin `dtd_var_mi`'nle denetler. Her çift için meşru ve saldırı girdisiyle on üç gerçek istek gönderilir; denetim kaydı her yanıtın gizli değer sızdırıp sızdırmadığını tutar. Run deneme kanıtı yazar, Check ayrıca kabul kanıtını yazar; yol stdout'ta görünür. Koşu yalnız kendi sunucusunu ve geçici klasörünü açar ve kapatır; dış hedef ya da indirme yoktur.

```starter
import re
import xml.parsers.expat
from string import Formatter
# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def guvenli_html(metin):
    return metin.replace("<","&lt;").replace(">","&gt;").replace("&","&amp;")

# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def sablon_dogrula(sablon,izinli):
    alanlar=re.findall(r"\{(\w+)",sablon)
    for a in alanlar:
        if a not in izinli:raise ValueError("izinsiz alan: "+a)
    return alanlar

# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def dtd_var_mi(belge):
    return b"<!ENTITY" in belge

from purple_web_lab import calistir
calistir(guvenli_html,sablon_dogrula,dtd_var_mi)
```

```solution
import re
import xml.parsers.expat
from string import Formatter
def guvenli_html(metin):
    if not isinstance(metin,str):raise ValueError("metin")
    return metin.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;").replace("'","&#x27;")

def sablon_dogrula(sablon,izinli):
    if not isinstance(sablon,str) or not isinstance(izinli,(list,tuple)) or any(not isinstance(a,str) for a in izinli):raise ValueError("tür")
    alanlar=set()
    for _,ad,bicim,donusum in Formatter().parse(sablon):
        if ad is None:continue
        if ad not in izinli or bicim or donusum:raise ValueError("izinsiz alan: "+repr(ad))
        alanlar.add(ad)
    return sorted(alanlar)

def dtd_var_mi(belge):
    if not isinstance(belge,bytes):raise ValueError("bayt")
    p=xml.parsers.expat.ParserCreate();bulundu=[]
    p.StartDoctypeDeclHandler=lambda *a:bulundu.append("doctype")
    try:p.Parse(belge,True)
    except xml.parsers.expat.ExpatError as e:raise ValueError("bozuk XML: "+str(e))
    return bool(bulundu)

from purple_web_lab import calistir
calistir(guvenli_html,sablon_dogrula,dtd_var_mi)
```

```test
need('guvenli_html');need('sablon_dogrula');need('dtd_var_mi')
from purple_web_lab import kod_koruma,calistir
ok(kod_koruma(src),'kaynak koruması: referans/dinamik kod/özel öznitelik yok')
if not kod_koruma(src):stop()
def sinama1(f):
    try:
        V=[("",""),("düz metin","düz metin"),("a&b","a&amp;b"),("<","&lt;"),(">","&gt;"),("&lt;","&amp;lt;"),("<a href=\"x\">'</a>","&lt;a href=&quot;x&quot;&gt;&#x27;&lt;/a&gt;"),
           ("Ayşe & Ali <3","Ayşe &amp; Ali &lt;3"),("\"'\"","&quot;&#x27;&quot;"),("&amp;amp;","&amp;amp;amp;"),("<<>>","&lt;&lt;&gt;&gt;"),("🙂&","🙂&amp;"),("x\n<y>","x\n&lt;y&gt;")]
        for g,b in V:
            if f(g)!=b:return False
        for bad in (None,b"<",5,["<"]):
            try:f(bad);return False
            except ValueError:pass
        return True
    except Exception:return False
def sinama2(f):
    try:
        V=[(("Merhaba {ad}!",("ad",)),["ad"]),(("{{ad}} {ad}",["ad"]),["ad"]),(("{soyad}{ad}{soyad}",("ad","soyad")),["ad","soyad"]),(("sabit",("ad",)),[]),(("",["ad"]),[]),
           (("{{{ad}}}",("ad",)),["ad"]),(("{ad:}",("ad",)),["ad"]),(("{{}}",()),[]),(("{ad}",["ad","x"]),["ad"])]
        for a,b in V:
            if f(*a)!=b:return False
        for s,i in (("{u.ayar[GIZLI]}",("ad",)),("{ad.__class__}",("ad",)),("{ad[0]}",("ad",)),("{ad!r}",("ad",)),("{ad!s}",("ad",)),("{ad:>10}",("ad",)),("{ad:{ad}}",("ad",)),
                    ("{}",("ad",)),("{0}",("ad",)),("{ad",("ad",)),("}",("ad",)),("{soyad}",("ad",)),("{Ad}",("ad",)),("{ad}",()),(None,("ad",)),(5,("ad",)),("{ad}","ad"),("{ad}",None),("{ad}",[1]),("{ad}",{"ad"})):
            try:f(s,i);return False
            except ValueError:pass
        return True
    except Exception:return False
def sinama3(f):
    try:
        V=[(b"<siparis><urun>kalem</urun></siparis>",False),(b'<!DOCTYPE r [<!ENTITY x "y">]><r>&x;</r>',True),(b'<!DOCTYPE r SYSTEM "dis.dtd"><r/>',True),(b"<!DOCTYPE r><r/>",True),
           (b'<?xml version="1.0"?>\n<!DOCTYPE r [\n  <!ELEMENT r ANY>\n]>\n<r/>',True),(b"<r><!-- <!ENTITY sahte> --></r>",False),(b"<r><![CDATA[<!DOCTYPE x>]]></r>",False),
           ('<?xml version="1.0" encoding="UTF-16"?><!DOCTYPE r [<!ENTITY x "y">]><r>&x;</r>'.encode("utf-16"),True),('<?xml version="1.0" encoding="UTF-16"?><r>ç</r>'.encode("utf-16"),False),
           ("<r>ç</r>".encode("utf-8"),False),(b"<r a='&amp;'/>",False)]
        for g,b in V:
            if f(g) is not b:return False
        for bad in (b"<r>",b"",b"<r></x>",b"<!DOCTYPE r [<!ENTITY x 'y'>]><r>&z;</r>",b"<r>&x;</r>","<r/>",None,5,bytearray(b"<r/>")):
            try:f(bad);return False
            except ValueError:pass
        return True
    except Exception:return False
tamam=sinama1(guvenli_html) and sinama2(sablon_dogrula) and sinama3(dtd_var_mi)
ok(tamam,"üç savunma işlevi gizli verilerle doğru")
for ad,mut in [("tek tırnak kaçışlanmıyor",lambda m:guvenli_html(m).replace("&#x27;","'")),("çift tırnak kaçışlanmıyor",lambda m:guvenli_html(m).replace("&quot;",'"')),("& en son",lambda m:guvenli_html(m).replace("&amp;lt;","&lt;").replace("&amp;gt;","&gt;"))]:
    ok(not sinama1(mut),"mutant reddedildi: "+ad)
def _bos(s,i):
    try:return sablon_dogrula(s,i)
    except ValueError:return []
for ad,mut in [("izinsiz alanda boş liste",_bos),("sırasız",lambda s,i:list(reversed(sablon_dogrula(s,i)))),("tekrarlı",lambda s,i:sablon_dogrula(s,i)+sablon_dogrula(s,i)[:1])]:
    ok(not sinama2(mut),"mutant reddedildi: "+ad)
def _yanlis(b):
    try:return dtd_var_mi(b)
    except ValueError:return False
for ad,mut in [("bozuk XML güvenli sayılıyor",_yanlis),("yalnız ENTITY",lambda b:dtd_var_mi(b) and b"ENTITY" in b),("ters karar",lambda b:not dtd_var_mi(b))]:
    ok(not sinama3(mut),"mutant reddedildi: "+ad)
if not tamam:stop()
k=calistir(guvenli_html,sablon_dogrula,dtd_var_mi,kabul=True)
eq(k['kaynak'],'gercek','gerçek yerel HTTP sunucusu')
ok(k['kabul'],'gerçek kabul: açık uçlar sızdırdı, korumalı uçlar durdurdu, meşru istekler çalıştı')
ok(k['cleanup'],'yalnız kendi sunucusu ve geçici dosyası kapandı')
ok(not any(d['gizli_sizdi'] for d in k['denetim'] if d['route'].startswith('/secure/')),'korumalı uçlardan gizli değer sızmadı')
eq(sum(d['gizli_sizdi'] for d in k['denetim']),2,'gizli değerler yalnız açık şablon ve açık XML uçlarından sızdı')
```

```setup
import sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_web_lab import hazirla
hazirla()
```

```hint
Önceki üç işlevi aynen birleştir. Kanıtta `xml-utf16-korumali` yanıtına bak: kusurlu başlangıç kodu bunu neden geçirirdi?
```
:::

::: anlat Sınır
Bu ders kendi yerel sunucusunda yansıyan XSS, Python `str.format` şablon enjeksiyonu ve dosya okuyan XXE'yi gerçek HTTP yanıtları ve denetim kaydıyla gösterir ve düzeltir; tarayıcıda betik çalışmasını, Jinja2 gibi motorlarda kod çalıştırmayı, kayıtlı/DOM XSS'i, XXE ile SSRF'yi ve gerçek uygulamaları kapsamaz.
:::
