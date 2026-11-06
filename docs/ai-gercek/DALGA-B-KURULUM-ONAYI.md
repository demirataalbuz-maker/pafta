# Dalga B indirme listesi: onaylandı, indirildi, doğrulandı

- **Tarih / yazar:** 05.11.2026, claude-yazar.
- **Durum:** kullanıcı 05.11'de "Hepsini onayla" dedi. Tüm kalemler indirildi; boyut ve sha256 (CTID/Atomic için git blob) tabloyla **birebir** uyuştu. Kayıt: `.deps/dalga-b-indirme-kaydi.json`.
  - FLOSS, capa, Ghidra 12.1.4 `.deps/<araç>/acik/` altında; `floss.exe` ve `capa.exe` çalışır, Ghidra 6695 dosya.
  - 6 Atomic YAML `.deps/atomic-red-team-a8f00488/atomics/` altında, git blob'ları doğrulandı.
  - İmajlar yalnız digest ile çekildi: `debian:13-slim`, `gophish/gophish@…672d29`, `axllent/mailpit@…fd5231`.
  - **Linux lab imajları kuruldu:** `pafta-linux-lab:13-1` (530 MB, 100 paket kuruldu — tahmin 97, %3 sapma) ve `pafta-linux-lab:13-1-mingw` (1,08 GB, +6 paket — tahmin 6, birebir). Depo imzalı InRelease ile doğrulandı (`Check-Valid-Until` yalnız arşiv tarihi için kapalı). Dockerfile'lar `.deps/linux-lab-build/`. Sapma %20 sınırının altında; durulmadı.
  - gcc 14.2, gdb 16.3, strace 6.13, python3 3.13 imajda çalışıyor; `ogrenci` (uid 10001) kullanıcısı var.

## İlk durum (05.11, üst veri aşaması)

- **HENÜZ İNDİRME YOK.** Yalnız üst veri çekildi: GitHub API, Docker Registry manifestleri, Adoptium API ve Debian `Packages` listesi. Araç ya da imaj indirilmedi, kurulum yapılmadı.
- **Kapsam:** purple-7 → purple-3 → klasik-3 → klasik-4 → purple-2.
- **Toplam indirme:** 966.858.765 bayt (yaklaşık **967 MB**). Diskte tahminen 3 GB; ölçüm anında C: üzerinde 153 GB boş.

## Plana göre değişenler

Taslak planı (`PURPLE-KLASIK-PLAN.md`) ölçümle sınadım. Dört madde değişti:

| Taslakta | Ölçüm | Bu listede |
|---|---|---|
| auditd ya da Sysmon for Linux içeren konteyner | Audit netlink isteği (`AUDIT_GET`, salt okunur) root + `CAP_AUDIT_CONTROL` ile hem ayrı PID alanında hem `--pid=host` ile `EPERM` döndü. Olası neden: Docker Desktop motorunun kendisi de ayrı bir PID alanında çalışıyor (bu neden ölçülmedi, kaynak kod bilgisine dayanıyor). | auditd **yok**. Telemetri `strace -f` ile alınır (aşağıdaki sınıra bakın). |
| Ghidra + yeni JDK | Ghidra 12.2 `application.java.min=25` istiyor; kurulu JDK Temurin 21.0.12.1. 12.1.4 `java.min=21` istiyor. | Ghidra **12.1.4**. JDK indirilmez. (12.2 seçilseydi ek 141 MB JDK 25 gerekirdi.) |
| MailHog | Son sürümü 2020 tarihli. Mailpit v1.33.0 ekim 2026 tarihli, MIT lisanslı ve imajı daha küçük. | **Mailpit**. |
| "Zararsız Atomic testleri" | Depodaki Linux testlerinin bir kısmı ağa çıkıyor ya da dosya indiriyor. Örneğin `T1543.002` içinde ağ kullanan bir test var; "Create SysV Service" ise FreeBSD biçiminde. | Depo klonlanmaz. Yalnız 6 tanım dosyası ve içinde **adıyla seçilmiş 8 test**. |

## Neden gerekli?

| Plan maddesi | Ders (öneri) | Kullandığı |
|---|---|---|
| purple-7 Tespiti doğrulama | Atomic test tanımını oku, izole konteynerde koş, kendi tespit kuralını aynı telemetride sına | Atomic tanımları, Linux lab imajı |
| purple-3 Çalıştırma ve kalıcılık | cron ve shell profili kalıcılığı, tespiti ve temizliği | Linux lab imajı |
| klasik-3 Pwn | Kendi yazdığımız küçük C programlarında overflow, format string, ROP; canary, NX, ASLR etkisi; çökme kanıtı | Linux lab imajı |
| klasik-4 Tersine mühendislik | Kendi derlediğimiz zararsız örnekte FLOSS, capa, Ghidra headless | FLOSS, capa, Ghidra, mingw katmanı |
| purple-2 İlk erişim | Kapalı ağda oltalama **tatbikatı**, kurgusal kullanıcılar, başlık ve URL kanıtıyla tespit | GoPhish, Mailpit |

## Liste

Araçlar `.deps/<araç>-<sürüm>/` altına açılır. PATH'e eklenmez, Windows'a kurulmaz, `.ai-venv` değişmez.

### A. Windows araçları (GitHub Releases)

| # | Araç | Sürüm | Dosya | Boyut | sha256 | Lisans |
|---|---|---|---|---|---|---|
| 1 | FLOSS | v3.2.0 · mandiant/flare-floss | `floss-v3.2.0-windows.zip` | 33.134.130 bayt | `c0c73bb99d043fedd8e913038b65d1591fd6308cd938d8a91df87b733b369af5` | Apache-2.0 |
| 2 | capa | v10.0.0 · mandiant/capa | `capa-v10.0.0-windows.zip` | 36.108.928 bayt | `8712991044321dbb2a5b0d60f7a5327a50c9c30a295e7ddb5c1088cb17fb59df` | Apache-2.0 |
| 3 | Ghidra | 12.1.4 · NationalSecurityAgency/ghidra | `ghidra_12.1.4_PUBLIC_20260921.zip` | 569.649.598 bayt | `ddac49f903da9d5bac833e5cc79395098b9c33cfd3279be5f31bd00387d2d4db` | Apache-2.0 |

### B. Atomic Red Team tanımları

Kaynak: `redcanaryco/atomic-red-team` @ `a8f00488f3be0d6f8a967585848bb3817a590e31`, MIT. Yalnız aşağıdaki YAML dosyaları (toplam 44.916 bayt). İndirince sha256 de kaydedilir.

| Dosya | Bayt | git blob | Koşulacak test (GUID başı) |
|---|---|---|---|
| `T1053.003.yaml` | 3.772 | `b9bdf9e852fb3661aba422c106e81ae170373b9e` | crontab değiştirme (`435057fb`), `/etc/cron.d` (`078e69eb`) |
| `T1546.004.yaml` | 4.991 | `eb845278f6a554c55cb496a6c59881935eee8ee0` | `.bashrc` (`0a898315`), `.bash_profile` (`94500ae1`) |
| `T1059.004.yaml` | 12.923 | `271a58c89a7ffbcebf4893bd7a768996b315cbba` | tmp altında betik (`8cd1947b`) |
| `T1222.002.yaml` | 9.653 | `48baa53d6f3432e5b92316b969f4b9112cd9b351` | chmod (`34ca1464`) |
| `T1087.001.yaml` | 6.768 | `1c71c0baedf7db649acf3ed63befed81cf94207f` | UID 0 hesapları (`c955a599`) |
| `T1070.003.yaml` | 6.809 | `a9fa7aa051bdca2969e17e10bd863024be7523b1` | Bash history silme (`a934276e`) |

### C. Konteyner imajları (Docker Hub, digest ile çekilir)

| # | İmaj | Digest | amd64 sıkıştırılmış boyut | Lisans / not |
|---|---|---|---|---|
| 4 | `debian:13-slim` | `sha256:f6b08b09a05725f9431502d3b5714f5c4576e82c1a84fa1debe0c24a7e0c3ec4` | 29.855.687 bayt | Linux lab tabanı |
| 5 | `gophish/gophish:0.12.1` | `sha256:8a57cd171999dcd1fa33f346d6898440913ae14be114ffc850cc678354672d29` | 133.379.947 bayt | MIT. **İmaj kasım 2022 tarihli, içi güncel değil**; bu yüzden yalnız iç ağda çalışır. |
| 6 | `axllent/mailpit:v1.33.0` | `sha256:9b3a463be15354c0f0eba91697d80e3e0d8a5623ef0e627cacc836bc17fd5231` | 14.903.107 bayt | MIT |

### D. Debian 13 paketleri (imaj içinde, Windows'a değil)

Kaynak: `snapshot.debian.org/archive/debian/20261101T000000Z`, `trixie main`. Tam liste, sürüm ve sha256 ile: [DALGA-B-APT-LISTE.json](DALGA-B-APT-LISTE.json).

| Yerel imaj | Paketler | Sayı | İndirme | Kurulu |
|---|---|---|---|---|
| `pafta-linux-lab` | gcc 14.2, libc6-dev, binutils, make, gdb 16.3, strace 6.13, cron, python3 3.13, procps | 97 | 84.720.872 bayt | ~ 302 MB |
| `pafta-linux-lab` üstüne mingw katmanı | gcc-mingw-w64-x86-64-win32 (FLOSS'un tam analizi için PE örneği derlemek) | 6 | 65.061.580 bayt | ~ 433 MB |

**Paket sayısı kesin değil.** Bağımlılıkları `Packages` dosyasından kendim çözdüm; taban imajın paketlerini tahmin ettim. Kural: imaj çekilince önce `apt-get -s` çalışır. Sonuç bu listeden **%20'den fazla** saparsa ya da sürüm çakışması çıkarsa durur, sana yeniden sorarım.

## Güvenlik kuralları

1. **Doğrulama:** Boyut ve sha256 tabloyla karşılaştırılır; uyuşmazsa dosya silinir ve durulur. İmajlar yalnız digest ile çekilir. Zip açılırken yol taşması denetlenir. Apt paketleri imzalı depo üzerinden doğrulanır.
2. **Linux lab:** `--network none` ile çalışır, `--privileged` kullanılmaz, her koşuda atılır. Saldırı adımı Windows'ta çalışmaz. Çekirdek ayarları (`randomize_va_space` dahil) değiştirilmez.
3. **Atomic testleri:** Yalnız yukarıdaki 8 test, adıyla izin listesinde. Listede olmayan test koşmaz. Argümanları ders verir.
4. **Pwn:** Hedef yalnız kendi yazdığımız programlar. Ölçüm: varsayılan Docker seccomp ptrace'e izin veriyor (`PTRACE_TRACEME` = 0) ama `personality(ADDR_NO_RANDOMIZE)` engelli (`EPERM`). ASLR kapalı karşılaştırma için yalnız bu çağrıyı açan dar bir seccomp profili yazılır.
5. **Oltalama:**
   - GoPhish ve Mailpit `--internal` Docker ağında çalışır; internete çıkış yoktur.
   - Alıcılar kurgusal, alan adları `.test` ya da `.example`. Gerçek SMTP aktarımı yok, gerçek marka taklidi yok.
   - Gerçek parola toplanmaz; sahte giriş sayfası yalnız kurgusal verilerle sınanır.
   - Mailpit dışarıya aktarım yapmaz (relay yapılandırılmaz).
6. **FLOSS, capa, Ghidra:** Yalnız kendi derlediğimiz zararsız örneklerde çalışır. Dışarıdan zararlı örnek indirilmez.
7. **Ağ sınaması:** Dalga A'daki gibi ilk koşular kayıt tutan yerel 403 vekiliyle yapılır. capa ve FLOSS'un gömülü kurallarla çevrimdışı çalıştığı ilk koşuda doğrulanır; ek kural paketi gerekirse ayrıca sorulur.
8. **Dokunulmayacaklar:** Docker Desktop ayarları, WSL, Ollama, mevcut imajlar ve konteynerler.

## Derslerde açıkça yazılacak sınırlar

- **strace bir EDR ya da auditd değildir.** Yalnız izlenen süreç ağacını görür; sistem geneli sensör değildir ve hedef süreç izlendiğini anlayabilir. Sigma kuralı bu yüzden kendi alan eşlemesiyle koşar; gerçek auditd log kaynağında aynı sonucu verdiği iddia edilmez.
- **systemd yok.** Konteynerde systemd çalışmadığı için servis kalıcılığı uygulamalı gösterilemez; ders cron ve shell profilini ölçer, systemd'yi yalnız birim dosyası düzeyinde inceler.
- **Windows tarafı yok.** Windows kalıcılığı ve Sysmon tarafı Dalga C'ye kalır.
- **GoPhish imajı eski.** Ders güncel bir oltalama altyapısını temsil etmez.

## Hâlâ doğrulanmamış olanlar

Bunları indirmeden ölçemem; ilk koşuda sınanır ve sonuç bu dosyaya yazılır:

- strace'in cron işlerini ve kalıcılık adımlarını yeterli ayrıntıyla yakalaması
- GoPhish 0.12.1'in `--internal` ağda Mailpit'e posta göndermesi
- Dar seccomp profiliyle ASLR kapalı koşunun çalışması
- Ghidra headless'ın kurulu JDK 21 ile açılması ve bu makinede analiz süresi (purple runner üst sınırı 60 sn; aşarsa analiz önceden yapılıp kaydedilmiş çıktı diye açıkça etiketlenir)

Smart App Control ölçüm anında kapalı (`VerifiedAndReputablePolicyState = 0`), bu yüzden Windows araçlarının engellenmesi beklenmiyor.

## Onaydan sonra sıra

1. İndir, boyut ve hash'i doğrula, kaydı `.deps/dalga-b-indirme-kaydi.json` dosyasına yaz.
2. `pafta-linux-lab` imajını kur, `apt-get -s` sonucunu listeyle karşılaştır.
3. Ağ sınaması ve yukarıdaki doğrulanmamış maddeler.
4. Ders sırası: purple-7 → purple-3 → klasik-3 → klasik-4 → purple-2. Her biri ayrı denetime gider.
