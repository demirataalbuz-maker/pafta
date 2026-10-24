# Çalışma panosu

Kim şu an neyle uğraşıyor, kim neyi bitirdi. Amaç: iki ajan aynı işi yapmasın, kimse "bu ne zaman oldu" demesin.

- Bir işe **başlamadan önce** buraya bir satır ekle (ya da kendi satırını güncelle) ve commit et.
- Ortak bir dosyaya (`engine/`, `sandbox/`, `server.py`, `web/`, `tools/validate.py`) dokunacaksan hangi dosya ve neden, onu da yaz.
- İş bitince durumu "denetime hazır" yap ve commit kimliğini ekle. "Bitti" kararı denetçinindir (`DENETIM.md`).
- `Pafta_Takip.xlsx` ve `DENETIM.md` denetçinindir; bu pano onların yerine geçmez, aradaki boşluğu doldurur.

## Şu an

| Ajan | İş | Takip no | Dokunduğu dosyalar | Durum |
|---|---|---|---|---|
| Claude (Yazar 2) | Regex yoluna gerçek PCRE2 motoru: Git for Windows'un `libpcre2-8-0.dll`'i üzerinden ctypes adaptörü, adım meta'sında `motor: pcre2` | 46 (ve 45'in PCRE2 ayağı) | yeni `sandbox/pcre2_engine.py`; `sandbox/py_harness.py` (regex işlevleri); `engine/runners.py` (yalnız `RegexRunner`/`for_step`, Yazar 1'in commit edilmemiş `cmd` satırına dokunmadan) | çalışılıyor |
| Claude (Yazar 2) | RX23: PCRE2 subroutine/recursion, branch reset ve kontrol fiilleri dersi | 46 | `tracks/regex/lessons/rx23-*.md`, `tracks/regex/track.json` | sırada (motordan sonra) |
| Claude (Yazar 2) | SQL yoluna gerçek PostgreSQL bağlantısı (Kali) ve rol/yetki dersi | 25 (ve 23'ün PostgreSQL ayağı) | henüz başlamadı; başlarken burası güncellenecek | sırada |

> **Codex'e not:** 45 numaralı maddenin (RX16 lehçelerini gerçek motorlarda sınamak) PCRE2 ayağı ve 23 numaralı maddenin PostgreSQL bağlantısı Yazar 2'nin işiyle aynı altyapıyı kullanır. Yeniden yazma; bu panodaki dosyaları kullan ya da genişlet. .NET, Node ve MySQL/SQL Server ayakları sende.

## Denetime hazır

| Ajan | İş | Takip no | Commit |
|---|---|---|---|
| Claude (Yazar 2) | SQ19 uygulama girdisinden SQL'e veri akışı, parametre bağlama, izinli alanlar | 24 | `3234635` |
| Claude (Yazar 2) | SQ20 JSON kayıtlarını sorgulamak (SQLite; PostgreSQL jsonb yalnız karşılık tablosu) | 26 | `a0290ad` |
