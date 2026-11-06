# Saldırı 51 — gerçek deney teslimi

2026-11-03 · Yazar Codex · Bağımsız denetçi claude-opus (bekleniyor). Puan verilmedi.

Kullanıcının “evet onay verdim” onayından sonra izole MLflow 2.1.1 ve 2.2.1 imajları kuruldu. Ders, CVE-2023-1177 için gerçek registry/artifact HTTP akışını karşılaştırıyor. Üç kusurlu başlangıç görevi, açılabilir JSON ve ham HTTP örneği, tahmin→çalıştır→fark, hata vitrini, kanıt yorumlama ve saldırı–savunma eşlemesi tamamlandı.

| Gerçek gözlem | MLflow 2.1.1 | MLflow 2.2.1 |
|---|---|---|
| Normal artifact | Okundu | Okundu |
| İzole labın özel canary dosyasını local source ile okuma | Okundu | Reddedildi (HTTP 400) |

CLI kabulü, ders ekranı Check kabulü ve ders ekranı Run denemesi ayrı rastgele canary ile aynı dört gözlemi üretti. Her deneyde 11 gerçek HTTP kaydı, gerçek sürüm, pip freeze, image ID, izolasyon inspect, istek/yanıt, cihaz ve cleanup sonuçları kaydedildi. Deney başarısızlığı PASS sayılmıyor; saldırının başarılı olması kabul şartı değil. Normal kontrolün çalışması ve gözlemin doğru sınıflandırılması gerekiyor.

## Kendi kontrollerim

- İzole PAFTA_DATA ile `.ai-venv/Scripts/python.exe -X utf8 tools/validate.py ai-saldiri-51`: TEMİZ, 9 kontrol.
- `docs/denetim/araclar/tahmin.py . ai-saldiri-51`: 1 tahmin, 0 şüpheli.
- Gerçek adımı çıkarılmış kopyada `mutasyon.py <kopya> --en-cok 1000 ai-saldiri-51`: 38 mutant, 0 geçen (11+15+12).
- `kopya_sonda.py ai-saldiri ai-saldiri-51 "from sandbox.ai_gercek_ai_saldiri_51 import referans_rapor as yama_raporu"`: reddedildi. Import/module/getattr/exec yollarıyla dört kopya sondası da reddedildi; module attribute değişikliği de reddedildi.
- Normal kontrolü yok sayan, yama yönünü tersleyen, hatayı kabul sayan 3 anlamlı yanlış çözüm reddedildi. Çocuğa özel erişilemeyen Docker endpoint durumunda kabul verilmedi.
- Ders ekranında starter reddedildi; referans Check 6/6 kabul edildi. Run gerçek çıktı üretti ve kabul=false olarak gösterildi. İlk referans Check denemesinde Failed to fetch görüldü; o deneme kabul sayılmadı, sonraki başarılı deneme ayrı kanıtla doğrulandı.
- İlk üç görevin açılabilir sentetik dosyaları Run ile gösterildi. Bunlar gerçek MLflow kanıtı değildir. Mock lifecycle kayıtları ayrıca fixture/kabul=false olarak tutuldu.
- `python -X utf8 tools/test_sinav.py`: 12 test OK. `node --check` (app.js'in .mjs kopyası) ve ilgili `git diff --check` başarılı. Bütün müfredatın regresyonu bu teslimde yeniden koşulmadı.

## Dosyalar ve kayıtlar

- Ders: `tracks/ai-saldiri/lessons/ai-saldiri-51-ml-altyapisi-cve.md`; ilgili fixture README/JSON/.http dosyaları.
- Runtime: `sandbox/ai_gercek_ai_saldiri_51.py`; Docker kaynakları: `sandbox/s51_docker/{Dockerfile,server.py,.dockerignore,README.md}`.
- Kurulum aracı: `tools/ai_s51_kur.py` (`--kontrol` salt okunur, `--kur` ayrı onaylı işlem). Ders otomatik pull/build yapmaz.
- `tracks/ai-saldiri/track.json`: yalnız 51 kaydı eklendi. `web/app.js`: Docker adımındaki yanlış Ollama rozetini düzelten dar görüntü değişikliği; diğer koşucular değişmedi.
- Kurulum raporu/logları, pip URL/hash kayıtları: `outputs/s51-kurulum/20261103T091940Z/`.
- Mutasyon ve yanlış/kopya/altyapı sondaları: `outputs/yeni-ai-saldiri-51/`; eski eksik-imaj kayıtları tarihsel başarısız hazırlıktır, güncel başarı yerine kullanılmaz.
- UI kabul ekranı: `C:/Users/demo12/Desktop/pafta-s51-ui-kabul-20261103.png`.

## Kurulum ve sınırlar

Taban Python 3.10 slim-bookworm linux/amd64 manifesti digest ile sabit. MLflow 2.1.1/2.2.1 ve PyPI bağımlılıkları yalnız Docker imajlarına kuruldu; mevcut venv değiştirilmedi. Görüntü boyutları 1.351.630.645 ve 1.355.951.699 bayt: toplam mantıksal 2.707.582.344 bayt. Katmanlar ortak olduğundan bu sayı gerçek ek disk tüketimi değildir. Başlangıçtaki 1–2 GB tahmini düşük kaldı; ağdan indirilen toplam bayt ölçülmedi.

Runtime ağsız, nonroot, salt okunur root, tmpfs, cap-drop ALL, no-new-privileges ve CPU/RAM/PID sınırlarıyla çalıştı. Host portu/dizini/socket mount edilmedi. Her koşu yalnız kendi tam container ID'lerini kaldırdı. Kullanıcı container'ları, Docker Desktop, WSL ve kurulan imajlar korunur.

Kapsam MLflow CVE-2023-1177'dir. Gradio/Jupyter için gerçek lab yapılmadı; container escape ya da genel ürün güvenliği kanıtlanmadı. 2.2.1 güncel veya genel olarak güvenli sürüm diye sunulmaz. S49 Opus tarafından kabul edilmişti; S51 bu raporla denetime sunuluyor. Savunma32/33, ortak panodaki 03.11.2026 12:21 kullanıcı kararıyla claude-yazar’a devredildi; Codex’e açık yeni ders kalmadı. Commit/push yok.

## Kanıt bütünlüğü

- `C:\Users\demo12\Desktop\pafta-s51-gercek-kabul-20261103\ai-kanit\saldiri51-kabul-1793697999970.json` · SHA256 `595fd0856ea3e07d3bb69121225c9cfb2835796b15ee2dc26a34496efa3bf6d3`

- `C:\Users\demo12\Documents\Pafta-AI-GercekLab\outputs\yeni-ai-saldiri-51\ui-data\ai-kanit\saldiri51-kabul-1793698270500.json` · SHA256 `5a1e03290f051eb5d4d7de2c64699eab00ecaf74a907a2ca45568b88d5698544`

- `C:\Users\demo12\Documents\Pafta-AI-GercekLab\outputs\yeni-ai-saldiri-51\ui-data\ai-kanit\saldiri51-run-1793698320449.json` · SHA256 `9b5259857dd7ba9291d0c6e5144e1e5ae4352a845ed8acdda36c9f48e92be608`
