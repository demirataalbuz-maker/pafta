---
id: pu15
title: Windows Adli İzleri · Registry, Prefetch, MFT ve LNK
summary: CDSA düzeyinde Registry anahtar-değer ve LastWriteTime sınırını, Prefetch ad/hash ve run count sınırlarını, MFT SI/FN MACB zamanları ile resident/nonresident ayrımını, LNK hedef ve zamanlarını sentetik kayıtlarda incelemek; UTC zaman çizelgesi kurarken çelişkili kanıtları birleştirip uydurma tek gerçek üretmemek.
timeout: 60
---

::: anlat Gerçek biçimi bil, sentetik temsili ayırt et
Bu ders Windows adli izlerinin **gerçek dosya biçimlerindeki anlamını** öğretir; fakat örnekler ham kanıt değildir. `adli/` altındaki küçük JSON dosyaları elle yazılmış, sentetik ve normalize edilmiştir. Yardımcı yalnız bu dosyaları kopyalar/okur. Ham hive, Prefetch, MFT veya LNK ayrıştırılmaz; canlı Registry ve dosya sistemi taranmaz, kanıt toplanmaz, paket kurulmaz.

| İz | Gerçek biçimde ne vardır? | Ne söyleyemez? |
|---|---|---|
| Registry hive | `nk` anahtar ve `vk` değer kayıtları; anahtarın LastWriteTime değeri | Bir değerin bağımsız yazılma zamanını veya programın çalıştığını |
| Prefetch | Yürütülebilir ad, yol hash'i, sürüme bağlı run count ve son çalıştırma zamanları | Bütün çalıştırmaları, her sayının güvenilirliğini veya zararlılığı |
| NTFS `$MFT` | Dosya kaydı, `$STANDARD_INFORMATION` (SI), `$FILE_NAME` (FN), `$DATA` gibi öznitelikler | Tek zamanın niçin değiştiğini kendiliğinden açıklamayı |
| Shell Link `.lnk` | LinkFlags, hedef bilgisi, StringData, ExtraData ve hedef zamanları | Kullanıcının hedefi gerçekten açtığını tek başına kanıtlamayı |

> [!GÜVENLİK]
> Bu çıktılar bir toplama aracının gerçek çıktısı değildir. Olay yeri disiplini, salt okunur edinim, hash doğrulaması, zincir-of-custody ve yetkili inceleme bu laboratuvarın kapsamı dışındadır. Buradaki sonuç “kesin kurcalama” veya “kesin çalıştırma” hükmü değildir.
:::

::: anlat Registry ve Prefetch alanlarını sınırlarıyla oku
Bir **Registry hive** (`NTUSER.DAT`, `SYSTEM` gibi) anahtar ağacını ve değerleri tutar. Anahtar yol ile, değer ise `value_name` ve `value_type` (`REG_SZ`, `REG_DWORD`, `REG_BINARY` vb.) ile tanımlanır. Gerçek hive'ın hücre yapısında anahtar `nk`, değer `vk` kaydıdır. **LastWriteTime anahtarın alanıdır**: aynı anahtarın hangi değerinin ne zaman değiştiğini tek başına göstermez; silinen değer için geçmiş sağlamaz ve otomatik çalıştırma kanıtı değildir.

Prefetch dosya adı olağan olarak `PROGRAM.EXE-HASH.pf` biçimindedir. Hash, dosyanın kriptografik içerik özeti değil, Prefetch'in yol bağlamıyla ilişkili kimliğidir. Aynı yürütülebilir adın farklı yolları farklı hash üretebilir. Bu derste `file_name`, `executable_name` ve `path_hash` tutarlılığı denetlenir; hash yeniden hesaplanmaz.

Gerçek Prefetch başlık ve alan yerleşimi Windows sürümüne bağlıdır; yeni sürümlerde dosya MAM ile sıkıştırılmış olabilir. Eski sürümlerde tek son çalıştırma zamanı, daha yeni sürümlerde tipik olarak sekize kadar zaman tutulabilir. Dolayısıyla listedeki zaman sayısı toplam çalıştırma sayısı değildir. `run_count` da sınırsız ve değiştirilemez bir sayaç değildir: sürüm, sistem davranışı, bozulma veya kurcalama nedeniyle dikkatle yorumlanır. En yeni saklanan zaman `max(last_run_times)` ile bulunur; listenin yazım sırasına güvenilmez.
:::

::: tahmin Hangi zaman en yeni saklanan çalıştırmadır?
```python
from windows_forensics_lab import zaman
zamanlar = ["2026-10-20T08:12:00Z", "2026-10-20T11:20:00+03:00"]
print([zaman(z) for z in zamanlar])
print(max(zaman(z) for z in zamanlar))
```

???

```
['2026-10-20 08:12:00', '2026-10-20 08:20:00']
2026-10-20 08:20:00
```

`+03:00` yazımı önce UTC'ye çevrilir. İki saklanan zaman olması run count'un 2 olduğunu göstermez; bu fixture'da sayaç 7'dir ve yalnız iki zaman korunmuştur.

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
```
:::

::: gorev 1 · Registry ve Prefetch kayıtlarını normalize et
`registry_izleri(rows)` her satır için `{"hive", "anahtar", "deger_ad", "deger_turu", "last_write_utc", "kapsam"}` döndürsün. `kapsam` sabit olarak `"anahtar-last-write"` olmalı; sonuç `(hive, anahtar, deger_ad)` ile sıralanmalı.

`prefetch_izleri(rows)` şu alanları döndürsün:

```text
{"dosya_ad": özgün ad, "yurutulebilir": özgün ad, "hash": büyük harf,
 "son_calistirma_utc": UTC metni, "run_count": int,
 "saklanan_zaman_sayisi": int, "yorum": "sinirli-son-calisma-listesi"}
```

Dosya adı, büyük/küçük harf duyarsız `YURUTULEBILIR-HASH.pf` kalıbıyla uyuşmuyorsa `ValueError` ver. Zamanları UTC'ye çevirip en büyüğünü seç; `run_count` değerini listeden türetme. Sonucu dosya adına göre sırala.

```starter
from windows_forensics_lab import json_yukle, zaman
registry = json_yukle("adli/registry.json")
prefetch = json_yukle("adli/prefetch.json")

def registry_izleri(rows):
    return [{"hive": r["hive"], "deger_ad": r["value_name"],
             "last_write_utc": r["last_write_time"]} for r in rows]

def prefetch_izleri(rows):
    return [{"dosya_ad": r["file_name"],
             "son_calistirma_utc": zaman(r["last_run_times"][0]),
             "run_count": len(r["last_run_times"])} for r in rows]

print(registry_izleri(registry))
print(prefetch_izleri(prefetch))
```

```test
need("registry_izleri"); need("prefetch_izleri")
rs = registry_izleri(registry); ps = prefetch_izleri(prefetch)
eq(len(rs), 2, "iki normalize Registry satırı")
run = next(r for r in rs if r["hive"] == "NTUSER.DAT")
eq(run, {"hive": "NTUSER.DAT", "anahtar": "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
         "deger_ad": "Updater", "deger_turu": "REG_SZ", "last_write_utc": "2026-10-20 08:15:00",
         "kapsam": "anahtar-last-write"}, "+03:00 UTC'ye çevrilir; LastWriteTime anahtara ait")
eq([r["hive"] for r in rs], ["NTUSER.DAT", "SYSTEM"], "kararlı Registry sırası")
eq(len(ps), 2, "iki Prefetch kaydı korunur")
tool = next(p for p in ps if p["yurutulebilir"] == "TOOL.EXE")
eq(tool, {"dosya_ad": "TOOL.EXE-9A1B2C3D.pf", "yurutulebilir": "TOOL.EXE", "hash": "9A1B2C3D",
          "son_calistirma_utc": "2026-10-20 08:20:00", "run_count": 7,
          "saklanan_zaman_sayisi": 2, "yorum": "sinirli-son-calisma-listesi"},
   "son zaman max; run count saklanan zaman sayısından türetilmez")
bozuk = [dict(prefetch[0], file_name="TOOL.EXE-FFFFFFFF.pf")]
try:
    prefetch_izleri(bozuk)
    ok(False, "dosya adındaki hash uyuşmazlığı yakalanmalı")
except ValueError:
    ok(True, "dosya adı/hash uyuşmazlığı")
```

```solution
from windows_forensics_lab import json_yukle, zaman
registry = json_yukle("adli/registry.json")
prefetch = json_yukle("adli/prefetch.json")

def registry_izleri(rows):
    sonuc = []
    for r in rows:
        sonuc.append({"hive": r["hive"], "anahtar": r["key_path"],
                      "deger_ad": r["value_name"], "deger_turu": r["value_type"],
                      "last_write_utc": zaman(r["last_write_time"]),
                      "kapsam": "anahtar-last-write"})
    return sorted(sonuc, key=lambda r: (r["hive"], r["anahtar"], r["deger_ad"]))

def prefetch_izleri(rows):
    sonuc = []
    for r in rows:
        ad = r["executable_name"]
        ozet = r["path_hash"].upper()
        beklenen = f"{ad}-{ozet}.pf"
        if r["file_name"].lower() != beklenen.lower():
            raise ValueError("Prefetch dosya adı, yürütülebilir ad veya hash ile uyuşmuyor")
        zamanlar = [zaman(t) for t in r["last_run_times"]]
        if not zamanlar:
            raise ValueError("En az bir sentetik son çalıştırma zamanı gerekli")
        sonuc.append({"dosya_ad": r["file_name"], "yurutulebilir": ad, "hash": ozet,
                      "son_calistirma_utc": max(zamanlar), "run_count": int(r["run_count"]),
                      "saklanan_zaman_sayisi": len(zamanlar),
                      "yorum": "sinirli-son-calisma-listesi"})
    return sorted(sonuc, key=lambda p: p["dosya_ad"])

print(registry_izleri(registry))
print(prefetch_izleri(prefetch))
```

```hint
Registry'de `key_path` alanını kaybetme. Prefetch'te beklenen dosya adını f-string ile kur, `.lower()` karşılaştır; zaman listesini normalize ettikten sonra `max` kullan ve sayaç için doğrudan `int(r["run_count"])` yaz.
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from windows_forensics_lab import hazirla
hazirla()
```
:::

::: anlat MFT özniteliklerini ve MACB'yi karıştırma
NTFS `$MFT` içindeki her kayıt özniteliklerden oluşur. `$STANDARD_INFORMATION` (SI) çoğu araçta dosya meta verisi görünümünü, `$FILE_NAME` (FN) ise ad ve üst dizin ilişkisini taşır. Her ikisinde dört zaman görülebilir:

- **M — Modified:** içerik değişikliği bağlamındaki değiştirilme zamanı.
- **A — Accessed:** erişim zamanı; güncelleme davranışı sistem ayarlarına bağlı olabilir.
- **C — Changed:** SI için MFT/meta veri değişimi bağlamındaki değişim zamanı; “içerik değişti” diye genellenmez.
- **B — Birth:** oluşturulma zamanı; kopyalama ve taşıma davranışları yorumu etkiler.

SI ve FN aynı sıklıkta güncellenmez. FN zamanlarının geçmiş görünmesi veya SI'dan farklı olması tek başına **timestomp** kanıtı değildir. İki alan grubunu ayrı sakla ve farkı `si-fn:<harf>` olarak raporla. Ayrıca `Changed` ile `Birth` harflerini değiştirme.

`resident`/`nonresident` bütün dosya kaydının MFT'de olup olmaması değil, özellikle `$DATA` gibi bir özniteliğin içeriğinin kayıt içinde mi, yoksa dış veri çalıştırmalarında (data runs) mı tutulduğudur. Küçük veri resident olabilir; nonresident içerik MFT kaydının içine gömülü değildir. Bu ders dosya içeriği okumaz, yalnız `data_resident` alanını etiketler.

Bir `.lnk` ise hedef yol, çalışma dizini ve hedefe ait M/A/B zamanlarını içerebilir. LNK'nin kendi dosya sistemindeki oluşturulma/değiştirilme zamanları **içteki hedef zamanları değildir**. Bu fixture'da ikinci grup `external_file_times` adıyla özellikle ayrılmıştır.
:::

::: gorev 2 · MFT SI/FN ve LNK zamanlarını ayrı koru
`mft_izleri(rows)` her kayıt için şu yapıyı döndürsün:

```text
{"kayit_no": int, "yol": str, "data_depo": "resident" veya "nonresident",
 "si": {"m", "a", "c", "b"}, "fn": {"m", "a", "c", "b"},
 "farklar": ["si-fn:a", ...]}
```

SI/FN sözlüklerinin anahtarları sırasıyla `modified`, `accessed`, `changed`, `birth` alanlarından UTC'ye çevrilir. Dört alanı karşılaştırıp farklı olanları `si-fn:<harf>` biçiminde, MACB sırasıyla yaz. Kayıtları `kayit_no` ile sırala.

`lnk_izleri(rows)` şu yapıyı döndürsün:

```text
{"lnk": str, "hedef": str, "calisma_dizini": str,
 "hedef_zamanlari_utc": {"m", "a", "b"},
 "dis_zamanlar_utc": {"m", "b"}}
```

İç hedef zamanlarıyla dış LNK dosya zamanlarını birbirinin üzerine yazma; LNK adına göre sırala.

```starter
from windows_forensics_lab import json_yukle, zaman
mft = json_yukle("adli/mft.json")
lnk = json_yukle("adli/lnk.json")

def mft_izleri(rows):
    return [{"kayit_no": r["record_number"], "yol": r["file_path"],
             "si": r["standard_information"], "fn": r["file_name"],
             "farklar": []} for r in rows]

def lnk_izleri(rows):
    return [{"lnk": r["lnk_name"], "hedef": r["target_path"],
             "hedef_zamanlari_utc": r["target_times"]} for r in rows]

print(mft_izleri(mft))
print(lnk_izleri(lnk))
```

```test
need("mft_izleri"); need("lnk_izleri")
ms = mft_izleri(mft); ls = lnk_izleri(lnk)
eq([m["kayit_no"] for m in ms], [12890, 13001], "MFT kayıt sırası")
tool = ms[0]
eq(tool["data_depo"], "nonresident", "nonresident $DATA içeriği MFT kaydına gömülü değildir")
eq(tool["si"], {"m": "2026-10-20 08:24:00", "a": "2026-10-20 08:26:00",
                "c": "2026-10-20 08:25:00", "b": "2026-10-20 08:25:00"}, "SI MACB eşlemesi ve UTC")
eq(tool["fn"], {"m": "2026-10-20 08:01:00", "a": "2026-10-20 08:02:00",
                "c": "2026-10-20 08:03:00", "b": "2026-10-20 08:05:00"}, "FN ayrı saklanır")
eq(tool["farklar"], ["si-fn:m", "si-fn:a", "si-fn:c", "si-fn:b"], "dört SI/FN farkı; kurcalama hükmü değil")
eq(ms[1]["data_depo"], "resident", "küçük sentetik $DATA resident")
eq(ms[1]["farklar"], [], "eşit SI/FN fark üretmez")
eq(ls, [{"lnk": "tool.exe.lnk", "hedef": "C:\\Users\\ayse\\Downloads\\tool.exe",
         "calisma_dizini": "C:\\Users\\ayse\\Downloads",
         "hedef_zamanlari_utc": {"m": "2026-10-20 08:09:00", "a": "2026-10-20 08:11:00", "b": "2026-10-20 08:10:00"},
         "dis_zamanlar_utc": {"m": "2026-10-20 08:35:00", "b": "2026-10-20 08:34:00"}}],
   "hedef, çalışma dizini, iç ve dış zamanlar ayrı")
```

```solution
from windows_forensics_lab import json_yukle, zaman
mft = json_yukle("adli/mft.json")
lnk = json_yukle("adli/lnk.json")
MACB = (("m", "modified"), ("a", "accessed"), ("c", "changed"), ("b", "birth"))

def macb_utc(row):
    return {harf: zaman(row[alan]) for harf, alan in MACB}

def mft_izleri(rows):
    sonuc = []
    for r in rows:
        si = macb_utc(r["standard_information"])
        fn = macb_utc(r["file_name"])
        sonuc.append({"kayit_no": int(r["record_number"]), "yol": r["file_path"],
                      "data_depo": "resident" if r["data_resident"] else "nonresident",
                      "si": si, "fn": fn,
                      "farklar": [f"si-fn:{harf}" for harf, _ in MACB if si[harf] != fn[harf]]})
    return sorted(sonuc, key=lambda m: m["kayit_no"])

def lnk_izleri(rows):
    sonuc = []
    for r in rows:
        hedef = r["target_times"]
        dis = r["external_file_times"]
        sonuc.append({"lnk": r["lnk_name"], "hedef": r["target_path"],
                      "calisma_dizini": r["working_directory"],
                      "hedef_zamanlari_utc": {h: zaman(hedef[a]) for h, a in (("m", "modified"), ("a", "accessed"), ("b", "birth"))},
                      "dis_zamanlar_utc": {h: zaman(dis[a]) for h, a in (("m", "modified"), ("b", "birth"))}})
    return sorted(sonuc, key=lambda l: l["lnk"])

print(mft_izleri(mft))
print(lnk_izleri(lnk))
```

```hint
Ortak `MACB` eşlemesini kullan; iki MFT özniteliğine aynı dönüşümü uygula ama sözlükleri ayrı bırak. LNK'de iki ayrı kapsayıcı kur: hedef M/A/B ve dış M/B.
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from windows_forensics_lab import hazirla
hazirla()
```
:::

::: anlat UTC çizelgesi kur; çelişkiyi “düzeltme”
Zaman çizelgesinde her gözlem ayrı olaydır: kaynak, kanıt kimliği, alan ve MACB etiketi korunur. ISO `Z` UTC demektir; `+03:00` gibi offset'ler UTC'ye çevrilir. Saat dilimi olmayan metni yerel saat kabul edip tahmin yürütme. Bu dersin `zaman()` yardımcısı böyle değerlerde `ValueError` verir.

Çelişki, iki kaynağı zorla aynı değere dönüştürme nedeni değildir. Örneğin Prefetch son çalıştırması MFT SI Birth'ten önce görünebilir; LNK hedef Birth ile MFT SI Birth farklı olabilir. Bunlar inceleme gerektiren **kaynaklar arası farklardır**. Dosya kopyalama, farklı öznitelik güncellemeleri, saat/ayar sorunları, araç yorumu veya kurcalama gibi olasılıklar bu sentetik veriyle ayrılamaz. Her iki zaman da çizelgede kalır; ayrı çelişki kaydı iki kanıt kimliğini ve iki özgün UTC zamanını gösterir. “Ortalama almak”, yeni kaynak seçmek veya eski olayı silmek kanıt uydurur.
:::

::: gorev 3 · UTC olayları ve çelişkileri ayrı raporla
Önceki görevlerin dört normalizasyon işlevini ve `MACB`/`macb_utc` yardımcılarını kopyala. `zaman_raporu(rs, ps, ms, ls)` şu sözlüğü döndürsün:

```text
{"olaylar": [{"zaman", "kaynak", "kanit_id", "alan", "macb"}],
 "celiskiler": [{"kod", "kaynaklar", "zamanlar", "yorum"}]}
```

Olayları şöyle üret:

- Registry: `kaynak="registry"`, kimlik `hive + "!" + anahtar`, alan `LastWriteTime`, `macb=""`.
- Prefetch: yalnız en yeni saklanan zaman, `kaynak="prefetch"`, kimlik dosya adı, alan `son_calistirma`, `macb=""`.
- MFT: SI ve FN için ayrı olaylar; kaynak `mft-si`/`mft-fn`, kimlik `str(kayit_no) + "!" + yol`, alan `si.m` gibi, MACB büyük harf.
- LNK: hedef M/A/B için `kaynak="lnk-target"`, dış M/B için `kaynak="lnk-dis"`; kimlik LNK adı, alan `hedef.m` veya `dis.m`, MACB büyük harf.

Olayları `(zaman, kaynak, kanit_id, alan)` ile sırala. Ardında yalnız şu iki çelişki sınıfını üret:

1. Aynı yürütülebilir dosya adı için Prefetch son çalıştırması `<` MFT SI Birth ise `calistirma-si-dogum-oncesi`.
2. LNK hedefi MFT yoluyla eşleşiyor ve hedef Birth `!=` MFT SI Birth ise `lnk-mft-dogum-farki`.

Yol eşlemesinde `\`/`/` farkını ve büyük/küçük harfi normalize et; sürücü önekine güvenmeden yol sonu eşleşmesi kullan. Çelişkide `kaynaklar` iki kanıt kimliğinin sıralı listesi, `zamanlar` ise `{"bir": ..., "iki": ...}` olsun; `yorum` sabit `"kaynaklar-ayri-koru"` olmalı. Çelişkileri `(kod, kaynaklar)` ile sırala. Hiçbir olayı silme, zamanı değiştirme veya girdileri güncelleme.

```starter
from windows_forensics_lab import json_yukle, zaman
registry = json_yukle("adli/registry.json")
prefetch = json_yukle("adli/prefetch.json")
mft = json_yukle("adli/mft.json")
lnk = json_yukle("adli/lnk.json")

def zaman_raporu(rs, ps, ms, ls):
    olaylar = []
    for p in ps:
        olaylar.append({"zaman": p["son_calistirma_utc"], "kaynak": "prefetch",
                        "kanit_id": p["dosya_ad"], "alan": "son_calistirma", "macb": ""})
    return {"olaylar": olaylar, "celiskiler": []}

print(zaman_raporu([], [], [], []))
```

```test
import copy
need("zaman_raporu"); need("registry_izleri"); need("prefetch_izleri"); need("mft_izleri"); need("lnk_izleri")
rs = registry_izleri(registry); ps = prefetch_izleri(prefetch)
ms = mft_izleri(mft); ls = lnk_izleri(lnk)
girdi = copy.deepcopy((rs, ps, ms, ls))
r = zaman_raporu(rs, ps, ms, ls)
eq(len(r["olaylar"]), 25, "2 Registry + 2 Prefetch + 16 MFT + 5 LNK olayı ayrı kalır")
eq([o["zaman"] for o in r["olaylar"]], sorted(o["zaman"] for o in r["olaylar"]), "UTC artan sıra")
eq(len([o for o in r["olaylar"] if o["kaynak"] == "mft-si"]), 8, "iki kayıt × dört SI zamanı")
eq(len([o for o in r["olaylar"] if o["kaynak"] == "mft-fn"]), 8, "iki kayıt × dört FN zamanı")
eq(len([o for o in r["olaylar"] if o["kaynak"] == "lnk-target"]), 3, "LNK hedef M/A/B")
eq(len([o for o in r["olaylar"] if o["kaynak"] == "lnk-dis"]), 2, "dış LNK M/B hedefle birleştirilmez")
eq([(c["kod"], c["zamanlar"]) for c in r["celiskiler"]],
   [("calistirma-si-dogum-oncesi", {"bir": "2026-10-20 08:20:00", "iki": "2026-10-20 08:25:00"}),
    ("lnk-mft-dogum-farki", {"bir": "2026-10-20 08:10:00", "iki": "2026-10-20 08:25:00"})],
   "çelişkili iki zaman korunur; tek zaman uydurulmaz")
ok(all(c["yorum"] == "kaynaklar-ayri-koru" and len(c["kaynaklar"]) == 2 for c in r["celiskiler"]),
   "iki kaynak kimliği ve sınırlı yorum")
eq((rs, ps, ms, ls), girdi, "rapor girdileri değiştirmez")
eski = copy.deepcopy(ms); eski[0]["si"]["b"] = "2026-10-20 08:15:00"
r2 = zaman_raporu(rs, ps, eski, ls)
eq([c["kod"] for c in r2["celiskiler"]], ["lnk-mft-dogum-farki"],
   "Prefetch artık Birth'ten önce değil; LNK farkı bağımsız kalır")
```

```solution
from windows_forensics_lab import json_yukle, zaman
registry = json_yukle("adli/registry.json")
prefetch = json_yukle("adli/prefetch.json")
mft = json_yukle("adli/mft.json")
lnk = json_yukle("adli/lnk.json")
MACB = (("m", "modified"), ("a", "accessed"), ("c", "changed"), ("b", "birth"))

def registry_izleri(rows):
    sonuc = []
    for r in rows:
        sonuc.append({"hive": r["hive"], "anahtar": r["key_path"],
                      "deger_ad": r["value_name"], "deger_turu": r["value_type"],
                      "last_write_utc": zaman(r["last_write_time"]), "kapsam": "anahtar-last-write"})
    return sorted(sonuc, key=lambda r: (r["hive"], r["anahtar"], r["deger_ad"]))

def prefetch_izleri(rows):
    sonuc = []
    for r in rows:
        ad = r["executable_name"]
        ozet = r["path_hash"].upper()
        if r["file_name"].lower() != f"{ad}-{ozet}.pf".lower():
            raise ValueError("Prefetch dosya adı, yürütülebilir ad veya hash ile uyuşmuyor")
        zamanlar = [zaman(t) for t in r["last_run_times"]]
        if not zamanlar:
            raise ValueError("En az bir sentetik son çalıştırma zamanı gerekli")
        sonuc.append({"dosya_ad": r["file_name"], "yurutulebilir": ad, "hash": ozet,
                      "son_calistirma_utc": max(zamanlar), "run_count": int(r["run_count"]),
                      "saklanan_zaman_sayisi": len(zamanlar), "yorum": "sinirli-son-calisma-listesi"})
    return sorted(sonuc, key=lambda p: p["dosya_ad"])

def macb_utc(row):
    return {harf: zaman(row[alan]) for harf, alan in MACB}

def mft_izleri(rows):
    sonuc = []
    for r in rows:
        si = macb_utc(r["standard_information"])
        fn = macb_utc(r["file_name"])
        sonuc.append({"kayit_no": int(r["record_number"]), "yol": r["file_path"],
                      "data_depo": "resident" if r["data_resident"] else "nonresident",
                      "si": si, "fn": fn,
                      "farklar": [f"si-fn:{h}" for h, _ in MACB if si[h] != fn[h]]})
    return sorted(sonuc, key=lambda m: m["kayit_no"])

def lnk_izleri(rows):
    sonuc = []
    for r in rows:
        hedef = r["target_times"]
        dis = r["external_file_times"]
        sonuc.append({"lnk": r["lnk_name"], "hedef": r["target_path"], "calisma_dizini": r["working_directory"],
                      "hedef_zamanlari_utc": {h: zaman(hedef[a]) for h, a in (("m", "modified"), ("a", "accessed"), ("b", "birth"))},
                      "dis_zamanlar_utc": {h: zaman(dis[a]) for h, a in (("m", "modified"), ("b", "birth"))}})
    return sorted(sonuc, key=lambda l: l["lnk"])

def olay(z, kaynak, kimlik, alan, macb=""):
    return {"zaman": z, "kaynak": kaynak, "kanit_id": kimlik, "alan": alan, "macb": macb}

def yol_adi(yol):
    return yol.replace("/", "\\").rstrip("\\").lower().split("\\")[-1]

def ayni_yol(bir, iki):
    a = bir.replace("/", "\\").rstrip("\\").lower()
    b = iki.replace("/", "\\").rstrip("\\").lower()
    return a == b or a.endswith("\\" + b) or b.endswith("\\" + a)

def zaman_raporu(rs, ps, ms, ls):
    olaylar = []
    for r in rs:
        olaylar.append(olay(r["last_write_utc"], "registry", r["hive"] + "!" + r["anahtar"], "LastWriteTime"))
    for p in ps:
        olaylar.append(olay(p["son_calistirma_utc"], "prefetch", p["dosya_ad"], "son_calistirma"))
    for m in ms:
        for kisaltma, kaynak in (("si", "mft-si"), ("fn", "mft-fn")):
            for harf, _ in MACB:
                olaylar.append(olay(m[kisaltma][harf], kaynak, str(m["kayit_no"]) + "!" + m["yol"],
                                    kisaltma + "." + harf, harf.upper()))
    for l in ls:
        for harf, z in l["hedef_zamanlari_utc"].items():
            olaylar.append(olay(z, "lnk-target", l["lnk"], "hedef." + harf, harf.upper()))
        for harf, z in l["dis_zamanlar_utc"].items():
            olaylar.append(olay(z, "lnk-dis", l["lnk"], "dis." + harf, harf.upper()))
    celiskiler = []
    for p in ps:
        for m in ms:
            if yol_adi(p["yurutulebilir"]) != yol_adi(m["yol"]):
                continue
            if p["son_calistirma_utc"] < m["si"]["b"]:
                celiskiler.append({"kod": "calistirma-si-dogum-oncesi",
                                   "kaynaklar": sorted([p["dosya_ad"], str(m["kayit_no"]) + "!" + m["yol"]]),
                                   "zamanlar": {"bir": p["son_calistirma_utc"], "iki": m["si"]["b"]},
                                   "yorum": "kaynaklar-ayri-koru"})
    for l in ls:
        for m in ms:
            if ayni_yol(l["hedef"], m["yol"]) and l["hedef_zamanlari_utc"]["b"] != m["si"]["b"]:
                celiskiler.append({"kod": "lnk-mft-dogum-farki",
                                   "kaynaklar": sorted([l["lnk"], str(m["kayit_no"]) + "!" + m["yol"]]),
                                   "zamanlar": {"bir": l["hedef_zamanlari_utc"]["b"], "iki": m["si"]["b"]},
                                   "yorum": "kaynaklar-ayri-koru"})
    return {"olaylar": sorted(olaylar, key=lambda o: (o["zaman"], o["kaynak"], o["kanit_id"], o["alan"])),
            "celiskiler": sorted(celiskiler, key=lambda c: (c["kod"], c["kaynaklar"]))}

print(zaman_raporu(registry_izleri(registry), prefetch_izleri(prefetch), mft_izleri(mft), lnk_izleri(lnk)))
```

```hint
Küçük bir `olay()` kurucu bütün olaylarda aynı beş alanı garanti eder. Önce bütün kaynakları çizelgeye ekle; ikinci aşamada Prefetch/MFT ve LNK/MFT çiftlerini karşılaştır. Çelişki kaydı yeni bir zaman seçmez, iki mevcut UTC değerini `bir`/`iki` olarak taşır.
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from windows_forensics_lab import hazirla
hazirla()
```
:::

::: anlat Bulguyu sınırlı ve doğrulanabilir yaz
Bu fixture'da Prefetch'in 7 run count değerine karşı yalnız iki saklanan zamanı vardır; TOOL.EXE için en yeni saklanan çalıştırma `2026-10-20 08:20:00` UTC'dir. MFT SI Birth `08:25:00`, LNK hedef Birth `08:10:00` olduğundan iki ayrı çelişki raporlanır. Bu sayılar gerçek bir olaydan toplanmamıştır ve tek başına zaman damgası kurcalamasını kanıtlamaz.

CDSA düzeyinde iyi rapor; hive/anahtar/değer kapsamını, Prefetch sürüm ve saklama sınırlarını, MFT SI/FN ayrımını, `$DATA` depolama durumunu ve LNK iç/dış zaman farkını açıklar. Her zamanı UTC'ye çevirir, kaynak alanını korur ve çelişkiyi açık inceleme maddesi yapar. “Hangi değer doğru?” sorusuna ek kanıt yoksa cevap uydurulmaz.
:::
