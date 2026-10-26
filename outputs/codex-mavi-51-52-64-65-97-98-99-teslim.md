# Mavi maddeler · Codex teslimi

26 Ekim 2026. İstenen yedi madde denetime hazır; bağımsız denetim/Bitti kararı verilmedi. Push yapılmadı. DENETIM.md ve ASAMA2.md değiştirilmedi.

| No | Teslim | Commit |
|---|---|---|
| 51 | YR23: gerçek libyara externals, include_callback, sources/namespace | e6d0254 |
| 52 | YR24: korpus taraması, sonuç/timeout ayrımı, ölçülen süre ve bayt raporu | 893ae19 |
| 64 | AD24–AD25: SYSVOL biçimleri ve LAPS okuma kanıtı | 7fa4b29 |
| 65 | Mevcut JV15 için yeniden üretilebilir gerçek Spring Security kabulü | 4e70d2c |
| 97 | PU04–PU05: MISP/IOC yaşam döngüsü ve gerçek SQLite avcılığı | 07e3c5a |
| 98 | PU06–PU07: ASR, Exploit Guard, LAPS köprüsü ve AppLocker kabulü | 2debc74 |
| 99 | PU08–PU09: CloudTrail ve Graph Entra kayıt analizi | fb93fa3 |

## Çalıştırılmış doğrulamalar

| Kapsam | Windows | Git Bash |
|---|---|---|
| YARA yolunun tamamı | 24 ders, 144 kontrol temiz | 24 ders, 144 kontrol temiz |
| Yeni AD24–AD25 | 2 ders, 12 kontrol temiz | 2 ders, 12 kontrol temiz |
| Java yolunun tamamı | 16 ders, 84 kontrol temiz | 16 ders, 84 kontrol temiz |
| Purple yolunun tamamı | 9 ders, 47 kontrol temiz | 9 ders, 47 kontrol temiz |

Bu teslimde bütün depo için tam validate çalıştırıldığı iddia edilmez. AD'nin canlı laboratuvar isteyen eski dersleri bu hedefli kabulün kapsamında değildir.

- `python tools/test_yara_bundle.py`: 4 test temiz; iki gerçek tahmin ve 10 bozuk çözümün reddi. Eski `tools/test_yara_runtime.py`: 15 test temiz.
- `python tools/test_ad_policy_lessons.py`: 2 test temiz; iki gerçek tahmin, 14 mutasyon reddi.
- `python tools/test_security_lesson.py`: 2 test temiz; gerçek Spring çıktısının 21 satırı JV15 ile uyuştu; 8 mutasyon reddi.
- `python tools/test_purple_extensions.py`: Windows ve Git Bash'te 2 test temiz; altı gerçek tahmin, 12 görevde 38 mutasyon reddi.
- Purple altı rütbeye dağıtıldı; PU01–PU09 sıralı, yeni altı dersin her birinde tahmin ve iki görev var.

## Gerçek araç ve kapsam sınırları

YARA gerçek yara-python/libyara kullanır. Include yalnız dersin verdiği dosya sözlüğünden çözülür, ana makine dosyalarını açmaz. Paket API'sinin sınırları: örnek başına 1 MiB, en fazla 32 örnek, tarama başına 1–5 saniye. Timeout temiz dosya sonucu sayılmaz. Süre ölçülür, makine hızına bağlı eşikle not verilmez. Küçük korpustaki timeout raporlama tanığı gerçek libyara timeout'u oluştuğu iddiası değildir. CLI kurulmadı.

AD24 gerçek UTF-16 INI/XML/binary başlık ayrıştırır; Registry.pol görevinde yalnız başlık doğrulanır, tam politika motoru yoktur. AD25 JSON, FILETIME ve sağlanan yetki gözlemlerini değerlendirir. GPO uygulama, canlı LAPS kurulumu/parola döndürme veya gerçek ACL hesabı iddia edilmez.

65 için kullanıcının açık onayıyla Maven Central bağımlılıkları `%LOCALAPPDATA%\Pafta\m2` önbelleğine indirildi. Pinli sürümler: Spring Security 7.0.2, Spring Framework 7.0.10, Servlet API 6.1.0; JDK 21 ve mevcut Maven kullanıldı. `python tools/security_lab.py` varsayılan çevrimdışı çalışır; `--download` açıkça seçilmeden indirme yapmaz. Gerçek çıktı `outputs/java-security-real.txt` içinde. JV15'in önceki yazarı Claude'dur; ders tekrar yazılmadı, gerçek kaynak düzeni ve sınır tanığı eklendi. Java okuma düzeyinde kaldı.

PU04–PU09 belgelenmiş biçimlerde sentetik çevrimdışı kayıtlarla gerçek Python/SQLite/XML çalıştırır. MISP sunucusu/decay motoru, Defender/AppLocker eşleştiricisi veya AWS/Graph API taklit edilmez. TTL ve pilot/teslim kapıları açık eğitim politikasıdır. Bulut aboneliği, ana makineye önleme politikası veya yeni paket kurulumu yapılmadı. Kaynaklar her dersin ilgili anlatımında; ürün üzerinde doğrulanmamış etki başarı diye sunulmaz.

`docs/durum.json` yedi madde için denetime-hazir ve ilgili commitleri içerir. `tools/durum_listesi.py` ile yerel DURUM.html yeniden üretilir.
