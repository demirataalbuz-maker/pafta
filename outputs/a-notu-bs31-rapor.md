# Madde 9 · journalctl JSON kabulü

27 Ekim 2026 · Codex

BS31'e gerçek journal-remote ile hazırlanan ayrı dosyadan journalctl -o json ve jq kullanarak kanıt raporu yazma görevi eklendi. Metin biçimini boşluktan parçalamak yerine JSON alanları okunuyor. PRIORITY metinden sayıya çevrilir, eksik değer dahil edilmez, 0/7 ve ara eşikler dahil uygulanır. Tam kimlik eşleşmesi, mikrosaniye zamanının metin olarak korunması, kaynak sırası, tab/tırnak/Unicode mesajlar ölçülüyor. Çok değerli/binary/büyük journal alanlarının genel normalleştirilmediği açıklandı; sistem journal'ına dokunulmuyor.

- `python -X utf8 tools/validate.py --yol bash bs31`: 1 ders, 17 kontrol, TEMİZ.
- `python -X utf8 tools/test_bash_journal_json.py`: 1 referans geçti; 9 yanlış çözüm reddedildi; 0 geçen.
- Paket indirilmedi; gerçek mevcut Kali araçları kullanıldı.

Öz değerlendirme: test 24/25, kapsam 24/25, derinlik 22/25, gerçeklik 15/15, yol 9/10 = 94/100 (A). Bu Codex öz değerlendirmesidir, bağımsız yeniden denetim değildir.
