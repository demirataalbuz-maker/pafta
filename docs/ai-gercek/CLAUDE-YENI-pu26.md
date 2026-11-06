# Yeni ders pu26 (plan-purple-7, Tespiti doğrulama): yazar kontrolleri tamam, denetime hazır

- **Yazar:** claude-yazar.
- **Atama:** ortak pano 04.11.2026 18:13 (tüm yazım claude-yazar'a); Dalga B onayı 05.11 ("Hepsini onayla").
- **Puan** verilmedi; bağımsız denetim claude-opus'tadır.
- **Görsel sınama** yapılmadı; kabul CLI üzerinden `tools/validate.py` ile yapıldı.

## Eklenen / değişen dosyalar

- `tracks/purple/lessons/pu26-tespit-dogrulama.md` (sha256 e106de54e851c239…)
- `sandbox/purple_tespit_lab.py` (495d3d86010ab2c8…):
  - `pafta-linux-lab:13-1` konteynerini `--network none`, `--security-opt no-new-privileges`, `--pids-limit 256`, `--memory 512m`, `-u 0` ile açar; konteyner `--rm` ile atılır.
  - İçinde bir meşru gürültü grubu + 4 seçili dosya-tabanlı Atomic adımı strace altında koşar; konteyner içindeki güvenilir ayrıştırıcı ham strace'i normalleştirilmiş olaylara çevirir ve saldırı/iyi-huylu etiketler.
  - Referanslar (`referans_sinifla`/`referans_atomik`/`referans_kural`), `kod_koruma` ve `calistir`.
- `tracks/purple/fixtures/pu26_tespit/`: `ornekler.json` (sentetik olaylar + atomic yaml + kural + sınıflı liste) ve `README.md`.
- `.deps/atomic-red-team-a8f00488/atomics/T10*/…` (onaylı, hash doğrulanmış 6 YAML; ders 4'ünü kullanır).
- `outputs/yeni-pu26/pu26-*.json`: son kabul kanıtı.
- `tracks/purple/track.json`: mevcut "İstihbarattan Avcılığa" modülüne pu25'ten sonra yalnız `pu26` eklendi; panoda `uyari`/`bitti` yazıldı.
- `.deps/linux-lab-build/` (Dockerfile'lar): Dalga B kurulumunda eklendi, imajlar burada üretildi.
- `engine/` ve `web/` değişmedi. Commit/push yok.

## İçerik

### Görevler
1. **`olay_sinifla(olaylar)`:** Normalleştirilmiş strace olaylarını sınıflar: `execve`→`calistir` (hedef `argv[0]`), `openat` yazma bayrağı (`O_WRONLY/O_RDWR/O_CREAT/O_APPEND/O_TRUNC`) varsa `yaz` yoksa `oku`, `chmod/fchmodat/renameat2/unlinkat`→`yaz`. Kütüphane/proc gürültüsünü (`.so`, `/usr/lib`, `/proc` …) eler.
2. **`atomik_oku(yaml_metni)`:** Atomic Red Team YAML tanımını ayrıştırır: teknik, her testin adı, `guid`, `yukseltme` (`elevation_required: true`), çok satırlı `command`. `guid`'e göre sıralı; biçim/yineleme reddi.
3. **`kural_uygula(sinifli, kural)`:** Sigma benzeri kuralı (seçim: `comm`/`yon`/`hedef_icerir`, koşul `hepsi`/`herhangi`) sınıflı olaylara uygular.
4. **Gerçek deney:** Konteyner telemetrisinde kalıcılık kuralını (yön `yaz` + kabuk/cron hedefi) çalıştırır; saldırı yazımlarını yakaladığını (TP) ve meşru okumada yanlış pozitif vermediğini (FP=0) ölçer; yalnız hedefe bakan "saf" kuralın yanıldığını gösterir.

### KUSURLU başlangıç kodları
- **K1:** `olay_sinifla` okuma ile yazmayı ayırmaz, gürültüyü elemez (her şey "yaz").
- **K2:** `atomik_oku` `guid`'i ve biçimi doğrulamaz, yükseltme/komutu okumaz.
- **K3:** `kural_uygula` koşulu (`hepsi`/`herhangi`) ve yönü yok sayar, yalnız hedefe bakar.

## Gerçek final (son kabul koşusu)

- **Telemetri:** ~88 normalleştirilmiş olay (1 meşru grup + 4 saldırı adımı). Koşu 2,6–3,4 sn.
- **Kalıcılık kuralı (yön `yaz` + hedef):** TP 2, FP 0. `~/.bashrc` eklemesi ve `/etc/cron.d/` yazması yakalandı; `/etc/passwd` okuması (T1087, bir okuma) doğru biçimde görmezden gelindi.
- **Saf kural (yalnız hedef):** TP 8, FP 2. Meşru `cat ~/.bashrc` **okumasını** da bulgu saydı (hata vitrini).
- **Atomic:** 4 teknik (T1053.003, T1070.003, T1087.001, T1546.004) tanımdan doğru ayrıştırıldı.
- **İzolasyon:** `--network none`; konteyner `--rm` + açık `docker rm -f` ile atıldı, `cleanup: true`, `kabul: true`.
- İkinci ve üçüncü koşuda karar aynı (2/0 ve 8/2).

## Kendi kontrollerim (`.ai-venv/Scripts/python.exe -X utf8`)

- **`tools/validate.py pu26`:** TEMİZ, 9 kontrol (1 tahmin, 4 solution, 4 starter).
- **`tahmin.py`:** 1 tahmin, 0 şüpheli.
- **Mekanik mutasyon (`mutasyon.py --en-cok 1000`):** 80 mutant, 0 geçen.
  - İlk turda 4 `or→and` mutantı hayatta kaldı (boş `yol`, boş `ad` için test yoktu). `atomik_oku`'nun `- name:` ayrıştırmasını `\s*`'ten `[ \t]*`'e aldım (satır sonunu yutmuyordu) ve iki test durumu ekledim; çözüm değişmedi.
- **Elle anlamsal mutant (scratchpad `pu26_elle_mutant.py`):** 15 mutant, 0 geçen.
  - İlk turda 4 geçti: `.so` ile biten (ama `.so.` içermeyen) gürültü, `elevation_required: false`, teknik alt-numarasının basamak sayısı (`\d{3}` vs `\d+`) ve büyük harf `guid`. Dördü için de test eklendi; çözüm değişmedi.
- **Kopya sondası (`kopya_sonda.py`):** 7/7 reddedildi (modül takma adı, from import, importlib, `__import__`, inspect+exec, `*` import, doğru çözüm + eval).

## Denetçiye not / kapsam

- **strace bir EDR değildir.** Yalnız izlenen süreç ağacını görür; sistem geneli sensör değildir ve hedef süreç izlendiğini anlayabilir. Bu konteyner motorunda audit netlink arabirimi root + `--pid=host` ile bile `EPERM` döndü (ölçüldü); bu yüzden auditd yerine strace kullanıldı. Sigma eşlemesi dersin kendi alan adlarıyla yapılır; gerçek auditd/Sysmon kaynağında aynı sonucu verdiği iddia edilmez — ders bunu "sınır" cümlesinde açıkça yazar.
- **Kalıcılığın kurulumu ölçülür, tetiklenmesi değil.** cron işinin çalışması beklenmez (60 sn sınırı); kalıcılık dosya yazımı anında yakalanır. systemd konteynerde yoktur; servis kalıcılığı yalnız birim dosyası düzeyinde anılır.
- **TP/FP oranları yalnız bu küçük örnek içindir;** kuralın genel başarısını ölçmez. Yük altında olay sayısı birkaç olay oynar; karar (2/0, saf FP≥1) sabittir.
- Atomic adımları yalnız izin listesindeki 4 zararsız dosya-tabanlı test; deponun ağa çıkan/FreeBSD/elevation testleri koşmaz.
- Windows tarafı ve gerçek EDR telemetrisi Dalga C'ye kalır.

## Sıradaki

Dalga B'de kalan: purple-3 (çalıştırma/kalıcılık), klasik-3 (pwn), klasik-4 (tersine mühendislik), purple-2 (olta tatbikatı). Her biri ayrı denetime.
