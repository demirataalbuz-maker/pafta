---
id: rx22
title: Proje · Kişisel Veri Maskeleme
summary: Günlükleri paylaşmadan önce e-posta, telefon ve kimlik numarasını maskelemek; bağlam için bir parçayı korumak, sayı dizilerinin içinden yanlış parça koparmamak, desen sırası ve maskelemenin sınırları.
---

::: anlat Proje: paylaşmadan önce maskele
Bir hatayı incelemek için günlükleri bir ekip arkadaşına, bir tedarikçiye ya da bir destek kaydına eklemen gerekiyor. Günlüklerde ise kişisel veri var: e-posta adresleri, telefon numaraları, kimlik numaraları. KVKK ve GDPR'nin temel ilkesi **veri en aza indirme**dir: işin gerektirmediği kişisel veri paylaşılmaz. Bu projede paylaşımdan önce çalışacak bir maskeleme adımı kuracaksın.

### Maskelemenin ilkeleri
1. **En iyisi hiç yazmamak.** Uygulama kişisel veriyi günlüğe hiç yazmıyorsa maskelemeye gerek kalmaz. Regex maskelemesi, kaynağı düzeltemediğin durumlar için bir güvenlik ağıdır.
2. **Bağlam için bir parça koru.** `a***@ornek.com`: hangi kurumdan bir kullanıcı olduğu görünür, kim olduğu görünmez. Telefonun son dört hanesi, aynı numaranın satırlar arasında izlenmesine yeter.
3. **Geri döndürülemez olmalı.** Maskelenmiş metinden asıl veri çıkarılamamalı. İlişkilendirme gerekiyorsa (aynı kullanıcının bütün satırları) değeri bir **anahtarlı özetle** (HMAC) değiştir; düz özet tahmin edilebilir değerlerde (telefon numarası gibi) tersine çevrilebilir.
4. **Yanlış negatif daha pahalıdır** (RX20). Kaçan tek bir adres sızıntıdır; fazladan maskelenen bir sipariş numarası yalnızca küçük bir rahatsızlıktır. Yine de sayıların içinden parça koparmak, günlüğü okunmaz hale getirir.
5. **Sıra önemlidir.** Önce en özgül desenleri uygula (IBAN), sonra genel olanları (kimlik numarası, telefon). Aksi halde genel bir desen, özgül bir verinin bir parçasını kendi biçiminde maskeleyip geri kalanını açıkta bırakabilir.

### Sayı dizilerinin içinden koparmamak
11 haneli bir kimlik numarası deseni, 15 haneli bir sipariş numarasının **içinde** de 11 hane bulur. Bu yüzden sayı desenleri iki yandan bakınmayla sınırlanır: `(?<!\d)` ve `(?!\d)`. `\b` burada yetmez, çünkü `TCKN10000000146` gibi harfe bitişik yazımda harf ile rakam arasında kelime sınırı yoktur.

```regex
\bTR\d{2}(?: ?\d{4}){5} ?\d{2}\b
---
IBAN: TR33 0006 1005 1978 6457 8413 26 hesabına, kısa TR12 3456 değil
```

Yukarıdaki IBAN deseni TR'den sonra 24 rakamı, dörtlü gruplar arasında isteğe bağlı boşluklarla bulur.

> [!TUZAK]
> Maskeleme bir **en iyi çaba** önlemidir. Desenin hiç görmediği bir biçim (`0 532 123 45 67`, `ayse [at] ornek.com`) olduğu gibi geçer. Maskelenmiş bir dosyayı paylaşmadan önce kişisel veri **arayan** geniş bir desenle son bir tarama yap ve sonucu gözle kontrol et.
:::

::: tahmin
Bu desen 11 haneli kimlik numaralarını bulmak için yazılmış. Neleri yakalar?

```regex
(?<!\d)\d{11}(?!\d)
```

```stdin
no 10000000146, sipariş 123456789012345, eski 01234567890
```

???

`10000000146` ve `01234567890`. Bakınmalar sayesinde 15 haneli sipariş numarasının içinden parça koparılmaz. Ama `01234567890` da yakalanır: kimlik numarası 0 ile başlamaz. İlk hane için `[1-9]` yazmak bu yanlış pozitifi giderir.
:::

::: gorev E-posta maskele
Testler `degistir(metin, r"\g<ilk>***@\g<alan>")` çağıracak. E-posta adreslerini yakalayan, yerel kısmın **ilk karakterini** `ilk`, alan adını `alan` adlı gruba alan bir desen yaz. Yerel kısmın geri kalanı maskelenecek.

```starter
\S+@\S+
```

```test
R = r"\g<ilk>***@\g<alan>"
gruplar_var = {"ilk", "alan"} <= set(rx.groupindex)
ok(gruplar_var, "ilk ve alan adlı grupları olmalı")
if not gruplar_var:
    stop()
eq(degistir("iletişim: ayse.k@ornek.com", R), "iletişim: a***@ornek.com", "tek adres")
eq(degistir("a@ornek.com.tr ve rapor+ekim@pafta.local.", R), "a***@ornek.com.tr ve r***@pafta.local.", "tek harfli yerel kısım, cümle sonu noktası")
eq(degistir("@ali yok", R), "@ali yok", "adres olmayan metin değişmez")
```

```solution
(?P<ilk>\w)[\w.+-]*@(?P<alan>[\w-]+(?:\.[\w-]+)+)
```

```hint
Yerel kısmı ikiye böl: ilk karakter `(?P<ilk>\w)`, geri kalanı `[\w.+-]*` (boş olabilir).
```

```hint
Alan adı RX20'deki gibi: `(?P<alan>[\w-]+(?:\.[\w-]+)+)`.
```
:::

::: gorev Telefonu maskele, son dört hane kalsın
Testler `degistir(metin, r"*** *** \g<son>")` çağıracak. Cep telefonu numaralarını (RX20'deki biçimler: isteğe bağlı `+90` ya da `0`, `5xx`, sonra 3 + 2 + 2 hane, gruplar arasında isteğe bağlı boşluk) yakala; son iki ikili, aralarındaki boşlukla birlikte `son` grubuna girsin. Daha uzun bir sayının içindeki rakamlar telefon sayılmasın.

```starter
5\d{2} ?\d{3} ?(?P<son>\d{2} ?\d{2})
```

```test
R = r"*** *** \g<son>"
eq(degistir("ara: 0532 123 45 67", R), "ara: *** *** 45 67", "boşluklu numara")
eq(degistir("05321234567 ve +90 532 123 45 68", R), "*** *** 4567 ve *** *** 45 68", "bitişik ve ülke kodlu")
eq(degistir("+905551112233", R), "*** *** 2233", "bitişik ülke kodlu")
eq(degistir("sipariş 1205321234567 değişmez", R), "sipariş 1205321234567 değişmez", "uzun sayının içi")
```

```solution
(?<![\d+])(?:\+90 ?|0)?5\d{2} ?\d{3} ?(?P<son>\d{2} ?\d{2})(?!\d)
```

```hint
Başlangıç kodu ülke kodunu ve baştaki sıfırı maskelemiyor, uzun sayıların içinden de parça koparıyor. Önek: `(?:\+90 ?|0)?`.
```

```hint
İki yandan sınırla: önünde rakam ya da `+` olmasın `(?<![\d+])`, ardından rakam gelmesin `(?!\d)`.
```
:::

::: gorev Kimlik numarasını maskele
Testler `degistir(metin, r"*********\g<son>")` çağıracak. 11 haneli, 0 ile başlamayan kimlik numaralarını yakala; son iki hane `son` grubuna girsin. Daha uzun sayıların parçaları ve 0 ile başlayan 11 haneli sayılar değişmesin.

```starter
\d{9}(?P<son>\d{2})
```

```test
R = r"*********\g<son>"
eq(degistir("TCKN 10000000146, sipariş 123456789012345", R), "TCKN *********46, sipariş 123456789012345", "uzun sayı değişmez")
eq(degistir("no: 01234567890 ve TCKN:10000000146.", R), "no: 01234567890 ve TCKN:*********46.", "0 ile başlayan değişmez")
eq(degistir("kayıt TCKN10000000146 açıldı", R), "kayıt TCKN*********46 açıldı", "harfe bitişik yazım")
```

```solution
(?<!\d)[1-9]\d{8}(?P<son>\d{2})(?!\d)
```

```hint
İlk hane `[1-9]`, sonra 8 hane, sonra yakalanan son 2 hane.
```

```hint
`\b` yerine rakam bakınması: `(?<!\d)` ve `(?!\d)`. Harfe bitişik yazımda da çalışır, uzun sayıların içinde ise tutmaz.
```
:::
