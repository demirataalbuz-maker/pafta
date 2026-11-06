# pu23 · Görünür Sentetik Örnekler

`ornekler.json` **sentetiktir**: araç çıktıları elle, gerçek biçimlerine bakılarak yazılmıştır; sırlar `REDACTED` ya da `****`'dır.

- `semgrep`, `gitleaks`, `trivy` (Görev 1): Üç aracın JSON çıktısından kısa örnekler. Yol ayırıcıları bilerek karışıktır.
- `bulgular` (Görev 2 ve 3): Üç örneğin 1. görevdeki doğru çözümle tek biçime çevrilmiş hâli.
- `gercek`, `kapsam` (Görev 2): Etiketli doğru liste ve hangi aracın hangi türden sorumlu olduğu.
- `istisnalar`, `bugun` (Görev 3): CI kapısının istisna (bastırma) listesi ve değerlendirme günü.

Setup her Çalıştır/Kontrol Et adımında eksik dosyaları kopyalar; **kalıcılık yoktur**. Son görev bu dosyayı kullanmaz: geçici bir git deposu kurar, Semgrep, gitleaks ve Trivy'yi `.deps` altındaki sabit sürümlerle gerçekten koşturur.
