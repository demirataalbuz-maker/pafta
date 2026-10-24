---
id: bs34
title: OpenSSH · Bağlanmadan Önce: Ayar ve Sunucu Kimliği
summary: ssh'ın hangi kullanıcı, adres, port ve anahtarla bağlanacağını bağlanmadan görmek (ssh -G); ssh_config'te ilk eşleşen değerin kazanması, joker Host blokları ve komut satırının önceliği; known_hosts, ssh-keygen -F ile (karma) kayıt aramak, -lf ile parmak izi ve StrictHostKeyChecking.
kazanim: LPIC1 105.2
backend: wsl
timeout: 60
---

::: anlat ssh nereye bağlanacak?
`ssh web-eski` yazdığında hangi kullanıcıyla, hangi adrese, hangi porta ve hangi anahtarla bağlanılacağını üç kaynak belirler: komut satırı (`-l`, `-p`, `-i`, `-o`), kullanıcının `~/.ssh/config` dosyası ve sistemin `/etc/ssh/ssh_config` dosyası. Bunları kafada birleştirmek hata kaynağıdır. `ssh -G hedef` **bağlanmadan** son hâli yazdırır: her ayar küçük harfle, satır başına bir tane.

```bash
ssh -G -F /dev/null -p 2222 -l ali ornek.test 2>/dev/null | grep -E '^(user|hostname|port) '
```

`-F dosya` yalnız o ayar dosyasını kullanır (`/dev/null` hiçbir ayar dosyası demektir). Bu derste ayarlar hep `-F` ile verilir; senin kendi `~/.ssh/config`'in karışmaz.

`ssh_config` dosyasının en çok yanlış okunan kuralı şudur: her ayar için **ilk bulunan değer kazanır**. Dosya yukarıdan aşağı okunur; hedefle eşleşen her `Host` bloğu uygulanır, ama daha önce değer almış bir ayar sonradan değişmez. Bu yüzden özel bloklar üstte, genel (`Host *`) bloklar en altta durur. Komut satırı her şeyden önce gelir.

| Yazım | Anlamı |
|---|---|
| `Host web-*` | `web-` ile başlayan her ad |
| `Host *.lab !db.lab` | `.lab` ile bitenler, `db.lab` hariç |
| `HostName 10.0.0.15` | gerçek adres; `Host` yalnız bir takma addır |
| `IdentityFile ~/.ssh/lab` | denenecek anahtar (birden çok olabilir, bu ayar birikir) |
| `IdentitiesOnly yes` | yalnız belirtilen anahtarları dene (ajanının hepsini değil) |

Kaynak: [ssh_config(5)](https://man.openbsd.org/ssh_config), [ssh(1), -G](https://man.openbsd.org/ssh#G).
:::

::: anlat Karşıdaki gerçekten o sunucu mu?
Her SSH sunucusunun bir **host anahtarı** vardır. İlk bağlantıda istemci bu anahtarın parmak izini gösterir ve kabul edilirse `known_hosts` dosyasına yazar; sonraki her bağlantıda karşılaştırır. Anahtar değişmişse `REMOTE HOST IDENTIFICATION HAS CHANGED` uyarısıyla bağlantıyı keser. Ya sunucu yeniden kuruldu ya da arada başka biri var; ikisini ayırmanın yolu parmak izini **ayrı bir kanaldan** (sunucunun yöneticisinden, yapılandırma yönetiminden) doğrulamaktır.

| Komut | Ne yapar |
|---|---|
| `ssh-keygen -lf anahtar.pub` | parmak izini yazar: `256 SHA256:... yorum (ED25519)` |
| `ssh-keygen -F ad -f known_hosts` | o ada ait kaydı bulur; bulamazsa 1 döner |
| `ssh-keygen -F '[ad]:2222' -f known_hosts` | 22 dışındaki port böyle yazılır |
| `ssh-keygen -H -f known_hosts` | adları karma (hash) hâline getirir: `\|1\|...` |
| `ssh-keygen -R ad -f known_hosts` | o adın kaydını siler |

Karma `known_hosts` satırlarında ad okunmaz (`|1|tuz|karma`), ama `ssh-keygen -F` adı aynı tuzla karıştırıp yine bulur. Dosyayı `grep` ile aramak bu yüzden yanıltır.

`StrictHostKeyChecking` ilk bağlantıdaki davranışı seçer: `yes` bilinmeyen anahtarı reddeder, `accept-new` bilinmeyeni kaydeder ama değişeni reddeder, `no` her şeyi kabul eder. Betiklerde `no` kullanmak, ortadaki adam saldırısına kapıyı açık bırakmaktır.

```bash
cd "$(mktemp -d)"
ssh-keygen -q -t ed25519 -N '' -f sunucu -C lab-sunucu
printf 'sunucu.lab %s\n' "$(cut -d' ' -f1,2 sunucu.pub)" > known_hosts
ssh-keygen -lf sunucu.pub | cut -d' ' -f1,4
ssh-keygen -F sunucu.lab -f known_hosts | head -1
ssh-keygen -F baska.lab -f known_hosts; echo "bulunamadı: $?"
```
:::

::: tahmin İlk eşleşen kazanır
```bash
cd "$(mktemp -d)"
cat > ayar <<'SON'
Host web-*
    User deploy
    Port 2201
Host web-eski
    User root
    HostName 10.0.0.15
Host *
    User nobody
SON
for h in web-yeni web-eski baska; do
    ssh -G -F ayar "$h" 2>/dev/null | awk '$1 == "user" || $1 == "hostname" || $1 == "port" { printf "%s ", $2 } END { print "" }'
done
```

???

```text
deploy web-yeni 2201 
deploy 10.0.0.15 2201 
nobody baska 22 
```

`ssh -G` ayarları kendi sabit sırasıyla yazar: bu üçünden önce `user`, sonra `hostname`, sonra `port`; `awk` onları geldikleri sırayla basar. `web-eski` iki bloğa uyar, ama `User` ve `Port` değerini ilk eşleşen `Host web-*` bloğu çoktan koymuştur; `User root` yok sayılır. `HostName`'i ise yalnız ikinci blok verir, o yüzden 10.0.0.15 gelir. `baska` yalnız `Host *`'a uyar ve port varsayılan 22'dir.
:::

::: gorev Bağlantı özeti
Çalışma klasöründe bir `ayar` dosyası (ssh_config) var. Girdinin her satırı bir hedef adıdır. Her hedef için ssh'ın **bağlanacağı** yeri `kullanici@adres:port` biçiminde, ardından bir boşluk ve denenecek **ilk** anahtar dosyasını yazdır:

```text
deploy@10.0.0.15:2201 ~/.ssh/web
```

- Değerleri `ayar` dosyasını kendin okuyarak değil, `ssh -G -F ayar` ile al.
- Boş satırları atla. Ad boşluk ya da `-` ile başlıyorsa o satır için `HATA` yazdır ve devam et; en sonda en az bir `HATA` olduysa **2** ile çık.

```stdin
web-eski
db.lab
```

```setup
import pathlib
pathlib.Path("ayar").write_text(
    "Host web-eski\n"
    "    HostName 10.0.0.15\n"
    "    User root\n"
    "Host web-*\n"
    "    User deploy\n"
    "    Port 2201\n"
    "    IdentityFile ~/.ssh/web\n"
    "Host *.lab !yedek.lab\n"
    "    Port 2222\n"
    "    IdentityFile ~/.ssh/lab\n"
    "Host *\n"
    "    User nobody\n"
    "    IdentityFile ~/.ssh/genel\n",
    encoding="utf-8", newline="\n")
```

```starter
while read -r hedef; do
    grep -A3 "Host $hedef" ayar
done
```

```test
eq(out, "root@10.0.0.15:2201 ~/.ssh/web\nnobody@db.lab:2222 ~/.ssh/lab\n",
   "web-eski: User üstteki bloktan root, Port ikinci bloktan; db.lab: *.lab bloğu")
eq(run(stdin="web-yeni\nyedek.lab\nbaska\n"),
   "deploy@web-yeni:2201 ~/.ssh/web\nnobody@yedek.lab:22 ~/.ssh/genel\nnobody@baska:22 ~/.ssh/genel\n",
   "joker blok, ! ile dışlanan ad ve yalnız Host * blokları")
eq(run(stdin="\nweb-yeni\n\n"), "deploy@web-yeni:2201 ~/.ssh/web\n", "boş satırlar atlanır")
r = calis(stdin="-oProxyCommand=x\nweb-yeni\n")
eq((r["kod"], r["cikti"]), (2, "HATA\ndeploy@web-yeni:2201 ~/.ssh/web\n"), "- ile başlayan ad seçenek olarak yorumlanmaz; diğerleri yine yazılır")
r = calis(stdin=" bosluk\n")
eq((r["kod"], r["cikti"]), (2, "HATA\n"), "boşlukla başlayan ad")
ok("-G" in src, "değerleri ssh -G ile al")
```

```solution
hata=0
while IFS= read -r hedef || [[ -n $hedef ]]; do
    [[ -z $hedef ]] && continue
    if [[ $hedef == [-[:space:]]* ]]; then
        echo HATA
        hata=1
        continue
    fi
    ssh -G -F ayar -- "$hedef" 2>/dev/null | awk '
        $1 == "user" { u = $2 }  $1 == "hostname" { h = $2 }  $1 == "port" { p = $2 }
        $1 == "identityfile" && i == "" { i = $2 }
        END { printf "%s@%s:%s %s\n", u, h, p, i }'
done
exit $(( hata ? 2 : 0 ))
```

```hint
`ssh -G -F ayar -- "$hedef"` çıktısından `user`, `hostname`, `port` ve ilk `identityfile` satırını `awk` ile topla. `--` adın seçenek sanılmasını önler.
```

```hint
`IdentityFile` birikir: birden çok satır gelebilir. İlkini al (`i == ""` iken ata). `IFS= read -r` satırı olduğu gibi okur; boşlukla başlayanları ayırt edebilmek için `IFS=` şart.
```
:::

::: gorev Sunucu anahtarını denetle
Çalışma klasöründe bir `known_hosts` dosyası ve `anahtarlar/` altında sunuculardan alınmış açık anahtarlar var. Girdinin her satırında bir **ad** (gerekirse `[ad]:port` biçiminde) ve bir **anahtar dosyası** bulunur. Her satır için tek bir sonuç yazdır:

- `eşleşti SHA256:...`: known_hosts'ta o ada ait kayıt var ve anahtar aynı;
- `değişti SHA256:...`: kayıt var ama anahtar farklı (sunucunun gönderdiği anahtarın parmak izini yaz);
- `bilinmiyor SHA256:...`: o ada ait kayıt yok.
- Anahtar dosyası yoksa ya da okunamıyorsa `HATA`; sona kadar devam et ve en az bir HATA olduysa **2** ile çık.

known_hosts'taki adların bir kısmı **karma** biçimdedir; `grep` ile değil `ssh-keygen -F` ile ara. Parmak izi `ssh-keygen -lf`'in ikinci alanıdır.

```stdin
web.lab anahtarlar/web.pub
db.lab anahtarlar/db_yeni.pub
```

```setup
import os, subprocess
os.makedirs("anahtarlar", exist_ok=True)
def uret(ad):
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", ad, "-f", f"anahtarlar/{ad}"], check=True)
    return open(f"anahtarlar/{ad}.pub").read().split()[:2]
web, db, db_yeni, git = uret("web"), uret("db"), uret("db_yeni"), uret("git")
with open("known_hosts", "w") as f:
    f.write(f"web.lab {' '.join(web)}\n")
    f.write(f"db.lab {' '.join(db)}\n")
    f.write(f"[git.lab]:2222 {' '.join(git)}\n")
subprocess.run(["ssh-keygen", "-q", "-H", "-f", "known_hosts"], check=True)
os.remove("known_hosts.old")
for ad in ("web", "db", "db_yeni", "git"):
    os.remove(f"anahtarlar/{ad}")
```

```starter
while read -r ad dosya; do
    if grep -q "$ad" known_hosts; then echo eşleşti; else echo bilinmiyor; fi
done
```

```test
import subprocess
def iz(dosya):
    return subprocess.run(["ssh-keygen", "-lf", dosya], capture_output=True, text=True).stdout.split()[1]
ok(all(s.startswith("|1|") for s in open("known_hosts").read().split("\n") if s), "hazırlık: bütün adlar karma")
eq(out, f"eşleşti {iz('anahtarlar/web.pub')}\ndeğişti {iz('anahtarlar/db_yeni.pub')}\n", "aynı anahtar ve değişmiş anahtar")
eq(run(stdin="[git.lab]:2222 anahtarlar/git.pub\ngit.lab anahtarlar/git.pub\n"),
   f"eşleşti {iz('anahtarlar/git.pub')}\nbilinmiyor {iz('anahtarlar/git.pub')}\n", "port 2222 kaydı yalnız [ad]:port ile bulunur")
eq(run(stdin="yeni.lab anahtarlar/web.pub\n"), f"bilinmiyor {iz('anahtarlar/web.pub')}\n", "kaydı olmayan ad")
eq(run(stdin="web.lab anahtarlar/db.pub\n"), f"değişti {iz('anahtarlar/db.pub')}\n", "başka sunucunun anahtarı")
r = calis(stdin="web.lab anahtarlar/yok.pub\ndb.lab anahtarlar/db.pub\n")
eq((r["kod"], r["cikti"]), (2, f"HATA\neşleşti {iz('anahtarlar/db.pub')}\n"), "olmayan anahtar dosyası; sonraki satır yine işlenir")
open("bozuk.pub", "w").write("bu bir anahtar değil\n")
r = calis(stdin="web.lab bozuk.pub\n")
eq((r["kod"], r["cikti"]), (2, "HATA\n"), "okunamayan anahtar")
```

```solution
hata=0
while read -r ad dosya || [[ -n $ad ]]; do
    [[ -z $ad ]] && continue
    if ! iz=$(ssh-keygen -lf "$dosya" 2>/dev/null) || [[ -z $iz ]]; then
        echo HATA
        hata=1
        continue
    fi
    iz=$(cut -d' ' -f2 <<< "$iz")
    gonderilen=$(cut -d' ' -f1,2 "$dosya")
    kayitlar=$(ssh-keygen -F "$ad" -f known_hosts 2>/dev/null | grep -v '^#' | cut -d' ' -f2,3)
    if [[ -z $kayitlar ]]; then
        echo "bilinmiyor $iz"
    elif grep -qxF "$gonderilen" <<< "$kayitlar"; then
        echo "eşleşti $iz"
    else
        echo "değişti $iz"
    fi
done
exit $(( hata ? 2 : 0 ))
```

```hint
`ssh-keygen -F "$ad" -f known_hosts` bulduğu satırları yazar (başında `#` olan bir bilgi satırıyla). Kayıt satırında ikinci ve üçüncü alan `tür anahtar`'dır; anahtar dosyasının ilk iki alanıyla birebir karşılaştır.
```

```hint
Parmak izi için `ssh-keygen -lf dosya`; başarısızsa (dosya yok, anahtar değil) 0 dışı döner. Port 22 değilse ad `[git.lab]:2222` olarak aranır; `git.lab` aynı kayıt değildir.
```
:::
