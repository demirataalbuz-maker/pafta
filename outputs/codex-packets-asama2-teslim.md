# Wireshark / tcpdump · Aşama 2 teslimi

Kullanıcının bu yolun kalan beş maddesini Codex'e verme isteği kapsamında
PK19–PK29 eklendi. Yol: **29 ders, 6 rütbe, 59 görev, 29 gerçek tahmin**.
Önceki PK01–PK18 korundu; PK18'in kapsam cümlesi yeni derslere yönlendirildi.

| Plan maddesi | Dersler | Kod commit'i |
|---|---|---|
| PCAPNG ve farklı link-layer türleriyle gerçek kayıt kabulü | PK19–PK20 | `d5288a5` |
| TLS/HTTP2/QUIC trafiğini ve görünürlük sınırını uygulamalı incelemek | PK21–PK22 | `ed6daba` |
| TCP yeniden birleştirme ve analist iş akışı | PK23–PK24 | `fa24b35` |
| SMB2 ve Kerberos/LDAP kayıtlarında inceleme | PK25–PK27 | `2c313ec` |
| Gerçek CLI ile kayıt toplama, alan çıkarma ve özet raporu | PK28–PK29 | `2690a1e` |

Arayüz/zaman tablosu: `6dfe939`. Başlama kaydı: `22f507f`.

## Gerçek araç davranışı

- Classic PCAP ve PCAPNG 1.0 Enhanced Packet Block; Ethernet, RAW IP,
  Linux SLL/SLL2. Her arayüzün gerçek DLT'siyle ayrı libpcap derlemesi.
  Frame sırası, section/interface kimliği, caplen/wirelen ve ondalık/ikilik
  çözünürlüğe göre tam zaman kesri korunur. Multi-section ve ters byte-order
  testleri vardır. Destek dışı linktype ve eski PCAPNG packet blokları açık
  hatadır. TShark özgün kayıt üzerinde ayrıştırır; Python yalnız framing'i okur.
- TLS 1.3–h2 oturumu gerçek Python ssl/MemoryBIO; QUIC gerçek aioquic 1.3.0
  ile bellekte üretilir. Ağ bağlantısı açılmaz. HTTP/2 yanıtları 200/201/202,
  QUIC stream yükü PAFTA-QUIC-LAB. QUIC örneği HTTP/3 değildir.
  Doğru/yanlış/yok eğitim keylog profilleri gerçek TShark'ta ayrılır.
  Eğitim sırları korpusa aittir; kullanıcı sırrı veya keylog dosya yolu alınmaz.
- Tam/tekrarlı/sırasız/eksik TCP korpusunda gerçek iki geçişli TShark,
  reassembly tercihleri, Follow Stream ve HTTP export kullanılır. Tam nesne
  13 bayt PAFTA-TCP-LAB'dır; eksik segmentten nesne uydurulmaz.
  Sırasız korpustaki geç segment bu sürümde retransmission etiketi alır;
  ders native etiket ile gerçek ağ olayı çıkarımını ayırır.
- SMB2/Kerberos/LDAP tel-biçimi örnekleri Scapy/BER kodlayıcılarıyla üretilir.
  Hiçbir SMB sunucusuna veya KDC'ye bağlanılmaz; gerçek AD oturumu iddiası
  yoktur. SMB3 Transform tanığı AES-CCM ile şifrelenir ve üreticide decrypt
  assertion'ıyla doğrulanır; iç SMB2 komutu TShark'ta görünmez.
- `dil:tshark` komutları gerçek TShark argv'sine dönüşür; kabuk kullanılmaz.
  Alan sütunları, hiyerarşi/konuşma/io istatistikleri, Follow Stream, HTTP
  nesne ve filtrelenmiş PCAPNG çıktısı desteklenir. Çıktılar geçici klasör ve
  izin verilen adlarla sınırlıdır. CLI stdout ve dosya tablosu arayüzde birlikte
  görünür. Yeni fence/dil desteği ders ayrıştırıcı, doğrulayıcı ve arayüze bağlıdır.
- `dil:tcpdump-lab` kurulu Kali WSL'de gerçek tcpdump 4.99.6 çalıştırır.
  Yalnız kendi rastgele localhost UDP uç çifti; ilgisiz porta gönderilen
  eş boyutlu gürültü hariçtir. Kullanıcı BPF'si bağımsız native derlemeden
  geçer ve zorunlu uç filtresinin içine dengeli parantezlerle alınır.
  Snaplen 63/64/65 sınırı ve 20 datagramın 17+3 paketlik iki dosyaya
  döndürülmesi gerçek araç çıktısıyla ölçülür. Alt süreç kill/wait ile
  toplanır; çalışma dizini Linux /tmp altında ve geçicidir.

## Kurulum ve açık sınırlar

Paket kurulmadı. Önceki offline dersler kurulu Windows TShark/libpcap ile
çalışır. PK29 ayrıca WSL, PAFTA_WSL_DISTRO (varsayılan kali-linux), Python3,
tcpdump ve `wsl -u root` çağrısı ister. Döndürme profili lo MTU ≥60028 ister;
ağ ayarı değiştirilmez. Fiziksel arayüz, başka dosya yolu veya keyfî program
çalıştırma alınmaz. Profil paket sayısı/süre/boyutla sınırlıdır. Eksik
bağımlılık açık hata verir. README ve captures/README yeniden üretim araçlarını
ve korpus sınırlamalarını açıklar. `advanced.json` dosya/üretici/SHA256
manifestidir; yükleyici dosya özetlerini doğrular.

## Tamamlanan doğrulamalar

- Windows ve Git Bash `tools/validate.py --yol packets`:
  **29 ders / 185 kontrol, TEMİZ**.
- `tools/test_packet_curriculum.py --audit-json ...`:
  **29 ders / 59 görev / 29 tahmin / 313 mutasyon, bulgu yok**.
  Mantıksal eşdeğerliği belgelenmiş 5 değişiklik ayrıca sayılır;
  bunlar bozuk kural öldürülmüş gibi gösterilmez.
- `python -m unittest tools.test_packet_runtime tools.test_capture_formats
  tools.test_packet_crypto tools.test_packet_cli tools.test_packet_directory
  tools.test_packet_capture_lab tools.test_packet_app`: **35 test temiz**.
- API testinde PK03/PK13 yanında PK24/PK29 tahmin, görev, ilerleme ve tekrar
  akışı; gerçek CLI export ve gerçek loopback yakalaması doğrulandı.
- Node arayüz testleri (packet/Elastic/CMD): **19 test temiz**; komutların
  editöre yüklenmesi, stdout + dosya tablosu, tam zaman/arayüz alanları,
  HTML kaçışı ve tahmin öncesi çalıştırma düğmesinin gizlenmesi sınanır.
- Değişen kaynaklar UTF-8/LF; git diff --check temiz.

Tam uygulama Windows/Git Bash günlükleri sonuçlanınca aşağıya eklenir.

## Denetçi için kanıt dosyaları

- `outputs/codex-packets-final-mutations.json`: bütün 313 mutasyonun kodu,
  sonucu, reddedilen kontrolleri ve eşdeğerlik gerekçeleri.
- `outputs/codex-pcapng-mutations.json`, `codex-crypto-packet-mutations.json`,
  `codex-tcp-workflow-mutations.json`, `codex-directory-packet-mutations.json`,
  `codex-cli-capture-mutations.json`: madde bazındaki ilk geçişler.
- Üreticiler: `tools/build_packet_protocol_corpus.py`,
  `tools/build_packet_analysis_corpus.py`, `tools/build_packet_directory_corpus.py`.
- Korpus manifesti ve kullanım: `tracks/packets/captures/advanced.json`,
  `tracks/packets/captures/README.md`.

DENETIM.md, ASAMA2.md ve denetçinin Excel dosyası değiştirilmedi.
Yalnız kendi dosya/değişiklikleri commit edildi; push yapılmadı.
