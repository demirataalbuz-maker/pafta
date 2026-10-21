---
id: el10
title: Lucene · İfade, Slop ve Fuzzy
summary: Tırnaklı ifadeyi karakter alt dizisi sanma; verilen terim konumları ve bir düzenleme modelini oku.
---

::: anlat Tırnak analiz edilmiş terimlere uygulanır
`message:"login failed"` bir phrase aramasıdır; text alanında analyzer'ın ürettiği terimleri ve konumları kullanır. Kaynak cümlede iki kelimeyi karakter alt dizisi olarak aramak aynı işlem değildir. Bu ders analyzer yazdırmaz: `message_tokens` hangi terimin hangi konuma indekslendiğini açıkça verir.

```lucene
message:"login failed"~1
```

`~1` phrase için bir konumluk esneklik verir. Slop sıfırken bitişik sırayı, bu iki terimli fixture'da slop birken arada en çok bir konum boşluğunu düşün. Ters çevrilmiş iki terim için maliyet ikidir. Görev modelimiz **yalnız sırayı koruyan iki ayrı terimi** hesaplar; genel phrase motorunun bütün yeniden sıralamalarını modellemez. Kaynak: [Phrase ve slop](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-match-query-phrase).
:::

::: anlat Fuzzy başka bir yakınlıktır
`user.name:alice~1` ifadesindeki `~1`, phrase boşluğu değil terim düzenleme uzaklığıdır. Ekleme, silme, değiştirme ve ayarına göre bitişik karakter transpozisyonu yakın terimler üretebilir. Sorgu stringindeki fuzzy ayarlarını ve alan eşlemesini kontrol et; harf normalizasyonunu kendiliğinden varsayma.

`query_string` varsayılanları `fuzzy_prefix_length=0`, `fuzzy_max_expansions=50` ve `fuzzy_transpositions=true` değerleridir: sabit bırakılması zorunlu bir önek yoktur, genişleme sayısı sınırlıdır ve bitişik transpozisyonlar düzenleme sayılır. Aşağıdaki görev yalnız zaten normalleştirilmiş iki terim için uzaklık 1 kararını verir; `fuzzy_max_expansions` sınırını veya indeks sözlüğünü sınamaz.

İkinci görevde önceden normalleştirilmiş iki terim arasında **en çok bir** bu tür düzenleme olup olmadığını hesaplayacağız. Bu sınırlandırılmış uzaklık alıştırması genişleme sınırları, puanlama veya bir indeks sözlüğü çalıştırmaz. Tam eşitlik sıfır, bir değişiklik bir, iki bağımsız değişiklik iki uzaklıktır.

Aynı `~` karakteri farklı konumlarda farklı kavrama işaret eder. Önce tırnaklı ifade mi tek terim mi olduğunu belirlemek, sorguyu okumadaki ilk adımdır. Kaynak: [query_string fuzzy ayarları](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-query-string-query).
:::

::: tahmin
Aşağıdaki Lucene sorgusunu verilen eşleme, zaman filtresi ve sıralama altında oku. Hangi kimlikler döner? Pafta bu sorguyu Elasticsearch üzerinde çalıştırmaz; cevap, açık veri sözleşmesine göre hazırlanmış okuma cevabıdır.

```lucene
message:"login failed"~1
```

```stdin
{
  "mapping": {
    "message": "text; analyzer sonucu message_tokens içinde [terim, konum] olarak verilmiş; eşanlamlı yok, aynı konumda terim yok"
  },
  "time_filter": {
    "gte": "2026-10-21T10:00:00Z",
    "lt": "2026-10-21T11:00:00Z"
  },
  "ordering": "id artan; bu iki terimli örnekte slop 1, ters sıra maliyeti 2 olduğundan kabul edilmez",
  "documents": [
    {
      "id": "a",
      "@timestamp": "2026-10-21T10:01:00Z",
      "message_tokens": [
        [
          "login",
          0
        ],
        [
          "failed",
          1
        ]
      ]
    },
    {
      "id": "b",
      "@timestamp": "2026-10-21T10:02:00Z",
      "message_tokens": [
        [
          "login",
          0
        ],
        [
          "again",
          1
        ],
        [
          "failed",
          2
        ]
      ]
    },
    {
      "id": "c",
      "@timestamp": "2026-10-21T10:03:00Z",
      "message_tokens": [
        [
          "login",
          0
        ],
        [
          "failed",
          3
        ]
      ]
    },
    {
      "id": "d",
      "@timestamp": "2026-10-21T10:04:00Z",
      "message_tokens": [
        [
          "failed",
          0
        ],
        [
          "login",
          1
        ]
      ]
    },
    {
      "id": "e",
      "@timestamp": "2026-10-21T10:05:00Z",
      "message_tokens": [
        [
          "login",
          0
        ]
      ]
    },
    {
      "id": "f",
      "@timestamp": "2026-10-21T10:06:00Z",
      "message_tokens": []
    }
  ]
}
```

```gercek
a
b
```

```test
import json, sys
from datetime import datetime
f = json.load(sys.stdin)
dt = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
bas, son = (dt(f["time_filter"][k]) for k in ("gte", "lt"))
ids = []
for d in f["documents"]:
    tokens = d.get("message_tokens", [])
    uygun = any(a == "login" and b == "failed" and 0 <= pb - pa - 1 <= 1
                for a, pa in tokens for b, pb in tokens)
    if uygun and bas <= dt(d["@timestamp"]) < son:
        ids.append(d["id"])
for kimlik in sorted(ids):
    print(kimlik)
```

???

`a` bitişik, `b` bir konum boşluklu olduğu için döner. c iki konum boşlukludur; d ters sıralıdır ve bu örnekte slop bir yetmez. Eksik terimler eşleşmez.
:::

::: gorev Sırayı koruyan iki terim
`sirali_cift_idleri(olaylar, ilk, ikinci, slop)` verilen `message_tokens` listesinde ilk terimden **sonra** ikinci terim bulunuyorsa ve `ikinci_konum - ilk_konum - 1 <= slop` ise kimliği seçsin. Kimlikleri artan döndür. Terimler farklı, konumlar artan integer, slop negatif olmayan integer. Tekrarlı terimler olabilir; herhangi uygun çift yeterlidir. Bu model ters sıra eşleşmesi yapmaz ve genel Lucene slop hesabı değildir.

```starter
def sirali_cift_idleri(olaylar, ilk, ikinci, slop):
    return []
```

```test
need("sirali_cift_idleri")
rows = [{"id": str(gap), "message_tokens": [["login", 0], ["failed", gap + 1]]} for gap in (0, 1, 2)]
rows += [{"id": "ters", "message_tokens": [["failed", 0], ["login", 1]]}, {"id": "eksik"}, {"id": "tek", "message_tokens": [["login", 0]]}]
eq(sirali_cift_idleri(rows, "login", "failed", 0), ["0"], "slop sıfır")
eq(sirali_cift_idleri(rows, "login", "failed", 1), ["0", "1"], "eşik -1/eşit/+1 boşlukları")
eq(sirali_cift_idleri(rows, "login", "failed", 2), ["0", "1", "2"], "genişletilen model hâlâ ters sıra kabul etmez")
repeated = [{"id": "sonraki", "message_tokens": [["open", 0], ["close", 5], ["open", 7], ["close", 8]]}]
eq(sirali_cift_idleri(repeated, "open", "close", 0), ["sonraki"], "yalnız ilk eşleşmeye bakma")
eq(sirali_cift_idleri(repeated, "start", "close", 1), [], "terim parametresi")
```

```solution
def sirali_cift_idleri(olaylar, ilk, ikinci, slop):
    ids = []
    for d in olaylar:
        tokens = d.get("message_tokens", [])
        if any(a == ilk and b == ikinci and 0 <= pb - pa - 1 <= slop
               for a, pa in tokens for b, pb in tokens):
            ids.append(d["id"])
    return sorted(ids)
```

```hint
Bütün ilk/ikinci konum çiftlerini incele; farkın negatif olmaması sırayı korur.
```
:::

::: gorev Bir düzenleme kadar yakın
`yakin_bir(a, b)` iki Unicode metni sıfır veya bir ekleme, silme, değiştirme ya da bitişik iki karakterin yer değiştirmesi ile eşit olabiliyorsa True döndürsün. Girdiler zaten normalleştirilmiş terimlerdir; fonksiyon küçük harfe çevirmez. Bu görev uzaklık 1 kararını öğretir; sorgu ayrıştırmaz, indeks taramaz.

```starter
def yakin_bir(a, b):
    return False
```

```test
need("yakin_bir")
for a, b, beklenen in [("alice", "alice", True), ("alice", "alixe", True), ("alice", "alce", True), ("alice", "alixce", True), ("alice", "ailce", True), ("alice", "alixez", False), ("abc", "cba", False), ("a", "", True), ("ab", "", False), ("", "", True), ("alice", "Alice", True), ("alice", "ALICE", False)]:
    eq(yakin_bir(a, b), beklenen, f"0/1/2 düzenleme: {a!r} -> {b!r}")
    eq(yakin_bir(b, a), beklenen, "yakınlık simetrik")
from itertools import product
alfabe = "ab"
kelimeler = [""] + ["".join(x) for n in (1, 2, 3) for x in product(alfabe, repeat=n)]
for a in kelimeler:
    komsular = {a}
    for i in range(len(a)):
        komsular.add(a[:i] + a[i + 1:])
        for c in alfabe:
            komsular.add(a[:i] + c + a[i + 1:])
    for i in range(len(a) + 1):
        for c in alfabe:
            komsular.add(a[:i] + c + a[i:])
    for i in range(len(a) - 1):
        komsular.add(a[:i] + a[i + 1] + a[i] + a[i + 2:])
    for b in kelimeler:
        eq(yakin_bir(a, b), b in komsular, "değişen kısa terim korpusu")
```

```solution
def yakin_bir(a, b):
    if a == b:
        return True
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        farklar = [i for i in range(len(a)) if a[i] != b[i]]
        if len(farklar) == 1:
            return True
        return (len(farklar) == 2 and farklar[1] == farklar[0] + 1
                and a[farklar[0]] == b[farklar[1]] and a[farklar[1]] == b[farklar[0]])
    kisa, uzun = sorted((a, b), key=len)
    return any(uzun[:i] + uzun[i + 1:] == kisa for i in range(len(uzun)))
```

```hint
Uzunluk farkını önce ayır. Aynı uzunlukta bir fark değiştirme, iki bitişik karşılıklı fark transpozisyon olabilir.
```
:::
