---
id: jv11
title: Yansıma (Reflection), JSON ve XML Okuma
summary: Class.forName ve getDeclaredFields ile yansıma, Jackson JSON bağlama (@JsonIgnore, @JsonProperty, çok biçimli tür güvenliği) ve güvenli XML ayrıştırıcı bayrakları.
---

::: anlat Yansıma (`Reflection`) ve Dinamik Sınıf Yükleme
Java'da bir sınıfın adını çalışma zamanında metin olarak alıp belleğe yüklemek, alanlarını ve metotlarını incelemek mümkündür; buna **Yansıma (Reflection)** denir. Web çerçeveleri (`Spring`, `Jackson`, `Hibernate`) anotasyonları okumak ve nesneleri otomatik oluşturmak için perde arkasında bu API'yi kullanır:

```java
import java.lang.reflect.Field;

Class<?> cls = Class.forName("tr.pafta.web.BiletIstegi");  #! sınıfı tam adıyla yükle
for (Field alan : cls.getDeclaredFields()) {
    System.out.println(alan.getName() + ":" + alan.getType().getSimpleName());
}
```

> [!GÜVENLİK] Kullanıcı girdisini `Class.forName(...)` veya çok biçimli JSON/nesne okuyucuya vermek
> Eğer bir uygulama sınıf adını HTTP isteğinden veya JSON içindeki `"@class"` alanından alıp `Class.forName(kullaniciSinifi)` ile örnekliyorsa, sınıf yolundaki (*classpath*) istenmeyen sınıfların kurucuları veya setter metotları tetiklenebilir! Aynı şekilde Java'nın ikili `ObjectInputStream.readObject()` metodu ve Jackson'ın `enableDefaultTyping()` özelliği yalnızca sabit bir izin listesiyle (`ObjectInputFilter` / sabit hedef DTO sınıfı) kullanılmalıdır.
:::

::: anlat Jackson JSON anotasyonları ve Güvenli XML (`DocumentBuilderFactory`)
Jackson `ObjectMapper` bir JSON metnini Java sınıfına veya `record` nesnesine dönüştürürken şu anotasyonlara uyar:
- **`@JsonProperty("istek_no")`**: JSON'daki `"istek_no"` alanını Java'daki `istekNo` alanına eşler.
- **`@JsonIgnore`**: İlgili alanın ne JSON'dan okunmasına ne de JSON çıktısına yazılmasına izin verir (parola özeti, iç bayraklar vb.).
- **`FAIL_ON_UNKNOWN_PROPERTIES`**: Varsayılan olarak tanımsız bir JSON alanı gelirse hata verir; kapatılmışsa tanımsız alanları sessizce atlar.

XML okuyan Java kodlarında (`DocumentBuilderFactory`, `SAXParserFactory`, `XMLInputFactory`) ise dış varlıkların (**XXE — XML External Entity**) kapatılıp kapatılmadığı şu yapılandırma satırlarından okunur:

```java
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
// GÜVENLİ YAPILANDIRMA: DOCTYPE bildirimlerini tamamen kapatır
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
dbf.setExpandEntityReferences(false);
```

> [!DERİN] Java'da `DocumentBuilderFactory` varsayılan olarak dış varlıklara izin verebilir
> Python'un `defusedxml` uyarısına benzer şekilde, Java'nın standart `DocumentBuilderFactory` sınıfında `disallow-doctype-decl` özelliği `true` yapılmamışsa `<!DOCTYPE ... [ <!ENTITY ...> ]>` içeren XML girdileri yerel dosyaları veya iç ağ adreslerini okuyabilir. Kod denetiminde XML ayrıştırıcı gördüğün anda ilk bakacağın yer `.setFeature(...)` satırlarıdır.
:::

::: tahmin
Java 21 ile çalıştırıldığında bu yansıma (Reflection) örneği ne yazdırır?

```java
import java.lang.reflect.RecordComponent;

public class Ornek {
    record KullaniciCikti(String ad, String rol, boolean aktif) {}

    public static void main(String[] args) {
        RecordComponent[] parcalar = KullaniciCikti.class.getRecordComponents();
        System.out.println(parcalar.length);
        for (RecordComponent rc : parcalar) {
            System.out.println(rc.getName() + ":" + rc.getType().getSimpleName());
        }
    }
}
```

```gercek
3
ad:String
rol:String
aktif:boolean
```

???

`3`, `ad:String`, `rol:String`, `aktif:boolean`. `KullaniciCikti.class.getRecordComponents()` yansıma API'siyle `record` tanımındaki 3 bileşeni tanımlandıkları sırayla döndürür; her bileşenin adı (`getName()`) ve kısa tür adı (`getType().getSimpleName()`) yazdırılır.
:::

::: gorev Jackson DTO bağlayıcı (`@JsonProperty`, `@JsonIgnore` ve bilinmeyen alanlar)
Aşağıdaki Jackson DTO bağlama kurallarını Python'da `json_dto_bagla(gelen_sozluk, alan_kurallari, bilinmeyende_hata)` fonksiyonu olarak kur:
- `alan_kurallari` sözlüğü her Java alanı için `{"json_adi": str, "ignore": bool, "varsayilan": Any}` bilgisi içerir.
- `ignore == True` olan Java alanları dışarıdan **asla** doldurulmaz; sonuçta her zaman kendi `"varsayilan"` değerini alır.
- `ignore == False` olan bir Java alanı, `gelen_sozluk` içinde kendi `"json_adi"` anahtarı varsa o değeri, yoksa `"varsayilan"` değerini alır.
- `bilinmeyende_hata == True` (`FAIL_ON_UNKNOWN_PROPERTIES`) ise: `gelen_sozluk` içinde `ignore == False` olan hiçbir alanın `"json_adi"` ile eşleşmeyen fazladan bir anahtar varsa `None` döndür! (`ignore == True` olan bir alanın adı JSON'da gönderilmişse ve `bilinmeyende_hata == True` ise o da bilinmeyen/yasak alan sayılır ve `None` döndürür.)

```starter
def json_dto_bagla(gelen_sozluk, alan_kurallari, bilinmeyende_hata):
    return dict(gelen_sozluk)
```

```test
need("json_dto_bagla")
kurallar = {
    "kullaniciAdi": {"json_adi": "kullanici_adi", "ignore": False, "varsayilan": ""},
    "departman": {"json_adi": "departman", "ignore": False, "varsayilan": "genel"},
    "icYetki": {"json_adi": "ic_yetki", "ignore": True, "varsayilan": False},
}
eq(json_dto_bagla({"kullanici_adi": "ayse"}, kurallar, True),
   {"kullaniciAdi": "ayse", "departman": "genel", "icYetki": False},
   "normal eşleme ve varsayılan değerler")
eq(json_dto_bagla({"kullanici_adi": "ayse", "ic_yetki": True}, kurallar, False),
   {"kullaniciAdi": "ayse", "departman": "genel", "icYetki": False},
   "bilinmeyende_hata=False iken @JsonIgnore alanı (ic_yetki) yok sayılmalı, varsayılan False kalmalı")
eq(json_dto_bagla({"kullanici_adi": "ayse", "ic_yetki": True}, kurallar, True),
   None,
   "bilinmeyende_hata=True iken @JsonIgnore alanının gönderilmesi reddedilmeli -> None")
eq(json_dto_bagla({"kullanici_adi": "ayse", "fazla": 1}, kurallar, True),
   None,
   "bilinmeyende_hata=True iken tanımsız alan -> None")
eq(json_dto_bagla({"kullanici_adi": "ayse", "fazla": 1}, kurallar, False),
   {"kullaniciAdi": "ayse", "departman": "genel", "icYetki": False},
   "bilinmeyende_hata=False iken tanımsız alan sessizce atlanmalı")
```

```solution
def json_dto_bagla(gelen_sozluk, alan_kurallari, bilinmeyende_hata):
    izinli_json_adlari = {
        bilgi["json_adi"]
        for bilgi in alan_kurallari.values()
        if not bilgi.get("ignore", False)
    }
    if bilinmeyende_hata:
        for k in gelen_sozluk:
            if k not in izinli_json_adlari:
                return None
    sonuc = {}
    for java_alani, bilgi in alan_kurallari.items():
        if bilgi.get("ignore", False):
            sonuc[java_alani] = bilgi["varsayilan"]
        else:
            j_adi = bilgi["json_adi"]
            sonuc[java_alani] = gelen_sozluk.get(j_adi, bilgi["varsayilan"])
    return sonuc
```

```hint
Önce `not bilgi.get("ignore", False)` olan alanların `json_adi` kümesini çıkar. `bilinmeyende_hata` doğruysa ve `gelen_sozluk` içinde bu kümede olmayan bir anahtar varsa `None` döndür.
```
:::

::: gorev XML ayrıştırıcı güvenlik yapılandırması denetleyicisi
Bir Java kodundaki `DocumentBuilderFactory` özellik haritasını (`features: dict[str, bool]`) inceleyip XXE'ye karşı güvenli olup olmadığını döndüren `xml_fabrikasi_guvenli_mi(features)` fonksiyonunu yaz.
Fabrikanın güvenli (`True`) sayılması için şu iki yoldan **en az biri** sağlanmalıdır:
1. `"http://apache.org/xml/features/disallow-doctype-decl"` özelliği açıkça `True` (`bool` olarak `True`) ayarlanmıştır; **VEYA**
2. Hem `"http://xml.org/sax/features/external-general-entities"` açıkça `False` **hem de** `"http://xml.org/sax/features/external-parameter-entities"` açıkça `False` ayarlanmıştır (ve `"http://apache.org/xml/features/disallow-doctype-decl"` varsa bile `False` olmasının sakıncası yoktur).

```starter
def xml_fabrikasi_guvenli_mi(features):
    return bool(features)
```

```test
need("xml_fabrikasi_guvenli_mi")
DOCTYPE = "http://apache.org/xml/features/disallow-doctype-decl"
GEN = "http://xml.org/sax/features/external-general-entities"
PAR = "http://xml.org/sax/features/external-parameter-entities"

eq(xml_fabrikasi_guvenli_mi({}), False, "boş yapılandırma güvensizdir")
eq(xml_fabrikasi_guvenli_mi({DOCTYPE: True}), True, "disallow-doctype-decl=True güvenli")
eq(xml_fabrikasi_guvenli_mi({DOCTYPE: False}), False, "disallow-doctype-decl=False tek başına güvensiz")
eq(xml_fabrikasi_guvenli_mi({GEN: False, PAR: False}), True, "her iki dış varlık özelliği de False ise güvenli")
eq(xml_fabrikasi_guvenli_mi({GEN: False}), False, "parameter-entities unutulmuşsa güvensiz")
eq(xml_fabrikasi_guvenli_mi({PAR: False}), False, "general-entities unutulmuşsa güvensiz")
eq(xml_fabrikasi_guvenli_mi({GEN: False, PAR: True}), False, "parameter-entities True ise güvensiz")
```

```solution
DOCTYPE = "http://apache.org/xml/features/disallow-doctype-decl"
GEN = "http://xml.org/sax/features/external-general-entities"
PAR = "http://xml.org/sax/features/external-parameter-entities"

def xml_fabrikasi_guvenli_mi(features):
    if not isinstance(features, dict):
        return False
    if features.get(DOCTYPE) is True:
        return True
    if features.get(GEN) is False and features.get(PAR) is False:
        return True
    return False
```

```hint
Python'da `features.get(GEN) == False` yazarken anahtar yoksa `None` döneceğine dikkat et; `features.get(GEN) is False and features.get(PAR) is False` ile tam `False` kontrolü yap.
```
:::
