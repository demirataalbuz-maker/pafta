# Codex görevi: AI derslerini A notuna çıkar (iyileştirme kuyruğu)

Kullanıcı kararı (30.10.2026): 153 AI dersinin hepsi A (≥ 90) olacak. **İlk düzelten sensin**, denetçi claude-opus.
Hakkın biterse kaldığın yerden başka AI veya claude-opus devralır; bu yüzden **her dersi tek tek al, bitir, teslim et**.
Aynı anda en çok 1 ders üzerinde ol (yarım iş bırakma).

Önce oku: `AGENTS.md`, `docs/ai-gercek/IYILESTIRME.md` (akış ve değişmeyen kurallar), örnek ders
`tracks/ai-guvence/lessons/ai-guvence-14-*.md` (purple standardının tam hâli).

## Sıra

1. **Dalga 1 — test güvenliği (23 ders).** `python -X utf8 tools/ai_iyilestirme.py liste --dalga 1 --durum acik`
   - Kopya açığı: ai-guvence-17..30 ve ai-saldiri-05. Gerçek deney testine
     `ai_lab.kod_denetimi(src, yasak=(<modüldeki her *_ref / ref* / *_referans adı>, "kanit_yaz"))` ekle; ihlalde `stop()`.
     Kanıt yalnız `kabul=all(checks)` ile yazılsın (bkz. ai-guvence-14 test bloğu). 17..20 ve 26..30'da referans
     modülden import edilince bugün GEÇİYOR (17 ve 26 denendi).
   - Geçen mutantlar: ai-guvence-31..34, ai-savunma-31, ai-saldiri-03/21/24. Sınır (`<=`/`<`), `or`/`and` ve sabit+1
     mutantlarını yakalayan test vakaları ekle; doğru testi zayıflatma.
   - Emirdeki diğer maddeler (tablo, fixture, kusurlu başlangıç, anlatım) de aynı emre dahildir; A olmadan kabul edilmez.
2. **Dalga 2 — çelişki (27 ders).** İlk anlatımdaki "bu derste … çalıştırılmaz" cümlesi son adımdaki gerçek deneyle
   çelişiyor. Düzelt + emirdeki diğer maddeler.
3. **Dalga 3 — purple standardı (77 ders).** Tablo + `[!NOT]`, `tracks/<yol>/fixtures/<ders>/` + `sandbox/ai_<yol>_veri.py`
   `hazirla()`, kusurlu başlangıç kodu, ~450+ kelime anlatım. Elle karar gerektiren 3 ders (ai-temel-08,
   ai-savunma-27, ai-guvence-23) için indirme/kurulum gerekiyorsa **dur, panoya `soru` yaz**, kullanıcı onayını bekle.

## Her ders için

```
python -X utf8 tools/ai_iyilestirme.py al <ders> --kim codex
python -X utf8 tools/ai_iyilestirme.py goster <ders>          # yapilacaklar listesinin hepsi
# ... düzelt ...
./.ai-venv/Scripts/python.exe -X utf8 tools/validate.py <ders>                         # TEMİZ (gerçek deney dahil, izole PAFTA_DATA)
./.ai-venv/Scripts/python.exe -X utf8 docs/denetim/araclar/tahmin.py . <ders>         # 0 şüpheli
./.ai-venv/Scripts/python.exe -X utf8 docs/denetim/araclar/kirp_gercek.py <geçici>    # mutasyon kopyası
./.ai-venv/Scripts/python.exe -X utf8 <geçici>/docs/denetim/araclar/mutasyon.py <geçici> --en-cok 1000 <ders>   # 0 geçen
PAFTA_DATA=<izole> ./.ai-venv/Scripts/python.exe -X utf8 docs/denetim/araclar/kopya_sonda.py <yol> <ders> "<referansı import eden kod>"  # korunuyor
python -X utf8 tools/ai_iyilestirme.py teslim <ders> --kim codex --not "validate TEMİZ · tahmin 0 · mutasyon 0/N · kopya korunuyor · yapılanlar: ..."
```

## Yapma

- `tools/ai_iyilestirme.py denetle` çalıştırma (denetçi claude-opus; araç seni zaten engeller).
- `ai-puanlar.json`'a puan yazma; puanı denetçi verir.
- `engine/`, `web/` davranışını değiştirme; commit/push; yeni indirme/kurulum (onaysız); kullanıcının Ollama/WSL/Docker'ını kapatma.
- Başkasının `alindi` emrine dokunma. Hakkın bitmek üzereyse elindeki dersi ya `teslim` et ya `birak`.
