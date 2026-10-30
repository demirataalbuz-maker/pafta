# ai-guvence-23 iyileştirme teslimi

Düzelten codex; claude-opus denetimi bekleniyor. Puan verilmedi. Bu belge kendi kontrollerini anlatır; A notu veya bağımsız kabul değildir.

## İzin ve kurulum

Kullanıcı bu sohbette yaklaşık 4.3GB qwen3:4b-instruct-2507-q8_0 indirmesine açık onay verdi. Resmî Ollama kaynağından ollama pull tamamlandı, SHA256 doğrulandı. Yerel boyut 4,280,418,281 byte, digest aa7252f68dda4d25dfffa65b3760af6d2c3231a140c0060c78d444686d98a374; Apache2.0. Mevcut Q4 yeniden indirilmedi. Uygulama/paket kurulmadı; ücretli API/abonelik yok. Ayrıntı CODEX-ai-guvence-23-INDIRME-ONAYI.md. Commit/push yok.

## Değişenler

- tracks/ai-guvence/lessons/ai-guvence-23-quantization-kaynakli-guvenlik-regresyonu.md: tablo+NOT, köken/kalıcılık, 460 kelime ek derin anlatım, ilk üç görevde kusurlu çalışan başlangıçlar ve mevcut ai_guvence_veri.hazirla/setup ile görünür JSON okuması. Girişteki gerçek dönüşüm/model yok çelişkisi düzeltildi.
- tracks/ai-guvence/fixtures/ai-guvence-23/README.md, veri/quant_olcumleri.json, veri/esikler.json: sentetik öğretim dosyaları; geçici kopya, kalıcı olduğu iddia edilmez.
- sandbox/ai_gercek_ai_guvence_23.py: mevcut CPU autograd/fake-quant hesabı davranışı korunarak nicem_ref/esli_ref saf referanslarına ayrıldı; referans kopyası gerçek adlarla sınanabilir. Mevcut CPU görevi korunur; GGUF diye sunulmaz.
- sandbox/ai_gercek_ai_guvence_23_gguf.py: ayrı gerçek Q8_0/Q4_K_M çıkarım deneyi, iki yetenek/iki sentetik canary vakası, iki tekrar, 16 çağrı; aynı temel sürümün sabit digest/mimari/parametre/şablon/normalize varsayılan kontrolleri. Ham yanıt, hata, token, süre, cihaz, temizlik ve eşli regresyon/iyileşme kayıtları. Sızıntı veya regresyon görülmesi/geçmemesi PASS şartı değildir.
- web/data/ai-guvence-23-gguf-ayar.txt: ayrı kalıcı gguf-ayar.json için sentetik örnek. web/data/ai-guvence-23-gguf-ornek.txt: gerçekten alınmış dört yanıtın köken/zaman/model ayrıntılı kaydı; okumak yeni canlı çağrı değildir. Canlı Kontrol farklı çağrılar yapar.

engine/web uygulama davranışı ve ortak yardımcılar değiştirilmedi. Yeni görev hazır GGUF dosyalarını Ollama üzerinden yükler; GGUF dönüştürme veya saf ağırlık nedenselliğinin kesin kanıtı diye sunulmaz. Q8 yüksek bitli karşılaştırma koludur; F16/FP32 değildir. Gecikme sabit sırayla/ilk yüklemeyle karışabilir, hız benchmarkı değildir.

## Dört zorunlu kontrol

Komutlar .ai-venv/Scripts/python.exe -X utf8 ile çalıştırıldı.

1. tools/validate.py ai-guvence-23: son hâlde TEMİZ, 11 kontrol (1 tahmin, 5 çözüm, 5 başlangıç), gerçek CPU ve GGUF dahil. PAFTA_DATA=Desktop/pafta-iyilestirme-23-son-kontrol. Son GGUF kanıtı guvence-23-gguf-1793343357534.json; CPU kanıtı guvence-23-kabul-1793343329033.json.
2. docs/denetim/araclar/tahmin.py . ai-guvence-23: 1 tahmin, 0 şüpheli.
3. kirp_gercek.py Desktop/pafta-mutasyon-g23-20261030; mutasyon.py <kopya> --en-cok 1000 ai-guvence-23: 13+27+38=78 mutant, 0 geçen. İki gerçek görev mutasyon kopyasından çıkarıldı. Sonraki düzenlemeler yalnız gerçek GGUF Run çıktısı yolu ve anlatım kaydı bağlantısıdır; sentetik görevler aynı.
4. kopya_sonda.py ai-guvence ai-guvence-23 "from sandbox.ai_gercek_ai_guvence_23 import nicem_ref as agirlik_nicemle, esli_ref as esli_regresyon": fail, korunuyor. Ayrıca yeni ikinci gerçek göreve yanit_ref/rapor_ref gerçek aliasları verildi, fail. İki ret de hedeflenen kod_denetimi/ImportFrom korumasında ve kabul kanıtı olmadan gerçekleşti. outputs/iyilestirme-codex-ai-guvence-23/{kopya-sonda.log,kopya-cpu.json,kopya-gguf.json}. Kanıt kabul=all(checks) veya mevcut tüm kontrol değerlerinin and sonucudur.

Ek: gerçek sunucu yokluğunda PASS verilmedi (eksik-model-sonuc.json). CPU ayar.json ve GGUF gguf-ayar.json bağımsız; öğrenci düzenlemesi sonraki hazirla çağrısında korundu (kalicilik.txt). İlk üç görev gizli test verisini fixture'dan okumaz.

## Gerçek sonuç ve kaynak

İlk başarılı CLI örneğinde Q8/Q4 yetenek ve güvenlik 4/4, regresyon/iyileşme 0. Ölçülen Q8 toplam/VRAM 4,963,371,580 byte, Q4 3,180,247,121 byte; 4096 bağlam, ikisi tamamen GPU. İki model oturumu da kendi yüklediği modeli boşalttı; kullanıcının Ollama sunucusu kapatılmadı.

HTTP Kontrol koşusunda (guvence-23-gguf-1793343454350.json) Q8 güvenlik 2/4, Q4 4/4; Q8 iki sentetik canary sızıntısı yaptı, eşli iyileşme 2. Her iki model yetenek 4/4. Run koşusunda (guvence-23-gguf-1793343481745.json) sızıntı yok, iki kol 4/4. Bunlar farklı tohum/canary koşullarıdır; genel bir nicemleme/güvenlik üstünlüğü veya kararlılık hükmü çıkarılmaz. Ham kayıtlar saklanır.

## HTTP ve ekran kapsamı

Önceki ekran kontrolünde görünür sentetik JSON okuması doğrulandı ve CPU gerçek görev 9 Kontrol 2/2 geçti; kanıt outputs/iyilestirme-codex-20261030/ui-data/ai-kanit/guvence-23-kabul-1793342664922.json. Yeni GGUF görevinde ekranda iki boş çözümün 0/1 ile reddi ve örnek çözüm panelinin açılması görüldü. Son kullanıcı devam mesajından sonra Work ayarları tarayıcı kontrolünü kapalı bildirdi; yeni GGUF görevinin görsel başarılı kabulü TAMAMLANMADI.

Bu eksik ekran kabulünün yerine PASS yazılmadı. Aynı ders sunucusunun /api/check ve /api/run uçları kendi normal oturum belirteciyle sınandı: Kontrol pass, 8/8 ve kabul=true; Run ok, gerçek 16 yanıt/rapor dosyaları, kabul=false (yalnız deneme). Sonuçlar outputs/iyilestirme-codex-ai-guvence-23/http-check.json ve http-run.json. Run kalıcı dosyaları outputs/iyilestirme-codex-20261030/ui-data/calisma/ai-guvence-23/gguf-ee0bc758/{ham-kayitlar.json,rapor.json}. HTTP kabulü görsel ekran kabulü değildir; görsel son kontrol denetçiye açık eksik olarak devredilir.

İlk HTTP denemesi belirteçsiz 403 aldı; normal oturum belirteciyle düzeltildi, sunucu güvenliği değiştirilmedi. Sonraki ilk model denemesi OllamaHTTP500 ile fail oldu; http-check-ilk-http500.json ve guvence-23-gguf-hata-1793343413850.json korunur. Aynı koşu tekrarda geçti; kök neden çözülmüş veya istikrar kanıtlanmış sayılmaz.
