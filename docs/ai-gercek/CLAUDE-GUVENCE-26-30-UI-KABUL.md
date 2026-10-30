# ai-guvence-26..30 · Ders ekranı kabulü ve devir kapanışı (claude-opus · 29 Ekim 2026)

Codex bu beş dersin kodunu ve CLI kabulünü tamamlamış (`CODEX-GUVENCE-26-30.md`), ders ekranı kabulünü ve tracker kapanışını ana ajana bırakmıştı. Codex'in hakkı bitince kullanıcı kararıyla claude-opus devraldı. **Codex'in ders ve sandbox kodu değiştirilmedi**; yalnız bağımsız yeniden doğrulama ve ekran kabulü yapıldı.

## Bağımsız yeniden doğrulama

| Ders | validate | tahmin | mutasyon (gerçek adım çıkarılmış kopya) |
|---|---|---|---|
| 26 FGSM replikasyonu | TEMİZ (9) | 0 şüpheli | 118 mutant, 0 geçen |
| 27 Kalibrasyon ve açık eval | TEMİZ (9) | 0 şüpheli | 60 mutant, 0 geçen |
| 28 Opt-in model çifti | TEMİZ (9, izole opt-in) | 0 şüpheli | 108 mutant, 0 geçen |
| 29 Sorumlu bildirim | TEMİZ (9) | 0 şüpheli | 104 mutant, 0 geçen |
| 30 Yayınlanabilir purple | TEMİZ (9) | 0 şüpheli | 109 mutant, 0 geçen |

## Ders ekranı kabulü

Kendi geçici Pafta sunucusu (`server.py`, rastgele boş port, ayrı belirteç, izole `--veri`) açıldı; ekranın çağırdığı uçlar her dersin gerçek deney adımında (adım 7, ekranda 8.) sırayla denendi; sonra yalnız bu sunucu kapatıldı.

| Ders | Başlangıç kodu · Kontrol | Çözümü göster | Çözüm · Kontrol | Çalıştır | Görünür ayar dosyası |
|---|---|---|---|---|---|
| 26 | fail (beklenen) | var | pass | ok, kalıcı ayar yolu + içerik basıldı | `/data/ai-guvence-26-deney.txt` 200 |
| 27 | fail | var | pass | ok | 200 |
| 28 | fail | var | pass | ok | 200 |
| 29 | fail | var | pass | ok | 200 |
| 30 | fail | var | pass | ok | 200 |

Ham sonuç: `CLAUDE-GUVENCE-26-30-UI-KABUL.json`. Kanıtlar (`kaynak: gercek`, `kabul: true`): `kanit/guvence-26-fgsm-replikasyon.json`, `guvence-27-kalibrasyon-eval.json`, `guvence-28-opt-in-model-cifti.json`, `guvence-29-sorumlu-bildirim.json`, `guvence-30-purple-yayin-paketi.json`.

## Sınırlar

- 28'de açık onay (`opt_in: true`) yalnız izole kabul veri klasöründe açıldı (kullanıcının önceki izni bu kapsamdaydı). Öğrencinin varsayılanı `web/data/ai-guvence-28-deney.txt` içinde hâlâ `opt_in: false`; onaysız koşu bilerek başarısız olur.
- Ekran kabulü HTTP uçları üzerinden yapıldı (ekran düğmelerinin çağırdığı uçlar); tarayıcıda görsel tıklama yapılmadı.
- Ollama modelleri deney sonunda boşaltıldı (`/api/ps` boş); kullanıcının Ollama sunucusuna, WSL'e, Docker'a dokunulmadı. Commit/push yok.
- "Denetime hazır" uygulayıcı kabulüdür; bağımsız denetim değildir.
