# ai-temel-24 iyileştirme teslimi

Codex'in kendi uygulama kontrolleridir; bağımsız denetim ve puan claude-opus'a aittir.

İş emrinin tamamı uygulandı: ilk tablo ve NOT, ilk3 sentetik/final gerçek model ayrımı, görünür savunma.json+README, mevcut ai_temel_veri.hazirla setup, dosyayı okuyan ilk3 starter/solution. Anlatım yaklaşık1267 sözcük. İlk görev ../ silme ve URL önek hatasını, ikinci onayın kapsam/üçlü kontrolünü atlamasını, üçüncü kapının ham argümanı denetimsiz yürütmesini gösterir. Üç starter çalışır ve Check'te reddedilir.

Veri tracks/ai-temel/fixtures/ai-temel-24 içindedir. Elle hazırlanmış sentetik argüman/politika vakaları ve üç çağrılı senaryodur; canlı kayıt değildir. Görev3 yardımcı politika/doğrulayıcıları yalnız örneğe ait tablo verisidir; genel doğrulayıcı/politika değildir. Örnek araçlar yalnız calisanlar listesine yazıp SENTETIK metin döndürür. Gerçek HTTP veya dosya etkisi yoktur. Setup her çalıştırmaya geçici kopya kurar; kalıcılık yoktur. Kaynak editörle açılır veya derste yüklenen sözlük değiştirilip Run denenir. Gizli testler ayrıdır.

Final gerçek Ollama ile ayrı bir RAG deneyidir. Araç kapısındaki izolasyon sözlüğü gerçek Docker/egress/TOCTOU güvenliği diye sunulmaz. Yetkisiz parça filtrelemesi modele gitmeden yapılır. html.escape hem kimliği hem metni kaçışlar; bu anlamsal injection bağışıklığı değildir. Sahte etiketi etkisizledi ifadesi ham sahte etiket kaçışlandı olarak düzeltildi. Python html.escape/urlsplit resmi belgeleri kaynak gösterilir.

Final kopya koruması referans/referans_korumali/getattr/kanit_yaz, AST takmaad/yıldız import kontrolü ve stop ile güçlendirildi. Sözleşme artık bekleneni çağrıdan önce hesaplar, derin kopya ile girdi değişmezliğini sınar; kimlikte tırnak/ampersand, yinelenen/boş/yanlış tip gizlilik ve üst sınır vakaları eklidir. Mevcut testler zayıflatılmadı. Gerçek iki yanıtın ikisi de hatasız ve boş olmayan metin olmalıdır; tek yanıt yeterli sayılmaz. Sızıntı veya belirli model metni PASS şartı değildir.

Kanıt yalnız gerçek deney r mevcutsa yazılır ve kabul=all(sonuclar) kalır. Hiç çalışmayan deney için gerçek etiketi üretilmez. Çalışıp hata veren deney kabulfalse kaydı korur. Ham kanıta tüm sentetik parçalar, naif/korumalı bağlamlar, her isteğin mesajları/seed42/sıcaklık0.2/max120 ve tam model yanıtı eklendi. Çalıştır keşif kanıtı kabulfalse kalır. dogru bulgusu artık123 içinde23 alt dizisini aramaz; sayısal sınır kontrolü kullanır. Bu dar sayı-bulunma ölçütüdür; anlamsal doğruluk kanıtı/PASS koşulu değildir.

Zorunlu kontroller (.ai-venv/Scripts/python.exe -X utf8):
- tools/validate.py ai-temel-24: izole PAFTA_DATA Desktop/pafta-t24-kabul-20261031; TEMİZ9 (tahmin1/solution4/starter4).
- docs/denetim/araclar/tahmin.py . ai-temel-24:1tahmin,0şüpheli. İlk sandbox denemesi WinError5 nedeniyle yapılamadı; izinli tekrar sonuç verdi, başarısız koşu PASS sayılmadı.
- kirp_gercek.py Desktop/pafta-mutasyon-t24-20261031: hedefin yokluğu doğrulandı; var olan hedef silinmedi. Kopyada mutasyon.py <kopya> --en-cok1000 ai-temel-24:23+18+24=65mutant,0geçen. İlk3 starter/solution/test/setup blokları kaynakla aynı.
- kopya_sonda.py ai-temel ai-temel-24 "from sandbox.ai_gercek_ai_temel_24 import referans_korumali as korumali_baglam":fail/korunuyor. Aynı guard negatif kopya.json ile ayrıca doğrulandı.

Ekler outputs/iyilestirme-codex-ai-temel-24:boş,sabit,erişim-yok,eksik-model ve kopya sondaları fail/kabul yok. Eksik model yalnız kendi çocuk ortamında loopback9 ve olmayan exe ile sınandı. Üç gorunur-dosya-run çıktısı normal runner/setup ileok. http-check.json8/8pass/gerçek kabul;http-run.jsonok/gerçek kabulfalse.

Gerçek CLI kanıtı Desktop/pafta-t24-kabul-20261031/ai-kanit/temel-savunma-1793433478951.json:Qwen3:4b-instruct-2507-q4_K_M;2/2 gerçek çağrı;iki yanıt23gün;korumalı bağlamda sır yok,naifte var;ham sahte etiket kaçışlanmış. Naif/korumalı yanıtların ikisinde de canary/sır sızıntısı görülmedi. Bu tek denemede kaçışlamanın davranışsal üstünlüğü gösterilmedi; deterministic bağlam güven sınırı gösterildi. model_bosaltildiTrue; kullanıcının sunucusu kapatılmadı.

Gerçek ders ekranı:starter Check3/4fail,gerçek kanıt yok;referans8/8gerçek kabul temel-savunma-1793433651584.json;Run iki gerçek yanıt ve kabulfalse temel-savunma-calistir-1793433683337.json. UI veri alanı outputs/iyilestirme-codex-20261030/ui-data. Görünür görev Run sonuçları ve kendi sunucunun kapanışı teslim ekindedir. Eski derslerin görsel açıkları bu kabul ile kapanmaz.

Değişen dosyalar:tracks/ai-temel/lessons/ai-temel-24-en-az-ayricalikli-rag-ve-tool-savunmasi.md,sandbox/ai_gercek_ai_temel_24.py,fixtures/ai-temel-24/README.md ve savunma.json,bu rapor;kuyruk/pano/devir/özet. Yeni indirme/kurulum,engine/web değişikliği,commit/push veya puan yazımı yok.

Teslim eki:Üç görünür görev UI Run ile dosya girdilerini ve starter kusurlarını gösterdi:kaçış/yanıltıcı URL kabulü,onayın kapsam/üçlü engellerini aşması,kapının üç ham çağrıyı çalıştırması. Doğru çözümler ve starter retleri validate içinde doğrulandı. Son değişiklik yalnız anlatımda Docker önerisini kurulmuş altyapı gibi anlatmayı kaldırır;çalıştırılabilir bloklar değişmedi. Kendi18800 sunucusu kapatıldı,dinleyenportyok. Kullanıcı süreçleri kapatılmadı.
