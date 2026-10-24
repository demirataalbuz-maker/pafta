# Çalışma panosu

Kim şu an neyle uğraşıyor, kim neyi bitirdi. Amaç: iki ajan aynı işi yapmasın, kimse "bu ne zaman oldu" demesin.

- Bir işe **başlamadan önce** buraya bir satır ekle (ya da kendi satırını güncelle) ve commit et.
- Ortak bir dosyaya (`engine/`, `sandbox/`, `server.py`, `web/`, `tools/validate.py`) dokunacaksan hangi dosya ve neden, onu da yaz.
- İş bitince durumu "denetime hazır" yap ve commit kimliğini ekle. "Bitti" kararı denetçinindir (`DENETIM.md`).
- `Pafta_Takip.xlsx` ve `DENETIM.md` denetçinindir; bu pano onların yerine geçmez, aradaki boşluğu doldurur.

## Şu an

| Ajan | İş | Takip no | Dokunduğu dosyalar | Durum |
|---|---|---|---|---|
| Claude (Yazar 2) | SQL yoluna gerçek PostgreSQL (Kali'deki küme, WSL üzerinden), adım meta'sında `motor: postgres`; SQ21 roller ve etkili yetkiler | 25 (ve 23'ün PostgreSQL ayağı) | yeni `sandbox/pg_lab.py`; `sandbox/py_harness.py` (yeni `pg_*` modları); `engine/runners.py` (yalnız yeni koşucu ve `for_step`); `tracks/sql/lessons/sq21-*.md` | çalışılıyor |

> **Codex'e not:** 45 numaralı maddenin (RX16 lehçelerini gerçek motorlarda sınamak) PCRE2 ayağı ve 23 numaralı maddenin PostgreSQL bağlantısı Yazar 2'nin işiyle aynı altyapıyı kullanır. Yeniden yazma; bu panodaki dosyaları kullan ya da genişlet. .NET, Node ve MySQL/SQL Server ayakları sende.

## Denetime hazır

| Ajan | İş | Takip no | Commit |
|---|---|---|---|
| Claude (Yazar 2) | SQ19 uygulama girdisinden SQL'e veri akışı, parametre bağlama, izinli alanlar | 24 | `3234635` |
| Claude (Yazar 2) | SQ20 JSON kayıtlarını sorgulamak (SQLite; PostgreSQL jsonb yalnız karşılık tablosu) | 26 | `a0290ad` |
| Claude (Yazar 2) | Regex yoluna gerçek PCRE2 motoru (`sandbox/pcre2_engine.py`, adım meta'sında `motor: pcre2`, `tools/test_pcre2_engine.py`) | 46 (45'in PCRE2 ayağı) | `6291614` |
| Claude (Yazar 2) | RX23 PCRE2 özyineleme, alt yordamlar, branch reset, kontrol fiilleri | 46 | bu commit |
