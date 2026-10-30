# Madde 8 · jq -e kabulü

27 Ekim 2026 · Codex

BS29'a gerçek jq -e/-s ile hazır olma kapısı görevi ve tahmin eklendi. Çıkış kodu ile JSON truthiness ayrılıyor; 0 ve boş dizi, false/null, boş akış ve son çıktı davranışı gerçek araçta ölçülüyor. Görev tek JSON belgesi, object/boolean/number türleri, dahil 0/10 sınırları, boşluk girdi, çoklu belge ve bozuk JSON ayrımını sınar.

- `python -X utf8 tools/validate.py --yol bash bs29`: 1 ders, 13 kontrol, TEMİZ.
- `python -X utf8 tools/test_bash_jq_exit_gate.py`: tahmin birebir doğrulandı; 10 yanlış çözüm reddedildi, 0 geçen.
- Yeni paket kurulmadı; mevcut gerçek Kali jq/Bash kullanıldı.

Öz değerlendirme: test 24/25, kapsam 24/25, derinlik 22/25, gerçeklik 15/15, yol 9/10 = 94/100 (A). Bağımsız yeniden denetim yapılmadı.
