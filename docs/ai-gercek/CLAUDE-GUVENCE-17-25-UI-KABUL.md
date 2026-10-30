# ai-guvence-17..25 · Ders ekranı kabulü ve devir kapanışı (claude-opus · 29 Ekim 2026)

Codex bu dokuz dersin kodunu ve CLI kabulünü tamamlamış (`CODEX-GUVENCE-17-20.md`, `CODEX-GUVENCE-21-25.md`), ders ekranı kabulünü ve tracker kapanışını ana ajana bırakmıştı. Codex'in hakkı bitince kullanıcı kararıyla claude-opus devraldı. **Codex'in ders ve sandbox kodu değiştirilmedi**; yalnız bağımsız yeniden doğrulama ve ekran kabulü yapıldı. Yöntem `CLAUDE-GUVENCE-26-30-UI-KABUL.md` ile aynıdır.

## Bağımsız yeniden doğrulama

| Ders | validate | tahmin | mutasyon (gerçek adım çıkarılmış kopya) |
|---|---|---|---|
| 17 Üyelik çıkarımı | TEMİZ | 0 şüpheli | 81 mutant, 0 geçen |
| 18 Aşırı öğrenme ve gizlilik riski | TEMİZ | 0 şüpheli | 58 / 0 |
| 19 Diferansiyel gizlilik bütçesi | TEMİZ | 0 şüpheli | 92 / 0 |
| 20 Gizlilik iddialarının saldırıyla doğrulanması | TEMİZ | 0 şüpheli | 65 / 0 |
| 21 Model ve veri SBOM | TEMİZ | 0 şüpheli | 39 / 0 |
| 22 Pickle/safetensors/GGUF ve chat template | TEMİZ | 0 şüpheli | 24 / 0 |
| 23 Quantization regresyonu | TEMİZ | 0 şüpheli | 78 / 0 |
| 24 Sleeper agent ve ağırlık backdoor | TEMİZ | 0 şüpheli | 65 / 0 |
| 25 Yerel model tedarik zinciri | TEMİZ | 0 şüpheli | 34 / 0 |

Toplam: validate 81 kontrol TEMİZ; mutasyon 536 mutant, 0 geçen.

## Ders ekranı kabulü

Kendi geçici Pafta sunucusu (rastgele boş port, ayrı belirteç, izole `--veri`) açıldı; gerçek deney adımı (dokuzunda da adım 7, ekranda 8.; 19 ve 20'de gerçek deneyden sonra bir adım daha var, adım başlığından bulundu) için ekranın çağırdığı uçlar denendi; sonra yalnız bu sunucu kapatıldı.

Dokuz dersin hepsinde: başlangıç kodu iki ayrı Kontrol'de `fail`; Çözümü göster var; çözüm Kontrol'de `pass`; Çalıştır `ok`; Çalıştır'ın yazdırdığı öğrenci dosyası (`PAFTA_DATA/calisma/<ders>/...`) diskte gerçekten oluştu; görünür dosya (`/data/ai-guvence-17..20-ayarlar.txt`, `/data/ai-guvence-21..25-deney.txt`) HTTP 200.

Ham sonuç: `CLAUDE-GUVENCE-17-25-UI-KABUL.json`. Kanıtlar (`kaynak: gercek`, `kabul: true`): `kanit/guvence-17-cpu.json` … `guvence-20-cpu.json`, `guvence-21-kabul.json` … `guvence-25-kabul.json`.

## Sınırlar

- Ekran kabulü HTTP uçları üzerinden yapıldı (ekran düğmelerinin çağırdığı uçlar); tarayıcıda görsel tıklama yapılmadı.
- Dokuz ders de CPU'da çalışır; Ollama kullanılmadı. Kullanıcının servislerine dokunulmadı. Commit/push yok.
- "Denetime hazır" uygulayıcı kabulüdür; bağımsız denetim değildir.
