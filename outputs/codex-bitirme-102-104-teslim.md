# Bitirme 102 ve 104 · Codex teslimi

26 Ekim 2026. Kullanıcının görselindeki iki mavi madde teslim edildi; 103 kapsamda değildir. Bağımsız denetime hazır olarak işaretlendi, Bitti kararı verilmedi. Yeni paket indirilmedi; push yapılmadı. DENETIM.md ve ASAMA2.md değiştirilmedi.

| Madde | Teslim | Commit |
|---|---|---|
| 102 | BT01–BT04: hash manifesti, UTC çizelgesi, Kusto/SPL araması, Sigma seçicisi ve gerçek TShark ile ortak vaka incelemesi | e1f59b7 |
| 104 | BT05–BT06: iddia defteri, rapor eki, tespit boşluğu planı, replay kabulü; örnek anlatı ve yeniden üretilebilir sonuç | 2518fe5 |

Yeni `tracks/bitirme` yolu Pafta'nın otomatik yol keşfiyle açılır. Altı rütbede BT01–BT06 sıralı, her derste tahmin ve iki görev vardır. Koşucu `engine/runners.py` içinde kayıtlıdır; dosyalar her çalışmada geçici çalışma dizinine kopyalanır. Ortak dosyalar düzenlenmeden önce git status kontrol edildi; başka ajanın commit edilmemiş değişikliği görülmedi.

## Çalıştırılmış kabul

- Windows ve Git Bash: `python -X utf8 tools/validate.py --yol bitirme` → **6 ders, 30 kontrol temiz** (6 tahmin, 12 çözüm, 12 başlangıç reddi).
- Her iki ortamda `python -X utf8 tools/test_capstone.py` → **3 test temiz**; altı tahmin stdout'u beklenen gerçek sonuçla uyuştu; 12 görevde **52 bozuk çözüm** reddedildi.
- Adapter regresyonu: hash bütünlüğü; PCAP'in fixture builder ile bayt bayt yeniden üretimi; frame uç/tür sınırları; SPL _time'ın gerçek epoch olması; desteklenmeyen dil/sorgu ve bozuk native filtrenin açık hatası; korpus baytlarının değişmemesi.
- `python -X utf8 tools/capstone_replay.py --out outputs/codex-bitirme-replay.json` ile gerçek motor sonuçlu örnek rapor üretildi. Araçlar: Python 3.11.9, pySigma 1.5.1, TShark 4.6.8. Örnek sonuç: üç auth kaydı, bir endpoint kaydı ve frame 1. CommandLine alanı kaldırılmış kontrolde FN=1, recall=0; eksiklik başarı sayılmadı.
- Kayıtlı sonuçta sorgu/kural/filtre metinleri, araç sürümleri, manifest SHA256, seçilen kanıtlar, zaman çizelgesi ve metrikler bulunur.

Bu teslimde bütün depo için tam validate çalıştırıldığı iddia edilmez; yeni yolun tamamı iki ortamda doğrulandı. Önceki yolların motor kodları değiştirilmedi; yeni adapter mevcut motorları çağırır.

## Gerçeklik sınırı ve insan kabulü

Vaka bütünüyle sentetiktir, saldırı zinciri veya canlı trafik üretilmedi. Kusto/SPL mevcut Pafta→SQLite çeviricileri; Sigma gerçek pySigma ve mevcut yerel olay backend'idir. Bunlar üretim Sentinel/Splunk pipeline veya dağıtım kabulü değildir. Paket filtresi gerçek native TShark'tır. PCAP yalnız istekleri içerir; yanıt/gövde veya dosya kimliği kanıtı yoktur. Aynı TCP segmentinin tekrarını yeni HTTP isteği saymama davranışı native araçta ölçüldü ve testte korundu.

Rapor derslerinin otomatik testleri yapı, alanlar, referanslar ve sayısal kabul kapılarını ölçer. Serbest Türkçe metnin doğruluğu, kanıtın iddiayı desteklemesi, hizmet etkisi ve önerinin boşlukla ilişkisi için açık **insan inceleme rubriği** vardır. Otomatik testin geçmesi veya örnek raporun üretilmesi insan onayı/öğrenci yazarlığı sayılmaz. Replay JSON'da human_review=pending kaydedilir. Sayısal eşikler eğitim politikasıdır; NIST veya ürün varsayılanı olarak sunulmaz.

Örnek anlatı: `tracks/bitirme/ornek-rapor.md`. Gerçek replay: `outputs/codex-bitirme-replay.json`. Öğrenci kendi raporunu Pafta tezgâhında üretir ve rubriğe göre inceletir. Yeni paket/abonelik, ağ izolasyonu, hesap kilitleme veya üretim politikası değişikliği gerekmez.
