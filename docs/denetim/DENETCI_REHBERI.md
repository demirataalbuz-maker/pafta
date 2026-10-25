# Pafta · Denetçi rehberi

Bu belge Pafta'yı ilk kez denetleyecek bir yapay zekâ (ya da insan) içindir. Okuyunca şunları bilmelisin: proje ne için var, nasıl kurulu, bir ders nasıl çalışır ve nasıl sınanır, kim neyi yazar, bir madde nasıl denetlenir, nerede tuzak var.

Yazan: Claude (Denetçi · Yazar 2), 25 Ekim 2026, `ac6f37b` üzerinde. Sayılar o günündür; kendin yeniden say.

---

## 1. Pafta ne için var

Pafta, kullanıcının bilgisayarında çalışan, güvenlik işi için dil ve araç öğreten bir okul. Hedef kullanıcı **purple team** (red + blue) uygulayıcısı olmak istiyor.

**Pafta'nın rolü altyapıdır.** Kullanıcı uygulamalı red/blue yollarını (path) TryHackMe ve HackTheBox'ta **paralel** yürüyor. Pafta onların laboratuvarlarını kopyalamaz. Pafta, o platformların "bunu zaten biliyorsun" diye varsaydığı temeli verir:

- dilin kendisi (Python, C, Bash, PowerShell, SQL, ...),
- aracın altında ne olduğu (ctypes'ta ABI, requests'te vekil ve CA, pip'te çözücü),
- aracın çıktısını okumak, veri biçimini anlamak (PCAP, EVTX, JSON log, PE),
- hazır bir betiği okuyup uyarlamak, kendi küçük aracını yazmak,
- tespit dillerinin kendisi (SPL, KQL, Sigma, YARA, Suricata/Zeek).

Denetlerken sorulacak ana soru: **"THM/HTB'de bu konuya gelen biri, Pafta'dan gereken temelle mi geliyor?"** Gerçek araç ve gerçek veri kullanılıyor mu, yoksa oyuncak bir benzetim mi? İş ilanında ve sertifikada (OSCP, CPTS, BSCP, BTL1, SC-200, PCEP/PCAP/PCPP1) karşılığı olan bir beceriye bağlanıyor mu?

## 2. Dosya düzeni

```
Pafta.pyw, server.py    uygulamayı açan yerel sunucu (tarayıcıda açılır)
web/                    arayüz: app.js, editor.js, md.js, hl.js, style.css
engine/
  lessons.py            .md dersleri okur, adımlara böler (Library)
  runners.py            her yol için koşucu; for_step() adımın meta'sına göre doğru koşucuyu seçer
  progress.py           öğrencinin ilerlemesi
  sinav.py              sınav ve tahmin çalıştırma
tracks/<yol>/
  track.json            yolun sırası, modüller, rütbeler, runner, kazanım listesi
  lessons/*.md          dersler (bir ders bir dosya)
  veri/                 bazı yolların sabit verisi
sandbox/                koşucuların ve derslerin kullandığı tezgâhlar (aşağıda)
tools/                  validate.py, tahmin_denetle.py, takip_excel.py, kurulum ve regresyon testleri
docs/                   çalışma panosu, durum, bu rehber, denetim raporu
.deps/                  derslerin Python paket deposu (pip --target); sistem Python'unu kirletmez
ASAMA2.md               104 maddelik plan: her madde için neden / ne gerekir / kurulum / kabul
DENETIM.md              maddelerin durum tablosu, açık ve kapanan bulgular, ajan kuralları
DEGERLENDIRME.md        genel değerlendirme
Pafta_Takip.xlsx        kullanıcının izlediği tablo; elle düzenlenmez, takip_excel.py üretir
```

### Yollar (25 Ekim 2026, ders sayısı)

| Grup | Yollar |
|---|---|
| Diller | python 83, bash 35, powershell 29, cmd 25, sql 22, regex 24, c 17, csharp 17, asm 16, java 16, javascript 16, php 16 |
| Web ve ağ | http 24, packets 29 |
| Savunma / tespit | spl 23, kql 24, elastic 27, sigma 22, yara 22, ids 5 |
| Ortam ve birleştirme | ad 23 (bir kısmı commit'lenmemiş), purple 3 |

Toplam ~518 ders dosyası. Her yol 6 rütbeye bölünür (Minik → Başpehlivan, güreş terimleri).

### Tezgâhlar (`sandbox/`)

Derslerin "gerçek hedefleri" burada. Önemlileri:

| Dosya | Ne kurar |
|---|---|
| `py_harness.py` | Python görevlerini ayrı süreçte çalıştıran düzenek; test yardımcıları burada |
| `api_tezgah.py` | Oturumlu yerel API, `/giris-form`, kimlikli vekil (`vekil_kur`), kendi CA'lı HTTPS (`tls_kur`); `import api` ile gelir |
| `ctypes_lab.py` | C kaynağını Kali'deki mingw/gcc ile win32/win64/linux64/DLL olarak gerçekten derler (`ctlab`) |
| `wsl_*.py` | `backend: wsl` adımlarını Kali'de çalıştıran koşucu |
| `splunk_lab.py`, `spl.py` | Gerçek Splunk'a arama gönderen ve yerel SPL motoru |
| `elastic_*.py` | Gerçek Elasticsearch: KQL, Lucene, EQL |
| `sigma_engine.py` | pySigma ile kural ayrıştırma ve yerel test |
| `yara_engine.py`, `yara_*fixtures.py` | YARA ve PE/biçim örnekleri |
| `ids_lab.py` | Suricata ve Zeek |
| `packet_*.py`, `capture_formats.py` | PCAP/PCAPNG korpusu ve paket motoru |
| `pg_lab.py`, `mariadb_lab.py` | Gerçek PostgreSQL ve MariaDB |
| `vql_lab.py` | Velociraptor (purple) |
| `ad_*.py`, `ad_vm/` | AD yolu: çevrimdışı motor ve gerçek DC sanal makinesi |
| `evtx_fixtures.py`, `ps_evtx_fixtures.py` | Olay günlüğü örnekleri |

## 3. Bir dersin yapısı

Ders dosyası, ön bilgi (YAML) ve `:::` bloklarından oluşur:

```markdown
---
id: p74
title: requests Session ve Beautiful Soup
summary: ...
kazanim: PCPP1 4.4          # sertifika eşlemesi (validate denetler)
backend: wsl                # isteğe bağlı: bütün adımlar Kali'de
---

::: anlat Başlık
Konu anlatımı. Görüntü amaçlı kod blokları ```python norun ile işaretlenir (çalıştırılmaz).
:::

::: tahmin Başlık
"Bu kod ne yazar?" sorusu, ardından kod.
???
Cevap ve açıklama. (Denetçi: kodu çalıştır, çıktının her satırı burada geçmeli.)
:::

::: gorev Başlık
Öğrenciye görev tanımı.
```setup     hazırlık: tezgâhı kurar, dosya üretir, DLL derler
```starter   başlangıç kodu: bilerek eksik ya da yanlış, testten KALMALI
```test      sınayan kod
```solution  doğru çözüm: testten GEÇMELİ
```hint      ipucu (birden çok olabilir)
```meta      adım ayarı: backend, motor, timeout, girdi, ...
:::
```

### Python test yardımcıları (`sandbox/py_harness.py`, `Tester`)

| Yardımcı | Ne yapar |
|---|---|
| `need("ad")` | öğrencinin kodunda o fonksiyon yoksa durur |
| `eq(got, exp, msg)` | eşitlik |
| `ok(cond, msg, got=)` | koşul |
| `yakin(got, exp, tol)` | kayan nokta yakınlığı |
| `raises(Exc, fn, ...)` | istisna bekler |
| `run(stdin=, argv=)` | öğrencinin programını yeniden çalıştırır, çıktıyı döndürür |
| `run_code(code)` | başka bir kodu aynı ortamda çalıştırır |
| `capture(fn, ...)` | fonksiyonun yazdığını yakalar |
| `uses(kind)`, `calls(name)` | kodda bir yapının ya da çağrının geçip geçmediği (AST) |
| `src` | öğrencinin kaynak metni ("şunu kullanma" kuralları için) |

Görev geçer = test hatasız biter, en az bir kontrol vardır ve hepsi doğrudur. Hiç `eq/ok` çağrılmazsa görev geçmez.

Python görevi, kurulumla **aynı süreçte** çalışır: `setup` bir modül kurarsa (`sys.modules["api"]`), öğrenci kodu ve test onu görür. Her iş geçici bir `pafta_*/calisma` klasöründe, `python -I -X utf8` ile koşar.

### Koşucular (`engine/runners.py`)

Yolun `track.json`'ındaki `runner` alanı koşucuyu seçer. `for_step(runner, step)` adımın `meta`'sına bakıp onu değiştirir:

- `backend: wsl` → Kali'de (`PAFTA_WSL_DISTRO`, varsayılan `kali-linux`). Linux yoksa **sessizce Windows'a düşmez**, hata verir.
- `motor:` → `pcre2`/`dotnet`/`javascript` (regex), `postgres`/`mariadb` (sql), `splunk` (spl, sigma), `suricata`/`zeek` (ids), `velociraptor` (purple), `pwsh` (PowerShell 7), `ad-vm`/`ad-client`/`python` (ad).
- `timeout:` → süre sınırı.

Bir denetim betiği de aynı yolu izlemeli: `runners.for_step(runners.get(track["runner"]), step).test(kod, step)`. Doğrudan `runners.get("python")` kullanırsan `backend: wsl` adımlarını yanlış ortamda çalıştırırsın.

## 4. Planlama ve iş akışı

- **`ASAMA2.md`:** 104 madde. Her biri bir eksikliği tarif eder: **neden** (sahada neye yarar), **ne gerekir** (dersin içermesi gereken), **kurulum**, **kabul**. Denetimin ölçütü bu sütunlardır, dersin kendi iddiası değil.
- **`DENETIM.md` → "Aşama 2 durum tablosu":** her maddenin yazarı ve durumu (`bekliyor · yazılıyor · denetlendi · geri döndü`). Bu tablo **bayatlayabilir**: dersi commit'lenmiş birçok madde hâlâ "bekliyor" görünüyor (23–30, 35–36, 38–48, 50, 55–60). Durumu tablodan değil `git log`'dan ve ders dosyasından doğrula.
- **`docs/CALISMA_PANOSU.md`:** kim neyi yapıyor; aynı işin iki kez yapılmaması için.
- **`Pafta_Takip.xlsx`:** kullanıcının baktığı yer. Her denetimden sonra `python -X utf8 tools/takip_excel.py` ile yeniden üretilir.

### Ajanlar

Hepsi aynı git kullanıcısıyla commit eder; kimin yaptığı commit mesajının **son satırındaki imzadan** anlaşılır.

| Ajan | İş | İmza |
|---|---|---|
| Claude Opus 4.8 | Yazar 1: yolların çoğu | `Ajan: Claude (Yazar 1)` |
| Codex | Yazar: Sigma/YARA, altyapı, AD'nin bir kısmı | `Ajan: Codex` |
| Claude | Eski Yazar 2, şimdi denetçi (bu rehberin yazarı) | `Ajan: Claude (Denetçi · Yazar 2)` |
| Antigravity | Şu an yok; raporları ölçülmeden kabul edilmez (A28) | `Ajan: Antigravity` |

Ajanlar birbirine mesaj atamaz; kullanıcı aktarır.

### Kurallar (DENETIM.md "Ajanlar ve kurallar"dan)

- `git add -A` / `git commit -a` **yok**. Yalnız kendi dosyalarını pathspec ile commit'le: `git commit -F - -- <dosyalar>`.
- Push yok (kullanıcı istemedikçe).
- Aynı dosyada aynı anda tek ajan. Commit'lenmemiş başka ajan dosyası varsa (`git status`) **dokunma**. 25 Ekim'de AD işi (AD15–AD23, `sandbox/ad_*`, `engine/runners.py`, `tools/validate.py`, `README.md`, `tracks/ad/track.json`) başka bir ajanda açık.
- Ortak dosyalar (`sandbox/py_harness.py`, `engine/*.py`, `web/*.js`, `README.md`, `tools/validate.py`): önce `git status`, bitince hemen commit.
- **Bir madde, yazarın raporuyla değil, denetçi kendi ölçümünü yeniden koşturunca kapanmış sayılır.**

## 5. Ortam

- Windows 11; Python yorumlayıcısı 64 bit Windows CPython. **32 bit Python yok.**
- WSL 2'de `kali-linux`: python3.14, pip 26.x, gcc 16, `i686-w64-mingw32-gcc`, `x86_64-w64-mingw32-gcc`, Scapy, TShark, Impacket, pwntools, curl/jq.
- Splunk, Elasticsearch, PostgreSQL, MariaDB, Suricata, Zeek, Velociraptor yerel kurulu; ilgili yolların koşucuları onlara bağlanır. Ağır yük altında Elastic görevleri ara sıra zaman aşımına düşebilir (EL20/EL21); tekrar koştur, kalıcıysa yaz.
- **WSL'i PowerShell'den çağır** (`wsl.exe -d kali-linux -- ...`). Git Bash yolları (`/c/...`) bozar.
- Proje yolunda emoji ve Türkçe karakter var (`📂 Projeler ve Çalışmalar\💻 Web ve Yazılım Projeleri\Pafta`). Bazı araçlar buna takılır. Bu yüzden denetim **ASCII bir geçici klasördeki anlık görüntüde** yapılır (bkz. 6.1).
- Türkçe çıktı için Python'u `-X utf8` ile çalıştır.

## 6. Denetim yöntemi

Rapor: `docs/denetim/madde-denetimi.md`. Maddeler **1'den 104'e sırayla**. Denetçi ders, motor ya da test **değiştirmez**; yalnız rapor yazar ve commit'ler. (Kullanıcı açıkça "tamamla" derse istisna; o zaman yazdığın bölüm için **çıkar çatışmasını** rapora yaz.)

Her madde iki soruya cevap verir:

1. **Çalışıyor mu?** (aşağıdaki ölçümler)
2. **İstenen yapıldı mı?** ASAMA2 satırının "neden" ve "ne gerekir" sütunlarını dersle tek tek karşılaştır. Karşılanmayan her şeyi, küçük olsa da, **sorulmadan** yaz. "Bitti" deme eğilimine karşı dur; her "Tam"ın yanında da eksik kalan varsa yaz.

Karar ölçeği: **Tam** · **Kısmen** (çalışıyor, istenenin bir kısmı yok) · **Eksik** (asıl istenen yok, ders yok) · **Sorunlu** (çalışmıyor ya da test yanlışı kabul ediyor).

### 6.1 Anlık görüntü

```powershell
$h = git rev-parse --short HEAD
$d = "$env:TEMP\pafta_denetim_$h"
git archive HEAD | tar -x -C (New-Item -ItemType Directory -Force $d)
cmd /c mklink /J "$d\.deps" "<proje>\.deps"
```

Böylece başka ajanların commit'lenmemiş işi sonucu etkilemez ve yol ASCII olur.

### 6.2 validate (iki kabukta)

```
python -X utf8 tools/validate.py p74 p75          # belirli dersler
python -X utf8 tools/validate.py --yol python     # bir yol
python -X utf8 tools/validate.py                  # hepsi + kazanım denetimi
```

Her görev için: starter **kalmalı**, solution **geçmeli**; tahminler çalışmalı; kazanım eşlemesi tutarlı olmalı. Sonda `TEMİZ` ya da `N SORUN`. Hem PowerShell'de hem Git Bash'te koştur; ikisinde farklı sonuç (yol, kodlama, süre) bir bulgudur.

### 6.3 Tahmin kontrolü

```
python -X utf8 docs/denetim/araclar/tahmin.py <anlık görüntü> p74 p75
python -X utf8 tools/tahmin_denetle.py p74       # projedeki eşdeğeri (yalnız Python koşucusu)
```

Tahmin kodu gerçekten çalıştırılır; çıktının her boş olmayan satırı cevap metninde geçmeli. Geçmiyorsa ders öğrenciye yanlış bir şey öğretiyor olabilir.

### 6.4 Mutasyon

```
python -X utf8 -u docs/denetim/araclar/mutasyon.py <anlık görüntü> [--en-cok N] p74 p75 > mut.txt
```

Örnek çözümde küçük değişiklikler yapar (sayı+1, `and`↔`or`, `>`↔`>=`, `asc`↔`desc`, PowerShell karşılaştırma işleçleri) ve testin bunu yakalayıp yakalamadığına bakar. **Geçen** her mutantı tek tek incele:

- **Eşdeğer** (sonucu değiştirmiyor, ör. yerel sunucuda `timeout=5`→`6`): zararsız, rapora "eşdeğer" diye yaz.
- **Gerçek boşluk** (sonuç değişiyor ama test görmüyor): bulgu.

Uzun süren yollarda (Splunk, Elastic) `-u` ve dosyaya yönlendirme kullan; yoksa çıktı sonda tek seferde gelir.

### 6.5 Elle yanlış çözüm

Mutasyonun üretemediği, öğrencinin gerçekten yapacağı hataları yaz ve testin reddettiğini göster:

```python
import sys; sys.path.insert(0, ".")          # anlık görüntü kökünde çalıştır
from engine.lessons import Library
from engine import runners
L = Library()
st = next(s for s in L.lesson("python", "p82")["steps"] if s.get("title") == "İmzaları başlıktan kur")
kod = st["solution"].replace("[], c_void_p", "[], c_int")      # restype yanlış
r = runners.for_step(runners.get("python"), st).test(kod, st)
print(r["status"])                                             # "fail" beklenir
```

Mutantı az olan ya da hiç olmayan görevlerde bu adım zorunlu.

### 6.6 ASAMA2 karşılaştırması

```
python -X utf8 docs/denetim/araclar/madde.py <anlık görüntü> 61 62 63
```

Maddenin DENETIM.md durumunu ve ASAMA2 "neden / gerekir / kurulum" metnini yazdırır. Sonra ders dosyasını **baştan sona oku**: istenen her öğe derste var mı, görevde sınanıyor mu, yoksa yalnız anılıyor mu?

### 6.7 Mercek

Her maddede ayrıca sor:

- Gerçek araç ve gerçek veri mi (gerçek derleyici, gerçek Splunk, gerçek PCAP), yoksa benzetim mi?
- Saldırı tarafı (teknik nasıl çalışır, hangi iz kalır) ve savunma tarafı (hangi kayıt, hangi kural yakalar) bu ders için gerekiyorsa var mı?
- THM/HTB yolunda bu konuya gelen biri temeli buradan alıyor mu? Platformların atladığı kısım (çıktıyı okumak, betiği uyarlamak, biçimi anlamak) var mı?
- THM/HTB laboratuvarını kopyalamayı **önerme**; Pafta'nın işi o değil.

### 6.8 Rapor ve commit

Her madde için şablon (rapordaki mevcut maddelerle aynı):

```markdown
## Madde N · <yol> · <ASAMA2'deki ad>

- **Ders:** <id> (`<commit>`). Yazar: <ajan>.
- **Denetim:** validate (iki kabuk), tahmin, mutasyon (kaç mutant, kaçı geçti, geçenler eşdeğer mi), elle yanlış çözümler.
- **Karşılananlar:** ...
- **Eksikler:** her biri ayrı madde; ASAMA2'deki ifadeyi kalın yaz.
- **Karar:** **Tam / Kısmen / Eksik / Sorunlu.**
```

Birkaç maddede bir commit:

```
git commit -F - -- docs/denetim/madde-denetimi.md
```

Mesajın son satırı imzan. Ardından `python -X utf8 tools/takip_excel.py`.

## 7. Bilinen tuzaklar

- **Yeşil validate yeterli değildir.** Testi zayıf bir görev de "temiz" çıkar; mutasyon ve elle yanlış çözüm bunun için var.
- **DENETIM.md durum tablosu bayat olabilir** (bkz. 4). `git log -- tracks/<yol>/lessons/<ders>.md` ile doğrula.
- **Yazar raporundaki sayıya güvenme**; kendin ölç (A28).
- `runners.get(...)` yerine her zaman `runners.for_step(...)` (bkz. 3).
- Paralel test, paylaşılan dosyalarda yarış yaratabilir (ör. `ctypes_lab` derleme önbelleği; WinError 32). Tekrar koştur; kalıcıysa bulgu.
- Keep-alive kullanan tezgâhlarda, okunmamış istek gövdesi sonraki isteği bozar (vekilde yaşandı, düzeltildi). HTTP tezgâhında garip sırayla gelen hatalar görürsen buna bak.
- `madde-denetimi.md` karışık CRLF/LF satır sonu içerir; git uyarır, zararsız.
- Saldırı ayrıntısı içeren bazı konular (kimlik doğrulama hatası senaryoları, Impacket) bazı modellerde güvenlik filtresine takılabiliyor. Takılırsan zorlamadan rapora yaz ve kullanıcıya hangi ajana yönlendirileceğini söyle.

## 8. Durum (25 Ekim 2026)

- Maddeler **1–60 denetlendi** (`docs/denetim/madde-denetimi.md`). Tam 33 · Kısmen 25 · Eksik 2 (51, 52: ders yok).
- 1, 2 ve 5'in eksikleri kullanıcının isteğiyle kapatıldı (`892ced3`, `f834b74`); 7 (Impacket) başka ajana bırakıldı.
- SPL/Sigma mutasyonunda 34 mutantın 4'ü geçti (sp21:2, sp21:4, sg19:2, sg22:3; sonuncusu büyük olasılıkla eşdeğer). Henüz rapora işlenmedi.
- Sıradaki iş: **61'den 104'e** aynı yöntemle.
- Python yolu: 83 ders, validate temiz. Kazanım: PCEP 15/15, PCAP 19/21 (random, platform eksik), PCPP1 21/24 (tkinter 3.1–3.3 eksik).

## 9. Araçlar (`docs/denetim/araclar/`)

| Dosya | Kullanım |
|---|---|
| `madde.py` | `<kök> <no...>`: DENETIM durumu + ASAMA2 neden/gerekir/kurulum |
| `tahmin.py` | `<kök> <ders...>`: tahminleri kendi koşucularında çalıştırıp cevapla karşılaştırır |
| `mutasyon.py` | `<kök> [--en-cok N] <ders...>`: örnek çözümü bozar, geçen mutantları listeler |

`<kök>` = anlık görüntü klasörü (6.1).
