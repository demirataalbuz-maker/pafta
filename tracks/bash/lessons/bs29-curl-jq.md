---
id: bs29
title: curl ve jq ile JSON API
summary: Gerçek Linux'ta curl ile istek, durum kodu ve çıkış kodu ayrı şeylerdir (401 alan curl 0 döner, --fail 22, kapalı port 7, zaman aşımı 28); çerez kavanozu, --json, güvenli sorgu dizesi; jq ile alan seçmek, süzmek, @tsv, --arg, -e ve boş girdinin sessizce geçmesi.
backend: wsl
timeout: 120
---

::: anlat curl: durum kodu ile çıkış kodu aynı şey değil
Bu dersin bütün adımları **gerçek Linux'ta** (Kali, WSL) çalışır. Hazırlık bloğu her işte yerel bir test API'si başlatır ve adresini `api_adres.txt` dosyasına yazar; internete çıkılmaz.

`curl` bir isteği atar ve gövdeyi standart çıktıya yazar. İlk tuzak: **HTTP durum kodu** ile curl'ün **çıkış kodu** farklı şeylerdir. Sunucu `401` ya da `500` dönse bile curl isteği başarıyla tamamladığı için `0` ile çıkar:

```bash
adres=$(cat api_adres.txt)
curl -s -o /dev/null -w '%{http_code}\n' "$adres/api/biletler"     #! durum kodu: 401
curl -s "$adres/api/biletler"; echo " çıkış=$?"                      #! gövde yazılır, çıkış 0
curl -s --fail "$adres/api/biletler"; echo "çıkış=$?"                #! --fail: gövde yok, çıkış 22
```

| Seçenek | Ne yapar |
|---|---|
| `-s` | İlerleme çubuğunu gizler (`-S` ile hatalar yine görünür) |
| `-o dosya` | Gövdeyi dosyaya yazar; `-o /dev/null` atar |
| `-w '%{http_code}'` | İstek bitince durum kodunu yazdırır |
| `--fail` | 4xx/5xx'te gövdeyi yazmaz, **22** ile çıkar |
| `--fail-with-body` | Gövdeyi yazar ve yine 22 ile çıkar |
| `--max-time 5` | Toplam süre sınırı; aşılırsa **28** |
| `--json '{...}'` | POST, gövde ve iki JSON başlığı birden |
| `-c kavanoz.txt` / `-b kavanoz.txt` | Çerezi dosyaya yaz / dosyadan gönder |
| `--get --data-urlencode "sayfa=$s"` | Sorgu dizesini **kodlayarak** kurar |

Bu derste ölçülen çıkış kodları: başarı ve 401 `0`, `--fail` ile 401 `22`, kapalı port `7`, `--max-time` aşımı `28`. Bir betikte "istek başarılı mı?" sorusu bu yüzden iki parçalıdır: curl çıktı mı (`$?`), ve durum kodu beklediğin mi?

Oturum için curl'ün kendi çerez kavanozu yeter:

```bash
adres=$(cat api_adres.txt)
curl -s -c kavanoz.txt --json '{"kullanici":"analist","parola":"pafta123"}' "$adres/giris"; echo
curl -s -b kavanoz.txt "$adres/api/biletler?sayfa=3"; echo         #! çerez gitti: 200
```

> [!TUZAK] Değişkeni adrese elle yapıştırma
> `curl "$adres/api/biletler?sayfa=$s"` satırında `$s` boşluk, `&` ya da `#` içerirse istek bozulur ya da başka bir parametre eklenir. Kullanıcıdan gelen değeri `--get --data-urlencode "sayfa=$s"` ile ver; curl onu kodlar. Aynı kural JSON gövdesi için de geçerli: değerleri metne yapıştırmak yerine `jq -n --arg` ile gövde kur.

```setup
import os, runpy, sys, pathlib
_s = next(os.path.dirname(m.__file__) for m in list(sys.modules.values())
          if os.path.basename(getattr(m, "__file__", None) or "") in ("py_harness.py", "wsl_job.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
pathlib.Path("api_adres.txt").write_text(sys.modules["api"].SUNUCU, encoding="utf-8")
```
:::

::: anlat jq: JSON'u komut hattında okumak
`jq` JSON için `awk` neyse odur: girdiyi okur, bir **süzgeç** uygular, sonucu yazar.

```bash
adres=$(cat api_adres.txt)
curl -s -c kavanoz.txt --json '{"kullanici":"analist","parola":"pafta123"}' "$adres/giris" >/dev/null
curl -s -b kavanoz.txt "$adres/api/biletler" > sayfa.json

jq '.toplam' sayfa.json                                   #! 7
jq -r '.kayitlar[] | [.id, .baslik] | @tsv' sayfa.json    #! sekmeyle ayrılmış satırlar
jq -r '.kayitlar[] | select(.oncelik == "yüksek") | .id' sayfa.json
jq '.kayitlar | length' sayfa.json                        #! 3
```

| Süzgeç | Anlamı |
|---|---|
| `.alan`, `.a.b` | Alan seçmek |
| `.dizi[]` | Dizinin her elemanı ayrı sonuç |
| `select(koşul)` | Koşulu tutanları geçir |
| `[.a, .b] \| @tsv` | Satırı sekmeyle ayır (`@csv` virgülle) |
| `.alan // "yok"` | Alan `null` ya da `false` ise varsayılan |
| `length` | Dizi, nesne ya da metnin uzunluğu |
| `-r` | Metni tırnaksız yaz |
| `--arg ad "$deger"` | Kabuk değerini **güvenle** `$ad` olarak ver |
| `-e` | Son sonuç `null`/`false` ise çıkış **1** |

> [!TUZAK] jq boş girdiyi hatasız geçer
> Gövdesi olmayan bir yanıtı (`204 No Content`, ya da bağlantı kesildiği için boş kalan dosya) `jq` ile okursan hiçbir şey yazmaz ve **0** ile çıkar: hata da, uyarı da yoktur. Bozuk JSON ise (ör. bir HTML sayfası) `parse error` verip **5** ile çıkar. Betiğinde gövdenin boş olmadığını ayrıca denetle: `[[ -s govde.json ]]`.

> [!TUZAK] Kabuk değerini jq programına yapıştırma
> `jq ".kayitlar[] | select(.oncelik == \"$o\")"` yazarsan `$o` içindeki bir tırnak jq programını değiştirir. Doğrusu `jq --arg o "$o" '.kayitlar[] | select(.oncelik == $o)'`: değer veri olarak gider, kod olarak değil.

```setup
import os, runpy, sys, pathlib
_s = next(os.path.dirname(m.__file__) for m in list(sys.modules.values())
          if os.path.basename(getattr(m, "__file__", None) or "") in ("py_harness.py", "wsl_job.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
pathlib.Path("api_adres.txt").write_text(sys.modules["api"].SUNUCU, encoding="utf-8")
```
:::

::: tahmin
Ne yazar?

```bash
adres=$(cat api_adres.txt)
curl -s -o /dev/null -w '%{http_code}\n' "$adres/api/biletler"
curl -s "$adres/api/biletler"; echo " rc=$?"
curl -s --fail "$adres/api/biletler"; echo "rc=$?"
curl -s "$adres/bos" | jq '.hata'; echo "rc=$?"
```

???

`401`, `{"hata": "oturum"} rc=0`, `rc=22` ve `rc=0`.

Oturumsuz liste isteği `401` alır. curl isteği tamamladığı için `--fail` olmadan çıkış kodu `0`'dır ve sunucunun hata gövdesi yazılır. `--fail` ile gövde yazılmaz, çıkış `22` olur. Son satır dersin en sinsi tuzağı: `/bos` gövdesiz bir `204` döner, `jq` boş girdiyi okur, **hiçbir şey yazmaz** ve `0` ile çıkar — bir betik bunu "alan boşmuş" diye yorumlayıp devam edebilir.

```setup
import os, runpy, sys, pathlib
_s = next(os.path.dirname(m.__file__) for m in list(sys.modules.values())
          if os.path.basename(getattr(m, "__file__", None) or "") in ("py_harness.py", "wsl_job.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
pathlib.Path("api_adres.txt").write_text(sys.modules["api"].SUNUCU, encoding="utf-8")
```
:::

::: gorev Oturumlu sayfa
Girdinin ilk satırı bir sayfa numarasıdır. `analist`/`pafta123` ile giriş yap (çerezi bir kavanoza yaz), o sayfayı iste ve her kayıt için `<id><TAB><başlık>` satırı yazdır. Sunucu `200` dışında bir kod dönerse ya da girdi boşsa tek satır `HATA` yazdır.

Sayfa numarasını adrese elle yapıştırma; `--get --data-urlencode` kullan.

```stdin
1
```

```setup
import os, runpy, sys, pathlib
_s = next(os.path.dirname(m.__file__) for m in list(sys.modules.values())
          if os.path.basename(getattr(m, "__file__", None) or "") in ("py_harness.py", "wsl_job.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
pathlib.Path("api_adres.txt").write_text(sys.modules["api"].SUNUCU, encoding="utf-8")
```

```starter
read -r sayfa
adres=$(cat api_adres.txt)
curl -s "$adres/api/biletler?sayfa=$sayfa"
```

```test
eq(out, "101\tweb01 disk doldu\n102\tdb01 yedek gecikti\n103\tcache01 yeniden başladı\n", "ilk sayfanın üç kaydı")
eq(run(stdin="3\n"), "107\tyedek01 disk testi\n", "son sayfada tek kayıt")
eq(run(stdin="4\n"), "", "aralık dışı sayfa boş: 200 ama kayıt yok")
eq(run(stdin="0\n"), "HATA\n", "sunucu 0 için 400 döner")
eq(run(stdin="bir\n"), "HATA\n", "sayı olmayan sayfa: sunucu 400 döner")
eq(run(stdin="1&sayfa=2\n"), "HATA\n", "kodlanmış girdi başka parametre ekleyemez")
eq(run(stdin="\n"), "HATA\n", "boş girdi HATA")
ok("data-urlencode" in src, "sayfa numarasını --data-urlencode ile ver")
```

```solution
read -r sayfa || true      # son satırda \n yoksa read 1 döner ama değeri yine atar
adres=$(cat api_adres.txt)
if [[ -z $sayfa ]]; then
    echo HATA
    exit 0
fi
curl -s -c kavanoz.txt --json '{"kullanici":"analist","parola":"pafta123"}' "$adres/giris" > /dev/null
kod=$(curl -s -b kavanoz.txt -o sayfa.json -w '%{http_code}' \
      --get --data-urlencode "sayfa=$sayfa" "$adres/api/biletler")
if [[ $kod != 200 ]]; then
    echo HATA
    exit 0
fi
jq -r '.kayitlar[] | [.id, .baslik] | @tsv' sayfa.json
```

```hint
Gövdeyi dosyaya, durum kodunu değişkene al: `kod=$(curl -s -o sayfa.json -w '%{http_code}' ...)`. Böylece ikisini ayrı ayrı denetlersin.
```

```hint
`1&sayfa=2` girdisi elle yapıştırılırsa ikinci bir `sayfa` parametresi olur; `--data-urlencode` onu `1%26sayfa%3D2` diye tek değer yapar ve sunucu 400 döner.
```
:::

::: gorev Bütün sayfaları süz
Girdinin ilk satırında iki kelime var: bir öncelik (`yüksek`, `orta`, `düşük`) ve bir durum (`açık`, `çözüldü`). Giriş yap, 1. sayfadan başlayıp `sonraki` alanı `null` olana kadar bütün sayfaları gez; bu öncelik ve durumdaki biletlerin numaralarını sırayla yazdır, en sona `toplam <sayı>` satırını ekle.

Öncelik ya da durum listedekilerden biri değilse, ya da iki kelimeden biri eksikse tek satır `HATA` yazdır. Değerleri jq programına yapıştırma; `--arg` kullan.

```stdin
yüksek açık
```

```setup
import os, runpy, sys, pathlib
_s = next(os.path.dirname(m.__file__) for m in list(sys.modules.values())
          if os.path.basename(getattr(m, "__file__", None) or "") in ("py_harness.py", "wsl_job.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
pathlib.Path("api_adres.txt").write_text(sys.modules["api"].SUNUCU, encoding="utf-8")
```

```starter
read -r oncelik durum
adres=$(cat api_adres.txt)
curl -s -c kavanoz.txt --json '{"kullanici":"analist","parola":"pafta123"}' "$adres/giris" > /dev/null
curl -s -b kavanoz.txt "$adres/api/biletler" | jq -r ".kayitlar[] | select(.oncelik == \"$oncelik\") | .id"
```

```test
eq(out, "101\n104\n106\ntoplam 3\n", "üç sayfaya dağılmış açık yüksek biletler")
eq(run(stdin="yüksek çözüldü\n"), "toplam 0\n", "eşleşme yoksa yalnız toplam 0")
eq(run(stdin="düşük çözüldü\n"), "103\ntoplam 1\n", "ilk sayfadaki tek kayıt")
eq(run(stdin="orta açık\n"), "102\ntoplam 1\n", "orta açık")
eq(run(stdin="acil açık\n"), "HATA\n", "listede olmayan öncelik")
eq(run(stdin="yüksek kapalı\n"), "HATA\n", "listede olmayan durum")
eq(run(stdin="Yüksek açık\n"), "HATA\n", "büyük-küçük harf duyarlı")
eq(run(stdin="yüksek\n"), "HATA\n", "durum eksik")
eq(run(stdin="\n"), "HATA\n", "boş girdi")
ok("--arg" in src, "değerleri jq'ya --arg ile ver")
```

```solution
read -r oncelik durum || true
adres=$(cat api_adres.txt)
case $oncelik in yüksek|orta|düşük) ;; *) echo HATA; exit 0 ;; esac
case $durum in açık|çözüldü) ;; *) echo HATA; exit 0 ;; esac

curl -s -c kavanoz.txt --json '{"kullanici":"analist","parola":"pafta123"}' "$adres/giris" > /dev/null
toplam=0
sayfa=1
while [[ -n $sayfa ]]; do
    curl -s -b kavanoz.txt -o sayfa.json --get --data-urlencode "sayfa=$sayfa" "$adres/api/biletler"
    while read -r no; do
        echo "$no"
        toplam=$((toplam + 1))
    done < <(jq -r --arg o "$oncelik" --arg d "$durum" \
             '.kayitlar[] | select(.oncelik == $o and .durum == $d) | .id' sayfa.json)
    sayfa=$(jq -r '.sonraki // empty' sayfa.json)
done
echo "toplam $toplam"
```

```hint
Döngünün koşulu sunucunun `sonraki` alanıdır: `sayfa=$(jq -r '.sonraki // empty' sayfa.json)` son sayfada boş metin verir ve `while [[ -n $sayfa ]]` durur.
```

```hint
Sayacı artırırken `jq ... | while read` yazarsan döngü bir alt kabukta çalışır ve `toplam` değişikliği kaybolur (BS15). Süreç ikamesi `done < <(jq ...)` döngüyü ana kabukta tutar.
```
:::

::: gorev Kod, gövde ve boşluk
Girdinin ilk satırı `/` ile başlayan bir yoldur (ör. `/durum/503`). O yolu iste ve tek satır yazdır:

- Gövde **boşsa**: `<kod>|BOS`
- Gövde geçerli JSON değilse: `<kod>|JSON_DEGIL`
- Geçerli JSON ise: `<kod>|<hata alanı>`; `hata` alanı yoksa `<kod>|-`

Yol `/` ile başlamıyorsa ya da girdi boşsa tek satır `HATA` yazdır. Oturum açma; bu uçların hiçbiri oturum istemez ya da oturumsuz yanıt görmek istiyoruz.

```stdin
/durum/503
```

```setup
import os, runpy, sys, pathlib
_s = next(os.path.dirname(m.__file__) for m in list(sys.modules.values())
          if os.path.basename(getattr(m, "__file__", None) or "") in ("py_harness.py", "wsl_job.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
pathlib.Path("api_adres.txt").write_text(sys.modules["api"].SUNUCU, encoding="utf-8")
```

```starter
read -r yol
adres=$(cat api_adres.txt)
curl -s "$adres$yol" | jq -r '.hata'
```

```test
eq(out, "503|istek\n", "istenen hata kodu ve gövdedeki hata alanı")
eq(run(stdin="/durum/400\n"), "400|istek\n", "alt sınır 400 kabul edilir")
eq(run(stdin="/durum/399\n"), "400|kod\n", "alt sınırın altı: 400 ama sebep başka")
eq(run(stdin="/durum/599\n"), "599|istek\n", "üst sınır 599")
eq(run(stdin="/durum/600\n"), "400|kod\n", "üst sınırın üstü")
eq(run(stdin="/api/bilet/101\n"), "401|oturum\n", "oturumsuz istek 401")
eq(run(stdin="/yavas?ms=0&no=1\n"), "200|-\n", "hata alanı olmayan geçerli JSON")
eq(run(stdin="/sayfa/biletler\n"), "200|JSON_DEGIL\n", "HTML gövde JSON değildir")
eq(run(stdin="/bos\n"), "204|BOS\n", "gövdesiz 204: jq bunu sessizce geçerdi")
eq(run(stdin="durum/503\n"), "HATA\n", "/ ile başlamayan yol")
eq(run(stdin="\n"), "HATA\n", "boş girdi")
```

```solution
read -r yol || true
adres=$(cat api_adres.txt)
if [[ $yol != /* ]]; then
    echo HATA
    exit 0
fi
kod=$(curl -s -o govde.dat -w '%{http_code}' "$adres$yol")
if [[ ! -s govde.dat ]]; then
    echo "$kod|BOS"
elif ! jq empty govde.dat 2> /dev/null; then
    echo "$kod|JSON_DEGIL"
else
    echo "$kod|$(jq -r '.hata // "-"' govde.dat)"
fi
```

```hint
Boşluğu **ayrıca** denetle (`[[ -s dosya ]]`): `jq empty` boş dosyayı geçerli JSON sayar. Boşluk denetimi, alanı okuyan daldan önce gelmeli; yoksa gövdesiz yanıt `204|` diye yarım bir satır üretir.
```

```hint
`jq empty` girdi geçerli JSON ise hiçbir şey yazmadan 0, değilse 5 ile çıkar; hata mesajını `2> /dev/null` ile sustur.
```
:::
