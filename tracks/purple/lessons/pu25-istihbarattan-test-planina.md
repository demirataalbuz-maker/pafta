---
id: pu25
title: İstihbarattan Plana · CTID APT29 Öykünme Planını Tespit Beklentili Test Planına Çevir
summary: Gerçek CTID APT29 öykünme planını (sabit commit, hash'i doğrulanmış) komut çalıştırmadan oku; adımları doğal sırayla ayıkla, teknikleri bugünkü ATT&CK'e karşı denetle, yerel telemetriye göre planla/ertele/kapsam-dışı ve kör nokta kararı veren bir test planı üret.
timeout: 30
---

::: anlat Tehdit istihbaratından test planına
| Sahada ne olur | Bu ders ne kullanır | Ne söyleyemez? |
|---|---|---|
| Purple ekip, gerçek bir tehdit grubunun davranışından (CTI) bir öykünme planı çıkarır ve hangi adımı nerede, hangi tespit beklentisiyle sınayacağını yazar | MITRE Engenuity CTID'in açık APT29 öykünme planı (79 adım, ATT&CK 8.1 ile yazılmış); ATT&CK Enterprise 19.2 özeti | Planı **çalıştırmaz**; APT29'un bugünkü davranışını, planın tamlığını ya da bir ürünün başarısını göstermez |
| Planlar eskir: teknikler yeniden adlandırılır, bölünür, emekli olur | Planın 2020 kimlik ve adlarını bugünkü ATT&CK ile karşılaştırma | ATT&CK'in bütün sürüm farklarını değil, yalnız bu plandaki teknikleri denetler |
| Her adım her ortamda sınanamaz: bazıları ikinci makine, bazıları dış hizmet ister; bazı teknikler için telemetri yoktur | Varsayımsal izole Windows VM'inin telemetri eşlemesi (elle yazılmış) ve ortam sınırları | Telemetri eşlemesi ölçülmüş değil **varsayılmıştır**; VM kurulunca (Dalga C) ölçülecektir |

> [!NOT]
> İlk üç görev `istihbarat/ornekler.json` ve `istihbarat/telemetri.json` dosyalarını okur. Örnek plan **sentetiktir**, komut alanları çıkarılmıştır. Setup her Çalıştır/Kontrol Et adımında eksik dosyaları kopyalar; **kalıcılık yoktur**. Dosyaları görmek için başlangıç kodundaki `print` satırlarını kullan. `attack.json` her çalıştırmada çalışma klasörüne gelir. Son görev, `.deps` altındaki önceden onaylanmış ve sha256'sı doğrulanmış gerçek CTID planını **yalnız okur**. Planın içindeki PowerShell ve cmd komutları hiçbir koşulda çalıştırılmaz; senin çıktına girip girmedikleri de ayrıca denetlenir. Planı uygulamak, izole ve sıfırlanabilir bir lab ile yazılı kapsam (pu21) gerektirir.

**Öykünme planı nedir?** CTID'in (Center for Threat-Informed Defense) açık öykünme kütüphanesi, kamuya açık tehdit raporlarından bir grubun davranışını adım adım yeniden kurar. APT29 planı iki senaryodan oluşur; her adımın bir kimliği (`1.A`, `2.B.1`), bir taktiği, bir ATT&CK tekniği, kaynağı gösteren bir CTI bağlantısı ve yürütücü komutları vardır. Purple ekip bu planı olduğu gibi çalıştırmaz. Önce **okur**: hangi teknik var, hangisi bizim ortamımızda sınanabilir, hangisini görebiliriz, hangisini göremeyiz?

**Saldırgan ne dener?** Plan, saldırganın gözünden yazılmıştır: keşif komutları (sistem, kullanıcı, süreç, ağ), PowerShell ile yürütme, belirteç çalma, kimlik bilgisi dökümü, kalıcılık, iz silme ve sızdırma. Gerçek saldırgan bunları sırayla, sessizce ve ortamın izin verdiği kadar yapar. Tespit edilemeyen her adım ona zaman kazandırır.

**Savunma neden kırılır?** Üç tipik nedenle. (1) **Eski istihbarat:** 2020'de "Credential Dumping" diye yazılan teknik bugün "OS Credential Dumping"tir. Kimlik ve ad eşleşmesi kontrol edilmezse kural kütüphanesiyle plan arasında sessiz kopukluklar oluşur. (2) **Yanlış genelleme:** "PowerShell'i görüyoruz" demek, her PowerShell tabanlı tekniği gördüğümüz anlamına gelmez. Alt tekniğin kendi telemetrisi yoksa üst tekniğe güvenmek kör noktayı gizler; tersine, bilinen bir kör noktayı açıkça yazmak gerekir. (3) **Ölçülemeyeni ölçmüş sanmak:** ikinci makine ya da dış bulut hesabı gerektiren adım tek makinelik labda "geçti" diye işaretlenemez. Ertelenir ya da kapsam dışı bırakılır, raporda da öyle görünür.

**Blue karşılığı.** Test planı her adım için bir **beklenti** yazar: "bu adım çalıştığında şu kayıtlar görünmeli" (örneğin Sysmon 10 ile LSASS erişimi, PowerShell 4104 ile betik bloğu). Tatbikat sırasında (pu21) beklenti ile gözlem karşılaştırılır. Kör nokta listesi de en az alarmlar kadar değerlidir: tespit mühendisliğinin bir sonraki işini o belirler.

Kaynaklar: [CTID · Adversary Emulation Library: APT29](https://github.com/center-for-threat-informed-defense/adversary_emulation_library/tree/master/apt29), [MITRE ATT&CK · APT29 (G0016)](https://attack.mitre.org/groups/G0016/), [MITRE ATT&CK · Enterprise sürüm notları](https://attack.mitre.org/resources/updates/), [MITRE ATT&CK · T1003 OS Credential Dumping](https://attack.mitre.org/techniques/T1003/). Bu dersteki bütün sayılar yalnız yerel kanıttan gelir.

Purple bağı: pu01 kapsamı ATT&CK ile ölçtü, pu04 istihbarattan avcılığa geçti, pu13 öykünme araçlarını tanıttı. Bu ders gerçek bir planı okuyup pu21'in tatbikat defterine girecek satırları üretir; Dalga C'deki bitirme dersi (purple-10) aynı planı izole labda uçtan uca öykünecektir.
:::

::: tahmin Doğal sıra ve alt teknik adı
Çıktıyı tahmin et, sonra Çalıştır ile karşılaştır.
```python
adimlar = ["10.A", "2.B.1", "2.B", "1.A"]
print(sorted(adimlar))
ad = "Masquerading: Match Legitimate Name or Location"
print(ad.split(": ", 1)[1])
tel = {"T1134.001": []}
print(tel.get("T1134.001"), tel.get("T1134"))
```
???
```cikti
['1.A', '10.A', '2.B', '2.B.1']
Match Legitimate Name or Location
[] None
```
Tahmininle gerçek çıktı arasındaki farkı tezgâhta yorum satırı olarak yaz: metin sıralaması `10.A`'yı neden ikinci sıraya koydu? Son satırdaki `[]` ile `None` test planında neden farklı anlamlara gelir? Sonra üç kusurlu başlangıç kodunu çalıştır. Hangisi plan ayrıntısını konumuna güvenerek atlayıp adımları metin olarak sıralıyor, hangisi alt teknik adını kırpmadan karşılaştırıp emekli ve kullanım dışı kimlikleri hiç tanımıyor, hangisi yalnız tam kimlikle telemetri arayıp ikinci makine gerektiren adımı "planla" sayıyor? Önce kendin teşhis et; açıklama çözümün ardından gelir.
:::

::: gorev 1 · Öykünme planının adımlarını oku
`plan_adimlari(belge)`: `belge`, CTID öykünme planı YAML'ının güvenli okunmuş hâlidir: bir liste. `technique` anahtarı olmayan öğeler (plan ayrıntısı gibi) atlanır. Her adım için `{"adim": procedure_step, "teknik": technique.attack_id, "ad": technique.name, "taktik": tactic, "yurutucu": executors içindeki farklı name değerleri (sıralı; executors yoksa ya da None ise boş), "girdi": input_arguments anahtarları (sıralı; yoksa ya da None ise boş)}` üret.

- `adim` `1.A`, `2.B.1`, `10.A.3` biçiminde olmalı: bir sayıyla başlar, noktayla ayrılmış büyük harf ya da rakam parçaları izler.
- `teknik` `T` + dört rakam, isteğe bağlı olarak `.` + üç rakam olmalı.
- Listeyi **doğal sırayla** döndür: parçalar soldan karşılaştırılır, sayı parçası sayı olarak; aynı konumda sayı, harften önce gelir; kısa olan önce gelir (`2.B` < `2.B.1` < `10.A`).

`belge` liste değilse, öğe bozuksa, biçim tutmuyorsa ya da aynı adım iki kez geçiyorsa `ValueError`. Komut metinlerine **dokunma**; plana yalnız kimlikler girer.

```starter
# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def plan_adimlari(belge):
    out=[]
    for x in belge[1:]:
        out.append({"adim":x["procedure_step"],"teknik":x["technique"]["attack_id"],"ad":x["technique"]["name"],"taktik":x["tactic"],
                    "yurutucu":[e["name"] for e in x["executors"]],"girdi":list(x["input_arguments"] or {})})
    return sorted(out,key=lambda a:a["adim"])

import json
from pathlib import Path
v=json.loads(Path("istihbarat/ornekler.json").read_text(encoding="utf-8"))
for a in plan_adimlari(v["plan"]):print(a)
```

```solution
import re
def _anahtar(a):
    return [(not p.isdigit(),int(p) if p.isdigit() else p) for p in a.split(".")]
def plan_adimlari(belge):
    if not isinstance(belge,list):raise ValueError("belge")
    out=[]
    try:
        for x in belge:
            if "technique" not in x:continue
            adim=x["procedure_step"]
            if not isinstance(adim,str) or not re.fullmatch(r"\d+(\.[A-Z0-9]+)*",adim):raise ValueError("adım: "+repr(adim))
            teknik=x["technique"]["attack_id"]
            if not isinstance(teknik,str) or not re.fullmatch(r"T\d{4}(\.\d{3})?",teknik):raise ValueError("teknik: "+repr(teknik))
            out.append({"adim":adim,"teknik":teknik,"ad":x["technique"]["name"],"taktik":x["tactic"],
                        "yurutucu":sorted({e["name"] for e in x.get("executors") or []}),"girdi":sorted(x.get("input_arguments") or {})})
    except (KeyError,TypeError,AttributeError):raise ValueError("bozuk plan")
    if len({a["adim"] for a in out})!=len(out):raise ValueError("yinelenen adım")
    return sorted(out,key=lambda a:_anahtar(a["adim"]))

import json
from pathlib import Path
v=json.loads(Path("istihbarat/ornekler.json").read_text(encoding="utf-8"))
for a in plan_adimlari(v["plan"]):print(a)
```

```test
need('plan_adimlari')
def sinama1(f):
    try:
        def A(adim,tid,ad,taktik,ex=("powershell",),girdi=None,**e):
            x={"id":"x","name":"n","tactic":taktik,"technique":{"attack_id":tid,"name":ad},"procedure_step":adim,"input_arguments":girdi}
            if ex is not None:x["executors"]=[{"name":k,"command":"(komut)"} for k in ex]
            x.update(e);return x
        def B(adim,tid,ad,taktik,y,g):return {"adim":adim,"teknik":tid,"ad":ad,"taktik":taktik,"yurutucu":y,"girdi":g}
        belge=[{"emulation_plan_details":{"id":"p"}},A("10.A","T1003","Credential Dumping","credential-access",("powershell",),{"z":{},"a":{}}),
               A("2.B.1","T1082","System Information Discovery","discovery",("powershell","command_prompt","powershell")),A("2.A","T1059.001","Command and Scripting Interpreter: PowerShell","execution",()),
               A("1.B","T1105","Ingress Tool Transfer","command-and-control",None),A("2.B","T1057","Process Discovery","discovery",("cmd",),{}),A("3.A","T1033","U","discovery"),A("3.1","T1016","N","discovery")]
        bek=[B("1.B","T1105","Ingress Tool Transfer","command-and-control",[],[]),B("2.A","T1059.001","Command and Scripting Interpreter: PowerShell","execution",[],[]),
             B("2.B","T1057","Process Discovery","discovery",["cmd"],[]),B("2.B.1","T1082","System Information Discovery","discovery",["command_prompt","powershell"],[]),
             B("3.1","T1016","N","discovery",["powershell"],[]),B("3.A","T1033","U","discovery",["powershell"],[]),B("10.A","T1003","Credential Dumping","credential-access",["powershell"],["a","z"])]
        if f(belge)!=bek:return False
        if f([])!=[] or f([{"emulation_plan_details":{}}])!=[]:return False
        x=A("1.A","T1000","a","b");x["executors"]=None
        if f([x])!=[B("1.A","T1000","a","b",[],[])]:return False
        for b in (None,{"plan":[]},[None],[{"technique":None,"tactic":"x","procedure_step":"1.A"}],[{"technique":{},"tactic":"x","procedure_step":"1.A"}],[A("1-A","T1003","a","b")],[A(5,"T1003","a","b")],[A("1.a","T1003","a","b")],[A("1.","T1003","a","b")],[A("A.1","T1003","a","b")],
                  [A("1.A","T10","a","b")],[A("1.A","t1003","a","b")],[A("1.A","T1003.1","a","b")],[A("1.A",1003,"a","b")],[{"technique":{"attack_id":"T1003","name":"a"},"tactic":"b"}],
                  [{"technique":{"attack_id":"T1003"},"tactic":"b","procedure_step":"1.A"}],[{"technique":{"attack_id":"T1003","name":"a"},"procedure_step":"1.A"}],
                  [A("1.A","T1003","a","b"),A("1.A","T1082","c","d")],[A("1.A","T1003","a","b",ex=None,executors=[{"command":"x"}])]):
            try:f(b);return False
            except ValueError:pass
        return True
    except Exception:return False
ok(sinama1(plan_adimlari),"adım ayıklama, doğal sıra, yürütücü ve girdi biçimi, kimlik doğrulaması, yinelenen adım")
def _bos(b):
    try:return plan_adimlari(b)
    except ValueError:return []
for ad,mut in [("metin sırası",lambda b:sorted(plan_adimlari(b),key=lambda a:a["adim"])),("yürütücü sırasız",lambda b:[dict(a,yurutucu=a["yurutucu"][::-1]) for a in plan_adimlari(b)]),("bozukta boş",_bos)]:
    ok(not sinama1(mut),"mutant reddedildi: "+ad)
```

```setup
import sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_istihbarat_lab import hazirla
hazirla()
```

```hint
Metin sıralamasında `10.A`, `2.A`'dan önce gelir. Her parçayı sayı ya da harf olarak etiketleyip demet listesine çevir.
```
:::

::: anlat İstihbarat da sürümlenir
ATT&CK yılda iki kez sürüm çıkarır. Teknikler alt tekniklere bölünür, adlar netleşir, bazı kimlikler emekli olur ve yerini başka bir kimliğe bırakır. Bir CTI raporu, bir öykünme planı ya da bir kural kütüphanesi hangi ATT&CK sürümüyle yazıldığını söylemelidir. APT29 planının ayrıntısında `attack_version: 8.1` yazar. Denetim, plandaki kimliği değiştirmez. Yalnız "bugün bu kimlik ne diyor?" sorusunu yanıtlar, böylece kural ve rapor eşlemeleri güncel kimlikle yapılır.
:::

::: gorev 2 · Teknikleri bugünkü ATT&CK'e karşı denetle
`attack_denetle(adimlar, attack)`: `attack`, çalışma klasöründeki `attack.json` (ATT&CK Enterprise 19.2 özeti): `teknikler` (`id`, `ad`), `emekli` (eski kimlik → yeni kimlik) ve `kullanim_disi` (kimlik listesi). Her **farklı** teknik için (adı ilk göründüğü adımdan alınır) bir kayıt üret: `{"teknik", "plan_adi", "durum", "guncel_ad", "yeni"}`.

- Öncelik sırası: `kullanim_disi`'ndaysa `"kullanim-disi"`; `emekli`'deyse `"emekli"` (`yeni` = yeni kimlik, `guncel_ad` = yeni kimliğin adı ya da yoksa `None`); `teknikler`'de yoksa `"bilinmiyor"`; adı farklıysa `"yeniden-adlandirildi"`; değilse `"gecerli"`.
- **Alt teknik** (kimlikte `.` var) ve plan adında `": "` varsa, karşılaştırmada ilk `": "`'dan sonrası kullanılır (`Masquerading: Right-to-Left Override` → `Right-to-Left Override`). Üst tekniğin adı kırpılmaz.
- `guncel_ad`, `gecerli` ve `yeniden-adlandirildi` durumunda ATT&CK'teki addır; `kullanim-disi` ve `bilinmiyor`'da `None`. `yeni` yalnız `emekli`'de doludur.
- Listeyi `teknik`'e göre sıralı döndür. Eksik anahtar ya da yanlış tür `ValueError` verir.

```starter
# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def attack_denetle(adimlar,attack):
    teknik={t["id"]:t["ad"] for t in attack["teknikler"]}
    out=[]
    for a in adimlar:
        i=a["teknik"]
        if i not in teknik:d="bilinmiyor"
        elif teknik[i]!=a["ad"]:d="yeniden-adlandirildi"
        else:d="gecerli"
        out.append({"teknik":i,"plan_adi":a["ad"],"durum":d,"guncel_ad":teknik.get(i),"yeni":None})
    return out

import json
from pathlib import Path
v=json.loads(Path("istihbarat/ornekler.json").read_text(encoding="utf-8"))
attack=json.loads(Path("attack.json").read_text(encoding="utf-8"))
adimlar=[{"teknik":x["technique"]["attack_id"],"ad":x["technique"]["name"]} for x in v["plan"] if "technique" in x]
for d in attack_denetle(adimlar,attack):print(d)
```

```solution
def attack_denetle(adimlar,attack):
    try:
        teknik={t["id"]:t["ad"] for t in attack["teknikler"]}
        emekli,kd=attack["emekli"],set(attack["kullanim_disi"])
        out={}
        for a in adimlar:
            i,ad=a["teknik"],a["ad"]
            if i in out:continue
            kisa=ad.split(": ",1)[1] if "." in i and ": " in ad else ad
            if i in kd:d={"durum":"kullanim-disi","guncel_ad":None,"yeni":None}
            elif i in emekli:d={"durum":"emekli","guncel_ad":teknik.get(emekli[i]),"yeni":emekli[i]}
            elif i not in teknik:d={"durum":"bilinmiyor","guncel_ad":None,"yeni":None}
            elif teknik[i]!=kisa:d={"durum":"yeniden-adlandirildi","guncel_ad":teknik[i],"yeni":None}
            else:d={"durum":"gecerli","guncel_ad":teknik[i],"yeni":None}
            out[i]=dict(teknik=i,plan_adi=ad,**d)
    except (KeyError,TypeError,AttributeError):raise ValueError("bozuk girdi")
    return [out[k] for k in sorted(out)]

import json
from pathlib import Path
v=json.loads(Path("istihbarat/ornekler.json").read_text(encoding="utf-8"))
attack=json.loads(Path("attack.json").read_text(encoding="utf-8"))
adimlar=[{"teknik":x["technique"]["attack_id"],"ad":x["technique"]["name"]} for x in v["plan"] if "technique" in x]
for d in attack_denetle(adimlar,attack):print(d)
```

```test
need('attack_denetle')
def sinama2(f):
    try:
        at={"teknikler":[{"id":"T1003","ad":"OS Credential Dumping"},{"id":"T1059.001","ad":"PowerShell"},{"id":"T1036.005","ad":"Match Legitimate Resource Name or Location"},
                         {"id":"T1082","ad":"System Information Discovery"},{"id":"T1560","ad":"Archive Collected Data"},{"id":"T1218.011","ad":"Rundll32"}],
            "emekli":{"T1002":"T1560","T1999":"T1888","T1064":"T1059"},"kullanim_disi":["T1064"]}
        def a(i,ad):return {"adim":"1","teknik":i,"ad":ad,"taktik":"x","yurutucu":[],"girdi":[]}
        adim=[a("T1082","System Information Discovery"),a("T1059.001","Command and Scripting Interpreter: PowerShell"),a("T1003","Credential Dumping"),
              a("T1036.005","Masquerading: Match Legitimate Name or Location"),a("T1002","Data Compressed"),a("T1999","Eski"),a("T1064","Scripting"),a("T1777","Bilinmeyen"),
              a("T1082","X"),a("T1218.011","Rundll32"),a("T1560","Archive: Archive Collected Data")]
        def D(i,p,d,g,y=None):return {"teknik":i,"plan_adi":p,"durum":d,"guncel_ad":g,"yeni":y}
        bek=[D("T1002","Data Compressed","emekli","Archive Collected Data","T1560"),D("T1003","Credential Dumping","yeniden-adlandirildi","OS Credential Dumping"),
             D("T1036.005","Masquerading: Match Legitimate Name or Location","yeniden-adlandirildi","Match Legitimate Resource Name or Location"),
             D("T1059.001","Command and Scripting Interpreter: PowerShell","gecerli","PowerShell"),D("T1064","Scripting","kullanim-disi",None),
             D("T1082","System Information Discovery","gecerli","System Information Discovery"),D("T1218.011","Rundll32","gecerli","Rundll32"),
             D("T1560","Archive: Archive Collected Data","yeniden-adlandirildi","Archive Collected Data"),D("T1777","Bilinmeyen","bilinmiyor",None),D("T1999","Eski","emekli",None,"T1888")]
        if f(adim,at)!=bek:return False
        if f([],at)!=[]:return False
        if f([a("T1600.002","Weaken Encryption: Downgrade: System Image")],{"teknikler":[{"id":"T1600.002","ad":"Downgrade: System Image"}],"emekli":{},"kullanim_disi":[]})[0]["durum"]!="gecerli":return False
        for x in (([a("T1003","a")],{"teknikler":[],"emekli":{}}),([a("T1003","a")],{"teknikler":[],"kullanim_disi":[]}),([a("T1003","a")],None),([{"teknik":"T1003"}],at),
                  ([a("T1003","a")],{"teknikler":[{"id":"T1003"}],"emekli":{},"kullanim_disi":[]}),(None,at),([None],at)):
            try:f(*x);return False
            except ValueError:pass
        return True
    except Exception:return False
ok(sinama2(attack_denetle),"geçerli, yeniden adlandırılmış, emekli, kullanım dışı, bilinmeyen; alt teknik adı; ilk görülen ad")
def _bos(a,t):
    try:return attack_denetle(a,t)
    except ValueError:return []
for ad,mut in [("sırasız",lambda a,t:attack_denetle(a,t)[::-1]),("emekli yeni yok",lambda a,t:[dict(d,yeni=None) for d in attack_denetle(a,t)]),("bozukta boş",_bos)]:
    ok(not sinama2(mut),"mutant reddedildi: "+ad)
```

```setup
import sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_istihbarat_lab import hazirla
hazirla()
```

```hint
Plan 2020'de ATT&CK 8.1 ile yazıldı. Alt tekniklerde `Üst: Alt` biçimi kullanılır; özet yalnız alt adı tutar.
```
:::

::: anlat Planla, ertele, kapsam dışı
Bir adımı "planla" diye işaretlemek, onu izole tek makinelik labda güvenle sınayabileceğimiz anlamına gelir. "Ertele" çok makineli bir labı (etki alanı, WinRM ile yatay hareket, uzak paylaşım) bekler. "Kapsam dışı" ise lab sınırının dışına çıkan adımdır, örneğin gerçek bir bulut hesabına sızdırma. Bu adım hiçbir zaman gerçek hizmete karşı koşmaz; gerekirse lab içinde bir taklitle yeniden tasarlanır. Kör nokta ayrı bir eksendir: planlanan bir adım da kör noktada olabilir. O zaman tatbikatın amacı tespit değil, kör noktayı kanıtlamaktır.
:::

::: gorev 3 · Tespit beklentili test planı
`test_plani(adimlar, denetim, telemetri, ortam)`: her adım için, verilen sırayla, bir satır üret: `{"adim", "teknik", "taktik", "durum", "beklenen", "kor_nokta"}`.

- `teknik`: denetimde `yeni` doluysa o, değilse adımın kendi kimliği.
- `beklenen`: `telemetri`'de bu kimlik **anahtar olarak varsa** onun listesi (boş liste, bilinen bir kör noktadır ve üst tekniğe düşülmez); yoksa üst tekniğin (`.`'dan önceki kısım) listesi; o da yoksa boş. Sıralı.
- `kor_nokta`: `beklenen` boşsa `True`.
- `durum`: adımın girdilerinden biri `ortam["dis_girdiler"]`'deyse `"kapsam-disi"` (dış hizmet: lab dışına çıkılmaz); değilse biri `ortam["coklu_makine_girdileri"]`'ndeyse `"ertele"` (çok makineli lab gerekir); değilse `"planla"`.
- `ozet`: her taktik için `planla`, `ertele`, `kapsam-disi` ve `kor_nokta` sayıları; taktik adları sıralı.

Döndür: `{"satirlar": [...], "ozet": {...}}`. Denetimde bulunmayan teknik, eksik anahtar ya da yanlış tür `ValueError` verir.

```starter
# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def test_plani(adimlar,denetim,telemetri,ortam):
    satirlar,ozet=[],{}
    for a in adimlar:
        kaynak=telemetri.get(a["teknik"],[])
        durum="kapsam-disi" if set(ortam["dis_girdiler"])&set(a["girdi"]) else "planla"
        satirlar.append({"adim":a["adim"],"teknik":a["teknik"],"taktik":a["taktik"],"durum":durum,"beklenen":kaynak,"kor_nokta":not kaynak})
        ozet.setdefault(a["taktik"],{"planla":0,"ertele":0,"kapsam-disi":0,"kor_nokta":0})[durum]+=1
    return {"satirlar":satirlar,"ozet":ozet}

import json
from pathlib import Path
v=json.loads(Path("istihbarat/ornekler.json").read_text(encoding="utf-8"))
tel=json.loads(Path("istihbarat/telemetri.json").read_text(encoding="utf-8"))
adimlar=[{"adim":x["procedure_step"],"teknik":x["technique"]["attack_id"],"taktik":x["tactic"],"girdi":sorted(x["input_arguments"] or {})} for x in v["plan"] if "technique" in x]
denetim=[{"teknik":a["teknik"],"yeni":None} for a in adimlar]
p=test_plani(adimlar,denetim,tel["telemetri"],tel["ortam"])
for s in p["satirlar"]:print(s)
for k,o in p["ozet"].items():print(k,o)
```

```solution
DURUMLAR=("planla","ertele","kapsam-disi")
def test_plani(adimlar,denetim,telemetri,ortam):
    try:
        yeni={d["teknik"]:d["yeni"] or d["teknik"] for d in denetim}
        dis,coklu=set(ortam["dis_girdiler"]),set(ortam["coklu_makine_girdileri"])
        satirlar,ozet=[],{}
        for a in adimlar:
            t=yeni[a["teknik"]]
            kaynak=telemetri.get(t)
            if kaynak is None:kaynak=telemetri.get(t.split(".")[0],[])
            if dis&set(a["girdi"]):durum="kapsam-disi"
            elif coklu&set(a["girdi"]):durum="ertele"
            else:durum="planla"
            satirlar.append({"adim":a["adim"],"teknik":t,"taktik":a["taktik"],"durum":durum,"beklenen":sorted(kaynak),"kor_nokta":not kaynak})
            o=ozet.setdefault(a["taktik"],{d:0 for d in DURUMLAR}|{"kor_nokta":0})
            o[durum]+=1
            o["kor_nokta"]+=not kaynak
    except (KeyError,TypeError,AttributeError):raise ValueError("bozuk girdi")
    return {"satirlar":satirlar,"ozet":{k:ozet[k] for k in sorted(ozet)}}

import json
from pathlib import Path
v=json.loads(Path("istihbarat/ornekler.json").read_text(encoding="utf-8"))
tel=json.loads(Path("istihbarat/telemetri.json").read_text(encoding="utf-8"))
adimlar=[{"adim":x["procedure_step"],"teknik":x["technique"]["attack_id"],"taktik":x["tactic"],"girdi":sorted(x["input_arguments"] or {})} for x in v["plan"] if "technique" in x]
denetim=[{"teknik":a["teknik"],"yeni":None} for a in adimlar]
p=test_plani(adimlar,denetim,tel["telemetri"],tel["ortam"])
for s in p["satirlar"]:print(s)
for k,o in p["ozet"].items():print(k,o)
```

```test
need('test_plani')
def sinama3(f):
    try:
        def a(adim,t,tak,g=()):return {"adim":adim,"teknik":t,"ad":"-","taktik":tak,"yurutucu":["powershell"],"girdi":list(g)}
        adim=[a("1.A","T1059.001","execution",["server"]),a("1.B","T1003","credential-access"),a("2.A","T1003.001","credential-access",["target.winrm.remote_host"]),
              a("3.A","T1002","collection",["onedrive.url","target.ntlm"]),a("4.A","T1134.001","privilege-escalation"),a("4.B","T1082","discovery"),a("0.Z","T1999","discovery",["x"])]
        den=[{"teknik":"T1059.001","yeni":None},{"teknik":"T1003","yeni":None},{"teknik":"T1003.001","yeni":None},{"teknik":"T1002","yeni":"T1560","durum":"emekli"},
             {"teknik":"T1134.001","yeni":None},{"teknik":"T1082","yeni":None},{"teknik":"T1999","yeni":None}]
        tel={"T1059.001":["PowerShell 4104"],"T1003":["Sysmon 10"],"T1560":["Sysmon 11","Sysmon 1"],"T1134":["Security 4624"],"T1134.001":[],"T1082":["Sysmon 1"],"T1002":["YANLIŞ"]}
        ort={"dis_girdiler":["onedrive.url"],"coklu_makine_girdileri":("target.winrm.remote_host","target.ntlm")}
        def S(ad,t,tak,d,b):return {"adim":ad,"teknik":t,"taktik":tak,"durum":d,"beklenen":b,"kor_nokta":not b}
        bek={"satirlar":[S("1.A","T1059.001","execution","planla",["PowerShell 4104"]),S("1.B","T1003","credential-access","planla",["Sysmon 10"]),
                         S("2.A","T1003.001","credential-access","ertele",["Sysmon 10"]),S("3.A","T1560","collection","kapsam-disi",["Sysmon 1","Sysmon 11"]),
                         S("4.A","T1134.001","privilege-escalation","planla",[]),S("4.B","T1082","discovery","planla",["Sysmon 1"]),S("0.Z","T1999","discovery","planla",[])],
             "ozet":{"collection":{"planla":0,"ertele":0,"kapsam-disi":1,"kor_nokta":0},"credential-access":{"planla":1,"ertele":1,"kapsam-disi":0,"kor_nokta":0},
                     "discovery":{"planla":2,"ertele":0,"kapsam-disi":0,"kor_nokta":1},"execution":{"planla":1,"ertele":0,"kapsam-disi":0,"kor_nokta":0},
                     "privilege-escalation":{"planla":1,"ertele":0,"kapsam-disi":0,"kor_nokta":1}}}
        r=f(adim,den,tel,ort)
        if r!=bek or list(r["ozet"])!=sorted(r["ozet"]):return False
        if f([],den,tel,ort)!={"satirlar":[],"ozet":{}}:return False
        for x in ((adim+[a("9.A","T1111","x")],den,tel,ort),(adim,den,tel,{"dis_girdiler":[]}),(adim,den,tel,{"coklu_makine_girdileri":[]}),(adim,den,None,ort),
                  (adim,[{"teknik":"T1003"}],tel,ort),(None,den,tel,ort),(adim,den,tel,None),([{"adim":"1","teknik":"T1003","taktik":"x"}],den,tel,ort)):
            try:f(*x);return False
            except ValueError:pass
        return True
    except Exception:return False
ok(sinama3(test_plani),"güncel kimlik, alt/üst teknik telemetrisi, açık kör nokta, durum önceliği, taktik özeti")
def _bos(*a):
    try:return test_plani(*a)
    except ValueError:return {"satirlar":[],"ozet":{}}
for ad,mut in [("kör nokta ters",lambda *a:dict(test_plani(*a),satirlar=[dict(s,kor_nokta=not s["kor_nokta"]) for s in test_plani(*a)["satirlar"]])),
               ("ertele planla sayılır",lambda *a:dict(test_plani(*a),satirlar=[dict(s,durum="planla" if s["durum"]=="ertele" else s["durum"]) for s in test_plani(*a)["satirlar"]])),("bozukta boş",_bos)]:
    ok(not sinama3(mut),"mutant reddedildi: "+ad)
```

```setup
import sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_istihbarat_lab import hazirla
hazirla()
```

```hint
Önce güncel kimliği bul, sonra telemetriyi ara. `telemetri.get(k)` ile `telemetri.get(k, [])` farklı şeyler söyler: anahtar yok mu, yoksa açıkça boş mu?
```
:::

::: anlat Hata vitrini · yazar koşusu
Yazar son görevi referans işlevlerle çalıştırdı (Python 3.13, PyYAML 6.0.3 `safe_load`). Koşu yaklaşık 0,3 sn sürdü; hiçbir komut çalıştırılmadı ve çıktıda plandaki komut metinlerinden hiçbiri yoktu.

- **Plan:** 101.876 bayt; sha256 onaylanan değerle aynı. Ayrıntıda `attack_version: 8.1` yazıyor. 79 adım doğal sırayla `1.A`'dan `20.B`'ye diziliyor.
- **ATT&CK 19.2 denetimi:** 42 farklı teknikten 39'u geçerli, 3'ü yeniden adlandırılmış:
  - `T1003` "Credential Dumping" → "OS Credential Dumping"
  - `T1036.005` "… Match Legitimate Name or Location" → "Match Legitimate Resource Name or Location"
  - `T1041` "Exfiltration Over Command and Control Channel" → "Exfiltration Over C2 Channel"

  Emekli, kullanım dışı ya da bilinmeyen kimlik çıkmadı.
- **Denetimin göremediği:** Üst teknik adları da değişti. Plan "Signed Binary Proxy Execution: Rundll32" yazıyor; bugün üst teknik "System Binary Proxy Execution". "Indicator Removal on Host" de bugün "Indicator Removal" adını taşıyor. Görev yalnız alt adı karşılaştırdığı için bu iki değişiklik "geçerli" göründü.
- **Test planı:** 69 adım planlandı. 9 adım ertelendi: WinRM, uzak paylaşım, pivot makine ve etki alanı/NTLM girdileri ikinci bir makine istiyor. 1 adım kapsam dışı kaldı: OneDrive'a sızdırma.
- **Kör noktalar:** 11 teknik kör noktada: `T1005`, `T1012`, `T1056.001`, `T1083`, `T1113`, `T1114.001`, `T1115`, `T1119`, `T1134.001`, `T1537`, `T1552.004`. Toplama (collection) taktiğinin 7 adımının 7'si kör noktada.

Kendi cümlenle açıkla: üst teknik adındaki değişikliği de yakalamak için `attack_denetle`'ye hangi veriyi eklerdin? Bu varsayımsal telemetriye hangi tek kaynağı eklemek en çok kör noktayı kapatırdı?
:::

::: gorev Gerçek deney · APT29 planından yerel test planı
Üç işlevi birleştir. Alttaki `calistir` satırı gerçek deneyi başlatır; silme. Koşu, `.deps` altındaki gerçek CTID APT29 öykünme planını (commit `4467a6ee`, sha256'sı onaylanan değerle karşılaştırılır) güvenli YAML okuyucusuyla okur. Adımları senin `plan_adimlari`'nla ayıklar, `attack_denetle` ile ATT&CK 19.2'ye karşı denetler ve `test_plani` ile `istihbarat/telemetri.json`'daki varsayımsal izole VM telemetrisine göre test planını üretir. Her sonuç referansla karşılaştırılır. Koşu **hiçbir komutu çalıştırmaz**; plandaki komut metinlerinin hiçbirinin çıktına girmediği de ayrıca denetlenir. Run deneme kanıtı yazar, Check ayrıca kabul kanıtını yazar; yol stdout'ta görünür.

```starter
import json
import re
# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def plan_adimlari(belge):
    out=[]
    for x in belge[1:]:
        out.append({"adim":x["procedure_step"],"teknik":x["technique"]["attack_id"],"ad":x["technique"]["name"],"taktik":x["tactic"],
                    "yurutucu":[e["name"] for e in x["executors"]],"girdi":list(x["input_arguments"] or {})})
    return sorted(out,key=lambda a:a["adim"])

# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def attack_denetle(adimlar,attack):
    teknik={t["id"]:t["ad"] for t in attack["teknikler"]}
    out=[]
    for a in adimlar:
        i=a["teknik"]
        if i not in teknik:d="bilinmiyor"
        elif teknik[i]!=a["ad"]:d="yeniden-adlandirildi"
        else:d="gecerli"
        out.append({"teknik":i,"plan_adi":a["ad"],"durum":d,"guncel_ad":teknik.get(i),"yeni":None})
    return out

# KUSURLU BAŞLANGIÇ KODU: teşhis et; kusuru çözümü açmadan önce tahmin et.
def test_plani(adimlar,denetim,telemetri,ortam):
    satirlar,ozet=[],{}
    for a in adimlar:
        kaynak=telemetri.get(a["teknik"],[])
        durum="kapsam-disi" if set(ortam["dis_girdiler"])&set(a["girdi"]) else "planla"
        satirlar.append({"adim":a["adim"],"teknik":a["teknik"],"taktik":a["taktik"],"durum":durum,"beklenen":kaynak,"kor_nokta":not kaynak})
        ozet.setdefault(a["taktik"],{"planla":0,"ertele":0,"kapsam-disi":0,"kor_nokta":0})[durum]+=1
    return {"satirlar":satirlar,"ozet":ozet}

from purple_istihbarat_lab import calistir
calistir(plan_adimlari,attack_denetle,test_plani)
```

```solution
import json
import re
def _anahtar(a):
    return [(not p.isdigit(),int(p) if p.isdigit() else p) for p in a.split(".")]
def plan_adimlari(belge):
    if not isinstance(belge,list):raise ValueError("belge")
    out=[]
    try:
        for x in belge:
            if "technique" not in x:continue
            adim=x["procedure_step"]
            if not isinstance(adim,str) or not re.fullmatch(r"\d+(\.[A-Z0-9]+)*",adim):raise ValueError("adım: "+repr(adim))
            teknik=x["technique"]["attack_id"]
            if not isinstance(teknik,str) or not re.fullmatch(r"T\d{4}(\.\d{3})?",teknik):raise ValueError("teknik: "+repr(teknik))
            out.append({"adim":adim,"teknik":teknik,"ad":x["technique"]["name"],"taktik":x["tactic"],
                        "yurutucu":sorted({e["name"] for e in x.get("executors") or []}),"girdi":sorted(x.get("input_arguments") or {})})
    except (KeyError,TypeError,AttributeError):raise ValueError("bozuk plan")
    if len({a["adim"] for a in out})!=len(out):raise ValueError("yinelenen adım")
    return sorted(out,key=lambda a:_anahtar(a["adim"]))

def attack_denetle(adimlar,attack):
    try:
        teknik={t["id"]:t["ad"] for t in attack["teknikler"]}
        emekli,kd=attack["emekli"],set(attack["kullanim_disi"])
        out={}
        for a in adimlar:
            i,ad=a["teknik"],a["ad"]
            if i in out:continue
            kisa=ad.split(": ",1)[1] if "." in i and ": " in ad else ad
            if i in kd:d={"durum":"kullanim-disi","guncel_ad":None,"yeni":None}
            elif i in emekli:d={"durum":"emekli","guncel_ad":teknik.get(emekli[i]),"yeni":emekli[i]}
            elif i not in teknik:d={"durum":"bilinmiyor","guncel_ad":None,"yeni":None}
            elif teknik[i]!=kisa:d={"durum":"yeniden-adlandirildi","guncel_ad":teknik[i],"yeni":None}
            else:d={"durum":"gecerli","guncel_ad":teknik[i],"yeni":None}
            out[i]=dict(teknik=i,plan_adi=ad,**d)
    except (KeyError,TypeError,AttributeError):raise ValueError("bozuk girdi")
    return [out[k] for k in sorted(out)]

DURUMLAR=("planla","ertele","kapsam-disi")
def test_plani(adimlar,denetim,telemetri,ortam):
    try:
        yeni={d["teknik"]:d["yeni"] or d["teknik"] for d in denetim}
        dis,coklu=set(ortam["dis_girdiler"]),set(ortam["coklu_makine_girdileri"])
        satirlar,ozet=[],{}
        for a in adimlar:
            t=yeni[a["teknik"]]
            kaynak=telemetri.get(t)
            if kaynak is None:kaynak=telemetri.get(t.split(".")[0],[])
            if dis&set(a["girdi"]):durum="kapsam-disi"
            elif coklu&set(a["girdi"]):durum="ertele"
            else:durum="planla"
            satirlar.append({"adim":a["adim"],"teknik":t,"taktik":a["taktik"],"durum":durum,"beklenen":sorted(kaynak),"kor_nokta":not kaynak})
            o=ozet.setdefault(a["taktik"],{d:0 for d in DURUMLAR}|{"kor_nokta":0})
            o[durum]+=1
            o["kor_nokta"]+=not kaynak
    except (KeyError,TypeError,AttributeError):raise ValueError("bozuk girdi")
    return {"satirlar":satirlar,"ozet":{k:ozet[k] for k in sorted(ozet)}}

from purple_istihbarat_lab import calistir
calistir(plan_adimlari,attack_denetle,test_plani)
```

```test
need('plan_adimlari');need('attack_denetle');need('test_plani')
from purple_istihbarat_lab import kod_koruma,calistir
ok(kod_koruma(src),'kaynak koruması: referans/dinamik kod/özel öznitelik yok')
if not kod_koruma(src):stop()
def sinama1(f):
    try:
        def A(adim,tid,ad,taktik,ex=("powershell",),girdi=None,**e):
            x={"id":"x","name":"n","tactic":taktik,"technique":{"attack_id":tid,"name":ad},"procedure_step":adim,"input_arguments":girdi}
            if ex is not None:x["executors"]=[{"name":k,"command":"(komut)"} for k in ex]
            x.update(e);return x
        def B(adim,tid,ad,taktik,y,g):return {"adim":adim,"teknik":tid,"ad":ad,"taktik":taktik,"yurutucu":y,"girdi":g}
        belge=[{"emulation_plan_details":{"id":"p"}},A("10.A","T1003","Credential Dumping","credential-access",("powershell",),{"z":{},"a":{}}),
               A("2.B.1","T1082","System Information Discovery","discovery",("powershell","command_prompt","powershell")),A("2.A","T1059.001","Command and Scripting Interpreter: PowerShell","execution",()),
               A("1.B","T1105","Ingress Tool Transfer","command-and-control",None),A("2.B","T1057","Process Discovery","discovery",("cmd",),{}),A("3.A","T1033","U","discovery"),A("3.1","T1016","N","discovery")]
        bek=[B("1.B","T1105","Ingress Tool Transfer","command-and-control",[],[]),B("2.A","T1059.001","Command and Scripting Interpreter: PowerShell","execution",[],[]),
             B("2.B","T1057","Process Discovery","discovery",["cmd"],[]),B("2.B.1","T1082","System Information Discovery","discovery",["command_prompt","powershell"],[]),
             B("3.1","T1016","N","discovery",["powershell"],[]),B("3.A","T1033","U","discovery",["powershell"],[]),B("10.A","T1003","Credential Dumping","credential-access",["powershell"],["a","z"])]
        if f(belge)!=bek:return False
        if f([])!=[] or f([{"emulation_plan_details":{}}])!=[]:return False
        x=A("1.A","T1000","a","b");x["executors"]=None
        if f([x])!=[B("1.A","T1000","a","b",[],[])]:return False
        for b in (None,{"plan":[]},[None],[{"technique":None,"tactic":"x","procedure_step":"1.A"}],[{"technique":{},"tactic":"x","procedure_step":"1.A"}],[A("1-A","T1003","a","b")],[A(5,"T1003","a","b")],[A("1.a","T1003","a","b")],[A("1.","T1003","a","b")],[A("A.1","T1003","a","b")],
                  [A("1.A","T10","a","b")],[A("1.A","t1003","a","b")],[A("1.A","T1003.1","a","b")],[A("1.A",1003,"a","b")],[{"technique":{"attack_id":"T1003","name":"a"},"tactic":"b"}],
                  [{"technique":{"attack_id":"T1003"},"tactic":"b","procedure_step":"1.A"}],[{"technique":{"attack_id":"T1003","name":"a"},"procedure_step":"1.A"}],
                  [A("1.A","T1003","a","b"),A("1.A","T1082","c","d")],[A("1.A","T1003","a","b",ex=None,executors=[{"command":"x"}])]):
            try:f(b);return False
            except ValueError:pass
        return True
    except Exception:return False
def sinama2(f):
    try:
        at={"teknikler":[{"id":"T1003","ad":"OS Credential Dumping"},{"id":"T1059.001","ad":"PowerShell"},{"id":"T1036.005","ad":"Match Legitimate Resource Name or Location"},
                         {"id":"T1082","ad":"System Information Discovery"},{"id":"T1560","ad":"Archive Collected Data"},{"id":"T1218.011","ad":"Rundll32"}],
            "emekli":{"T1002":"T1560","T1999":"T1888","T1064":"T1059"},"kullanim_disi":["T1064"]}
        def a(i,ad):return {"adim":"1","teknik":i,"ad":ad,"taktik":"x","yurutucu":[],"girdi":[]}
        adim=[a("T1082","System Information Discovery"),a("T1059.001","Command and Scripting Interpreter: PowerShell"),a("T1003","Credential Dumping"),
              a("T1036.005","Masquerading: Match Legitimate Name or Location"),a("T1002","Data Compressed"),a("T1999","Eski"),a("T1064","Scripting"),a("T1777","Bilinmeyen"),
              a("T1082","X"),a("T1218.011","Rundll32"),a("T1560","Archive: Archive Collected Data")]
        def D(i,p,d,g,y=None):return {"teknik":i,"plan_adi":p,"durum":d,"guncel_ad":g,"yeni":y}
        bek=[D("T1002","Data Compressed","emekli","Archive Collected Data","T1560"),D("T1003","Credential Dumping","yeniden-adlandirildi","OS Credential Dumping"),
             D("T1036.005","Masquerading: Match Legitimate Name or Location","yeniden-adlandirildi","Match Legitimate Resource Name or Location"),
             D("T1059.001","Command and Scripting Interpreter: PowerShell","gecerli","PowerShell"),D("T1064","Scripting","kullanim-disi",None),
             D("T1082","System Information Discovery","gecerli","System Information Discovery"),D("T1218.011","Rundll32","gecerli","Rundll32"),
             D("T1560","Archive: Archive Collected Data","yeniden-adlandirildi","Archive Collected Data"),D("T1777","Bilinmeyen","bilinmiyor",None),D("T1999","Eski","emekli",None,"T1888")]
        if f(adim,at)!=bek:return False
        if f([],at)!=[]:return False
        if f([a("T1600.002","Weaken Encryption: Downgrade: System Image")],{"teknikler":[{"id":"T1600.002","ad":"Downgrade: System Image"}],"emekli":{},"kullanim_disi":[]})[0]["durum"]!="gecerli":return False
        for x in (([a("T1003","a")],{"teknikler":[],"emekli":{}}),([a("T1003","a")],{"teknikler":[],"kullanim_disi":[]}),([a("T1003","a")],None),([{"teknik":"T1003"}],at),
                  ([a("T1003","a")],{"teknikler":[{"id":"T1003"}],"emekli":{},"kullanim_disi":[]}),(None,at),([None],at)):
            try:f(*x);return False
            except ValueError:pass
        return True
    except Exception:return False
def sinama3(f):
    try:
        def a(adim,t,tak,g=()):return {"adim":adim,"teknik":t,"ad":"-","taktik":tak,"yurutucu":["powershell"],"girdi":list(g)}
        adim=[a("1.A","T1059.001","execution",["server"]),a("1.B","T1003","credential-access"),a("2.A","T1003.001","credential-access",["target.winrm.remote_host"]),
              a("3.A","T1002","collection",["onedrive.url","target.ntlm"]),a("4.A","T1134.001","privilege-escalation"),a("4.B","T1082","discovery"),a("0.Z","T1999","discovery",["x"])]
        den=[{"teknik":"T1059.001","yeni":None},{"teknik":"T1003","yeni":None},{"teknik":"T1003.001","yeni":None},{"teknik":"T1002","yeni":"T1560","durum":"emekli"},
             {"teknik":"T1134.001","yeni":None},{"teknik":"T1082","yeni":None},{"teknik":"T1999","yeni":None}]
        tel={"T1059.001":["PowerShell 4104"],"T1003":["Sysmon 10"],"T1560":["Sysmon 11","Sysmon 1"],"T1134":["Security 4624"],"T1134.001":[],"T1082":["Sysmon 1"],"T1002":["YANLIŞ"]}
        ort={"dis_girdiler":["onedrive.url"],"coklu_makine_girdileri":("target.winrm.remote_host","target.ntlm")}
        def S(ad,t,tak,d,b):return {"adim":ad,"teknik":t,"taktik":tak,"durum":d,"beklenen":b,"kor_nokta":not b}
        bek={"satirlar":[S("1.A","T1059.001","execution","planla",["PowerShell 4104"]),S("1.B","T1003","credential-access","planla",["Sysmon 10"]),
                         S("2.A","T1003.001","credential-access","ertele",["Sysmon 10"]),S("3.A","T1560","collection","kapsam-disi",["Sysmon 1","Sysmon 11"]),
                         S("4.A","T1134.001","privilege-escalation","planla",[]),S("4.B","T1082","discovery","planla",["Sysmon 1"]),S("0.Z","T1999","discovery","planla",[])],
             "ozet":{"collection":{"planla":0,"ertele":0,"kapsam-disi":1,"kor_nokta":0},"credential-access":{"planla":1,"ertele":1,"kapsam-disi":0,"kor_nokta":0},
                     "discovery":{"planla":2,"ertele":0,"kapsam-disi":0,"kor_nokta":1},"execution":{"planla":1,"ertele":0,"kapsam-disi":0,"kor_nokta":0},
                     "privilege-escalation":{"planla":1,"ertele":0,"kapsam-disi":0,"kor_nokta":1}}}
        r=f(adim,den,tel,ort)
        if r!=bek or list(r["ozet"])!=sorted(r["ozet"]):return False
        if f([],den,tel,ort)!={"satirlar":[],"ozet":{}}:return False
        for x in ((adim+[a("9.A","T1111","x")],den,tel,ort),(adim,den,tel,{"dis_girdiler":[]}),(adim,den,tel,{"coklu_makine_girdileri":[]}),(adim,den,None,ort),
                  (adim,[{"teknik":"T1003"}],tel,ort),(None,den,tel,ort),(adim,den,tel,None),([{"adim":"1","teknik":"T1003","taktik":"x"}],den,tel,ort)):
            try:f(*x);return False
            except ValueError:pass
        return True
    except Exception:return False
tamam=sinama1(plan_adimlari) and sinama2(attack_denetle) and sinama3(test_plani)
ok(tamam,"üç işlev gizli verilerle doğru")
def _bos(b):
    try:return plan_adimlari(b)
    except ValueError:return []
for ad,mut in [("metin sırası",lambda b:sorted(plan_adimlari(b),key=lambda a:a["adim"])),("yürütücü sırasız",lambda b:[dict(a,yurutucu=a["yurutucu"][::-1]) for a in plan_adimlari(b)]),("bozukta boş",_bos)]:
    ok(not sinama1(mut),"mutant reddedildi: "+ad)
def _bos(a,t):
    try:return attack_denetle(a,t)
    except ValueError:return []
for ad,mut in [("sırasız",lambda a,t:attack_denetle(a,t)[::-1]),("emekli yeni yok",lambda a,t:[dict(d,yeni=None) for d in attack_denetle(a,t)]),("bozukta boş",_bos)]:
    ok(not sinama2(mut),"mutant reddedildi: "+ad)
def _bos(*a):
    try:return test_plani(*a)
    except ValueError:return {"satirlar":[],"ozet":{}}
for ad,mut in [("kör nokta ters",lambda *a:dict(test_plani(*a),satirlar=[dict(s,kor_nokta=not s["kor_nokta"]) for s in test_plani(*a)["satirlar"]])),
               ("ertele planla sayılır",lambda *a:dict(test_plani(*a),satirlar=[dict(s,durum="planla" if s["durum"]=="ertele" else s["durum"]) for s in test_plani(*a)["satirlar"]])),("bozukta boş",_bos)]:
    ok(not sinama3(mut),"mutant reddedildi: "+ad)
if not tamam:stop()
k=calistir(plan_adimlari,attack_denetle,test_plani,kabul=True)
eq(k['kaynak'],'gercek','gerçek CTID APT29 planı')
ok(k['kabul'],'gerçek kabul: üç işlev gerçek planda referansla aynı')
eq(k['plan']['sha256'],'644f28185097f545e522ca8ed04b43f19ec8b31ace864d347feb138bc56c1615','onaylanan plan dosyası')
eq(k['adim_sayisi'],79,'79 öykünme adımı')
eq(k['komut_sizintisi'],0,'plana komut metni girmedi')
eq(k['calistirilan_komut'],0,'hiçbir komut çalıştırılmadı')
eq(k['denetim_ozet']['bilinmiyor'],0,'plandaki bütün teknikler ATT&CK 19.2 içinde')
ok(k['denetim_ozet']['yeniden-adlandirildi']>0,'2020 planındaki bazı teknik adları bugün farklı')
```

```setup
import sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_istihbarat_lab import hazirla
hazirla()
```

```hint
Önceki üç işlevi aynen birleştir. Kanıtta `kor_nokta` listesine bak: hangi taktiklerde toplanıyor?
```
:::

::: anlat Sınır
Bu ders gerçek CTID APT29 öykünme planını yalnız okur; adımları ayıklar, teknikleri ATT&CK 19.2'ye karşı denetler ve varsayımsal bir izole VM telemetrisine göre tespit beklentili bir test planı üretir. Planın hiçbir komutunu çalıştırmaz. Telemetri eşlemesini ölçmez, APT29'un güncel davranışını, planın kendisinin doğruluğunu ve bir güvenlik ürününün başarısını değerlendirmez.
:::
