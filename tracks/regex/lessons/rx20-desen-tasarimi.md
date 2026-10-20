---
id: rx20
title: Desen Tasarımı ve Test
summary: Olumlu ve olumsuz örneklerle başlamak, yanlış pozitif ile yanlış negatif dengesi, bağlam sınırları (sürüm numarası IP'nin parçası olmasın), (?x) ile belgelenmiş desen, parçalardan desen kurmak ve gereğinden geniş deseni daraltmak.
---

::: anlat Bir deseni nasıl tasarlarsın?
Usta ile acemi arasındaki fark, bilinen sözdiziminde değil **yöntemdedir**. Acemi bir örneğe bakıp desen yazar ve ilk eşleşmede durur. Usta önce örnek toplar:

1. **Olumlu örnekler**: yakalanması gereken her biçim (kısa, uzun, kenar durumları).
2. **Olumsuz örnekler**: benzeyen ama yakalanmaması gerekenler. Asıl zor olan bunlardır.
3. **Dar başla**: önce bir örneği birebir eşle, sonra adım adım genelle.
4. **Bağlamı sınırla**: desenin sol ve sağında ne olmamalı? `\b`, bakınma ya da çapa.
5. **Her değişiklikte bütün örnekleri yeniden dene.** Bir hatayı düzeltirken başka bir şeyi bozmak en yaygın hatadır.

### Yanlış pozitif mi, yanlış negatif mi?
| Hata | Anlamı | Ne zaman daha pahalı |
|---|---|---|
| Yanlış pozitif | yakalanmaması gerekeni yakaladın | gürültü: uyarı yorgunluğu, maskelemede gereksiz kayıp |
| Yanlış negatif | yakalanması gerekeni kaçırdın | kör nokta: maskelenmemiş kişisel veri, ayrıştırılmamış satır |

Hiçbir desen ikisini birden sıfırlayamaz. Hangisinin daha pahalı olduğuna göre dengeyi bilerek seç ve kararını desenin yanına yaz. Örneğin kişisel veri maskelemede yanlış negatif çok daha pahalıdır, bu yüzden desen biraz geniş tutulur.

### Bağlam sınırları
`\d+\.\d+\.\d+` bir sürüm numarası bulur, ama `10.0.0.1` adresinin içinden de `10.0.0`'ı koparır. Sürümü IP'den ayırmak için iki yanını sınırlarsın: solunda rakam ya da nokta olmasın, sağında "nokta ve rakam" gelmesin:

```regex
(?<![\d.])\d+\.\d+\.\d+(?!\.?\d)
---
sürüm 1.2.3, adres 10.0.0.1, eski 2.10.0-beta, yol 1.2.3.4.5
```
:::

::: anlat Belgelenmiş desen
`(?x)` (RX10) desendeki boşlukları yok sayar ve `#`'den satır sonuna kadar olan kısmı yorum sayar. Uzun bir desen böylece kendi belgesini taşır:

```regex
(?x)
(?<![\d.])     # solunda rakam ya da nokta yok
\d+ \. \d+ \. \d+
(?!\.?\d)      # sağında nokta+rakam ya da rakam yok
---
sürüm 1.2.3, adres 10.0.0.1
```

> [!TUZAK]
> `(?x)` kipinde desendeki **düz boşluk da yok sayılır**. Gerçek bir boşluk eşlemek için `[ ]`, `\ ` ya da `\s` yaz; `#` karakterini eşlemek için `\#` ya da `[#]`.

### Parçalardan desen kurmak
Büyük desenler kodda küçük, adlandırılmış ve ayrı ayrı test edilmiş parçalardan kurulur:

```python
OKTET = r"(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"
IPV4 = rf"{OKTET}(?:\.{OKTET}){{3}}"          # f-string'de { } ikilenir: {{3}}
SATIR = re.compile(rf"kaynak=(?P<kaynak>{IPV4}) hedef=(?P<hedef>{IPV4})")
```

Bir parçayı düzelttiğinde onu kullanan her desen birlikte düzelir. Splunk'ın `transforms.conf`'u, Logstash'in grok kalıpları (`%{IPV4:kaynak}`) ve KQL'de `let` ile tanımlanan desen değişkenleri aynı fikrin uygulamalarıdır.
:::

::: tahmin
Hangi parçalar yakalanır? Ayrı satırlara yaz.

```regex
(?x)ERROR [0-9]+
```

```stdin
ERROR 42 ERROR42
```

???

Yalnızca `ERROR42`. `(?x)` kipinde desendeki boşluk yok sayılır ve desen `ERROR[0-9]+` olur: `ERROR`'dan hemen sonra rakam ister. Boşluklu biçimi eşlemek için `ERROR[ ][0-9]+` yazılmalıydı.
:::

::: gorev Sürüm mü, adres mi?
Üç parçalı sürüm numaralarını (`1.2.3`) bul. IP adreslerinin ya da daha uzun noktalı dizilerin **parçası olanlar** alınmasın; cümle sonundaki nokta ve sürümden sonra gelen `-beta` gibi ekler sürümü engellemesin.

```starter
\d+\.\d+\.\d+
```

```test
eq(bul("sürüm 1.2.3, adres 10.0.0.1, eski 2.10.0-beta, yol 1.2.3.4.5"), ["1.2.3", "2.10.0"], "IP ve uzun dizi hariç")
eq(bul("Sürüm 3.4.5."), ["3.4.5"], "cümle sonundaki nokta")
eq(bul("v12.0.1 ve 4.5"), ["12.0.1"], "önünde harf olabilir, iki parçalı sayılmaz")
```

```solution
(?<![\d.])\d+\.\d+\.\d+(?!\.?\d)
```

```hint
Sol bağlam: önünde rakam ya da nokta olmasın, `(?<![\d.])`. Sağ bağlam: ardından bir rakam ya da "nokta ve rakam" gelmesin.
```

```hint
`(?!\.?\d)`: hem `10.0.0` + `.1`'i hem de `1.2.3` + `4`'ü engeller, ama cümle sonundaki tek noktaya izin verir.
```
:::

::: gorev Belgelenmiş telefon deseni
Türkiye cep telefonu numaralarını doğrulayan bir desen yaz. Desen `(?x)` ile başlasın ve **en az üç** parçası `#` yorumuyla açıklansın. Olumlu örneklerin hepsi kabul edilmeli, olumsuz örneklerin hiçbiri kabul edilmemeli.

- İsteğe bağlı başlangıç: `+90` (ardından isteğe bağlı boşluk) ya da `0`
- Operatör kodu `5` ile başlayan üç rakam
- Ardından 3 + 2 + 2 rakam; gruplar arasında isteğe bağlı **tek boşluk**

```starter
\+?\d[\d ]{9,15}
```

```test
olumlu = ["05321234567", "0532 123 45 67", "+90 532 123 45 67", "+905321234567", "532 123 45 67"]
olumsuz = ["0432 123 45 67", "+90 532 123 45 6", "0532-123-45-67", "905321234567", "(0532) 123 45 67", "0532 123 45 678"]
for s in olumlu:
    ok(tam(s), f"kabul edilmeli: {s}")
for s in olumsuz:
    ok(not tam(s), f"reddedilmeli: {s}")
ok(src.lstrip().startswith("(?x)"), "desen (?x) ile başlamalı")
ok(src.count("#") >= 3, "en az üç yorum")
```

```solution
(?x)
(?:\+90[ ]?|0)?   # ülke kodu ya da baştaki sıfır, isteğe bağlı
5\d{2}            # cep operatör kodu: 5xx
[ ]?\d{3}         # ilk üçlü
[ ]?\d{2}         # ikili
[ ]?\d{2}         # son ikili
```

```hint
`(?x)` kipinde boşluk yok sayılır: numaradaki boşluklar için `[ ]?` yaz. Her parçayı ayrı satıra koyup sonuna `# açıklama` ekle.
```

```hint
Başlangıç: `(?:\+90[ ]?|0)?`, sonra `5\d{2}`, sonra `[ ]?\d{3}`, `[ ]?\d{2}`, `[ ]?\d{2}`.
```
:::

::: gorev Gereğinden geniş deseni daralt
Metindeki e-posta adreslerini bul. Başlangıç deseni fazla geniş: yanındaki noktalama işaretini adrese katıyor, alan adı olmayan `a@b`'yi de alıyor. Yerel kısım harf, rakam, `.`, `+`, `-` ve `_` içerir; alan adı noktayla ayrılmış en az iki etiketten oluşur.

```starter
\S+@\S+
```

```test
metin = "Yaz: ad.soyad@ornek.com.tr veya destek@pafta.local; @ali'ye sor, a@b geçersiz, son: bilgi@ornek.org."
eq(bul(metin), ["ad.soyad@ornek.com.tr", "destek@pafta.local", "bilgi@ornek.org"], "üç adres, noktalama hariç")
eq(bul("rapor+ekim@ornek.com ve ayse_k@alt.ornek.com"), ["rapor+ekim@ornek.com", "ayse_k@alt.ornek.com"], "artı ve alt çizgi")
```

```solution
[\w.+-]+@[\w-]+(?:\.[\w-]+)+
```

```hint
`\S` her şeyi kabul ediyor. Yerel kısım için kesin bir sınıf yaz: `[\w.+-]+`.
```

```hint
Alan adı: bir etiket, sonra en az bir kez "nokta ve etiket": `[\w-]+(?:\.[\w-]+)+`. Etiket noktayla bitemediği için cümle sonundaki nokta dışarıda kalır.
```
:::
