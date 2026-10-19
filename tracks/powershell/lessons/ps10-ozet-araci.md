---
id: ps10
title: Proje · Olay Özeti Aracı
summary: CSV olay kaydını özetleyen, parametreli, doğrulamalı ve doğru çıkış kodlarıyla çalışan bir araç.
---

::: anlat Proje tanımı
Bir uygulama, kullanıcı işlemlerini bir CSV dosyasına kaydediyor:

```text
zaman,kullanici,olay,sonuc
2026-10-19T08:00:01,ali,giris,basarili
2026-10-19T08:00:09,root,giris,basarisiz
...
```

Ekip her sabah şu özeti istiyor:

```cikti
toplam: 8
başarısız: 4
en çok başarısız: root (3)
```

Bu projede, öğrendiğin her şeyi birleştiren bir **araç** yazacaksın: parametre (P02), dosya kontrolü ve kodlama (P08), nesneler ve gruplama (P07), hata yönetimi ve çıkış kodları (P09).

İyi bir aracın sözleşmesi:

| Durum | Davranış |
|---|---|
| Parametre verilmedi | stderr'e kullanım mesajı, çıkış kodu **2** |
| Dosya yok | stderr'e hata, çıkış kodu **1** |
| Başarılı | özet stdout'a, çıkış kodu **0** |

> [!NOT]
> Çıkış kodları aracını otomasyona uygun yapar: zamanlanmış bir görev ya da CI hattı, `$LASTEXITCODE`'a bakarak işin başarılı olup olmadığını anlar. Kullanım hatası (2) ile çalışma zamanı hatasını (1) ayırmak Unix geleneğidir ve PowerShell araçlarında da iyi bir uygulamadır.
:::

::: gorev 1 · Sağlam giriş kontrolleri
Önce sözleşmenin hata kısımlarını yaz. Betik `$Dosya` parametresi alsın:

- `$Dosya` boşsa: stderr'e `kullanım: ozet.ps1 -Dosya <csv>` yaz, **2** ile çık
- Dosya yoksa: stderr'e `hata: dosya yok: <ad>` yaz, **1** ile çık
- Varsa: `tamam` yazdır

```setup
open("olaylar.csv", "w", encoding="utf-8", newline="\n").write("zaman,kullanici,olay,sonuc\n")
```

```starter
param($Dosya)
"tamam"
```

```meta
argv: olaylar.csv
```

```test
eq(out, "tamam\n", "dosya varsa tamam")
r = calis()
eq(r["kod"], 2, "parametresiz → kod 2")
ok("kullanım" in r["hata"], "kullanım mesajı stderr'de", got=r["hata"])
r = calis(argv=["yok.csv"])
eq(r["kod"], 1, "dosya yok → kod 1")
ok("dosya yok" in r["hata"], "hata mesajı stderr'de", got=r["hata"])
```

```solution
param([string]$Dosya)
if (-not $Dosya) {
    [Console]::Error.WriteLine("kullanım: ozet.ps1 -Dosya <csv>")
    exit 2
}
if (-not (Test-Path -Path $Dosya -PathType Leaf)) {
    [Console]::Error.WriteLine("hata: dosya yok: $Dosya")
    exit 1
}
"tamam"
```

```hint
`if (-not $Dosya) { ...; exit 2 }` ve `if (-not (Test-Path $Dosya)) { ...; exit 1 }`.
```
:::

::: gorev 2 · Özet
Şimdi özeti üret. Kontroller aşağıda hazır; dosyayı `Import-Csv -Encoding UTF8` ile oku ve şu üç satırı yazdır. `en çok başarısız`, `sonuc` alanı `basarisiz` olan kayıtlarda en sık geçen kullanıcıdır.

```cikti
toplam: 8
başarısız: 4
en çok başarısız: root (3)
```

```setup
satirlar = ["zaman,kullanici,olay,sonuc",
            "2026-10-19T08:00:01,ali,giris,basarili",
            "2026-10-19T08:00:09,root,giris,basarisiz",
            "2026-10-19T08:00:15,root,giris,basarisiz",
            "2026-10-19T08:01:02,veli,dosya,basarili",
            "2026-10-19T08:02:40,root,giris,basarisiz",
            "2026-10-19T08:03:11,ayse,giris,basarili",
            "2026-10-19T08:04:00,veli,giris,basarisiz",
            "2026-10-19T08:05:30,ali,cikis,basarili"]
open("olaylar.csv", "w", encoding="utf-8", newline="\n").write("\n".join(satirlar) + "\n")
```

```starter
param([string]$Dosya)
if (-not $Dosya) { [Console]::Error.WriteLine("kullanım: ozet.ps1 -Dosya <csv>"); exit 2 }
if (-not (Test-Path -Path $Dosya -PathType Leaf)) { [Console]::Error.WriteLine("hata: dosya yok: $Dosya"); exit 1 }

$kayitlar = Import-Csv -Path $Dosya -Encoding UTF8
"toplam: $($kayitlar.Count)"
```

```meta
argv: olaylar.csv
```

```test
eq(out, "toplam: 8\nbaşarısız: 4\nen çok başarısız: root (3)\n", "özet")
```

```solution
param([string]$Dosya)
if (-not $Dosya) { [Console]::Error.WriteLine("kullanım: ozet.ps1 -Dosya <csv>"); exit 2 }
if (-not (Test-Path -Path $Dosya -PathType Leaf)) { [Console]::Error.WriteLine("hata: dosya yok: $Dosya"); exit 1 }

$kayitlar = @(Import-Csv -Path $Dosya -Encoding UTF8)
$basarisiz = @($kayitlar | Where-Object sonuc -eq "basarisiz")
$enCok = $basarisiz | Group-Object kullanici | Sort-Object Count -Descending | Select-Object -First 1

"toplam: $($kayitlar.Count)"
"başarısız: $($basarisiz.Count)"
"en çok başarısız: $($enCok.Name) ($($enCok.Count))"
```

```hint
Başarısızları süz: `Where-Object sonuc -eq "basarisiz"`. En sık kullanıcı: `Group-Object kullanici | Sort-Object Count -Descending | Select-Object -First 1`.
```

```hint
Sonuçları `@( ... )` ile sar: tek kayıt kalırsa `.Count` yine doğru çalışsın.
```
:::

::: gorev 3 · Boş kayıt dosyası
Aracın kenar durumlarına dayanıklı olması gerekir. Sadece başlık satırı olan (kaydı olmayan) bir dosyada araç çökmemeli ve şunu yazdırmalı:

```cikti
toplam: 0
başarısız: 0
en çok başarısız: -
```

Önceki görevdeki betiği bu duruma dayanıklı hale getir; dolu dosyada eski çıktıyı vermeye devam etmeli.

```setup
open("bos.csv", "w", encoding="utf-8", newline="\n").write("zaman,kullanici,olay,sonuc\n")
satirlar = ["zaman,kullanici,olay,sonuc", "2026-10-19T08:00:09,root,giris,basarisiz",
            "2026-10-19T08:00:15,ali,giris,basarili", "2026-10-19T08:00:20,root,giris,basarisiz"]
open("dolu.csv", "w", encoding="utf-8", newline="\n").write("\n".join(satirlar) + "\n")
```

```starter
param([string]$Dosya)
if (-not $Dosya) { [Console]::Error.WriteLine("kullanım: ozet.ps1 -Dosya <csv>"); exit 2 }
if (-not (Test-Path -Path $Dosya -PathType Leaf)) { [Console]::Error.WriteLine("hata: dosya yok: $Dosya"); exit 1 }

$kayitlar = Import-Csv -Path $Dosya -Encoding UTF8
$basarisiz = $kayitlar | Where-Object sonuc -eq "basarisiz"
$enCok = $basarisiz | Group-Object kullanici | Sort-Object Count -Descending | Select-Object -First 1

"toplam: $($kayitlar.Count)"
"başarısız: $($basarisiz.Count)"
"en çok başarısız: $($enCok.Name) ($($enCok.Count))"
```

```meta
argv: bos.csv
```

```test
eq(out, "toplam: 0\nbaşarısız: 0\nen çok başarısız: -\n", "boş dosya")
eq(run(argv=["dolu.csv"]), "toplam: 3\nbaşarısız: 2\nen çok başarısız: root (2)\n", "dolu dosya")
```

```solution
param([string]$Dosya)
if (-not $Dosya) { [Console]::Error.WriteLine("kullanım: ozet.ps1 -Dosya <csv>"); exit 2 }
if (-not (Test-Path -Path $Dosya -PathType Leaf)) { [Console]::Error.WriteLine("hata: dosya yok: $Dosya"); exit 1 }

$kayitlar = @(Import-Csv -Path $Dosya -Encoding UTF8)
$basarisiz = @($kayitlar | Where-Object sonuc -eq "basarisiz")
$enCok = $basarisiz | Group-Object kullanici | Sort-Object Count -Descending | Select-Object -First 1

"toplam: $($kayitlar.Count)"
"başarısız: $($basarisiz.Count)"
if ($enCok) {
    "en çok başarısız: $($enCok.Name) ($($enCok.Count))"
} else {
    "en çok başarısız: -"
}
```

```hint
Boş dosyada `Import-Csv` hiçbir şey döndürmez; `$null.Count` 0 verse de `$enCok` `$null` olur. Sonuçları `@( )` ile sar ve `$enCok`'u `if` ile kontrol et.
```
:::
