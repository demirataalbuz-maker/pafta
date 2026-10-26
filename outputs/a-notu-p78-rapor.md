# Madde 7 · Impacket betiği okuma kabulü

27 Ekim 2026 · Codex

P78'e iki görev eklendi; mevcut gerçek SID ve P79 SMB görevleri korunuyor. İlk görev Kali paketindeki gerçek smbclient.py dosyasının argparse bildirimlerini AST ile, programı çalıştırmadan okur. Positional hedef, bağlantı/kimlik doğrulama seçenekleri, alias, kaynak sırası, action/default/choices ve dinamik ifadenin açık hatası ölçülür. Envanterin çalışma zamanı argparse doğrulaması olmadığı açıkça yazıldı.

İkinci görev gerçek importlib ve metadata ile import edilen dosya/sürümü döndürür. Eksik modül, var olan modülün eksik bağımlılığı, eksik metadata ve eksik API ayrılır. Geçici modüller gerçek import hataları üretir; başka ImportError gizlenmez, None değerli simge var kabul edilir. Ağ veya paket kurulumu yoktur.

- `python -X utf8 tools/validate.py --yol python p78 p79`: 2 ders, 17 kontrol, TEMİZ.
- `python -X utf8 tools/test_python_impacket_reading.py`: 2 referans geçti, 14 yanlış çözüm reddedildi, 0 yanlış çözüm geçti.

Öz değerlendirme: test 24/25, kapsam 24/25, derinlik 22/25, gerçeklik 15/15, yol değeri 8/10 = 93/100 (A). İlk dalganın betik okuma/protokol verisi kapsamı içindir; bir canlı AD/DC oturumunun kabulü olarak sunulmuyor. Bağımsız yeniden denetim henüz yapılmadı.
