# ai-guvence-25 iyileştirme teslimi

Düzelten codex; claude-opus denetimi bekleniyor. Puan verilmedi.

Değişenler: ders markdown ve tracks/ai-guvence/fixtures/ai-guvence-25/{README.md,veri/tedarik_kayitlari.json}. İlk tablo+NOT, köken/kalıcılık, üç görevde aynı dosyayı okuyan mevcut hazirla/setup, kusurlu çalışan başlangıçlar ve 465 kelime ek anlatım eklendi. Girişteki sentetik kayıt anlatımı son gerçek CPU/safetensors yüklemesiyle tutarlı hâle getirildi. Hash/manifest, kaynak etiketi/imza, safetensors biçimi/güvenilir model ayrımları açıklanır; tam sandbox veya modelscan/Syft iddiası yok.

sandbox/ai_gercek_ai_guvence_25.py içinde hesap bağımsız kapi_ref adıyla ifade edildi; mevcut vaka/bağımsız beklenen sonuçlar korundu ve aralarında tutarlılık assertion eklendi. Gerçek eğitim ve yükleme kararı davranışı değiştirilmedi. Test kapi_ref/kanit_yaz ve ImportFrom takma ad/yıldız kullanımını guard içinde durdurur. Kanıt mevcut bütün kontrollerin and sonucuyla kabul edilir. engine/web davranışı değiştirilmedi.

## Dört zorunlu kontrol

.ai-venv/Scripts/python.exe -X utf8 ile:

- tools/validate.py ai-guvence-25: TEMİZ, 9 kontrol (1 tahmin, 4 çözüm, 4 başlangıç), iki seed gerçek eğitim/safetensors yükleme dahil; PAFTA_DATA=Desktop/pafta-iyilestirme-25-kanit.
- docs/denetim/araclar/tahmin.py . ai-guvence-25: 1 tahmin, 0 şüpheli.
- kirp_gercek.py Desktop/pafta-mutasyon-g25-20261030; mutasyon.py <kopya> --en-cok 1000 ai-guvence-25: 3+14+17=34 mutant, 0 geçen.
- kopya_sonda.py ai-guvence ai-guvence-25 "from sandbox.ai_gercek_ai_guvence_25 import kapi_ref as tedarik_kapisi": fail, korunuyor. Ayrıca hedeflenen guard mesajı ve kabul kanıtı yokluğu doğrulandı: outputs/iyilestirme-codex-ai-guvence-25/{kopya-sonda.log,kopya-sonucu.json}.

## Öğrenci akışı ve açık eksik

Görünür dosya sıradan runner/setup/starter Run akışında gerçekten okundu ve hatasız çıktı üretti (gorunur-dosya-run.json). Kendi 18800 test sunucusunda dersin /api/check ucu pass/4kontrol ve kabul=true, /api/run ucu ok ve kabul=false (yalnız deneme) verdi. Sonuçlar http-check.json ve http-run.json. Bu HTTP kontrolü tarayıcı görsel kabulü değildir. Work ayarları yerel tarayıcı kontrolünü kapalı bildirdiğinden ders 25 görsel ekran kabulü YAPILMADI ve PASS sayılmadı; denetçiye açık eksik.

Gerçek diskte yalnız sağlam dosya yüklendi, değişmiş byte/kaynak/biçim/sürüm/eksik manifest vakaları reddedildi. Yalnız kendi ürettiğimiz ağırlıklar açılır; bilinmeyen veya zararlı model yüklenmez. Bu ders için indirme/kurulum yok; daha önce onaylanan ders23 Q8 kurulumu ayrı rapordadır. Commit/push yok.
