---
id: ad06
title: Get-ADComputer, -SearchBase ve -SearchScope
summary: Bilgisayar hesapları ($ son eki, operatingSystem, dNSHostName, 4096/8192 bitleri, Domain Controllers OU'su), -SearchBase ile aramayı bir alt ağaca sınırlamak, Base/OneLevel/Subtree kapsamları ve Get-ADOrganizationalUnit, Get-ADObject.
---

::: anlat Bilgisayar hesapları
Etki alanına katılan her makinenin dizinde bir **bilgisayar hesabı** vardır. Bu hesap kendi parolasıyla (makine otomatik olarak yaklaşık 30 günde bir değiştirir) etki alanına kimliğini kanıtlar.

| Özellik | Örnek | Not |
|---|---|---|
| `sAMAccountName` | `SRV-SQL01$` | her zaman `$` ile biter |
| `dNSHostName` | `srv-sql01.pafta.local` | tam alan adı |
| `operatingSystem` | `Windows Server 2022` | makine kendisi yazar |
| `userAccountControl` | `4096` | WORKSTATION_TRUST_ACCOUNT: üye sunucu ya da istasyon |
| `userAccountControl` | `532480` | 8192 (SERVER_TRUST_ACCOUNT) + 524288: etki alanı denetleyicisi |

Etki alanı denetleyicileri (DC) varsayılan olarak `OU=Domain Controllers` altında durur; tezgahta DC01 oradadır.

```ad
Get-ADComputer -Filter * -Properties dNSHostName, OperatingSystem

Get-ADComputer -Filter 'Enabled -eq $false'
```

> [!GÜVENLİK]
> Destek süresi bitmiş işletim sistemleri (ör. Windows Server 2012 R2) artık güvenlik güncellemesi almaz. `operatingSystem` üzerinde `-like` sorgusu, envanterde unutulmuş makineleri bulmanın en hızlı yoludur. Devre dışı ama silinmemiş bilgisayar hesapları da düzenli temizlenmelidir.
:::

::: anlat Nerede arıyorsun: -SearchBase ve -SearchScope
Varsayılan olarak arama etki alanının **kökünden** başlar ve bütün ağacı tarar. `-SearchBase` aramayı bir DN'in altına sınırlar, `-SearchScope` ne kadar derine inileceğini söyler:

| Kapsam | Ne döner |
|---|---|
| `Base` | yalnızca SearchBase nesnesinin kendisi |
| `OneLevel` | SearchBase'in **doğrudan** çocukları (kendisi hariç) |
| `Subtree` | SearchBase'in kendisi ve altındaki her şey (varsayılan) |

`OU=Merkez`'in doğrudan altında tek bir kullanıcı vardır; ötekiler alt OU'lardadır:

```ad
Get-ADUser -Filter * -SearchBase "OU=Merkez,DC=pafta,DC=local" -SearchScope OneLevel

Get-ADUser -Filter * -SearchBase "OU=Merkez,DC=pafta,DC=local"
```

`Get-ADOrganizationalUnit` OU'ları, `Get-ADObject` ise sınıf ayırmadan her nesneyi getirir. `Base` kapsamı tek bir nesneye bakmak için kullanılır:

```ad
Get-ADOrganizationalUnit -Filter * -SearchBase "OU=Merkez,DC=pafta,DC=local"

Get-ADObject -Filter * -SearchBase "OU=Finans,OU=Merkez,DC=pafta,DC=local" -SearchScope Base
```

> [!TUZAK]
> `-SearchBase` olarak verdiğin DN dizinde yoksa gerçek AD hata verir; tezgah da aynı davranır. `CN=Users`'ın bir OU olmadığını unutma: `OU=Users,DC=pafta,DC=local` diye bir nesne yoktur.

> [!İPUCU]
> Büyük bir dizinde kapsamı daraltmak hem sorguyu hızlandırır hem de yanlışlıkla başka birimlerin nesnelerini toplamanı önler. Bir OU'ya yönetim devredilmişse, o OU'nun yöneticisinin sorguları zaten bu kapsamla yazılır.
:::

::: tahmin
İki komut art arda çalışıyor. Çıktı ne?

```ad
Get-ADUser -Filter * -SearchBase "OU=Merkez,DC=pafta,DC=local" -SearchScope OneLevel

Get-ADObject -Filter * -SearchBase "OU=Finans,OU=Merkez,DC=pafta,DC=local" -SearchScope OneLevel
```

???

Önce `selin.aydinkaya`, sonra `elif.koc`, `burak.sahin`, `Tedarikci Destek`. OneLevel yalnızca doğrudan çocuklara bakar: OU=Merkez'in doğrudan altındaki tek kullanıcı Selin'dir; SOC, BT ve Finans OU'larındaki kullanıcılar bir alt düzeydedir. İkinci komut Get-ADObject olduğu için sınıf ayırmaz: Finans OU'sunun iki kullanıcısıyla birlikte kişi nesnesi de gelir. OneLevel SearchBase'in kendisini (Finans OU'sunu) içermez.
:::

::: gorev Desteği bitmiş sistemler
İşletim sistemi **Windows Server 2012** ailesinden olan ya da **Windows 10** ile başlayan bilgisayarları, işletim sistemi adıyla birlikte (`sAMAccountName|OperatingSystem`) listele.

```cikti
SRV-ESKI01$|Windows Server 2012 R2
PC-FIN01$|Windows 10 Enterprise
```

```starter
Get-ADComputer -Filter 'OperatingSystem -like "*2012*"' -Properties OperatingSystem
```

```test
eq(satirlar, ["SRV-ESKI01$|Windows Server 2012 R2", "PC-FIN01$|Windows 10 Enterprise"], "iki eski sistem")
eq(dene(ek=[yeni_bilgisayar("SRV-ESKI02", ou="OU=Sunucular", operatingSystem="Windows Server 2012")], satir_olarak=True), ["SRV-ESKI01$|Windows Server 2012 R2", "PC-FIN01$|Windows 10 Enterprise", "SRV-ESKI02$|Windows Server 2012"], "Windows Server 2012 (R2'siz) de gelmeli")
eq(len(dene(ek=[yeni_bilgisayar("PC-YENI", operatingSystem="Windows 11 Pro")], satir_olarak=True)), 2, "Windows 11 gelmemeli")
eq(len(dene(ek=[yeni_bilgisayar("SRV-2016", ou="OU=Sunucular", operatingSystem="Windows Server 2016")], satir_olarak=True)), 2, "Windows Server 2016 gelmemeli")
eq(len(dene(ek=[yeni_bilgisayar("PC-KALIP", operatingSystem="Eski Windows 10 Kalibi")], satir_olarak=True)), 2, "Windows 10 ile başlamayan işletim sistemi gelmemeli")
```

```solution
Get-ADComputer -Filter 'OperatingSystem -like "*2012*" -or OperatingSystem -like "Windows 10*"' -Properties OperatingSystem
```

```hint
İki `-like` koşulunu `-or` ile bağla; ikincisi `"Windows 10*"`.
```
:::

::: gorev Sunucular OU'sundaki etkin makineler
Yalnızca **OU=Sunucular** altındaki **etkin** bilgisayar hesaplarını getir.

```starter
Get-ADComputer -Filter 'Enabled -eq $true'
```

```test
eq(sonuc, ["SRV-SQL01$", "SRV-WEB01$"], "Sunucular OU'sunda etkin iki makine")
eq(dene(ek=[yeni_bilgisayar("SRV-YENI01", ou="OU=Sunucular")]), ["SRV-SQL01$", "SRV-WEB01$", "SRV-YENI01$"], "Sunucular'a eklenen etkin makine gelmeli")
eq(dene(ek=[yeni_bilgisayar("SRV-PASIF02", ou="OU=Sunucular", userAccountControl=4098)]), ["SRV-SQL01$", "SRV-WEB01$"], "devre dışı makine gelmemeli")
eq(dene(ek=[yeni_bilgisayar("PC-SOC02", ou="OU=Istasyonlar")]), ["SRV-SQL01$", "SRV-WEB01$"], "Istasyonlar'daki makine gelmemeli")
```

```solution
Get-ADComputer -Filter 'Enabled -eq $true' -SearchBase "OU=Sunucular,DC=pafta,DC=local"
```

```hint
`-SearchBase "OU=Sunucular,DC=pafta,DC=local"` ekle. DC01 zaten `OU=Domain Controllers` altındadır.
```
:::

::: gorev Merkez'in doğrudan alt birimleri
**OU=Merkez**'in **doğrudan** altındaki OU'ları getir; Merkez'in kendisi ve daha derindeki OU'lar gelmesin.

```starter
Get-ADOrganizationalUnit -Filter * -SearchBase "OU=Merkez,DC=pafta,DC=local"
```

```test
eq(sonuc, ["SOC", "BT", "Finans"], "üç doğrudan alt OU")
derin = {"distinguishedName": "OU=Vardiya,OU=SOC,OU=Merkez,DC=pafta,DC=local", "name": "Vardiya", "ou": "Vardiya", "objectCategory": "organizationalUnit", "objectClass": ["top", "organizationalUnit"]}
eq(dene(ek=[derin]), ["SOC", "BT", "Finans"], "SOC'un altındaki OU gelmemeli")
yeni = {"distinguishedName": "OU=Hukuk,OU=Merkez,DC=pafta,DC=local", "name": "Hukuk", "ou": "Hukuk", "objectCategory": "organizationalUnit", "objectClass": ["top", "organizationalUnit"]}
eq(dene(ek=[yeni]), ["SOC", "BT", "Finans", "Hukuk"], "Merkez'e eklenen yeni OU gelmeli")
```

```solution
Get-ADOrganizationalUnit -Filter * -SearchBase "OU=Merkez,DC=pafta,DC=local" -SearchScope OneLevel
```

```hint
Varsayılan kapsam Subtree'dir ve SearchBase'in kendisini de içerir. Doğrudan çocuklar için `-SearchScope OneLevel`.
```
:::
