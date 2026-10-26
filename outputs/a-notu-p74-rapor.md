# Madde 3 · Beautiful Soup kabulü

27 Ekim 2026 · Codex

P74’e bir tahmin ve iki yazma görevi eklendi. Form görevi hidden/text/password alanlarını DOM sıralı çift listesinde korur; duplicate name, entity, disabled, boş değer, eksik form, method ve destek dışı kontrol davranışları ölçülür. Bağlantı görevi href, ilk base, göreli/mutlak/protokol bağımsız hedef, şema, fragment ve tekilleştirmeyi gerçek Beautiful Soup ile işler. Form alt kümesinin tarayıcı algoritmasının tamamı olmadığı açıkça yazıldı.

- `python -X utf8 tools/validate.py --yol python p74`: 1 ders, 29 kontrol, TEMİZ.
- `python -X utf8 tools/test_python_html_extraction.py`: gerçek Kali/Beautiful Soup; 2 referans geçti, 17 yanlış çözüm reddedildi, 0 yanlış çözüm geçti.
- Mutasyon sırasında base’i yok sayan ve FTP’yi kabul eden iki zayıflık bulundu; ayrı host/yol ve FTP örnekleriyle kapatıldı.
- Yeni paket indirilmedi, ağ hedeflerine istek gönderilmedi.

Öz değerlendirme: test 24/25, kapsam 24/25, derinlik 21/25, gerçeklik 15/15, yol değeri 8/10 = 92/100 (A). Tam tarayıcı form gönderimi kapsam dışında ve açıkça belirtiliyor. Bu puan Codex öz değerlendirmesidir; bağımsız denetim henüz tekrarlanmadı.
