# A notu · ikinci kapsam teslimi

27 Ekim 2026 · dal: codex/a-notu-104 · push yok.

Kullanıcının son kararı: önce A olmayan maddeler; 100 puan hedefi sonraya bırakıldı. Numara sırası izleniyor.

| Madde | Kapanan açık | Öz değerlendirme | Uygulama commit'i | Reddedilen yanlış çözüm |
|---|---|---|---|---|
| 12 | Gerçek Bats teardown; Git Bash/Linux farklarının gerçek envanteri | 94/A | 3f1fd61 | 7 |
| 13 | Gerçek PowerShell yönlendirme, multipart FileInfo ve başlık/gövde timeout | 94/A | 97b36ee | 12 |
| 14 | Gerçek FilterXml ve ham ToXml alanları; EVTX dosya yolu ve kaynak temizliği | 94/A | 3303dd8 | 11 |

Toplam 5 yeni yazma görevi, 1 yeni tahmin; 30 yanlış çözüm reddedildi, 0 geçen. Reddedilen çalışma zamanı ÇıkışKodu/error durumları JSON'larda test fail'den ayrı kaydedilir. Yeni paket indirilmedi. Her maddenin ayrıntısı a-notu-bs30-rapor.md, a-notu-ps23-rapor.md ve a-notu-ps27-rapor.md içinde.

## Doğrulama

- Bash tam yol: Windows ve Git Bash'te 35 ders, 347 kontrol TEMİZ.
- PowerShell son dosyalarla Windows tam yol: 29 ders, 278 kontrol TEMİZ.
- PowerShell Git Bash tam yol: 29 ders, 276 kontrol TEMİZ (son PS27 görevi eklenmeden önce); son PS27/28 ayrıca Git Bash'te 2 ders, 16 kontrol TEMİZ. PS23 ayrıca Git Bash'te 17 kontrol temiz.
- Çapraz ortam ham logları a-notu-dalga2-platform-kabul.json dosyasında listeli. Son PS27 Git Bash logu a-notu-ps27-git-bash.log; BS30 ve PS23 hedefli logları da saklandı.
- UTF-8/LF ve Python motor/test dosyalarının sözdizimi doğrulandı.

Bütün uygulamanın bu teslimde yeniden çalıştırıldığı iddia edilmiyor; değişen yollar ve yeni görevlerin iki çağıran ortamı sınandı. PowerShell 5.1 kabulünde Codex host'unun PS7 modül yolunun karışmaması için yalnız test sürecinde PSModulePath Windows 5.1 modüllerine ayarlandı; sistem ayarı değiştirilmedi.

## Panel ve devam

puanlar.json ve üretilen DENETIM_SAYFASI.html güncellendi. 12/13/14 açıkları kapatıldı; önceki bağımsız puanları saklanıyor ve yeni puanlar açıkça Codex öz değerlendirmesi olarak gösteriliyor. Bağımsız yeniden denetim bekleniyor.

Panelde 73/104 A var; tamamı henüz A değil. Sıradaki A olmayan madde 15: gerçek NTFS Deny sonrasında erişim karşılaştırması. Bu teslimde yarım yeni madde bırakılmadı.

Bilinen tezgâh sınırı: Windows PowerShell 5.1 FilterXml okuyucusunda & içeren EVTX yolu doğrudan çalışmadı; kaynak GUID adlı çalışma kopyasından okunuyor. Çalışma klasörü yolunun kendisinde & desteği iddia edilmedi. Bu durum derste ve kanıtta açık.
