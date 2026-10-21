---
id: ad09
title: AD Güvenlik Günlükleri ve Olay Kimlikleri
summary: Windows Güvenlik günlüğü (Security.evtx), Logon Type'lar (2 yerel, 3 ağ, 10 RDP), Olay 4624/4625, 4720 (hesap açıldı), 4728/4732/4756 (gruba eklendi), 4768/4769/4771 (Kerberos biletleri ve ön doğrulama), 4740 (kilitlenme) ve SIEM bildirimini dizin sorgusuyla doğrulamak.
---

::: anlat Olay günlükleri dizinin canlı sesidir
Dizinde yapılan her oturum açma, parola denemesi ve grup değişikliği Windows Olay Günlüğü'nün **Security** (Güvenlik) günlüğüne bir olay (Event ID) olarak düşer. Savunma tarafında SIEM (Sentinel, Splunk, Elastic) bu günlükleri toplar; bir analist günlüğü okurken dizinle eşleştirir: "4625'i gördüm, bu kullanıcı dizinde kimdir, hangi OU'da duruyor, hesabı kilitlendi mi?"

En kritik olay kimlikleri:

### 1. Oturum Açma ve Kimlik Doğrulama
| Olay Kimliği | Anlamı | Savunma Notu |
|---|---|---|
| **4624** | Başarılı oturum açma | Logon Type'a bakılır (Type 2 yerel konsol, Type 3 ağ/SMB/LDAP, Type 10 RDP) |
| **4625** | Başarısız oturum açma | Hata kodu (0xC000006A yanlış parola, 0xC0000064 kullanıcı yok, 0xC000006E hesap kısıtı, 0xC000006F oturum saati kısıtı, 0xC0000234 kilitli) |
| **4740** | Bir hesap kilitlendi | `badPwdCount` eşiğe ulaştığında üretilir; kaynak makine adını taşır |

### 2. Hesap ve Grup Yönetimi
| Olay Kimliği | Anlamı | Savunma Notu |
|---|---|---|
| **4720** | Yeni kullanıcı hesabı oluşturuldu | Kim açtı, hangi OU'da, onaylı talep var mı? |
| **4722** / **4725** | Hesap etkinleştirildi / devre dışı bırakıldı | İşten ayrılan ya da izindeki hesapların takibi |
| **4726** | Kullanıcı hesabı silindi | Silinme yerine devre dışı bırakma yaygındır |
| **4728** / **4729** | Global güvenlik grubuna üye eklendi / çıkarıldı | Domain Admins gibi gruplarda kritik alarmdır |
| **4732** / **4733** | Domain Local güvenlik grubuna üye eklendi / çıkarıldı | Yerel yöneticiler grubu takibi |
| **4756** / **4757** | Universal güvenlik grubuna üye eklendi / çıkarıldı | Orman çapında yetki değişiklikleri |

### 3. Kerberos Olayları (Etki Alanı Denetleyicisi)
| Olay Kimliği | Anlamı | Savunma Notu |
|---|---|---|
| **4768** | Kerberos TGT (bilet verme bileti) istendi | AS-REQ başarılı; Ticket Encryption Type (0x12 AES256, 0x17 RC4) |
| **4769** | Kerberos hizmet bileti (TGS) istendi | SPN'li bir hizmete erişim talebi (MSSQLSvc, HTTP vb.) |
| **4771** | Kerberos ön kimlik doğrulama başarısız | Pre-authentication failed (genelde yanlış parola denemesi) |
| **4776** | NTLM kimlik doğrulaması denendi | Eski NTLM protokolünün kullanımını tespit etmek için |

> [!GÜVENLİK]
> **Logon Type 10 vs 3:** Bir servis hesabının sunucuya ağ üzerinden bağlanması (Logon Type 3) normal olabilir; ancak aynı servis hesabıyla RDP oturumu açılması (Logon Type 10) ya da konsoldan oturum denenmesi (Logon Type 2) acil araştırma gerektiren bir yetki aşımı göstergesidir.
:::

::: anlat Günlükten dizine: Şüpheliyi dizinde aramak
SIEM'den bir alarm geldiğinde analist dizinde o hesabı sorgular. Örneğin Olay 4771 veya 4625 fırtınası gördüğünde:

```ad
Get-ADUser -Identity mehmet.yilmaz -Properties badPwdCount, Enabled, lastLogonTimestamp
```

Ya da bir gruba üye ekleme alarmı (Olay 4728) geldiğinde, grubun şu anki durumuna ve üyelerine bakar:

```ad
Get-ADGroup -Identity "Domain Admins" -Properties member
```

> [!İPUCU]
> Tezgahtaki dizin verisi sabittir (`DC=pafta,DC=local`); ancak gerçek ortamda günlükler sürekli akar. Bir hesaba saldırı olduğunda `badPwdCount` artar; hesap kilitlendiğinde Olay 4740 üretilir. Analist SIEM'deki olay ile AD'deki `badPwdCount` ve `Enabled` durumunu karşılaştırarak karantinaya karar verir.
:::

::: tahmin
SOC analisti çok sayıda parola hatası şüphesiyle etkin hesapları inceliyor. Bu sorgu hangi satırları yazar?

```ad
Get-ADUser -Filter 'badPwdCount -ge 2 -and Enabled -eq $true' -Properties badPwdCount, Title
```

???

Üç satır yazar: `ayse.demir|2|SOC Takim Lideri`, `zeynep.arslan|3|Sistem Yoneticisi`, `can.ozkan|4|Ag Uzmani`. Filtre iki koşul içerir: `badPwdCount >= 2` VE `Enabled -eq $true`. Mehmet Yılmaz'ın sayacı 5, svc_yedek'in sayacı 6'dır ama ikisi de devre dışıdır (Enabled=$false). Ali Kaya ve Administrator'ın sayacı 0'dır, Elif Koç'unki 1'dir. Geriye sayaçları 2, 3 ve 4 olan etkin üç çalışan kalır.
:::

::: gorev Olay 4740 ve 4625 eşiği
SIEM'de kilitlenme (4740) ve çok sayıda parola hatası (4625) alarmı üretmiş olan, yani `badPwdCount` değeri **5 ya da daha yüksek** olan kullanıcı hesaplarını `badPwdCount` ve `Enabled` özellikleriyle birlikte (`sAMAccountName|badPwdCount|Enabled`) listele. Get-ADUser ve `-Filter` kullan.

```cikti
mehmet.yilmaz|5|False
svc_yedek|6|False
```

```starter
Get-ADUser -Filter 'badPwdCount -gt 5' -Properties badPwdCount, Enabled
```

```test
eq(satirlar, ["mehmet.yilmaz|5|False", "svc_yedek|6|False"], "sayacı 5 ve 6 olan iki hesap")
ok(kullanir("Get-ADUser") and kullanir("-Filter"), "Get-ADUser ve -Filter kullan")
eq(dene(ek=[yeni_kullanici("sinir.dort", badPwdCount=4)], satir_olarak=True), ["mehmet.yilmaz|5|False", "svc_yedek|6|False"], "badPwdCount=4 gelmemeli")
eq(dene(ek=[yeni_kullanici("sinir.bes", badPwdCount=5, userAccountControl=512)], satir_olarak=True), ["mehmet.yilmaz|5|False", "svc_yedek|6|False", "sinir.bes|5|True"], "badPwdCount=5 etkin hesap da gelmeli (sınır dahil)")
```

```solution
Get-ADUser -Filter 'badPwdCount -ge 5' -Properties badPwdCount, Enabled
```

```hint
`-gt 5` kesin büyüktür (6 ve üstü); "5 ya da daha yüksek" için `-ge 5` kullan.
```
:::

::: gorev Olay 4728 alarmı: Lider ve yönetici grupları
Güvenlik operasyon merkezi, kritik gruplara üye ekleme olaylarını (4728/4732) izliyor. Adında (`Name`) **Lider** ya da **Yonetici** geçen grupları ve doğrudan üyelerini (`sAMAccountName|member`) Get-ADGroup ve `-Filter` ile listele.

```cikti
Altyapi-Yoneticileri|CN=Zeynep Arslan,OU=BT,OU=Merkez,DC=pafta,DC=local;CN=Sunucu-Operatorleri,OU=Gruplar,DC=pafta,DC=local
SOC-Liderleri|CN=Ayse Demir,OU=SOC,OU=Merkez,DC=pafta,DC=local
```

```starter
Get-ADGroup -Filter 'Name -like "*Lider*"' -Properties member
```

```test
eq(satirlar, ["Altyapi-Yoneticileri|CN=Zeynep Arslan,OU=BT,OU=Merkez,DC=pafta,DC=local;CN=Sunucu-Operatorleri,OU=Gruplar,DC=pafta,DC=local", "SOC-Liderleri|CN=Ayse Demir,OU=SOC,OU=Merkez,DC=pafta,DC=local"], "iki grup ve üyeleri")
ok(kullanir("Get-ADGroup") and kullanir("-Filter"), "Get-ADGroup ve -Filter kullan")
def yeni_grup(ad):
    return {"distinguishedName": f"CN={ad},OU=Gruplar,DC=pafta,DC=local", "sAMAccountName": ad, "cn": ad, "name": ad, "objectCategory": "group", "objectClass": ["top", "group"], "groupType": -2147483646, "member": []}
eq(dene(ek=[yeni_grup("Ag-Yoneticileri")], satir_olarak=True), ["Altyapi-Yoneticileri|CN=Zeynep Arslan,OU=BT,OU=Merkez,DC=pafta,DC=local;CN=Sunucu-Operatorleri,OU=Gruplar,DC=pafta,DC=local", "SOC-Liderleri|CN=Ayse Demir,OU=SOC,OU=Merkez,DC=pafta,DC=local", "Ag-Yoneticileri|"], "Ag-Yoneticileri de gelmeli")
eq(dene(ek=[yeni_grup("Analistler")], satir_olarak=True), satirlar, "Analistler gelmemeli")
```

```solution
Get-ADGroup -Filter 'Name -like "*Lider*" -or Name -like "*Yonetici*"' -Properties member
```

```hint
İki `-like` koşulunu `-or` ile birleştir: `'Name -like "*Lider*" -or Name -like "*Yonetici*"'`.
```
:::

::: gorev Olay 4768 ve 4771 incelemesi: Ön kimlik doğrulaması kapalı hesap
Kerberos Olay 4768 günlüğünde ön kimlik doğrulama gerektirmeden bilet alan hesapları tespit etmek istiyorsun. Dizinde `DoesNotRequirePreAuth` özelliği `$true` olan kullanıcıları bu özellik değeriyle birlikte (`sAMAccountName|DoesNotRequirePreAuth`) listele. Get-ADUser ve `-Filter` kullan.

```cikti
svc_rapor|True
```

```starter
Get-ADUser -Filter * -Properties DoesNotRequirePreAuth
```

```test
eq(satirlar, ["svc_rapor|True"], "ön kimlik doğrulaması kapatılmış tek hesap")
ok(kullanir("DoesNotRequirePreAuth"), "DoesNotRequirePreAuth özelliğini filtrele")
eq(dene(ek=[yeni_kullanici("preauth.yok", userAccountControl=4194816)], satir_olarak=True), ["svc_rapor|True", "preauth.yok|True"], "yeni preauth kapalı hesap gelmeli")
eq(dene(ek=[yeni_kullanici("normal.hesap", userAccountControl=512)], satir_olarak=True), ["svc_rapor|True"], "normal hesap gelmemeli")
```

```solution
Get-ADUser -Filter 'DoesNotRequirePreAuth -eq $true' -Properties DoesNotRequirePreAuth
```

```hint
`DoesNotRequirePreAuth -eq $true` filtresini kullan ve `-Properties DoesNotRequirePreAuth` ile alanı çıktıya ekle.
```
:::
