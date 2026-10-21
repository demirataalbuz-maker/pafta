---
id: ht11
title: Formlar
summary: Formun action, method ve enctype öznitelikleri; GET formunun sorguya, POST formunun gövdeye yazması; hangi denetimlerin gönderildiği (name, disabled, işaretsiz checkbox, select, textarea, tıklanan düğme) ve sırası; istemci tarafı denetimin koruma olmaması ve form jetonları.
---

::: anlat Bir form neyi gönderir?
Tezgahın bilet formu (`GET /bilet-ac`):

```html
<form action="/bilet-ac" method="post">
  <input type="hidden" name="form_kodu" value="fk-1029">
  <label>Başlık <input type="text" name="baslik" required maxlength="80"></label>
  <label>Öncelik
    <select name="oncelik">
      <option value="düşük">Düşük</option>
      <option value="orta" selected>Orta</option>
      <option value="yüksek">Yüksek</option>
      <option value="kritik">Kritik</option>
    </select>
  </label>
  <label>Kaynak <input type="text" name="kaynak" value="web" disabled></label>
  <label><input type="checkbox" name="acil" value="evet"> Acil</label>
  <textarea name="aciklama" rows="3"></textarea>
  <button type="submit" name="islem" value="kaydet">Kaydet</button>
</form>
```

| Öznitelik | Anlamı | Yoksa |
|---|---|---|
| `action` | nereye gönderilecek; göreli olabilir (sayfanın adresine göre çözülür, HT02) | sayfanın kendi adresi |
| `method` | `get`: alanlar **sorguya** (`?baslik=...`); `post`: alanlar **gövdeye** | `get` |
| `enctype` | gövdenin biçimi: `application/x-www-form-urlencoded`, dosyalar için `multipart/form-data` | `application/x-www-form-urlencoded` |

Tarayıcı formu gönderirken denetimleri **belgedeki sırayla** dolaşır ve her biri için şu kurala bakar:

| Denetim | Gönderilir mi | Değer |
|---|---|---|
| `name`'i olmayan | hayır | |
| `disabled` | **hayır** | |
| `text`, `password`, `hidden`, `textarea`, `readonly` | evet, **boş olsa bile** | yazılan metin ya da `value` |
| `checkbox`, `radio` | **yalnızca işaretliyse** | `value`; `value` yoksa `on` |
| `select` | evet | seçilen `option`'ın `value`'su (yoksa metni); hiçbiri seçilmemişse ilk seçenek |
| düğme (`button`, `type="submit"`) | yalnızca **tıklanan** ve `name`'i olan | `value` |

Aynı ad birden çok kez geçebilir: `etiket=web&etiket=prod`.
:::

::: anlat İstemci tarafı denetim bir koruma değildir
`required`, `maxlength="80"`, `pattern`, `type="email"`, `disabled` ve gizli alanlar **tarayıcının** uyguladığı kolaylıklardır. Ham bir istek bunların hiçbirini görmez:

```python
from urllib.parse import urlencode
import tezgah

govde = urlencode({"form_kodu": "fk-1029", "baslik": "x" * 90, "kaynak": "elle"})
y = tezgah.yanit(f"POST /bilet-ac HTTP/1.1\r\nHost: pafta.test\r\nContent-Type: application/x-www-form-urlencoded\r\n"
                 f"Content-Length: {len(govde)}\r\n\r\n{govde}")
print(y.durum)                     #! maxlength=80 aşıldı; sunucu kendi kuralıyla reddediyor
```

Tarayıcı 80 karakterden uzun yazdırmazdı, devre dışı `kaynak` alanını göndermezdi; ham istekte ikisi de gitti. Sunucu başlığı kendi kuralıyla yeniden denetlediği için 422 döndü. Denetimi yalnızca formda yapan bir sunucu bu isteği kabul ederdi.

> [!GÜVENLİK]
> Sunucu her alanı **yeniden** doğrulamalı: tür, uzunluk, izinli değerler ve bu kullanıcının bu işlemi yapmaya yetkisi. Gizli ya da devre dışı bir alanın değerine güvenilmez; kullanıcı onu değiştirebilir. Durum değiştiren formlar oturuma bağlı, tahmin edilemez bir **form jetonu** taşır (`form_kodu` gibi) ve sunucu her gönderimde jetonu doğrular; böylece başka bir sitenin kullanıcı adına form göndermesi engellenir. Tezgahtaki jeton sabittir ve denetlenmez, yalnızca kalıbı göstermek içindir.
:::

::: tahmin
Kuralları bir listeye uygulayan kısa bir kod. Ne yazar?

```python
from urllib.parse import urlencode

# (ad, tür, değer, devre_dışı, işaretli)
denetimler = [
    ("q", "text", "disk dolu", False, None),
    ("sayfa", "hidden", "1", True, None),
    ("acik", "checkbox", "on", False, True),
    ("kritik", "checkbox", "evet", False, False),
    ("", "text", "x", False, None),
    ("rol", "select", "web", False, None),
]
gonderilen = [(ad, deger) for ad, tur, deger, kapali, isaretli in denetimler
              if ad and not kapali and (tur != "checkbox" or isaretli)]
print("/sonuc?" + urlencode(gonderilen))
```

???

`/sonuc?q=disk+dolu&acik=on&rol=web`. Devre dışı `sayfa` gönderilmez, işaretsiz `kritik` gönderilmez, adı olmayan alan gönderilmez. İşaretli `acik` kutusunun `value`'su yoktu, bu yüzden değeri `on`'dur. Alanlar belgedeki sırayla dizilir ve `q`'daki boşluk sorguda `+` olur.
:::

::: gorev Formun özeti
`form_ozeti(html, sayfa_url)` fonksiyonu kaynaktaki **ilk** formun `(yontem, adres, enctype)` üçlüsünü döndürsün:

- `yontem` büyük harfle (`GET` ya da `POST`); `method` yoksa `GET`
- `adres`: `action` sayfa adresine göre çözülmüş mutlak adres; `action` yoksa ya da boşsa `sayfa_url`
- `enctype` yoksa `application/x-www-form-urlencoded`

```starter
def form_ozeti(html, sayfa_url):
    return ("POST", sayfa_url, "")
```

```test
import tezgah
need("form_ozeti")
html = tezgah.yanit("GET /bilet-ac HTTP/1.1\r\nHost: pafta.test\r\n\r\n").govde
eq(form_ozeti(html, "http://pafta.test/bilet-ac"),
   ("POST", "http://pafta.test/bilet-ac", "application/x-www-form-urlencoded"), "bilet formu")
eq(form_ozeti('<form action="sonuc"><input name="q"></form>', "http://pafta.test/rapor/ara.html"),
   ("GET", "http://pafta.test/rapor/sonuc", "application/x-www-form-urlencoded"), "varsayılan GET, göreli action")
eq(form_ozeti('<FORM METHOD=Post ACTION="" ENCTYPE="multipart/form-data">', "http://pafta.test/yukle"),
   ("POST", "http://pafta.test/yukle", "multipart/form-data"), "boş action, büyük harfli öznitelikler")
eq(form_ozeti('<form id="a" action="/bir" method="get"></form><form action="/iki" method="post"></form>', "http://pafta.test/"),
   ("GET", "http://pafta.test/bir", "application/x-www-form-urlencoded"), "yalnızca ilk form")
eq(form_ozeti("<form>", "http://pafta.test/x?y=1"),
   ("GET", "http://pafta.test/x?y=1", "application/x-www-form-urlencoded"), "hiç öznitelik yok")
```

```solution
from html.parser import HTMLParser
from urllib.parse import urljoin


class _Ilk(HTMLParser):
    def __init__(self):
        super().__init__()
        self.oz = None

    def handle_starttag(self, etiket, oznitelikler):
        if etiket == "form" and self.oz is None:
            self.oz = dict(oznitelikler)


def form_ozeti(html, sayfa_url):
    p = _Ilk()
    p.feed(html)
    oz = p.oz or {}
    yontem = (oz.get("method") or "get").upper()
    adres = urljoin(sayfa_url, oz.get("action") or "") if oz.get("action") else sayfa_url
    enctype = oz.get("enctype") or "application/x-www-form-urlencoded"
    return (yontem, adres, enctype)
```

```hint
İlk `<form>` etiketinin özniteliklerini `dict(oznitelikler)` ile sakla ve sonrakileri yok say. `oz.get("method") or "get"` hem yokluğu hem boşluğu karşılar.
```
:::

::: gorev Ne gönderilecek?
`gonderilecekler(html, doldur)` fonksiyonu kaynaktaki ilk formu, kullanıcının doldurduklarıyla birlikte bir tarayıcı gibi gönderseydin gidecek `(ad, değer)` çiftlerini **belgedeki sırayla** bir liste olarak döndürsün. `doldur` bir sözlük:

- metin alanları ve `textarea` için yazılan metin (yoksa `value` özniteliği ya da `textarea`'nın içeriği, o da yoksa `""`)
- `checkbox` için `True` ya da `False` (yoksa kutunun `checked` özniteliği belirler)
- `select` için seçilen değer (yoksa `selected` seçenek, o da yoksa ilk seçenek)
- `"__dugme"`: tıklanan düğmenin `name`'i (yoksa hiçbir düğme gönderilmez)

Kurallar anlatımdaki tablodaki gibi: `name`'i olmayan ve `disabled` olan gönderilmez; işaretli kutunun değeri `value`, `value` yoksa `on`; `option`'ın `value`'su yoksa metni.

```starter
def gonderilecekler(html, doldur):
    return list(doldur.items())
```

```test
import tezgah
need("gonderilecekler")
form = tezgah.yanit("GET /bilet-ac HTTP/1.1\r\nHost: pafta.test\r\n\r\n").govde
eq(gonderilecekler(form, {"baslik": "Ağ yavaş", "__dugme": "islem"}),
   [("form_kodu", "fk-1029"), ("baslik", "Ağ yavaş"), ("oncelik", "orta"), ("aciklama", ""), ("islem", "kaydet")],
   "bilet formu: varsayılan seçenek, boş textarea, devre dışı ve işaretsiz alan yok, tıklanan düğme")
eq(gonderilecekler(form, {"baslik": "x", "oncelik": "kritik", "acil": True, "aciklama": "a"}),
   [("form_kodu", "fk-1029"), ("baslik", "x"), ("oncelik", "kritik"), ("acil", "evet"), ("aciklama", "a")],
   "işaretli kutu, seçilen değer; düğmeye tıklanmadı")
ornek = """<form>
  <input name="q" value="disk">
  <input value="adsız">
  <input type="checkbox" name="bir" checked>
  <input type="checkbox" name="iki" value="2" checked>
  <select name="rol"><option>web</option><option value="db">Veritabanı</option></select>
  <textarea name="not">  merhaba  </textarea>
  <input type="submit" name="git" value="Ara">
</form>"""
eq(gonderilecekler(ornek, {}),
   [("q", "disk"), ("bir", "on"), ("iki", "2"), ("rol", "web"), ("not", "  merhaba  ")],
   "value'suz kutu on, seçimsiz select ilk seçenek (metni), textarea içeriği olduğu gibi")
eq(gonderilecekler(ornek, {"iki": False, "rol": "db", "__dugme": "git"}),
   [("q", "disk"), ("bir", "on"), ("rol", "db"), ("not", "  merhaba  "), ("git", "Ara")],
   "kullanıcı kutuyu kaldırdı; submit girdisi tıklandı")
eq(gonderilecekler("<form><input name='a' disabled><input name='b' type='hidden'></form>", {"a": "x"}),
   [("b", "")], "devre dışı alan doldurulsa da gitmez; değersiz gizli alan boş gider")
eq(gonderilecekler('<form><select name="k" disabled><option>1</option></select><select><option>2</option></select>'
                   '<select name="bos"></select><textarea name="t" disabled>x</textarea><textarea>y</textarea></form>', {}),
   [], "devre dışı ya da adsız select/textarea ve seçeneksiz select gitmez")
eq(gonderilecekler('<form><select name="r"><optgroup label="Ön yüz"><option>web</option></optgroup>'
                   '<optgroup label="Arka"><option selected>db</option></optgroup></select></form>', {}),
   [("r", "db")], "optgroup içindeki seçenekler")
eq(gonderilecekler('<form><input name="sehir" list="s"><datalist id="s"><option value="İzmir"></datalist>'
                   '</select></textarea><input name="a" value="1"></form>', {}),
   [("sehir", ""), ("a", "1")], "select dışındaki option ve fazladan bitiş etiketleri çökertmez")
```

```solution
from html.parser import HTMLParser

METIN = {"text", "password", "hidden", "email", "search", "number", "tel", "url"}
DUGME = {"submit", "button"}


class _Form(HTMLParser):
    def __init__(self, doldur):
        super().__init__()
        self.doldur = doldur
        self.ciftler = []
        self.formda = False
        self.bitti = False
        self.select = None
        self.secenek = None
        self.textarea = None

    def handle_starttag(self, etiket, oznitelikler):
        oz = dict(oznitelikler)
        if self.bitti:
            return
        if etiket == "form":
            self.formda = True
            return
        if not self.formda:
            return
        ad = oz.get("name")
        kapali = "disabled" in oz
        if etiket == "input":
            tur = (oz.get("type") or "text").lower()
            if not ad or kapali:
                return
            if tur == "checkbox" or tur == "radio":
                isaretli = self.doldur.get(ad, "checked" in oz)
                if isaretli:
                    self.ciftler.append((ad, oz.get("value") or "on"))
            elif tur in DUGME:
                if self.doldur.get("__dugme") == ad:
                    self.ciftler.append((ad, oz.get("value") or ""))
            elif tur in METIN:
                self.ciftler.append((ad, self.doldur.get(ad, oz.get("value") or "")))
        elif etiket == "button":
            if ad and not kapali and self.doldur.get("__dugme") == ad:
                self.ciftler.append((ad, oz.get("value") or ""))
        elif etiket == "select":
            self.select = {"ad": ad, "kapali": kapali, "secenekler": [], "secili": None}
        elif etiket == "option" and self.select is not None:
            self.secenek = {"deger": oz.get("value"), "metin": ""}
            self.select["secenekler"].append(self.secenek)
            if "selected" in oz:
                self.select["secili"] = self.secenek
        elif etiket == "textarea":
            self.textarea = {"ad": ad, "kapali": kapali, "metin": ""}

    def handle_data(self, veri):
        if self.secenek is not None:
            self.secenek["metin"] += veri
        elif self.textarea is not None:
            self.textarea["metin"] += veri

    def handle_endtag(self, etiket):
        if etiket == "option":
            self.secenek = None
        elif etiket == "select" and self.select is not None:
            s, self.select, self.secenek = self.select, None, None
            if s["ad"] and not s["kapali"] and s["secenekler"]:
                secili = s["secili"] or s["secenekler"][0]
                varsayilan = secili["deger"] if secili["deger"] is not None else secili["metin"].strip()
                self.ciftler.append((s["ad"], self.doldur.get(s["ad"], varsayilan)))
        elif etiket == "textarea" and self.textarea is not None:
            t, self.textarea = self.textarea, None
            if t["ad"] and not t["kapali"]:
                self.ciftler.append((t["ad"], self.doldur.get(t["ad"], t["metin"])))
        elif etiket == "form" and self.formda:
            self.formda = False
            self.bitti = True


def gonderilecekler(html, doldur):
    f = _Form(doldur)
    f.feed(html)
    return f.ciftler
```

```hint
Üç tür denetim farklı zamanda "biter": `input` başlangıç etiketinde tamdır; `select` ve `textarea` ise içerikleri okunduktan sonra, **bitiş** etiketlerinde karara bağlanır. `select` için seçenekleri bir listede topla, `</select>`'te seçileni bul.
```

```hint
Kutular için: `doldur.get(ad, "checked" in oz)` kullanıcı bir şey söylemediyse varsayılanı kullanır. Düğmeler için: `doldur.get("__dugme") == ad`.
```
:::

::: gorev İsteği kur
`form_istegi(yontem, yol, ciftler)` fonksiyonu bir formun göndereceği ham isteği (`Host: pafta.test`) **metin** olarak döndürsün:

- `GET`: çiftler `urlencode` ile sorguya yazılır (`yol?a=1&b=2`); çift yoksa `?` de yok; gövde yok
- `POST`: çiftler gövdeye yazılır; `Content-Type: application/x-www-form-urlencoded` ve doğru `Content-Length` (çift yoksa `0`)

`ciftler` bir `(ad, değer)` listesidir; aynı ad tekrar edebilir ve sıra korunmalıdır.

```starter
def form_istegi(yontem, yol, ciftler):
    return f"{yontem} {yol} HTTP/1.1\r\nHost: pafta.test\r\n\r\n"
```

```test
import tezgah
need("form_istegi")
eq(form_istegi("GET", "/yanki", [("q", "disk dolu"), ("etiket", "web"), ("etiket", "prod")]),
   "GET /yanki?q=disk+dolu&etiket=web&etiket=prod HTTP/1.1\r\nHost: pafta.test\r\n\r\n", "GET: sorgu, tekrar eden ad")
eq(form_istegi("GET", "/sunucular", []), "GET /sunucular HTTP/1.1\r\nHost: pafta.test\r\n\r\n", "çiftsiz GET")
eq(form_istegi("POST", "/yanki", []),
   "POST /yanki HTTP/1.1\r\nHost: pafta.test\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 0\r\n\r\n",
   "çiftsiz POST: Content-Length 0")
y = tezgah.yanit(form_istegi("POST", "/yanki", [("baslik", "Ağ & yavaş"), ("oncelik", "yüksek")]))
eq(y.json()["govde"], "baslik=A%C4%9F+%26+yava%C5%9F&oncelik=y%C3%BCksek", "POST gövdesi olduğu gibi ulaştı")
y = tezgah.yanit(form_istegi("POST", "/bilet-ac", [("form_kodu", "fk-1029"), ("baslik", "Ağ yavaş"), ("oncelik", "orta")]))
eq(y.durum, 303, "tezgahın formu kabul ediyor")
```

```solution
from urllib.parse import urlencode


def form_istegi(yontem, yol, ciftler):
    govde = urlencode(ciftler)
    if yontem == "GET":
        hedef = f"{yol}?{govde}" if govde else yol
        return f"GET {hedef} HTTP/1.1\r\nHost: pafta.test\r\n\r\n"
    return (f"POST {yol} HTTP/1.1\r\nHost: pafta.test\r\nContent-Type: application/x-www-form-urlencoded\r\n"
            f"Content-Length: {len(govde)}\r\n\r\n{govde}")
```

```hint
`urlencode` bir sözlük gibi `(ad, değer)` listesi de alır ve sırayı korur; çıktısı saf ASCII olduğu için karakter sayısı bayt sayısına eşittir.
```
:::
