---
id: pu21
title: Tatbikat Yönetimi · RoE Kapısı, Kırmızı/Mavi Eşleştirme ve Sonuç Tablosu
summary: Purple tatbikatında her eylemi kurallara (RoE) karşı kapıda denetle; pu19 yerel labında izinli eylemleri gerçekten yürüt, kapsam dışı yem dinleyicisine tek bağlantı bile gitmediğini kanıtla, mavi alarmları kırmızı eylemlerle eşleştir ve teknik bazlı sonuç tablosu çıkar.
timeout: 30
---

::: anlat Tatbikatı kim yönetir?
| Sahada ne olur | Bu ders ne kullanır | Ne söyleyemez? |
|---|---|---|
| Purple tatbikatı yazılı kurallarla (rules of engagement, RoE) yürür: hangi hedef, hangi teknik, hangi zaman aralığı, ne zaman durulur. Ekipler eylemleri ve alarmları ortak bir takip aracında (ör. açık kaynak VECTR) eşleştirir | pu19'un yerel `127.0.0.1` labı, kapsam dışı bir yem dinleyicisi, dokuz eylemlik plan, lab denetim kaydından alarm üreten iki basit mavi kural | Gerçek bir kurumun onay sürecini, iletişim planını, VECTR'ı ya da bir SIEM'i göstermez |
| Teknikler MITRE ATT&CK kimlikleriyle yazılır (ör. T1190, T1078, T1110.001) | Aynı kimlikler; alt teknik yazımı `T1110.001` | Bir tekniğin bütün varyantlarının tespit edildiğini kanıtlamaz |

> [!NOT]
> İlk üç görev `tatbikat/plan.json` dosyasını okur; plan, alarmlar ve kayıtlar **sentetiktir**, hedefler kurgusaldır ve hiçbirine bağlantı açılmaz. Setup her Çalıştır/Kontrol Et adımında eksik dosyaları kopyalar; **kalıcılık yoktur**. Dosyayı görmek için başlangıç kodundaki `print` satırlarını kullan. Son görev yalnız kendi açtığı iki yerel dinleyiciye bağlanır ve işi bitince ikisini de kapatır. Dış hedef, gerçek hesap, paket ya da indirme yoktur.

**RoE neden bir kapıdır, bir belge değil?** Kurallar yalnız bir PDF'te kalırsa, operatör yorgunken yanlış IP'yi yazar ve tatbikat bir üretim sistemine dokunur. Bu derste her eylem gönderilmeden önce bir işlevden geçer: hedef kapsamda mı, teknik yasak mı, zaman penceresi uygun mu? Kapı "hayır" derse eylem **hiç** gönderilmez. Bunu kanıtlamanın yolu, kapsam dışındaki bir yem dinleyicisine gelen bağlantıları saymaktır: sayı sıfır olmalıdır.

**Kapının üç tuzağı.** (1) **Metin içinde arama:** `"127.0.0.1" in hedef` ifadesi `127.0.0.10`'u da kapsam içi sayar; hedef adı ve port birebir karşılaştırılmalıdır. (2) **Alt teknik:** RoE `T1499`'u (Endpoint Denial of Service) yasaklıyorsa `T1499.004` da yasaktır. Ama yalnız `T1485.001` yasaksa ana teknik `T1485` serbest kalabilir. (3) **Zaman:** ISO metinlerini dizgi olarak karşılaştırmak farklı saat dilimlerinde yanlış sonuç verir; bitiş anı pencereye dahil değildir.

**Eşleştirme (deconfliction).** Mavi ekip bir alarm gördüğünde "bu tatbikat mı, gerçek saldırı mı?" diye sorar. Kırmızı ekip de "denediğim teknik görüldü mü?" diye sorar. İkisini eşleştirmek için aynı teknik, aynı hedef ve eylemden **sonra** gelen kısa bir pencere gerekir. Eylemden önce gelen alarm o eylemin sonucu olamaz. Bir alarm iki eylemi birden "tespit" edemez. Hiçbir eylemle eşleşmeyen alarm ya yanlış alarmdır ya da tatbikat dışı gerçek bir olaydır ve ayrıca incelenir.

**Saldırgan ne dener, savunma neden kırılır?** Bu derste "saldırgan" tatbikatın kırmızı ekibidir; amacı tespiti ölçmektir, kuralları aşmak değil. Gerçek saldırgan ise tam da tatbikatın kör noktalarını kullanır. Geçerli hesapla giriş (T1078) imza tabanlı bir kurala hiç takılmaz. Savunmanın kırıldığı yer genelde kuralın kendisidir: "kullanıcı adında tırnak varsa SQLi alarmı" kuralı, adında kesme işareti olan meşru bir kullanıcıda da çalışır. Sonuç tablosu bu yüzden yalnız "tespit oranı" vermez; önlenen, tespit edilen ve kaçırılan eylemleri ayrı sayar. Kapsam dışı bir planlama hatası varsa tatbikat yöneticisine "durdur ve planı düzelt" der.

Kaynaklar: [MITRE ATT&CK · T1190](https://attack.mitre.org/techniques/T1190/), [T1078](https://attack.mitre.org/techniques/T1078/), [T1110.001](https://attack.mitre.org/techniques/T1110/001/), [T1499](https://attack.mitre.org/techniques/T1499/), [NIST SP 800-115](https://csrc.nist.gov/pubs/sp/800/115/final). Bu dersteki bütün sayılar yalnız yerel kanıttan gelir.

Purple bağı: pu02 olay zaman çizelgesini, pu13 Atomic/Caldera ile öykünme planını anlatır; bu ders o planın güvenli yürütülmesini ve sonucunun tabloya dökülmesini ölçer. pu20 aynı labın bulgularını rapora çevirir.
:::

::: tahmin Metin mi, zaman mı?
Çıktıyı tahmin et, sonra Çalıştır ile karşılaştır.
```python
from datetime import datetime
a, b = "2026-11-04T10:00:00+03:00", "2026-11-04T08:00:00+00:00"
print(a < b, datetime.fromisoformat(a) < datetime.fromisoformat(b))
print("127.0.0.1" in "127.0.0.10:8080", "127.0.0.10:8080".rsplit(":", 1))
```
???
```cikti
False True
True ['127.0.0.10', '8080']
```
Tahmininle gerçek çıktı arasındaki farkı tezgâhta yorum satırı olarak yaz: İstanbul saatiyle 10:00 ile UTC 08:00'den hangisi önce gelir? `127.0.0.10` neden kapsam içi görünüyor? Sonra üç kusurlu başlangıç kodunu çalıştır. Hangisi benzer IP'yi ve alt tekniği kaçırıp zamanı metin olarak karşılaştırıyor, hangisi eylemden önceki alarmı ve başka hedefin alarmını eşleştirip aynı alarmı iki kez kullanıyor, hangisi reddedilen eylemleri denenmiş sayıp önlenen eylemi "kaçırıldı" diyor? Önce kendin teşhis et; açıklama çözümün ardından gelir.
:::

::: gorev 1 · RoE kapısı
`kapsam_kontrol(eylem, roe)`: `eylem` tam olarak `id` (dolu string), `hedef`, `teknik`, `zaman`; `roe` tam olarak `hedefler` (liste), `yasak_teknikler` (liste), `baslangic`, `bitis`. Hedef biçimi `ad:port`: `ad` yalnız harf, rakam, nokta ve tire içerir; `port` 1–5 rakam ya da (yalnız RoE'de) `*`. Teknik biçimi `T` + 4 rakam, isteğe bağlı `.` + 3 rakam (ör. `T1110.001`). Zamanlar saat dilimi içeren ISO 8601 metinleridir (`datetime.fromisoformat`; saat dilimi yoksa geçersiz). Herhangi bir kural bozulursa `ValueError`. Karar sırası: (1) eylemin `ad`'ı bir RoE hedefinin adıyla **birebir** aynı değilse ya da port uyuşmuyorsa (`*` her portu kapsar) `kapsam-disi-hedef`; (2) teknik ya da ana tekniği (noktadan önceki kısım) yasaklıysa `yasak-teknik`; (3) zaman `[baslangic, bitis)` aralığında değilse (bitiş hariç) `zaman-disi`. `{"karar": "izinli" | "red", "neden": None | neden}` döndür. Girdi değişmez.

```starter
# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def kapsam_kontrol(eylem,roe):
    if not any(h.split(":")[0] in eylem["hedef"] for h in roe["hedefler"]):neden="kapsam-disi-hedef"
    elif eylem["teknik"] in roe["yasak_teknikler"]:neden="yasak-teknik"
    elif not roe["baslangic"]<=eylem["zaman"]<=roe["bitis"]:neden="zaman-disi"
    else:neden=None
    return {"karar":"red" if neden else "izinli","neden":neden}

import json
from pathlib import Path
v=json.loads(Path("tatbikat/plan.json").read_text(encoding="utf-8"))
for e in v["eylemler"]:print(e["id"],e["hedef"],e["teknik"],e["zaman"],"→",kapsam_kontrol(e,v["roe"]))
```

```solution
import re
from datetime import datetime
def kapsam_kontrol(eylem,roe):
    def zaman(s):
        if not isinstance(s,str):raise ValueError("zaman")
        z=datetime.fromisoformat(s)
        if z.tzinfo is None:raise ValueError("saat dilimi")
        return z
    def hedef(s):
        if not isinstance(s,str) or not re.fullmatch(r"[0-9A-Za-z.\-]+:(\d{1,5}|\*)",s):raise ValueError("hedef")
        return s.split(":")
    if not isinstance(eylem,dict) or set(eylem)!={"id","hedef","teknik","zaman"}:raise ValueError("eylem")
    if not isinstance(roe,dict) or set(roe)!={"hedefler","yasak_teknikler","baslangic","bitis"}:raise ValueError("roe")
    if not isinstance(eylem["id"],str) or not eylem["id"] or not isinstance(eylem["teknik"],str) or not re.fullmatch(r"T\d{4}(\.\d{3})?",eylem["teknik"]):raise ValueError("eylem alanı")
    host,port=hedef(eylem["hedef"])
    if port=="*":raise ValueError("eylem hedefi joker olamaz")
    if not isinstance(roe["hedefler"],list) or not isinstance(roe["yasak_teknikler"],list):raise ValueError("roe listesi")
    izin=[hedef(h) for h in roe["hedefler"]]
    t,b,s=zaman(eylem["zaman"]),zaman(roe["baslangic"]),zaman(roe["bitis"])
    if not any(host==h and p in ("*",port) for h,p in izin):neden="kapsam-disi-hedef"
    elif eylem["teknik"] in roe["yasak_teknikler"] or eylem["teknik"].split(".")[0] in roe["yasak_teknikler"]:neden="yasak-teknik"
    elif not b<=t<s:neden="zaman-disi"
    else:neden=None
    return {"karar":"red" if neden else "izinli","neden":neden}

import json
from pathlib import Path
v=json.loads(Path("tatbikat/plan.json").read_text(encoding="utf-8"))
for e in v["eylemler"]:print(e["id"],e["hedef"],e["teknik"],e["zaman"],"→",kapsam_kontrol(e,v["roe"]))
```

```test
need('kapsam_kontrol')
def sinama1(f):
    import copy
    try:
        R={"hedefler":["127.0.0.1:8080","lab.local:*","10.0.0.5:443"],"yasak_teknikler":["T1499","T1485.001"],"baslangic":"2026-11-04T09:00:00+03:00","bitis":"2026-11-04T18:00:00+03:00"}
        def e(h,t,z,i="E"):return {"id":i,"hedef":h,"teknik":t,"zaman":z}
        I={"karar":"izinli","neden":None};K={"karar":"red","neden":"kapsam-disi-hedef"};Y={"karar":"red","neden":"yasak-teknik"};Z={"karar":"red","neden":"zaman-disi"}
        V=[(e("127.0.0.1:8080","T1190","2026-11-04T10:00:00+03:00"),I),(e("lab.local:22","T1078","2026-11-04T10:00:00+03:00"),I),(e("lab.local:65535","T1110.001","2026-11-04T07:00:00+00:00"),I),
           (e("127.0.0.10:8080","T1190","2026-11-04T10:00:00+03:00"),K),(e("127.0.0.1:80","T1190","2026-11-04T10:00:00+03:00"),K),(e("127.0.0.1:808","T1190","2026-11-04T10:00:00+03:00"),K),
           (e("sub.lab.local:22","T1190","2026-11-04T10:00:00+03:00"),K),(e("10.0.0.5:4430","T1190","2026-11-04T10:00:00+03:00"),K),(e("LAB.local:22","T1190","2026-11-04T10:00:00+03:00"),K),
           (e("127.0.0.1:8080","T1499","2026-11-04T10:00:00+03:00"),Y),(e("127.0.0.1:8080","T1499.004","2026-11-04T10:00:00+03:00"),Y),(e("127.0.0.1:8080","T1485.001","2026-11-04T10:00:00+03:00"),Y),
           (e("127.0.0.1:8080","T1485","2026-11-04T10:00:00+03:00"),I),(e("127.0.0.1:8080","T1485.002","2026-11-04T10:00:00+03:00"),I),
           (e("127.0.0.1:8080","T1190","2026-11-04T09:00:00+03:00"),I),(e("127.0.0.1:8080","T1190","2026-11-04T18:00:00+03:00"),Z),(e("127.0.0.1:8080","T1190","2026-11-04T08:59:59+03:00"),Z),
           (e("127.0.0.1:8080","T1190","2026-11-04T14:59:59+00:00"),I),(e("127.0.0.1:8080","T1190","2026-11-04T15:00:00+00:00"),Z),(e("127.0.0.1:8080","T1190","2026-11-04T05:30:00+00:00"),Z),(e("127.0.0.1:8080","T1190","2026-11-04T06:30:00+00:00"),I),
           (e("127.0.0.1:8080","T1190","2026-11-05T01:00:00+10:00"),Z),(e("127.0.0.1:8080","T1190","2026-11-04T16:00:00+10:00"),I),(e("127.0.0.1:8080","T1190","2026-11-04T05:59:59+00:00"),Z),
           (e("127.0.0.9:1","T1499","2026-11-05T10:00:00+03:00"),K),(e("127.0.0.1:8080","T1499","2026-11-05T10:00:00+03:00"),Y)]
        for x,b in V:
            x0=copy.deepcopy(x);r0=copy.deepcopy(R)
            if f(x,R)!=b or x!=x0 or R!=r0:return False
        T=lambda **d:dict(V[0][0],**d)
        for bx,br in ((None,R),(V[0][0],None),(T(ek=1),R),({"id":"E","hedef":"127.0.0.1:8080","teknik":"T1190"},R),(T(id=""),R),(T(id=1),R),(T(teknik="t1190"),R),(T(teknik="T190"),R),(T(teknik="T1190.1"),R),
                      (T(teknik=None),R),(T(hedef="127.0.0.1"),R),(T(hedef="127.0.0.1:*"),R),(T(hedef="127.0.0.1:abc"),R),(T(hedef="127.0.0.1:123456"),R),(T(hedef="http://x:80"),R),(T(hedef=None),R),(T(zaman="2026-11-04T10:00:00"),R),
                      (T(zaman="dün"),R),(T(zaman=None),R),(V[0][0],dict(R,ek=1)),(V[0][0],dict(R,hedefler="127.0.0.1:8080")),(V[0][0],dict(R,hedefler=["127.0.0.1"])),(V[0][0],dict(R,yasak_teknikler="T1499")),
                      (V[0][0],dict(R,baslangic="2026-11-04T09:00:00")),(V[0][0],dict(R,bitis=5)),(V[0][0],{k:v for k,v in R.items() if k!="bitis"})):
            try:f(bx,br);return False
            except ValueError:pass
        return True
    except Exception:return False
ok(sinama1(kapsam_kontrol),"tam hedef eşleşmesi, alt teknik yasağı, saat dilimli yarı açık pencere, öncelik ve geçersiz girdi")
for ad,mut in [("alt teknik yasaktan kaçıyor",lambda e,r:{"karar":"izinli","neden":None} if kapsam_kontrol(e,r)["neden"]=="yasak-teknik" and e["teknik"] not in r["yasak_teknikler"] else kapsam_kontrol(e,r)),("bitiş dahil",lambda e,r:{"karar":"izinli","neden":None} if kapsam_kontrol(e,r)["neden"]=="zaman-disi" and e["zaman"]==r["bitis"] else kapsam_kontrol(e,r)),("benzer IP kapsamda",lambda e,r:{"karar":"izinli","neden":None} if e["hedef"].startswith("127.0.0.1") and kapsam_kontrol(e,r)["neden"]=="kapsam-disi-hedef" else kapsam_kontrol(e,r))]:
    ok(not sinama1(mut),"mutant reddedildi: "+ad)
```

```setup
import sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_tatbikat_lab import hazirla
hazirla()
```

```hint
Hedefi metin içinde arama; `ad` ve `port`'u ayırıp birebir karşılaştır. Zamanları metin olarak değil `datetime` olarak karşılaştır.
```
:::

::: anlat Alarm, eylemin gölgesidir
Eşleştirme bir zaman çizelgesi problemidir. Eylemleri zaman sırasıyla gez. Her eylem için kullanılmamış, aynı teknik ve aynı hedefe ait, pencere içindeki en erken alarmı seç. Pencere çok genişse, sonraki bir eylemin alarmı öncekine "çalınır". Çok darsa, gecikmeli gelen alarm kaçırılmış sayılır. Pencereyi raporda yaz; aynı veriyle farklı pencere farklı tespit oranı verir.
:::

::: gorev 2 · Kırmızı eylem ile mavi alarmı eşleştir
`eslestir(eylemler, alarmlar, pencere_sn)`: iki liste; her öğe tam olarak `id` (listede benzersiz dolu string), `hedef`, `teknik` (string), `zaman` (saat dilimli ISO 8601). `pencere_sn` int ya da float (bool değil), ≥ 0. Aksi hâlde `ValueError`. Eylemler `(zaman, id)` sırasıyla işlenir. Her eylem için aday alarmlar: henüz kullanılmamış, `teknik` ve `hedef` birebir aynı, `0 ≤ alarm_zamanı - eylem_zamanı ≤ pencere_sn`. En erken aday (eşitlikte küçük `id`) seçilir ve bir daha kullanılmaz; aday yoksa `None`. `{"eslesme": {eylem_id: alarm_id | None}, "eslesmeyen_alarm": [sıralı id]}` döndür. Girdi değişmez.

```starter
from datetime import datetime
# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def eslestir(eylemler,alarmlar,pencere_sn):
    eslesme={}
    for e in eylemler:
        t=datetime.fromisoformat(e["zaman"])
        aday=[a["id"] for a in alarmlar if a["teknik"]==e["teknik"] and abs((datetime.fromisoformat(a["zaman"])-t).total_seconds())<=pencere_sn]
        eslesme[e["id"]]=aday[0] if aday else None
    return {"eslesme":eslesme,"eslesmeyen_alarm":[a["id"] for a in alarmlar if a["id"] not in eslesme.values()]}

import json
from pathlib import Path
v=json.loads(Path("tatbikat/plan.json").read_text(encoding="utf-8"))
print(eslestir(v["yurutulen"],v["alarmlar"],v["pencere_sn"]))
```

```solution
from datetime import datetime,timedelta
def eslestir(eylemler,alarmlar,pencere_sn):
    def zaman(x,ad):
        if not isinstance(x,dict) or set(x)!={"id","hedef","teknik","zaman"} or not isinstance(x["id"],str) or not x["id"] or not isinstance(x["hedef"],str) or not isinstance(x["teknik"],str) or not isinstance(x["zaman"],str):raise ValueError(ad)
        z=datetime.fromisoformat(x["zaman"])
        if z.tzinfo is None:raise ValueError("saat dilimi")
        return z
    if type(pencere_sn) not in (int,float) or pencere_sn<0:raise ValueError("pencere")
    if not isinstance(eylemler,list) or not isinstance(alarmlar,list):raise ValueError("liste")
    ez={};az={}
    for e in eylemler:
        z=zaman(e,"eylem")
        if e["id"] in ez:raise ValueError("eylem id")
        ez[e["id"]]=z
    for a in alarmlar:
        z=zaman(a,"alarm")
        if a["id"] in az:raise ValueError("alarm id")
        az[a["id"]]=z
    kullanilan=set();eslesme={}
    for e in sorted(eylemler,key=lambda e:(ez[e["id"]],e["id"])):
        aday=sorted((az[a["id"]],a["id"]) for a in alarmlar if a["id"] not in kullanilan and a["teknik"]==e["teknik"] and a["hedef"]==e["hedef"]
                    and timedelta(0)<=az[a["id"]]-ez[e["id"]]<=timedelta(seconds=pencere_sn))
        eslesme[e["id"]]=aday[0][1] if aday else None
        if aday:kullanilan.add(aday[0][1])
    return {"eslesme":eslesme,"eslesmeyen_alarm":sorted(a for a in az if a not in kullanilan)}

import json
from pathlib import Path
v=json.loads(Path("tatbikat/plan.json").read_text(encoding="utf-8"))
print(eslestir(v["yurutulen"],v["alarmlar"],v["pencere_sn"]))
```

```test
need('eslestir')
def sinama2(f):
    import copy
    try:
        def x(i,h,t,z):return {"id":i,"hedef":h,"teknik":t,"zaman":"2026-11-04T10:00:"+z+"+03:00"}
        H="127.0.0.1:8080";G="127.0.0.1:9090"
        E=[x("E3",H,"T1190","00.900000"),x("E1",H,"T1190","00"),x("E2",H,"T1190","00.800000"),x("E4",H,"T1110.001","00"),x("E5",G,"T1190","00"),x("E6",H,"T1078","00")]
        A=[x("AL9",H,"T1190","01"),x("AL2",H,"T1190","01"),x("AL3",H,"T1190","09"),x("AL4",H,"T1110","00"),x("AL5",H,"T1190","00.500000"),x("AL6",G,"T1190","05"),x("AL7",G,"T1190","05.000001"),x("AL8",H,"T1078","59")]
        e0=copy.deepcopy(E);a0=copy.deepcopy(A)
        r=f(E,A,5)
        if E!=e0 or A!=a0:return False
        if r!={"eslesme":{"E1":"AL5","E4":None,"E5":"AL6","E6":None,"E2":"AL2","E3":"AL9"},"eslesmeyen_alarm":["AL3","AL4","AL7","AL8"]}:return False
        if f(list(reversed(E)),list(reversed(A)),5)!=r:return False
        if f([x("Q1",H,"T1190","00")],[x("Q2",H,"T1190","00")],0)!={"eslesme":{"Q1":"Q2"},"eslesmeyen_alarm":[]}:return False
        if f(E,A,0)["eslesme"]!={"E1":None,"E2":None,"E3":None,"E4":None,"E5":None,"E6":None}:return False
        if f(E,A,0.5)["eslesme"]["E1"]!="AL5" or f([E[0]],[A[2]],9)["eslesme"]!={"E3":"AL3"} or f([E[0]],[A[2]],8)["eslesme"]!={"E3":None}:return False
        if f([dict(E[1],zaman="2026-11-04T07:00:00+00:00")],[dict(A[4],zaman="2026-11-04T10:00:03+03:00")],5)!={"eslesme":{"E1":"AL5"},"eslesmeyen_alarm":[]}:return False
        if f([],A,5)!={"eslesme":{},"eslesmeyen_alarm":sorted(a["id"] for a in A)} or f(E,[],5)["eslesmeyen_alarm"]!=[]:return False
        for bad in ((None,A,5),(E,None,5),(tuple(E),A,5),(E,A,-1),(E,A,True),(E,A,"5"),(E,A,None),(E+[E[0]],A,5),(E,A+[A[0]],5),([dict(E[0],ek=1)],A,5),([dict(E[0],id="")],A,5),([dict(E[0],zaman="2026-11-04T10:00:00")],A,5),
                    (E,[dict(A[0],zaman="yarın")],5),(E,[dict(A[0],hedef=5)],5),([dict(E[0],teknik=None)],A,5),([None],A,5),(E,[{"id":"Q","hedef":H,"teknik":"T1190"}],5),([dict(E[0],zaman=None)],A,5)):
            try:f(*bad);return False
            except ValueError:pass
        return True
    except Exception:return False
ok(sinama2(eslestir),"zaman sırası, pencere sınırları, tek kullanım, hedef/teknik eşitliği ve geçersiz girdi")
for ad,mut in [("alarm tekrar kullanılıyor",lambda E,A,p:dict(eslestir(E,A,p),eslesmeyen_alarm=[])),("sırasız eşleşmeyen",lambda E,A,p:dict(eslestir(E,A,p),eslesmeyen_alarm=list(reversed(eslestir(E,A,p)["eslesmeyen_alarm"])))),("ilk eylem eşleşmesiz",lambda E,A,p:{"eslesme":dict(eslestir(E,A,p)["eslesme"],**({min(eslestir(E,A,p)["eslesme"]):None} if E else {})),"eslesmeyen_alarm":eslestir(E,A,p)["eslesmeyen_alarm"]})]:
    ok(not sinama2(mut),"mutant reddedildi: "+ad)
```

```setup
import sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_tatbikat_lab import hazirla
hazirla()
```

```hint
Eylemi beklemeden önceki alarm o eylemin sonucu olamaz. Bir alarm iki eylemi birden 'tespit edemez'.
```
:::

::: anlat Sonuç tablosu: önlendi, tespit edildi, kaçırıldı
Purple tatbikatının sonucu teknik bazında üç sayıdır. **Önlendi:** kontrol eylemi durdurdu (ör. 401). **Tespit edildi:** mavi tarafta eşleşen bir alarm var. **Kaçırıldı:** ikisi de yok; asıl iş listesi burasıdır. Reddedilen eylemler hiç denenmediği için bu sayılara girmez, ayrı listelenir. Kapsam dışı bir hedef planlanmışsa bu bir plan hatasıdır ve tatbikat yöneticisine "durdur" denir.
:::

::: gorev 3 · Tatbikat özeti
`tatbikat_ozeti(kayitlar)`: boş olmayan liste; her kayıt tam olarak `id` (benzersiz dolu string), `teknik` (dolu string), `karar`, `neden`, `onlendi`, `tespit`. `karar == "izinli"` ise `neden` `None`, `onlendi` ve `tespit` bool; `karar == "red"` ise `neden` üç nedenden biri, `onlendi` ve `tespit` `None`. Başka her durum `ValueError`. `teknikler`: izinli kayıtlar için teknik adına göre sıralı `{"denenen", "onlendi", "tespit", "kacirildi"}`; `kacirildi` = ne önlenen ne tespit edilen. `reddedilen`: her üç neden için sıralı kimlik listesi (boş olabilir). `tespit_orani`: tespit edilen izinli kayıtlar / izinli kayıtlar (izinli yoksa `None`). `durdur`: en az bir `kapsam-disi-hedef` reddi var mı. Girdi değişmez.

```starter
# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def tatbikat_ozeti(kayitlar):
    tek={};red={"kapsam-disi-hedef":[],"yasak-teknik":[],"zaman-disi":[]}
    for k in kayitlar:
        t=tek.setdefault(k["teknik"],{"denenen":0,"onlendi":0,"tespit":0,"kacirildi":0})
        t["denenen"]+=1;t["onlendi"]+=bool(k["onlendi"]);t["tespit"]+=bool(k["tespit"]);t["kacirildi"]+=not k["tespit"]
        if k["karar"]=="red":red[k["neden"]].append(k["id"])
    return {"teknikler":tek,"reddedilen":red,"tespit_orani":sum(t["tespit"] for t in tek.values())/len(kayitlar),"durdur":any(red.values())}

import json
from pathlib import Path
v=json.loads(Path("tatbikat/plan.json").read_text(encoding="utf-8"))
print(json.dumps(tatbikat_ozeti(v["kayitlar"]),ensure_ascii=False))
```

```solution
def tatbikat_ozeti(kayitlar):
    nedenler=("kapsam-disi-hedef","yasak-teknik","zaman-disi")
    if not isinstance(kayitlar,list) or not kayitlar:raise ValueError("liste")
    ids=set();tek={};red={n:[] for n in nedenler}
    for k in kayitlar:
        if not isinstance(k,dict) or set(k)!={"id","teknik","karar","neden","onlendi","tespit"}:raise ValueError("şema")
        if not isinstance(k["id"],str) or not k["id"] or k["id"] in ids or not isinstance(k["teknik"],str) or not k["teknik"]:raise ValueError("alan")
        ids.add(k["id"])
        if k["karar"]=="izinli":
            if k["neden"] is not None or type(k["onlendi"]) is not bool or type(k["tespit"]) is not bool:raise ValueError("izinli kayıt")
            t=tek.setdefault(k["teknik"],{"denenen":0,"onlendi":0,"tespit":0,"kacirildi":0})
            t["denenen"]+=1;t["onlendi"]+=k["onlendi"];t["tespit"]+=k["tespit"];t["kacirildi"]+=not k["onlendi"] and not k["tespit"]
        elif k["karar"]=="red":
            if k["neden"] not in nedenler or k["onlendi"] is not None or k["tespit"] is not None:raise ValueError("red kayıt")
            red[k["neden"]].append(k["id"])
        else:raise ValueError("karar")
    denenen=sum(t["denenen"] for t in tek.values())
    return {"teknikler":{t:tek[t] for t in sorted(tek)},"reddedilen":{n:sorted(v) for n,v in red.items()},
            "tespit_orani":sum(t["tespit"] for t in tek.values())/denenen if denenen else None,"durdur":bool(red["kapsam-disi-hedef"])}

import json
from pathlib import Path
v=json.loads(Path("tatbikat/plan.json").read_text(encoding="utf-8"))
print(json.dumps(tatbikat_ozeti(v["kayitlar"]),ensure_ascii=False))
```

```test
need('tatbikat_ozeti')
def sinama3(f):
    import copy
    try:
        def i(k,t,o,s):return {"id":k,"teknik":t,"karar":"izinli","neden":None,"onlendi":o,"tespit":s}
        def r(k,t,n):return {"id":k,"teknik":t,"karar":"red","neden":n,"onlendi":None,"tespit":None}
        K=[i("A2","T1190",False,True),i("A1","T1078",False,False),i("A3","T1190",True,True),i("A4","T1110.001",True,False),i("A9","T1078",False,False),
           r("A6","T1190","kapsam-disi-hedef"),r("A5","T1499","yasak-teknik"),r("A8","T1190","zaman-disi"),r("A7","T1190","kapsam-disi-hedef"),i("B1","T1190",True,False)]
        k0=copy.deepcopy(K);s=f(K)
        if K!=k0:return False
        if s!={"teknikler":{"T1078":{"denenen":2,"onlendi":0,"tespit":0,"kacirildi":2},"T1110.001":{"denenen":1,"onlendi":1,"tespit":0,"kacirildi":0},"T1190":{"denenen":3,"onlendi":2,"tespit":2,"kacirildi":0}},
               "reddedilen":{"kapsam-disi-hedef":["A6","A7"],"yasak-teknik":["A5"],"zaman-disi":["A8"]},"tespit_orani":2/6,"durdur":True}:return False
        if list(s["teknikler"])!=["T1078","T1110.001","T1190"] or f(list(reversed(K)))!=s:return False
        if f([r("X","T1499","yasak-teknik")])!={"teknikler":{},"reddedilen":{"kapsam-disi-hedef":[],"yasak-teknik":["X"],"zaman-disi":[]},"tespit_orani":None,"durdur":False}:return False
        if f([i("Y","T1",True,True),r("Z","T2","zaman-disi")])!={"teknikler":{"T1":{"denenen":1,"onlendi":1,"tespit":1,"kacirildi":0}},"reddedilen":{"kapsam-disi-hedef":[],"yasak-teknik":[],"zaman-disi":["Z"]},"tespit_orani":1.0,"durdur":False}:return False
        T=lambda **d:[dict(K[0],**d)]+K[1:]
        for bad in (None,[],tuple(K),K+[K[0]],T(id=""),T(id=3),T(teknik=""),T(teknik=None),T(karar="belki"),T(neden="yasak-teknik"),T(onlendi=None),T(tespit=1),T(onlendi="evet"),T(ek=1),
                    [{k:v for k,v in K[0].items() if k!="tespit"}]+K[1:],[dict(K[5],neden=None)]+K,[dict(K[5],neden="baska",id="Q")]+K,[dict(K[5],onlendi=False,id="Q")]+K,[dict(K[5],tespit=True,id="Q")]+K,[None]):
            try:f(bad);return False
            except ValueError:pass
        return True
    except Exception:return False
ok(sinama3(tatbikat_ozeti),"teknik sayaçları, kaçırılan tanımı, oran, durdurma ve geçersiz girdi")
for ad,mut in [("kaçırılan = tespitsiz",lambda K:{**tatbikat_ozeti(K),"teknikler":{t:dict(v,kacirildi=v["denenen"]-v["tespit"]) for t,v in tatbikat_ozeti(K)["teknikler"].items()}}),("oran tüm kayıtlardan",lambda K:dict(tatbikat_ozeti(K),tespit_orani=sum(v["tespit"] for v in tatbikat_ozeti(K)["teknikler"].values())/len(K))),("her retle durdur",lambda K:dict(tatbikat_ozeti(K),durdur=any(tatbikat_ozeti(K)["reddedilen"].values())))]:
    ok(not sinama3(mut),"mutant reddedildi: "+ad)
```

```setup
import sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_tatbikat_lab import hazirla
hazirla()
```

```hint
Reddedilen eylem hiç denenmemiştir; oranın paydasına girmez. Önlenen ama tespit edilmeyen bir eylem 'kaçırılmış' değildir.
```
:::

::: anlat Hata vitrini · yazar koşusu
Yazar son görevi referans işlevlerle çalıştırdı. Kapı dokuz eylemden dördünü reddetti: A5 (yasak T1499), A6 ve A7 (kapsam dışı) ve A8 (zaman dışı). Yem dinleyicisine gelen bağlantı sayısı **0**'dı. Yürütülen beş eylem labda yedi gerçek istek üretti.

- **Geçerli hesap görünmez.** A1 ve A9 (T1078) 200 aldı, hiç alarm üretmedi: iki eylem de **kaçırıldı**. Bu bir kural hatası değil, imza tabanlı kuralların doğal kör noktasıdır.
- **Yanlış alarm.** A9'un kullanıcısı adında kesme işareti taşıyan meşru bir hesaptı. "Adında tırnak" kuralı bunun için T1190 alarmı (AL4) üretti. AL4 hiçbir T1190 eylemiyle eşleşmedi ve `eslesmeyen_alarm`'a düştü.
- **Önlendi ama yine de görüldü.** A3 korumalı uçta 401 aldı (önlendi) ve aynı kural alarm üretti (tespit edildi). A2 açık uçta 200 aldı; önlenmedi, yalnız tespit edildi.
- Tespit oranı **3/5 = 0.6** çıktı. Bu sayı tek başına "iyi" ya da "kötü" değildir: hangi tekniklerin kaçırıldığını ve bir yanlış alarm olduğunu söylemeyen bir oran eksiktir.

Kendi cümlenle açıkla: AL4'ü "tatbikatın parçası" diye kapatmak neden hatalı olurdu?
:::

::: gorev Gerçek deney · Yerel labda RoE kapılı tatbikat
Üç işlevi birleştir. Alttaki `calistir` satırı gerçek deneyi başlatır; silme. Her koşu pu19'un yerel `127.0.0.1` labını ve **kapsam dışı** bir yem dinleyicisini açar; RoE yalnız labın portunu kapsar. Dokuz eylemlik plan: A1 meşru giriş (T1078), A2 açık uçta atlatma ve A3 korumalı uçta aynı girdi (T1190), A4 aynı hesaba üç yanlış parola (T1110.001), A5 yasak hizmet dışı bırakma (T1499), A6 yem dinleyicisi (kapsam dışı), A7 `127.0.0.10` (benzer ama kapsam dışı), A8 yarına planlanmış eylem, A9 adında kesme işareti olan meşru hesapla giriş (T1078). Yalnız referans RoE kararının izin verdiği eylemler gerçekten yürütülür; senin kararların ayrıca karşılaştırılır. Mavi kural lab denetim kaydından alarm üretir: kullanıcı adında `'` → T1190; aynı hesaba üçüncü ret → T1110.001. Run deneme kanıtı yazar, Check ayrıca kabul kanıtını yazar; yol stdout'ta görünür. Koşu yalnız kendi dinleyicilerini ve geçici DB'sini açar ve kapatır.

```starter
import re
from datetime import datetime,timedelta
# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def kapsam_kontrol(eylem,roe):
    if not any(h.split(":")[0] in eylem["hedef"] for h in roe["hedefler"]):neden="kapsam-disi-hedef"
    elif eylem["teknik"] in roe["yasak_teknikler"]:neden="yasak-teknik"
    elif not roe["baslangic"]<=eylem["zaman"]<=roe["bitis"]:neden="zaman-disi"
    else:neden=None
    return {"karar":"red" if neden else "izinli","neden":neden}

# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def eslestir(eylemler,alarmlar,pencere_sn):
    eslesme={}
    for e in eylemler:
        t=datetime.fromisoformat(e["zaman"])
        aday=[a["id"] for a in alarmlar if a["teknik"]==e["teknik"] and abs((datetime.fromisoformat(a["zaman"])-t).total_seconds())<=pencere_sn]
        eslesme[e["id"]]=aday[0] if aday else None
    return {"eslesme":eslesme,"eslesmeyen_alarm":[a["id"] for a in alarmlar if a["id"] not in eslesme.values()]}

# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def tatbikat_ozeti(kayitlar):
    tek={};red={"kapsam-disi-hedef":[],"yasak-teknik":[],"zaman-disi":[]}
    for k in kayitlar:
        t=tek.setdefault(k["teknik"],{"denenen":0,"onlendi":0,"tespit":0,"kacirildi":0})
        t["denenen"]+=1;t["onlendi"]+=bool(k["onlendi"]);t["tespit"]+=bool(k["tespit"]);t["kacirildi"]+=not k["tespit"]
        if k["karar"]=="red":red[k["neden"]].append(k["id"])
    return {"teknikler":tek,"reddedilen":red,"tespit_orani":sum(t["tespit"] for t in tek.values())/len(kayitlar),"durdur":any(red.values())}

from purple_tatbikat_lab import calistir
calistir(kapsam_kontrol,eslestir,tatbikat_ozeti)
```

```solution
import re
from datetime import datetime,timedelta
def kapsam_kontrol(eylem,roe):
    def zaman(s):
        if not isinstance(s,str):raise ValueError("zaman")
        z=datetime.fromisoformat(s)
        if z.tzinfo is None:raise ValueError("saat dilimi")
        return z
    def hedef(s):
        if not isinstance(s,str) or not re.fullmatch(r"[0-9A-Za-z.\-]+:(\d{1,5}|\*)",s):raise ValueError("hedef")
        return s.split(":")
    if not isinstance(eylem,dict) or set(eylem)!={"id","hedef","teknik","zaman"}:raise ValueError("eylem")
    if not isinstance(roe,dict) or set(roe)!={"hedefler","yasak_teknikler","baslangic","bitis"}:raise ValueError("roe")
    if not isinstance(eylem["id"],str) or not eylem["id"] or not isinstance(eylem["teknik"],str) or not re.fullmatch(r"T\d{4}(\.\d{3})?",eylem["teknik"]):raise ValueError("eylem alanı")
    host,port=hedef(eylem["hedef"])
    if port=="*":raise ValueError("eylem hedefi joker olamaz")
    if not isinstance(roe["hedefler"],list) or not isinstance(roe["yasak_teknikler"],list):raise ValueError("roe listesi")
    izin=[hedef(h) for h in roe["hedefler"]]
    t,b,s=zaman(eylem["zaman"]),zaman(roe["baslangic"]),zaman(roe["bitis"])
    if not any(host==h and p in ("*",port) for h,p in izin):neden="kapsam-disi-hedef"
    elif eylem["teknik"] in roe["yasak_teknikler"] or eylem["teknik"].split(".")[0] in roe["yasak_teknikler"]:neden="yasak-teknik"
    elif not b<=t<s:neden="zaman-disi"
    else:neden=None
    return {"karar":"red" if neden else "izinli","neden":neden}

def eslestir(eylemler,alarmlar,pencere_sn):
    def zaman(x,ad):
        if not isinstance(x,dict) or set(x)!={"id","hedef","teknik","zaman"} or not isinstance(x["id"],str) or not x["id"] or not isinstance(x["hedef"],str) or not isinstance(x["teknik"],str) or not isinstance(x["zaman"],str):raise ValueError(ad)
        z=datetime.fromisoformat(x["zaman"])
        if z.tzinfo is None:raise ValueError("saat dilimi")
        return z
    if type(pencere_sn) not in (int,float) or pencere_sn<0:raise ValueError("pencere")
    if not isinstance(eylemler,list) or not isinstance(alarmlar,list):raise ValueError("liste")
    ez={};az={}
    for e in eylemler:
        z=zaman(e,"eylem")
        if e["id"] in ez:raise ValueError("eylem id")
        ez[e["id"]]=z
    for a in alarmlar:
        z=zaman(a,"alarm")
        if a["id"] in az:raise ValueError("alarm id")
        az[a["id"]]=z
    kullanilan=set();eslesme={}
    for e in sorted(eylemler,key=lambda e:(ez[e["id"]],e["id"])):
        aday=sorted((az[a["id"]],a["id"]) for a in alarmlar if a["id"] not in kullanilan and a["teknik"]==e["teknik"] and a["hedef"]==e["hedef"]
                    and timedelta(0)<=az[a["id"]]-ez[e["id"]]<=timedelta(seconds=pencere_sn))
        eslesme[e["id"]]=aday[0][1] if aday else None
        if aday:kullanilan.add(aday[0][1])
    return {"eslesme":eslesme,"eslesmeyen_alarm":sorted(a for a in az if a not in kullanilan)}

def tatbikat_ozeti(kayitlar):
    nedenler=("kapsam-disi-hedef","yasak-teknik","zaman-disi")
    if not isinstance(kayitlar,list) or not kayitlar:raise ValueError("liste")
    ids=set();tek={};red={n:[] for n in nedenler}
    for k in kayitlar:
        if not isinstance(k,dict) or set(k)!={"id","teknik","karar","neden","onlendi","tespit"}:raise ValueError("şema")
        if not isinstance(k["id"],str) or not k["id"] or k["id"] in ids or not isinstance(k["teknik"],str) or not k["teknik"]:raise ValueError("alan")
        ids.add(k["id"])
        if k["karar"]=="izinli":
            if k["neden"] is not None or type(k["onlendi"]) is not bool or type(k["tespit"]) is not bool:raise ValueError("izinli kayıt")
            t=tek.setdefault(k["teknik"],{"denenen":0,"onlendi":0,"tespit":0,"kacirildi":0})
            t["denenen"]+=1;t["onlendi"]+=k["onlendi"];t["tespit"]+=k["tespit"];t["kacirildi"]+=not k["onlendi"] and not k["tespit"]
        elif k["karar"]=="red":
            if k["neden"] not in nedenler or k["onlendi"] is not None or k["tespit"] is not None:raise ValueError("red kayıt")
            red[k["neden"]].append(k["id"])
        else:raise ValueError("karar")
    denenen=sum(t["denenen"] for t in tek.values())
    return {"teknikler":{t:tek[t] for t in sorted(tek)},"reddedilen":{n:sorted(v) for n,v in red.items()},
            "tespit_orani":sum(t["tespit"] for t in tek.values())/denenen if denenen else None,"durdur":bool(red["kapsam-disi-hedef"])}

from purple_tatbikat_lab import calistir
calistir(kapsam_kontrol,eslestir,tatbikat_ozeti)
```

```test
need('kapsam_kontrol');need('eslestir');need('tatbikat_ozeti')
from purple_tatbikat_lab import kod_koruma,calistir
ok(kod_koruma(src),'kaynak koruması: referans/dinamik kod/özel öznitelik yok')
if not kod_koruma(src):stop()
def sinama1(f):
    import copy
    try:
        R={"hedefler":["127.0.0.1:8080","lab.local:*","10.0.0.5:443"],"yasak_teknikler":["T1499","T1485.001"],"baslangic":"2026-11-04T09:00:00+03:00","bitis":"2026-11-04T18:00:00+03:00"}
        def e(h,t,z,i="E"):return {"id":i,"hedef":h,"teknik":t,"zaman":z}
        I={"karar":"izinli","neden":None};K={"karar":"red","neden":"kapsam-disi-hedef"};Y={"karar":"red","neden":"yasak-teknik"};Z={"karar":"red","neden":"zaman-disi"}
        V=[(e("127.0.0.1:8080","T1190","2026-11-04T10:00:00+03:00"),I),(e("lab.local:22","T1078","2026-11-04T10:00:00+03:00"),I),(e("lab.local:65535","T1110.001","2026-11-04T07:00:00+00:00"),I),
           (e("127.0.0.10:8080","T1190","2026-11-04T10:00:00+03:00"),K),(e("127.0.0.1:80","T1190","2026-11-04T10:00:00+03:00"),K),(e("127.0.0.1:808","T1190","2026-11-04T10:00:00+03:00"),K),
           (e("sub.lab.local:22","T1190","2026-11-04T10:00:00+03:00"),K),(e("10.0.0.5:4430","T1190","2026-11-04T10:00:00+03:00"),K),(e("LAB.local:22","T1190","2026-11-04T10:00:00+03:00"),K),
           (e("127.0.0.1:8080","T1499","2026-11-04T10:00:00+03:00"),Y),(e("127.0.0.1:8080","T1499.004","2026-11-04T10:00:00+03:00"),Y),(e("127.0.0.1:8080","T1485.001","2026-11-04T10:00:00+03:00"),Y),
           (e("127.0.0.1:8080","T1485","2026-11-04T10:00:00+03:00"),I),(e("127.0.0.1:8080","T1485.002","2026-11-04T10:00:00+03:00"),I),
           (e("127.0.0.1:8080","T1190","2026-11-04T09:00:00+03:00"),I),(e("127.0.0.1:8080","T1190","2026-11-04T18:00:00+03:00"),Z),(e("127.0.0.1:8080","T1190","2026-11-04T08:59:59+03:00"),Z),
           (e("127.0.0.1:8080","T1190","2026-11-04T14:59:59+00:00"),I),(e("127.0.0.1:8080","T1190","2026-11-04T15:00:00+00:00"),Z),(e("127.0.0.1:8080","T1190","2026-11-04T05:30:00+00:00"),Z),(e("127.0.0.1:8080","T1190","2026-11-04T06:30:00+00:00"),I),
           (e("127.0.0.1:8080","T1190","2026-11-05T01:00:00+10:00"),Z),(e("127.0.0.1:8080","T1190","2026-11-04T16:00:00+10:00"),I),(e("127.0.0.1:8080","T1190","2026-11-04T05:59:59+00:00"),Z),
           (e("127.0.0.9:1","T1499","2026-11-05T10:00:00+03:00"),K),(e("127.0.0.1:8080","T1499","2026-11-05T10:00:00+03:00"),Y)]
        for x,b in V:
            x0=copy.deepcopy(x);r0=copy.deepcopy(R)
            if f(x,R)!=b or x!=x0 or R!=r0:return False
        T=lambda **d:dict(V[0][0],**d)
        for bx,br in ((None,R),(V[0][0],None),(T(ek=1),R),({"id":"E","hedef":"127.0.0.1:8080","teknik":"T1190"},R),(T(id=""),R),(T(id=1),R),(T(teknik="t1190"),R),(T(teknik="T190"),R),(T(teknik="T1190.1"),R),
                      (T(teknik=None),R),(T(hedef="127.0.0.1"),R),(T(hedef="127.0.0.1:*"),R),(T(hedef="127.0.0.1:abc"),R),(T(hedef="127.0.0.1:123456"),R),(T(hedef="http://x:80"),R),(T(hedef=None),R),(T(zaman="2026-11-04T10:00:00"),R),
                      (T(zaman="dün"),R),(T(zaman=None),R),(V[0][0],dict(R,ek=1)),(V[0][0],dict(R,hedefler="127.0.0.1:8080")),(V[0][0],dict(R,hedefler=["127.0.0.1"])),(V[0][0],dict(R,yasak_teknikler="T1499")),
                      (V[0][0],dict(R,baslangic="2026-11-04T09:00:00")),(V[0][0],dict(R,bitis=5)),(V[0][0],{k:v for k,v in R.items() if k!="bitis"})):
            try:f(bx,br);return False
            except ValueError:pass
        return True
    except Exception:return False
def sinama2(f):
    import copy
    try:
        def x(i,h,t,z):return {"id":i,"hedef":h,"teknik":t,"zaman":"2026-11-04T10:00:"+z+"+03:00"}
        H="127.0.0.1:8080";G="127.0.0.1:9090"
        E=[x("E3",H,"T1190","00.900000"),x("E1",H,"T1190","00"),x("E2",H,"T1190","00.800000"),x("E4",H,"T1110.001","00"),x("E5",G,"T1190","00"),x("E6",H,"T1078","00")]
        A=[x("AL9",H,"T1190","01"),x("AL2",H,"T1190","01"),x("AL3",H,"T1190","09"),x("AL4",H,"T1110","00"),x("AL5",H,"T1190","00.500000"),x("AL6",G,"T1190","05"),x("AL7",G,"T1190","05.000001"),x("AL8",H,"T1078","59")]
        e0=copy.deepcopy(E);a0=copy.deepcopy(A)
        r=f(E,A,5)
        if E!=e0 or A!=a0:return False
        if r!={"eslesme":{"E1":"AL5","E4":None,"E5":"AL6","E6":None,"E2":"AL2","E3":"AL9"},"eslesmeyen_alarm":["AL3","AL4","AL7","AL8"]}:return False
        if f(list(reversed(E)),list(reversed(A)),5)!=r:return False
        if f([x("Q1",H,"T1190","00")],[x("Q2",H,"T1190","00")],0)!={"eslesme":{"Q1":"Q2"},"eslesmeyen_alarm":[]}:return False
        if f(E,A,0)["eslesme"]!={"E1":None,"E2":None,"E3":None,"E4":None,"E5":None,"E6":None}:return False
        if f(E,A,0.5)["eslesme"]["E1"]!="AL5" or f([E[0]],[A[2]],9)["eslesme"]!={"E3":"AL3"} or f([E[0]],[A[2]],8)["eslesme"]!={"E3":None}:return False
        if f([dict(E[1],zaman="2026-11-04T07:00:00+00:00")],[dict(A[4],zaman="2026-11-04T10:00:03+03:00")],5)!={"eslesme":{"E1":"AL5"},"eslesmeyen_alarm":[]}:return False
        if f([],A,5)!={"eslesme":{},"eslesmeyen_alarm":sorted(a["id"] for a in A)} or f(E,[],5)["eslesmeyen_alarm"]!=[]:return False
        for bad in ((None,A,5),(E,None,5),(tuple(E),A,5),(E,A,-1),(E,A,True),(E,A,"5"),(E,A,None),(E+[E[0]],A,5),(E,A+[A[0]],5),([dict(E[0],ek=1)],A,5),([dict(E[0],id="")],A,5),([dict(E[0],zaman="2026-11-04T10:00:00")],A,5),
                    (E,[dict(A[0],zaman="yarın")],5),(E,[dict(A[0],hedef=5)],5),([dict(E[0],teknik=None)],A,5),([None],A,5),(E,[{"id":"Q","hedef":H,"teknik":"T1190"}],5),([dict(E[0],zaman=None)],A,5)):
            try:f(*bad);return False
            except ValueError:pass
        return True
    except Exception:return False
def sinama3(f):
    import copy
    try:
        def i(k,t,o,s):return {"id":k,"teknik":t,"karar":"izinli","neden":None,"onlendi":o,"tespit":s}
        def r(k,t,n):return {"id":k,"teknik":t,"karar":"red","neden":n,"onlendi":None,"tespit":None}
        K=[i("A2","T1190",False,True),i("A1","T1078",False,False),i("A3","T1190",True,True),i("A4","T1110.001",True,False),i("A9","T1078",False,False),
           r("A6","T1190","kapsam-disi-hedef"),r("A5","T1499","yasak-teknik"),r("A8","T1190","zaman-disi"),r("A7","T1190","kapsam-disi-hedef"),i("B1","T1190",True,False)]
        k0=copy.deepcopy(K);s=f(K)
        if K!=k0:return False
        if s!={"teknikler":{"T1078":{"denenen":2,"onlendi":0,"tespit":0,"kacirildi":2},"T1110.001":{"denenen":1,"onlendi":1,"tespit":0,"kacirildi":0},"T1190":{"denenen":3,"onlendi":2,"tespit":2,"kacirildi":0}},
               "reddedilen":{"kapsam-disi-hedef":["A6","A7"],"yasak-teknik":["A5"],"zaman-disi":["A8"]},"tespit_orani":2/6,"durdur":True}:return False
        if list(s["teknikler"])!=["T1078","T1110.001","T1190"] or f(list(reversed(K)))!=s:return False
        if f([r("X","T1499","yasak-teknik")])!={"teknikler":{},"reddedilen":{"kapsam-disi-hedef":[],"yasak-teknik":["X"],"zaman-disi":[]},"tespit_orani":None,"durdur":False}:return False
        if f([i("Y","T1",True,True),r("Z","T2","zaman-disi")])!={"teknikler":{"T1":{"denenen":1,"onlendi":1,"tespit":1,"kacirildi":0}},"reddedilen":{"kapsam-disi-hedef":[],"yasak-teknik":[],"zaman-disi":["Z"]},"tespit_orani":1.0,"durdur":False}:return False
        T=lambda **d:[dict(K[0],**d)]+K[1:]
        for bad in (None,[],tuple(K),K+[K[0]],T(id=""),T(id=3),T(teknik=""),T(teknik=None),T(karar="belki"),T(neden="yasak-teknik"),T(onlendi=None),T(tespit=1),T(onlendi="evet"),T(ek=1),
                    [{k:v for k,v in K[0].items() if k!="tespit"}]+K[1:],[dict(K[5],neden=None)]+K,[dict(K[5],neden="baska",id="Q")]+K,[dict(K[5],onlendi=False,id="Q")]+K,[dict(K[5],tespit=True,id="Q")]+K,[None]):
            try:f(bad);return False
            except ValueError:pass
        return True
    except Exception:return False
tamam=sinama1(kapsam_kontrol) and sinama2(eslestir) and sinama3(tatbikat_ozeti)
ok(tamam,"üç sözleşme gizli verilerle doğru")
for ad,mut in [("alt teknik yasaktan kaçıyor",lambda e,r:{"karar":"izinli","neden":None} if kapsam_kontrol(e,r)["neden"]=="yasak-teknik" and e["teknik"] not in r["yasak_teknikler"] else kapsam_kontrol(e,r)),("bitiş dahil",lambda e,r:{"karar":"izinli","neden":None} if kapsam_kontrol(e,r)["neden"]=="zaman-disi" and e["zaman"]==r["bitis"] else kapsam_kontrol(e,r)),("benzer IP kapsamda",lambda e,r:{"karar":"izinli","neden":None} if e["hedef"].startswith("127.0.0.1") and kapsam_kontrol(e,r)["neden"]=="kapsam-disi-hedef" else kapsam_kontrol(e,r))]:
    ok(not sinama1(mut),"mutant reddedildi: "+ad)
for ad,mut in [("alarm tekrar kullanılıyor",lambda E,A,p:dict(eslestir(E,A,p),eslesmeyen_alarm=[])),("sırasız eşleşmeyen",lambda E,A,p:dict(eslestir(E,A,p),eslesmeyen_alarm=list(reversed(eslestir(E,A,p)["eslesmeyen_alarm"])))),("ilk eylem eşleşmesiz",lambda E,A,p:{"eslesme":dict(eslestir(E,A,p)["eslesme"],**({min(eslestir(E,A,p)["eslesme"]):None} if E else {})),"eslesmeyen_alarm":eslestir(E,A,p)["eslesmeyen_alarm"]})]:
    ok(not sinama2(mut),"mutant reddedildi: "+ad)
for ad,mut in [("kaçırılan = tespitsiz",lambda K:{**tatbikat_ozeti(K),"teknikler":{t:dict(v,kacirildi=v["denenen"]-v["tespit"]) for t,v in tatbikat_ozeti(K)["teknikler"].items()}}),("oran tüm kayıtlardan",lambda K:dict(tatbikat_ozeti(K),tespit_orani=sum(v["tespit"] for v in tatbikat_ozeti(K)["teknikler"].values())/len(K))),("her retle durdur",lambda K:dict(tatbikat_ozeti(K),durdur=any(tatbikat_ozeti(K)["reddedilen"].values())))]:
    ok(not sinama3(mut),"mutant reddedildi: "+ad)
if not tamam:stop()
k=calistir(kapsam_kontrol,eslestir,tatbikat_ozeti,kabul=True)
eq(k['kaynak'],'gercek','gerçek HTTP, SQLite ve yem dinleyici')
ok(k['kabul'],'gerçek kabul: RoE kararı, eşleştirme ve özet referansla aynı')
ok(k['cleanup'],'yalnız kendi lab ve yem dinleyicisi kapandı')
eq(k['yem_vurus'],0,'kapsam dışı yem dinleyicisine tek bağlantı bile gitmedi')
eq(len(k['audit']),7,'yalnız izinli beş eylemin yedi gerçek isteği labda')
```

```setup
import sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_tatbikat_lab import hazirla
hazirla()
```

```hint
Önceki üç işlevi aynen birleştir. Kanıtta `yem_vurus` ve `eslesmeyen_alarm` değerlerine bak: AL4 hangi eylemden geldi?
```
:::

::: anlat Sınır
Bu ders tek bir yerel eğitim labında, dokuz eylemlik bir planla RoE kapısını, kapsam dışı trafiğin hiç gönderilmediğini, iki basit kuralın alarmlarıyla eşleştirmeyi ve teknik bazlı sonuç tablosunu ölçer; gerçek bir kurumun onay ve iletişim sürecini, VECTR ya da SIEM kullanımını ve bir tekniğin bütün varyantlarının tespitini göstermez.
:::
