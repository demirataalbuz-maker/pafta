---
id: rx14
title: Koşullu Desenler ve Listeler
summary: (?(1)evet|hayır) ile bir grubun eşleşip eşleşmemesine göre dallanmak, ayraçlı liste kalıbı öğe(?:,öğe)*, tekrar sınırı, tekrarlanan grubun yalnızca son değeri tutması ve Python regex'inin iç içe yapılardaki sınırı.
---

::: anlat Bir gruba göre dallanmak
Bazen desenin bir parçası, **önceki bir grubun eşleşip eşleşmediğine** bağlıdır: açılan parantez kapanmalı, açılmayan kapanmamalı. Bunun için **koşullu desen** vardır:

| Yazım | Anlamı |
|---|---|
| `(?(1)evet\|hayır)` | 1. grup eşleştiyse `evet`, eşleşmediyse `hayır` kısmını uygula |
| `(?(1)evet)` | 1. grup eşleştiyse `evet`, eşleşmediyse hiçbir şey |
| `(?(ad)evet\|hayır)` | aynısı, adlı grupla |

Alan koduna parantez isteğe bağlı olsun, ama açıldıysa kapansın:

```regex
(\()?\d{3}(?(1)\)) \d{3} \d{2} \d{2}
---
(212) 555 01 02 ve 212 555 01 03 ve (212 555 01 04
```

İlk iki numara beklendiği gibi eşleşir. Üçüncüsünde parantez kapanmadığı için motor açılış parantezinde eşleşme bulamaz, **bir sonraki konumdan** dener ve `212 555 01 04` parçasını parantezsiz biçim olarak bulur. Koşullu desen tek başına "bütün" yapıyı garanti etmez. Tamamını doğrulamak için `tam()`, çapalar ya da `(?<!\()` gibi bir bakınma gerekir.

> [!NOT]
> Koşullu desen Python, PCRE ve .NET'te vardır; JavaScript ve RE2'de (KQL) yoktur. Onlarda aynı işi iki alternatifle yaparsın: `\(\d{3}\)|\d{3}`.

### Ayraçlı liste kalıbı
"Virgülle ayrılmış bir veya daha çok öğe" için evrensel kalıp **öğe, sonra (ayraç öğe) tekrarı**dır:

```regex
\d+(?:,\d+)*
---
portlar: 80,443,8080 ve 22
```

Bu kalıp sondaki ya da baştaki ayracı (`80,` veya `,80`) ve çift ayracı (`80,,443`) doğal olarak reddeder. Öğe sayısını sınırlamak için tekrarı sınırla: `öğe(?:,öğe){0,4}` en fazla beş öğe demektir.

### Tekrarlanan grup yalnızca sonuncuyu tutar
`(\d+)(?:,(\d+))*` deseni `80,443,8080` metnine uyar, ama 2. grup **yalnızca son** tekrarın değerini tutar: `8080`. `443` kaybolur. Bir listenin bütün öğelerine ihtiyacın varsa iki adımda çalış: önce listeyi doğrula, sonra öğeleri ayrı bir desenle (`\d+` ile `findall` ya da `split`) çıkar.

> [!DERİN]
> İç içe ve dengeli yapılar (iç içe parantezler, HTML etiketleri, JSON) gerçek anlamda "düzenli" değildir ve Python'un `re` modülü bunları genel olarak eşleyemez. PCRE ve .NET'in özyineleme ve dengeleme grupları bu sınırı aşar, ama okunması zor desenler ortaya çıkar. JSON için `json`, HTML için bir ayrıştırıcı kullan.
:::

::: tahmin
Hangi parçalar yakalanır? Ayrı satırlara yaz.

```regex
(<)?\w+(?(1)>)
```

```stdin
<kök> düz <eksik kapalı>
```

???

`<kök>`, `düz`, `eksik`, `kapalı`. `<eksik`'te grup `<`'yi alır, ama `eksik`'ten sonra `>` gelmez; motor geri izler, grubu boş bırakmayı dener, o da `<` konumunda tutmaz. Bir sonraki konumdan `eksik` parantezsiz biçimde eşleşir. `kapalı>`'da ise `<` olmadığı için koşul "hayır" kolundadır ve `>` istenmez: yalnızca `kapalı` alınır.
:::

::: gorev Köşeli parantezli port listesi
Bir metnin **tamamının** geçerli bir port listesi olup olmadığını denetle: virgülle ayrılmış sayılar; liste isteğe bağlı olarak köşeli parantez içinde olabilir, ama açılan parantez kapanmalı, açılmayan kapanmamalı.

```starter
\[?\d+(?:,\d+)*\]?
```

```test
ok(tam("80") and tam("80,443,8080"), "parantezsiz listeler")
ok(tam("[80,443]") and tam("[22]"), "parantezli listeler")
ok(not tam("[80,443"), "açılıp kapanmayan parantez")
ok(not tam("80,443]"), "açılmadan kapanan parantez")
ok(not tam("80,,443") and not tam("80,") and not tam("[]"), "boş öğe yok")
```

```solution
(\[)?\d+(?:,\d+)*(?(1)\])
```

```hint
Açılış parantezini bir gruba al: `(\[)?`. Sonda ise yalnızca o grup eşleştiyse kapanış iste.
```

```hint
Koşullu desen: `(?(1)\])`.
```
:::

::: gorev Sınırlı etiket listesi
Bir sunucunun etiket alanını doğrula: etiketler küçük harf, rakam ve tire içerir; virgülle, virgülden sonra isteğe bağlı boşlukla ayrılır; **en az bir, en fazla beş** etiket olur.

```starter
[a-z0-9-]+(?:,\s*[a-z0-9-]+)*
```

```test
ok(tam("web") and tam("web, db,cache") and tam("a,b,c,d,e"), "geçerli listeler")
ok(not tam("a,b,c,d,e,f"), "altı etiket fazla")
ok(not tam("web,") and not tam(",web"), "baştaki ya da sondaki virgül")
ok(not tam("Web"), "büyük harf yok")
```

```solution
[a-z0-9-]+(?:,\s*[a-z0-9-]+){0,4}
```

```hint
İlk öğe zorunlu, sonraki `(?:,öğe)` tekrarı ise en fazla dört kez: `*` yerine `{0,4}`.
```
:::

::: gorev Tek grupta tırnaklı ya da tırnaksız değer
`anahtar=değer` çiftlerini bul. Değer çift ya da tek tırnak içinde olabilir (o zaman aynı tırnakla kapanır ve içinde öteki tırnak geçebilir) ya da tırnaksız, boşluğa kadar bir dizidir. Testler her eşleşmeden `anahtar` ve `deger` adlı grupları okuyacak; `deger` **tırnaksız** içeriği tutmalı. Python'da aynı adı iki grupta kullanamazsın, bu yüzden üç alternatifi tek bir `deger` grubunda birleştirmen gerekiyor.

```starter
(?P<anahtar>\w+)=(?P<deger>"[^"]*"|\S+)
```

```test
satir = """ad="Ali Veli" not='o "dedi"' kod=42 bos="\""""
eq([(d["anahtar"], d["deger"]) for d in hepsi(satir)],
   [("ad", "Ali Veli"), ("not", 'o "dedi"'), ("kod", "42"), ("bos", "")], "dört çift, tırnaklar değerin dışında")
eq(hepsi('ad="Ali'), [], "kapanmayan tırnak eşleşmez")
```

```solution
(?P<anahtar>\w+)=(?P<q>["'])?(?P<deger>(?(q)(?:(?!(?P=q)).)*|[^\s"']+))(?(q)(?P=q))
```

```hint
Açılış tırnağını bir gruba al: `(?P<q>["'])?`. Değerin içeriği bu gruba bağlı: tırnak açıldıysa "o tırnak olmayan her şey", açılmadıysa `[^\s"']+`.
```

```hint
`(?P<deger>(?(q)(?:(?!(?P=q)).)*|[^\s"']+))` ve sonda yalnızca tırnak açıldıysa aynı tırnakla kapat: `(?(q)(?P=q))`.
```
:::
