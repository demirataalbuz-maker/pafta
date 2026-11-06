# ai-temel-04 · gerçek deney adımı (uygulayıcı raporu, bağımsız denetim değil)

Adım 8 (index 7): "Gerçek deney · Gerçek logitlerde aday kümesi ve örnekleme", `motor: ai-gercek`, `gereksinim: torch`.
Derse özel kod: `sandbox/ai_gercek_ai_temel_04.py` (yeni). Ortak dosya değişmedi.

Kabul (`python -X utf8 kabul.py`, gerçek koşucu üzerinden): referans PASS + `kaynak: gercek, kabul: true` kanıtı;
başlangıç, boş, sabit cevap ve 4 anlamlı hata (top-p tam dağılımda, eşikteki aday dışarıda, sıcaklık yok, son normalize yok) reddedildi.
Test içinde ayrıca 6 mutant reddediliyor. Referans 3 ek koşuda da PASS (rastgele vakalar). transformers
Temperature/TopK/TopP işlemcileri 7/7 vakada aynı aday kümesini verdi.
`validate.py --yol ai-temel`: 18 ders, 134 kontrol, TEMİZ. Ders ekranı: başlangıç reddedildi, çözüm "✓ geçti";
Çalıştır gerçek çıktı + "kabul yok (yalnız deneme)" kanıtı.

Gerçek çıktı (SmolLM2-135M@93efa2f0, 'Once upon a time, in a small village,'): p=0.9 aday sayısı T=0.5'te 2, T=1.5'te 1210.
12 token, tohum 7: greedy ' lived two best friends named Sam and Alex. They loved exploring';
T=1.5,p=0.95 ' lived three mothers who believed that adversity helped children move higher on'.
