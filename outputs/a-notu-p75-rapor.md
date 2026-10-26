# 01 · pip/venv yeniden kabul

27 Ekim 2026 · Codex

Kullanıcının istediği 01'den sıralı incelemenin ilk maddesi. Ders/anlatım/çözümler değiştirilmedi; önceki test onarımları güncel gerçek Kali ortamında tekrar sınandı. Yeni paket indirilmedi: dersin mevcut yerel kaynaklarından wheel üretilip geçici venv'lere çevrimdışı kuruldu.

- `python -X utf8 tools/validate.py --yol python p75`: 1 ders, 14 kontrol, TEMİZ.
- `python -X utf8 tools/test_python_venv_regression.py`: 2 gerçek çözüm geçti; --no-index kaldırma, metin sürüm sıralaması ve ters sürüm gerilemesi karşılaştırması reddedildi. 3 yanlış çözüm, 0 geçen. Bu hedefli regresyondur; bütün olası mutantlarda sıfır kaldığı iddia edilmez.
- Mevcut genel mutasyon kaydındaki > / >= eşdeğerliği korunuyor; eşdeğer mutant hata diye sayılmadı ve kayıttan silinmedi.

## Ölçütler

Test 24/25: gerçek pip/venv, wheel normalleştirme, bozuk hash, sistem Python'una sızmama, PYTHONPATH önceliği, kısıt sınırları ve yeni 0.9/0.10 regresyon tanığı mevcut; hedefli tekrar kabul kusurlu çözümleri reddetti. Bu mutasyon kümesi eksiksiz ispat değildir.

Kapsam 24/25, derinlik 23/25, gerçeklik 15/15, yol değeri 9/10: önceki bağımsız değerlendirmedeki bu dört ölçüt değişmedi. İçerik pip/venv, wheel, çevrimdışı kurulum, hash kilidi, paket deposu ile ortam farkı ve dependency resolver/backtracking'i gerçek araçta ölçüyor. Toplam 95/100 (A), Codex öz değerlendirmesi. Önceki bağımsız 86/100 puan ve bulgular korunur; bağımsız yeniden denetim yapılmadı.

02'nin 98 puanı kalite referansı olarak alındı; bütün kartlara aynı sayıyı yazmak yerine her kart kendi kanıtıyla değerlendiriliyor.
