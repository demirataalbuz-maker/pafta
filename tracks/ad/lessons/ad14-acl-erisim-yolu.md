---
id: ad14
title: ACL Kanıtından Erişim Yolunu Çıkarmak
summary: Doğrulanmış etkili hakları iç içe grup üyeliğiyle birleştirip en kısa inceleme yolunu bulmak; hak ile fiili oturumu ayırmak.
---

::: anlat Grafikteki ok ne demek?
Bir erişim yolu için iki ayrı kanıt gerekir: **grup üyeliği** ve **hedefte etkili nesne hakkı**. `acl.json` içindeki `ali.kaya → svc_sql` ilişkisini `WriteDacl` olarak ancak ad13'teki DACL kararından sonra grafiğe ekleriz. `mehmet.yilmaz` aynı gruptadır ama kendi deny kaydı nedeniyle bu kenara sahip değildir. Grup düğümünden doğrudan `svc_sql`'a kenar çizip Mehmet'i de taşımak yanlış pozitif üretir.

BloodHound'un `WriteDacl` kenarı nesnenin DACL'sini düzenleme yeteneğini gösterir; bunun sonraki adımlarla daha geniş etkiye dönüşebilmesi ayrı bir risktir. `GenericAll`, `WriteOwner`, `WriteProperty` gibi haklar ayrı anlam taşır. Grafiği “kanıtlı **inceleme yolu**” olarak kullan; gerçek oturum/kimlik devri ya da otomatik ele geçirme diye yorumlama. [SpecterOps WriteDacl](https://bloodhound.specterops.io/resources/edges/write-dacl), [GenericAll](https://bloodhound.specterops.io/resources/edges/generic-all).

Gerçek etki alanında AD12 laboratuvarındaki nesne ACL'lerini topla, SID'leri çöz, BloodHound CE verisinde hedef kullanıcıya giden ilişkileri aç ve şüpheli her kenarı `Get-Acl` ile karşılaştır. Bu dersin grafiği küçük bir sentetik alt kümedir; BloodHound CE'nin toplama ve hesaplama motoru değildir. [BloodHound CE kurulumu](https://bloodhound.specterops.io/get-started/quickstart/community-edition-quickstart).
:::

::: tahmin Üyelik zincirini oku
Kod, `svc_sql` hesabının doğrudan ve dolaylı grup zincirini hangi sırayla yazar?

```python
import json
v = json.load(open("acl.json", encoding="utf-8"))
x = "svc_sql"
while v["gruplar"].get(x):
    x = v["gruplar"][x][0]
    print(x)
```

???

`Sunucu-Operatorleri`, `Altyapi-Yoneticileri`, `Domain Admins` sırasıyla yazılır. Bu üyelik, `svc_sql` üzerinde etkili `WriteDacl` sahibi olan kişinin mutlaka Domain Admins oturumu açtığı anlamına gelmez; incelenecek risk zinciridir.

```meta
motor: python
dil: python
```
:::

::: gorev Doğrulanmış kenarlarla en kısa yolu bul
`inceleme_yolu(gruplar, hak_kenarlari, kaynak, hedef)` işlevi bir düğüm listesi döndürsün. `gruplar` sözlüğündeki üyelikler `hesap → grup` yönündedir. `hak_kenarlari` listesi yalnızca ad13'te **etkili olduğu doğrulanmış** `(özne, nesne, hak)` üçlülerini içerir; bu üçlüler de `özne → nesne` yönündedir. En kısa yönlü yolu BFS ile bul. Yol yoksa `[]`, kaynak ve hedef aynıysa `[kaynak]` döndür. Döngüleri sonlandır; girdi listelerini değiştirme. Böylece reddedilmiş bir ACE'yi yol sanmazsın.

```starter
import json
veri = json.load(open("acl.json", encoding="utf-8"))
hak_kenarlari = [("ali.kaya", "svc_sql", "WriteDacl")]

def inceleme_yolu(gruplar, hak_kenarlari, kaynak, hedef):
    return []

print(" -> ".join(inceleme_yolu(veri["gruplar"], hak_kenarlari, "ali.kaya", "Domain Admins")))
```

```test
import copy
g = veri["gruplar"]
h = [("ali.kaya", "svc_sql", "WriteDacl")]
eq(inceleme_yolu(g, h, "ali.kaya", "Domain Admins"), ["ali.kaya", "svc_sql", "Sunucu-Operatorleri", "Altyapi-Yoneticileri", "Domain Admins"], "kanıtlı hak ve üyelik zinciri")
eq(inceleme_yolu(g, h, "mehmet.yilmaz", "Domain Admins"), [], "deny nedeniyle Mehmet için hak kenarı yok")
eq(inceleme_yolu(g, h, "ayse.demir", "Domain Admins"), ["ayse.demir", "SOC-Liderleri", "Domain Admins"], "hak kenarı olmadan gerçek üyelik yolu")
eq(inceleme_yolu(g, h, "ali.kaya", "ali.kaya"), ["ali.kaya"], "aynı kaynak ve hedef")
eq(inceleme_yolu(g, h, "ali.kaya", "olmayan"), [], "ulaşılamayan hedef")
g2 = copy.deepcopy(g)
g2["Domain Admins"] = ["SOC-Analistleri"]
eq(inceleme_yolu(g2, h, "mehmet.yilmaz", "yok"), [], "döngüde sonsuz arama yok")
g2["ali.kaya"] = ["SOC-Analistleri", "KisaGrup"]
g2["KisaGrup"] = ["Domain Admins"]
eq(inceleme_yolu(g2, h, "ali.kaya", "Domain Admins"), ["ali.kaya", "KisaGrup", "Domain Admins"], "en kısa yol seçilmeli")
eq(inceleme_yolu(g, [], "ali.kaya", "Domain Admins"), [], "ACL kenarı kaldırılırsa yol da kalkar")
eq(h, [("ali.kaya", "svc_sql", "WriteDacl")], "girdi mutasyona uğramasın")
```

```solution
import json
from collections import deque
veri = json.load(open("acl.json", encoding="utf-8"))
hak_kenarlari = [("ali.kaya", "svc_sql", "WriteDacl")]

def inceleme_yolu(gruplar, hak_kenarlari, kaynak, hedef):
    komsular = {ad: list(ustler) for ad, ustler in gruplar.items()}
    for ozne, nesne, _hak in hak_kenarlari:
        komsular.setdefault(ozne, []).append(nesne)
    kuyruk = deque([[kaynak]])
    gorulen = {kaynak}
    while kuyruk:
        yol = kuyruk.popleft()
        son = yol[-1]
        if son == hedef:
            return yol
        for sonraki in komsular.get(son, []):
            if sonraki not in gorulen:
                gorulen.add(sonraki)
                kuyruk.append(yol + [sonraki])
    return []

print(" -> ".join(inceleme_yolu(veri["gruplar"], hak_kenarlari, "ali.kaya", "Domain Admins")))
```

```hint
Üyelikleri ve yalnız doğrulanmış hak kenarlarını aynı yönlü komşuluk listesinde birleştir; `deque` ile BFS yap. Düğümleri ilk kez kuyruğa eklerken işaretle.
```

```meta
motor: python
dil: python
```
:::

::: anlat SharpHound çıktısı: grafik ilişkisi, etkin erişim kararı değildir
Bir önceki görevdeki elle yazılmış kenarları şimdi **SpecterOps'un yayımladığı SharpHound örnek toplamasından** çıkaracağız. Paket PHANTOM/GHOST/WRAITH alanlarına ait yayımlanmış eğitim verisidir; bu laptopun veya senin kuruluşunun güncel taraması değildir. Kaynak ZIP ve seçilen altı users/groups dosyası SHA-256 manifestiyle paketlendi. Görev çalışırken indirme, DC bağlantısı veya BloodHound CE kurulumu yapılmaz.

`ObjectIdentifier` düğüm kimliğidir; `Properties.name` yalnız etikettir. Bir grubun `Members` listesi **üye → grup** kenarıdır. Kullanıcının `PrimaryGroupSID` alanı da üyelik verir. Hedef nesnenin `Aces` listesinde `PrincipalSID → ObjectIdentifier` yönünde hak ilişkisi bulunur; devralınmış hakları sırf `IsInherited=true` diye silme. Bu dosya, sıralı deny/allow güvenlik tanımlayıcısının tamamı değildir; AD13'teki DACL hesabının veya AD15'teki AccessCheck'in yerine geçmez.

Bu görev yalnız MemberOf, GenericAll, WriteDacl alt grafiğini okur. WriteOwner/Owns ve diğer kenarların üründeki ek koşulları farklıdır; desteklemediğini GenericAll'a dönüştürme. SID-only veya keşfedilmiş nesneler eklenebildiğinden kaynak `meta.count` ile liste uzunluğunu aynı şey sayma. Kayıtları `meta.version=6`, `meta.type=users/groups` çerçevesinde oku.

Kaynaklar: [resmi örnek veri](https://bloodhound.specterops.io/get-started/quickstart/ce-ingest-sample-data), [ürünün üyelik ve ACE dönüştürücüsü](https://github.com/SpecterOps/BloodHound/blob/main/packages/go/ein/ad.go). Çıkan yol **inceleme adayıdır**; oturum veya yetki yükseltme kanıtı değildir. CE UI/Cypher karşılaştırması ve gerçek DC doğrulaması canlı kabulde ayrıca yapılır.
:::

::: gorev SharpHound dışa aktarımında SID ve ACL kanıtıyla yolu oku
`bloodhound-documents.json`, resmi arşivdeki users/groups belgelerini **kayıtları değiştirmeden** içerir. `bh_kenarlari(belgeler)` sıralı, tekrarsız `(kaynakSID, hedefSID, tür, devralma)` tuple listesi döndürsün. MemberOf için devralma `None`, ACL için gerçek bool `IsInherited`. Silinen nesneleri (`IsDeleted is True`) ve onlara bağlanan ilişkileri çıkar; öz-ACL ilişkisini atla. Boş/yanlış kimlik ve string devralma `ValueError`; sürüm/tür dışında belge `ValueError`. Desteklenmeyen ACE hakları ilişkiye dönüşmez.

`bh_yolu(belgeler,kaynak,hedef)` bu kenarlarda BFS ile en kısa SID listesini bulsun; eşit uzunlukta komşular SID sırasıyla, yol yoksa `[]`, kaynak=hedef ise `[kaynak]`. Girdiyi değiştirme. Resmi örnekte DU001 hesabından PHANTOM Domain Admins grubuna ilişkinin `MemberOf` ve `WriteDacl` kayıtlarını göster. Adı yönetici diye bir düğüme özel kestirme yazma; testler kimlikleri ve hakları değiştirir.

```starter
import json
belgeler=json.load(open("bloodhound-documents.json",encoding="utf-8"))
def bh_kenarlari(belgeler):return []
def bh_yolu(belgeler,kaynak,hedef):return []
```

```test
import copy
need("bh_kenarlari");need("bh_yolu")
s="S-1-5-21-2697957641-2271029196-387917394-2202"
a="PHANTOM.CORP-S-1-5-32-544"
t="S-1-5-21-2697957641-2271029196-387917394-512"
eq(bh_yolu(belgeler,s,t),[s,a,t],"resmi örnekte DU001 → ADMINISTRATORS → DOMAIN ADMINS")
e=bh_kenarlari(belgeler)
ok((s,a,"MemberOf",None) in e,"grup Members üyeden gruba yönelir")
ok(any(x[:3]==(a,t,"WriteDacl") for x in e),"ACL öznesinden nesneye yönelir")
eq(bh_yolu(belgeler,t,s),[t,s],"ters yön ayrı sorgudur: örnek veride Domain Admins kullanıcıya doğrudan hak sahibidir")
def doc(kind,rows):return {"meta":{"type":kind,"version":6,"count":len(rows)},"data":rows}
def node(sid,**kw):return dict(ObjectIdentifier=sid,Properties={"name":"AYNI-AD"},**kw)
x=[doc("users",[node("u",PrimaryGroupSID="g",Aces=[]),node("b",Aces=[])]),doc("groups",[node("g",Members=[{"ObjectIdentifier":"u"}],Aces=[]),node("a",Members=[],Aces=[{"PrincipalSID":"g","RightName":"WriteDacl","IsInherited":True}])])]
old=copy.deepcopy(x)
eq(bh_kenarlari(x),[("g","a","WriteDacl",True),("u","g","MemberOf",None)],"tekrar eden üyelik tek, inherited ACL korunur; isimler kimlik değildir")
eq(bh_yolu(x,"u","a"),["u","g","a"],"üyelik + ACL")
y=copy.deepcopy(x);y[1]["data"][0]["Members"]=[]
eq(bh_yolu(y,"u","a"),["u","g","a"],"Members listesinde olmayan primary-group üyeliği")

y=copy.deepcopy(x);y[1]["data"][1]["Aces"][0]["RightName"]="GenericAll"
eq(bh_yolu(y,"u","a"),["u","g","a"],"GenericAll kenarı da okunur")
y=copy.deepcopy(x);y[1]["data"][1]["ObjectIdentifier"]=""
raises(ValueError,bh_kenarlari,y,msg="boş hedef SID reddedilir")
y=[doc("users",[node("u")]),doc("groups",[node("a",Members=[{"ObjectIdentifier":"u"}]),node("z",Members=[{"ObjectIdentifier":"u"}]),node("b",Members=[{"ObjectIdentifier":"z"}]),node("t",Members=[{"ObjectIdentifier":"a"},{"ObjectIdentifier":"b"}])])]
eq(bh_yolu(y,"u","t"),["u","a","t"],"DFS'nin daha uzun dalı yerine en kısa yol")

eq(bh_yolu(x,"b","a"),[],"aynı görünen ad ayrı SID'leri birleştirmez")
eq(x,old,"girdi değişmez")
x[1]["data"][1]["Aces"][0]["RightName"]="WriteOwner"
eq(bh_yolu(x,"u","a"),[],"desteklenmeyen hak sessizce WriteDacl olmaz")
x=copy.deepcopy(old);x[0]["data"][0]["IsDeleted"]=True
eq(bh_yolu(x,"u","a"),[],"silinen kaynak üyelikte görünse de çıkarılır")
x=copy.deepcopy(old);x[1]["data"][1]["IsDeleted"]=True
eq(bh_yolu(x,"u","a"),[],"silinen hedef çıkarılır")
x=copy.deepcopy(old);x[1]["data"][1]["Aces"][0]["IsInherited"]="false"
raises(ValueError,bh_kenarlari,x,msg="metin false gerçek bool değildir")
x=copy.deepcopy(old);x[0]["meta"]["version"]=5
raises(ValueError,bh_kenarlari,x,msg="bilinmeyen sürüm")
x=[doc("users",[node("u",PrimaryGroupSID="g")]),doc("groups",[node("g",Members=[]),node("a",Members=[{"ObjectIdentifier":"u"},{"ObjectIdentifier":"g"}])])]
eq(bh_yolu(x,"u","a"),["u","a"],"doğrudan kısa yol")
x[1]["data"][0]["Members"]=[{"ObjectIdentifier":"a"}]
eq(bh_yolu(x,"u","yok"),[],"döngü biter")
eq(bh_yolu(x,"u","u"),["u"],"özdeşik istek")
x=[doc("users",[node("u",Aces=[{"PrincipalSID":"u","RightName":"GenericAll","IsInherited":False}])])]
eq(bh_kenarlari(x),[],"ürün ithalatı gibi öz-ACL kenarı atlanır")
```

```solution
import json
from collections import deque
belgeler = json.load(open("bloodhound-documents.json",encoding="utf-8"))

def bh_kenarlari(belgeler):
    silinen = {n["ObjectIdentifier"] for d in belgeler for n in d["data"] if n.get("IsDeleted") is True}
    kenarlar = set()
    def ekle(kaynak, hedef, tur, devralma):
        if not isinstance(kaynak,str) or not kaynak or not isinstance(hedef,str) or not hedef:
            raise ValueError("Nesne kimliği boş olamaz")
        if kaynak not in silinen and hedef not in silinen:
            kenarlar.add((kaynak,hedef,tur,devralma))
    for belge in belgeler:
        meta=belge["meta"]
        if meta.get("version") != 6 or meta.get("type") not in ("users","groups"):
            raise ValueError("Yalnız users/groups sürüm 6 desteklenir")
        for nesne in belge["data"]:
            hedef=nesne["ObjectIdentifier"]
            if not isinstance(hedef,str) or not hedef: raise ValueError("Nesne kimliği boş olamaz")
            if nesne.get("IsDeleted") is True: continue
            if meta["type"]=="groups":
                for uye in nesne.get("Members",[]):
                    ekle(uye["ObjectIdentifier"],hedef,"MemberOf",None)
            elif nesne.get("PrimaryGroupSID"):
                ekle(hedef,nesne["PrimaryGroupSID"],"MemberOf",None)
            for ace in nesne.get("Aces",[]):
                if ace["RightName"] not in ("GenericAll","WriteDacl"): continue
                if type(ace["IsInherited"]) is not bool: raise ValueError("Devralma boolean olmalı")
                if ace["PrincipalSID"] != hedef:
                    ekle(ace["PrincipalSID"],hedef,ace["RightName"],ace["IsInherited"])
    return sorted(kenarlar,key=lambda e:(e[0],e[1],e[2],str(e[3])))

def bh_yolu(belgeler,kaynak,hedef):
    komsular={}
    for s,t,_,_ in bh_kenarlari(belgeler):
        komsular.setdefault(s,set()).add(t)
    kuyruk=deque([[kaynak]]);gorulen={kaynak}
    while kuyruk:
        yol=kuyruk.popleft();son=yol[-1]
        if son==hedef:return yol
        for dugum in sorted(komsular.get(son,())):
            if dugum not in gorulen:
                gorulen.add(dugum);kuyruk.append(yol+[dugum])
    return []
```

```setup
import sys,json,zipfile,hashlib
from pathlib import Path
root=Path(sys.modules["__main__"].__file__).resolve().parents[1]
folder=root/"tracks/ad/veri/bloodhound"
m=json.loads((folder/"manifest.json").read_text(encoding="utf-8"))
zpath=folder/"specterops-ad-sample.zip"
if hashlib.sha256(zpath.read_bytes()).hexdigest()!=m["archive_sha256"]:raise ValueError("BloodHound örnek ZIP hash uyuşmazlığı")
docs=[]
with zipfile.ZipFile(zpath) as z:
    for entry in m["entries"]:
        raw=z.read(entry["file"])
        if hashlib.sha256(raw).hexdigest()!=entry["sha256"]:raise ValueError("Kaynak kayıt hash uyuşmazlığı")
        docs.append(json.loads(raw))
Path("bloodhound-documents.json").write_text(json.dumps(docs,ensure_ascii=False),encoding="utf-8")
Path("bloodhound-provenance.json").write_text(json.dumps(m,ensure_ascii=False),encoding="utf-8")
```

```meta
motor: python
dil: python
```

```hint
Members listesindeki ObjectIdentifier kaynaktır; onu taşıyan grubun ObjectIdentifier değeri hedeftir. Aces listesinde ise PrincipalSID kaynaktır. Aynı üyelik primary group ve Members içinde iki kez görünürse set ile tekilleştir.
```
:::
