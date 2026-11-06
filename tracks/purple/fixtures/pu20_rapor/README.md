# pu20 · Görünür Sentetik Örnek Veri

`bulgular.json` **sentetiktir**: istek/yanıt metinleri, iddia hash'leri ve bulgular elle yazılmıştır, gerçek sunucu kaydı değildir.

- `vektorler` (Görev 1): Dört CVSS 3.1 vektörü.
- `kanitlar`, `iddialar` (Görev 2): İki ham istek/yanıt kanıtı ve bir rapor taslağının bunlar için iddia ettiği sha256 değerleri. `E2` iddiası yanıtı değiştirilmiş bir kopyadan hesaplanmıştır; `E7` dosyası hiç yoktur.
- `bulgular`, `durum` (Görev 3): Üç taslak bulgu ve kanıt bütünlüğü sonucu.

Setup her Çalıştır/Kontrol Et adımında eksik dosyaları kopyalar; **kalıcılık yoktur**. Son görev bu dosyayı kullanmaz: pu19'un yerel HTTP + SQLite labını açar, dört gerçek istek gönderir ve kanıtı kendisi üretir.
