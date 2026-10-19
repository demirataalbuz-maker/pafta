---
id: p12
title: match-case · Yapısal Eşleme
summary: Python 3.10'un desen eşlemesi; değer, alternatif, yakalama, dizi ve sözlük desenleri.
---

::: anlat Uzun elif zincirinin zarif hali
`match`, bir değeri sırayla **desenlere** karşı dener ve ilk tutan `case` bloğunu çalıştırır:

```python
komut = "durum"
match komut:
    case "baslat":
        print("servis başlatılıyor")
    case "durdur" | "kapat":          #! | = alternatifler
        print("servis durduruluyor")
    case "durum":
        print("servis çalışıyor")
    case _:                           #! _ = her şey (joker), else gibi
        print("bilinmeyen komut")
```

Buraya kadar bir `elif` zincirinden farkı yok. `match`'in asıl gücü değerin **yapısını** eşleyebilmesidir.

### Dizi desenleri ve yakalama
```python
for satir in ["goster loglar", "sil 42", "kopyala a.txt b.txt", "cik"]:
    match satir.split():
        case ["goster", ne]:              #! 2 elemanlı liste; 2.'si ne'ye bağlanır
            print("gösteriliyor:", ne)
        case ["sil", kimlik]:
            print("silinecek:", kimlik)
        case ["kopyala", kaynak, hedef]:
            print(kaynak, "→", hedef)
        case ["cik"]:
            print("çıkış")
```

Desendeki çıplak bir isim (`ne`, `kaynak`) **yakalama** yapar: o konumdaki değer o isme atanır. Eleman sayısı da eşleşmenin parçasıdır: `["goster"]` tek başına `["goster", ne]` desenine uymaz.

> [!TUZAK]
> `case HATA_KODU:` gibi düz bir isim yazarsan Python onu karşılaştırma sanmaz, **yakalama** sanar: her şey eşleşir ve değer o isme atanır! Sabitlerle karşılaştırmak için noktalı isim (`case Durum.HATA:`) ya da düz değer (`case 500:`) kullan.
:::

::: tahmin
Çıktı ne?

```python
komut = "kopyala rapor.txt yedek/"
match komut.split():
    case ["kopyala", kaynak]:
        print("hedef eksik")
    case ["kopyala", kaynak, hedef]:
        print(f"{kaynak} -> {hedef}")
    case _:
        print("?")
```

???

`rapor.txt -> yedek/`. `split()` 3 elemanlı liste verir. İlk desen 2 eleman beklediği için tutmaz, ikincisi tutar ve elemanları yakalar.
:::

::: anlat Koruyucular, *geri kalan ve sözlük desenleri
**Koruyucu** (guard), desene `if` ile ek bir koşul ekler. `*isim` dizinin geri kalanını yakalar:

```python
for kod in (200, 404, 503):
    match kod:
        case 200 | 201:
            print("tamam")
        case k if 500 <= k < 600:         #! yakala + koşul
            print("sunucu hatası", k)
        case k:
            print("diğer", k)

match ["grep", "-i", "-n", "hata", "app.log"]:
    case ["grep", *secenekler, desen, dosya]:   #! ortadakiler bir listeye
        print(secenekler, desen, dosya)
```

**Sözlük desenleri**, JSON olayları için biçilmiş kaftandır. Sözlükleri P16'da derinlemesine göreceğiz; şimdilik `{"anahtar": değer}` yapısını gör:

```python
olay = {"tur": "giris", "basarili": False, "kullanici": "root", "ip": "10.0.0.7"}
match olay:
    case {"tur": "giris", "basarili": False, "kullanici": "root"}:
        print("KRİTİK: root için başarısız giriş")
    case {"tur": "giris", "basarili": False, "kullanici": k}:
        print("uyarı: başarısız giriş:", k)
    case {"tur": "giris"}:
        print("bilgi: giriş")
```

Sözlük deseni **alt küme** eşler: olayda fazladan anahtar (`ip`) olması sorun değil.

> [!GÜVENLİK]
> Tespit mühendisliğinin özü budur: olayın **yapısına** bakıp kural uygulamak. Sigma kuralları (P67'de mini bir motorunu yazacaksın) tam olarak "şu alanlar şu değerlerdeyse alarm" der. `match` bunun Python'a gömülü küçük bir versiyonudur.
:::

::: tahmin
Dört satır:

```python
for kod in (200, 404, 503, 302):
    match kod:
        case 200 | 201:
            print("tamam")
        case k if 500 <= k < 600:
            print("sunucu", k)
        case 404:
            print("yok")
        case _:
            print("diğer")
```

???

`tamam`, `yok`, `sunucu 503`, `diğer`. 404 için ikinci desen yakalar ama koruyucu (500–599) tutmaz, sonraki desene geçilir. 302 hiçbirine uymaz ve joker yakalar.
:::

::: gorev Komut kabuğu
Girdiden tek satırlık bir komut oku ve `match` ile yorumla:

| Komut | Çıktı |
|---|---|
| `yardim` | `komutlar: yardim, topla A B, cik` |
| `topla A B` | A ile B'nin toplamı (tam sayı) |
| `cik` | `görüşürüz` |
| başka her şey | `bilinmeyen komut` |

```starter
satir = input()

```

```stdin
topla 2 40
```

```test
eq(run("yardim").strip(), "komutlar: yardim, topla A B, cik", "yardim")
eq(run("topla 2 40").strip(), "42", "topla 2 40 → 42")
eq(run("topla -5 5").strip(), "0", "topla -5 5 → 0")
eq(run("cik").strip(), "görüşürüz", "cik")
eq(run("topla 1").strip(), "bilinmeyen komut", "eksik argüman → bilinmeyen komut")
eq(run("sil her_sey").strip(), "bilinmeyen komut", "bilinmeyen")
ok(uses("match"), "match-case kullan")
```

```solution
satir = input()
match satir.split():
    case ["yardim"]:
        print("komutlar: yardim, topla A B, cik")
    case ["topla", a, b]:
        print(int(a) + int(b))
    case ["cik"]:
        print("görüşürüz")
    case _:
        print("bilinmeyen komut")
```

```hint
`match satir.split():` ve `case ["topla", a, b]:` — yakalanan a ve b metindir, `int()` ile çevir.
```
:::

::: gorev Olay sınıflandırıcı
Girdiden bir log olayı oku (boşlukla ayrılmış alanlar) ve sınıflandır:

| Olay | Çıktı |
|---|---|
| `login KULLANICI fail` | `UYARI: KULLANICI için başarısız giriş` |
| `login root ok` | `DİKKAT: root oturum açtı` |
| `login KULLANICI ok` (root değil) | `bilgi: KULLANICI girdi` |
| `sudo KULLANICI` | `DİKKAT: KULLANICI yetki yükseltti` |
| başka her şey | `yok say` |

```starter
olay = input()

```

```stdin
login ali fail
```

```test
eq(run("login ali fail").strip(), "UYARI: ali için başarısız giriş", "login ali fail")
eq(run("login root ok").strip(), "DİKKAT: root oturum açtı", "login root ok")
eq(run("login veli ok").strip(), "bilgi: veli girdi", "login veli ok")
eq(run("sudo ayse").strip(), "DİKKAT: ayse yetki yükseltti", "sudo ayse")
eq(run("logout ali").strip(), "yok say", "logout → yok say")
eq(run("login root fail").strip(), "UYARI: root için başarısız giriş", "login root fail → UYARI")
ok(uses("match"), "match-case kullan")
```

```solution
olay = input()
match olay.split():
    case ["login", k, "fail"]:
        print(f"UYARI: {k} için başarısız giriş")
    case ["login", "root", "ok"]:
        print("DİKKAT: root oturum açtı")
    case ["login", k, "ok"]:
        print(f"bilgi: {k} girdi")
    case ["sudo", k]:
        print(f"DİKKAT: {k} yetki yükseltti")
    case _:
        print("yok say")
```

```hint
Desenlerin **sırası** önemli: `["login", "root", "ok"]` deseni genel `["login", k, "ok"]` deseninden önce gelmeli.
```
:::
