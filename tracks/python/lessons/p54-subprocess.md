---
id: p54
title: Süreçler · subprocess
summary: Başka programları güvenle çalıştırmak; argüman listesi, çıktı yakalama, dönüş kodu, zaman aşımı.
---

::: anlat Başka bir program çalıştırmak
Python'dan başka bir programı (bir sistem aracını, bir betiği, başka bir Python sürecini) çalıştırmanın modern yolu `subprocess.run`'dır. Örneklerde taşınabilir olması için hep Python'un kendisini (`sys.executable`) çocuk süreç olarak çalıştırıyoruz:

```python
import subprocess, sys

r = subprocess.run(
    [sys.executable, "-c", "print('merhaba'); import sys; sys.exit(0)"],   #! komut + argümanlar LİSTE olarak
    capture_output=True,          #! stdout/stderr'i yakala (ekrana basma)
    text=True,                    #! baytları metne çevir
    timeout=10,                   #! asılı kalırsa TimeoutExpired
)
print("dönüş kodu:", r.returncode)    #! 0 = başarı, başka her şey = hata (gelenek)
print("çıktı:", r.stdout.strip())
print("hata akışı:", repr(r.stderr))
```

| Parametre | İş |
|---|---|
| `capture_output=True` | `r.stdout` ve `r.stderr`'i doldurur |
| `text=True` | bytes yerine str |
| `check=True` | dönüş kodu 0 değilse `CalledProcessError` |
| `timeout=N` | N saniyede bitmezse süreci öldürür, `TimeoutExpired` |
| `input="..."` | çocuğun stdin'ine veri gönder |
| `cwd=`, `env=` | çalışma klasörü, ortam değişkenleri |

```python
import subprocess, sys

try:
    subprocess.run([sys.executable, "-c", "import sys; sys.exit(2)"], check=True)
except subprocess.CalledProcessError as e:
    print("başarısız, kod:", e.returncode)

r = subprocess.run([sys.executable, "-c", "print(input()[::-1])"],
                   input="pafta", capture_output=True, text=True)
print(r.stdout.strip())
```

> [!NOT]
> `os.system("...")` ve `os.popen` eski yöntemlerdir: çıktıyı düzgün yakalayamazsın ve her zaman bir kabuk (shell) üzerinden çalışırlar. Yeni kodda `subprocess.run` kullan.
:::

::: tahmin
Çıktı tek satır:

```python
import subprocess, sys
r = subprocess.run([sys.executable, "-c", "import sys; print('cikti'); sys.exit(3)"],
                   capture_output=True, text=True)
print(r.returncode, r.stdout.strip())
```

???

`3 cikti`. Çocuk süreç önce yazdı, sonra 3 koduyla çıktı. `check=True` verilmediği için sıfırdan farklı kod istisna yükseltmez; sadece `returncode`'a yazılır.
:::

::: anlat Komut enjeksiyonu ve argüman listesi
`subprocess`'in en önemli güvenlik kuralı: **komutu metin olarak kurup `shell=True` ile çalıştırma**, özellikle içinde dışarıdan gelen bir değer varsa.

```python norun
# KÖTÜ: dosya_adi kullanıcıdan geliyor
subprocess.run(f"cat {dosya_adi}", shell=True)
# dosya_adi = "rapor.txt; <başka bir komut>" olursa kabuk İKİ komut çalıştırır
```

`shell=True` dediğinde metin bir **kabuğa** (`/bin/sh` ya da `cmd.exe`) verilir. Kabuk `;`, `&&`, `|`, `` ` `` ve `$()` gibi karakterleri komut ayırıcısı olarak yorumlar. Kullanıcı girdisi bu karakterleri içerirse, girdinin yazarı senin sunucunda istediği komutu çalıştırır. Buna **komut enjeksiyonu** (OS command injection) denir.

**Argüman listesi** kullanınca kabuk yoktur: işletim sistemine "şu programı, tam olarak şu argümanlarla çalıştır" denir. Argümanın içinde ne olursa olsun **tek bir argüman** olarak kalır:

```python
import subprocess, sys

girdi = "rapor.txt; echo ikinci-komut"
r = subprocess.run([sys.executable, "-c", "import sys; print(sys.argv[1:])", girdi],
                   capture_output=True, text=True)
print(r.stdout.strip())       #! ['rapor.txt; echo ikinci-komut'] — sadece bir metin
```

> [!GÜVENLİK]
> Savunma katmanları:
> 1. **Liste kullan, `shell=True` kullanma.** Kabuk özelliğine (boru, joker) gerçekten ihtiyacın varsa onu Python'da yap.
> 2. **Girdiyi izin listesiyle doğrula**: bir host adı bekliyorsan sadece harf, rakam, nokta ve tire kabul et (`re.fullmatch`). Kötü karakterleri ayıklamaya çalışma; iyi olanı tarif et.
> 3. **Seçenek enjeksiyonuna dikkat**: `-` ile başlayan bir girdi programın seçeneği sanılabilir (`--output=/etc/...`). Gerekirse argümanlardan önce `--` koy.
> 4. Kaçınılmazsa `shlex.quote()` ile tırnakla (sadece POSIX kabukları için).
>
> Aynı ilke SQL'deki parametreli sorgularla (P29) aynıdır: **veri ile komutu ayrı kanallardan ilet.**
:::

::: tahmin
Çıktı tek satır:

```python
import subprocess, sys
kod = "import sys; print(len(sys.argv) - 1)"
r = subprocess.run([sys.executable, "-c", kod, "a b", "c;d", "--x"], capture_output=True, text=True)
print(r.stdout.strip())
```

???

`3`. Liste biçiminde her eleman ayrı ve **tek** bir argümandır: `"a b"` boşluk içerdiği halde bölünmez, `"c;d"` bir komut ayırıcı olarak yorumlanmaz. Çocuk süreç tam üç argüman görür.
:::

::: gorev Çocuk süreçte çalıştır
`calistir(kod)` fonksiyonu verilen Python kodunu **ayrı bir süreçte** (`sys.executable -c kod`) çalıştırsın ve `(dönüş_kodu, stdout)` demetini döndürsün; stdout'un kenar boşlukları temizlenmiş olsun. 5 saniyelik zaman aşımı koy; zaman aşımında `(-1, "")` döndür.

```starter
import subprocess, sys

def calistir(kod):
    pass
```

```meta
timeout: 20
```

```test
need("calistir")
eq(calistir("print(6 * 7)"), (0, "42"), "print(6*7) → (0, '42')")
eq(calistir("import sys; print('x'); sys.exit(4)"), (4, "x"), "çıkış kodu 4")
eq(calistir("import time; time.sleep(30)"), (-1, ""), "zaman aşımı → (-1, '')")
ok(calls("run"), "subprocess.run kullan")
ok("shell=True" not in src.replace(" ", ""), "shell=True kullanma")
```

```solution
import subprocess, sys

def calistir(kod):
    try:
        r = subprocess.run([sys.executable, "-c", kod], capture_output=True, text=True, timeout=5)
    except subprocess.TimeoutExpired:
        return -1, ""
    return r.returncode, r.stdout.strip()
```

```hint
`subprocess.run([sys.executable, "-c", kod], capture_output=True, text=True, timeout=5)` ve `except subprocess.TimeoutExpired:`.
```
:::

::: gorev Güvenli komut kurucu
Bir ağ teşhis aracı, kullanıcıdan aldığı host adına `ping` atacak. `ping_komutu(host)` fonksiyonu komutu **çalıştırmasın**, sadece **argüman listesini** döndürsün: `["ping", "-c", "1", host]`.

Host'u izin listesiyle doğrula: 1–253 karakter, sadece harf, rakam, nokta ve tire; **tire ile başlayamaz**. Geçersizse `ValueError` yükselt.

```starter
import re

def ping_komutu(host):
    return ["ping", "-c", "1", host]
```

```test
need("ping_komutu")
eq(ping_komutu("ornek.com"), ["ping", "-c", "1", "ornek.com"], "normal host")
eq(ping_komutu("10.0.0.7"), ["ping", "-c", "1", "10.0.0.7"], "IP adresi")
eq(ping_komutu("web-01.lab"), ["ping", "-c", "1", "web-01.lab"], "tireli host")
for kotu in ["ornek.com; echo x", "a && b", "$(id)", "`id`", "a|b", "-oProxy", "", "a b", "x" * 254, "ornek.com\n"]:
    raises(ValueError, ping_komutu, kotu, msg=f"reddedilmeli: {kotu[:20]!r}")
```

```solution
import re

GECERLI = re.compile(r"[A-Za-z0-9][A-Za-z0-9.-]{0,252}")

def ping_komutu(host):
    if not GECERLI.fullmatch(host):
        raise ValueError(f"geçersiz host: {host!r}")
    return ["ping", "-c", "1", host]
```

```hint
`re.fullmatch` kullan, `match` ya da `search` değil: tüm metin desene uymalı. Sondaki `\n` için de `fullmatch` güvenlidir (`$` değil).
```

```hint
Desen: ilk karakter harf/rakam, sonra 0–252 tane harf/rakam/nokta/tire: `[A-Za-z0-9][A-Za-z0-9.-]{0,252}`.
```
:::

::: gorev Hata raporu
`sonuc(kod)` fonksiyonu Python kodunu çocuk süreçte `check=True` ile çalıştırsın:

- Başarılıysa: `"tamam: <stdout>"` (kenar boşlukları temizlenmiş)
- Başarısızsa (`CalledProcessError`): `"hata <kod>: <stderr'in son boş olmayan satırı>"`

```starter
import subprocess, sys

def sonuc(kod):
    pass
```

```meta
timeout: 20
```

```test
need("sonuc")
eq(sonuc("print('selam')"), "tamam: selam", "başarılı")
eq(sonuc("1/0"), "hata 1: ZeroDivisionError: division by zero", "istisna → son satır")
eq(sonuc("import sys; sys.stderr.write('disk dolu\\n'); sys.exit(5)"), "hata 5: disk dolu", "özel kod ve mesaj")
ok(uses("try") and "check=True" in src.replace(" ", ""), "check=True ve try/except kullan")
```

```solution
import subprocess, sys

def sonuc(kod):
    try:
        r = subprocess.run([sys.executable, "-c", kod], capture_output=True, text=True,
                           check=True, timeout=10)
    except subprocess.CalledProcessError as e:
        satirlar = [s for s in e.stderr.splitlines() if s.strip()]
        return f"hata {e.returncode}: {satirlar[-1] if satirlar else ''}"
    return f"tamam: {r.stdout.strip()}"
```

```hint
`CalledProcessError` nesnesinin `returncode` ve (capture_output ile) `stderr` nitelikleri var.
```
:::
