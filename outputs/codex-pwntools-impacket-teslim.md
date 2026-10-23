# Codex teslim raporu · pwntools ve Impacket

Atama kaynağı: kullanıcının Masaüstü Pafta_Takip.xlsx dosyası, Yapılacaklar sayfası.
Dosyadaki 5. ve 6. satır (Sıra 3 ve 4) Codex / Bekliyor olarak okundu.
Excel'deki atamalar/durumlar değiştirilmedi.

## Tamamlanan işler

| Madde | Teslim | Commit |
|---|---|---|
| pwntools kullanan hazır betiği okumak ve uyarlamak | P76 packing/context; P77 yerel process/tube, timeout ve EOF. İki ders, dört görev. | 312e90b5030fcb46e935604c674fd05914aee90d |
| Impacket kullanan Windows/AD protokol betiğini okumak | P78 SID binary parse/serialize; P79 SMB2 alanları ve ECHO kaydı. İki ders, dört görev. | Bu raporla aynı commit. |

Her ders Başpehlivan ekosistem modülüne kaydedildi ve gerçek çalıştırmayla karşılaştırılan bir tahmin içeriyor.
Mevcut Kali WSL koşucusu kullanıldı; pwntools 4.15.0 ve Impacket 0.14.0.dev0 zaten kurulu.
Paket indirilmedi/kurulmadı. Yeni motor veya ortak koşucu değişikliği gerekmedi.

## Kabul sonuçları

- Windows ve Git Bash: `python tools/validate.py p76 p77 p78 p79` → 4 ders, 26 kontrol, TEMİZ.
- `python tools/test_pwntools_lessons.py` → 4 test grubu geçti; 35 mutasyon reddedildi.
  Test Windows ve Git Bash çağırıcılarında gerçek Kali üzerinde çalıştırıldı.
- `python tools/test_impacket_lessons.py` → 4 test grubu geçti; 43 mutasyon reddedildi.
  Test Windows ve Git Bash çağırıcılarında gerçek Kali üzerinde çalıştırıldı.
- Dört tahminin cevabı gerçek stdout ile bayt içeriği bakımından karşılaştırıldı; stderr boş.
- Sekiz örnek çözüm geçti; sekiz başlangıç kodu geçmedi.
- Eklenen dosyalar UTF-8/LF; track.json'a yalnız yeni ders kimlikleri eklendi.

İlk mutasyon turunda P79'un bool tür kontrolünü kaldıran değişiklik geçebildi:
True ile MessageID=1 ve False ile MessageID=0 eşleşmeleri eklendi; son turda bu mutant da reddedildi.
P77 timeout testlerinde çocuk süreç hazır bariyeri var; kısa timeout ile süreç başlatma hızını ölçmüyor.

## Tam depo doğrulamasında kalan bulgu

P76/P77 entegrasyonu sırasında Windows ve Git Bash'ten tam `python tools/validate.py` çalıştırıldı:
her ikisi 403 ders / 3479 kontrol saydı ve yalnız `powershell/ps22:6 — Gerçek ACL raporu` başarısız oldu.
Beklenen KLASOR/ANAHTAR ACL satırları yerine yalnız `TEMIZ\n` döndü.
Ardından Windows'ta tek başına `python tools/validate.py ps22` çalıştırıldı: aynı hata tekrarlandı.
Dolayısıyla iki tam doğrulamanın aynı anda çalışmasına özgü bir sonuç değil.
PS22 dosyasına dokunulmadı; mevcut ortamda nedeni bu teslimde araştırılmadı.

P78/P79 eklenmesinden sonra yukarıdaki **dört dersin** doğrulaması her iki ortamda tekrarlandı.
Son repo halinin bütün yolları temiz geçtiği iddia edilmiyor; tam depo sayıları P76/P77 anlık görüntüsüne ait.

## Kapsam ve sürüm sınırları

- pwntools: gerçek packing, context ve yerel process/tube; uzak bağlantı, ELF veya debugger yok.
- Impacket: gerçek yerel yapı nesneleri; AD/DC bağlantısı, kimlik doğrulama veya kriptografik imza doğrulaması yapılmadı.
- Kurulu LDAP_SID metin yardımcılarının authority'yi tek baytla sınırlaması derste gerçek örnekle gösterildi.
  Görevler altı baytlık authority alanını kayıpsız kullanır.
- SMB özetleyicisi tek SYNC yanıt başlığını kabul eder; ASYNC ve NextCommand != 0 açıkça reddedilir.
  SIGNED bayrağı doğrulanmış imza anlamına gelmez.
- Kaynaklar derslerin ilgili açıklamalarında verilmiştir; kurulu kaynak ve gerçek çıktı ayrıca kontrol edildi.

## Durma noktası

Bu iki madde tamamlandı. Yarım bırakılmış Codex işi yok.
Sıradaki atama: **CMD: wevtutil ile offline EVTX sorgu ve export**; başlanmadı.
Yazar 1'in Bash BS31 / track.json çalışmasına dokunulmadı.
DENETIM.md ve ASAMA2.md değiştirilmedi. Push yapılmadı.
