---
id: ht10
title: Sayfa Kaynağını Okumak
summary: Bir HTML belgesinin yapısı; etiket, öznitelik, boş (void) öğeler, değeri olmayan öznitelikler, yorumlar ve karakter varlıkları; head içindeki title, meta, link ve script; sunucudan gelen kaynak ile tarayıcının DOM'u; html.parser ile kaynağı gezmek.
---

::: anlat Bir HTML belgesi
Sunucudan gelen bir web sayfası da bir metindir. Tezgahın ana sayfasının kaynağı:

```python
import tezgah

y = tezgah.yanit("GET / HTTP/1.1\r\nHost: pafta.test\r\n\r\n")
print(y.baslik("Content-Type"))
print(y.govde)
```

| Kavram | Örnek | Not |
|---|---|---|
| öğe | `<h1>Pafta Bilet Masası</h1>` | başlangıç etiketi, içerik, bitiş etiketi |
| öznitelik | `<a href="/sunucular">` | `ad="değer"`; tırnaksız da yazılabilir: `class=not` |
| değeri olmayan öznitelik | `<input required>`, `<option selected>` | **var olması** yeter |
| boş (void) öğe | `<meta>`, `<link>`, `<img>`, `<input>`, `<br>` | bitiş etiketi yoktur; `<br/>` de yazılır |
| yorum | `<!-- sürüm 2.4.1 -->` | sayfada görünmez, **kaynakta görünür** |
| karakter varlığı | `&amp;` `&lt;` `&gt;` `&quot;` `&#39;` | `&`, `<`, `>`, `"`, `'` |

Etiket ve öznitelik **adları** büyük-küçük harfe duyarsızdır (`<P CLASS=x>` ile `<p class=x>` aynı). `<head>` sayfanın kendisi hakkında bilgi taşır: `<title>` (sekmede görünen ad), `<meta charset>` ve `<meta name="description">`, `<link rel="stylesheet">` (stil dosyası), `<script src>` (betik).

> [!NOT]
> "Sayfa kaynağını görüntüle" sunucunun gönderdiği **ham** HTML'i gösterir. Geliştirici araçlarının öğe görünümü ise tarayıcının o andaki **DOM**'unu gösterir: JavaScript sayfayı yükledikten sonra değiştirmiş olabilir. Bir sayfanın sunucudan ne getirdiğini anlamak için ham kaynağa bakılır; bu yolda yaptığın da budur.
:::

::: anlat html.parser ile gezmek
Python'un `html.parser.HTMLParser` sınıfı kaynağı baştan sona okur ve gördüğü her şey için bir metot çağırır. Alt sınıfta ilgilendiğin metotları yazarsın:

| Metot | Ne zaman |
|---|---|
| `handle_starttag(etiket, oznitelikler)` | başlangıç etiketi; `oznitelikler` `(ad, değer)` listesi |
| `handle_endtag(etiket)` | bitiş etiketi |
| `handle_startendtag(etiket, oznitelikler)` | `<br/>` gibi kendini kapatan etiket; varsayılan hâli önce `handle_starttag`, sonra `handle_endtag`'i çağırır |
| `handle_data(veri)` | etiketlerin arasındaki metin |
| `handle_comment(veri)` | yorumun içi |

```python
from html.parser import HTMLParser

class Gezgin(HTMLParser):
    def handle_starttag(self, etiket, oznitelikler):
        print("başla", etiket, oznitelikler)
    def handle_endtag(self, etiket):
        print("bitir", etiket)
    def handle_data(self, veri):
        if veri.strip():
            print("metin", repr(veri.strip()))
    def handle_comment(self, veri):
        print("yorum", repr(veri))

Gezgin().feed('<P CLASS=not>Açık <b>2</b> bilet &amp; <!-- gizli değil --> <input name="q" required></p>')
```

Etiket ve öznitelik adları **küçük harfe** çevrilmiş gelir; değeri olmayan bir özniteliğin değeri `None`'dır; `&amp;` gibi varlıklar çözülmüş gelir (`convert_charrefs=True` varsayılandır). Bir öğenin özniteliklerine `dict(oznitelikler)` ile kolayca bakılır.

> [!GÜVENLİK]
> Sayfa kaynağı herkesin okuyabildiği bir belgedir. Yorumlara, gizli alanlara (`type="hidden"`) ya da gömülü betiklere iç adres, kimlik bilgisi veya hata ayıklama notu yazılmamalı. Tersi yönde de bir kural var: kullanıcıdan gelen bir metin sayfaya yazılırken `<`, `>`, `&` ve tırnaklar varlıklara çevrilir (Python'da `html.escape`); JS ve PHP yollarındaki "çıktıyı kaçır" ilkesi budur.
:::

::: tahmin
İki satır yazar:

```python
from html.parser import HTMLParser

class Sayac(HTMLParser):
    def __init__(self):
        super().__init__()
        self.etiketler = []
        self.yorumlar = []
    def handle_starttag(self, etiket, oznitelikler):
        self.etiketler.append(etiket)
    def handle_comment(self, veri):
        self.yorumlar.append(veri.strip())

s = Sayac()
s.feed('<UL><li>web01<li>db01</ul><img src=logo.png alt="&lt;Pafta&gt;"><!-- not: eski sürüm --><br/>')
print(s.etiketler)
print(s.yorumlar)
```

???

`['ul', 'li', 'li', 'img', 'br']` ve `['not: eski sürüm']`. Etiket adları küçük harfe çevrilir. `<li>`'nin bitiş etiketi yazılmamış ama her `<li>` yine bir başlangıç etiketidir. `<br/>` kendini kapatan bir etikettir; `handle_startendtag`'in varsayılan hâli `handle_starttag`'i çağırdığı için listeye girer. Yorumun içi kenar boşlukları atılarak gelir.
:::

::: gorev Kaynaktaki yorumlar
`yorumlar(html)` fonksiyonu bir HTML kaynağındaki bütün yorumların içeriğini, kenar boşlukları atılmış olarak ve sırasıyla bir liste hâlinde döndürsün. `html.parser` kullan.

```starter
def yorumlar(html):
    return []
```

```test
import tezgah
need("yorumlar")
ok(uses("class") or "HTMLParser" in src, "html.parser.HTMLParser kullan")
def sayfa(yol):
    return tezgah.yanit(f"GET {yol} HTTP/1.1\r\nHost: pafta.test\r\n\r\n").govde
eq(yorumlar(sayfa("/")), ["sürüm 2.4.1 · ön yüz ekibi"], "ana sayfa")
eq(yorumlar(sayfa("/kaynaklar")), ["not: eski uç nokta /v1/durum kaldırıldı, /durum kullanılıyor"], "kaynaklar sayfası")
eq(yorumlar(sayfa("/bilet-ac")), [], "yorumsuz sayfa")
eq(yorumlar("<p>a</p><!--bir--><!--  iki <b>kalın değil</b>  -->"), ["bir", "iki <b>kalın değil</b>"],
   "iki yorum; yorumun içindeki etiket metindir")
```

```solution
from html.parser import HTMLParser


class _Yorumcu(HTMLParser):
    def __init__(self):
        super().__init__()
        self.bulunan = []

    def handle_comment(self, veri):
        self.bulunan.append(veri.strip())


def yorumlar(html):
    y = _Yorumcu()
    y.feed(html)
    return y.bulunan
```

```hint
`HTMLParser`'dan türeyen bir sınıf yaz, `__init__`'te bir liste kur (önce `super().__init__()`), `handle_comment`'te listeye ekle.
```
:::

::: gorev Etiket sayımı
`etiket_sayisi(html)` fonksiyonu kaynaktaki her etiketin kaç kez **başladığını** bir sözlük olarak döndürsün (`{"a": 4, "p": 1, ...}`). Kendini kapatan etiketler (`<br/>`) de sayılsın; bitiş etiketleri sayılmasın.

```starter
def etiket_sayisi(html):
    return {}
```

```test
import tezgah
need("etiket_sayisi")
def sayfa(yol):
    return tezgah.yanit(f"GET {yol} HTTP/1.1\r\nHost: pafta.test\r\n\r\n").govde
eq(etiket_sayisi(sayfa("/bilet-ac")),
   {"html": 1, "head": 1, "meta": 1, "title": 1, "body": 1, "h1": 1, "form": 1, "input": 4, "label": 4,
    "select": 1, "option": 4, "textarea": 1, "button": 1}, "bilet formu")
eq(etiket_sayisi("<UL><li>a<li>b</ul><br/><BR>"), {"ul": 1, "li": 2, "br": 2}, "küçük harf; <br/> ve <BR> aynı etiket")
eq(etiket_sayisi("düz metin"), {}, "etiketsiz metin")
```

```solution
from html.parser import HTMLParser


class _Sayac(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sayilar = {}

    def handle_starttag(self, etiket, oznitelikler):
        self.sayilar[etiket] = self.sayilar.get(etiket, 0) + 1


def etiket_sayisi(html):
    s = _Sayac()
    s.feed(html)
    return s.sayilar
```

```hint
`handle_starttag`'i yazman yeter: `handle_startendtag`'in varsayılan hâli onu zaten çağırır.
```
:::

::: gorev Sayfa bilgisi
`sayfa_bilgisi(html)` fonksiyonu bir sayfadan şu sözlüğü çıkarsın:

- `"baslik"`: `<title>`'ın içindeki metin, kenar boşlukları atılmış (`<title>` yoksa `None`)
- `"meta"`: `name` özniteliği olan her `<meta>` için `{name: content}` (adlar küçük harf; `<meta charset>` gibi `name`'i olmayanlar girmez)
- `"dil"`: `<html>`'in `lang` özniteliği (yoksa `None`)

```starter
def sayfa_bilgisi(html):
    return {"baslik": None, "meta": {}, "dil": None}
```

```test
import tezgah
need("sayfa_bilgisi")
ana = tezgah.yanit("GET / HTTP/1.1\r\nHost: pafta.test\r\n\r\n").govde
eq(sayfa_bilgisi(ana), {"baslik": "Ana sayfa · Pafta Bilet Masası",
                        "meta": {"description": "Altyapı ekibinin bilet masası"}, "dil": "tr"}, "ana sayfa")
eq(sayfa_bilgisi('<HTML><head><TITLE>\n  Rapor &amp; Özet </title><META NAME="Robots" CONTENT="noindex">'
                 '<meta charset="utf-8"><meta name="author" content="ayse"></head></HTML>'),
   {"baslik": "Rapor & Özet", "meta": {"robots": "noindex", "author": "ayse"}, "dil": None},
   "büyük harfli etiketler, varlık, charset meta'sı dışarıda, lang yok")
eq(sayfa_bilgisi("<p>başlıksız</p>"), {"baslik": None, "meta": {}, "dil": None}, "boş sayfa bilgisi")
```

```solution
from html.parser import HTMLParser


class _Bilgi(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sonuc = {"baslik": None, "meta": {}, "dil": None}
        self.baslikta = False

    def handle_starttag(self, etiket, oznitelikler):
        oz = dict(oznitelikler)
        if etiket == "html":
            self.sonuc["dil"] = oz.get("lang")
        elif etiket == "title":
            self.baslikta = True
            self.sonuc["baslik"] = ""
        elif etiket == "meta" and oz.get("name"):
            self.sonuc["meta"][oz["name"].lower()] = oz.get("content")

    def handle_endtag(self, etiket):
        if etiket == "title":
            self.baslikta = False
            self.sonuc["baslik"] = self.sonuc["baslik"].strip()

    def handle_data(self, veri):
        if self.baslikta:
            self.sonuc["baslik"] += veri


def sayfa_bilgisi(html):
    b = _Bilgi()
    b.feed(html)
    return b.sonuc
```

```hint
`<title>`'ın metni `handle_data`'ya gelir; bunun başlığa ait olduğunu bilmek için `handle_starttag`'te bir bayrak aç, `handle_endtag`'te kapat.
```

```hint
Öznitelikleri `dict(oznitelikler)` ile sözlüğe çevir; değeri olmayan bir öznitelik `None` olur, `oz.get("name")` hem yokluğu hem boşluğu yakalar.
```
:::
