---
id: pu14
title: Oltalama E-postası Analizi · Başlık, Kimlik Doğrulama, URL ve Ek Kanıtı
summary: Gerçek .eml biçimindeki sentetik iletileri standart email parser ile çevrimdışı incelemek; RFC 5322 kimlikleri, Received aşamaları, SPF/DKIM/DMARC alignment, görünen ve gerçek URL ile ek/MIME/SHA-256 kanıtlarını SOC bulgusuna dönüştürmek.
timeout: 60
---

::: anlat Oltalama analizi kanıt ayrıştırmadır; etkileşim değildir
CDSA/SOC incelemesinde amaç “kötü görünüyor” izlenimini tekrarlanabilir kanıta çevirmektir. Bu derste iki küçük, gerçek MIME/RFC 5322 yapısında `.eml` fixture vardır. Standart `email.parser.BytesParser(policy=policy.default)` kullanılır; başlıklar elle satır bölünmez ve MIME ekleri regex ile çıkarılmaz.

> [!GÜVENLİK]
> Bütün kişiler, alan adları, Message-ID değerleri ve olaylar kurgusaldır. Dış DNS, whois, URL açma, HTTP isteği, ek yazma/açma/çalıştırma, ağ ve paket kurulumu yoktur. SPF/DKIM/DMARC satırları fixture'a elle yazılmış sentetik sonuçlardır; burada kriptografik imza doğrulanmaz. `MZ` önekli ek yalnız zararsız metin baytlarından oluşan sınıflandırma kanıtıdır.

Analizde üç soruyu ayrı tut: **Kimlikler birbiriyle uyumlu mu? Alıcı aşaması hangi doğrulama sonucunu kaydetmiş? İçerik kullanıcıyı hangi gerçek hedefe veya eke yöneltiyor?** Tek bir `pass`, tek bir şüpheli kelime ya da tek bir dosya uzantısı nihai hüküm değildir.
:::

::: anlat RFC 5322 kimlikleri ve Received zinciri aynı şey değildir
`From`, kullanıcı arayüzünde görünen gönderici kimliğidir; display-name ile addr-spec'i `email.utils.parseaddr` ayırır. `"Pafta Finans <finans@pafta.test>" <fatura@pafta-billing.example>` örneğinde gerçek `From` adresi ikinci addr-spec'tir. Görünen addaki kurumsal e-posta metni **gönderen alanını kanıtlamaz**. `Reply-To` yanıtların yönleneceği ayrı adrestir; `From` ile farklı alan taşıması inceleme bulgusudur ama tek başına kötü niyet kanıtı değildir. `Return-Path` ise bounce/envelope-from bilgisini taşır; kullanıcıya gösterilen `From` ile aynı kavram değildir.

Her aktarım aşaması normalde en üste yeni bir `Received` ekler. Bu nedenle dosyadaki sıra çoğunlukla **en yeni → en eski** okunur. `by`, o aşamada iletiyi kabul eden sistemi; `from`, onun bildirdiği önceki sistemi gösterir. Alanlar başlangıçta güvenilmez metinlerdir; özellikle daha eski satırlar gönderici tarafından etkilenebilir. IP, zaman ve host envanterle ayrıca ilişkilendirilir.

`Authentication-Results` da her zaman güvenilir değildir. Gönderici benzer görünen başlıklar ekleyebilir; bir ağ geçidi yalnız kendi güven sınırında ürettiği/bildirdiği sonuç için değerlendirme yapabilir. Başlığın başındaki `authserv-id` sonucun hangi hizmete ait olduğunu söyler. Bunu `Received` satırlarındaki `by` ile karşılaştırmak, hangi aşamaya ait olduğunu anlamaya yardım eder; **başlığın gerçekten o sistem tarafından yazıldığını kriptografik olarak kanıtlamaz**. Birden çok sonuçta aşama ve güven sınırı ayrıca ele alınır; rastgele ilk `pass` seçilmez.
:::

::: anlat SPF, DKIM ve DMARC: sonuç kadar alignment da gerekir
SPF, envelope-from (`smtp.mailfrom`) için yetkilendirme sonucu verir. DKIM sonucundaki `header.d`, imzalayan alanı belirtir. DMARC değerlendirmesi `From` alanıyla SPF veya DKIM alanının alignment koşulunu kullanır. Bu derste alan eşitliği veya birinin diğerinin alt alanı olması alignment sayılır; gerçek relaxed/strict kip ve organizational-domain hesabı ürün politikasına bağlıdır.

| Soru | Kanıt alanı | Yanıltıcı kısayol |
|---|---|---|
| SPF kim için geçti? | `spf=...`, `smtp.mailfrom=...` | `pass` ise `From` kesin güvenli |
| DKIM'i kim imzaladı? | `dkim=...`, `header.d=...` | Herhangi bir geçerli imza kurumsal kimliktir |
| DMARC hangi `From` için geçti? | `dmarc=...`, `header.from=...` | DMARC geçen ileti oltalama olamaz |
| Sonuç hangi aşamaya ait? | `authserv-id` + ilgili `Received by` | Her Authentication-Results güvenilirdir |

Fixture'daki saldırgan kendi `pafta-billing.example` alanında SPF, DKIM ve DMARC `pass` elde eder; üç alan da birbiriyle hizalıdır. Yine de bu alan kurumsal `pafta.test` değildir. **Başarılı kimlik doğrulama, alanın sahipliğini/kimliğini doğrular; içeriğin iyi niyetli olduğunu doğrulamaz.** Lookalike alan, display-name spoofing, URL hedefi ve ek bulguları bu nedenle bağımsız kalır.
:::

::: tahmin Bütün doğrulamalar geçerse kurumsal gönderen kanıtlanır mı?
```python
sonuc = {"spf": "pass", "dkim": "pass", "dmarc": "pass"}
from_alani = "pafta-billing.example"
print(all(v == "pass" for v in sonuc.values()))
print(from_alani == "pafta.test")
```

???

Çıktı `True` sonra `False` olur. Üç sonuç da `pass` olsa bile `From` alanı beklenen kurumsal alan değildir. SOC raporu iki gözlemi birbirini silmeden taşır: kimlik doğrulama mekanizmaları saldırganın kendi alanında başarılı; kurumsal kimlik iddiası ise alan, görünen ad, URL ve ek kanıtıyla çelişkili.
:::

::: gorev 1 · Kimlikleri, doğrulama sonuçlarını ve Received aşamasını ilişkilendir
`baslik_analizi(mesaj, kurumsal_alan="pafta.test")` işlevini yaz. Girdi standart parser'dan gelen `EmailMessage` nesnesidir; dönüş aşağıdaki sözlük yapısını taşır:

```text
{
 "from": {"display_name": str, "email": str, "domain": str},
 "reply_to": str, "return_path": str,
 "received": [{"from": str, "by": str}, ...],
 "authentication": {
   "authserv_id": str, "spf": str, "spf_domain": str,
   "dkim": str, "dkim_domain": str, "dmarc": str,
   "spf_aligned": bool, "dkim_aligned": bool,
   "stage_received_index": int | None
 },
 "findings": [str, ...]
}
```

Kurallar:

- Adresleri `parseaddr` ile çıkar; alanları küçük harfe çevir. Eksik adres/sonuç için boş metin kullan. `received`, dosyadaki en yeni → en eski sırayı korusun.
- `Authentication-Results` başındaki `authserv-id` ile aynı `by` değerine sahip ilk Received öğesinin sıfır tabanlı indeksini yaz; eşleşme yoksa `None`. Bu yalnız aşama eşleşmesidir, güven kanıtı değildir.
- SPF/DKIM alignment için karşılık gelen alan ile `From` alanı eşitse ya da biri diğerinin alt alanıysa `True` yaz.
- Sıralı ve yinelenmeyen bulgular: `From` kurumsal alan veya alt alanı değilse `from-kurumsal-degil`; kurumsal marka parçası farklı bir `From` alanında geçiyorsa `lookalike-domain`; display-name içinde kurumsal alanlı adres metni varken gerçek `From` kurumsal değilse `display-name-spoofing`; `Reply-To` alanı `From` alanından farklıysa `reply-to-farkli`; `Return-Path` alanı `From` alanından farklıysa `return-path-farkli`.

```starter
from email_analysis_lab import eml_yukle
mesaj = eml_yukle("email_analysis/oltalama.eml")
kurumsal = eml_yukle("email_analysis/kurumsal.eml")


def baslik_analizi(mesaj, kurumsal_alan="pafta.test"):
    return {}

print(baslik_analizi(mesaj))
```

```test
import copy
need("baslik_analizi")
r = baslik_analizi(mesaj)
eq(r["from"], {"display_name": "Pafta Finans <finans@pafta.test>",
               "email": "fatura@pafta-billing.example", "domain": "pafta-billing.example"},
   "display-name ve gerçek RFC5322 addr-spec ayrılır")
eq((r["reply_to"], r["return_path"]),
   ("operasyon@pafta-billing.example", "bounce@pafta-billing.example"), "Reply-To ve Return-Path ayrı kimliklerdir")
eq([h["by"] for h in r["received"]], ["edge.pafta.test", "mail.pafta-billing.example"], "Received en yeni-eski sırası")
eq(r["authentication"], {"authserv_id": "edge.pafta.test", "spf": "pass",
   "spf_domain": "pafta-billing.example", "dkim": "pass", "dkim_domain": "pafta-billing.example",
   "dmarc": "pass", "spf_aligned": True, "dkim_aligned": True, "stage_received_index": 0},
   "sonuç, alan alignment ve Authentication-Results aşaması")
eq(r["findings"], ["display-name-spoofing", "from-kurumsal-degil", "lookalike-domain"],
   "pass sonuçları display-name ve lookalike bulgularını silmez")
k = baslik_analizi(kurumsal)
eq((k["findings"], k["authentication"]["spf_aligned"], k["authentication"]["dkim_aligned"]),
   ([], True, True), "kurumsal kontrol aligned ve bulgusuz")
x = copy.deepcopy(mesaj)
x.replace_header("Reply-To", "Yanıt <baska@dis-alan.example>")
eq("reply-to-farkli" in baslik_analizi(x)["findings"], True, "farklı Reply-To alanı")
x = copy.deepcopy(mesaj)
x.replace_header("Return-Path", "<bounce@baska.example>")
eq("return-path-farkli" in baslik_analizi(x)["findings"], True, "Return-Path From ile karıştırılmaz")
x = copy.deepcopy(mesaj)
x.replace_header("Authentication-Results", "edge.pafta.test; spf=fail smtp.mailfrom=dis.example; dkim=fail header.d=imzalayan.example; dmarc=fail header.from=pafta-billing.example")
a = baslik_analizi(x)["authentication"]
eq((a["spf"], a["dkim"], a["dmarc"], a["spf_aligned"], a["dkim_aligned"]),
   ("fail", "fail", "fail", False, False), "fail ve hizasız alanlar korunur")
x = copy.deepcopy(mesaj); del x["Received"]
eq(baslik_analizi(x)["authentication"]["stage_received_index"], None, "Received yoksa aşama uydurulmaz")
x["Received"] = "by edge.pafta.test; Tue, 20 Oct 2026 08:00:00 +0000"
r = baslik_analizi(x)
eq((r["received"], r["authentication"]["stage_received_index"]),
   ([{"from": "", "by": "edge.pafta.test"}], 0), "from alanı eksik Received kaydı korunur")
x = copy.deepcopy(mesaj); del x["Received"]
x["Received"] = "from mail.pafta-billing.example; Tue, 20 Oct 2026 07:59:00 +0000"
r = baslik_analizi(x)
eq((r["received"], r["authentication"]["stage_received_index"]),
   ([{"from": "mail.pafta-billing.example", "by": ""}], None), "by alanı eksik Received kaydı korunur")
x = copy.deepcopy(mesaj)
x.replace_header("Authentication-Results", "bilinmeyen.example; spf=pass smtp.mailfrom=pafta-billing.example; dkim=pass header.d=pafta-billing.example; dmarc=pass header.from=pafta-billing.example")
eq(baslik_analizi(x)["authentication"]["stage_received_index"], None, "authserv-id hiçbir by aşamasına bağlanamaz")
x = copy.deepcopy(mesaj)
x.replace_header("From", '"Bildirim <finans@pafta.test>" <fatura@tamamen-farkli.example>')
f = baslik_analizi(x)["findings"]
eq(("display-name-spoofing" in f, "lookalike-domain" in f), (True, False),
   "lookalike yokken display-name spoofing bağımsız kalır")
x = copy.deepcopy(mesaj)
x.replace_header("From", "Fatura Servisi <fatura@pafta-billing.example>")
eq(baslik_analizi(x)["findings"], ["from-kurumsal-degil", "lookalike-domain"],
   "görünen adda kurumsal adres yoksa display-name spoofing yazılmaz")
x.replace_header("From", '"finans@pafta.test" <finans@mail.pafta.test>')
f = baslik_analizi(x)["findings"]
eq([b for b in f if b not in ("reply-to-farkli", "return-path-farkli")], [],
   "kurumsal alt alan kurumsaldır; gerçek From kurumsalken görünen addaki adres spoofing değildir")
x.replace_header("From", "Destek <destek@notpafta.test>")
eq("from-kurumsal-degil" in baslik_analizi(x)["findings"], True, "nokta sınırı olmadan sonek eşleşmesi alt alan sayılmaz")
x = copy.deepcopy(mesaj)
x.replace_header("From", "Fatura <fatura@mail.pafta-billing.example>")
x.replace_header("Authentication-Results", "edge.pafta.test; spf=pass smtp.mailfrom=bounce.mail.pafta-billing.example; dkim=pass header.d=pafta-billing.example; dmarc=pass header.from=mail.pafta-billing.example")
a = baslik_analizi(x)["authentication"]
eq((a["spf_aligned"], a["dkim_aligned"]), (True, True),
   "alignment iki yönde de alt alanı kabul eder: SPF alanı From'un, From da DKIM alanının alt alanı")
```

```solution
import re
from email.utils import parseaddr


def alan(adres):
    return parseaddr(adres)[1].rsplit("@", 1)[-1].lower() if "@" in parseaddr(adres)[1] else ""


def ayni_kok(a, b):
    return bool(a and b) and (a == b or a.endswith("." + b) or b.endswith("." + a))


from email_analysis_lab import eml_yukle
mesaj = eml_yukle("email_analysis/oltalama.eml")
kurumsal = eml_yukle("email_analysis/kurumsal.eml")


def baslik_analizi(mesaj, kurumsal_alan="pafta.test"):
    gorunen, from_email = parseaddr(mesaj.get("From", ""))
    from_domain = from_email.rsplit("@", 1)[-1].lower() if "@" in from_email else ""
    reply_to = parseaddr(mesaj.get("Reply-To", ""))[1]
    return_path = parseaddr(mesaj.get("Return-Path", ""))[1]
    received = []
    for deger in mesaj.get_all("Received", []):
        from_eslesme = re.search(r"^\s*from\s+(.+?)(?=\s+by\s+|\s*;|$)", deger, re.I | re.S)
        by_eslesme = re.search(r"(?:^|[;\s])by\s+([^\s;]+)", deger, re.I)
        received.append({
            "from": " ".join(from_eslesme.group(1).split()) if from_eslesme else "",
            "by": by_eslesme.group(1).lower() if by_eslesme else "",
        })
    ar = mesaj.get("Authentication-Results", "")
    authserv = ar.split(";", 1)[0].strip().lower()

    def deger(desen):
        bulgu = re.search(desen, ar, re.I)
        return bulgu.group(1).lower() if bulgu else ""

    auth = {
        "authserv_id": authserv,
        "spf": deger(r"(?:^|[;\s])spf=([a-z]+)"),
        "spf_domain": deger(r"smtp\.mailfrom=([^\s;]+)"),
        "dkim": deger(r"(?:^|[;\s])dkim=([a-z]+)"),
        "dkim_domain": deger(r"header\.d=([^\s;]+)"),
        "dmarc": deger(r"(?:^|[;\s])dmarc=([a-z]+)"),
        "spf_aligned": False,
        "dkim_aligned": False,
        "stage_received_index": next((i for i, h in enumerate(received) if h["by"] == authserv), None),
    }
    auth["spf_aligned"] = ayni_kok(auth["spf_domain"], from_domain)
    auth["dkim_aligned"] = ayni_kok(auth["dkim_domain"], from_domain)
    kurumsal = ayni_kok(from_domain, kurumsal_alan)
    findings = set()
    if not kurumsal:
        findings.add("from-kurumsal-degil")
    if not kurumsal and kurumsal_alan.split(".", 1)[0] in from_domain:
        findings.add("lookalike-domain")
    if not kurumsal and re.search(r"[\w.+-]+@" + re.escape(kurumsal_alan) + r"\b", gorunen, re.I):
        findings.add("display-name-spoofing")
    if alan(reply_to) and alan(reply_to) != from_domain:
        findings.add("reply-to-farkli")
    if alan(return_path) and alan(return_path) != from_domain:
        findings.add("return-path-farkli")
    return {"from": {"display_name": gorunen, "email": from_email, "domain": from_domain},
            "reply_to": reply_to, "return_path": return_path, "received": received,
            "authentication": auth, "findings": sorted(findings)}


print(baslik_analizi(mesaj))
```

```hint
`parseaddr` dört kimlik için de kullanılmalı. Önce Received listesini kur; `next((i ...), None)` ile authserv-id eşleşmesini bul. Alignment ve kurumsallık için ortak bir alt alan işlevi yaz.
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from email_analysis_lab import hazirla, eml_yukle
klasor = hazirla()
mesaj = eml_yukle(klasor / "oltalama.eml")
kurumsal = eml_yukle(klasor / "kurumsal.eml")
```
:::

::: anlat Bağlantının yazısı değil gerçek hedefi analiz edilir
HTML `<a>` öğesinde kullanıcı gövde metnini, tıklama ise `href` hedefini kullanır. `https://pafta.test/odeme` yazan bir bağlantı başka bir alana gidebilir. Ayrıca URL userinfo sözdiziminde `https://pafta.test@odeme-guvenli.example/giris` için gerçek host **`odeme-guvenli.example`**, `pafta.test` ise yalnız kullanıcı bilgisidir. Host çıkarımında string'in bir yerinde kurumsal ad aramak yerine `urllib.parse.urlsplit(...).hostname` kullanılır. Bu işlem ağ isteği yapmaz.

Rapor veya sohbet dışına aktarılan IOC'de defang uygula: örneğin `https://alan.example/yol` → `hxxps[:]//alan[.]example/yol`. Amaç yanlışlıkla tıklanabilir bağlantı üretmemektir; defang hedefi güvenli yapmaz ve orijinal kanıtın yerine geçmez. Analiz çıktısında hem orijinal string hem defang biçimi bulunur. Punycode, kısaltıcı, redirect ve benzeri durumlar gerçek ortamda ek çevrimdışı kanıt gerektirir; bu ders onları çözümlemek için dış servise gitmez.
:::

::: gorev 2 · HTML bağlantılarında gövde/gerçek hedef ayrımını çıkar
`baglantilari_analizet(mesaj)` işlevini yaz. Standart `html.parser.HTMLParser` ile yalnız `text/html` parçalarındaki `<a href=...>` öğelerini topla. URL açma. Her bağlantı için belge sırasını koruyan şu sözlüğü döndür:

```text
{"gorunen": str, "gercek": str, "alan": str,
 "kullanici_bilgisi": str | None, "defang": str, "uyusmuyor": bool}
```

- `gorunen`, anchor içindeki metnin boşlukları normalize edilmiş hâli; `gercek`, href değeri; `alan`, `urlsplit(gercek).hostname` küçük harfli; kullanıcı bilgisi yoksa `None`.
- `uyusmuyor`, görünen metin ile gerçek href'in birebir aynı olmamasıdır. Bu bir inceleme sinyalidir; tek başına zararlı hükmü değildir.
- Defang için baştaki `http` → `hxxp`, `:` → `[:]`, `.` → `[.]` dönüşümlerini uygula. Orijinal `gercek` alanını değiştirme.
- HTML olmayan parçaları ve `href` taşımayan anchor'ları atla.

```starter
from email_analysis_lab import eml_yukle
mesaj = eml_yukle("email_analysis/oltalama.eml")


def baglantilari_analizet(mesaj):
    return []

print(baglantilari_analizet(mesaj))
```

```test
from email.message import EmailMessage
need("baglantilari_analizet")
r = baglantilari_analizet(mesaj)
eq(len(r), 2, "iki HTML anchor, ekler ve metin taramasına karışmaz")
eq(r[0], {"gorunen": "https://pafta.test/odeme/1042",
   "gercek": "https://pafta.test@odeme-guvenli.example/giris", "alan": "odeme-guvenli.example",
   "kullanici_bilgisi": "pafta.test", "defang": "hxxps[:]//pafta[.]test@odeme-guvenli[.]example/giris",
   "uyusmuyor": True}, "görünen hedef, userinfo, gerçek host ve defang")
eq((r[1]["alan"], r[1]["kullanici_bilgisi"], r[1]["uyusmuyor"]),
   ("pafta.test", None, False), "kurumsal kontrol bağlantısı")
x = EmailMessage(); x.add_alternative('<a href="https://dis.example/x">https://dis.example/x</a>', subtype="html")
eq(baglantilari_analizet(x)[0]["uyusmuyor"], False, "aynen tekrarlanan href uyumsuz değil")
x = EmailMessage(); x.add_alternative('<a href="https://dis.example/x">Güvenli portal</a>', subtype="html")
eq((baglantilari_analizet(x)[0]["uyusmuyor"], baglantilari_analizet(x)[0]["alan"]),
   (True, "dis.example"), "URL olmayan anchor metni de gerçek href'ten ayrılır")
x = EmailMessage(); x.set_content("https://duz-metin.example")
eq(baglantilari_analizet(x), [], "bu görev yalnız HTML anchor sözleşmesini uygular")
x = EmailMessage(); x.add_alternative('<p><a href="https://dis.example/f"><span>Faturayı</span> <b>görüntüle</b></a></p>', subtype="html")
eq(baglantilari_analizet(x), [{"gorunen": "Faturayı görüntüle", "gercek": "https://dis.example/f", "alan": "dis.example",
   "kullanici_bilgisi": None, "defang": "hxxps[:]//dis[.]example/f", "uyusmuyor": True}],
   "anchor içindeki span/b kapanışı kaydı erken kapatmaz; iç metin görünen yazıya katılır")
x = EmailMessage(); x.add_alternative('<link rel="stylesheet" href="https://cdn.example/s.css"><p>Merhaba</p></a>'
                                      '<a href="https://dis.example/x">Portal</a>', subtype="html")
eq([b["gercek"] for b in baglantilari_analizet(x)], ["https://dis.example/x"],
   "yalnız <a> kayıt açar; href taşıyan başka öğe ve sahipsiz </a> bağlantı değildir")
```

```solution
import re
from html.parser import HTMLParser
from urllib.parse import urlsplit


from email_analysis_lab import eml_yukle
mesaj = eml_yukle("email_analysis/oltalama.eml")


def baglantilari_analizet(mesaj):
    baglantilar = []

    class Toplayici(HTMLParser):
        def __init__(self):
            super().__init__()
            self.href = None
            self.metin = []

        def handle_starttag(self, tag, attrs):
            if tag.lower() == "a" and self.href is None:
                self.href = dict(attrs).get("href")
                self.metin = []

        def handle_data(self, data):
            if self.href is not None:
                self.metin.append(data)

        def handle_endtag(self, tag):
            if tag.lower() == "a" and self.href is not None:
                gercek = self.href
                parca = urlsplit(gercek)
                gorunen = " ".join("".join(self.metin).split())
                baglantilar.append({"gorunen": gorunen, "gercek": gercek,
                    "alan": (parca.hostname or "").lower(), "kullanici_bilgisi": parca.username,
                    "defang": re.sub(r"^http", "hxxp", gercek, flags=re.I).replace(":", "[:]").replace(".", "[.]"),
                    "uyusmuyor": gorunen != gercek})
                self.href = None
                self.metin = []

    for parca in mesaj.walk():
        if parca.get_content_type() == "text/html":
            Toplayici().feed(parca.get_content())
    return baglantilar


print(baglantilari_analizet(mesaj))
```

```hint
`HTMLParser` alt sınıfında aktif href ve metin listesi tut; `</a>` ile kaydı kapat. Host ve username için yalnız `urlsplit` kullan. `walk()` içinden MIME türü `text/html` olanları seç.
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from email_analysis_lab import hazirla, eml_yukle
klasor = hazirla()
mesaj = eml_yukle(klasor / "oltalama.eml")
kurumsal = eml_yukle(klasor / "kurumsal.eml")
```
:::

::: anlat Ek adı değil, birleşik kanıt raporlanır
Dosya adı saldırganın seçtiği bir etikettir. Son uzantıyı, önceki uzantıları, MIME türünü ve içerik imzasını birlikte incele. `Fatura_1042.pdf.exe` için son uzantı `.exe`; `.pdf` görünmesi belge olduğunu kanıtlamaz. MIME `application/x-msdownload` da yürütülebilir içerik sinyalini destekler ama MIME de gönderenin beyanıdır. Baştaki `MZ` baytları ayrı bir içerik gözlemidir; dosyanın gerçekten çalıştığı veya zarar verdiği anlamına gelmez.

SHA-256, **decode edilmiş ek baytlarının** bütünlük/tekilleştirme kanıtıdır. Hash, dosyanın iyi veya kötü olduğunu söylemez; aynı kanıtı başka kayıtla eşlemeyi ve sonradan değişip değişmediğini denetlemeyi sağlar. Base64 metnini değil `get_payload(decode=True)` sonucunu hash'le. Eki diske çıkarma, açma veya çalıştırma. Dosya adı/MIME/uzantı uyuşmazlığı ile hash farklı alanlarda saklanır; hash hesaplamış olmak sınıflandırma kurallarını atlamayı mazur göstermez.
:::

::: gorev 3 · Ek adı, MIME, uzantı ve SHA-256 kanıt paketi üret
`ek_kanitlari(mesaj)` işlevini yaz. `iter_attachments()` ile her eki belge sırasında şu sözlüğe çevir:

```text
{"filename": str, "mime": str, "extension": str, "size": int,
 "sha256": str, "findings": [str, ...]}
```

- `filename` parser'ın çözdüğü addır; `mime`, `get_content_type()`; `extension`, son dosya uzantısının küçük harfli hâli veya boş metin; `size`, decode edilmiş bayt uzunluğu; `sha256`, bu baytların hexadecimal SHA-256 değeri.
- Son iki uzantıdan ilki `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx` ve son uzantı `.exe`, `.scr`, `.js`, `.vbs`, `.ps1`, `.bat`, `.cmd`, `.hta`, `.jar` ise `cift-uzanti`.
- Son uzantı tehlikeli kümedeyse `tehlikeli-uzanti`; decode edilmiş içerik `MZ` ile başlıyorsa `yurutulebilir-imza`.
- Basit MIME beklentisi: `.pdf` → `application/pdf`, `.txt` → `text/plain`, `.csv` → `text/csv`, `.exe` → `application/x-msdownload` veya `application/vnd.microsoft.portable-executable`. Uyuşmazsa `mime-uzanti-uyusmuyor`. Haritada olmayan uzantı için bu bulguyu üretme.

```starter
from email_analysis_lab import eml_yukle
mesaj = eml_yukle("email_analysis/oltalama.eml")
kurumsal = eml_yukle("email_analysis/kurumsal.eml")


def ek_kanitlari(mesaj):
    return []

print(ek_kanitlari(mesaj))
```

```test
import copy
from email.message import EmailMessage
need("ek_kanitlari")
r = ek_kanitlari(mesaj)
eq(len(r), 2, "iki MIME eki")
eq(r[0], {"filename": "Fatura_1042.pdf.exe", "mime": "application/x-msdownload", "extension": ".exe",
   "size": 41, "sha256": "77b35f33eaa412199758158b6ac9b925b7fa20e10dc1b57db4441bbc9663ba29",
   "findings": ["cift-uzanti", "tehlikeli-uzanti", "yurutulebilir-imza"]},
   "çift uzantı, tehlikeli son uzantı, MZ ve decode edilmiş SHA-256")
eq(r[1]["findings"], ["mime-uzanti-uyusmuyor"], "PDF adı ile text/plain MIME uyuşmaz")
eq(r[1]["sha256"], "3de492415ce1ccb0629889d45b26c7100d246f574574480458d757f365501401", "ikinci ek hash kanıtı")
eq(ek_kanitlari(kurumsal), [{"filename": "butce.csv", "mime": "text/csv", "extension": ".csv", "size": 24,
   "sha256": "4f02bfe98f3cf3e70b45ea56427e3f2b4561ea1a08100c848c403d661c178680", "findings": []}],
   "güvenli CSV kontrolü ve hash")
x = EmailMessage(); x.add_attachment(b"hello\n", maintype="text", subtype="plain", filename="not.txt")
r = ek_kanitlari(x)
eq((r[0]["findings"], r[0]["size"]), ([], 6), "eşleşen TXT MIME ve uzantı")
x = EmailMessage(); x.add_attachment(b"MZ-degisik", maintype="application", subtype="x-msdownload", filename="a.exe")
once = ek_kanitlari(x)[0]
x = EmailMessage(); x.add_attachment(b"MZ-degisik!", maintype="application", subtype="x-msdownload", filename="a.exe")
sonra = ek_kanitlari(x)[0]
eq(once["sha256"] != sonra["sha256"], True, "tek bayt değişimi hash kanıtını değiştirir")
eq((once["extension"], sonra["extension"]), (".exe", ".exe"), "hash değişimi diğer alanların atlanmasına neden olmaz")
x = EmailMessage(); x.add_attachment(b"%PDF-sentetik", maintype="text", subtype="plain", filename="rapor.pdf")
eq(ek_kanitlari(x)[0]["findings"], ["mime-uzanti-uyusmuyor"], "içerik imzası olmasa da ad/MIME denetimi kalır")
x = EmailMessage(); x.set_content("eksiz")
eq(ek_kanitlari(x), [], "ek yoksa boş kanıt listesi")
x = EmailMessage()
for ad, ana, alt in (("kurulum.exe", "application", "x-msdownload"), ("rapor.pdf.txt", "text", "plain"),
                     ("arsiv.zip.exe", "application", "x-msdownload")):
    x.add_attachment(b"veri", maintype=ana, subtype=alt, filename=ad)
eq([e["findings"] for e in ek_kanitlari(x)], [["tehlikeli-uzanti"], [], ["tehlikeli-uzanti"]],
   "çift uzantı yalnız belge uzantısı + tehlikeli son uzantıdır; tek .exe, .pdf.txt ve .zip.exe değildir")
```

```solution
import hashlib
from pathlib import PurePath


from email_analysis_lab import eml_yukle
mesaj = eml_yukle("email_analysis/oltalama.eml")
kurumsal = eml_yukle("email_analysis/kurumsal.eml")


def ek_kanitlari(mesaj):
    tehlikeli = {".exe", ".scr", ".js", ".vbs", ".ps1", ".bat", ".cmd", ".hta", ".jar"}
    belge = {".pdf", ".doc", ".docx", ".xls", ".xlsx"}
    beklenen_mime = {".pdf": {"application/pdf"}, ".txt": {"text/plain"}, ".csv": {"text/csv"},
        ".exe": {"application/x-msdownload", "application/vnd.microsoft.portable-executable"}}
    sonuc = []
    for ek in mesaj.iter_attachments():
        ad = ek.get_filename() or ""
        mime = ek.get_content_type().lower()
        icerik = ek.get_payload(decode=True) or b""
        uzantilar = [u.lower() for u in PurePath(ad).suffixes]
        uzanti = uzantilar[-1] if uzantilar else ""
        findings = set()
        if len(uzantilar) >= 2 and uzantilar[-2] in belge and uzanti in tehlikeli:
            findings.add("cift-uzanti")
        if uzanti in tehlikeli:
            findings.add("tehlikeli-uzanti")
        if icerik.startswith(b"MZ"):
            findings.add("yurutulebilir-imza")
        if uzanti in beklenen_mime and mime not in beklenen_mime[uzanti]:
            findings.add("mime-uzanti-uyusmuyor")
        sonuc.append({"filename": ad, "mime": mime, "extension": uzanti, "size": len(icerik),
                      "sha256": hashlib.sha256(icerik).hexdigest(), "findings": sorted(findings)})
    return sonuc


print(ek_kanitlari(mesaj))
```

```hint
Önce `get_payload(decode=True)` ile baytları bir kez al; boyut, MZ ve hash bunu kullanır. `PurePath(ad).suffixes` bütün uzantıları verir. MIME eşleşmesini hash hesabından bağımsız uygula.
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from email_analysis_lab import hazirla, eml_yukle
klasor = hazirla()
mesaj = eml_yukle(klasor / "oltalama.eml")
kurumsal = eml_yukle(klasor / "kurumsal.eml")
```
:::

::: anlat SOC triage notunu kanıt sınırıyla kapat
Bu sentetik olayda doğru özet şudur: görünen ad kurumsal adres izlenimi veriyor; gerçek `From` alanı lookalike `pafta-billing.example`; `Reply-To` ve `Return-Path` ayrı rolleriyle kaydedildi. En yeni `Received by` olan `edge.pafta.test`, Authentication-Results `authserv-id` ile aşama düzeyinde eşleşiyor. SPF/DKIM/DMARC `pass` ve alignment var, ancak bunlar saldırganın kendi alanına ait; içeriği temizlemez.

HTML bağlantısının görünen metni `pafta.test` derken gerçek host `odeme-guvenli.example`; ayrıca `pafta.test` userinfo olarak kullanılmış. Eklerde çift uzantı, tehlikeli son uzantı, MIME uyuşmazlığı ve SHA-256 kanıtları ayrı korunur. Gerçek SOC sürecinde ham `.eml` bütünlüğü, teslim zamanı, alıcı kapsamı, mesaj izleme kayıtları, benzer iletiler ve yetkili müdahale adımları ayrıca eklenir. Bu ders herhangi bir dış itibar sorgusu yapmadığı için alanın kaydı, güncel sahibi veya hedefin çevrimiçi durumu hakkında iddia üretmez.
:::
