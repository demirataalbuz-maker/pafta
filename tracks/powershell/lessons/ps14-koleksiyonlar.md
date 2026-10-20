---
id: ps14
title: Koleksiyonlar ve Performans
summary: Dizilerin sabit boyutu ve += maliyeti, List, Dictionary ve HashSet, hashtable anahtarlarının büyük-küçük harfe duyarsızlığı, [ordered], Group-Object -AsHashTable, Compare-Object ve Measure-Command.
---

::: anlat Doğru koleksiyonu seçmek
PowerShell dizileri **sabit boyutludur**. `$dizi += $x` her seferinde yeni bir dizi oluşturup bütün elemanları kopyalar: on bin elemanda fark edilmez, yüz bin elemanda betik dakikalarca sürer. Büyüyen listeler için .NET koleksiyonları kullanılır:

| Tür | Ne için |
|---|---|
| `[System.Collections.Generic.List[string]]` | eleman eklenen liste (`.Add`, `.Remove`, `.Count`) |
| `[System.Collections.Generic.Dictionary[string,int]]` | türü belli, **büyük-küçük harfe duyarlı** sözlük |
| `@{}` (hashtable) | hızlı sözlük, anahtarlar **duyarsız** |
| `[ordered]@{}` | ekleme sırasını koruyan sözlük |
| `[System.Collections.Generic.HashSet[string]]` | tekrarsız küme; `.Add` yeni elemanda `$true` döner |
| `Queue`, `Stack` | ilk giren ilk çıkar / son giren ilk çıkar |

```powershell
$sure1 = Measure-Command { $a = @(); foreach ($i in 1..5000) { $a += $i } }
$sure2 = Measure-Command { $l = [System.Collections.Generic.List[int]]::new(); foreach ($i in 1..5000) { $l.Add($i) } }
"dizi +=: {0:N0} ms, List: {1:N0} ms" -f $sure1.TotalMilliseconds, $sure2.TotalMilliseconds
```

> [!TUZAK]
> PowerShell hashtable'larında anahtarlar büyük-küçük harfe **duyarsızdır**: `@{ Web = 1 }["WEB"]` 1 döner ve `Web` ile `web` aynı anahtar sayılır. Çoğu zaman işine yarar; ama kayıtlardaki kullanıcı adları ya da dosya adları gibi farkın önemli olduğu sayımlarda sessizce birleştirme yapar. Duyarlı bir sözlük için `Dictionary[string,int]` kullan.

### Gruplamak ve karşılaştırmak
```powershell
$sunucular = @"
Ad,Rol
web01,web
db01,db
web02,web
"@ | ConvertFrom-Csv
$rol = $sunucular | Group-Object Rol -AsHashTable -AsString     #! rol → o roldeki nesneler
$rol["web"].Ad -join ","

Compare-Object @("a", "b", "c") @("b", "c", "d") | ForEach-Object { "$($_.SideIndicator) $($_.InputObject)" }
```

`Compare-Object`'te `<=` yalnızca soldakinde, `=>` yalnızca sağdakinde olan demektir; `-IncludeEqual` ortakları da (`==`) gösterir.
:::

::: tahmin
Üç satır yazar:

```powershell
$h = @{ Web = 1 }
$h["WEB"]
$d = [System.Collections.Generic.Dictionary[string,int]]::new()
$d["Web"] = 1
$d.ContainsKey("WEB")
$o = [ordered]@{ z = 1; a = 2 }
$o.Keys -join ","
```

???

`1`, `False`, `z,a`. Hashtable anahtarları harfe duyarsız olduğu için "WEB" ile "Web"i bulur. Generic `Dictionary` varsayılan olarak duyarlıdır. `[ordered]` anahtarları ekleme sırasıyla tutar.
:::

::: gorev Duyarlı sayım
Girdideki kelimeleri **büyük-küçük harfe duyarlı** say ve her kelimeyi ilk görüldüğü sırayla `kelime: sayı` olarak yazdır.

```starter
$say = @{}
foreach ($satir in $Girdi) {
    foreach ($k in $satir -split '\s+') { if ($k) { $say[$k]++ } }
}
foreach ($k in $say.Keys) { "${k}: $($say[$k])" }
```

```stdin
web Web web
db WEB
```

```test
eq(run("web Web web\ndb WEB\n"), "web: 2\nWeb: 1\ndb: 1\nWEB: 1\n", "harfe duyarlı, ilk görülme sırasıyla")
ok("Dictionary" in src, "Dictionary kullan")
```

```solution
$say = [System.Collections.Generic.Dictionary[string,int]]::new()
foreach ($satir in $Girdi) {
    foreach ($k in $satir -split '\s+') {
        if ($k) {
            if ($say.ContainsKey($k)) { $say[$k]++ } else { $say[$k] = 1 }
        }
    }
}
foreach ($k in $say.Keys) { "${k}: $($say[$k])" }
```

```hint
Hashtable "web", "Web" ve "WEB"i tek anahtar sayar. `[System.Collections.Generic.Dictionary[string,int]]::new()` duyarlıdır ve ekleme sırasını korur.
```
:::

::: gorev Kurulu paket farkı
`onceki.txt` ve `sonraki.txt` bir makinedeki kurulu paketlerin iki farklı günde alınmış listeleri. Yeni kurulanları `+ ad`, kaldırılanları `- ad` olarak, paket adına göre sıralı yazdır.

```setup
open("onceki.txt", "w", encoding="utf-8", newline="\n").write("git\nnodejs\npython\n7zip\n")
open("sonraki.txt", "w", encoding="utf-8", newline="\n").write("git\npython\nvscode\n7zip\nterraform\n")
```

```starter
Get-Content sonraki.txt
```

```test
eq(out, "- nodejs\n+ terraform\n+ vscode\n", "bir kaldırılan, iki eklenen")
ok("Compare-Object" in src, "Compare-Object kullan")
```

```solution
Compare-Object (Get-Content onceki.txt) (Get-Content sonraki.txt) |
    Sort-Object InputObject |
    ForEach-Object {
        $isaret = if ($_.SideIndicator -eq "=>") { "+" } else { "-" }
        "$isaret $($_.InputObject)"
    }
```

```hint
`Compare-Object eski yeni`: `=>` yalnızca yenide (eklenen), `<=` yalnızca eskide (kaldırılan).
```
:::

::: gorev Rol sorguları
`sunucular.csv` (`Ad,Rol`) dosyasından rol → sunucular tablosu kur (`Group-Object -AsHashTable`). Girdinin her satırı bir rol adı; her biri için o roldeki sunucuları virgülle (alfabetik) yazdır, rol yoksa `yok` yaz.

```setup
open("sunucular.csv", "w", encoding="utf-8", newline="\n").write("Ad,Rol\nweb02,web\ndb01,db\nweb01,web\ncache01,onbellek\n")
```

```starter
$liste = Import-Csv sunucular.csv
foreach ($rol in $Girdi) {
    ($liste | Where-Object Rol -eq $rol).Ad -join ","
}
```

```stdin
web
dizin
db
```

```test
eq(run("web\ndizin\ndb\n"), "web01,web02\nyok\ndb01\n", "web, olmayan rol, db")
ok("AsHashTable" in src, "Group-Object -AsHashTable kullan")
```

```solution
$tablo = Import-Csv sunucular.csv | Group-Object Rol -AsHashTable -AsString
foreach ($rol in $Girdi) {
    if ($tablo.ContainsKey($rol)) {
        ($tablo[$rol].Ad | Sort-Object) -join ","
    } else {
        "yok"
    }
}
```

```hint
`Group-Object Rol -AsHashTable -AsString` her rolü bir anahtar yapar; değer o roldeki satırlardır. Her sorguda yeniden süzmek yerine tabloya bak.
```
:::
