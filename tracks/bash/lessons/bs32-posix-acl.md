---
id: bs32
title: POSIX ACL · rwx'in Ötesindeki Yetki
summary: ls -l'deki + işaretinin arkası: getfacl ve setfacl ile adlı kullanıcı/grup girdileri, maske ve #effective, erişim denetiminin sırası, chmod'un ACL'li dosyada maskeyi değiştirmesi, varsayılan (default) ACL ile kalıtım ve umask'ın devre dışı kalması; sonuçları root'suz bir kullanıcı ad alanında ikinci bir kimlikle gerçek erişimle doğrulamak.
kazanim: LPIC1 104.5
backend: wsl
timeout: 90
---

::: anlat Dokuz bitin yetmediği yer
BS17'de bir dosyanın yetkisini dokuz bitle okudun: sahip, grup, diğerleri için `rwx`. Gerçek sunucularda bu yetmez: "bu rapor dosyasını **yalnız** `yedek` kullanıcısı da okuyabilsin, grubu değiştirmeden" demek dokuz bitle mümkün değildir. Linux bunun için **POSIX ACL** (erişim denetim listesi) kullanır. Bir dosyada ACL varsa `ls -l` yetki dizisinin sonuna `+` koyar; dokuz bit artık bütün hikâyeyi anlatmaz.

| Girdi | Anlamı |
|---|---|
| `user::rw-` | sahip (dokuz bitin ilk üçlüsü) |
| `user:1000:r--` | **adlı kullanıcı**: UID 1000 |
| `group::r--` | dosyanın grubu |
| `group:50:r--` | **adlı grup** |
| `mask::r--` | adlı kullanıcıların, grubun ve adlı grupların **en fazla** alabileceği yetki |
| `other::---` | diğerleri |

`setfacl -m u:1000:rw dosya` bir girdi ekler ya da değiştirir, `setfacl -x u:1000 dosya` siler, `setfacl -b dosya` bütün ACL'yi kaldırır. `getfacl -n` adlar yerine sayısal kimlik gösterir; `--omit-header` baştaki `# file` satırlarını atar.

**Maske** ACL'nin en çok yanlış okunan parçasıdır. Adlı bir kullanıcıya `rw-` verilmiş olabilir, ama maske `r--` ise etkili yetkisi `r--`'dir. `getfacl` bu durumda satırın sonuna `#effective:` yazar. Sahibe ve diğerlerine maske uygulanmaz.

Çekirdek bir erişimi şu **sırayla** denetler ve ilk eşleşen girdide durur:

1. Süreç dosyanın sahibiyse: `user::`.
2. Adlı bir `user:UID:` girdisi süreçle eşleşiyorsa: o girdi **ve maske**.
3. Süreç dosyanın grubunda ya da adlı bir grupta ise: o girdiler **ve maske** (biri yeterliyse izin).
4. Hiçbiri değilse: `other::`.

Sıra önemlidir: adlı kullanıcı girdisi olan biri `other::r--` olsa bile, kendi girdisi `---` ise okuyamaz. Diğerlerine verilen yetki ondan geri alınmış olur.

> [!GÜVENLİK]
> ACL'li bir dosyada `chmod g+w` grup bitlerini değil **maskeyi** değiştirir. Maskeyi bilerek `r--`'ye çektiğin bir dosyada sonradan yapılan sıradan bir `chmod g+w`, bütün adlı kullanıcılara ve gruplara sessizce yazma yetkisi açar. `ls -l`'deki ortadaki üçlü, ACL varken grubun değil maskenin yetkisidir.

Kaynak: [acl(5): erişim denetim algoritması](https://man7.org/linux/man-pages/man5/acl.5.html), [setfacl(1)](https://man7.org/linux/man-pages/man1/setfacl.1.html).
:::

::: anlat Kalıtım ve ikinci bir kimlikle sınamak
Bir klasöre **varsayılan (default) ACL** konabilir: `setfacl -d -m u:1000:rw klasor`. Varsayılan girdiler klasörün kendi erişimini değiştirmez; klasörde **sonradan açılan** her dosya ve alt klasör bu girdileri kendi ACL'si olarak alır. Önemli bir ayrıntı: klasörde varsayılan ACL varsa yeni dosyaya **umask uygulanmaz**. `umask 077` ile açılan dosya da varsayılan ACL'deki adlı kullanıcıya yetki verir; yalnızca dosyayı açan programın istediği kip (`touch` için `rw-rw-rw-`) maskeyi sınırlar.

Klasörlerde `x` "içine girebilmek" demektir. Bir dosyanın ACL'si ne derse desin, yolundaki klasörlerden birinde `x` yoksa dosyaya ulaşılamaz. ACL denetiminde ilk bakılacak yer çoğu zaman dosya değil, yolun kendisidir.

Bir ACL'nin gerçekten ne yaptığını görmenin tek yolu **o kimlikle** erişmeyi denemektir. Bu tezgahta root yetkin yok; bunun yerine root gerektirmeyen bir **kullanıcı ad alanı** kurulur: `unshare --map-auto --map-root-user` içinde sen UID 0 görünürsün (yalnız bu ad alanında), alt UID aralığından gelen 1000 ve 1001 ise ayrı kullanıcılardır. `setpriv --reuid=1000 --regid=1000 --clear-groups komut` bir komutu o kimlikle çalıştırır:

```bash
cd "$(mktemp -d)"
chmod 711 .
echo gizli > rapor.txt
chmod 640 rapor.txt
unshare --map-auto --map-root-user bash -c '
    olarak() { setpriv --reuid="$1" --regid="$1" --clear-groups "${@:2}" 2>&1; echo "çıkış=$?"; }
    olarak 1000 cat rapor.txt
    setfacl -m u:1000:r rapor.txt
    olarak 1000 cat rapor.txt
    olarak 1001 cat rapor.txt
    setfacl -m m::--- rapor.txt
    olarak 1000 cat rapor.txt
    getfacl -n --omit-header rapor.txt
'
```

`chmod 711 .` olmasaydı çalışma klasörü 700 kalırdı ve 1000 ne verirsen ver dosyaya ulaşamazdı. Ad alanındaki "root" ise ayrıcalıklıdır: sahip denetimini `CAP_DAC_OVERRIDE` ile aşar. Bu yüzden yetkileri **hep 1000 ve 1001 ile** sınarız.
:::

::: tahmin Maske adlı kullanıcıyı ne kadar sınırlar?
```bash
cd "$(mktemp -d)"
echo gizli > f
chmod 640 f
setfacl -m u:1000:rw f
setfacl -m m::r f
getfacl -n --omit-header f
ls -l f | cut -c1-11
```

???

```text
user::rw-
user:1000:rw-	#effective:r--
group::r--
mask::r--
other::---

-rw-r-----+
```

`user:1000` girdisinde `rw-` yazılı ama maske `r--` olduğu için etkili yetkisi `r--`'dir; `getfacl` bunu `#effective:` ile gösterir. Grubun etkili yetkisi zaten `r--` olduğundan onun satırında not yoktur. `ls -l`'in ortadaki üçlüsü `r--` maskedir ve sondaki `+` ACL olduğunu söyler. `getfacl` girdileri bir boş satırla bitirir.
:::

::: gorev Adlı kullanıcının etkili yetkisi
Girdinin tek satırında bir dosya yolu ve bir UID var: `rapor.txt 1000`. O dosyada bu UID için bir **adlı kullanıcı girdisi** varsa, maskeyle sınırlanmış **etkili** yetkisini `rwx` biçiminde yazdır (örneğin `r--`). Girdi yoksa `yok` yazdır.

- Dosya yoksa standart hataya bir ileti yaz ve **2** ile çık.
- UID sayı değilse ya da satır eksikse `HATA` yazdır ve **2** ile çık.
- Etkili yetkiyi `getfacl`'in `#effective` notuna bakmadan, girdiyi ve maskeyi kendin karşılaştırarak bul (`getfacl` notu yalnız fark olduğunda yazar).

Testler betiğini kullanıcı ad alanında da çalıştırır ve bulduğun yetkiyi 1000 kimliğiyle gerçek okuma/yazma denemesiyle karşılaştırır.

```stdin
rapor.txt 1000
```

```setup
import os, subprocess
open("rapor.txt", "w").write("gizli\n")
os.chmod("rapor.txt", 0o640)
subprocess.run(["setfacl", "-m", "u:1000:rw,m::r", "rapor.txt"], check=True)
open("duz.txt", "w").write("acl yok\n")
```

```starter
read -r dosya uid
getfacl -n "$dosya" | grep "user:$uid:"
```

```test
import os, subprocess
def ns(komut):
    r = subprocess.run(["unshare", "--map-auto", "--map-root-user", "bash", "-c", komut], capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr
eq(out, "r--\n", "rw- girdisi, r-- maske: etkili r--")
eq(run(stdin="duz.txt 1000\n"), "yok\n", "ACL'siz dosya")
eq(run(stdin="rapor.txt 1001\n"), "yok\n", "başka UID'nin girdisi yok")
r = calis(stdin="olmayan.txt 1000\n")
ok(r["kod"] == 2 and r["hata"].strip() and not r["cikti"], "olmayan dosya: stderr ve çıkış 2", got=r)
for kotu in ("rapor.txt abc\n", "rapor.txt\n", "\n", "rapor.txt -5\n"):
    r = calis(stdin=kotu)
    eq((r["kod"], r["cikti"]), (2, "HATA\n"), f"hatalı girdi: {kotu!r}")
deneme = '''
d=$PWD; while [ "$d" != / ]; do chmod o+x "$d" 2>/dev/null; d=$(dirname "$d"); done
olarak() { setpriv --reuid=1000 --regid=1000 --clear-groups "$@" >/dev/null 2>&1 && echo E || echo H; }
for kurulum in "u:1000:rw,m::r" "u:1000:rw,m::rw" "u:1000:r,m::rwx" "u:1000:rw,m::-" "u:1000:-,m::rw" "u:1001:rw,m::rw" "u:1000:rwx,m::wx"; do
    printf 'x\\n' > lab.txt; chmod 600 lab.txt; setfacl -b lab.txt; setfacl -m "$kurulum" lab.txt
    bulunan=$(bash betik.sh <<< "lab.txt 1000")
    okur=$(olarak cat lab.txt); yazar=$(olarak sh -c 'echo y >> lab.txt')
    echo "$kurulum $bulunan $okur$yazar"
done
'''
kod, cikti, hata = ns(deneme)
eq(cikti, "u:1000:rw,m::r r-- EH\nu:1000:rw,m::rw rw- EE\nu:1000:r,m::rwx r-- EH\nu:1000:rw,m::- --- HH\n"
          "u:1000:-,m::rw --- HH\nu:1001:rw,m::rw yok HH\nu:1000:rwx,m::wx -wx HE\n",
   "ad alanında: bulunan yetki 1000'in gerçek okuma (E/H) ve yazma (E/H) sonucuyla tutarlı")
```

```solution
read -r dosya uid extra || true
if [[ -z $dosya || ! $uid =~ ^[0-9]+$ ]]; then
    echo HATA
    exit 2
fi
if [[ ! -e $dosya ]]; then
    echo "dosya yok: $dosya" >&2
    exit 2
fi
acl=$(getfacl -n --omit-header "$dosya" 2>/dev/null)
girdi=$(awk -F: -v u="$uid" '$1 == "user" && $2 == u { split($3, a, "\t"); print a[1] }' <<< "$acl")
maske=$(awk -F: '$1 == "mask" { split($3, a, "\t"); print a[1] }' <<< "$acl")
if [[ -z $girdi ]]; then
    echo yok
    exit 0
fi
sonuc=""
for i in 0 1 2; do
    g=${girdi:i:1}
    m=${maske:i:1}
    if [[ $g != - && $m == "$g" ]]; then sonuc+=$g; else sonuc+=-; fi
done
echo "$sonuc"
```

```hint
`getfacl -n --omit-header dosya` satırları `tür:kimlik:yetki` biçimindedir; `#effective` notu bir sekmeden sonra gelir. `awk -F:` ile `$1 == "user" && $2 == uid` olan satırın üçüncü alanını al, sekmeden sonrasını at.
```

```hint
Etkili yetki harf harf kesişimdir: girdide ve maskede aynı konumda aynı harf varsa o harf, yoksa `-`. Adlı kullanıcı girdisi varken ACL'de her zaman bir maske de bulunur.
```
:::

::: gorev Paylaşılan klasör
Girdinin tek satırında bir klasör ve bir UID var: `ortak 1000`. Klasörü öyle ayarla ki:

- Bu UID klasöre girebilsin, içindekileri listeleyebilsin ve içinde dosya açabilsin;
- klasörde **bundan sonra kim açarsa açsın** her dosyayı bu UID okuyup yazabilsin (umask ne olursa olsun);
- **diğerleri** (`other`) klasöre ve içindeki yeni dosyalara hiçbir yetki almasın;
- klasörün sahibi ve grubu değişmesin.

Klasör yoksa standart hataya bir ileti yaz ve **2** ile çık; UID sayı değilse ya da satır eksikse `HATA` yazdır ve **2** ile çık. Başarıda hiçbir şey yazdırma.

Testler betiğini kullanıcı ad alanında çalıştırır, ardından sahip olarak `umask 077` ile dosya açar ve 1000 ile 1001 kimliklerinin gerçek erişimini dener.

```stdin
ortak 1000
```

```setup
import os
os.mkdir("ortak")
os.chmod("ortak", 0o750)
```

```starter
read -r klasor uid
chmod 777 "$klasor"
```

```test
import subprocess
def ns(komut):
    r = subprocess.run(["unshare", "--map-auto", "--map-root-user", "bash", "-c", komut], capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr
r = calis(stdin="olmayan 1000\n")
ok(r["kod"] == 2 and r["hata"].strip() and not r["cikti"], "olmayan klasör: stderr ve çıkış 2", got=r)
for kotu in ("ortak x\n", "ortak\n", "\n"):
    r = calis(stdin=kotu)
    eq((r["kod"], r["cikti"]), (2, "HATA\n"), f"hatalı girdi: {kotu!r}")
deneme = '''
d=$PWD; while [ "$d" != / ]; do chmod o+x "$d" 2>/dev/null; d=$(dirname "$d"); done
rm -rf lab; mkdir lab; chmod 750 lab
cikti=$(bash betik.sh <<< "lab 1000"); echo "kod=$? cikti=[$cikti]"
olarak() { u=$1; shift; setpriv --reuid="$u" --regid="$u" --clear-groups "$@" >/dev/null 2>&1 && echo E || echo H; }
umask 077
echo sahip > lab/sahibin.txt
mkdir lab/alt; echo derin > lab/alt/derin.txt
echo "1000: liste=$(olarak 1000 ls lab) oku=$(olarak 1000 cat lab/sahibin.txt) yaz=$(olarak 1000 sh -c 'echo y >> lab/sahibin.txt') ac=$(olarak 1000 sh -c 'echo z > lab/bin.txt') derin=$(olarak 1000 cat lab/alt/derin.txt)"
echo "1001: liste=$(olarak 1001 ls lab) oku=$(olarak 1001 cat lab/sahibin.txt)"
stat -c "%U:%G %A" lab | cut -c1-14
getfacl -n --omit-header lab/sahibin.txt | grep -E "^other"
'''
kod, cikti, hata = ns(deneme)
eq(cikti, "kod=0 cikti=[]\n"
          "1000: liste=E oku=E yaz=E ac=E derin=E\n"
          "1001: liste=H oku=H\n"
          "root:root drwx\n"
          "other::---\n",
   "1000 her şeye, alt klasördeki yeni dosyaya da erişir; 1001 erişemez; diğerleri ---; sahip ve grup aynı")
ok(not hata.strip(), "ad alanındaki deneme hatasız", got=hata)
```

```solution
read -r klasor uid extra || true
if [[ -z $klasor || ! $uid =~ ^[0-9]+$ ]]; then
    echo HATA
    exit 2
fi
if [[ ! -d $klasor ]]; then
    echo "klasör yok: $klasor" >&2
    exit 2
fi
chmod o-rwx "$klasor"
setfacl -m "u:$uid:rwx" "$klasor"
setfacl -d -m "u:$uid:rwx,u::rwx,o::-" "$klasor"
```

```hint
İki ayrı ACL gerekir: klasörün kendi erişimi için `setfacl -m u:UID:rwx` (girmek, listelemek, dosya açmak) ve yeni dosyalar için varsayılan ACL `setfacl -d -m u:UID:rwx`.
```

```hint
Varsayılan ACL'de `o::-` diğerlerini kapatır; `u::rwx` sahibin kendi açtığı alt klasöre girebilmesini sağlar. Varsayılan ACL varken umask uygulanmaz, bu yüzden `umask 077` 1000'i dışarıda bırakmaz.
```
:::
