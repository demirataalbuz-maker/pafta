# Madde 11 · SFTP batch kabulü

27 Ekim 2026 · Codex

BS35'e gerçek OpenSSH sshd -i/internal-sftp üzerinde sftp -b ile put/get görevi eklendi. Mevcut anahtar ve host doğrulaması korunuyor, ağda dinleyen servis açılmıyor. Boşluklu yerel/uzak yollar, bütün baytları içeren ikili veri, sıfır bayt, değişen kaynak ve hedef, olmayan kaynak/klasör, gerçek aktarımın ardından bozulan geri indirme ölçülüyor. Batch yolu alt kümesi ve ayrı sunucu izolasyonu olmadığı açıklandı. SFTP'nin gerçek stderr ayrıntıları ayrı dosyada tutuluyor.

- `python -X utf8 tools/validate.py --yol bash bs34 bs35`: 2 ders, 17 kontrol, TEMİZ.
- `python -X utf8 tools/test_bash_sftp_batch.py`: referans geçti; 8 yanlış çözüm reddedildi, 0 geçen. JSON kanıtında test fail ile başlangıç çalıştırmasında beklenmedik çıkış kodu nedeniyle reddedilen error ayrı kaydedilir; altyapı hatası kabul edilmez.
- Bozma tanığı yalnız gerçek sftp başarılı bittikten sonra geri.bin'e bayt ekler; aktarım/kimlik doğrulama taklit edilmez.
- Yeni paket kurulmadı.

Öz değerlendirme: test 24/25, kapsam 24/25, derinlik 22/25, gerçeklik 15/15, yol 9/10 = 94/100 (A). Bağımsız yeniden denetim yapılmadı.
