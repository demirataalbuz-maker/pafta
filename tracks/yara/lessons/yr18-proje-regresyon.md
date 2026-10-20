---
id: yr18
title: Proje · Kural Paketi ve Regresyon
summary: Ortak biçim kontrolü, iki public tespit ve değişikliklerden korunmuş olumlu/olumsuz veri kümesi.
---

::: anlat Tek kuraldan küçük bir tespit paketine
Son projede iki farklı rapor türünü aynı paketle ayıracağız. Ortak biçim: PFREP; ile başlayan, 12–256 baytlık veri. ALPHA türü KIND=A; ve SIGN=ALPHA; işaretlerini; BETA türü KIND=B; ve SIGN=BETA; işaretlerini birlikte ister. Ortak biçim private yardımcı kuralda dursun; public raporda sadece tür kuralları görünsün.

Bu tasarım bir örneğin birden fazla türe uyabilmesini de görünür kılar. Türler karşılıklı dışlayıcı olacaksa bunu biçim sözleşmesiyle ve ek şartla tarif etmek gerekir. İlk görevde iki türün işaretleri birlikteyse iki tespit de raporlanır; ikinci görev bu politikayı değiştirecek.

```yara
private rule Rapor_Bicim { strings: $a = "PFREP;" condition: $a at 0 and filesize >= 12 and filesize <= 256 } #! ortak biçim kapısı
rule Rapor_A { strings: $k = "KIND=A;" $s = "SIGN=ALPHA;" condition: Rapor_Bicim and $k and $s }              #! A ailesi sınıflandırıcısı
rule Rapor_B { strings: $k = "KIND=B;" $s = "SIGN=BETA;" condition: Rapor_Bicim and $k and $s }              #! B ailesi sınıflandırıcısı
```

> [!DERİN] Tespit mühendisliğinde sınıflandırma (Classification) vs. avcılık (Hunting)
> Geniş avcılık kurallarında bir örneğin birden fazla kuralla eşleşmesi normaldir; ancak otomatik ayrıştırma veya aile sınıflandırma paketlerinde iki ailenin işaretleri birbirini dışlamalıdır (`not ($other_k or $other_s)`).
:::

::: anlat Regresyon kümesi yaşayan bir sözleşmedir
Bir yanlış pozitifi düzeltirken eski olumlu örnekleri tekrar çalıştır. Yalnız yeni olumsuz örneği reddetmek yeterli değildir; düzeltme bütün tespitleri kapatmış olabilir. Küçük veri kümesinde “tamamı geçti” sonucu üretim kapsamasının kanıtı değildir. Veri kümesine yeni sürümleri, benzer zararsız dosyaları ve sınır durumlarını eklemek bakımın parçasıdır.

Pafta testleri yalnız burada verilen etkisiz verileri tarar. Gerçek kullanıma geçerken derleyici sürümü, dosya türü, boyut sınırı, tarama zamanı ve beklenen yanlış pozitifler kayıt altına alınmalıdır. Kuralın amacı ve sınırları, onu kullanan analistin kararına eşlik eder.

> [!GÜVENLİK] Üretim öncesi regresyon kontrol listesi
> Bir YARA kural paketini üretime (EDR, e-posta ağ geçidi veya SIEM/SOAR hattına) almadan önce:
> - Hedef aile örneklerinin tamamında eşleştiğini (**True Positive**),
> - Yakın temiz dosyalarda ve bozuk başlıklarda sustuğunu (**True Negative**),
> - Sınır değerlerinde (`filesize`, eşik sayısı, ofset) kırılmadığını otomatik testlerle doğrula.

Kaynak: [Resmî YARA belgeleri](https://yara.readthedocs.io/en/stable/writingrules.html).
:::

::: tahmin
Girdi kutusundaki veriyi bu kuralla tara. Hangi kural adı yazılır; neden?

```yara
private rule Rapor_Bicim { strings: $a = "PFREP;" condition: $a at 0 and filesize >= 12 and filesize <= 256 }
rule Rapor_A { strings: $k = "KIND=A;" $s = "SIGN=ALPHA;" condition: Rapor_Bicim and $k and $s }
rule Rapor_B { strings: $k = "KIND=B;" $s = "SIGN=BETA;" condition: Rapor_Bicim and $k and $s }
```

```stdin
PFREP;KIND=A;SIGN=ALPHA;
```

???

`Rapor_A` yazılır. Private biçim kuralı raporlanmaz; B türünün iki işareti yoktur.
:::

::: gorev İki türü sınıflandır
Anlatımdaki `Rapor_Bicim`, `Rapor_A`, `Rapor_B` paketini yaz. Biçim yardımcısı private olsun. ALPHA ve BETA türlerinin kendi iki işareti zorunlu olsun.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
private rule Rapor_Bicim { condition: false }
rule Rapor_A { condition: false }
rule Rapor_B { condition: false }
```

```stdin
PFREP;KIND=A;SIGN=ALPHA;
```

```test
eq(eslesenler("PFREP;KIND=A;SIGN=ALPHA;"), ["Rapor_A"], "A raporu")
eq(eslesenler("PFREP;KIND=B;SIGN=BETA;"), ["Rapor_B"], "B raporu")
eq(sorted(eslesenler("PFREP;KIND=A;SIGN=ALPHA;KIND=B;SIGN=BETA;")), ["Rapor_A", "Rapor_B"], "iki tür birlikte")
for data in ("xPFREP;KIND=A;SIGN=ALPHA;", "PFREP;KIND=A;SIGN=BETA;", "PFREP;KIND=B;SIGN=ALPHA;", "PFREP;KIND=A;", "PFREP;KIND=A;SIGN=ALPHA;" + "x" * 256):
    eq(eslesenler(data), [], "yakın olumsuz örnek")
# Tür işaretleri 12 bayta sığmaz; private biçim sözleşmesini ayrı gözlemle.
probe = derle(src + "\nrule Pafta_Bicim_Probe { condition: Rapor_Bicim }")
for boyut, beklenen in ((11, False), (12, True), (13, True), (255, True), (256, True), (257, False)):
    veri = b"PFREP;" + b"x" * (boyut - 6)
    eq([m.rule for m in probe.match(data=veri, timeout=2)], ["Pafta_Bicim_Probe"] if beklenen else [],
       f"private biçim: {boyut} bayt, 12–256 sınırları dahil")
for temel, kural in (("PFREP;KIND=A;SIGN=ALPHA;", "Rapor_A"), ("PFREP;KIND=B;SIGN=BETA;", "Rapor_B")):
    for boyut, beklenen in ((255, True), (256, True), (257, False)):
        veri = temel + "x" * (boyut - len(temel))
        eq(eslesenler(veri), [kural] if beklenen else [], f"{kural}: {boyut} bayt üst sınırı")
```

```solution
private rule Rapor_Bicim { strings: $a = "PFREP;" condition: $a at 0 and filesize >= 12 and filesize <= 256 }
rule Rapor_A { strings: $k = "KIND=A;" $s = "SIGN=ALPHA;" condition: Rapor_Bicim and $k and $s }
rule Rapor_B { strings: $k = "KIND=B;" $s = "SIGN=BETA;" condition: Rapor_Bicim and $k and $s }
```

```hint
Her public koşul ortak yardımcıya ve kendi iki işaretine bağlı olsun.
```
:::

::: gorev Belirsiz türleri reddet
Yeni politika: bir rapor hem KIND=A; hem KIND=B; içeriyorsa **hiçbir tür tespiti** üretme. Önceki geçerli A ve B örnekleri çalışmaya devam etsin. Private biçim kuralını koru.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
private rule Rapor_Bicim { condition: false }
rule Rapor_A { condition: false }
rule Rapor_B { condition: false }
```

```stdin
PFREP;KIND=A;SIGN=ALPHA;
```

```test
eq(eslesenler("PFREP;KIND=A;SIGN=ALPHA;"), ["Rapor_A"], "A regresyonu")
eq(eslesenler("PFREP;KIND=B;SIGN=BETA;"), ["Rapor_B"], "B regresyonu")
eq(eslesenler("PFREP;KIND=A;SIGN=ALPHA;KIND=B;SIGN=BETA;"), [], "belirsiz dosya")
eq(eslesenler("PFREP;KIND=A;SIGN=ALPHA;KIND=B;"), [], "diğer tür işareti tek başına dışlar")
eq(eslesenler("PFREP;KIND=B;SIGN=BETA;KIND=A;"), [], "simetrik dışlama")
eq(eslesenler("KIND=A;SIGN=ALPHA;"), [], "ortak biçim korunmuş")
probe = derle(src + "\nrule Pafta_Bicim_Probe { condition: Rapor_Bicim }")
for boyut, beklenen in ((11, False), (12, True), (13, True), (255, True), (256, True), (257, False)):
    veri = b"PFREP;" + b"x" * (boyut - 6)
    eq([m.rule for m in probe.match(data=veri, timeout=2)], ["Pafta_Bicim_Probe"] if beklenen else [],
       f"private biçim regresyonu: {boyut} bayt, 12–256 sınırları dahil")
for temel, kural in (("PFREP;KIND=A;SIGN=ALPHA;", "Rapor_A"), ("PFREP;KIND=B;SIGN=BETA;", "Rapor_B")):
    for boyut, beklenen in ((255, True), (256, True), (257, False)):
        veri = temel + "x" * (boyut - len(temel))
        eq(eslesenler(veri), [kural] if beklenen else [], f"{kural}: dışlamadan sonra {boyut} bayt üst sınırı")
```

```solution
private rule Rapor_Bicim { strings: $a = "PFREP;" condition: $a at 0 and filesize >= 12 and filesize <= 256 }
rule Rapor_A { strings: $k = "KIND=A;" $s = "SIGN=ALPHA;" $diger = "KIND=B;" condition: Rapor_Bicim and $k and $s and not $diger }
rule Rapor_B { strings: $k = "KIND=B;" $s = "SIGN=BETA;" $diger = "KIND=A;" condition: Rapor_Bicim and $k and $s and not $diger }
```

```hint
Her public kuralda diğer türün KIND işaretini tanımlayıp not ile dışla. Eski olumlu örnekleri koru.
```
:::
