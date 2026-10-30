# Bu projede çalışan yapay zekâlara

Burada aynı anda birden çok AI çalışıyor (Claude, Codex, ChatGPT, ...). Çakışmayı (iki ajanın aynı işe/kaynağa girmesi) önlemek için **iki ortak araç** var. İş yapmadan önce ikisine de bak.

## 1) Ortak hafıza panosu — `tools/ai_pano.py`

Ne yaptığını herkesin görmesi için buraya yaz. Canlı sayfa: `docs/ai-gercek/PANO.html` (8798 portundan: `http://127.0.0.1:8798/PANO.html`).

```
# Dokunmadan önce: açık iş var mı bak
python -X utf8 tools/ai_pano.py acik
python -X utf8 tools/ai_pano.py oku          # son kayıtlar

# İşe başlarken / bitince / herkese duyuru
python -X utf8 tools/ai_pano.py yaz --kim <ad> --tur basladi --konu ai-temel-17 --mesaj "..."
python -X utf8 tools/ai_pano.py yaz --kim <ad> --tur bitti   --konu ai-temel-17 --mesaj "..."
python -X utf8 tools/ai_pano.py yaz --kim <ad> --tur uyari   --konu .ai-araclar --mesaj "kurulum yapıyorum, dokunmayın"
```

Türler: `basladi` (işe giriştim) · `bitti` (tamam) · `not` (bilgi) · `uyari` (dikkat/dokunma) · `soru` (karar bekliyor) · `karar` (ortak karar).

## 2) Ders iş-tablosu — `tools/ai_ders_takip.py`

Her dersi **dokunmadan önce** sahiplen; başkasının aldığı derse dokunma. Canlı sayfa: `docs/ai-gercek/TAKIP.html`.

```
python -X utf8 tools/ai_ders_takip.py liste
python -X utf8 tools/ai_ders_takip.py al ai-saldiri-05 --kim <ad>
python -X utf8 tools/ai_ders_takip.py durum ai-saldiri-05 denetime-hazir --kim <ad> --not "3/3 mutant reddedildi"
```
`bitti` yalnız bağımsız denetimden sonra yazılır; kendi kontrolün `denetime-hazir`.

## Kurallar (özet)

1. **Önce pano + tracker'a bak**, sonra dokun. Paylaşılan kaynağa (venv, kurulum) girmeden panoya `uyari` bırak.
2. **Bir ders / kurulum / görevi tek ajan sahiplenir.** Aynı anda aynı ortama iki pip, aynı derse iki yazar olmaz.
3. `motor: ai-gercek` dersleri gerçek araç/model ister, fixture'dan ayrı, yanlış çözümü reddeden test + kanıt dosyası. Ayrıntı: `docs/ai-gercek-lab.md`.
4. İki ayrı ortam: dersler `.ai-venv` (torch/transformers), red-team araçları `.ai-araclar` (garak/PyRIT/lm-eval). Karıştırma.
5. İş bölümü ve yerleşim planı: `C:\Users\demo12\Desktop\Pafta-Platform-Projesi\YENI_DERSLER_YERLESIM.md`.


## Yeni katılan ajan: görünür veri standardı

Kullanıcının 29 Ekim 2026 kararı ve ayrıntılı çalışma/devir kuralları: `docs/ai-gercek/YENI-AJAN-REHBERI.md` (proje köküne göre). İşe başlamadan önce oku. Sonraki uygun örneklerde açılabilir/değiştirilebilir öğrenci veri dosyaları sun; sentetik örnek, kaydedilmiş çıktı, canlı deney ve gizli test verisini ayır. Tüm eski dersler dönüştürülmüş değildir. Rehber ortak panonun üst kısmında da kalıcı olarak görünür.
