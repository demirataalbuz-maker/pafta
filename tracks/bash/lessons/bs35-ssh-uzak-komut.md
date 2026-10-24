---
id: bs35
title: OpenSSH · Uzak Komut ve Dosya Akışı
summary: Ayrılmış bir yerel laboratuvar uç noktasında (sshd -i, ProxyCommand) ssh ile uzak komut çalıştırmak; uzak stdout/stderr ve çıkış kodunun yerel komuta geçişi, 255'in iki anlamı ve çıkış kodunu bant içinde taşımak; uzak kabuğun alıntılamayı ikinci kez yorumlaması ve komutu stdin'den göndermek; scp ve sftp -b ile dosya aktarımı, çıkış kodları ve uzakta sha256 ile doğrulama.
kazanim: LPIC1 105.2, LPIC1 103.4, LPIC1 103.2
backend: wsl
timeout: 90
---

::: anlat Laboratuvar uç noktası
Bu derste gerçek bir OpenSSH sunucusuna bağlanacaksın, ama ağa bir port açılmaz ve arkada çalışan bir sunucu kalmaz. Her derste hazırlık, çalışma klasöründe şunları üretir:

| Dosya | Ne |
|---|---|
| `host_ed25519` | laboratuvar sunucusunun host anahtarı |
| `id_lab` | senin istemci anahtarın (parolasız, yalnız bu laboratuvar için) |
| `authorized_keys` | sunucunun kabul ettiği açık anahtarlar |
| `sshd_config` | sunucu ayarı: yalnız anahtarla giriş, SFTP alt sistemi |
| `known_hosts` | `lab` adının host anahtarı (önceden doğrulanmış) |
| `ayar` | istemci ayarı: `Host lab` bloğu |

`ayar` içindeki `ProxyCommand /usr/sbin/sshd -i -f .../sshd_config` satırı işin püf noktasıdır: ssh bir TCP bağlantısı açmak yerine bu komutu başlatır ve onunla stdin/stdout üzerinden konuşur. `sshd -i` (inetd kipi) tek bir bağlantıya hizmet edip çıkar. Böylece her `ssh -F ayar lab` gerçek bir SSH el sıkışması, host anahtarı doğrulaması ve anahtarla kimlik doğrulaması yapar; bağlantı bitince sunucu süreci de biter. Uzak taraf aynı makinedeki aynı kullanıcıdır; bu yüzden "uzak" yollar çalışma klasörünün içindedir.

Kaynak: [sshd(8), -i](https://man.openbsd.org/sshd#i), [ssh_config(5), ProxyCommand](https://man.openbsd.org/ssh_config#ProxyCommand).
:::

::: anlat Uzak komutun çıktısı ve çıkış kodu
`ssh hedef komut` komutu uzakta çalıştırır; uzak **stdout** yerel stdout'a, uzak **stderr** yerel stderr'e gelir ve uzak komutun **çıkış kodu** `ssh`'ın çıkış kodu olur. Bir istisna dışında: `ssh`'ın kendisi başarısız olursa (bağlanamazsa, host anahtarı tutmazsa, kimlik doğrulanamazsa) **255** döner. Uzak komut da 255 ile çıkabildiği için tek başına `$?` ikisini ayıramaz.

| Durum | `ssh`'ın çıkış kodu |
|---|---|
| uzak komut 0 ile bitti | 0 |
| uzak komut 7 ile bitti | 7 |
| uzak komut 255 ile bitti | 255 |
| host anahtarı tutmadı, bağlanılamadı | 255 |

İkinci tuzak **alıntılamadır**. `ssh lab 'echo "$HOME"'` yazdığında yerel kabuk tek tırnakları açar ve uzağa `echo "$HOME"` metnini gönderir; uzaktaki kabuk bu metni **ikinci kez** yorumlar. Komutu birkaç argüman olarak verirsen ssh onları boşlukla birleştirip tek bir metin yapar: `ssh lab echo "a  b"` uzakta `echo a  b` olur ve iki boşluk tek boşluğa iner. Bir betikte kullanıcıdan gelen bir komutu ya da yolu uzağa güvenle taşımanın yolu, onu **komut satırına değil stdin'e** koymaktır:

```bash
ssh -F ayar lab 'sh -c "$(cat)"' <<< 'echo "a  b"; exit 3'; echo "çıkış=$?"
```

Uzaktaki sabit kısım (`sh -c "$(cat)"`) stdin'den gelen metni bir kez, olduğu gibi çalıştırır. Aynı kalıp uzak bir yolu da taşır: `ssh lab 'sha256sum -- "$(cat)"' <<< "$yol"`.

```bash
ssh -F ayar lab 'echo standart; echo hata >&2; exit 7' 2>hata.txt
echo "çıkış=$?"; echo "stderr: $(cat hata.txt)"
```

```setup
import os, subprocess
L = os.getcwd()
for ad in ("host_ed25519", "id_lab"):
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", ad, "-f", ad], check=True)
os.replace("id_lab.pub", "authorized_keys"); os.chmod("authorized_keys", 0o600)
open("sshd_config", "w").write(f"HostKey {L}/host_ed25519\nAuthorizedKeysFile {L}/authorized_keys\nPasswordAuthentication no\n"
    "KbdInteractiveAuthentication no\nUsePAM no\nStrictModes no\nPidFile none\nSubsystem sftp internal-sftp\nLogLevel ERROR\n")
open("known_hosts", "w").write("lab " + " ".join(open("host_ed25519.pub").read().split()[:2]) + "\n")
kullanici = subprocess.run(["id", "-un"], capture_output=True, text=True).stdout.strip()
open("ayar", "w").write(f"Host lab\n    HostName lab\n    User {kullanici}\n    IdentityFile {L}/id_lab\n    IdentitiesOnly yes\n"
    f"    UserKnownHostsFile {L}/known_hosts\n    StrictHostKeyChecking yes\n    ProxyCommand /usr/sbin/sshd -i -f {L}/sshd_config\n    LogLevel ERROR\n")
```
:::

::: anlat Dosya aktarımı
| Komut | Ne yapar | Çıkış kodu |
|---|---|---|
| `scp yerel lab:/yol/` | dosyayı uzağa kopyalar | başarı 0; uzak klasör yok ya da yazılamıyor 1; bağlantı hatası 255 |
| `scp lab:/yol/dosya .` | uzaktan yerele | aynı |
| `sftp -b komutlar lab` | `put`, `get`, `ls`, `mkdir` gibi komutları toplu çalıştırır | herhangi bir komut başarısızsa 0 dışı |

OpenSSH 9'dan beri `scp` arka planda **SFTP protokolünü** kullanır; bu yüzden sunucuda `Subsystem sftp` tanımlı olmalıdır (laboratuvarın `sshd_config`'inde var) ve uzak yollar artık uzak kabukta genişletilmez: adında boşluk olan bir yol ek alıntı gerektirmez. Bir aktarımın başarılı olması dosyanın **doğru** geldiğini kanıtlamaz; önemli dosyalarda iki taraftaki özet (`sha256sum`) karşılaştırılır.

```bash
echo içerik > "yerel dosya.txt"
mkdir -p "uzak klasör"
scp -F ayar -q "yerel dosya.txt" "lab:$PWD/uzak klasör/"; echo "scp=$?"
printf 'ls "%s/uzak klasör"\n' "$PWD" | sftp -F ayar -q -b - lab
ssh -F ayar lab 'sha256sum -- "$(cat)"' <<< "$PWD/uzak klasör/yerel dosya.txt" | cut -c1-16
```

```setup
import os, subprocess
L = os.getcwd()
for ad in ("host_ed25519", "id_lab"):
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", ad, "-f", ad], check=True)
os.replace("id_lab.pub", "authorized_keys"); os.chmod("authorized_keys", 0o600)
open("sshd_config", "w").write(f"HostKey {L}/host_ed25519\nAuthorizedKeysFile {L}/authorized_keys\nPasswordAuthentication no\n"
    "KbdInteractiveAuthentication no\nUsePAM no\nStrictModes no\nPidFile none\nSubsystem sftp internal-sftp\nLogLevel ERROR\n")
open("known_hosts", "w").write("lab " + " ".join(open("host_ed25519.pub").read().split()[:2]) + "\n")
kullanici = subprocess.run(["id", "-un"], capture_output=True, text=True).stdout.strip()
open("ayar", "w").write(f"Host lab\n    HostName lab\n    User {kullanici}\n    IdentityFile {L}/id_lab\n    IdentitiesOnly yes\n"
    f"    UserKnownHostsFile {L}/known_hosts\n    StrictHostKeyChecking yes\n    ProxyCommand /usr/sbin/sshd -i -f {L}/sshd_config\n    LogLevel ERROR\n")
```
:::

::: tahmin Çıkış kodları nereden geliyor?
```bash
ssh -F ayar lab 'exit 7'; echo "a=$?"
ssh -F ayar lab 'sh -c "$(cat)"' <<< 'echo "x  y"'; echo "b=$?"
ssh -F ayar lab echo "x  y"; echo "c=$?"
cp known_hosts yedek; echo "lab $(cut -d' ' -f1,2 authorized_keys)" > known_hosts
ssh -F ayar lab true 2>/dev/null; echo "d=$?"
mv yedek known_hosts
```

```setup
import os, subprocess
L = os.getcwd()
for ad in ("host_ed25519", "id_lab"):
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", ad, "-f", ad], check=True)
os.replace("id_lab.pub", "authorized_keys"); os.chmod("authorized_keys", 0o600)
open("sshd_config", "w").write(f"HostKey {L}/host_ed25519\nAuthorizedKeysFile {L}/authorized_keys\nPasswordAuthentication no\n"
    "KbdInteractiveAuthentication no\nUsePAM no\nStrictModes no\nPidFile none\nSubsystem sftp internal-sftp\nLogLevel ERROR\n")
open("known_hosts", "w").write("lab " + " ".join(open("host_ed25519.pub").read().split()[:2]) + "\n")
kullanici = subprocess.run(["id", "-un"], capture_output=True, text=True).stdout.strip()
open("ayar", "w").write(f"Host lab\n    HostName lab\n    User {kullanici}\n    IdentityFile {L}/id_lab\n    IdentitiesOnly yes\n"
    f"    UserKnownHostsFile {L}/known_hosts\n    StrictHostKeyChecking yes\n    ProxyCommand /usr/sbin/sshd -i -f {L}/sshd_config\n    LogLevel ERROR\n")
```

???

```text
a=7
x  y
b=0
x y
c=0
d=255
```

`a`: uzak komutun kodu ssh'ın kodu olur. `b`: komut stdin'den gidip uzakta bir kez yorumlandığı için iki boşluk korunur. `c`: ssh argümanları boşlukla birleştirip uzağa `echo x  y` gönderir; uzak kabuk onu iki argümana böler ve boşluklar tek boşluğa iner. `d`: `known_hosts`'taki anahtar sunucununki değil; ssh bağlanmayı reddeder ve kendi hatası için 255 döner. Uzak bir komut da 255 dönebilseydi, `d`'ye bakarak ikisini ayıramazdın.
:::

::: gorev Kesin çıkış kodu
Girdinin tek satırı uzakta çalıştırılacak bir kabuk komutudur. Onu laboratuvarda (`ssh -F ayar lab`) çalıştır ve:

- uzak komutun **stdout**'unu olduğu gibi yazdır (son satırı yeni satırla bitmiyorsa sonuna yeni satır ekle);
- ardından `uzak: <kod>` satırını yazdır: uzak komutun gerçek çıkış kodu, **255 dahil**;
- uzak stderr yerel stderr'e gitsin;
- komut uzakta hiç çalışamadıysa (ssh'ın kendisi başarısız olduysa) yalnız `ssh: hata` yazdır ve **255** ile çık; komut çalıştıysa kodu ne olursa olsun **0** ile çık.
- Boş satır ya da girdi yoksa `HATA` yazdır ve **2** ile çık.

Komut tırnak, `$` ve `;` içerebilir; uzakta **bir kez**, yazıldığı gibi yorumlanmalı.

```stdin
echo merhaba; exit 7
```

```setup
import os, subprocess
L = os.getcwd()
for ad in ("host_ed25519", "id_lab"):
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", ad, "-f", ad], check=True)
os.replace("id_lab.pub", "authorized_keys"); os.chmod("authorized_keys", 0o600)
open("sshd_config", "w").write(f"HostKey {L}/host_ed25519\nAuthorizedKeysFile {L}/authorized_keys\nPasswordAuthentication no\n"
    "KbdInteractiveAuthentication no\nUsePAM no\nStrictModes no\nPidFile none\nSubsystem sftp internal-sftp\nLogLevel ERROR\n")
open("known_hosts", "w").write("lab " + " ".join(open("host_ed25519.pub").read().split()[:2]) + "\n")
kullanici = subprocess.run(["id", "-un"], capture_output=True, text=True).stdout.strip()
open("ayar", "w").write(f"Host lab\n    HostName lab\n    User {kullanici}\n    IdentityFile {L}/id_lab\n    IdentitiesOnly yes\n"
    f"    UserKnownHostsFile {L}/known_hosts\n    StrictHostKeyChecking yes\n    ProxyCommand /usr/sbin/sshd -i -f {L}/sshd_config\n    LogLevel ERROR\n")
```

```starter
read -r komut
ssh -F ayar lab "$komut"
echo "uzak: $?"
```

```test
import os, subprocess
eq(out, "merhaba\nuzak: 7\n", "uzak çıktı ve kod 7")
eq(run(stdin="true\n"), "uzak: 0\n", "çıktısız başarılı komut")
eq(run(stdin="echo son; exit 255\n"), "son\nuzak: 255\n", "uzak komutun kendi 255'i ssh hatasından ayrılır")
eq(run(stdin='printf "%s|%s\\n" "a  b" "$((2 + 3))"\n'), "a  b|5\nuzak: 0\n", "tırnak ve $ uzakta bir kez yorumlanır")
eq(run(stdin="printf abc\n"), "abc\nuzak: 0\n", "yeni satırla bitmeyen çıktı")
eq(run(stdin="echo bir; echo; echo iki\n"), "bir\n\niki\nuzak: 0\n", "çıktının içindeki boş satır korunur")
r = calis(stdin="echo dışarı; echo içeri >&2; exit 4\n")
eq((r["kod"], r["cikti"], r["hata"].strip()), (0, "dışarı\nuzak: 4\n", "içeri"), "stderr ayrı akar; komut çalıştıysa betik 0 döner")
os.replace("known_hosts", "known_hosts.dogru")
open("known_hosts", "w").write("lab " + " ".join(open("authorized_keys").read().split()[:2]) + "\n")
r = calis(stdin="echo olmamalı\n")
os.replace("known_hosts.dogru", "known_hosts")
eq((r["kod"], r["cikti"]), (255, "ssh: hata\n"), "host anahtarı tutmazsa komut hiç çalışmaz: ssh: hata, 255")
r = calis(stdin="\n")
eq((r["kod"], r["cikti"]), (2, "HATA\n"), "boş satır")
r = calis(stdin="")
eq((r["kod"], r["cikti"]), (2, "HATA\n"), "girdi yok")
```

```solution
IFS= read -r komut || true
if [[ -z $komut ]]; then
    echo HATA
    exit 2
fi
cikti=$(ssh -F ayar lab 'sh -c "$(cat)"; k=$?; printf "\n__kod=%s\n" "$k"' <<< "$komut"; printf x)
cikti=${cikti%x}
if [[ ! $cikti =~ $'\n'__kod=([0-9]+)$'\n'$ ]]; then
    echo "ssh: hata"
    exit 255
fi
kod=${BASH_REMATCH[1]}
govde=${cikti%$'\n'__kod=*}
if [[ -n $govde ]]; then
    printf '%s' "$govde"
    [[ $govde == *$'\n' ]] || echo
fi
echo "uzak: $kod"
```

```hint
Kodu bant içinde taşı: uzakta `sh -c "$(cat)"; k=$?; printf "\n__kod=%s\n" "$k"` çalıştır ve komutu stdin'den gönder (`<<< "$komut"`). İşaretçi satırı gelmediyse komut uzakta hiç çalışmamıştır.
```

```hint
`$(...)` sondaki yeni satırları yer; korumak için sonuna `printf x` ekleyip sonra `${cikti%x}` ile at. İşaretçiden önceki gövde `${cikti%$'\n'__kod=*}`'dır; işaretçiden önce eklediğin `\n` böylece gider.
```
:::

::: gorev Gönder ve uzakta doğrula
Girdinin tek satırında, sekmeyle ayrılmış iki alan var: **yerel dosya** ve **uzak klasör** (laboratuvardaki mutlak yol; bu görevde hazırlık uzak tarafı `/tmp/pafta-bs35/` altında kurar). Dosyayı `scp` ile uzak klasöre aynı adla gönder, sonra özetini **uzakta** `sha256sum` ile hesaplatıp yerel özetle karşılaştır:

- başarıda `tamam <sha256>` yazdır ve 0 ile çık;
- gönderim başarısızsa (uzak klasör yok, yazılamıyor) `gönderilemedi` yazdır ve **1** ile çık;
- iki özet farklıysa `uyuşmazlık` yazdır ve **1** ile çık;
- yerel dosya yoksa ya da alanlardan biri eksikse `HATA` yazdır ve **2** ile çık.

Dosya ve klasör adlarında boşluk olabilir. Uzak yolu uzaktaki komuta stdin'den ver.

```stdin
rapor.txt	/tmp/pafta-bs35/gelen
```

```setup
import os, subprocess
L = os.getcwd()
for ad in ("host_ed25519", "id_lab"):
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", ad, "-f", ad], check=True)
os.replace("id_lab.pub", "authorized_keys"); os.chmod("authorized_keys", 0o600)
open("sshd_config", "w").write(f"HostKey {L}/host_ed25519\nAuthorizedKeysFile {L}/authorized_keys\nPasswordAuthentication no\n"
    "KbdInteractiveAuthentication no\nUsePAM no\nStrictModes no\nPidFile none\nSubsystem sftp internal-sftp\nLogLevel ERROR\n")
open("known_hosts", "w").write("lab " + " ".join(open("host_ed25519.pub").read().split()[:2]) + "\n")
kullanici = subprocess.run(["id", "-un"], capture_output=True, text=True).stdout.strip()
open("ayar", "w").write(f"Host lab\n    HostName lab\n    User {kullanici}\n    IdentityFile {L}/id_lab\n    IdentitiesOnly yes\n"
    f"    UserKnownHostsFile {L}/known_hosts\n    StrictHostKeyChecking yes\n    ProxyCommand /usr/sbin/sshd -i -f {L}/sshd_config\n    LogLevel ERROR\n")
U = "/tmp/pafta-bs35"          # aynı anda çalışan denemeler paylaşır: silinmez, yalnız eksikse kurulur
os.makedirs(U + "/gelen", exist_ok=True)
os.makedirs(U + "/salt okunur", exist_ok=True)
os.chmod(U + "/salt okunur", 0o555)
open("rapor.txt", "w").write("çeyrek raporu\n")
open("boşluklu ad.bin", "wb").write(bytes(range(256)) * 40)
open("bos.txt", "w").close()
```

```starter
IFS=$'\t' read -r yerel uzak
scp -F ayar "$yerel" "lab:$uzak/"
echo tamam
```

```test
import hashlib, os
def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()
U = "/tmp/pafta-bs35"
eq(run(stdin=f"rapor.txt\t{U}/gelen\n"), f"tamam {sha('rapor.txt')}\n", "gönderildi ve uzak özet tuttu")
eq(open(f"{U}/gelen/rapor.txt", "rb").read(), open("rapor.txt", "rb").read(), "uzaktaki dosya aynı")
eq(run(stdin=f"boşluklu ad.bin\t{U}/gelen\n"), f"tamam {sha('boşluklu ad.bin')}\n", "adında boşluk olan ikili dosya")
eq(run(stdin=f"bos.txt\t{U}/gelen\n"), f"tamam {sha('bos.txt')}\n", "boş dosya")
os.makedirs(f"{U}/iki kelime", exist_ok=True)
eq(run(stdin=f"rapor.txt\t{U}/iki kelime\n"), f"tamam {sha('rapor.txt')}\n", "uzak klasör adında boşluk")
r = calis(stdin=f"rapor.txt\t{U}/olmayan\n")
eq((r["kod"], r["cikti"]), (1, "gönderilemedi\n"), "uzak klasör yok")
r = calis(stdin=f"rapor.txt\t{U}/salt okunur\n")
eq((r["kod"], r["cikti"]), (1, "gönderilemedi\n"), "uzak klasör yazılamıyor")
r = calis(stdin=f"olmayan.txt\t{U}/gelen\n")
eq((r["kod"], r["cikti"]), (2, "HATA\n"), "yerel dosya yok")
r = calis(stdin="rapor.txt\n")
eq((r["kod"], r["cikti"]), (2, "HATA\n"), "uzak klasör alanı eksik")
ok("sha256sum" in src and "ssh" in src, "uzak özet ssh ile hesaplatılır")
```

```solution
IFS=$'\t' read -r yerel uzak || true
if [[ -z $yerel || -z $uzak || ! -f $yerel ]]; then
    echo HATA
    exit 2
fi
ad=$(basename -- "$yerel")
if ! scp -F ayar -q -- "$yerel" "lab:$uzak/$ad" 2>/dev/null; then
    echo gönderilemedi
    exit 1
fi
yerel_ozet=$(sha256sum -- "$yerel" | cut -d' ' -f1)
uzak_ozet=$(ssh -F ayar lab 'sha256sum -- "$(cat)"' <<< "$uzak/$ad" | cut -d' ' -f1)
if [[ -n $uzak_ozet && $uzak_ozet == "$yerel_ozet" ]]; then
    echo "tamam $yerel_ozet"
else
    echo uyuşmazlık
    exit 1
fi
```

```hint
Satırı `IFS=$'\t' read -r yerel uzak` ile oku: adlardaki boşluklar bölünmez. `scp ... "lab:$uzak/$ad"` başarısızsa (1) gönderilemedi.
```

```hint
Uzak özet: `ssh -F ayar lab 'sha256sum -- "$(cat)"' <<< "$uzak/$ad"`. Yol uzakta yalnız bir kez, `"$(cat)"` içinde açılır; boşluklar korunur.
```
:::
