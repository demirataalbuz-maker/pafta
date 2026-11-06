---
id: pu24
title: Keşif · ffuf ve nuclei ile Kendi Sunucunu Tara, Erişim Kaydında Yakala
summary: Yumuşak 404 dönen kendi 127.0.0.1 sunucusunda gerçek ffuf ve nuclei koşusu; ffuf sonucunu taban imzasıyla ayıkla, negatif eşleştiricili kendi nuclei şablonunu kur, ters vekil arkasındaki erişim kaydında taramayı kayan pencereyle tespit et.
timeout: 30
---

::: anlat Keşfin iki yüzü
| Sahada ne olur | Bu ders ne kullanır | Ne söyleyemez? |
|---|---|---|
| Saldırgan web uygulamasında gizli yolları kelime listesiyle dener (dizin keşfi), bilinen ifşaları şablonla doğrular | Sabit sürümlü ffuf 2.3.0 ve nuclei 3.11.1; kendi `127.0.0.1` sunucusu, 25 kelimelik sentetik liste, öğrencinin kendi üç şablonu | Gerçek bir hedefi, nuclei'nin genel şablon deposunu, kimlik doğrulamalı taramayı ya da WAF atlatmayı göstermez |
| Birçok uygulama bulunamayan sayfaya 200 döner (yumuşak 404); ham sonuç gürültüdür | Bulunamayan yolu sayfaya yazan bir sunucu | Gerçek uygulamalardaki bütün yumuşak 404 biçimlerini kapsamaz |
| Savunma tarafı aynı olayı erişim kaydında görür; uygulama çoğu zaman bir ters vekilin arkasındadır | X-Forwarded-For'lu erişim kaydı, kayan pencere eşiği | Bir SIEM'i, Zeek'i ya da dağıtık ve yavaş taramayı göstermez |

> [!NOT]
> İlk üç görev `kesif/ornekler.json` dosyasını okur; girdiler **sentetiktir**, hiçbir sunucuya gönderilmez. Setup her Çalıştır/Kontrol Et adımında eksik dosyaları kopyalar; **kalıcılık yoktur**. Dosyayı görmek için başlangıç kodundaki `print` satırlarını kullan. Son görev, `.deps` altındaki önceden onaylanmış ve hash'i doğrulanmış ffuf ve nuclei'yi **yalnız** o koşuda açılan kendi `127.0.0.1` sunucusuna karşı çalıştırır. nuclei güncelleme denetimi kapalı (`-duc`) ve yalnız senin şablonlarınla koşar; genel şablon deposu indirilmez. Araçlar her isteği kaydedip reddeden yerel bir vekil üzerinden koşar. Bu araçları sahibi olmadığın ya da yazılı izin almadığın bir sisteme yöneltmek yasa dışıdır; pu21'deki kapsam kapısı burada da geçerlidir.

**Dizin keşfi ve yumuşak 404.** ffuf, URL'deki `FUZZ` yerine kelime listesindeki her kelimeyi koyar ve yanıtı kaydeder. `-mc all` ile her yanıtı tutarsan sorun açıktır: bu labdaki sunucu var olmayan her yola `200` ve "Sayfa bulunamadi: /yol" döner. Yalnız 404'ü elemek hiçbir şeyi elemez. Çözüm **kalibrasyondur**: rastgele, kesinlikle var olmayan bir yola istek gönder ve yanıtın imzasını al. Durum aynı, kelime ve satır sayısı aynı olan sonuç büyük olasılıkla aynı "bulunamadı" sayfasıdır. Uzunluk imzaya girmez, çünkü sayfa istenen yolu kendine yazar ve her istekte birkaç bayt değişir. ffuf'un `-fw`, `-fl` ve `-ac` seçenekleri bu işi araç içinde yapar; burada kararı kendin veriyorsun.

**Şablonla doğrulama.** nuclei, YAML şablonunda tarif edilen isteği gönderir ve yanıtı **eşleştiricilerle** sınar. Varsayılan birleştirme `or`'dur: kelime eşleştiricisi tutarsa durum kodu önemsizleşir. Yumuşak 404 sayfası istenen yolu sayfaya yazdığı için `/yonetim` yolunda "yonetim" kelimesini aramak, var olmayan bir paneli "bulur". Sağlam bir şablon üç şey ister: `matchers-condition: and`, içeriğe özgü kelimeler ve bilinen yanlış pozitif için `negative: true` bir eşleştirici.

**Saldırgan ne dener?** Küçük ve hızlı listelerle `.git/HEAD`, yedek dosyaları, yönetim panelleri ve sürüm ifşası gibi düşük maliyetli kazanımlara bakar. Tarayıcısını gerçek bir tarayıcı gibi tanıtır: nuclei her istekte rastgele bir tarayıcı User-Agent'ı kullanır. Gerekirse yavaşlar, birden çok adres kullanır ya da `X-Forwarded-For` başlığına sahte bir adres yazar.

**Savunma neden kırılır?** User-Agent'a bakan kural nuclei'yi göremez. Ters vekil arkasında bütün trafik vekilin adresinden gelir: kural soket adresine bakarsa herkes tek bir "istemci" olur. Başlığa körü körüne güvenirse saldırgan kendi yazdığı adresle iz değiştirir. Doğrusu, yalnız **güvendiğin vekilin eklediği** değeri, yani en sağdaki öğeyi kullanmaktır. Toplam sayıya bakan eşik yavaş taramayı kaçırır, meşru yoğun kullanıcıyı da işaretler. Davranışa, yani kısa sürede çok sayıda "bulunamadı" isteğine bakmak daha sağlamdır.

**Blue karşılığı.** Kendi erişim kaydında aynı taramayı yakalarsın. Kayan pencerede "bulunamadı" sayısı eşiği aşan istemci alarm üretir. Alarm, kaç farklı yolun denendiğini ve istemcinin kullandığı bütün User-Agent'ları taşır; analist "tek bir tarayıcı mı, kimliğini değiştiren bir araç mı?" sorusunu buradan sorar.

Kaynaklar: [ffuf · README](https://github.com/ffuf/ffuf), [nuclei · Templates: matchers](https://docs.projectdiscovery.io/templates/reference/matchers), [OWASP WSTG · Enumerate Infrastructure and Application Admin Interfaces](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management_Testing/05-Enumerate_Infrastructure_and_Application_Admin_Interfaces), [MDN · X-Forwarded-For](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Forwarded-For), [MITRE ATT&CK · T1595.003 Wordlist Scanning](https://attack.mitre.org/techniques/T1595/003/). Bu dersteki bütün sayılar yalnız yerel kanıttan gelir.

Purple bağı: pu18 aynı keşif döngüsünün ağ katmanını Nmap ile ölçtü; bu ders uygulama katmanına çıkar. Burada bulunan `.git/HEAD` ve sürüm ifşası pu20'deki gibi kanıtlı bulguya, tespit kuralı da pu21'deki tatbikat defterine bir "beklenen alarm" satırı olarak girer.
:::

::: tahmin Kelime, satır ve en sağdaki adres
Çıktıyı tahmin et, sonra Çalıştır ile karşılaştır.
```python
a = "<html>Sayfa bulunamadi: /backup</html>"
b = "<html>Sayfa bulunamadi: /uploads/eski</html>"
print(len(a.split()), len(b.split()), len(a) == len(b))
xff = "203.0.113.7, 10.66.0.9"
print(xff.split(",")[0], "|", xff.split(",")[-1].strip())
```
???
```cikti
3 3 False
203.0.113.7 | 10.66.0.9
```
Tahmininle gerçek çıktı arasındaki farkı tezgâhta yorum satırı olarak yaz: iki "bulunamadı" sayfasının kelime sayısı neden aynı, uzunluğu neden farklı? XFF'nin hangi ucunu istemcinin kendisi yazabilir? Sonra üç kusurlu başlangıç kodunu çalıştır. Hangisi yalnız 404'ü eleyip yumuşak 404'leri "bulgu" sayıyor, hangisi eşleştiricileri `or` ile bırakıp durum koduna bakmıyor, hangisi XFF'ye körü körüne güvenip toplam istek sayısını eşikle karşılaştırıyor? Önce kendin teşhis et; açıklama çözümün ardından gelir.
:::

::: gorev 1 · ffuf çıktısında gerçek yolu ayıkla
`ffuf_ayikla(ham, taban)`: `ham`, `ffuf -mc all -of json` çıktısının `json.loads` sonucudur; `taban` rastgele, var olmayan bir yola verilen yanıtın imzasıdır: `{"status", "words", "lines"}`. `ham["results"]` içindeki her sonuç için:

- Durum `404` ise ya da `(status, words, lines)` üçlüsü tabanla **aynıysa** (yumuşak 404) ele.
- Kalanlar için `{"yol": "/" + FUZZ (baştaki eğik çizgiler tekillenir), "durum", "uzunluk": length, "yonlendirme": redirectlocation ya da yoksa/boşsa None}` üret.
- Listeyi `yol`'a göre sıralı döndür.

FUZZ boş ya da yalnız `/` ise, sayısal alanlardan biri tamsayı değilse, taban eksik ya da yanlış türdeyse, beklenen bir anahtar yoksa `ValueError`. **Uzunluk** imzaya katılmaz: yumuşak 404 sayfası istenen yolu sayfaya yazdığı için uzunluğu her istekte değişir.

```starter
# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def ffuf_ayikla(ham,taban):
    out=[]
    for r in ham["results"]:
        if r["status"]==404:continue
        out.append({"yol":"/"+r["input"]["FUZZ"],"durum":r["status"],"uzunluk":r["length"],"yonlendirme":r["redirectlocation"]})
    return out

import json
from pathlib import Path
v=json.loads(Path("kesif/ornekler.json").read_text(encoding="utf-8"))
for b in ffuf_ayikla(v["ffuf"],v["taban"]):print(b)
```

```solution
def ffuf_ayikla(ham,taban):
    try:
        if not isinstance(ham["results"],list):raise ValueError("tür")
        imza=(taban["status"],taban["words"],taban["lines"])
        if any(not isinstance(x,int) for x in imza):raise ValueError("taban")
        out=[]
        for r in ham["results"]:
            kelime=r["input"]["FUZZ"]
            if not kelime.strip("/") or not all(isinstance(r[k],int) for k in ("status","words","lines","length")):raise ValueError("sonuç")
            if r["status"]==404 or (r["status"],r["words"],r["lines"])==imza:continue
            out.append({"yol":"/"+kelime.lstrip("/"),"durum":r["status"],"uzunluk":r["length"],"yonlendirme":r.get("redirectlocation") or None})
    except (KeyError,TypeError,AttributeError):raise ValueError("bozuk ffuf çıktısı")
    return sorted(out,key=lambda x:x["yol"])

import json
from pathlib import Path
v=json.loads(Path("kesif/ornekler.json").read_text(encoding="utf-8"))
for b in ffuf_ayikla(v["ffuf"],v["taban"]):print(b)
```

```test
need('ffuf_ayikla')
def sinama1(f):
    try:
        def R(k,st,ln,w,l,yon=None):
            r={"input":{"FUZZ":k},"status":st,"length":ln,"words":w,"lines":l}
            if yon is not None:r["redirectlocation"]=yon
            return r
        tb={"status":200,"words":3,"lines":1}
        h={"results":[R("x1",200,30,3,1),R("api/surum",200,39,1,1),R("admin",302,0,1,1,"/giris"),R("/zaten",200,31,3,1),R("eski",404,10,2,1),R("/.git/HEAD",200,21,3,2,""),R("sayfa",200,30,3,3),R("bos",500,0,0,0)]}
        bek=[{"yol":"/.git/HEAD","durum":200,"uzunluk":21,"yonlendirme":None},{"yol":"/admin","durum":302,"uzunluk":0,"yonlendirme":"/giris"},
             {"yol":"/api/surum","durum":200,"uzunluk":39,"yonlendirme":None},{"yol":"/bos","durum":500,"uzunluk":0,"yonlendirme":None},{"yol":"/sayfa","durum":200,"uzunluk":30,"yonlendirme":None}]
        if f(h,tb)!=bek:return False
        if f({"results":[R("a",404,9,2,1),R("b",200,50,5,2)],"config":{}},{"status":404,"words":2,"lines":1})!=[{"yol":"/b","durum":200,"uzunluk":50,"yonlendirme":None}]:return False
        if f({"results":[]},tb)!=[]:return False
        if f({"results":[R("a",301,0,1,1,"/a/"),R("a",200,9,3,1)]},{"status":301,"words":1,"lines":1})!=[{"yol":"/a","durum":200,"uzunluk":9,"yonlendirme":None}]:return False
        for a in (([],tb),({},tb),(None,tb),({"results":None},tb),({"results":["x"]},tb),({"results":[{"status":200,"length":1,"words":1,"lines":1}]},tb),
                  ({"results":[R("",200,1,1,1)]},tb),({"results":[R("/",200,1,1,1)]},tb),({"results":[R(5,200,1,1,1)]},tb),({"results":[R("a","200",1,1,1)]},tb),({"results":[R("a",200,1,None,1)]},tb),
                  ({"results":[]},{"status":200,"words":3}),({"results":[]},{"status":200,"words":"3","lines":1}),({"results":[]},None)):
            try:f(*a);return False
            except ValueError:pass
        return True
    except Exception:return False
ok(sinama1(ffuf_ayikla),"404 ve yumuşak 404 imzası elenir, yol ve yönlendirme biçimi, sıralama, bozuk çıktı reddi")
def _bos(h,t):
    try:return ffuf_ayikla(h,t)
    except ValueError:return []
for ad,mut in [("sırasız",lambda h,t:list(reversed(ffuf_ayikla(h,t)))),("yönlendirme boş metin",lambda h,t:[dict(b,yonlendirme=b["yonlendirme"] or "") for b in ffuf_ayikla(h,t)]),("bozukta boş",_bos)]:
    ok(not sinama1(mut),"mutant reddedildi: "+ad)
```

```setup
import sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_kesif_lab import hazirla
hazirla()
```

```hint
Yalnız 404'ü elemek yetmez; bu sunucu bulunamayan sayfaya 200 döner. Uzunluk değil, kelime ve satır sayısı sabit kalır.
```
:::

::: anlat Şablon bir iddiadır
Bir nuclei şablonu "bu yanıt şu özellikleri taşıyorsa açık vardır" diyen bir iddiadır. İddia ne kadar dar ve içeriğe özgüyse yanlış pozitif o kadar azdır: sürüm ifşasında ürün adı **ve** sürüm alanı birlikte, `.git/HEAD`'de `ref: refs/heads/` dizisi aranır. Negatif eşleştirici, bilinen bir gürültüyü ("Sayfa bulunamadi") açıkça dışarıda bırakır. Genel şablon depoları binlerce iddia taşır; bu ders kendi iddianı yazmayı ve yanlış iddianın gerçek koşuda nasıl yanıldığını göstermeyi seçer.
:::

::: gorev 2 · Kendi nuclei şablonunu kur
`sablon_kur(kimlik, yol, kelimeler, onem, haric=())`: nuclei'nin YAML şablonunu Python sözlüğü olarak üret (lab onu JSON olarak yazar; YAML, JSON'u da okur).

- `id` = `kimlik`; yalnız küçük harf, rakam ve tek tirelerle ayrılmış parçalar (`pafta-surum-ifsasi`).
- `info` = `{"name": kimlik, "author": "pafta-ogrenci", "severity": onem}`; `onem` `info`, `low`, `medium`, `high`, `critical`'dan biri.
- `http` tek öğeli liste: `method` `GET`, `path` `["{{BaseURL}}" + yol]`, `matchers-condition` `"and"`.
- `matchers` sırasıyla: durum `[200]`; gövdede **bütün** `kelimeler` (`condition: and`); `haric` boş değilse gövdede `haric` kelimeleri için `negative: true` bir kelime eşleştirici.

`yol` `/` ile başlamalı, boşluk ya da `{{` içermemeli. `kelimeler` boş olmayan, `haric` boş olabilen; ikisi de boş olmayan string'lerden oluşan liste ya da demet. Kurallardan biri bozulursa `ValueError`. Listeler çıktıda `list` olur.

```starter
# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def sablon_kur(kimlik,yol,kelimeler,onem,haric=()):
    return {"id":kimlik,"info":{"name":kimlik,"author":"pafta-ogrenci","severity":onem},
            "http":[{"method":"GET","path":["{{BaseURL}}"+yol],"matchers":[{"type":"word","words":list(kelimeler)}]}]}

import json
from pathlib import Path
v=json.loads(Path("kesif/ornekler.json").read_text(encoding="utf-8"))
print(json.dumps(sablon_kur(*v["sablon"]),ensure_ascii=False))
```

```solution
import re
ONEM=("info","low","medium","high","critical")
def sablon_kur(kimlik,yol,kelimeler,onem,haric=()):
    if not isinstance(kimlik,str) or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*",kimlik):raise ValueError("kimlik")
    if not isinstance(yol,str) or not yol.startswith("/") or "{{" in yol or any(c.isspace() for c in yol):raise ValueError("yol")
    for liste in (kelimeler,haric):
        if not isinstance(liste,(list,tuple)) or any(not isinstance(k,str) or not k for k in liste):raise ValueError("kelime listesi")
    if not kelimeler or onem not in ONEM:raise ValueError("kelime ya da önem")
    eslestir=[{"type":"status","status":[200]},{"type":"word","part":"body","words":list(kelimeler),"condition":"and"}]
    if haric:eslestir.append({"type":"word","part":"body","words":list(haric),"negative":True})
    return {"id":kimlik,"info":{"name":kimlik,"author":"pafta-ogrenci","severity":onem},
            "http":[{"method":"GET","path":["{{BaseURL}}"+yol],"matchers-condition":"and","matchers":eslestir}]}

import json
from pathlib import Path
v=json.loads(Path("kesif/ornekler.json").read_text(encoding="utf-8"))
print(json.dumps(sablon_kur(*v["sablon"]),ensure_ascii=False))
```

```test
need('sablon_kur')
def sinama2(f):
    try:
        s=f("pafta-x","/a/b",("k1","k2"),"low",["Sayfa bulunamadi"])
        bek={"id":"pafta-x","info":{"name":"pafta-x","author":"pafta-ogrenci","severity":"low"},
             "http":[{"method":"GET","path":["{{BaseURL}}/a/b"],"matchers-condition":"and","matchers":[{"type":"status","status":[200]},{"type":"word","part":"body","words":["k1","k2"],"condition":"and"},
                     {"type":"word","part":"body","words":["Sayfa bulunamadi"],"negative":True}]}]}
        if s!=bek:return False
        s=f("x9","/.git/HEAD",["ref: refs/heads/"],"critical")
        if s["http"][0]["matchers"]!=[{"type":"status","status":[200]},{"type":"word","part":"body","words":["ref: refs/heads/"],"condition":"and"}] or s["info"]["severity"]!="critical" or s["id"]!="x9":return False
        if f("a-b-c","/",["x"],"info",())["http"][0]["path"]!=["{{BaseURL}}/"]:return False
        for a in ((5,"/a",["k"],"low"),("Pafta","/a",["k"],"low"),("pafta_x","/a",["k"],"low"),("-x","/a",["k"],"low"),("x-","/a",["k"],"low"),("a--b","/a",["k"],"low"),("","/a",["k"],"low"),
                  ("x",5,["k"],"low"),("x","a",["k"],"low"),("x","/a b",["k"],"low"),("x","/{{x}}",["k"],"low"),("x","/a\t",["k"],"low"),
                  ("x","/a",[],"low"),("x","/a",[""],"low"),("x","/a","abc","low"),("x","/a",[1],"low"),("x","/a",None,"low"),("x","/a",["k"],"orta"),("x","/a",["k"],None),
                  ("x","/a",["k"],"low",[""]),("x","/a",["k"],"low","x"),("x","/a",["k"],"low",None)):
            try:f(*a);return False
            except ValueError:pass
        return True
    except Exception:return False
ok(sinama2(sablon_kur),"durum + kelime (and) + negatif eşleştirici, kimlik/yol/önem doğrulaması")
def _neg_yok(*a):
    s=sablon_kur(*a);s["http"][0]["matchers"]=[m for m in s["http"][0]["matchers"] if not m.get("negative")];return s
def _veya(*a):
    s=sablon_kur(*a);s["http"][0]["matchers-condition"]="or";return s
def _bos(*a):
    try:return sablon_kur(*a)
    except ValueError:return {}
for ad,mut in [("negatif eşleştirici yok",_neg_yok),("koşul or",_veya),("bozukta boş şablon",_bos)]:
    ok(not sinama2(mut),"mutant reddedildi: "+ad)
```

```setup
import sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_kesif_lab import hazirla
hazirla()
```

```hint
Eşleştiriciler varsayılan olarak `or` ile birleşir. Yumuşak 404 sayfası istenen yolu sayfaya yazar: yolun kendisini kelime olarak aramak tehlikelidir.
```
:::

::: anlat Kayan pencere neden?
"Son bir saatte 100'den fazla bulunamadı" gibi toplam sayı kuralı iki yönde yanılır. Bir günlük yoğun kullanıcıyı yakalar, 10 dakikaya yayılmış bir taramayı da zamanlamaya göre kaçırabilir. Kayan pencere hızı ölçer: herhangi bir 2 saniyelik dilimde kaç "bulunamadı" isteği var? İki işaretçili yöntem bunu sıralı zamanlar üzerinde tek geçişte hesaplar. Pencerenin sınırı bilerek dahildir. Sınırın hangi tarafta olduğu ders kitabı ayrıntısı gibi görünür, ama eşik tam sınırdayken alarmın çalıp çalmayacağını belirler.
:::

::: gorev 3 · Erişim kaydından taramayı tespit et
`tarama_tespit(kayitlar, esik, pencere, guvenilir)`: her kayıt `t` (saniye), `kaynak` (soket adresi), `xff` (X-Forwarded-For ya da `None`), `yol`, `bulunamadi` (bool) ve `ua` taşır.

- **İstemci:** `kaynak` `guvenilir` vekiller arasındaysa ve `xff` boş olmayan bir string'se, `xff`'nin **en sağdaki** öğesi (virgülle ayrılmış, boşlukları kırpılmış); yoksa `kaynak`.
- Her istemci için `bulunamadi` olan isteklerin zamanlarında, uzunluğu `pencere` saniye olan kayan pencereye (iki uç dahil: `t_son - t_ilk <= pencere`) sığan **en çok** istek sayısını bul.
- Bu sayı `esik`'e ulaşan her istemci için `{"istemci", "en_cok", "farkli_yol": bulunamayan farklı yol sayısı, "ilk", "son": bulunamayan ilk ve son istek zamanı, "ua": istemcinin bütün isteklerindeki farklı User-Agent'lar, yoksa "-", sıralı}` üret.
- Listeyi `istemci`'ye göre sıralı döndür.

`esik` 1 ya da daha büyük tamsayı, `pencere` pozitif sayı, `guvenilir` liste/demet/küme olmalı; kayıtta `t` sayı, `kaynak` string, `bulunamadi` bool olmalı; aksi hâlde `ValueError`.

```starter
# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def tarama_tespit(kayitlar,esik,pencere,guvenilir):
    sayac={}
    for k in kayitlar:
        istemci=k.get("xff") or k["kaynak"]
        sayac.setdefault(istemci,[]).append(k)
    return [{"istemci":i,"en_cok":len(v),"farkli_yol":len({k["yol"] for k in v}),"ilk":v[0]["t"],"son":v[-1]["t"],"ua":[v[0]["ua"]]} for i,v in sayac.items() if len(v)>=esik]

import json
from pathlib import Path
v=json.loads(Path("kesif/ornekler.json").read_text(encoding="utf-8"))
for a in tarama_tespit(v["kayitlar"],v["esik"],v["pencere"],v["guvenilir"]):print(a)
```

```solution
def tarama_tespit(kayitlar,esik,pencere,guvenilir):
    if (not isinstance(kayitlar,list) or not isinstance(esik,int) or esik<1 or not isinstance(pencere,(int,float))
            or pencere<=0 or not isinstance(guvenilir,(list,tuple,set))):raise ValueError("parametre")
    olay={}
    try:
        for k in kayitlar:
            if not isinstance(k["t"],(int,float)) or not isinstance(k["kaynak"],str) or not isinstance(k["bulunamadi"],bool):raise ValueError("kayıt")
            xff=k.get("xff")
            istemci=xff.split(",")[-1].strip() if k["kaynak"] in guvenilir and isinstance(xff,str) and xff.strip() else k["kaynak"]
            o=olay.setdefault(istemci,{"t":[],"yol":set(),"ua":set()})
            o["ua"].add(k.get("ua") or "-")
            if k["bulunamadi"]:
                o["t"].append(k["t"]);o["yol"].add(k["yol"])
    except (KeyError,TypeError,AttributeError):raise ValueError("bozuk kayıt")
    alarm=[]
    for istemci,o in olay.items():
        t=sorted(o["t"]);en,j=0,0
        for i in range(len(t)):
            while t[i]-t[j]>pencere:j+=1
            en=max(en,i-j+1)
        if en>=esik:alarm.append({"istemci":istemci,"en_cok":en,"farkli_yol":len(o["yol"]),"ilk":t[0],"son":t[-1],"ua":sorted(o["ua"])})
    return sorted(alarm,key=lambda a:a["istemci"])

import json
from pathlib import Path
v=json.loads(Path("kesif/ornekler.json").read_text(encoding="utf-8"))
for a in tarama_tespit(v["kayitlar"],v["esik"],v["pencere"],v["guvenilir"]):print(a)
```

```test
need('tarama_tespit')
def sinama3(f):
    try:
        def K(t,kaynak,yol,bul,xff=None,ua="u"):return {"t":t,"kaynak":kaynak,"xff":xff,"yol":yol,"durum":200,"bulunamadi":bul,"ua":ua}
        P="10.0.0.1"
        L=[K(0,P,"/a",True,"6.6.6.6","s1"),K(0.5,P,"/b",True,"6.6.6.6","s1"),K(1,P,"/c",True,"6.6.6.6","s1"),K(1.5,P,"/d",True,"203.0.113.7, 6.6.6.6","s2"),K(2,P,"/a",True,"203.0.113.7,6.6.6.6","s2"),K(10,P,"/e",True,"203.0.113.7, 6.6.6.6","s2"),
           K(3,P,"/z",False,"6.6.6.6","s3"),K(0,P,"/u1",True,"1.1.1.1, 2.2.2.2"),K(1,P,"/u2",True,"1.1.1.1, 2.2.2.2"),K(1.2,P,"/",False,"1.1.1.1, 2.2.2.2"),
           K(0,"9.9.9.9","/x1",True,"6.6.6.6",None),K(0.1,"9.9.9.9","/x2",True,"6.6.6.6",None),K(0.2,"9.9.9.9","/x3",True,"6.6.6.6",None),K(0.3,"9.9.9.9","/x4",True,"6.6.6.6",None),K(0.4,"9.9.9.9","/x5",True,"6.6.6.6",None),
           K(5,P,"/q",True,"",None)]
        a6={"istemci":"6.6.6.6","en_cok":5,"farkli_yol":5,"ilk":0,"son":10,"ua":["s1","s2","s3"]}
        a9={"istemci":"9.9.9.9","en_cok":5,"farkli_yol":5,"ilk":0,"son":0.4,"ua":["-"]}
        if f(L,5,2.0,[P])!=[a6,a9]:return False
        if f(L[::-1],5,2,(P,))!=[a6,a9]:return False
        if f(L,5,1.9,{P})!=[a9]:return False
        if f(L,6,2.0,[P])!=[]:return False
        r=f(L,5,2.0,[])
        if [x["istemci"] for x in r]!=[P,"9.9.9.9"] or r[0]["en_cok"]!=7 or r[0]["farkli_yol"]!=8 or r[0]["ua"]!=["-","s1","s2","s3","u"] or (r[0]["ilk"],r[0]["son"])!=(0,10):return False
        if f([K(5,P,"/q",True,"",None),K(6,P,"/r",True,"  ",None)],1,1,[P])!=[{"istemci":P,"en_cok":2,"farkli_yol":2,"ilk":5,"son":6,"ua":["-"]}]:return False
        if f([],1,1,[])!=[] or f([K(1,"a","/x",True)],1,0.5,[])!=[{"istemci":"a","en_cok":1,"farkli_yol":1,"ilk":1,"son":1,"ua":["u"]}]:return False
        for a in ((L,0,2.0,[P]),(L,"5",2.0,[P]),(L,5,0,[P]),(L,5,"2",[P]),(L,5,2.0,P),(None,5,2.0,[P]),([{"kaynak":"a","bulunamadi":True,"yol":"/"}],1,1,[]),
                  ([K("1","a","/",True)],1,1,[]),([K(1,None,"/",True)],1,1,[]),([K(1,"a","/","evet")],1,1,[]),(["x"],1,1,[]),([{"t":1,"kaynak":"a","bulunamadi":True}],1,1,[])):
            try:f(*a);return False
            except ValueError:pass
        return True
    except Exception:return False
ok(sinama3(tarama_tespit),"güvenilir vekil ve XFF, kayan pencere sınırı, farklı yol, UA, geçersiz girdi")
def _bos(*a):
    try:return tarama_tespit(*a)
    except ValueError:return []
for ad,mut in [("sırasız",lambda *a:tarama_tespit(*a)[::-1]),("ua sırasız",lambda *a:[dict(x,ua=x["ua"][::-1]) for x in tarama_tespit(*a)]),("bozukta boş",_bos)]:
    ok(not sinama3(mut),"mutant reddedildi: "+ad)
```

```setup
import sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_kesif_lab import hazirla
hazirla()
```

```hint
XFF'nin en solu istemcinin kendi yazdığı değerdir; güvendiğin vekilin eklediği en sağdakidir. Pencereyi iki işaretçiyle kaydır.
```
:::

::: anlat Hata vitrini · yazar koşusu
Yazar son görevi referans işlevlerle ve `validate` ile birçok kez çalıştırdı (Python 3.13, Windows). Makine yüküne göre ffuf 0,2–1,6 sn, nuclei 0,3–2,9 sn sürdü. Vekile hiçbir koşuda dış istek gelmedi.

- **ffuf:** `-mc all` ile 25 kelimenin 25'i de yanıt döndürdü. Taban imzası `200 / 3 kelime / 1 satır` ile ayıklanınca geriye beş gerçek yol kaldı: `/.git/HEAD`, `/admin` (302 → `/giris`), `/api/surum`, `/urunler`, `/yedek`.
- **nuclei:** Senin üç şablonundan ikisi gerçek ifşayı buldu (`/api/surum`, `/.git/HEAD`). `/yonetim` şablonu **eşleşmedi**, çünkü yol yok. Negatif eşleştiricisiz "saf" eşi aynı yolda **eşleşti**: yumuşak 404 sayfası "yonetim" kelimesini kendisi yazıyordu.
- **Tespit:** Alarm yalnız `10.66.0.9` için üretildi: 2 sn'lik pencerede en çok 21–22 "bulunamadı" isteği. Sayı, kalibrasyon isteğinin pencereye düşüp düşmediğine göre koşudan koşuya değişti. Bu istemcinin User-Agent listesinde ffuf'un kendi adı, kalibrasyon isteğinin adı ve nuclei'nin rastgele seçtiği birkaç tarayıcı adı vardı. Meşru kullanıcının tek yazım hatası alarm üretmedi.
- **Vekile güvenilmezse:** Aynı kayıtta güvenilir vekil listesi boş bırakılınca bütün trafik `127.0.0.1`'e yığıldı ve alarm vekilin kendisi için çaldı.

Kendi cümlenle açıkla: tarayıcı `X-Forwarded-For: 10.20.0.5` yazarak meşru kullanıcının adresini taklit etseydi, bu labdaki tespit hangi adresi görürdü? Gerçek bir ters vekil bu başlığı nasıl işlemelidir?
:::

::: gorev Gerçek deney · Kendi sunucunu tara, kendi kaydında yakala
Üç işlevi birleştir. Alttaki `calistir` satırı gerçek deneyi başlatır; silme. Koşu kendi `127.0.0.1` sunucusunu açar: bulunamayan sayfaya 200 dönen küçük bir "Pafta Market". Sunucu ters vekil arkasındaymış gibi her isteği X-Forwarded-For ile kaydeder. Sıra şöyledir: önce meşru bir kullanıcı (10.20.0.5) birkaç sayfa gezer. Sonra tarayıcı istemci (10.66.0.9) rastgele bir yolla taban imzasını alır ve `.deps` altındaki sabit sürümlü **ffuf**'u `kesif/kelimeler.txt` ile çalıştırır. Ardından **nuclei** yalnız senin `sablon_kur` ile ürettiğin üç şablonla ve karşılaştırma için negatif eşleştiricisiz bir "saf" şablonla koşar (`-duc`, genel şablon deposu yok). Son olarak erişim kaydı senin `tarama_tespit`'ine verilir (eşik 5, pencere 2 sn, güvenilir vekil `127.0.0.1`). Araçlar, her isteği kaydedip reddeden yerel bir vekil üzerinden koşar; dış ağa çıkma denemesi kanıta yazılır. Run deneme kanıtı yazar, Check ayrıca kabul kanıtını yazar; yol stdout'ta görünür.

```starter
import json
import re
# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def ffuf_ayikla(ham,taban):
    out=[]
    for r in ham["results"]:
        if r["status"]==404:continue
        out.append({"yol":"/"+r["input"]["FUZZ"],"durum":r["status"],"uzunluk":r["length"],"yonlendirme":r["redirectlocation"]})
    return out

# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def sablon_kur(kimlik,yol,kelimeler,onem,haric=()):
    return {"id":kimlik,"info":{"name":kimlik,"author":"pafta-ogrenci","severity":onem},
            "http":[{"method":"GET","path":["{{BaseURL}}"+yol],"matchers":[{"type":"word","words":list(kelimeler)}]}]}

# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def tarama_tespit(kayitlar,esik,pencere,guvenilir):
    sayac={}
    for k in kayitlar:
        istemci=k.get("xff") or k["kaynak"]
        sayac.setdefault(istemci,[]).append(k)
    return [{"istemci":i,"en_cok":len(v),"farkli_yol":len({k["yol"] for k in v}),"ilk":v[0]["t"],"son":v[-1]["t"],"ua":[v[0]["ua"]]} for i,v in sayac.items() if len(v)>=esik]

from purple_kesif_lab import calistir
calistir(ffuf_ayikla,sablon_kur,tarama_tespit)
```

```solution
import json
import re
def ffuf_ayikla(ham,taban):
    try:
        if not isinstance(ham["results"],list):raise ValueError("tür")
        imza=(taban["status"],taban["words"],taban["lines"])
        if any(not isinstance(x,int) for x in imza):raise ValueError("taban")
        out=[]
        for r in ham["results"]:
            kelime=r["input"]["FUZZ"]
            if not kelime.strip("/") or not all(isinstance(r[k],int) for k in ("status","words","lines","length")):raise ValueError("sonuç")
            if r["status"]==404 or (r["status"],r["words"],r["lines"])==imza:continue
            out.append({"yol":"/"+kelime.lstrip("/"),"durum":r["status"],"uzunluk":r["length"],"yonlendirme":r.get("redirectlocation") or None})
    except (KeyError,TypeError,AttributeError):raise ValueError("bozuk ffuf çıktısı")
    return sorted(out,key=lambda x:x["yol"])

ONEM=("info","low","medium","high","critical")
def sablon_kur(kimlik,yol,kelimeler,onem,haric=()):
    if not isinstance(kimlik,str) or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*",kimlik):raise ValueError("kimlik")
    if not isinstance(yol,str) or not yol.startswith("/") or "{{" in yol or any(c.isspace() for c in yol):raise ValueError("yol")
    for liste in (kelimeler,haric):
        if not isinstance(liste,(list,tuple)) or any(not isinstance(k,str) or not k for k in liste):raise ValueError("kelime listesi")
    if not kelimeler or onem not in ONEM:raise ValueError("kelime ya da önem")
    eslestir=[{"type":"status","status":[200]},{"type":"word","part":"body","words":list(kelimeler),"condition":"and"}]
    if haric:eslestir.append({"type":"word","part":"body","words":list(haric),"negative":True})
    return {"id":kimlik,"info":{"name":kimlik,"author":"pafta-ogrenci","severity":onem},
            "http":[{"method":"GET","path":["{{BaseURL}}"+yol],"matchers-condition":"and","matchers":eslestir}]}

def tarama_tespit(kayitlar,esik,pencere,guvenilir):
    if (not isinstance(kayitlar,list) or not isinstance(esik,int) or esik<1 or not isinstance(pencere,(int,float))
            or pencere<=0 or not isinstance(guvenilir,(list,tuple,set))):raise ValueError("parametre")
    olay={}
    try:
        for k in kayitlar:
            if not isinstance(k["t"],(int,float)) or not isinstance(k["kaynak"],str) or not isinstance(k["bulunamadi"],bool):raise ValueError("kayıt")
            xff=k.get("xff")
            istemci=xff.split(",")[-1].strip() if k["kaynak"] in guvenilir and isinstance(xff,str) and xff.strip() else k["kaynak"]
            o=olay.setdefault(istemci,{"t":[],"yol":set(),"ua":set()})
            o["ua"].add(k.get("ua") or "-")
            if k["bulunamadi"]:
                o["t"].append(k["t"]);o["yol"].add(k["yol"])
    except (KeyError,TypeError,AttributeError):raise ValueError("bozuk kayıt")
    alarm=[]
    for istemci,o in olay.items():
        t=sorted(o["t"]);en,j=0,0
        for i in range(len(t)):
            while t[i]-t[j]>pencere:j+=1
            en=max(en,i-j+1)
        if en>=esik:alarm.append({"istemci":istemci,"en_cok":en,"farkli_yol":len(o["yol"]),"ilk":t[0],"son":t[-1],"ua":sorted(o["ua"])})
    return sorted(alarm,key=lambda a:a["istemci"])

from purple_kesif_lab import calistir
calistir(ffuf_ayikla,sablon_kur,tarama_tespit)
```

```test
need('ffuf_ayikla');need('sablon_kur');need('tarama_tespit')
from purple_kesif_lab import kod_koruma,calistir
ok(kod_koruma(src),'kaynak koruması: referans/dinamik kod/özel öznitelik yok')
if not kod_koruma(src):stop()
def sinama1(f):
    try:
        def R(k,st,ln,w,l,yon=None):
            r={"input":{"FUZZ":k},"status":st,"length":ln,"words":w,"lines":l}
            if yon is not None:r["redirectlocation"]=yon
            return r
        tb={"status":200,"words":3,"lines":1}
        h={"results":[R("x1",200,30,3,1),R("api/surum",200,39,1,1),R("admin",302,0,1,1,"/giris"),R("/zaten",200,31,3,1),R("eski",404,10,2,1),R("/.git/HEAD",200,21,3,2,""),R("sayfa",200,30,3,3),R("bos",500,0,0,0)]}
        bek=[{"yol":"/.git/HEAD","durum":200,"uzunluk":21,"yonlendirme":None},{"yol":"/admin","durum":302,"uzunluk":0,"yonlendirme":"/giris"},
             {"yol":"/api/surum","durum":200,"uzunluk":39,"yonlendirme":None},{"yol":"/bos","durum":500,"uzunluk":0,"yonlendirme":None},{"yol":"/sayfa","durum":200,"uzunluk":30,"yonlendirme":None}]
        if f(h,tb)!=bek:return False
        if f({"results":[R("a",404,9,2,1),R("b",200,50,5,2)],"config":{}},{"status":404,"words":2,"lines":1})!=[{"yol":"/b","durum":200,"uzunluk":50,"yonlendirme":None}]:return False
        if f({"results":[]},tb)!=[]:return False
        if f({"results":[R("a",301,0,1,1,"/a/"),R("a",200,9,3,1)]},{"status":301,"words":1,"lines":1})!=[{"yol":"/a","durum":200,"uzunluk":9,"yonlendirme":None}]:return False
        for a in (([],tb),({},tb),(None,tb),({"results":None},tb),({"results":["x"]},tb),({"results":[{"status":200,"length":1,"words":1,"lines":1}]},tb),
                  ({"results":[R("",200,1,1,1)]},tb),({"results":[R("/",200,1,1,1)]},tb),({"results":[R(5,200,1,1,1)]},tb),({"results":[R("a","200",1,1,1)]},tb),({"results":[R("a",200,1,None,1)]},tb),
                  ({"results":[]},{"status":200,"words":3}),({"results":[]},{"status":200,"words":"3","lines":1}),({"results":[]},None)):
            try:f(*a);return False
            except ValueError:pass
        return True
    except Exception:return False
def sinama2(f):
    try:
        s=f("pafta-x","/a/b",("k1","k2"),"low",["Sayfa bulunamadi"])
        bek={"id":"pafta-x","info":{"name":"pafta-x","author":"pafta-ogrenci","severity":"low"},
             "http":[{"method":"GET","path":["{{BaseURL}}/a/b"],"matchers-condition":"and","matchers":[{"type":"status","status":[200]},{"type":"word","part":"body","words":["k1","k2"],"condition":"and"},
                     {"type":"word","part":"body","words":["Sayfa bulunamadi"],"negative":True}]}]}
        if s!=bek:return False
        s=f("x9","/.git/HEAD",["ref: refs/heads/"],"critical")
        if s["http"][0]["matchers"]!=[{"type":"status","status":[200]},{"type":"word","part":"body","words":["ref: refs/heads/"],"condition":"and"}] or s["info"]["severity"]!="critical" or s["id"]!="x9":return False
        if f("a-b-c","/",["x"],"info",())["http"][0]["path"]!=["{{BaseURL}}/"]:return False
        for a in ((5,"/a",["k"],"low"),("Pafta","/a",["k"],"low"),("pafta_x","/a",["k"],"low"),("-x","/a",["k"],"low"),("x-","/a",["k"],"low"),("a--b","/a",["k"],"low"),("","/a",["k"],"low"),
                  ("x",5,["k"],"low"),("x","a",["k"],"low"),("x","/a b",["k"],"low"),("x","/{{x}}",["k"],"low"),("x","/a\t",["k"],"low"),
                  ("x","/a",[],"low"),("x","/a",[""],"low"),("x","/a","abc","low"),("x","/a",[1],"low"),("x","/a",None,"low"),("x","/a",["k"],"orta"),("x","/a",["k"],None),
                  ("x","/a",["k"],"low",[""]),("x","/a",["k"],"low","x"),("x","/a",["k"],"low",None)):
            try:f(*a);return False
            except ValueError:pass
        return True
    except Exception:return False
def sinama3(f):
    try:
        def K(t,kaynak,yol,bul,xff=None,ua="u"):return {"t":t,"kaynak":kaynak,"xff":xff,"yol":yol,"durum":200,"bulunamadi":bul,"ua":ua}
        P="10.0.0.1"
        L=[K(0,P,"/a",True,"6.6.6.6","s1"),K(0.5,P,"/b",True,"6.6.6.6","s1"),K(1,P,"/c",True,"6.6.6.6","s1"),K(1.5,P,"/d",True,"203.0.113.7, 6.6.6.6","s2"),K(2,P,"/a",True,"203.0.113.7,6.6.6.6","s2"),K(10,P,"/e",True,"203.0.113.7, 6.6.6.6","s2"),
           K(3,P,"/z",False,"6.6.6.6","s3"),K(0,P,"/u1",True,"1.1.1.1, 2.2.2.2"),K(1,P,"/u2",True,"1.1.1.1, 2.2.2.2"),K(1.2,P,"/",False,"1.1.1.1, 2.2.2.2"),
           K(0,"9.9.9.9","/x1",True,"6.6.6.6",None),K(0.1,"9.9.9.9","/x2",True,"6.6.6.6",None),K(0.2,"9.9.9.9","/x3",True,"6.6.6.6",None),K(0.3,"9.9.9.9","/x4",True,"6.6.6.6",None),K(0.4,"9.9.9.9","/x5",True,"6.6.6.6",None),
           K(5,P,"/q",True,"",None)]
        a6={"istemci":"6.6.6.6","en_cok":5,"farkli_yol":5,"ilk":0,"son":10,"ua":["s1","s2","s3"]}
        a9={"istemci":"9.9.9.9","en_cok":5,"farkli_yol":5,"ilk":0,"son":0.4,"ua":["-"]}
        if f(L,5,2.0,[P])!=[a6,a9]:return False
        if f(L[::-1],5,2,(P,))!=[a6,a9]:return False
        if f(L,5,1.9,{P})!=[a9]:return False
        if f(L,6,2.0,[P])!=[]:return False
        r=f(L,5,2.0,[])
        if [x["istemci"] for x in r]!=[P,"9.9.9.9"] or r[0]["en_cok"]!=7 or r[0]["farkli_yol"]!=8 or r[0]["ua"]!=["-","s1","s2","s3","u"] or (r[0]["ilk"],r[0]["son"])!=(0,10):return False
        if f([K(5,P,"/q",True,"",None),K(6,P,"/r",True,"  ",None)],1,1,[P])!=[{"istemci":P,"en_cok":2,"farkli_yol":2,"ilk":5,"son":6,"ua":["-"]}]:return False
        if f([],1,1,[])!=[] or f([K(1,"a","/x",True)],1,0.5,[])!=[{"istemci":"a","en_cok":1,"farkli_yol":1,"ilk":1,"son":1,"ua":["u"]}]:return False
        for a in ((L,0,2.0,[P]),(L,"5",2.0,[P]),(L,5,0,[P]),(L,5,"2",[P]),(L,5,2.0,P),(None,5,2.0,[P]),([{"kaynak":"a","bulunamadi":True,"yol":"/"}],1,1,[]),
                  ([K("1","a","/",True)],1,1,[]),([K(1,None,"/",True)],1,1,[]),([K(1,"a","/","evet")],1,1,[]),(["x"],1,1,[]),([{"t":1,"kaynak":"a","bulunamadi":True}],1,1,[])):
            try:f(*a);return False
            except ValueError:pass
        return True
    except Exception:return False
tamam=sinama1(ffuf_ayikla) and sinama2(sablon_kur) and sinama3(tarama_tespit)
ok(tamam,"üç işlev gizli verilerle doğru")
def _bos(h,t):
    try:return ffuf_ayikla(h,t)
    except ValueError:return []
for ad,mut in [("sırasız",lambda h,t:list(reversed(ffuf_ayikla(h,t)))),("yönlendirme boş metin",lambda h,t:[dict(b,yonlendirme=b["yonlendirme"] or "") for b in ffuf_ayikla(h,t)]),("bozukta boş",_bos)]:
    ok(not sinama1(mut),"mutant reddedildi: "+ad)
def _neg_yok(*a):
    s=sablon_kur(*a);s["http"][0]["matchers"]=[m for m in s["http"][0]["matchers"] if not m.get("negative")];return s
def _veya(*a):
    s=sablon_kur(*a);s["http"][0]["matchers-condition"]="or";return s
def _bos(*a):
    try:return sablon_kur(*a)
    except ValueError:return {}
for ad,mut in [("negatif eşleştirici yok",_neg_yok),("koşul or",_veya),("bozukta boş şablon",_bos)]:
    ok(not sinama2(mut),"mutant reddedildi: "+ad)
def _bos(*a):
    try:return tarama_tespit(*a)
    except ValueError:return []
for ad,mut in [("sırasız",lambda *a:tarama_tespit(*a)[::-1]),("ua sırasız",lambda *a:[dict(x,ua=x["ua"][::-1]) for x in tarama_tespit(*a)]),("bozukta boş",_bos)]:
    ok(not sinama3(mut),"mutant reddedildi: "+ad)
if not tamam:stop()
k=calistir(ffuf_ayikla,sablon_kur,tarama_tespit,kabul=True)
eq(k['kaynak'],'gercek','gerçek ffuf ve nuclei koşusu')
ok(k['kabul'],'gerçek kabul: ayıklama, şablonlar ve tespit referansla aynı')
ok(k['cleanup'],'yalnız kendi sunucusu, vekili ve geçici klasörü kapandı')
eq(k['dis_istek'],[],'araçlar dış ağa istek göndermedi')
eq([a['istemci'] for a in k['alarm']],['10.66.0.9'],'alarm yalnız tarayan istemci için')
eq([a['istemci'] for a in k['guvenilmez_vekil_alarm']],['127.0.0.1'],'XFF güvenilmezse bütün trafik vekilin adresine yığılır')
ok(any(n['sablon']=='pafta-yonetim-saf' for n in k['nuclei']) and not any(n['sablon']=='pafta-yonetim-paneli' for n in k['nuclei']),'negatif eşleştiricisiz şablon yumuşak 404\'te yanıldı, seninki yanılmadı')
```

```setup
import sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_kesif_lab import hazirla
hazirla()
```

```hint
Önceki üç işlevi aynen birleştir. Kanıtta `ua` listesine bak: nuclei kendini hangi tarayıcı gibi tanıttı?
```
:::

::: anlat Sınır
Bu ders sabit sürümlü ffuf ve nuclei'yi yalnız kendi `127.0.0.1` sunucusunda gerçekten koşturur; yumuşak 404'ü taban imzasıyla ayıklar, kendi negatif eşleştiricili nuclei şablonlarını kurar ve ters vekil arkasındaki erişim kaydında taramayı kayan pencereyle tespit eder. Gerçek hedefleri, genel şablon depolarını, kimlik doğrulamalı ya da yavaş/dağıtık taramayı, WAF'ları ve SIEM entegrasyonunu kapsamaz.
:::
