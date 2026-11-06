# ai-saldiri-13 — gerçek PDF katmanları ve vision OCR
Uygulayıcı kabulü; bağımsız denetim değildir. 29 Ekim 2026.

Değişen: ai-saldiri-13 ders sonuna anlat+gerçek görev index8; sandbox/ai_gercek_ai_saldiri_13.py; sandbox/ai_saldiri_13_pdf_worker.py; web/data/ai-saldiri-13-tarif.txt. Mevcut ders adımları korundu. Ortak motor/uygulama kodu değiştirilmedi; kurulum/commit/push yok.

Kurulu .ai-araclar: reportlab5.1.0,pypdf6.21.4,Pillow13.0.0. Yardımcı Python ortam değişkeniyle seçilebilir. Görünür sentetik tarif kalıcı öğrenci kopyasına alınır, mevcut kopya sıfırlanmaz. Gerçek PDF'ler görünür fatura görüntüsü, render mode3 görünmez metin ve metadata alanları taşır. Pypdf gerçek dosyadan metin/metadata ve gömülü görüntüyü çıkarır. Kurulu qwen2.5vl:3b bu görüntüye gerçekten OCR yapar; önceden yazılmış OCR tablosu yoktur. Bu genel sayfa render/OCR ürünü değil, kontrollü tek görüntülü PDF örneğidir. Son Qwen3 4B çağrısı yalnız son belgenin metadata başlığını tek satır çıkarır; katmanlar arası nedensellik iddiası yoktur.

Görsel QA: PDF becerisinin işlem kaydı ilk üretim öncesi çalıştırıldı. QA iki gerçek PDF Poppler ile render edildi: qa/render-0.png ve render-1.png görsel olarak incelendi; fatura okunaklı, kesilme/taşma yok, gizli canary görünmüyor. Bunlar sentetik görsel QA, canlı model kabulünün yerine sayılmaz.

İlk deney metadata yanıtı boş/yarım nedeniyle FAIL oldu (ilk-deneme-fail.txt); ham yanıt o ilk koşuda korunmadı, bu eksik açıkça yazıldı. Başlık çıkarımına daraltılan son görevde hedef validate10kontrol TEMİZ. Son kodda metadata hatası tekrar olursa ham yanıt kabulfalse hata kanıtına yazılır; kesilme PASS sayılmaz.

kabul.py/summary.json 9/9: referans PASS; starter/boş/sabit ve güven yükseltme,substring işaret,yanlış aşama sırası mutantları FAIL. Çalıştır OK/kabulfalse; eksik Ollama FAIL. missing-pdf-python.json: eksik PDF yardımcı Python FAIL/kabul yok. persistence.json: farklı süreç/dizinlerde öğrenci dosyası korunur. Yeni testlerde alıntı yanlış pozitif ve geç aşama kontrolü de var.

Gerçek referans bulgu: text-only PDF canary metin katmanında true, metadata/ocr false; meta-only PDF metadata true, metin/ocr false. İlk gözlem sırasıyla çıkarma/metin-katmanı ve çıkarma/metadata. OCR kalitesi sabit metinle sınanmadı; öğrenci hesapları gerçek çıkarım/model çıktılarının bağımsız ölçümüyle karşılaştırıldı. Modelin işareti aktarması geçme şartı değil. Model/vision digest/sürüm/bellek/cihaz,PDF SHA256,PNG SHA256,ham OCR ve metadata yanıtı kanıtta.

Son UI ve ilgili grup regresyonu aşağıya eklenecek. PDF dosyaları Çalıştır'da öğrenci alanında korunur; test geçici dosyaları yalnız kendi kapsamıdır. Bağımsız denetim/ikinci cihaz kabulü yok.

Son UI Kontrol30/30: outputs/codex-kirmizi-seri-20261029/ui-data/ai-kanit/saldiri-13-pdf-1793269600117.json. İlk UI Çalıştır vision HTTP500 nedeniyle başarısızdı (ui-run-500-fail.txt); PASS sayılmadı. Son kod en fazla2 vision denemesi yapar, geçici ağ/5xx hatasını kaydeder,4xx tekrar etmez. vision-retry-fixture.json3/3 yalnız fixture kontrolüdür, model kabulü yerine sayılmaz. Son kod hedef validate10/10 TEMİZ (validate-son.log). Son UI Çalıştır saldiri-13-pdf-1793270036610.json; bütün gerçek kontrollertrue,kabulfalse;PDF/OCR/katman sonuçları göründü. 11/13 grup regresyonu20/20TEMİZ. Yeni paket kurulmadı.
