# Purple + Klasik planı (19 madde) · claude-yazar · 04.11.2026

**Durum (04.11.2026):** Kullanıcı yapı için **seçenek A**'yı onayladı ("Evet, A + başla"). Dalga A'nın kurulumsuz üç dersi yazıldı ve denetime hazır: `pu20` (klasik-7 pentest raporu), `pu21` (purple-9 tatbikat yönetimi), `pu22` (klasik-2 web; Juice Shop yerine kendi yerel uygulaması). Dalga A'nın hafif indirmeleri kullanıcı onayıyla ("Hepsini onayla", 04.11) indirilip doğrulandı (`DALGA-A-KURULUM-ONAYI.md`). Bunlarla yazılan üç ders de denetime hazır: `pu23` (klasik-6 DevSecOps: Semgrep, gitleaks, Trivy), `pu24` (klasik-1 keşif: ffuf, nuclei, tespit; nmap kısmı `pu18`'de) ve `pu25` (purple-1 CTID APT29 → test planı). **Dalga A tamamlandı.** Dalga B'nin imaj ve araç listesi (purple-7 → purple-3 → klasik-3 → klasik-4 → purple-2) kesin sürüm/boyut/hash ile hazırlandı ve kullanıcı onayı bekliyor (05.11): `DALGA-B-KURULUM-ONAYI.md`. Ölçüm sonucu bu listede auditd yerine strace, MailHog yerine Mailpit var; aşağıdaki Dalga B tablosu taslak halidir.

Bu belge bir **taslak**tır. Ders yazılmadı, indirme ya da kurulum yapılmadı. Boyutlar tahminidir; her araç için kesin sürüm, kaynak, boyut ve sha256 o aracın onayı istenirken ayrıca doğrulanacak. Kaynak plan: `EKLEME-PLANI-KAYNAK.md` (B2, B4, C).

## 1. Bugünkü durum (ölçüldü)

- **Purple yolu:** 9 modülde 19 ders (`pu01`–`pu19`).
  - Çoğu mavi takım dersi: kapsam, IR, Velociraptor, MISP, sertleştirme, adli izler.
  - Kırmızı tarafı uygulayan yalnız iki ders var: `pu18` (nmap) ve `pu19` (yerel SQLi).
- **AD yolu:** 25 ders (`ad01`–`ad25`). `pafta-samba-dc` konteyneri ve BloodHound CE imajı mevcut.
- **Bitirme yolu:** 7 ders (`bt01`–`bt07`).
- **Kurulu ya da mevcut araçlar:**
  - nmap, Velociraptor, Sysinternals, sigma-cli, yara-python, scapy, pwsh.
  - Docker imajları: Splunk, Elastic/Kibana, Kusto emülatörü, Zeek, BloodHound CE 9.9.0, neo4j, Postgres, MySQL, MSSQL, Samba DC.
- **Makine:** 6 çekirdek, Windows'un gördüğü RAM 23,3 GB; ölçüm anında boşta 2,4 GB. C: diskinde 155 GB boş.
  - **Ağır labın (çok VM'li AD) sınırı bellek.** Aynı anda tek ağır lab çalışabilir.

## 2. Yazım kuralları (her madde için aynı)

- Her plan maddesi 1–3 gerçek derse dönüşür. AI derslerindeki kabul zinciri burada da geçerli: validate, tahmin, mutasyon, kopya sondası, gerçek deney, kanıt dosyası.
- Saldırı tarafındaki her adım **izole** bir labda koşar: iç ağ, internet yok, sıfırlanabilir. Ana Windows'ta saldırı tekniği çalıştırılmaz.
- Ders, kırmızı adımı tek başına öğretmez. Her ders aynı olayın tespitini de ölçer: log, alarm, kural. Purple'ın amacı budur.
- Her yeni araç ya da imaj için sıra aynıdır: önce kaynak, sürüm, boyut ve hash; sonra panoya `soru`; kullanıcı onayı; sonra indirme.
- Mevcut `pu`/`ad`/`bt` dersleri silinmez ve yeniden yazılmaz; yeni dersler üstüne eklenir.

## 3. Karar 1: Purple yolunun yapısı

| Seçenek | Ne olur | Artı | Eksi |
|---|---|---|---|
| **A (önerilen)** | Mevcut 9 modül kalır, M1–M10 için yeni modüller eklenir; eski dersler `track.json`'da ilgili yeni modüle taşınmaz, bağlantı ders içi `esleme` ile kurulur | Mevcut puan ve denetim kayıtları bozulmaz | Yol uzar (19 → 40+ ders) |
| B | Purple yolu M1–M10 düzenine yeniden dizilir, eski dersler bu modüllere dağıtılır | Plana birebir uyar | Denetim kayıtları ve ilerleme sırası değişir; `track.json` büyük değişiklik |

## 4. Madde madde plan

Boyut sütunu indirme tahminidir. "Var" mevcut kurulumla yazılabileceği anlamına gelir.

### Dalga A: kurulumsuz ya da hafif (ilk yazılacaklar)

| Madde | Önerilen ders(ler) | Mevcut mavi bağı | Gereken | Tahmini indirme |
|---|---|---|---|---|
| klasik-7 Pentest raporu | Bulgudan rapora: kanıt, risk puanı (CVSS v4 hesaplayıcısı), tekrar üretilebilir adım, yönetici özeti | bt05, bt06 | Var (saf Python) | 0 |
| purple-9 Tatbikat yönetimi | Kurallar ve kapsam (RoE) denetimi; tatbikat takip defteri (VECTR yerine yerel JSON/SQLite) | pu02 | Var | 0 (VECTR sonra, isteğe bağlı) |
| purple-1 İstihbarattan plana | CTID emülasyon planını okuyup kendi labına uyan, tespit beklentisi yazılmış bir test planına çevirmek | pu01, pu04, pu13 | CTID adversary_emulation_library deposundan tek bir plan (YAML/MD) | < 5 MB |
| klasik-1 Keşif | nmap (var) ile kendi konteyner ağını tarama; ffuf ile dizin keşfi; nuclei'nin yalnız yerel şablonla koşması; tespit tarafında Zeek kaydı | pu18 | ffuf, nuclei (tek binary) + sabit sürümlü şablon alt kümesi | ~ 30–60 MB |
| klasik-6 DevSecOps | Semgrep, Trivy ve gitleaks'i kasıtlı açıklı küçük bir depoda CI adımı gibi koşturmak; yanlış pozitif ve kaçırma ölçümü | pu07 | semgrep (ayrı venv), trivy, gitleaks binary'leri + Trivy zafiyet DB'si | ~ 150–300 MB (DB dahil) |
| klasik-2 Web sömürüsü | Yerel, kasıtlı açıklı küçük web uygulamalarında XSS, SSTI ve XXE; her biri için savunma ve log kanıtı (SQLi `pu19`'da var) | pu11, pu19 | Kendi Flask uygulamamız (kurulumsuz) **ya da** OWASP Juice Shop imajı | 0 ya da ~ 400–600 MB |

### Dalga B: orta (konteyner ya da tek araç)

| Madde | Önerilen ders(ler) | Mevcut mavi bağı | Gereken | Tahmini indirme |
|---|---|---|---|---|
| purple-2 Keşif ve ilk erişim | Oltalama **tatbikatı** altyapısı: kapalı ağda GoPhish + MailHog, kurgusal kullanıcılar; tespit tarafında `pu14` başlık ve URL kanıtı | pu11, pu14 | GoPhish + MailHog imajları | ~ 100–200 MB |
| purple-7 Tespiti doğrulama | Atomic Red Team test **tanımlarını** okuyup izole Linux konteynerinde zararsız testleri koşturmak; Sigma kuralını aynı telemetride sınamak | pu05, pu06, pu07, bt03 | atomic-red-team deposu (yalnız tanımlar) + auditd/Sysmon-for-Linux içeren konteyner | ~ 100–300 MB |
| klasik-4 Tersine mühendislik | Kendi derlediğimiz zararsız örnek ikili dosyalar üzerinde FLOSS (string), capa (yetenek) ve Ghidra headless analizi | pu10 | FLOSS, capa (+ kural seti), Ghidra + JDK | ~ 700 MB – 1 GB |
| klasik-3 Pwn | Linux konteynerde kendi yazdığımız açıklı küçük C programları; derleyici korumalarının (canary, NX, ASLR) etkisini ölçmek; tespit tarafında çökme kanıtı | pu16 | gcc/gdb içeren Linux imajı | ~ 300–500 MB |
| purple-3 Çalıştırma ve kalıcılık | Linux konteynerde zamanlanmış görev ve servis kalıcılığı ile auditd tespiti; Windows tarafı Dalga C'ye kalır | pu03, pu15 | Dalga B'deki Linux imajı | ek ~ 0 |

### Dalga C: ağır (VM / çok makineli AD; donanım kararı gerekir)

| Madde | Önerilen ders(ler) | Mevcut mavi bağı | Gereken | Not |
|---|---|---|---|---|
| purple-4 Yetki yükseltme | Linux tarafı konteynerde (Dalga B'den); Windows tarafı izole Windows VM'de | pu12, pu16, ad01–ad07 | Windows değerlendirme VM'i | VM katmanı seçilmeli |
| purple-5 Kimlik bilgisi | Kerberos tabanlı saldırı ve tespit çiftleri; önce mevcut Samba DC ile ne yapılabildiği ölçülür | pu17, ad08–ad10 | Samba DC (var) → yetmezse GOAD-Light | GOAD-Light ~ 3 VM, ~ 10–12 GB RAM |
| purple-6 Yatay hareket + C2 | İzole ağda açık kaynak bir C2 çerçevesinin **trafiğini** Zeek ve RITA ile yakalamak; tespit odaklı | pu12 | C2 sunucu + Zeek (var) + RITA | Yalnız iç ağ; internete çıkış yok |
| purple-8 Atlatma + dayanıklılık | Aynı tekniğin varyantlarına karşı imza ve davranış tespitinin karşılaştırılması | pu05, pu06 | purple-7 telemetrisi | Dalga B'den sonra |
| purple-10 Bitirme | APT29 planının lab üzerinde uçtan uca öykünmesi ve tespit raporu | pu10, bt01–bt07 | purple-1..8'in labları | En son yazılır |
| klasik-5 Windows/AD saldırı | `ad13`–`ad25` kanıt derslerinin kırmızı yarısı | ad11–ad25 | purple-5 ile aynı lab | purple-5 ile birlikte |

### Dalga D: sonra

| Madde | Önerilen ders(ler) | Gereken | Tahmini indirme |
|---|---|---|---|
| klasik-8 Cloud/container | moto (sahte AWS) ile IAM yanlış yapılandırması; kind ile Kubernetes RBAC; Trivy imaj taraması | moto (pip, ayrı venv), kind + kubectl | ~ 200–400 MB |
| klasik-9 Mobil, kripto, gerçek imajla DFIR | Kripto: saf Python ile zayıf kip/IV hataları (kurulumsuz). Mobil ve gerçek imajla DFIR ayrıca planlanır | kripto için 0; diğerleri ayrı karar | — |

## 5. Önerilen sıra

1. **Dalga A, kurulumsuz:** klasik-7 → purple-9 → klasik-2 (kendi Flask uygulamamızla).
2. **Dalga A, hafif indirme** (tek toplu onay): purple-1 (CTID planı), klasik-1 (ffuf, nuclei), klasik-6 (semgrep, trivy, gitleaks).
3. **Dalga B** (toplu onay; her imaj ayrı listelenir): purple-7 → purple-3 → klasik-3 → klasik-4 → purple-2.
4. **Dalga C:** önce VM katmanı ve bellek kararı. Hyper-V, VirtualBox ya da yalnız Samba DC ile devam edilip edilmeyeceği seçilmeli. Ardından purple-5 + klasik-5 → purple-4 → purple-6 → purple-8 → purple-10.
5. **Dalga D:** klasik-8, sonra klasik-9.

Kaba iş tahmini: Dalga A ~ 6–9 ders, Dalga B ~ 7–10 ders, Dalga C ~ 8–12 ders, Dalga D ~ 3–5 ders.

## 6. Kullanıcının vereceği kararlar

1. Purple yapısı: seçenek A mı, B mi?
2. Dalga A'nın kurulumsuz üç dersine başlansın mı? (Onay gerekmez, yalnız sıra.)
3. klasik-2 için Juice Shop imajı mı, kurulumsuz kendi uygulamamız mı?
4. Dalga A'nın hafif indirme listesi, kesin sürüm, boyut ve hash'leriyle sunulduğunda onaylanacak mı?
5. Dalga C için VM katmanı ve bellek planı. Bu karar Dalga B bitene kadar beklemeye alınabilir.
