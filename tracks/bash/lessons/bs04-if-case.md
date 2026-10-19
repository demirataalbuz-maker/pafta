---
id: bs04
title: if ve case
summary: if/elif/else blokları, case ile desen tabanlı dallanma ve komut dağıtıcı kalıbı.
---

::: anlat if: komutun başarısına göre dallan
Bash'te `if` bir **komutun çıkış koduna** bakar; çoğu zaman o komut `[[ ]]` ya da `(( ))` testidir:

```bash
kod=404
if (( kod >= 500 )); then
    echo "sunucu hatası"
elif (( kod >= 400 )); then
    echo "istemci hatası"
else
    echo "sorun yok"
fi
```

Yapı: `if KOMUT; then ... elif KOMUT; then ... else ... fi`. `fi`, `if`'in tersten yazılışıdır. Herhangi bir komut koşul olabilir:

```bash
if grep -q "root" /etc/passwd 2>/dev/null; then   #! -q: sessiz, sadece kod döndür
    echo "root kullanıcısı tanımlı"
else
    echo "passwd okunamadı ya da root yok"
fi
```

### case: desene göre dallan
Bir değeri birçok desenle karşılaştırırken `case` uzun `elif` zincirinden çok daha okunaklıdır. Desenler **joker** sözdizimindedir (`*`, `?`, `[...]`), regex değil:

```bash
for dosya in a.log b.txt c.sh d; do
    case "$dosya" in
        *.log)       echo "$dosya: log" ;;        #! ;; dalı bitirir
        *.sh|*.py)   echo "$dosya: betik" ;;      #! | ile alternatif desenler
        *)           echo "$dosya: bilinmiyor" ;; #! * her şeyi yakalar
    esac
done
```

> [!NOT]
> Komut satırı araçları alt komutları (`servis start`, `servis stop`) genelde `case "$1" in` ile dağıtır. `/etc/init.d` altındaki eski servis betiklerinin hepsi bu kalıptadır.
:::

::: tahmin
Çıktıyı satır satır yaz:

```bash
for dosya in a.log b.txt c.sh d; do
    case "$dosya" in
        *.log) echo "$dosya: log" ;;
        *.sh|*.py) echo "$dosya: betik" ;;
        *) echo "$dosya: bilinmiyor" ;;
    esac
done
```

???

```cikti
a.log: log
b.txt: bilinmiyor
c.sh: betik
d: bilinmiyor
```

`case` desenleri yukarıdan aşağı dener ve ilk tutanda durur. `*` her şeyi yakalayan son daldır.
:::

::: gorev HTTP durum sınıfı
Girdiden bir HTTP durum kodu oku ve sınıfını yazdır: 200–299 `başarılı`, 300–399 `yönlendirme`, 400–499 `istemci hatası`, 500–599 `sunucu hatası`, diğerleri `geçersiz`.

```starter
read -r kod

```

```stdin
404
```

```test
for girdi, beklenen in [("200", "başarılı"), ("301", "yönlendirme"), ("404", "istemci hatası"), ("503", "sunucu hatası"), ("99", "geçersiz"), ("600", "geçersiz")]:
    eq(run(girdi + "\n").strip(), beklenen, f"{girdi} → {beklenen}")
```

```solution
read -r kod
if (( kod >= 200 && kod <= 299 )); then
    echo "başarılı"
elif (( kod >= 300 && kod <= 399 )); then
    echo "yönlendirme"
elif (( kod >= 400 && kod <= 499 )); then
    echo "istemci hatası"
elif (( kod >= 500 && kod <= 599 )); then
    echo "sunucu hatası"
else
    echo "geçersiz"
fi
```

```hint
`(( kod >= 200 && kod <= 299 ))` aritmetik testinde `&&` kullanılabilir.
```
:::

::: gorev Servis komutu
Betik ilk argümana göre şunları yazdırsın (`case` kullan):

| Argüman | Çıktı |
|---|---|
| `start` | `servis başlatılıyor` |
| `stop` ya da `kill` | `servis durduruluyor` |
| `status` | `servis çalışıyor` |
| başka/yok | `kullanım: start|stop|status` (standart hataya) ve çıkış kodu 2 |

```starter
if [[ "$1" == "start" ]]; then echo "servis başlatılıyor"; fi
```

```meta
argv: status
```

```test
eq(run(argv=["start"]), "servis başlatılıyor\n", "start")
eq(run(argv=["stop"]), "servis durduruluyor\n", "stop")
eq(run(argv=["kill"]), "servis durduruluyor\n", "kill")
eq(run(argv=["status"]), "servis çalışıyor\n", "status")
r = calis(argv=["restart"])
eq(r["kod"], 2, "bilinmeyen komut → kod 2")
ok("kullanım" in r["hata"], "kullanım mesajı standart hataya", got=r["hata"])
ok("case" in src, "case kullan")
```

```solution
case "$1" in
    start)      echo "servis başlatılıyor" ;;
    stop|kill)  echo "servis durduruluyor" ;;
    status)     echo "servis çalışıyor" ;;
    *)
        echo "kullanım: start|stop|status" >&2
        exit 2
        ;;
esac
```

```hint
`case "$1" in ... esac`. Varsayılan dal `*)`; içinde birden fazla komut yazılabilir, son satırda `;;`.
```
:::

::: gorev Dosya türü
Girdiden satır satır dosya adları gelecek (her satır bir dosya). Her biri için `ad: tür` yazdır: `.jpg`/`.png` → `görsel`, `.log` → `log`, `.tar.gz`/`.zip` → `arşiv`, diğerleri → `diğer`. Büyük harfli uzantılar (`.PNG`) da tanınmalı.

```starter
while read -r dosya; do
    echo "$dosya: diğer"
done
```

```stdin
foto.jpg
yedek.tar.gz
app.log
```

```test
girdi = "foto.jpg\nyedek.tar.gz\napp.log\nEKRAN.PNG\nnotlar.txt\nsiparis.zip\n"
eq(run(girdi).splitlines(), ["foto.jpg: görsel", "yedek.tar.gz: arşiv", "app.log: log", "EKRAN.PNG: görsel", "notlar.txt: diğer", "siparis.zip: arşiv"], "türler")
```

```solution
while read -r dosya; do
    case "${dosya,,}" in
        *.jpg|*.png)     tur="görsel" ;;
        *.log)           tur="log" ;;
        *.tar.gz|*.zip)  tur="arşiv" ;;
        *)               tur="diğer" ;;
    esac
    echo "$dosya: $tur"
done
```

```hint
Küçük harfe çevirmek için Bash'in `${degisken,,}` genişletmesi var: `case "${dosya,,}" in`.
```
:::
