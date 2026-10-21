# CMD / Batch · yazma yolu

Bu yol Windows'un gerçek `cmd.exe` yorumlayıcısıyla **komut ve batch betiği yazdırır**. PowerShell'den ayrı bir dildir. Altı rütbeye dağıtılan `cm01`–`cm18` derslerinin her birinde gerçek çalıştırmayla karşılaştırılan bir tahmin ve iki görev vardır. Kaynaklar, dosya hazırlıkları ve görevler sentetik eğitim verisi kullanır.

## Tezgah sözleşmesi

- Koşucu, mevcut `ProcRunner`/`ProcTester` protokolünü kullanır. Başlatma seçenekleri `/d /q /e:on /v:off /c`: AutoRun kapalı, komut yankısı kapalı, komut uzantıları açık, gecikmeli genişleme başlangıçta kapalıdır. Öğrenci `setlocal EnableDelayedExpansion` ile kendi kapsamında açabilir.
- Kaynak dosyalar UTF-8 ve LF'dir. Geçici `betik.cmd` ise UTF-8, BOM olmadan **CRLF** yazılır; böylece cmd.exe'nin satır ayrıştırması korunur. Başlatıcı `chcp 65001` ile yalnız çalıştırılan sürecin kod sayfasını ayarlar. `/u` kullanılmaz; stdout/stderr UTF-8 olarak okunur, CRLF uygulamada LF'ye çevrilir. Kodlamasını kendi belirleyen harici araçlar bu ayardan bağımsız olabilir.
- Girdi kutusu UTF-8/CRLF geçici dosyasından stdin'e yönlendirilir. Bu, `set /p` komutlarının ardışık kısa satır okumasını sağlar; Windows pipe tamponlamasının aynı davranacağı varsayılmaz. Native SET /P'nin tampon sınırı nedeniyle ilgili görevlerin satırları en fazla 200 karakterle sınırlıdır; genel uzun satır okuyucu iddiası yoktur. Klavye etkileşimi, `pause`, yeni pencere ve yönetici istemi gerektiren örnekler bu yolun dışında tutulur.
- Meta `argv` değerleri veya `calis(argv=[...])` argümanları tek açılımla aktarılır; başlatıcı veri üzerinde `call` ile ikinci genişleme yapmaz. Boşluk, Unicode, `& | < > ^ % !` desteklenir. Argüman içinde çift tırnak, NUL, CR veya LF **desteklenmez** ve süreç çalışmadan kod 87 ile reddedilir. Bu, bütün Windows programları için genel argv kodlayıcısı değildir. Öğrencinin kendi betiğinde veriyi tırnaksız kullanması veya `call` ile yeniden yorumlaması hâlâ sonucu değiştirebilir.
- Her koşucu işi ayrı geçici çalışma klasöründe başlar. Aynı görev testinin `run`/`calis` tekrarları aynı klasörü paylaşır; testler bu sayede dosya değişimini inceleyebilir. İş bittiğinde klasör kaldırılır. Bu düzen, bilgisayarın diğer dosyalarına erişimi engelleyen bir güvenlik kum havuzu değildir.
- Bir native çağrı için süre sınırı 10 saniye, genel run sınırı 15, görev sınırı 35 saniyedir. Görev meta'sı genel görev sınırını değiştirebilir (üst sınır 60); çağrı başına native sınır 10 olarak kalır. Süre dolunca süreç ağacı kapatılır. cmd.exe güvenilir satır numaralı bir iz sağlamadığından **Röntgen/Bytecode yoktur**; komut yankısı sahte bir adım izi olarak sunulmaz.

Kaynak, `_pafta_cmd.cmd`, `_pafta_cmd_stdin.txt` ve `__PAFTA_CMD_ARG_*` adları koşucunun iç çalışma dosyaları/değişkenleridir; ders verisi için bu adlar kullanılmaz. `betik.cmd` dosyasının yolu geçicidir; `%~dp0` bu klasörü gösterir.

## Ders kapsamı

| Dersler | Konular |
|---|---|
| cm01–cm03 | CMD/PowerShell ayrımı, echo/rem, değişkenler ve tırnaklar, parametreler ve shift |
| cm04–cm06 | set /p, boş/EOF girdi, if/defined, sayısal sınırlar, set /a ve blok bütçesi projesi |
| cm07–cm09 | Erken/gecikmeli genişleme, ünlemli veri, for ve for /l, for /f token/ayraç kuralları |
| cm10–cm12 | Tam/göreli yol, pushd/popd, stdout/stderr yönlendirme, findstr/find/sort ve metin projesi |
| cm13–cm15 | Çıkış kodları ve errorlevel, koşullu komutlar, alt yordamlar, call/shift, setlocal/endlocal |
| cm16–cm18 | Dosya envanteri ve kopya, Windows inceleme komutları ve sentetik çıktıları, parametreli rapor projesi |

Windows inceleme dersinde `where`, `tasklist`, `whoami`, `ipconfig`, `netstat` ve `wevtutil` seçenekleri anlatılır. Tahminler ve görevler kullanıcının canlı süreçlerini/ağını sorgulamaz; açık şemalı örnek çıktıları işler. Bu, yerelleştirilmiş her araç çıktısı için genel ayrıştırıcı değildir.

## Denetim

Proje kökünden:

```text
python tools/validate.py --yol cmd
python tools/test_cmd_runtime.py
python tools/test_cmd_curriculum.py
python tools/test_cmd_integration.py
python tools/audit_cmd_mutations.py
node --test tools/test_cmd_ui.mjs
```

Genel doğrulama bütün örnekleri/tahminleri cmd.exe'de çalıştırır; görev çözümleri geçmeli, başlangıçlar geçmemelidir. Müfredat testi ayrıca kimlik/rütbe düzenini ve tahmin çıktılarının açıklamalarda bulunmasını denetler. API testi geçici ilerleme verisi kullanır. Mutasyon denetimi sayısal karşılaştırmaları, koşullu akışı, errorlevel eşiklerini, sabit for /l uçlarını, sayacı/yuvarlamayı, gecikmeli genişlemeyi, harf duyarlılığını, ekleme/üzerine yazmayı, sıralamayı, ikili kopyayı ve token/literal seçimini tek tek değiştirir; çalışma hatasıyla reddedilenleri `error`, yanlış sonuçla reddedilenleri `fail` diye ayrı raporlar. Her olası bozuk betiği yakalama iddiası yoktur.

## Resmi dayanaklar

21 Ekim 2026 tarihinde başvurulan Microsoft belgeleri: [cmd](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cmd), [set](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/set_1), [if](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/if), [for](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/for), [call](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/call), [setlocal](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/setlocal), [findstr](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/findstr). Her ders ilgili komutların kaynaklarını ayrıca verir; belgede net olmayan örnekler gerçek yorumlayıcıyla sınanır.
