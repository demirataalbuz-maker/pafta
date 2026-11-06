# Dalga A indirme listesi: onaylandı, indirildi, doğrulandı

- **Tarih / yazar:** 04.11.2026, claude-yazar.
- **Durum:** kullanıcı 04.11'de "Hepsini onayla" dedi. 6 kalemin tümü indirildi; boyut ve sha256 (CTID için git blob) tabloyla **birebir** uyuştu. Kayıt: `.deps/dalga-a-indirme-kaydi.json`.
  - Semgrep `.deps/semgrep-venv` içine `--require-hashes --no-deps --only-binary=:all:` ile kuruldu (67 paket, diskte 361 MB).
  - Sürüm çıktıları: ffuf 2.3.0, nuclei v3.11.1, trivy 0.76.1, gitleaks 8.30.1, semgrep 1.183.0.
  - **Çevrimdışı sınama** (`.deps/dalga-a-sinama.json`): her araç geçici bir ev dizini ve her isteği kaydedip 403 dönen yerel bir vekille (HTTP(S)_PROXY) koştu; hedef `127.0.0.1`. Vekile **0 istek** geldi; nuclei şablon deposu indirmedi; trivy `misconfig` denetimleri ikili dosyaya gömülü çıktı (DS-0026 vb. buldu), yani ek kontrol paketi gerekmedi. Sınır: vekile uymayan doğrudan bağlantıları bu yöntem görmez.
- **Kaynak bilgisi:** sürüm, boyut ve sha256 değerleri resmî GitHub Releases API'den (`digest` alanı) ve PyPI JSON API'den okundu. Yalnız üst veri çekildi.
- **Semgrep bağımlılıkları:** `pip install --dry-run --report` ile çözüldü; hiçbir şey kurulmadı.

## Neden gerekli?

| Plan maddesi | Ders (öneri) | Araç |
|---|---|---|
| purple-1 İstihbarattan plana | CTID APT29 öykünme planını labımıza uyan, tespit beklentisi yazılmış bir test planına çevirmek | CTID APT29 YAML |
| klasik-1 Keşif | Kendi yerel lab ağında dizin keşfi (ffuf) ve **kendi yazdığımız** şablonla zafiyet doğrulama (nuclei); mavi tarafta erişim kaydı | ffuf, nuclei |
| klasik-6 DevSecOps | Kasıtlı açıklı küçük bir depoda SAST (Semgrep), sır taraması (gitleaks), yapılandırma ve sır taraması (Trivy); yanlış pozitif ve kaçırma ölçümü | semgrep, gitleaks, trivy |

## Liste

Yükleme yeri her biri için ayrı bir klasör: `.deps/<araç>-<sürüm>/`. PATH'e eklenmez, Windows'a kurulmaz, `.ai-venv` değişmez.

| # | Araç | Sürüm / kaynak | Dosya | Boyut | sha256 | Lisans |
|---|---|---|---|---|---|---|
| 1 | ffuf | v2.3.0 · github.com/ffuf/ffuf | `ffuf_2.3.0_windows_amd64.zip` | 4.497.208 bayt (4,5 MB) | `091c8a22d0c7fbe07d343b3ae2c213dbd37b38a8a2ed40631fcd3128ea1764fb` | MIT |
| 2 | nuclei | v3.11.1 · github.com/projectdiscovery/nuclei | `nuclei_3.11.1_windows_amd64.zip` | 46.067.128 bayt (46,1 MB) | `bb6cb9ff8939b753f6fcab06fd30a15f5bc61d8382a597871334c007a85ff9d2` | MIT |
| 3 | trivy | v0.76.1 · github.com/aquasecurity/trivy | `trivy_0.76.1_windows-64bit.zip` | 53.886.844 bayt (53,9 MB) | `1051f49cb22d5284f43425f72aad9cda63ca12ceb92e7caa06903490c82dc9bf` | Apache-2.0 |
| 4 | gitleaks | v8.30.1 · github.com/gitleaks/gitleaks | `gitleaks_8.30.1_windows_x64.zip` | 8.438.883 bayt (8,4 MB) | `d29144deff3a68aa93ced33dddf84b7fdc26070add4aa0f4513094c8332afc4e` | MIT |
| 5 | semgrep | 1.183.0 · PyPI (resmî Windows wheel) | `semgrep-1.183.0-…-none-win_amd64.whl` + 66 bağımlılık | toplam 82.383.032 bayt (82,4 MB); semgrep wheel'i 59.495.454 bayt | wheel: `8e9d96b976d6cb8e1240d454e50245decd52d1329d84540df26c7f06787439f7`; her paketin sha256'sı pip raporunda | semgrep LGPL-2.1-or-later; bağımlılıkların çoğu MIT/BSD/Apache |
| 6 | CTID APT29 planı | center-for-threat-informed-defense/adversary_emulation_library @ `4467a6eed6e67d25009704130e1d27d1a8007f57` | `apt29/Emulation_Plan/yaml/APT29.yaml` | 101.876 bayt | git blob `7f23eb7da088e53f560bf868baffbe93a1688942` (indirince sha256 de kaydedilecek) | Apache-2.0 |

**Toplam indirme:** yaklaşık **195 MB**. Açıldıktan sonra diskte tahminen 400–500 MB; boş alan 155 GB.

Semgrep ayrı bir sanal ortama kurulur: `.deps/semgrep-venv`, Pafta'nın Python 3.13'üyle. En büyük bağımlılıklar şunlar:

| Paket | Sürüm | Boyut |
|---|---|---|
| pywin32 | 311 | 9,5 MB |
| cryptography | 50.0.2 | 3,8 MB |
| pydantic_core | 2.50.2 | 2,3 MB |
| Pygments | 2.21.0 | 1,3 MB |

Diğer bağımlılıklar arasında rich, protobuf, opentelemetry, mcp, httpx ve starlette var.

## Güvenlik ve çevrimdışı çalışma kuralları

1. **Doğrulama:**
   - Her dosya indirildikten sonra boyutu ve sha256'sı yukarıdakiyle karşılaştırılır; uyuşmazsa silinir ve durulur.
   - Zip açılırken yol taşması denetlenir.
   - Semgrep bağımlılıkları `--require-hashes` ile, pip raporundaki hash'lerle kurulur.
2. **Hedefler:** ffuf ve nuclei **yalnız** dersin kendi `127.0.0.1` labına yönelir. pu21'deki RoE kapısı aynen kullanılır; kapsam dışı yem dinleyicisi yine 0 bağlantı göstermelidir.
3. **nuclei:**
   - Yalnız dersin kendi YAML şablonuyla çalışır; güncelleme denetimi kapatılır (`-duc`).
   - Yapılandırma klasörü geçici dizine yönlendirilir; genel şablon deposu (nuclei-templates) **indirilmez**.
   - İlk koşu, ağ trafiği izlenerek bunu doğrular. Yine de indirmeye kalkarsa ders bu durumu gösterir ve araç o kipte kullanılmaz.
4. **semgrep:**
   - `--metrics=off` ile, yalnız yerel kural dosyasıyla çalışır.
   - Semgrep Registry, giriş (login) ya da bulut kullanılmaz.
5. **trivy:**
   - Yalnız `secret` ve `misconfig` tarayıcıları kullanılır; `--skip-db-update` ve `--skip-check-update` açık.
   - **Zafiyet veritabanı (trivy-db) bu listede yok.** SCA dersi için gerekirse boyut ve hash ile ayrıca onaya sunulacak.
   - Yapılandırma denetimlerinin ikili dosyaya gömülü olup olmadığı ilk koşuda doğrulanacak. Gömülü değilse kontrol paketi de ayrıca onaya sunulacak; o zamana kadar yalnız `secret` taraması yapılır.
6. **gitleaks:** yalnız dersin geçici deposunda, sahte sırlarla (canary) çalışır.
7. **Dokunulmayacaklar:** kullanıcının Docker'ı, WSL'i, Ollama'sı ve mevcut kurulumları.

## Onaydan sonra sıra

1. İndir, boyut ve hash'i doğrula, `.deps` altına aç, sürüm çıktısını kaydet.
2. klasik-6 DevSecOps dersi: semgrep, gitleaks, trivy (secret).
3. klasik-1 keşif dersi: ffuf, nuclei (kendi şablonu) + nmap (zaten kurulu).
4. purple-1 dersi: CTID APT29 planından yerel test planı.
