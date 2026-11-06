---
id: pu23
title: DevSecOps · Semgrep, gitleaks ve Trivy ile Kod, Sır ve Yapılandırma Taraması
summary: Kasıtlı açıklı küçük bir git deposunda üç gerçek tarayıcıyı koştur; çıktılarını tek biçime çevir, etiketli listeye karşı kesinlik ve duyarlılığı ölç, gerekçeli ve süreli istisnalarla bir CI kapısı kur; hangi aracın neyi neden kaçırdığını kanıtla.
timeout: 60
---

::: anlat Boru hattında üç göz
| Sahada ne olur | Bu ders ne kullanır | Ne söyleyemez? |
|---|---|---|
| Kod her commit'te CI'da taranır: SAST (kaynak kodda tehlikeli kalıp), sır taraması (anahtar, token), yapılandırma taraması (Dockerfile, IaC) | Sabit sürümlü Semgrep 1.183.0, gitleaks 8.30.1, Trivy 0.76.1; geçici, iki commit'lik sentetik bir git deposu | Gerçek bir CI sistemini, Semgrep Registry/Pro kurallarını, bağımlılık (SCA) taramasını ya da Trivy'nin zafiyet veritabanını göstermez |
| Araçlar farklı JSON biçimleri, farklı kural adları ve farklı gürültü düzeyleriyle gelir | Üç aracın ham çıktısı, etiketli bir "gerçek liste" (sorun ve tuzak) | Bu küçük depodaki oranlar araçların genel başarısını ölçmez; yalnız bu kurallar ve bu depo için geçerlidir |
| Ekipler gürültüyü istisnayla (bastırma) susturur | Gerekçeli ve bitiş tarihli istisna listesi | Gerçek risk kabul sürecini ve onay zincirini göstermez |

> [!NOT]
> İlk üç görev `devsecops/ornekler.json` dosyasını okur; araç çıktıları **sentetiktir** ve elle yazılmıştır. Setup her Çalıştır/Kontrol Et adımında eksik dosyaları kopyalar; **kalıcılık yoktur**. Dosyayı görmek için başlangıç kodundaki `print` satırlarını kullan. Son görev, `.deps` altındaki önceden onaylanmış ve hash'i doğrulanmış araçları geçici bir klasörde koşturur. Depodaki bütün "sırlar" her koşuda rastgele üretilen **sahte** değerlerdir ve kanıta yazılmaz. Araçlar her isteği kaydedip reddeden yerel bir vekil üzerinden koşar; indirme, kayıt, giriş ya da telemetri yoktur. Koşu sonunda geçici klasör silinir.

**Üç tarayıcı, üç ayrı soru.** **Semgrep** kaynak kodu sözdizimiyle okur ve yazdığın kalıbı arar: `$DB.execute("..." + $X + "...")` gibi bir kural, SQL metnine girdi eklenen her çağrıyı bulur. Ama **yalnız yazdığın kalıbı** bulur. `subprocess.run(..., shell=True)` kuralı `os.system(komut)`'u görmez. **gitleaks** düzenli ifade ve entropi ile sır arar. `git` kipinde bütün commit geçmişini tarar; silinmiş bir `.env` dosyasındaki token geçmişte durduğu sürece bulunur. **Trivy** `fs` kipinde çalışma ağacındaki dosyalara bakar. `secret` tarayıcısı sırları, `misconfig` tarayıcısı Dockerfile'daki yanlış ayarları (AVD kimlikleri: `DS-0001` `:latest` etiketi, `DS-0002` root kullanıcı, `DS-0005` `ADD`) bulur. Geçmişi görmez.

**Saldırgan ne dener?** Açık depoları ve sızmış depo kopyalarını sır için tarar. Geçmişe de bakar, çünkü geliştirici "dosyayı sildim" der ama commit hâlâ oradadır. Kodda girdinin komut ya da sorguya karıştığı yeri arar (pu19 ve pu22'de kanıtlanan açıkların kaynağı). Root çalışan bir konteynerde kaçış ya da yetki yükseltme kolaylaşır.

**Savunma neden kırılır?** Dört tanıdık nedenle. (1) Araç yalnız baktığı yeri görür: çalışma ağacını tarayan araç geçmişteki sırrı kaçırır. (2) Kural yalnız yazılan kalıbı bilir: eksik kural sessiz bir kaçırmadır, raporda "0 bulgu" diye görünür. (3) Gürültülü kural yorgunluk üretir: önbellek anahtarı için kullanılan MD5'i de "zayıf özet" diye işaretleyen kural, ekibi toptan bastırmaya iter. (4) Bastırma çürür: gerekçesiz ve süresiz istisna, kod değiştikten sonra da sessizce açığı örter.

**Blue karşılığı.** Araçların çıktısını tek biçime çevir; kural adına değil **konuma** (dosya, satır, tür) göre eşleştir. Aynı sızmış anahtar gitleaks'te `generic-api-key`, Trivy'de `aws-secret-access-key` adını taşır. Etiketli küçük bir depoyla her aracın **kesinliğini** (bulduklarının ne kadarı gerçek) ve **duyarlılığını** (gerçek sorunların ne kadarını buldu) ölç. CI kapısında her istisna bir gerekçe ve bitiş tarihi taşısın; süresi dolan istisna bastırmasın, hiçbir şeyi bastırmayan istisna temizlik için raporlansın. Sızan sır için silmek yetmez: anahtar **iptal edilip yenilenir** (rotate).

Kaynaklar: [Semgrep · Rule syntax](https://semgrep.dev/docs/writing-rules/rule-syntax), [gitleaks · README](https://github.com/gitleaks/gitleaks), [Trivy · Secret scanning](https://trivy.dev/latest/docs/scanner/secret/), [Trivy · Misconfiguration scanning](https://trivy.dev/latest/docs/scanner/misconfiguration/), [OWASP · Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html), [OWASP · DevSecOps Guideline](https://owasp.org/www-project-devsecops-guideline/). Bu dersteki bütün sayılar yalnız yerel kanıttan gelir.

Purple bağı: pu19 ve pu22 enjeksiyon açıklarını çalışan uygulamada gerçek HTTP ile kanıtladı. Bu ders aynı kök nedeni kod aşamasında, CI'da yakalamaya çalışır ve neyi yakalayamadığını ölçer. pu20 bulguları rapora çevirir; buradaki "kaçan" listesi o raporun kapsam sınırıdır.
:::

::: tahmin Boş alan, yol ve oran
Çıktıyı tahmin et, sonra Çalıştır ile karşılaştır.
```python
import json
ham = json.loads('{"Results": null}')
print(ham.get("Results") or [])
print("src\\db.py".replace("\\", "/"))
print(round(2 / 3, 3), round(5 / 6, 3))
```
???
```cikti
[]
src/db.py
0.667 0.833
```
Tahmininle gerçek çıktı arasındaki farkı tezgâhta yorum satırı olarak yaz: `ham["Results"]` yazsaydık ne olurdu, `ham.get("Results", [])` neden yetmezdi? İkinci satırdaki Python dizgesinde kaç ters bölü vardı? Sonra üç kusurlu başlangıç kodunu çalıştır. Hangisi yol ayırıcısını düzeltmeyip PASS denetimlerini de bulgu sayıyor, hangisi tuzak öğeyle eşleşen bulguyu "doğru" sayıp aynı sorunu iki kez sayıyor, hangisi süresi dolmuş istisnayı hâlâ geçerli kabul edip satırı yok sayıyor? Önce kendin teşhis et; açıklama çözümün ardından gelir.
:::

::: gorev 1 · Üç aracın çıktısını tek biçime çevir
`normalize(arac, ham)`: `arac` `"semgrep"`, `"gitleaks"` ya da `"trivy"`; `ham` aracın JSON çıktısının `json.loads` sonucudur. Her bulgu için `{"arac", "kural", "dosya", "satir", "tur"}` sözlüğü üret ve listeyi `(dosya, satir, arac, kural)` sırasıyla döndür.

- **semgrep:** `ham["results"]` listesi; kural `check_id`, dosya `path`, satır `start.line`, tür `"sast"`.
- **gitleaks:** `ham` bir liste; kural `RuleID`, dosya `File`, satır `StartLine`, tür `"sir"`.
- **trivy:** `ham["Results"]` (yoksa ya da `None` ise boş). Her sonucun `Target`'ı dosyadır. `Secrets` → kural `RuleID`, satır `StartLine`, tür `"sir"`. `Misconfigurations` → yalnız `Status == "FAIL"` olanlar; kural `ID`, satır `CauseMetadata.StartLine`, bu yoksa, `None` ya da 0 ise `0` (dosya düzeyi bulgu), tür `"yapilandirma"`. `Secrets`/`Misconfigurations` yoksa ya da `None` ise atla.

Dosya yolunda `\\` → `/` yap, baştaki `./` öneklerini (birden çok olabilir) at. Kural ve dosya boş olmayan string, satır negatif olmayan tamsayı olmalı. Bilinmeyen araç, beklenen alanın eksikliği ya da yanlış türü `ValueError` verir.

```starter
# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def normalize(arac,ham):
    out=[]
    if arac=="semgrep":
        for r in ham["results"]:
            out.append({"arac":arac,"kural":r["check_id"],"dosya":r["path"],"satir":r["start"]["line"],"tur":"sast"})
    elif arac=="gitleaks":
        for r in ham:
            out.append({"arac":arac,"kural":r["RuleID"],"dosya":r["File"],"satir":r["StartLine"],"tur":"sir"})
    else:
        for res in ham["Results"]:
            for s in res.get("Secrets",[]):
                out.append({"arac":arac,"kural":s["RuleID"],"dosya":res["Target"],"satir":s["StartLine"],"tur":"sir"})
            for m in res.get("Misconfigurations",[]):
                out.append({"arac":arac,"kural":m["ID"],"dosya":res["Target"],"satir":m["CauseMetadata"].get("StartLine",0),"tur":"yapilandirma"})
    return out

import json
from pathlib import Path
v=json.loads(Path("devsecops/ornekler.json").read_text(encoding="utf-8"))
for a in ("semgrep","gitleaks","trivy"):
    for b in normalize(a,v[a]):print(b)
```

```solution
def _yol(d):
    if not isinstance(d,str) or not d:raise ValueError("yol")
    d=d.replace("\\","/")
    while d.startswith("./"):d=d[2:]
    return d
def _tam(x):
    if not isinstance(x,int) or x<0:raise ValueError("satır")
    return x
def _ad(x):
    if not isinstance(x,str) or not x:raise ValueError("kural")
    return x
def normalize(arac,ham):
    out=[]
    try:
        if arac=="semgrep":
            if not isinstance(ham["results"],list):raise ValueError("semgrep")
            for r in ham["results"]:
                out.append({"arac":arac,"kural":_ad(r["check_id"]),"dosya":_yol(r["path"]),"satir":_tam(r["start"]["line"]),"tur":"sast"})
        elif arac=="gitleaks":
            if not isinstance(ham,list):raise ValueError("gitleaks")
            for r in ham:
                out.append({"arac":arac,"kural":_ad(r["RuleID"]),"dosya":_yol(r["File"]),"satir":_tam(r["StartLine"]),"tur":"sir"})
        elif arac=="trivy":
            if not isinstance(ham,dict):raise ValueError("trivy")
            for res in ham.get("Results") or []:
                hedef=_yol(res["Target"])
                for s in res.get("Secrets") or []:
                    out.append({"arac":arac,"kural":_ad(s["RuleID"]),"dosya":hedef,"satir":_tam(s["StartLine"]),"tur":"sir"})
                for m in res.get("Misconfigurations") or []:
                    if m["Status"]!="FAIL":continue
                    satir=(m.get("CauseMetadata") or {}).get("StartLine") or 0
                    out.append({"arac":arac,"kural":_ad(m["ID"]),"dosya":hedef,"satir":_tam(satir),"tur":"yapilandirma"})
        else:raise ValueError("bilinmeyen araç")
    except (KeyError,TypeError,AttributeError):raise ValueError("bozuk çıktı")
    return sorted(out,key=lambda b:(b["dosya"],b["satir"],b["arac"],b["kural"]))

import json
from pathlib import Path
v=json.loads(Path("devsecops/ornekler.json").read_text(encoding="utf-8"))
for a in ("semgrep","gitleaks","trivy"):
    for b in normalize(a,v[a]):print(b)
```

```test
need('normalize')
def sinama1(f):
    try:
        def B(a,k,d,s,t):return {"arac":a,"kural":k,"dosya":d,"satir":s,"tur":t}
        V=[(("semgrep",{"results":[{"check_id":"a","path":".\\x\\y.py","start":{"line":3}},{"check_id":"b","path":"x/a.py","start":{"line":9,"col":2}}],"errors":[]}),
            [B("semgrep","b","x/a.py",9,"sast"),B("semgrep","a","x/y.py",3,"sast")]),
           (("semgrep",{"results":[]}),[]),
           (("semgrep",{"results":[{"check_id":"z","path":"m.py","start":{"line":2}},{"check_id":"c","path":"m.py","start":{"line":2}}]}),[B("semgrep","c","m.py",2,"sast"),B("semgrep","z","m.py",2,"sast")]),
           (("gitleaks",[]),[]),
           (("gitleaks",[{"RuleID":"r","File":"./././k.env","StartLine":1,"Commit":"c1"},{"RuleID":"aws","File":"a\\b.py","StartLine":0,"Commit":""}]),
            [B("gitleaks","aws","a/b.py",0,"sir"),B("gitleaks","r","k.env",1,"sir")]),
           (("trivy",{}),[]),(("trivy",{"Results":None}),[]),(("trivy",{"Results":[{"Target":"D","Misconfigurations":None,"Secrets":None}]}),[]),
           (("trivy",{"Results":[{"Target":"Dockerfile","Misconfigurations":[{"ID":"DS-0026","Status":"FAIL"},{"ID":"DS-0002","Status":"FAIL","CauseMetadata":None},
                                  {"ID":"DS-0001","Status":"PASS","CauseMetadata":{"StartLine":1}},{"ID":"DS-0005","Status":"FAIL","CauseMetadata":{"StartLine":3}},
                                  {"ID":"DS-0009","Status":"FAIL","CauseMetadata":{"StartLine":0}},{"ID":"DS-0010","Status":"FAIL","CauseMetadata":{"StartLine":None}}]},
                                 {"Target":".\\src\\ayar.py","Secrets":[{"RuleID":"aws-access-key-id","StartLine":2},{"RuleID":"aws-secret-access-key","StartLine":3}]}]}),
            [B("trivy","DS-0002","Dockerfile",0,"yapilandirma"),B("trivy","DS-0009","Dockerfile",0,"yapilandirma"),B("trivy","DS-0010","Dockerfile",0,"yapilandirma"),B("trivy","DS-0026","Dockerfile",0,"yapilandirma"),
             B("trivy","DS-0005","Dockerfile",3,"yapilandirma"),B("trivy","aws-access-key-id","src/ayar.py",2,"sir"),B("trivy","aws-secret-access-key","src/ayar.py",3,"sir")])]
        for a,b in V:
            if f(*a)!=b:return False
        for a in (("Semgrep",{"results":[]}),(None,[]),("semgrep",[]),("semgrep",{}),("semgrep",{"results":None}),("semgrep",{"results":[{"check_id":"a","path":"x"}]}),
                  ("semgrep",{"results":[{"check_id":"a","path":"x","start":{"line":"3"}}]}),("semgrep",{"results":[{"check_id":"a","path":"x","start":{"line":-1}}]}),
                  ("semgrep",{"results":[{"check_id":"","path":"x","start":{"line":1}}]}),("semgrep",{"results":[{"check_id":"a","path":"","start":{"line":1}}]}),
                  ("gitleaks",{}),("gitleaks",[{"RuleID":"r","StartLine":1}]),("gitleaks",[{"RuleID":"r","File":"f","StartLine":None}]),("gitleaks",["x"]),
                  ("trivy",[]),("trivy",{"Results":[{"Secrets":[]}]}),("trivy",{"Results":[{"Target":"D","Misconfigurations":[{"ID":"x"}]}]}),
                  ("trivy",{"Results":[{"Target":"D","Secrets":[{"RuleID":"r","StartLine":"2"}]}]}),("trivy",{"Results":[{"Target":"D","Misconfigurations":[{"ID":"x","Status":"FAIL","CauseMetadata":{"StartLine":-2}}]}]})):
            try:f(*a);return False
            except ValueError:pass
        return True
    except Exception:return False
ok(sinama1(normalize),"üç biçim, yol ayırıcısı, PASS ve boş alanlar, sıralama, bozuk çıktı reddi")
def _bos(a,h):
    try:return normalize(a,h)
    except ValueError:return []
for ad,mut in [("sırasız",lambda a,h:list(reversed(normalize(a,h)))),("tür hep sast",lambda a,h:[dict(b,tur="sast") for b in normalize(a,h)]),("bozukta boş liste",_bos)]:
    ok(not sinama1(mut),"mutant reddedildi: "+ad)
```

```setup
import sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_devsecops_lab import hazirla
hazirla()
```

```hint
Önce yolu düzelt; `"src\\db.py"` ile `"src/db.py"` aynı dosyadır. Trivy'de PASS bir bulgu değildir; `CauseMetadata` boş da olabilir.
```
:::

::: anlat Kesinlik ve duyarlılık
Bir tarayıcıyı tek sayı ile değerlendirmek yanıltır. **Kesinlik** düşükse ekip gürültüde boğulur ve kuralları kapatır. **Duyarlılık** düşükse "temiz" rapor sahte bir güven verir. İkisini ölçmek için doğruyu bilmek gerekir: bu yüzden lab deposundaki her kasıtlı sorun ve her tuzak (parametreli sorgu, AWS belgelerindeki örnek anahtar, güvenlik amaçlı olmayan MD5) etiketlidir. Ölçüm **aracın kapsamına** göre yapılır. Semgrep'ten sır bulmasını beklemek haksızdır; ama Trivy hem sırdan hem yapılandırmadan sorumludur. Bütün hattın ("hat") kaçırdığı, hiçbir aracın bulmadığı sorundur. Asıl risk oradadır.
:::

::: gorev 2 · Etiketli listeye karşı ölç
`olc(bulgular, gercek, kapsam)`: `bulgular` 1. görevin çıktılarının birleşimi; `gercek` etiketli liste (her öğe `id`, `tur`, `dosya`, `satir`, `sorun` taşır); `kapsam` araç adından tür listesine bir sözlük. Bir bulgu, `(dosya, satir, tur)` üçlüsü aynı olan gerçek öğeyle eşleşir.

- Her araç için: eşleştiği `sorun: True` öğelerin **farklı** kimlik sayısı `dogru`; hiçbir `sorun: True` öğeyle eşleşmeyen bulgu sayısı `yanlis` (tuzak öğeyle eşleşen de yanlıştır; aynı sorunun tekrarı yanlış sayılmaz); aracın kapsamındaki türlerden bulunmayan `sorun: True` kimlikleri sıralı `kacan`.
- `kesinlik = dogru / (dogru + yanlis)`, `duyarlilik = dogru / (dogru + len(kacan))`; payda 0 ise `None`; değilse 3 basamağa yuvarla.
- Ek olarak `"hat"` anahtarı: bütün araçların bulduğu kimliklerin birleşimi, toplam yanlış, **hiçbir** aracın bulmadığı `sorun: True` kimlikleri ve aynı iki oran.

Kapsamda olmayan araç adı taşıyan bulgu, yinelenen kimlik, bilinmeyen tür, bool olmayan `sorun`, tamsayı olmayan satır ya da yanlış kapsam `ValueError` verir.

```starter
# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def olc(bulgular,gercek,kapsam):
    sonuc={}
    for a in kapsam:
        dogru=yanlis=0;bulunan=set()
        for b in bulgular:
            if b["arac"]!=a:continue
            g=[g for g in gercek if (g["dosya"],g["satir"])==(b["dosya"],b["satir"])]
            if g:dogru+=1;bulunan.add(g[0]["id"])
            else:yanlis+=1
        kacan=[g["id"] for g in gercek if g["sorun"] and g["id"] not in bulunan]
        sonuc[a]={"dogru":dogru,"yanlis":yanlis,"kacan":kacan,"kesinlik":round(dogru/(dogru+yanlis),3),"duyarlilik":round(dogru/(dogru+len(kacan)),3)}
    return sonuc

import json
from pathlib import Path
v=json.loads(Path("devsecops/ornekler.json").read_text(encoding="utf-8"))
for a,s in olc(v["bulgular"],v["gercek"],v["kapsam"]).items():print(a,s)
```

```solution
TURLER=("sast","sir","yapilandirma")
def _oran(a,b):
    return None if b==0 else round(a/b,3)
def olc(bulgular,gercek,kapsam):
    if not isinstance(bulgular,list) or not isinstance(gercek,list) or not isinstance(kapsam,dict):raise ValueError("tür")
    ids=set()
    for g in gercek:
        if (not isinstance(g,dict) or not isinstance(g.get("id"),str) or g["id"] in ids or g.get("tur") not in TURLER
                or not isinstance(g.get("sorun"),bool) or not isinstance(g.get("dosya"),str) or not isinstance(g.get("satir"),int)):
            raise ValueError("gerçek liste")
        ids.add(g["id"])
    for t in kapsam.values():
        if not isinstance(t,(list,tuple)) or any(x not in TURLER for x in t):raise ValueError("kapsam")
    anahtar={(g["dosya"],g["satir"],g["tur"]):g for g in gercek}
    sonuc,hat_bulunan,hat_yanlis={},set(),0
    for a in sorted(kapsam):
        bulunan,yanlis=set(),0
        for b in bulgular:
            if not isinstance(b,dict) or b.get("arac") not in kapsam:raise ValueError("bulgu")
            if b["arac"]!=a:continue
            g=anahtar.get((b["dosya"],b["satir"],b["tur"]))
            if g is not None and g["sorun"]:bulunan.add(g["id"])
            else:yanlis+=1
        kacan=sorted(g["id"] for g in gercek if g["sorun"] and g["tur"] in kapsam[a] and g["id"] not in bulunan)
        sonuc[a]={"dogru":len(bulunan),"yanlis":yanlis,"kacan":kacan,"kesinlik":_oran(len(bulunan),len(bulunan)+yanlis),"duyarlilik":_oran(len(bulunan),len(bulunan)+len(kacan))}
        hat_bulunan|=bulunan;hat_yanlis+=yanlis
    kacan=sorted(g["id"] for g in gercek if g["sorun"] and g["id"] not in hat_bulunan)
    sonuc["hat"]={"dogru":len(hat_bulunan),"yanlis":hat_yanlis,"kacan":kacan,"kesinlik":_oran(len(hat_bulunan),len(hat_bulunan)+hat_yanlis),"duyarlilik":_oran(len(hat_bulunan),len(hat_bulunan)+len(kacan))}
    return sonuc

import json
from pathlib import Path
v=json.loads(Path("devsecops/ornekler.json").read_text(encoding="utf-8"))
for a,s in olc(v["bulgular"],v["gercek"],v["kapsam"]).items():print(a,s)
```

```test
need('olc')
def sinama2(f):
    try:
        def B(a,d,s,t):return {"arac":a,"kural":"k","dosya":d,"satir":s,"tur":t}
        G=[{"id":"A1","tur":"sast","dosya":"f.py","satir":3,"sorun":True},{"id":"A2","tur":"sast","dosya":"f.py","satir":9,"sorun":True},
           {"id":"B1","tur":"sir","dosya":"k.env","satir":1,"sorun":True},{"id":"N1","tur":"sast","dosya":"f.py","satir":5,"sorun":False}]
        K={"s":["sast"],"g":("sir",),"t":["sir","sast"]}
        b=[B("s","f.py",3,"sast"),B("s","f.py",3,"sast"),B("s","f.py",5,"sast"),B("s","f.py",7,"sast"),B("g","k.env",1,"sir"),B("g","k.env",1,"sast"),B("t","f.py",9,"sast")]
        bek={"g":{"dogru":1,"yanlis":1,"kacan":[],"kesinlik":0.5,"duyarlilik":1.0},"s":{"dogru":1,"yanlis":2,"kacan":["A2"],"kesinlik":0.333,"duyarlilik":0.5},
             "t":{"dogru":1,"yanlis":0,"kacan":["A1","B1"],"kesinlik":1.0,"duyarlilik":0.333},"hat":{"dogru":3,"yanlis":3,"kacan":[],"kesinlik":0.5,"duyarlilik":1.0}}
        if f(b,G,K)!=bek:return False
        if f([],[{"id":"N","tur":"sir","dosya":"a","satir":0,"sorun":False}],{"x":["sir"]})!={"x":{"dogru":0,"yanlis":0,"kacan":[],"kesinlik":None,"duyarlilik":None},"hat":{"dogru":0,"yanlis":0,"kacan":[],"kesinlik":None,"duyarlilik":None}}:return False
        G2=[{"id":"Z1","tur":"sir","dosya":"a","satir":1,"sorun":True},{"id":"P2","tur":"sir","dosya":"a","satir":2,"sorun":True},{"id":"A9","tur":"sir","dosya":"a","satir":3,"sorun":True},
            {"id":"C4","tur":"yapilandirma","dosya":"D","satir":0,"sorun":True}]
        r=f([B("a","a",2,"sir"),B("a","a",9,"sir")],G2,{"a":["sir"],"b":["yapilandirma"]})
        if r!={"a":{"dogru":1,"yanlis":1,"kacan":["A9","Z1"],"kesinlik":0.5,"duyarlilik":0.333},"b":{"dogru":0,"yanlis":0,"kacan":["C4"],"kesinlik":None,"duyarlilik":0.0},
               "hat":{"dogru":1,"yanlis":1,"kacan":["A9","C4","Z1"],"kesinlik":0.5,"duyarlilik":0.25}}:return False
        r=f([B("a","a",1,"sir"),B("a","a",2,"sir")],G2[:3],{"a":["sir"]})
        if r["a"]["duyarlilik"]!=0.667 or r["a"]["kesinlik"]!=1.0 or r["hat"]["kacan"]!=["A9"]:return False
        for a in (([B("q","f.py",3,"sast")],G,K),([],G+[dict(G[0])],K),([],[{"id":"X","tur":"xss","dosya":"a","satir":1,"sorun":True}],K),
                  ([],[{"id":"X","tur":"sir","dosya":"a","satir":1,"sorun":"evet"}],K),([],[{"id":"X","tur":"sir","dosya":"a","satir":"1","sorun":True}],K),
                  ([],["x"],K),([],[{"id":5,"tur":"sir","dosya":"a","satir":1,"sorun":True}],K),([],[{"id":"X","tur":"sir","dosya":None,"satir":1,"sorun":True}],K),([],G,{"s":["sql"]}),([],G,{"s":"sast"}),((),G,K),([],None,K),([],G,[("s",["sast"])]),(["x"],G,K)):
            try:f(*a);return False
            except ValueError:pass
        return True
    except Exception:return False
ok(sinama2(olc),"kapsama göre doğru/yanlış/kaçan, tekrar ve tuzak, oranlar, geçersiz girdi")
def _bos(b,g,k):
    try:return olc(b,g,k)
    except ValueError:return {}
for ad,mut in [("hat yok",lambda b,g,k:{a:s for a,s in olc(b,g,k).items() if a!="hat"}),("kaçan sırasız",lambda b,g,k:{a:dict(s,kacan=s["kacan"][::-1]) for a,s in olc(b,g,k).items()}),("bozukta boş",_bos)]:
    ok(not sinama2(mut),"mutant reddedildi: "+ad)
```

```setup
import sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_devsecops_lab import hazirla
hazirla()
```

```hint
Eşleşmede tür de önemlidir. `dogru`'yu kimlik kümesiyle say; aynı bulgunun iki kopyası sorunu iki kez bulmaz.
```
:::

::: anlat İstisna bir borçtur
Her bastırma "bu riski şimdilik kabul ediyorum" demektir. İyi bir istisna kimin, neden ve **ne zamana kadar** kabul ettiğini söyler; kapsamı mümkün olduğunca dardır (aynı kuralın bütün dosyası değil, tek satırı). Süresi dolan istisna sessizce yenilenmez, kapı yeniden kapanır. Hiçbir şeyi bastırmayan istisna zararsız görünür ama tehlikelidir: kod değişince yanlış yeri örtmeye başlayabilir, bu yüzden temizlik listesine girer.
:::

::: gorev 3 · CI kapısı: istisna, gerekçe ve bitiş günü
`ci_kapisi(bulgular, istisnalar, bugun)`: `bugun` ISO tarihi (`"2026-11-04"`). Her istisnada `id`, `arac`, `kural`, `dosya`, `gerekce`, `bitis` string olarak bulunmalı, `satir` isteğe bağlı tamsayıdır. Gerekçe boş ya da yalnız boşluk olamaz, kimlikler tekrarlanamaz, tarihler geçerli olmalı; aksi hâlde `ValueError`.

- `bitis >= bugun` olan istisna **etkindir** (bitiş günü dahil); diğerleri `suresi_dolan` listesine girer ve hiçbir şeyi bastırmaz.
- Bir bulgu, `arac`, `kural`, `dosya` alanları aynı (ve istisnada `satir` varsa satırı da aynı) etkin bir istisna varsa bastırılır.
- Döndür: `gecti` (engelleyen yoksa `True`), `engelleyen` (`(dosya, satir, arac, kural)` sırasıyla), `bastirilan` (bastırılan bulgu sayısı), `suresi_dolan` ve `kullanilmayan` (hiçbir bulguyu bastırmayan etkin istisnalar); kimlik listeleri sıralı.

```starter
# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def ci_kapisi(bulgular,istisnalar,bugun):
    engel=[]
    for b in bulgular:
        if not any((i["arac"],i["kural"],i["dosya"])==(b["arac"],b["kural"],b["dosya"]) for i in istisnalar):engel.append(b)
    return {"gecti":not engel,"engelleyen":engel,"bastirilan":len(bulgular)-len(engel),"suresi_dolan":[],"kullanilmayan":[]}

import json
from pathlib import Path
v=json.loads(Path("devsecops/ornekler.json").read_text(encoding="utf-8"))
k=ci_kapisi(v["bulgular"],v["istisnalar"],v["bugun"])
print("geçti:",k["gecti"],"· bastırılan:",k["bastirilan"],"· süresi dolan:",k["suresi_dolan"],"· kullanılmayan:",k["kullanilmayan"])
for e in k["engelleyen"]:print("ENGEL",e)
```

```solution
from datetime import date
def _gun(x):
    if not isinstance(x,str):raise ValueError("tarih")
    try:return date.fromisoformat(x)
    except ValueError:raise ValueError("tarih: "+x)
def ci_kapisi(bulgular,istisnalar,bugun):
    gun=_gun(bugun)
    if not isinstance(bulgular,list) or not isinstance(istisnalar,list):raise ValueError("tür")
    aktif,dolan,ids=[],[],set()
    for i in istisnalar:
        if not isinstance(i,dict) or any(not isinstance(i.get(k),str) for k in ("id","arac","kural","dosya","gerekce","bitis")):raise ValueError("istisna")
        if i["id"] in ids or not i["gerekce"].strip():raise ValueError("istisna: kimlik ya da gerekçe")
        if "satir" in i and not isinstance(i["satir"],int):raise ValueError("istisna satır")
        ids.add(i["id"])
        (aktif if _gun(i["bitis"])>=gun else dolan).append(i)
    engel,bastir,kullanilan=[],0,set()
    for b in bulgular:
        eslesen=[i for i in aktif if (i["arac"],i["kural"],i["dosya"])==(b["arac"],b["kural"],b["dosya"]) and ("satir" not in i or i["satir"]==b["satir"])]
        if eslesen:
            bastir+=1;kullanilan.update(i["id"] for i in eslesen)
        else:engel.append(b)
    return {"gecti":not engel,"engelleyen":sorted(engel,key=lambda b:(b["dosya"],b["satir"],b["arac"],b["kural"])),"bastirilan":bastir,
            "suresi_dolan":sorted(i["id"] for i in dolan),"kullanilmayan":sorted(i["id"] for i in aktif if i["id"] not in kullanilan)}

import json
from pathlib import Path
v=json.loads(Path("devsecops/ornekler.json").read_text(encoding="utf-8"))
k=ci_kapisi(v["bulgular"],v["istisnalar"],v["bugun"])
print("geçti:",k["gecti"],"· bastırılan:",k["bastirilan"],"· süresi dolan:",k["suresi_dolan"],"· kullanılmayan:",k["kullanilmayan"])
for e in k["engelleyen"]:print("ENGEL",e)
```

```test
need('ci_kapisi')
def sinama3(f):
    try:
        def B(a,k,d,s):return {"arac":a,"kural":k,"dosya":d,"satir":s,"tur":"sast"}
        def I(i,a,k,d,bitis,**e):return dict({"id":i,"arac":a,"kural":k,"dosya":d,"gerekce":"neden","bitis":bitis},**e)
        b1,b2,b3,b4=B("semgrep","r1","f.py",3),B("semgrep","r1","f.py",8),B("trivy","DS-1","D",0),B("gitleaks","g","e",1)
        ist=[I("i1","semgrep","r1","f.py","2026-12-31",satir=3),I("i2","trivy","DS-1","D","2026-11-04"),I("i3","gitleaks","g","e","2026-11-03"),I("i4","semgrep","r9","f.py","2030-01-01")]
        if f([b1,b2,b3,b4],ist,"2026-11-04")!={"gecti":False,"engelleyen":[b4,b2],"bastirilan":2,"suresi_dolan":["i3"],"kullanilmayan":["i4"]}:return False
        if f([b1,b2,b3,b4],ist,"2026-11-05")!={"gecti":False,"engelleyen":[b3,b4,b2],"bastirilan":1,"suresi_dolan":["i2","i3"],"kullanilmayan":["i4"]}:return False
        if f([b2,b1],[I("j","semgrep","r1","f.py","2027-01-01")],"2026-11-04")!={"gecti":True,"engelleyen":[],"bastirilan":2,"suresi_dolan":[],"kullanilmayan":[]}:return False
        if f([],[],"2026-11-04")!={"gecti":True,"engelleyen":[],"bastirilan":0,"suresi_dolan":[],"kullanilmayan":[]}:return False
        if f([b1],[I("x","semgrep","r1","f.py","2027-01-01"),I("y","semgrep","r1","f.py","2027-01-01",satir=3)],"2026-11-04")!={"gecti":True,"engelleyen":[],"bastirilan":1,"suresi_dolan":[],"kullanilmayan":[]}:return False
        if f([b1],[I("x","trivy","r1","f.py","2027-01-01"),I("y","semgrep","r1","g.py","2027-01-01"),I("z","semgrep","r2","f.py","2027-01-01"),I("w","semgrep","r1","f.py","2027-01-01",satir=4)],"2026-11-04")!={"gecti":False,"engelleyen":[b1],"bastirilan":0,"suresi_dolan":[],"kullanilmayan":["w","x","y","z"]}:return False
        for a in (([],[],"2026-13-01"),([],[],None),([],[],"dün"),([],[I("a","s","k","d","2027-01-01",gerekce="   ")],"2026-11-04"),([],[{"id":"a","arac":"s","kural":"k","dosya":"d","bitis":"2027-01-01"}],"2026-11-04"),
                  ([],[I("a","s","k","d","yarın")],"2026-11-04"),([],[I("a","s","k","d","2027-01-01"),I("a","s","k2","d","2027-01-01")],"2026-11-04"),
                  ([],[I("a","s","k","d","2027-01-01",satir="3")],"2026-11-04"),([],None,"2026-11-04"),(None,[],"2026-11-04"),([],["x"],"2026-11-04")):
            try:f(*a);return False
            except ValueError:pass
        return True
    except Exception:return False
ok(sinama3(ci_kapisi),"istisna eşleşmesi, satır, bitiş günü dahil, süresi dolan, kullanılmayan, geçersiz girdi")
def _gec(b,i,g):
    try:return ci_kapisi(b,i,g)
    except ValueError:return {"gecti":True,"engelleyen":[],"bastirilan":0,"suresi_dolan":[],"kullanilmayan":[]}
for ad,mut in [("hep geçer",lambda b,i,g:dict(ci_kapisi(b,i,g),gecti=True)),("engelleyen sırasız",lambda b,i,g:dict(ci_kapisi(b,i,g),engelleyen=ci_kapisi(b,i,g)["engelleyen"][::-1])),("bozukta geçer",_gec)]:
    ok(not sinama3(mut),"mutant reddedildi: "+ad)
```

```setup
import sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_devsecops_lab import hazirla
hazirla()
```

```hint
Tarihleri `date.fromisoformat` ile karşılaştır. Bir istisna yalnız kendi satırını kapsıyorsa aynı kuralın başka satırı engellemeye devam eder.
```
:::

::: anlat Hata vitrini · yazar koşusu
Yazar son görevi referans işlevlerle ve `validate` ile birçok kez çalıştırdı (Python 3.13, Windows). Aşağıdaki deneme koşusu dışında bulgular ve ölçümler her koşuda aynıydı. Vekile hiçbir koşuda dış istek gelmedi.

- **Süre:** Semgrep'in standart Python sarmalayıcısı bu makinede her koşuda 18–28 sn sürdü. Bir doğrulama koşusu 60 sn sınırını aştı. Lab bu yüzden aynı motoru doğrudan çağıran `scan --experimental` (yerel osemgrep) kipini kullanır. Bulgular iki kipte birebir aynıydı. Paralel koşuda süreler makine yüküne göre Semgrep için 1–16 sn, gitleaks için 4–14 sn, Trivy için 2–6 sn oldu.

- **Semgrep:** 3 doğru, 1 yanlış (önbellek anahtarı MD5'i), kaçan `S4` (`os.system`; kural yazılmamıştı). Kesinlik 0,75, duyarlılık 0,75.
- **gitleaks:** 3 doğru, 0 yanlış. Silinmiş `.env`'deki token'ı (`G3`) **geçmişten** buldu. AWS gizli anahtarını kendi `generic-api-key` kuralıyla yakaladı.
- **Trivy:** 5 doğru, 1 yanlış (`DS-0026` HEALTHCHECK yok; bu politika için işletim konusu), kaçan `G3`: çalışma ağacında olmayan dosyayı göremez. Kesinlik ve duyarlılık 0,833.
- **Hat:** 9 doğru, 2 yanlış, tek kaçan `S4`. AWS belgelerindeki örnek anahtarı hiçbir araç işaretlemedi.
- **CI kapısı kapandı:** 11 engelleyen, 2 bastırılan (`I1` HEALTHCHECK, `I2` önbellek MD5'i, yalnız kendi satırı). `I3` (`ADD` için) süresi dolduğu için bastırmadı. `I4` hiçbir şeyi bastırmadı ve temizlik listesine düştü.
- **Bir deneme koşusundan ders:** Lab ilk sürümünde sahte gizli anahtarı `/` ve `+` da içerebilen bir alfabeyle üretiyordu. Bir koşuda gitleaks'in genel kuralı bu anahtarı kaçırdı. Lab bu yüzden artık yalnız harf ve rakam üretir. Kural tabanlı sır taraması, değerin biçimine bağlıdır.

Kendi cümlenle açıkla: `S4`'ü yakalamak için `.semgrep.yml`'e nasıl bir kural eklerdin, bu kural `liste()` işlevindeki güvenli `subprocess.run([...])` çağrısını da işaretler miydi?
:::

::: gorev Gerçek deney · Üç aracı gerçek depoda koştur
Üç işlevi birleştir. Alttaki `calistir` satırı gerçek deneyi başlatır; silme. Koşu geçici bir klasörde iki commit'lik küçük bir git deposu kurar: kasıtlı açıklı `uygulama/app.py`, rastgele üretilmiş **sahte** AWS anahtarları içeren `uygulama/ayar.py`, AWS belgelerindeki örnek anahtarı taşıyan bir test dosyası, zayıf bir `Dockerfile` ve ilk commit'te eklenip ikincide silinen bir `.env`. Ardından `.deps` altındaki sabit sürümlerle **Semgrep** (`scan --experimental` ile yerel motor, yalnız depodaki `.semgrep.yml` kuralları, `--metrics=off`), **gitleaks** (git geçmişi, `--redact`) ve **Trivy** (`secret` + `misconfig`, güncellemeler kapalı) paralel koşar. Ham çıktılar senin `normalize`, `olc` ve `ci_kapisi` işlevlerinden geçer; sonuçlar referansla karşılaştırılır. Araçlar her isteği kaydedip reddeden yerel bir vekil üzerinden koşar: dış ağa çıkma denemesi kanıta yazılır. Run deneme kanıtı yazar, Check ayrıca kabul kanıtını yazar; yol stdout'ta görünür.

```starter
import json
from datetime import date
# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def normalize(arac,ham):
    out=[]
    if arac=="semgrep":
        for r in ham["results"]:
            out.append({"arac":arac,"kural":r["check_id"],"dosya":r["path"],"satir":r["start"]["line"],"tur":"sast"})
    elif arac=="gitleaks":
        for r in ham:
            out.append({"arac":arac,"kural":r["RuleID"],"dosya":r["File"],"satir":r["StartLine"],"tur":"sir"})
    else:
        for res in ham["Results"]:
            for s in res.get("Secrets",[]):
                out.append({"arac":arac,"kural":s["RuleID"],"dosya":res["Target"],"satir":s["StartLine"],"tur":"sir"})
            for m in res.get("Misconfigurations",[]):
                out.append({"arac":arac,"kural":m["ID"],"dosya":res["Target"],"satir":m["CauseMetadata"].get("StartLine",0),"tur":"yapilandirma"})
    return out

# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def olc(bulgular,gercek,kapsam):
    sonuc={}
    for a in kapsam:
        dogru=yanlis=0;bulunan=set()
        for b in bulgular:
            if b["arac"]!=a:continue
            g=[g for g in gercek if (g["dosya"],g["satir"])==(b["dosya"],b["satir"])]
            if g:dogru+=1;bulunan.add(g[0]["id"])
            else:yanlis+=1
        kacan=[g["id"] for g in gercek if g["sorun"] and g["id"] not in bulunan]
        sonuc[a]={"dogru":dogru,"yanlis":yanlis,"kacan":kacan,"kesinlik":round(dogru/(dogru+yanlis),3),"duyarlilik":round(dogru/(dogru+len(kacan)),3)}
    return sonuc

# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def ci_kapisi(bulgular,istisnalar,bugun):
    engel=[]
    for b in bulgular:
        if not any((i["arac"],i["kural"],i["dosya"])==(b["arac"],b["kural"],b["dosya"]) for i in istisnalar):engel.append(b)
    return {"gecti":not engel,"engelleyen":engel,"bastirilan":len(bulgular)-len(engel),"suresi_dolan":[],"kullanilmayan":[]}

from purple_devsecops_lab import calistir
calistir(normalize,olc,ci_kapisi)
```

```solution
import json
from datetime import date
def _yol(d):
    if not isinstance(d,str) or not d:raise ValueError("yol")
    d=d.replace("\\","/")
    while d.startswith("./"):d=d[2:]
    return d
def _tam(x):
    if not isinstance(x,int) or x<0:raise ValueError("satır")
    return x
def _ad(x):
    if not isinstance(x,str) or not x:raise ValueError("kural")
    return x
def normalize(arac,ham):
    out=[]
    try:
        if arac=="semgrep":
            if not isinstance(ham["results"],list):raise ValueError("semgrep")
            for r in ham["results"]:
                out.append({"arac":arac,"kural":_ad(r["check_id"]),"dosya":_yol(r["path"]),"satir":_tam(r["start"]["line"]),"tur":"sast"})
        elif arac=="gitleaks":
            if not isinstance(ham,list):raise ValueError("gitleaks")
            for r in ham:
                out.append({"arac":arac,"kural":_ad(r["RuleID"]),"dosya":_yol(r["File"]),"satir":_tam(r["StartLine"]),"tur":"sir"})
        elif arac=="trivy":
            if not isinstance(ham,dict):raise ValueError("trivy")
            for res in ham.get("Results") or []:
                hedef=_yol(res["Target"])
                for s in res.get("Secrets") or []:
                    out.append({"arac":arac,"kural":_ad(s["RuleID"]),"dosya":hedef,"satir":_tam(s["StartLine"]),"tur":"sir"})
                for m in res.get("Misconfigurations") or []:
                    if m["Status"]!="FAIL":continue
                    satir=(m.get("CauseMetadata") or {}).get("StartLine") or 0
                    out.append({"arac":arac,"kural":_ad(m["ID"]),"dosya":hedef,"satir":_tam(satir),"tur":"yapilandirma"})
        else:raise ValueError("bilinmeyen araç")
    except (KeyError,TypeError,AttributeError):raise ValueError("bozuk çıktı")
    return sorted(out,key=lambda b:(b["dosya"],b["satir"],b["arac"],b["kural"]))

TURLER=("sast","sir","yapilandirma")
def _oran(a,b):
    return None if b==0 else round(a/b,3)
def olc(bulgular,gercek,kapsam):
    if not isinstance(bulgular,list) or not isinstance(gercek,list) or not isinstance(kapsam,dict):raise ValueError("tür")
    ids=set()
    for g in gercek:
        if (not isinstance(g,dict) or not isinstance(g.get("id"),str) or g["id"] in ids or g.get("tur") not in TURLER
                or not isinstance(g.get("sorun"),bool) or not isinstance(g.get("dosya"),str) or not isinstance(g.get("satir"),int)):
            raise ValueError("gerçek liste")
        ids.add(g["id"])
    for t in kapsam.values():
        if not isinstance(t,(list,tuple)) or any(x not in TURLER for x in t):raise ValueError("kapsam")
    anahtar={(g["dosya"],g["satir"],g["tur"]):g for g in gercek}
    sonuc,hat_bulunan,hat_yanlis={},set(),0
    for a in sorted(kapsam):
        bulunan,yanlis=set(),0
        for b in bulgular:
            if not isinstance(b,dict) or b.get("arac") not in kapsam:raise ValueError("bulgu")
            if b["arac"]!=a:continue
            g=anahtar.get((b["dosya"],b["satir"],b["tur"]))
            if g is not None and g["sorun"]:bulunan.add(g["id"])
            else:yanlis+=1
        kacan=sorted(g["id"] for g in gercek if g["sorun"] and g["tur"] in kapsam[a] and g["id"] not in bulunan)
        sonuc[a]={"dogru":len(bulunan),"yanlis":yanlis,"kacan":kacan,"kesinlik":_oran(len(bulunan),len(bulunan)+yanlis),"duyarlilik":_oran(len(bulunan),len(bulunan)+len(kacan))}
        hat_bulunan|=bulunan;hat_yanlis+=yanlis
    kacan=sorted(g["id"] for g in gercek if g["sorun"] and g["id"] not in hat_bulunan)
    sonuc["hat"]={"dogru":len(hat_bulunan),"yanlis":hat_yanlis,"kacan":kacan,"kesinlik":_oran(len(hat_bulunan),len(hat_bulunan)+hat_yanlis),"duyarlilik":_oran(len(hat_bulunan),len(hat_bulunan)+len(kacan))}
    return sonuc

def _gun(x):
    if not isinstance(x,str):raise ValueError("tarih")
    try:return date.fromisoformat(x)
    except ValueError:raise ValueError("tarih: "+x)
def ci_kapisi(bulgular,istisnalar,bugun):
    gun=_gun(bugun)
    if not isinstance(bulgular,list) or not isinstance(istisnalar,list):raise ValueError("tür")
    aktif,dolan,ids=[],[],set()
    for i in istisnalar:
        if not isinstance(i,dict) or any(not isinstance(i.get(k),str) for k in ("id","arac","kural","dosya","gerekce","bitis")):raise ValueError("istisna")
        if i["id"] in ids or not i["gerekce"].strip():raise ValueError("istisna: kimlik ya da gerekçe")
        if "satir" in i and not isinstance(i["satir"],int):raise ValueError("istisna satır")
        ids.add(i["id"])
        (aktif if _gun(i["bitis"])>=gun else dolan).append(i)
    engel,bastir,kullanilan=[],0,set()
    for b in bulgular:
        eslesen=[i for i in aktif if (i["arac"],i["kural"],i["dosya"])==(b["arac"],b["kural"],b["dosya"]) and ("satir" not in i or i["satir"]==b["satir"])]
        if eslesen:
            bastir+=1;kullanilan.update(i["id"] for i in eslesen)
        else:engel.append(b)
    return {"gecti":not engel,"engelleyen":sorted(engel,key=lambda b:(b["dosya"],b["satir"],b["arac"],b["kural"])),"bastirilan":bastir,
            "suresi_dolan":sorted(i["id"] for i in dolan),"kullanilmayan":sorted(i["id"] for i in aktif if i["id"] not in kullanilan)}

from purple_devsecops_lab import calistir
calistir(normalize,olc,ci_kapisi)
```

```test
need('normalize');need('olc');need('ci_kapisi')
from purple_devsecops_lab import kod_koruma,calistir
ok(kod_koruma(src),'kaynak koruması: referans/dinamik kod/özel öznitelik yok')
if not kod_koruma(src):stop()
def sinama1(f):
    try:
        def B(a,k,d,s,t):return {"arac":a,"kural":k,"dosya":d,"satir":s,"tur":t}
        V=[(("semgrep",{"results":[{"check_id":"a","path":".\\x\\y.py","start":{"line":3}},{"check_id":"b","path":"x/a.py","start":{"line":9,"col":2}}],"errors":[]}),
            [B("semgrep","b","x/a.py",9,"sast"),B("semgrep","a","x/y.py",3,"sast")]),
           (("semgrep",{"results":[]}),[]),
           (("semgrep",{"results":[{"check_id":"z","path":"m.py","start":{"line":2}},{"check_id":"c","path":"m.py","start":{"line":2}}]}),[B("semgrep","c","m.py",2,"sast"),B("semgrep","z","m.py",2,"sast")]),
           (("gitleaks",[]),[]),
           (("gitleaks",[{"RuleID":"r","File":"./././k.env","StartLine":1,"Commit":"c1"},{"RuleID":"aws","File":"a\\b.py","StartLine":0,"Commit":""}]),
            [B("gitleaks","aws","a/b.py",0,"sir"),B("gitleaks","r","k.env",1,"sir")]),
           (("trivy",{}),[]),(("trivy",{"Results":None}),[]),(("trivy",{"Results":[{"Target":"D","Misconfigurations":None,"Secrets":None}]}),[]),
           (("trivy",{"Results":[{"Target":"Dockerfile","Misconfigurations":[{"ID":"DS-0026","Status":"FAIL"},{"ID":"DS-0002","Status":"FAIL","CauseMetadata":None},
                                  {"ID":"DS-0001","Status":"PASS","CauseMetadata":{"StartLine":1}},{"ID":"DS-0005","Status":"FAIL","CauseMetadata":{"StartLine":3}},
                                  {"ID":"DS-0009","Status":"FAIL","CauseMetadata":{"StartLine":0}},{"ID":"DS-0010","Status":"FAIL","CauseMetadata":{"StartLine":None}}]},
                                 {"Target":".\\src\\ayar.py","Secrets":[{"RuleID":"aws-access-key-id","StartLine":2},{"RuleID":"aws-secret-access-key","StartLine":3}]}]}),
            [B("trivy","DS-0002","Dockerfile",0,"yapilandirma"),B("trivy","DS-0009","Dockerfile",0,"yapilandirma"),B("trivy","DS-0010","Dockerfile",0,"yapilandirma"),B("trivy","DS-0026","Dockerfile",0,"yapilandirma"),
             B("trivy","DS-0005","Dockerfile",3,"yapilandirma"),B("trivy","aws-access-key-id","src/ayar.py",2,"sir"),B("trivy","aws-secret-access-key","src/ayar.py",3,"sir")])]
        for a,b in V:
            if f(*a)!=b:return False
        for a in (("Semgrep",{"results":[]}),(None,[]),("semgrep",[]),("semgrep",{}),("semgrep",{"results":None}),("semgrep",{"results":[{"check_id":"a","path":"x"}]}),
                  ("semgrep",{"results":[{"check_id":"a","path":"x","start":{"line":"3"}}]}),("semgrep",{"results":[{"check_id":"a","path":"x","start":{"line":-1}}]}),
                  ("semgrep",{"results":[{"check_id":"","path":"x","start":{"line":1}}]}),("semgrep",{"results":[{"check_id":"a","path":"","start":{"line":1}}]}),
                  ("gitleaks",{}),("gitleaks",[{"RuleID":"r","StartLine":1}]),("gitleaks",[{"RuleID":"r","File":"f","StartLine":None}]),("gitleaks",["x"]),
                  ("trivy",[]),("trivy",{"Results":[{"Secrets":[]}]}),("trivy",{"Results":[{"Target":"D","Misconfigurations":[{"ID":"x"}]}]}),
                  ("trivy",{"Results":[{"Target":"D","Secrets":[{"RuleID":"r","StartLine":"2"}]}]}),("trivy",{"Results":[{"Target":"D","Misconfigurations":[{"ID":"x","Status":"FAIL","CauseMetadata":{"StartLine":-2}}]}]})):
            try:f(*a);return False
            except ValueError:pass
        return True
    except Exception:return False
def sinama2(f):
    try:
        def B(a,d,s,t):return {"arac":a,"kural":"k","dosya":d,"satir":s,"tur":t}
        G=[{"id":"A1","tur":"sast","dosya":"f.py","satir":3,"sorun":True},{"id":"A2","tur":"sast","dosya":"f.py","satir":9,"sorun":True},
           {"id":"B1","tur":"sir","dosya":"k.env","satir":1,"sorun":True},{"id":"N1","tur":"sast","dosya":"f.py","satir":5,"sorun":False}]
        K={"s":["sast"],"g":("sir",),"t":["sir","sast"]}
        b=[B("s","f.py",3,"sast"),B("s","f.py",3,"sast"),B("s","f.py",5,"sast"),B("s","f.py",7,"sast"),B("g","k.env",1,"sir"),B("g","k.env",1,"sast"),B("t","f.py",9,"sast")]
        bek={"g":{"dogru":1,"yanlis":1,"kacan":[],"kesinlik":0.5,"duyarlilik":1.0},"s":{"dogru":1,"yanlis":2,"kacan":["A2"],"kesinlik":0.333,"duyarlilik":0.5},
             "t":{"dogru":1,"yanlis":0,"kacan":["A1","B1"],"kesinlik":1.0,"duyarlilik":0.333},"hat":{"dogru":3,"yanlis":3,"kacan":[],"kesinlik":0.5,"duyarlilik":1.0}}
        if f(b,G,K)!=bek:return False
        if f([],[{"id":"N","tur":"sir","dosya":"a","satir":0,"sorun":False}],{"x":["sir"]})!={"x":{"dogru":0,"yanlis":0,"kacan":[],"kesinlik":None,"duyarlilik":None},"hat":{"dogru":0,"yanlis":0,"kacan":[],"kesinlik":None,"duyarlilik":None}}:return False
        G2=[{"id":"Z1","tur":"sir","dosya":"a","satir":1,"sorun":True},{"id":"P2","tur":"sir","dosya":"a","satir":2,"sorun":True},{"id":"A9","tur":"sir","dosya":"a","satir":3,"sorun":True},
            {"id":"C4","tur":"yapilandirma","dosya":"D","satir":0,"sorun":True}]
        r=f([B("a","a",2,"sir"),B("a","a",9,"sir")],G2,{"a":["sir"],"b":["yapilandirma"]})
        if r!={"a":{"dogru":1,"yanlis":1,"kacan":["A9","Z1"],"kesinlik":0.5,"duyarlilik":0.333},"b":{"dogru":0,"yanlis":0,"kacan":["C4"],"kesinlik":None,"duyarlilik":0.0},
               "hat":{"dogru":1,"yanlis":1,"kacan":["A9","C4","Z1"],"kesinlik":0.5,"duyarlilik":0.25}}:return False
        r=f([B("a","a",1,"sir"),B("a","a",2,"sir")],G2[:3],{"a":["sir"]})
        if r["a"]["duyarlilik"]!=0.667 or r["a"]["kesinlik"]!=1.0 or r["hat"]["kacan"]!=["A9"]:return False
        for a in (([B("q","f.py",3,"sast")],G,K),([],G+[dict(G[0])],K),([],[{"id":"X","tur":"xss","dosya":"a","satir":1,"sorun":True}],K),
                  ([],[{"id":"X","tur":"sir","dosya":"a","satir":1,"sorun":"evet"}],K),([],[{"id":"X","tur":"sir","dosya":"a","satir":"1","sorun":True}],K),
                  ([],["x"],K),([],[{"id":5,"tur":"sir","dosya":"a","satir":1,"sorun":True}],K),([],[{"id":"X","tur":"sir","dosya":None,"satir":1,"sorun":True}],K),([],G,{"s":["sql"]}),([],G,{"s":"sast"}),((),G,K),([],None,K),([],G,[("s",["sast"])]),(["x"],G,K)):
            try:f(*a);return False
            except ValueError:pass
        return True
    except Exception:return False
def sinama3(f):
    try:
        def B(a,k,d,s):return {"arac":a,"kural":k,"dosya":d,"satir":s,"tur":"sast"}
        def I(i,a,k,d,bitis,**e):return dict({"id":i,"arac":a,"kural":k,"dosya":d,"gerekce":"neden","bitis":bitis},**e)
        b1,b2,b3,b4=B("semgrep","r1","f.py",3),B("semgrep","r1","f.py",8),B("trivy","DS-1","D",0),B("gitleaks","g","e",1)
        ist=[I("i1","semgrep","r1","f.py","2026-12-31",satir=3),I("i2","trivy","DS-1","D","2026-11-04"),I("i3","gitleaks","g","e","2026-11-03"),I("i4","semgrep","r9","f.py","2030-01-01")]
        if f([b1,b2,b3,b4],ist,"2026-11-04")!={"gecti":False,"engelleyen":[b4,b2],"bastirilan":2,"suresi_dolan":["i3"],"kullanilmayan":["i4"]}:return False
        if f([b1,b2,b3,b4],ist,"2026-11-05")!={"gecti":False,"engelleyen":[b3,b4,b2],"bastirilan":1,"suresi_dolan":["i2","i3"],"kullanilmayan":["i4"]}:return False
        if f([b2,b1],[I("j","semgrep","r1","f.py","2027-01-01")],"2026-11-04")!={"gecti":True,"engelleyen":[],"bastirilan":2,"suresi_dolan":[],"kullanilmayan":[]}:return False
        if f([],[],"2026-11-04")!={"gecti":True,"engelleyen":[],"bastirilan":0,"suresi_dolan":[],"kullanilmayan":[]}:return False
        if f([b1],[I("x","semgrep","r1","f.py","2027-01-01"),I("y","semgrep","r1","f.py","2027-01-01",satir=3)],"2026-11-04")!={"gecti":True,"engelleyen":[],"bastirilan":1,"suresi_dolan":[],"kullanilmayan":[]}:return False
        if f([b1],[I("x","trivy","r1","f.py","2027-01-01"),I("y","semgrep","r1","g.py","2027-01-01"),I("z","semgrep","r2","f.py","2027-01-01"),I("w","semgrep","r1","f.py","2027-01-01",satir=4)],"2026-11-04")!={"gecti":False,"engelleyen":[b1],"bastirilan":0,"suresi_dolan":[],"kullanilmayan":["w","x","y","z"]}:return False
        for a in (([],[],"2026-13-01"),([],[],None),([],[],"dün"),([],[I("a","s","k","d","2027-01-01",gerekce="   ")],"2026-11-04"),([],[{"id":"a","arac":"s","kural":"k","dosya":"d","bitis":"2027-01-01"}],"2026-11-04"),
                  ([],[I("a","s","k","d","yarın")],"2026-11-04"),([],[I("a","s","k","d","2027-01-01"),I("a","s","k2","d","2027-01-01")],"2026-11-04"),
                  ([],[I("a","s","k","d","2027-01-01",satir="3")],"2026-11-04"),([],None,"2026-11-04"),(None,[],"2026-11-04"),([],["x"],"2026-11-04")):
            try:f(*a);return False
            except ValueError:pass
        return True
    except Exception:return False
tamam=sinama1(normalize) and sinama2(olc) and sinama3(ci_kapisi)
ok(tamam,"üç işlev gizli verilerle doğru")
def _bos(a,h):
    try:return normalize(a,h)
    except ValueError:return []
for ad,mut in [("sırasız",lambda a,h:list(reversed(normalize(a,h)))),("tür hep sast",lambda a,h:[dict(b,tur="sast") for b in normalize(a,h)]),("bozukta boş liste",_bos)]:
    ok(not sinama1(mut),"mutant reddedildi: "+ad)
def _bos(b,g,k):
    try:return olc(b,g,k)
    except ValueError:return {}
for ad,mut in [("hat yok",lambda b,g,k:{a:s for a,s in olc(b,g,k).items() if a!="hat"}),("kaçan sırasız",lambda b,g,k:{a:dict(s,kacan=s["kacan"][::-1]) for a,s in olc(b,g,k).items()}),("bozukta boş",_bos)]:
    ok(not sinama2(mut),"mutant reddedildi: "+ad)
def _gec(b,i,g):
    try:return ci_kapisi(b,i,g)
    except ValueError:return {"gecti":True,"engelleyen":[],"bastirilan":0,"suresi_dolan":[],"kullanilmayan":[]}
for ad,mut in [("hep geçer",lambda b,i,g:dict(ci_kapisi(b,i,g),gecti=True)),("engelleyen sırasız",lambda b,i,g:dict(ci_kapisi(b,i,g),engelleyen=ci_kapisi(b,i,g)["engelleyen"][::-1])),("bozukta geçer",_gec)]:
    ok(not sinama3(mut),"mutant reddedildi: "+ad)
if not tamam:stop()
k=calistir(normalize,olc,ci_kapisi,kabul=True)
eq(k['kaynak'],'gercek','gerçek araç koşusu')
ok(k['kabul'],'gerçek kabul: üç araç koştu, ölçüm ve CI kararı referansla aynı')
ok(k['cleanup'],'yalnız kendi geçici deposu ve vekili kapandı')
eq(k['dis_istek'],[],'araçlar dış ağa istek göndermedi')
eq(k['sizinti'],[],'kanıtta sırrın kendisi yok')
eq(k['olcum']['hat']['kacan'],['S4'],'üç aracın birlikte kaçırdığı tek sorun os.system')
eq(k['ci']['suresi_dolan'],['I3'],'süresi dolan istisna bastırmadı')
ok(not k['ci']['gecti'],'CI kapısı gerçek sorunlar yüzünden kapandı')
```

```setup
import sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_devsecops_lab import hazirla
hazirla()
```

```meta
timeout: 60
```
```hint
Önceki üç işlevi aynen birleştir. Çıktıda trivy'nin `kacan` listesine bak: hangi sorunu neden göremedi?
```
:::

::: anlat Sınır
Bu ders sabit sürümlü Semgrep, gitleaks ve Trivy'yi sentetik, kasıtlı açıklı küçük bir git deposunda gerçekten koşturur; çıktıları tek biçime çevirir, etiketli listeye karşı kesinlik ve duyarlılığı ölçer ve gerekçeli, süreli istisnalarla bir CI kapısı kurar. Gerçek bir CI sistemini, bağımlılık zafiyeti (SCA) taramasını, Semgrep Registry kurallarını, sızan sırrın iptal edilmesini ve bu oranların başka depolara genellenmesini kapsamaz.
:::
