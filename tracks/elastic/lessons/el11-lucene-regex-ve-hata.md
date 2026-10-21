---
id: el11
title: Lucene · Regex Otomatı ve Açık Hatalar
summary: Lucene regex dilini Python/PCRE kurallarından ayır; mapping hatasını sessiz sonuç sanma.
---

::: anlat Regex tek indeks terimini kapsar
Slash içindeki Lucene regex, keyword değerinin veya text alanındaki tek indeks teriminin tamamını eşler. `process.name:/(cmd|powershell)\.exe/` iki tam dosya adını kabul eder; xcmd.exe ve cmd.exe.bak uymaz. Noktayı \. ile kaçırmak, herhangi bir karakter yerine gerçek noktayı ister. Normalizersız keyword büyük/küçük harfe duyarlıdır.

Lucene regex'i Python re veya PCRE değildir. `^` ve `$` burada alışıldık başlangıç/bitiş çapaları olarak desteklenmez; desen zaten tüm terime uygulanır. Lookaround, geri başvuru ve Python bayrakları varsayma. Bu ders kontrollü alternatif, karakter sınıfı ve tekrar kullanır; gerçek Lucene RegExp otomatı derlenir.

```lucene
process.name:/(cmd|powershell)\.exe/
```

`/cmd/` kaynak metin içinde cmd geçen her belgeyi bulmaz. Bunun için tek terime başta/sonda .* eklemek başka bir desendir; text alanında yine terim sınırlarını aşamaz. Çok geniş otomatlara motor çalışma limiti uygular. [Lucene RegExp dili](https://lucene.apache.org/core/9_12_3/core/org/apache/lucene/util/automaton/RegExp.html), [Elastic regex uyarıları](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-query-string-query). Kaynaklar 21 Ekim 2026 tarihinde kontrol edildi.

```meta
dil: lucene
```
:::

::: anlat Hata, boş eşleşme ve sınırlı destek
Geçerli sorgu hiç belge bulmayabilir; bu başarıyla hesaplanmış boş kümedir. Kapanmamış parantez, bilinmeyen alan veya long alanda geçersiz sayı ise sorgu hatasıdır. Pafta bunları geçerli boş sonuç gibi kabul etmez. Alan adını ve mapping'i kontrol ederek düzelt.

Bu yolda explicit alan gereklidir. Varsayılan alan, alan adı jokeri, nested Lucene sorgusu, özel analyzer, puanlama boost'u ve Elasticsearch API seçenekleri kapsam dışıdır ve reddedilir. Gerçek Elasticsearch query_string davranışının tamamı olduğu iddiası yoktur. index:false alanının doc_values üzerinden aranması da desteklenmez. Bu sınırlar metin, eşleme ve API farklarını gizlememek içindir.

Bir regex'in geçerli olması niyetinin doğru olduğu anlamına gelmez. Tam terim, harf büyüklüğü, tam iki rakam ve sayısal açık üst uç için ayrı karşı örnekler gerekir. Sonraki görevde regex ile sayısal aralığı AND kurarak dosya adı biçimi ile boyutu birlikte sınırlayacaksın. [Elastic Lucene özellik sınırları](https://www.elastic.co/docs/explore-analyze/query-filter/languages/lucene-query-syntax).

```meta
dil: lucene
```
:::

::: tahmin
Sorguyu çalıştırmadan önce dönecek kimlikleri sırayla tahmin et. Gerçek Lucene motoru kullanılacak. Context sıralaması yoksa belge giriş sırası korunur; bütün veri aşağıdadır.

```lucene
process.name:/(cmd|powershell)\.exe/
```

```stdin
{
  "dil": "lucene",
  "mapping": {
    "process.name": {
      "type": "keyword"
    },
    "file.name": {
      "type": "keyword"
    },
    "file.size": {
      "type": "long"
    }
  },
  "documents": [
    {
      "id": "a",
      "process.name": "cmd.exe"
    },
    {
      "id": "b",
      "process.name": "powershell.exe"
    },
    {
      "id": "c",
      "process.name": "xcmd.exe"
    },
    {
      "id": "d",
      "process.name": "CMD.exe"
    },
    {
      "id": "e",
      "process.name": "cmd.exe.bak"
    },
    {
      "id": "f",
      "process.name": "bash.exe"
    }
  ],
  "context": {}
}
```

```meta
dil: lucene
```

???

Çıktı:

```text
a
b
```

Regex tüm keyword terimini tüketir; c/e yalnız alt metin olarak benzer. d büyük harf nedeniyle farklıdır; f alternatiflerde yoktur.
:::

::: gorev İki tam araç adını native regex ile bul
process.name tam cmd.exe veya powershell.exe olsun. Büyük/küçük harfi koru; önek, ek ve nokta yerine başka karakteri kabul etme.

Editöre yalnız Lucene sorgusu yaz. `stdin` eşlemeyi, belgeleri ve bağımsız zaman/sıralama bağlamını taşır. Testte `eslesenler()` senin sorgunun kimliklerini döndürür; `eslesenler(belge_listesi)` aynı mapping/context ile yeni belgeleri sınar. Python kodu yazman gerekmiyor.

```starter
*:*
```

```stdin
{
  "dil": "lucene",
  "mapping": {
    "process.name": {
      "type": "keyword"
    },
    "file.name": {
      "type": "keyword"
    },
    "file.size": {
      "type": "long"
    }
  },
  "documents": [
    {
      "id": "a",
      "process.name": "cmd.exe"
    },
    {
      "id": "b",
      "process.name": "powershell.exe"
    },
    {
      "id": "c",
      "process.name": "xcmd.exe"
    },
    {
      "id": "d",
      "process.name": "CMD.exe"
    },
    {
      "id": "e",
      "process.name": "cmd.exe.bak"
    },
    {
      "id": "f",
      "process.name": "bash.exe"
    }
  ],
  "context": {}
}
```

```meta
dil: lucene
```

```test
eq(eslesenler(), ['a', 'b'], "ana korpus")
eq(eslesenler([{'id': 'x', 'process.name': 'cmdXexe'}, {'id': 'y', 'process.name': 'powershell.exe.old'}, {'id': 'z', 'process.name': 'powershell.exe'}]), ['z'], "değişen korpus 1")
eq(eslesenler([{'id': 'p', 'process.name': ['other', 'cmd.exe']}, {'id': 'q', 'process.name': 'PowerShell.exe'}, {'id': 'r'}]), ['p'], "değişen korpus 2")
```

```solution
process.name:/(cmd|powershell)\.exe/
```

```hint
Alternatifleri (cmd|powershell) olarak grupla ve gerçek noktayı \. ile yaz.
```
:::

::: gorev İki rakamlı raporu boyutuyla daralt
file.name tam report + iki ASCII rakam + .txt biçiminde olsun. file.size 100 dahil, 200 hariç olsun. Dosya adı normalizersız keyword; eksik boyut dışlanır.

Editöre yalnız Lucene sorgusu yaz. `stdin` eşlemeyi, belgeleri ve bağımsız zaman/sıralama bağlamını taşır. Testte `eslesenler()` senin sorgunun kimliklerini döndürür; `eslesenler(belge_listesi)` aynı mapping/context ile yeni belgeleri sınar. Python kodu yazman gerekmiyor.

```starter
*:*
```

```stdin
{
  "dil": "lucene",
  "mapping": {
    "process.name": {
      "type": "keyword"
    },
    "file.name": {
      "type": "keyword"
    },
    "file.size": {
      "type": "long"
    }
  },
  "documents": [
    {
      "id": "a",
      "file.name": "report01.txt",
      "file.size": 100
    },
    {
      "id": "b",
      "file.name": "report99.txt",
      "file.size": 199
    },
    {
      "id": "c",
      "file.name": "report01.txt",
      "file.size": 200
    },
    {
      "id": "d",
      "file.name": "report1.txt",
      "file.size": 150
    },
    {
      "id": "e",
      "file.name": "xreport01.txt",
      "file.size": 150
    }
  ],
  "context": {}
}
```

```meta
dil: lucene
```

```test
eq(eslesenler(), ['a', 'b'], "ana korpus")
eq(eslesenler([{'id': 'x', 'file.name': 'report00.txt', 'file.size': 99}, {'id': 'y', 'file.name': 'report10.txt', 'file.size': 100}, {'id': 'z', 'file.name': 'report100.txt', 'file.size': 150}, {'id': 'w', 'file.name': 'report10Xtxt', 'file.size': 150}]), ['y'], "değişen korpus 1")
eq(eslesenler([{'id': 'p', 'file.name': 'Report01.txt', 'file.size': 199}, {'id': 'q', 'file.name': 'report02.txt'}, {'id': 'r', 'file.name': 'report02.txt', 'file.size': 199}, {'id': 's', 'file.name': 'report02.txt', 'file.size': 201}]), ['r'], "değişen korpus 2")
```

```solution
file.name:/report[0-9]{2}\.txt/ AND file.size:[100 TO 200}
```

```hint
Regex için /report[0-9]{2}\.txt/; boyut için ayrı yarı açık aralık yaz ve AND ile bağla.
```
:::
