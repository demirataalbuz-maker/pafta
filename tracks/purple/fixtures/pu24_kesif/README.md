# pu24 · Görünür Sentetik Örnekler

`ornekler.json` **sentetiktir**: girdiler elle, gerçek biçimlerine bakılarak yazılmıştır; hiçbir sunucuya gönderilmez.

- `ffuf`, `taban` (Görev 1): `ffuf -mc all -of json` çıktısından kısa bir örnek ve rastgele bir yola verilen yanıtın imzası.
- `sablon` (Görev 2): `sablon_kur` için örnek girdiler.
- `kayitlar`, `esik`, `pencere`, `guvenilir` (Görev 3): Ters vekil arkasındaki bir sunucunun erişim kaydı. `kaynak` soket adresi, `xff` X-Forwarded-For başlığıdır.

`kelimeler.txt` son görevde ffuf'un kullandığı küçük sentetik kelime listesidir.

Setup her Çalıştır/Kontrol Et adımında eksik dosyaları kopyalar; **kalıcılık yoktur**. Son görev bu dosyaları kendi `127.0.0.1` sunucusuna karşı kullanır; dış hedef yoktur.
