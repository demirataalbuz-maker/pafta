---
id: jv15
title: Spring Security · Zincir Sırası ve Metot Yetkilendirmesi
summary: authorizeHttpRequests kuralları sırayla denenir ve ilk eşleşen kural karar verir; genel kalıbı öne koymak arkasındaki özel kuralı ölü koda çevirir. /onek/** kalıbı /onek'i de tutar, /oneksil'i tutmaz ve büyük/küçük harfe duyarlıdır. hasRole("X") yetkiyi ROLE_X diye arar, hasAuthority("X") harfi harfine X arar; aynı yetkiyle zıt karar verirler. @PreAuthorize bir vekil (proxy) üzerinden çalışır: dışarıdan gelen çağrı denetlenir, nesnenin kendi içinden yaptığı çağrı vekili atlar ve anotasyon hiç çalışmaz.
---

::: anlat Kurallar sırayla denenir
`JV09`'da Servlet filtre zincirini okudun. Spring Security'nin yetkilendirme kararı da bir **sıralı kural listesidir**: her istek için kurallar yukarıdan aşağı denenir, **ilk eşleşen** kural kararı verir ve zincir orada biter. Geri kalan kurallara hiç bakılmaz.

Bu dersin ölçümü gerçek `spring-security-core/web/config 7.0.2` ve Spring Framework 7.0.10 üzerinde, `RequestMatcherDelegatingAuthorizationManager` ile alındı (JDK 21).

```java
// Zincir A — özel kural önce
RequestMatcherDelegatingAuthorizationManager.builder()
    .add(pp.matcher("/yonetim/**"), AuthorityAuthorizationManager.hasAuthority("YONETICI"))
    .add(AnyRequestMatcher.INSTANCE, AuthenticatedAuthorizationManager.authenticated())
    .build();

// Zincir B — aynı iki kural, ters sırada
RequestMatcherDelegatingAuthorizationManager.builder()
    .add(AnyRequestMatcher.INSTANCE, AuthenticatedAuthorizationManager.authenticated())
    .add(pp.matcher("/yonetim/**"), AuthorityAuthorizationManager.hasAuthority("YONETICI"))
    .build();
```

İki zincirde de **aynı iki kural** var. Yine de `/yonetim/sil` isteğinde farklı davranırlar: B'de her isteği tutan genel kural başta olduğu için `/yonetim/**` kuralına **hiç sıra gelmez**. O satır dosyada durur, denetimde "yönetim yolu korunuyor" diye okunur, ama **ölü koddur**.

Kalıpların kendisi de okunmayı bekler. Ölçülen `/yonetim/**`:

| Yol | `/yonetim/**` tutar mı |
|---|---|
| `/yonetim/sil` | evet |
| `/yonetim/a/b/c` | evet (`**` birden çok parça yutar) |
| `/yonetim` | **evet** — önekin kendisi de kapsamda |
| `/yonetimsil` | hayır — ayırıcı olmadan önek sayılmaz |
| `/Yonetim/sil` | **hayır** — eşleştirme büyük/küçük harfe duyarlı |
:::

::: anlat ROLE_ öneki ve vekil sınırı
Kuralın gövdesinde iki benzer görünen yöntem var ve **aynı yetkiyle zıt karar verirler**:

- `hasAuthority("YONETICI")` kullanıcının yetkileri arasında harfi harfine `YONETICI` arar.
- `hasRole("YONETICI")` ise aradığı metnin başına `ROLE_` ekler; yani `ROLE_YONETICI` arar.

Bu yüzden yetkileri `ROLE_` öneksiz üretilen bir sistemde `hasRole` sessizce hiç kimseyi geçirmez; öneki koyan bir sistemde `hasAuthority` sessizce hiç kimseyi geçirmez. İkisi de "yetki yok" diye reddeder, ikisi de yapılandırma hatası gibi görünmez.

İkinci katman **metot yetkilendirmesidir**. `@EnableMethodSecurity` ile birlikte `@PreAuthorize` taşıyan bean'ler bir **vekil (proxy)** arkasına alınır; denetim vekilde yapılır, gerçek nesneye çağrı ancak denetim geçerse gider.

```java
class Servis {
    @PreAuthorize("hasAuthority('RAPOR_OKU')")
    public String rapor() { return "rapor"; }

    public String dolayli() { return rapor(); }   // anotasyon yok, içeriden çağırıyor

    @PreAuthorize("#sahip == authentication.name")
    public String belge(String sahip) { return "belge:" + sahip; }
}
```

`belge` satırı ilginç: ifade yetkiye değil **argümana** bakıyor. `#sahip` çağrının parametresi, `authentication.name` oturumdaki kullanıcı. Böylece "yalnız kendi belgesini okuyabilir" kuralı rol listesiyle değil, nesne düzeyinde kurulur.

> [!TUZAK] Nesnenin kendi içinden yaptığı çağrı denetlenmez
> Denetim vekilde yapıldığı için yalnız **dışarıdan gelen** çağrı denetlenir. `dolayli()` içindeki `rapor()` çağrısı `this` üzerinden gider, vekile hiç uğramaz ve `rapor`'un `@PreAuthorize`'ı **çalışmaz**. Aynı kullanıcı, aynı metot: doğrudan çağırınca reddedilir, anotasyonsuz bir komşu metot üzerinden çağırınca geçer. Kod okurken "bu metot korunuyor" demek yetmez; **hangi yoldan çağrıldığına** bakmak gerekir.
:::

::: tahmin Zincir ve vekil ne karar verir?
`ayse` kullanıcısının tek yetkisi `RAPOR_OKU`, `mdr`'nin tek yetkisi `YONETICI`. Zincir A ve B yukarıdaki iki yapılandırma; `anonim` hiç kimlik taşımıyor.

Metot bölümünde `Servis` bean'i `@EnableMethodSecurity` açık bir bağlamdan alındı.

```gercek
--- zincir A: /yonetim/** once, /** sonra ---
ayse[RAPOR_OKU] GET /yonetim/sil -> RED
mdr[YONETICI]   GET /yonetim/sil -> IZIN
ayse[RAPOR_OKU] GET /yonetim     -> RED
ayse[RAPOR_OKU] GET /yonetimsil  -> IZIN
ayse[RAPOR_OKU] GET /Yonetim/sil -> IZIN
ayse[RAPOR_OKU] GET /rapor       -> IZIN
anonim(null)    GET /rapor       -> RED
--- zincir B: /** once, /yonetim/** sonra ---
ayse[RAPOR_OKU] GET /yonetim/sil -> IZIN
--- hasRole / hasAuthority ---
yetki=YONETICI       hasRole(YONETICI)      -> RED
yetki=YONETICI       hasAuthority(YONETICI) -> IZIN
yetki=ROLE_YONETICI  hasRole(YONETICI)      -> IZIN
yetki=ROLE_YONETICI  hasAuthority(YONETICI) -> RED
--- metot yetkilendirme (bean proxy mi: true) ---
ayse[RAPOR_OKU] rapor()     -> OK rapor
ayse[RAPOR_OKU] belge(ayse) -> OK belge:ayse
ayse[RAPOR_OKU] belge(can)  -> RED AuthorizationDeniedException
mdr[YONETICI]   rapor()     -> RED AuthorizationDeniedException
mdr[YONETICI]   dolayli()   -> OK rapor
```

???

**Zincir A** beklendiği gibi: `ayse` yönetim yolunda reddedilir, `mdr` geçer. `/yonetim` de reddedilir — kalıbın öneki kendisini de kapsar. `/yonetimsil` ve `/Yonetim/sil` ise `/yonetim/**` kuralına takılmaz, genel kurala düşer ve kimliği olan herkese izin verilir. İkisi de zararsız görünür ama bir denetimde "yönetim yolu kapalı" cümlesini çürütür: ayırıcı ve harf durumu kalıbın parçasıdır.

`anonim` genel kuralda reddedilir, çünkü `authenticated()` kimlik ister. `RED` ile `KURAL YOK` aynı şey değildir: burada eşleşen bir kural var ve karar olumsuz.

**Zincir B** dersin asıl noktası: `ayse`, `YONETICI` yetkisi olmadan `/yonetim/sil`e **girer**. Kurallar değişmedi, yalnız sıraları değişti. `/yonetim/**` satırı hâlâ dosyada, ama ilk eşleşen kural kararı verdiği için o satıra hiç ulaşılmıyor.

**hasRole / hasAuthority** tablosu dört hücreyi de dolduruyor: çaprazda `IZIN`, düzde `RED`. `hasRole("YONETICI")` `ROLE_YONETICI` arar, `hasAuthority("YONETICI")` `YONETICI` arar. Yetkileri hangi önekle ürettiğini bilmeden hangisini yazdığına karar veremezsin.

**Metot tarafı.** `bean proxy mi: true` — aldığımız nesne `Servis` değil, onun vekili. `mdr` `YONETICI` yetkisiyle `rapor()`u çağırınca `AuthorizationDeniedException` alıyor: `hasAuthority('RAPOR_OKU')` bir yetki adı arar, "yönetici her şeyi yapar" diye bir örtük kural yoktur.

`belge(ayse)` geçerken `belge(can)` reddediliyor; `ayse`nin yetkisi değişmedi, **argüman** değişti. İfade argümana baktığı için karar her çağrıda yeniden veriliyor.

Son satır tuzağı gösteriyor: `mdr` `dolayli()` çağırıyor ve `rapor` değerini **alıyor**. Bir satır yukarıda aynı kullanıcı aynı metottan reddedilmişti. `dolayli()` anotasyonsuz olduğu için vekil onu serbest geçirir; içindeki `rapor()` çağrısı `this` üzerinden gittiği için denetim hiç çalışmaz. Korumanın yeri metot değil, **vekil sınırıdır**.
:::

::: gorev Zincir kararını modelle
`zincirKarari(kurallar, yol, yetkiler)` yaz: sıralı kural listesini ölçülen davranışa göre uygula.

- `kurallar`: sırayla `(kalip, gereken)` ikilileri.
  - `kalip` `"/**"` ise her yolu tutar. `"/onek/**"` biçimindeyse `"/onek"` yolunun kendisini ve `"/onek/"` ile başlayan her yolu tutar. Başka her kalıp **birebir** eşleşir.
  - `gereken` bir yetki adıdır; `"*"` ise "kimliği olan herkes" demektir.
- `yetkiler`: kullanıcının yetki listesi. `None` kimliksiz (anonim) demektir; boş liste kimliği olan ama yetkisi olmayan kullanıcıdır.
- **İlk eşleşen** kural karar verir: `"IZIN"` ya da `"RED"`. Hiçbir kural tutmazsa `"KURAL YOK"`.
- Eşleştirme büyük/küçük harfe duyarlıdır.

```starter
def zincirKarari(kurallar, yol, yetkiler):
    for kalip, gereken in kurallar:
        if kalip == yol:
            if yetkiler and gereken in yetkiler:
                return "IZIN"
            return "RED"
    return "KURAL YOK"
```

```test
need("zincirKarari")
A = [("/yonetim/**", "YONETICI"), ("/**", "*")]
B = [("/**", "*"), ("/yonetim/**", "YONETICI")]
eq(zincirKarari(A, "/yonetim/sil", ["RAPOR_OKU"]), "RED", "ölçülen: ayse yönetim yolunda reddedilir")
eq(zincirKarari(A, "/yonetim/sil", ["YONETICI"]), "IZIN", "ölçülen: mdr geçer")
eq(zincirKarari(A, "/yonetim", ["RAPOR_OKU"]), "RED", "ölçülen: /onek/** önekin kendisini de tutar")
eq(zincirKarari(A, "/yonetim/a/b/c", ["RAPOR_OKU"]), "RED", "** birden çok parça yutar")
eq(zincirKarari(A, "/yonetimsil", ["RAPOR_OKU"]), "IZIN", "ölçülen: ayırıcı olmadan önek sayılmaz")
eq(zincirKarari(A, "/Yonetim/sil", ["RAPOR_OKU"]), "IZIN", "ölçülen: eşleştirme harf durumuna duyarlı")
eq(zincirKarari(A, "/rapor", ["RAPOR_OKU"]), "IZIN", "genel kural: kimliği olan geçer")
eq(zincirKarari(A, "/rapor", []), "IZIN", "yetkisi yok ama kimliği var: authenticated() yeter")
eq(zincirKarari(A, "/rapor", None), "RED", "ölçülen: anonim genel kuralda reddedilir")
eq(zincirKarari(A, "/yonetim/sil", None), "RED", "anonim özel kuralda da reddedilir")
eq(zincirKarari(B, "/yonetim/sil", ["RAPOR_OKU"]), "IZIN",
   "ölçülen: genel kural önde, /yonetim/** ölü kod")
eq(zincirKarari(B, "/yonetim/sil", ["YONETICI"]), "IZIN", "B'de yönetici de genel kuraldan geçer")
eq(zincirKarari([("/yonetim/**", "YONETICI")], "/rapor", ["YONETICI"]), "KURAL YOK",
   "hiçbir kural tutmadı: RED ile aynı şey değil")
eq(zincirKarari([], "/x", ["YONETICI"]), "KURAL YOK", "kural listesi boş")
eq(zincirKarari([("/rapor", "*")], "/rapor/alt", ["X"]), "KURAL YOK", "birebir kalıp alt yolu tutmaz")
eq(zincirKarari([("/**", "YONETICI")], "/x", ["A", "YONETICI", "B"]), "IZIN", "yetki listenin ortasında")
```

```solution
def zincirKarari(kurallar, yol, yetkiler):
    for kalip, gereken in kurallar:
        if kalip.endswith("/**"):
            onek = kalip[:-3]
            tutar = onek == "" or yol == onek or yol.startswith(onek + "/")
        else:
            tutar = kalip == yol
        if not tutar:
            continue
        if yetkiler is None:
            return "RED"
        if gereken == "*":
            return "IZIN"
        return "IZIN" if gereken in yetkiler else "RED"
    return "KURAL YOK"
```

```hint
Başlangıç kodu yalnız birebir eşleşiyor, bu yüzden `/**` taşıyan kuralları hiç görmüyor. Kalıbı önce çöz: `"/**"` her şeyi tutar, `"/onek/**"` hem `"/onek"` yolunu hem `"/onek/"` ile başlayanları tutar.
```

```hint
Eşleşen kuralı bulduğun anda karar verilmiş olur: o kural ne derse o olur, sonraki kurallara bakılmaz. `continue` yalnız eşleşme olmadığında çalışmalı; eşleşme olduğunda her dalda bir `return` bulunmalı.
```

```hint
Üç durumu ayır: `yetkiler is None` (anonim) her kuralda reddedilir; `gereken == "*"` kimliği olana izin verir; geri kalanda yetki adı listede aranır. `yetkiler` boş liste olduğunda `if yetkiler` yanlış verir — bu yüzden `None` denetimini ayrıca yapmak gerekir.
```
:::

::: gorev Vekil sınırını modelle
`metotKarari(anotasyonlar, cagriYolu, yetkiler)` yaz: bir çağrı zincirinde `@PreAuthorize`ın gerçekten hangi halkada çalıştığını hesapla.

- `anotasyonlar`: metot adından gereken yetkiye eşleme. Değer `None` ise o metot anotasyonsuzdur; sözlükte hiç yoksa da anotasyonsuz sayılır.
- `cagriYolu`: çağrı zinciri, **en dıştan içe** doğru. Yalnız ilk halka vekilden geçer; geri kalanı nesnenin kendi içinden yapılan çağrılardır ve anotasyonları çalışmaz.
- `yetkiler`: kullanıcının yetki listesi.
- Dönüş `"IZIN"` ya da `"RED"`. `cagriYolu` boşsa `None`.

```starter
def metotKarari(anotasyonlar, cagriYolu, yetkiler):
    for ad in cagriYolu:
        gereken = anotasyonlar.get(ad)
        if gereken and gereken not in yetkiler:
            return "RED"
    return "IZIN"
```

```test
need("metotKarari")
AN = {"rapor": "RAPOR_OKU", "dolayli": None, "sil": "YONETICI"}
eq(metotKarari(AN, ["rapor"], ["RAPOR_OKU"]), "IZIN", "ölçülen: ayse raporu alır")
eq(metotKarari(AN, ["rapor"], ["YONETICI"]), "RED",
   "ölçülen: mdr reddedilir, yönetici her şeyi yapar diye örtük kural yok")
eq(metotKarari(AN, ["dolayli", "rapor"], ["YONETICI"]), "IZIN",
   "ölçülen: dolayli() anotasyonsuz, içindeki rapor() vekili atlar")
eq(metotKarari(AN, ["dolayli", "rapor"], []), "IZIN", "hiç yetkisi olmayan da aynı yoldan geçer")
eq(metotKarari(AN, ["dolayli"], ["YONETICI"]), "IZIN", "anotasyonsuz metot serbest")
eq(metotKarari(AN, ["sil"], ["YONETICI"]), "IZIN", "dıştaki halka yetkiliyse geçer")
eq(metotKarari(AN, ["sil", "rapor"], ["YONETICI"]), "IZIN",
   "yalnız sil denetlenir; raporun anotasyonu çalışmaz")
eq(metotKarari(AN, ["sil", "rapor"], ["RAPOR_OKU"]), "RED",
   "ilk halka reddetti: içeriye hiç girilmiyor")
eq(metotKarari(AN, ["rapor", "rapor"], ["RAPOR_OKU"]), "IZIN", "aynı metot iki kez: karar ilk halkada")
eq(metotKarari(AN, ["bilinmeyen"], []), "IZIN", "sözlükte olmayan metot anotasyonsuz sayılır")
eq(metotKarari({}, ["x"], []), "IZIN", "hiç anotasyon yok")
eq(metotKarari(AN, [], ["YONETICI"]), None, "çağrı zinciri boş")
```

```solution
def metotKarari(anotasyonlar, cagriYolu, yetkiler):
    if not cagriYolu:
        return None
    gereken = anotasyonlar.get(cagriYolu[0])
    if gereken is None:
        return "IZIN"
    return "IZIN" if gereken in yetkiler else "RED"
```

```hint
Başlangıç kodu zincirin **her** halkasını denetliyor; ölçüm bunun yanlış olduğunu gösterdi. Vekil yalnız dışarıdan gelen çağrıyı sarar, yani karar `cagriYolu[0]` halkasında verilir ve zincirin geri kalanı hiç denetlenmez.
```

```hint
Boş zincirde denetlenecek çağrı yoktur; `"IZIN"` değil `None` döndürülmeli. Döngüsüz yaz: tek bir metoda bakıp karar vermek yeterli.
```
:::
