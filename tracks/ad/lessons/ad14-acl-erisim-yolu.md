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
