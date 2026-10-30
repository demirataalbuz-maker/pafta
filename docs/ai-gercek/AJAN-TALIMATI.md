# AI dersleri · Claude ve Codex için çalışma talimatı

İki ajan aynı anda, aynı kopyada (`Documents\Pafta-AI-GercekLab`, dal `ai/gercek-pilotlar`) çalışıyor. İş bölümü yok: boştaki dersi alan yapar. Canlı tablo: `docs/ai-gercek/TAKIP.html`.

## Döngü

1. Ders al: `python -X utf8 tools/ai_ders_takip.py siradaki --kim codex` (ya da `claude`). Belirli bir ders için `al ID`. Almadığın derse dokunma.
2. Başlarken: `durum ID calisiliyor --kim ...`
3. Dersi oku ve karar ver: gerçek bir araç (yerel model, torch, gerçek dosya/süreç etkisi) bu derste öğrenilen şeyi gerçekten ölçebilir mi?
   - Ölçemiyorsa ya da mevcut deterministik görev zaten yeterliyse: `gereksinim ID yok`, ardından `durum ID gerekmez --not "gerekçe"`. Gerekçe yazmadan `gerekmez` deme; denetim bunu da kontrol eder.
   - Ölçebiliyorsa: `gereksinim ID ollama|torch|ollama+torch|baska`, sonra 4. adım.
4. Gerçek deney adımını ekle; dört pilot örnektir (ai-temel-03, ai-saldiri-02, ai-savunma-12, ai-guvence-07; tasarım `docs/ai-gercek-lab.md`).
   - Ders dosyasının **sonuna** `gorev "Gerçek deney · …"` adımı ekle; meta: `motor: ai-gercek`, `gereksinim: ...`. Mevcut adımları silme, yeniden yazma.
   - Test gerçek çağrı yapar ve `ai_lab.kanit_yaz(...)` ile `kaynak: gercek, kabul: true` kanıtı yazar; kanıt yoksa koşucu PASS vermez.
   - Testin içinde en az: boş kod, sabit cevap ve 2–3 anlamlı hatalı çözüm (mutant) reddedilmeli. Rastgele model çıktısını sabit metinle karşılaştırma. Saldırı başarısını geçme şartı yapma.
   - Yalnız sentetik veri ve canary. Gerçek kişisel veri, dış ağ, ücretli API yok.
5. Kendi kontrolün: dersi ders ekranında Kontrol ile geçir; `python -X utf8 tools/validate.py --yol <yol>` temiz olsun. Sonra `durum ID denetime-hazir --not "ne denendi, sonuç"`.
6. `bitti`yi yalnız denetim yazar. Kendi kontrolüne "bağımsız denetim" deme.

Takılırsan: `durum ID engelli --not "neden"`. Vazgeçersen: `birak ID`.

## Ortak dosyalar (iki ajan da dokunabilir, çakışma riski)

`sandbox/ai_gercek_lab.py`, `engine/runners.py`, `web/app.js`, `web/style.css`, `tools/test_ai_gercek.py`, `track.json` dosyaları.

- Derse özel laboratuvar kodunu mümkünse yeni bir dosyaya koy: `sandbox/ai_gercek_<ders_id>.py` (test içinden `from sandbox import ...`).
- Ortak dosyayı değiştirmen gerekiyorsa: düzenlemeden hemen önce dosyayı yeniden oku, yalnız küçük bir blok ekle, biçimlendirme/yeniden yazma yapma ve tabloda dersin notuna "ortak dosya: X değişti" yaz.
- `engine/` ya da `web/` davranışını değiştirecek bir şey gerekirse önce kullanıcıya sor.

## Kesin kurallar

- Yeni indirme/kurulum yok; gerekiyorsa kaynak, sürüm, boyut ve amaçla kullanıcıya sor, beklerken başka derse geç.
- Commit/push yok. Mevcut dosyaları silme.
- Yalnız kendi başlattığın süreçleri kapat. Kullanıcının Ollama sunucusunu, WSL'yi, Docker'ı kapatma; önceden yüklü modeli boşaltma.
- `ai-temel-17/18/20/22/23/24` dosyaları başka oturumda yazılıyor; tabloda "dosya yok" görünenlere dokunma.
- Ders yolu ya da cihaz yolu gömme; ortam değişkenleri `docs/ai-gercek-lab.md`'de.
- Ollama aynı anda iki ajandan çağrı alabilir; bellek yetmezse (8 GB VRAM) bekle ve yeniden dene, başkasının modelini boşaltma.


## Yeni katılan ajan: görünür veri standardı

Kullanıcının 29 Ekim 2026 kararı ve ayrıntılı çalışma/devir kuralları: `docs/ai-gercek/YENI-AJAN-REHBERI.md` (proje köküne göre). İşe başlamadan önce oku. Sonraki uygun örneklerde açılabilir/değiştirilebilir öğrenci veri dosyaları sun; sentetik örnek, kaydedilmiş çıktı, canlı deney ve gizli test verisini ayır. Tüm eski dersler dönüştürülmüş değildir. Rehber ortak panonun üst kısmında da kalıcı olarak görünür.
