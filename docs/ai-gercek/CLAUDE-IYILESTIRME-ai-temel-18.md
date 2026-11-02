# ai-temel-18 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Tablo ve `[!NOT]`:** İlk anlatımın başına tablo eklendi.
  - **Gerçekte ne olur:** `docker run` bayrakları `HostConfig` alanlarına iner. Çekirdek bunları namespace, cgroup v2 (`memory.max`, `pids.max`, `cpu.max`), capability ve seccomp olarak uygular.
  - **Ders ne kullanır:** Görev 1–3 sentetik dizgeler, token listeleri ve bağlamalar kullanır. Son adım yerel `busybox` imajıyla iki gerçek `docker run --rm` konteyneri başlatır ve cgroup değerlerini içeriden okur.
  - **Ders ne söyleyemez:** Çekirdek açığı, kaçış, seccomp profili, symlink ve rootless kurulum sınanmaz. Görev 2 Docker CLI'ın yalnız bir alt kümesini tanır.

  Tablonun altına sentetik veri ve kalıcılık notu eklendi. Not, imajın indirilmediğini ve konteynerlerin `--rm` ile silindiğini de söylüyor.
- **Çelişki düzeltmesi:** İkinci anlatım "Bu derste Docker çalıştırılmaz ve konteyner başlatılmaz" diyordu, oysa son adım gerçek konteyner başlatıyor. Cümle, görev 1–3 ile son adımı ayıracak şekilde düzeltildi.
- **Görünür fixture:** `tracks/ai-temel/fixtures/ai-temel-18/` altına README ve üç dosya eklendi. Temel yolunun düzeni korundu: dosyalar klasörde düz durur ve `veri/` altına kopyalanır. Beklenen değerler dersin kendi çözümleriyle hesaplandı.
  - `kaynak_sinirlari.json`: 13 örnek. 7 geçerli: 3g bellek+takas toplamı, `"0"` takas, `1.000000001` CPU, `6144k` (1024 tabanı) ve diğerleri. 6 `ValueError`: `mb`, `1.5g`, küçük takas, 6m altı, fazla CPU, 0.01 altı.
  - `run_komutlari.json`: 9 komut.
    - Sertleştirilmiş llama.cpp sunucusu: bulgu yok.
    - Sertleştirmesiz model sunucusu: 7 bulgu.
    - İmajdan sonraki `--privileged` konteyner komutuna aittir.
    - `/var/run/../run/docker.sock` normalleştirilince docker.sock olur.
    - `--pids-limit -1` sınır değildir; `--user 00:0` root'tur.
    - 4 `ValueError`.
  - `baglamalar.json`: 11 bağlama. 4 izinli; 7 red: `izinsiz` (`modeller-yedek` önek tuzağı), `kacis`, `sock`, `kok`, `yinelenen` ve iki `yazilabilir_model`.
- **Kusurlu başlangıç kodları:**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | 1000 tabanı; `mb`/boşluk kırpma; takas toplamı yanlış; float NanoCpus; sınır yok | 13 örneğin 13'ü yanlış |
  | 2 | Birleştirilmiş metinde alt metin; normalleştirme yok; `=` ve küçük `all` tanınmıyor; doğrulama yok | 9 komutun 8'i yanlış |
  | 3 | `/`'süz önek; `..` normalleştirmeden sonra aranıyor; sock/kök/yinelenen/yazılabilir model denetlenmiyor | Binds yanlış; 7 redden 7'si bulunamıyor; 4 fazla red |
  | Gerçek deney | `--memory-swap` yok; ağ kararı ters; `--cap-drop=all` küçük harf ve NNP yok | Sözleşme düşüyor; `all(sonuclar)` kapısı canlı deneyi başlatmıyor (kanıt dosyasında `deney: null`) |

- **Kısa notlar:** Her göreve sık tuzaklar eklendi.
- **Kopya koruması:**
  - Var olan yasak listesi (`referans`, `referans_argv`, `getattr`) korundu; `kanit_yaz` eklendi.
  - AST kontrolü eklendi: takma adlı ve `*` import, `inspect`, `importlib`, `runpy`, `exec`, `eval`, `compile`, `__builtins__`. İhlalde `stop()` çalışıyor.
- **Değiştirilmeyenler:** `sandbox/ai_gercek_ai_temel_18.py`, ortak `ai_temel_veri.py`, var olan bütün testler, `engine/` ve `web/`. Docker Desktop ayarlarına ve kullanıcının var olan konteynerlerine dokunulmadı.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

| Kontrol | Sonuç |
|---|---|
| validate `ai-temel-18` | **TEMİZ**, 9 kontrol, ilk koşuda. Adım yapısı (`anlat, anlat, tahmin, gorev ×4`) değişmedi. |
| tahmin | 1 tahmin, **0 şüpheli** |
| mutasyon (`kirp_gercek.py` kopyası) | 32 + 26 + 29 = **87 mutant, 0 geçen**; kopya silindi |
| kopya sondası | 6/6 **fail → korunuyor**. Sondalar `referans_argv` için: takma ad, öznitelik, `vars()`, `inspect` + `exec`, `*` import + `globals()`, `importlib` + `__dict__`. Bu derste `getattr` zaten yasaklı olduğu için `getattr` yerine `vars()` denendi. Doğru çözüme yalnız `import inspect` ya da `eval('1')` eklendiğinde de fail. |

Görünür veri kontrolü: Üç başlangıç kodu ve çözüm görünür fixture'larla ayrı ayrı çalıştırıldı. Tablodaki kusurlar görüldü; çözümler bütün beklenen değerleri verdi.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/st18-kabul/ai-kanit/temel-konteyner-*.json` (kabul `true`). Ortam: Docker 29.9.2, `busybox:1.36`, cgroup v2.
- **Sertleştirilmiş konteyner:**
  - `memory.max` = 33554432 (32 MiB, beklenenle aynı).
  - `pids.max` = 16; fork engellendi.
  - Arayüz yalnız `lo`; ağ ve yazma reddedildi.
  - Dört denetimin dördü uygulandı.
- **Sınırsız taban:** `memory.max` ve `pids.max` yok, `eth0` var, yazma ve ağ açık; hiçbir denetim uygulanmadı.
- **Temizlik:** Validate sonrası `docker ps -a` çıktısında dersin bıraktığı bir konteyner yoktu; görülenler kullanıcının önceki konteynerleri.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.**
- **Kurulum, imaj indirme, commit/push ve puan yazımı yapılmadı.**
