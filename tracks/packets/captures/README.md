# Eğitim PCAP kayıtları

## PK28–PK29: CLI raporu ve gerçek kontrollü yakalama

PK28 `-T fields/-e` ile gerçek alan sütunları, `-q -z io,phs` ile
protokol hiyerarşisi ve `-w/-F` ile filtrelenmiş PCAPNG üretir. 4xx aralığı
399/400/401 ve 498/499/500 komşularıyla sınanır. CLI çıktısında Windows
CRLF satır sonları LF'ye normalize edilir; alan değerleri değiştirilmez.

PK29 `sandbox/packet_capture_lab.py` üzerinden Kali WSL root kullanıcısı
ile gerçek tcpdump çalıştırır. Yalnız lo, kendi rastgele localhost UDP uç
çifti, üç küçük / yirmi büyük eğitim datagramı. Aynı göndericiden başka bir
UDP porta eş boyutlu gürültü gönderilir ve bu trafik zorunlu filtreyle
dışlanır. Komut `-i lo -nn -s ... -c ... -w sonuc.pcap` biçimindedir;
döndürmede yalnız `-C 1 -W 2` profili vardır. Yanlış arayüz/yol/program
ve hostname açık hatadır. Kullanıcı filtresi tcpdump tarafından gerçekten
derlenir; uyumsuz filtre en fazla üç saniyelik yakalama süresinde hataya
dönüşür. İş sonunda tcpdump kill/wait ve Linux geçici klasör temizliği
uygulanır. Windows çağrısının ek üst sınırı 20 saniyedir.

Girdi `{"dil":"tcpdump-lab","laboratuvar":"kisa"}` veya `donusum`.
Kali Python3/tcpdump ve root çağrısı gerekir; dağıtım PAFTA_WSL_DISTRO'dan
okunur. Döndürme için lo MTU ≥60028 gerekir; ayar değiştirilmez.
Bu mod dış kayıt/keylog almaz. Diğer filtre/CLI modları canlı yakalama açmaz.

## SMB2, Kerberos ve LDAP

`tools/build_packet_directory_corpus.py` kurulu Kali Scapy kodlayıcısı ve
yerel BER üreticisiyle `smb-lab`, `kerberos-lab`, `ldap-lab` oluşturur.
Sunucuya bağlantı veya gerçek domaine giriş yoktur. Bunlar pasif tel-biçimi
tanıklarıdır; tam doğrulanmış AD oturumu yerine geçmezler. SMB2 komut/yön,
başarı ve farklı NTSTATUS; Kerberos alice/bob AS-REQ ve 23/24/25 hata;
LDAP Bind sonuçları 0/48/49/50 ve iki SearchRequest kökü içerirler.
SMB3 Transform tanığı gerçek AES-CCM ile üretilir ve üreticide decrypt
assertion'ı ile doğrulanır; TShark'ta iç SMB2 komutu görünmez.
`advanced.json` sabit dosya adları, üretici ve SHA256 özetlerini tutar;
korpus yükleyici dosya özetlerini denetler. Testler gerçek native alanları
seçer; manifest açıklaması ayrıştırılmış alan yerine kullanılmaz.

## TCP analist korpusu ve CLI

`tools/build_packet_analysis_corpus.py` dört sentetik TCP kaydı oluşturur:
`tcp-tam`, `tcp-tekrar`, `tcp-sirasiz`, `tcp-kayip`. HTTP istek/yanıtı
segmentlere ayrılır; çıkarılacak tam gövde PAFTA-TCP-LAB (13 bayt).
Native TShark etiketleri kaydın zaman/sequence bağlamına bağlıdır;
sırasız korpustaki geç orta segment bu sürümde retransmission etiketi alır.
Sırasız yeniden birleştirme tercihi açılınca tam gövde çıkar, eksik korpusta
eksik baytlar tamamlanmaz. TCP/HTTP baytları ağda gönderilmez.

Girdi `{"dil":"tshark","kayit":"tcp-sirasiz"}` olduğunda editör gerçek
TShark komutunu alır. `-r secili` dışında giriş yolu, geçici `sonuc` dışında
çıktı yolu verilmez; keylog profili JSON'dan seçilir. Desteklenen kapsam:
`-2`, `-Y`, `-T fields/-e/-E`, belirli TCP/HTTP `-o` tercihleri,
Follow TCP ascii/raw, protocol hierarchy/conversation/io istatistikleri,
HTTP nesne çıkarma ve `sonuc.pcap[ng]` dosyasına offline kayıt yazma.
Canlı `-i` bu editörde kabul edilmez. Çıkarılan dosyalar geçici klasörden
okunup `exports` ve sonuç tablosunda gösterilir; kalıcı dosyaya yazılmaz.

## TLS / HTTP2 / QUIC korpusu

`tools/build_packet_protocol_corpus.py` kurulu Kali ssl/cryptography/hpack ve
aioquic ile bellekte TLS 1.3–h2 ve QUIC oturumları üretir; soket açmaz.
`tls-h2.pcap` içinde HTTP/2 yanıtları 200/201/202; `quic-lab.pcap` içinde
ALPN pafta-lab ve PAFTA-QUIC-LAB stream verisi vardır (HTTP/3 değildir).
`*.keys` yalnız bu eğitim oturumlarının sırlarıdır; kullanıcının sırrı yoktur.
JSON `anahtar`: yok / yanlis / tls-h2 / quic-lab. Dosya yolu alınmaz.
Doğru sır, sır yokluğu ve yanlış sır testlerle ayrılır. Anahtar profili
TShark'ın geçici kişisel yapılandırmasına uygulanır. Kriptografik üretim
rastlantısaldır; üreticiyi yeniden çalıştırınca kayıt ve anahtar dosyaları
birlikte güncellenmeli, tahminler ve testler gerçek motorda doğrulanmalıdır.

## PCAPNG ve link-layer uzantısı

`arayuzler` kaydı `sandbox/packet_advanced_fixtures.py` tarafından üretilir:
Ethernet, RAW IP, Linux SLL ve SLL2; her arayüzde port 79/80/81 tanıkları
ve sonda kesilmiş paket. BPF her arayüzün gerçek DLT'siyle derlenir.
Ondalık/ikilik zaman çözünürlükleri tam kesir olarak korunur. Yeni girdi
kapsamı classic PCAP 2.4 veya PCAPNG 1.0 Enhanced Packet Block'tur;
PCAPNG eski Packet Block/Simple Packet Block açıkça reddedilir.
Aşağıdaki üç eski korpusun baytları ve tanımları değişmedi.

Bütün paketler `sandbox/packet_fixtures.py` tarafından baytlardan üretilir; kullanıcı trafiği kaydedilmez. `get_capture(ad)` dosyayla aynı baytları döndürür, `describe(ad)` bu dökümü verir. Classic Ethernet PCAP 2.4, FCS yok; dolgu dahildir. IPv4/TCP/UDP ve SCTP başlıkları gerçek uzunluk/checksum alanlarıyla kurulur. Kasıtlı kesilmiş paket, yakalanan bayt ile hat uzunluğu farkını öğretir.

Frame numaraları 1 tabanlı kayıt sırasıdır; IP kimliği veya başka kayda taşınan global kimlik değildir. Zaman başlangıcı Unix 1700000000 saniye, adım tam 1 saniye; göreli zaman `id-1`. Alanlar manifestte veri üreticisinin açıklamasıdır; Wireshark alanlarının varlığı ve akış/reassembly etkileri gerçek TShark'tan gelir. Özellikle sonraki fragment'te port alanı bulunmaz; TLS ClientHello bir anahtar veya şifre çözme verisi değildir.

Girdi: `{"dil":"wireshark","kayit":"temel"}` veya `{"dil":"bpf","kayit":"sinirlar"}`. Filtre metni tek başına editöre yazılır. Özel denemede `kayit` yerine `pcap_base64` verilebilir. Backend yalnız offline PCAP okur; canlı arayüz açmaz.

| Kayıt | Paket | Amaç | SHA-256 |
|---|---:|---|---|
| temel | 24 | ARP, DNS, TCP el sıkışma, HTTP, TLS başlığı, IPv6, SCTP, ICMP | `f60e4dade52fe26e726f4c45ce4415ad55ba5703f1319c091d213e917725bdbe` |
| sinirlar | 50 | Port/CIDR/boyut komşuları, fragment, VLAN/QinQ, HTTP durumları ve snaplen | `207c874848967402d49e5f268c42c0b6a7e0e55ea18c51b0064cdc9ff85c079c` |
| olay | 25 | DNS ve HTTP ilişkili örnek akış, benzer ama koşulu sağlamayan trafik | `7e20594d3875fed23289ddd2cb2996d45919e1dc75d76c703068ae22c8b1f0e6` |

## temel

| Frame | Göreli sn | Protokol | Kaynak | Hedef | Portlar | Yakalanan / hat | Açıklama |
|---:|---:|---|---|---|---|---|---|
| 1 | 0 | arp | 10.0.0.10 | 10.0.0.20 | — | 60 / 60 | ARP istek |
| 2 | 1 | arp | 10.0.0.20 | 10.0.0.10 | — | 60 / 60 | ARP yanıt |
| 3 | 2 | UDP | 10.0.0.10 | 10.0.0.53 | 53000 → 53 | 75 / 75 | DNS A sorusu |
| 4 | 3 | UDP | 10.0.0.53 | 10.0.0.10 | 53 → 53000 | 91 / 91 | DNS A yanıtı |
| 5 | 4 | TCP | 10.0.0.10 | 10.0.0.20 | 40000 → 80 | 60 / 60 | HTTP akışı SYN; TCP flags 0x02 |
| 6 | 5 | TCP | 10.0.0.20 | 10.0.0.10 | 80 → 40000 | 60 / 60 | HTTP akışı SYN ACK; TCP flags 0x12 |
| 7 | 6 | TCP | 10.0.0.10 | 10.0.0.20 | 40000 → 80 | 60 / 60 | HTTP akışı ACK; TCP flags 0x10 |
| 8 | 7 | TCP | 10.0.0.10 | 10.0.0.20 | 40000 → 80 | 147 / 147 | HTTP GET /health; TCP flags 0x18 |
| 9 | 8 | TCP | 10.0.0.20 | 10.0.0.10 | 80 → 40000 | 140 / 140 | HTTP 200 yanıtı; TCP flags 0x18 |
| 10 | 9 | TCP | 10.0.0.10 | 10.0.0.20 | 40001 → 443 | 60 / 60 | TLS akışı SYN; TCP flags 0x02 |
| 11 | 10 | TCP | 10.0.0.20 | 10.0.0.10 | 443 → 40001 | 60 / 60 | TLS akışı SYN ACK; TCP flags 0x12 |
| 12 | 11 | TCP | 10.0.0.10 | 10.0.0.20 | 40001 → 443 | 60 / 60 | TLS akışı ACK; TCP flags 0x10 |
| 13 | 12 | TCP | 10.0.0.10 | 10.0.0.20 | 40001 → 443 | 154 / 154 | TLS ClientHello; yalnız başlık; TCP flags 0x18 |
| 14 | 13 | UDP | 2001:db8::10 | 2001:db8::53 | 53001 → 53 | 95 / 95 | IPv6 DNS AAAA sorusu |
| 15 | 14 | TCP | 2001:db8::10 | 2001:db8::20 | 40002 → 443 | 74 / 74 | IPv6 TCP SYN; TCP flags 0x02 |
| 16 | 15 | SCTP | 10.0.0.10 | 10.0.0.20 | 50000 → 3868 | 66 / 66 | SCTP INIT |
| 17 | 16 | ICMP | 10.0.0.10 | 10.0.0.20 | — | 60 / 60 | ICMP echo isteği |
| 18 | 17 | ICMPv6 | 2001:db8::10 | 2001:db8::20 | — | 67 / 67 | ICMPv6 echo isteği |
| 19 | 18 | TCP | 10.0.0.10 | 10.0.0.20 | 41000 → 80 | 146 / 146 | HTTP istek portal.lab.test/admin; TCP flags 0x18 |
| 20 | 19 | TCP | 10.0.0.20 | 10.0.0.10 | 80 → 41000 | 150 / 150 | HTTP yanıt 401; TCP flags 0x18 |
| 21 | 20 | TCP | 10.0.0.10 | 10.0.0.20 | 41001 → 80 | 146 / 146 | HTTP istek portal.lab.test/login; TCP flags 0x18 |
| 22 | 21 | TCP | 10.0.0.20 | 10.0.0.10 | 80 → 41001 | 149 / 149 | HTTP yanıt 400; TCP flags 0x18 |
| 23 | 22 | TCP | 10.0.0.10 | 10.0.0.20 | 41002 → 80 | 148 / 148 | HTTP istek portal.lab.test/payment; TCP flags 0x18 |
| 24 | 23 | TCP | 10.0.0.20 | 10.0.0.10 | 80 → 41002 | 154 / 154 | HTTP yanıt 402; TCP flags 0x18 |

## sinirlar

| Frame | Göreli sn | Protokol | Kaynak | Hedef | Portlar | Yakalanan / hat | Açıklama |
|---:|---:|---|---|---|---|---|---|
| 1 | 0 | TCP | 10.0.0.10 | 10.0.0.20 | 42000 → 0 | 60 / 60 | Hedef port sınırı 0; TCP flags 0x02 |
| 2 | 1 | TCP | 10.0.0.10 | 10.0.0.20 | 42001 → 1 | 60 / 60 | Hedef port sınırı 1; TCP flags 0x10 |
| 3 | 2 | UDP | 10.0.0.10 | 10.0.0.20 | 42002 → 52 | 60 / 60 | Hedef port sınırı 52 |
| 4 | 3 | UDP | 10.0.0.10 | 10.0.0.20 | 42003 → 53 | 73 / 73 | Hedef port sınırı 53 |
| 5 | 4 | UDP | 10.0.0.10 | 10.0.0.20 | 42004 → 54 | 60 / 60 | Hedef port sınırı 54 |
| 6 | 5 | TCP | 10.0.0.10 | 10.0.0.20 | 42005 → 79 | 60 / 60 | Hedef port sınırı 79; TCP flags 0x02 |
| 7 | 6 | TCP | 10.0.0.10 | 10.0.0.20 | 42006 → 80 | 60 / 60 | Hedef port sınırı 80; TCP flags 0x12 |
| 8 | 7 | TCP | 10.0.0.10 | 10.0.0.20 | 42007 → 81 | 60 / 60 | Hedef port sınırı 81; TCP flags 0x10 |
| 9 | 8 | TCP | 10.0.0.10 | 10.0.0.20 | 42008 → 82 | 60 / 60 | Hedef port sınırı 82; TCP flags 0x04 |
| 10 | 9 | TCP | 10.0.0.10 | 10.0.0.20 | 42009 → 443 | 60 / 60 | Hedef port sınırı 443; TCP flags 0x11 |
| 11 | 10 | TCP | 10.0.0.10 | 10.0.0.20 | 42010 → 444 | 60 / 60 | Hedef port sınırı 444; TCP flags 0x18 |
| 12 | 11 | TCP | 10.0.0.10 | 10.0.0.20 | 42011 → 65534 | 60 / 60 | Hedef port sınırı 65534; TCP flags 0x02 |
| 13 | 12 | TCP | 10.0.0.10 | 10.0.0.20 | 42012 → 65535 | 60 / 60 | Hedef port sınırı 65535; TCP flags 0x02 |
| 14 | 13 | TCP | 10.0.0.10 | 10.0.0.20 | 53 → 44000 | 60 / 60 | Kaynak TCP port 53; TCP flags 0x10 |
| 15 | 14 | UDP | 10.0.0.53 | 10.0.0.10 | 53 → 44001 | 89 / 89 | Kaynak UDP port 53; DNS yanıtı |
| 16 | 15 | SCTP | 10.0.0.10 | 10.0.0.20 | 44002 → 53 | 66 / 66 | SCTP port 53 |
| 17 | 16 | UDP | 192.0.2.0 | 198.51.100.20 | 45063 → 9000 | 63 / 63 | Tam 63 bayt; IPv4 CIDR tanığı |
| 18 | 17 | UDP | 192.0.2.255 | 198.51.100.20 | 45064 → 9000 | 64 / 64 | Tam 64 bayt; IPv4 CIDR tanığı |
| 19 | 18 | UDP | 192.0.1.255 | 198.51.100.20 | 45065 → 9000 | 65 / 65 | Tam 65 bayt; IPv4 CIDR tanığı |
| 20 | 19 | UDP | 192.0.3.0 | 198.51.100.20 | 45127 → 9000 | 127 / 127 | Tam 127 bayt; IPv4 CIDR tanığı |
| 21 | 20 | UDP | 192.0.2.1 | 198.51.100.20 | 45128 → 9000 | 128 / 128 | Tam 128 bayt; IPv4 CIDR tanığı |
| 22 | 21 | UDP | 192.0.2.254 | 198.51.100.20 | 45129 → 9000 | 129 / 129 | Tam 129 bayt; IPv4 CIDR tanığı |
| 23 | 22 | UDP | 2001:db8:0:ffff:ffff:ffff:ffff:ffff | 2001:db8:ffff::20 | 46022 → 9000 | 62 / 62 | IPv6 /126 CIDR sınırı |
| 24 | 23 | UDP | 2001:db8:1:: | 2001:db8:ffff::20 | 46023 → 9000 | 62 / 62 | IPv6 /126 CIDR sınırı |
| 25 | 24 | UDP | 2001:db8:1::3 | 2001:db8:ffff::20 | 46024 → 9000 | 62 / 62 | IPv6 /126 CIDR sınırı |
| 26 | 25 | UDP | 2001:db8:1::4 | 2001:db8:ffff::20 | 46025 → 9000 | 62 / 62 | IPv6 /126 CIDR sınırı |
| 27 | 26 | TCP | 10.0.0.10 | 10.0.0.20 | 47000 → 80 | 60 / 60 | IPv4 ilk fragment; TCP başlığı var; fragment ofseti 0 × 8 bayt |
| 28 | 27 | TCP | 10.0.0.10 | 10.0.0.20 | — | 60 / 60 | IPv4 sonraki fragment; port alanı yok; fragment ofseti 3 × 8 bayt |
| 29 | 28 | TCP | 10.0.0.10 | 10.0.0.20 | 48000 → 80 | 60 / 60 | VLAN 100 TCP SYN; TCP flags 0x02 |
| 30 | 29 | TCP | 10.0.0.10 | 10.0.0.20 | 48001 → 80 | 60 / 60 | VLAN 101 TCP SYN; TCP flags 0x02 |
| 31 | 30 | UDP | 10.0.0.10 | 10.0.0.20 | 48002 → 53 | 80 / 80 | QinQ 100/200 DNS |
| 32 | 31 | TCP | 10.0.0.10 | 10.0.0.20 | 48003 → 80 | 60 / 60 | IPv4 IHL=6; TCP port ofseti değişir; TCP flags 0x02 |
| 33 | 32 | TCP | 2001:db8::10 | 2001:db8::20 | 48004 → 443 | 82 / 82 | IPv6 Hop-by-Hop ardından TCP |
| 34 | 33 | TCP | 2001:db8::10 | 2001:db8::20 | 48005 → 443 | 86 / 86 | IPv6 fragment ilk; fragment ofseti 0 × 8 bayt |
| 35 | 34 | TCP | 2001:db8::10 | 2001:db8::20 | — | 70 / 70 | IPv6 fragment sonraki; fragment ofseti 3 × 8 bayt |
| 36 | 35 | UDP | 10.0.0.10 | 10.0.0.53 | 49035 → 53 | 75 / 75 | DNS portal.lab.test tür 1 |
| 37 | 36 | UDP | 10.0.0.10 | 10.0.0.53 | 49036 → 53 | 75 / 75 | DNS portal.lab.test tür 28 |
| 38 | 37 | UDP | 10.0.0.10 | 10.0.0.53 | 49037 → 53 | 74 / 74 | DNS other.lab.test tür 1 |
| 39 | 38 | TCP | 10.0.0.10 | 10.0.0.20 | 50038 → 80 | 146 / 146 | HTTP seçim tanığı portal.lab.test/admin; TCP flags 0x18 |
| 40 | 39 | TCP | 10.0.0.10 | 10.0.0.20 | 50039 → 80 | 147 / 147 | HTTP seçim tanığı portal.lab.test/health; TCP flags 0x18 |
| 41 | 40 | TCP | 10.0.0.10 | 10.0.0.20 | 50040 → 80 | 145 / 145 | HTTP seçim tanığı other.lab.test/admin; TCP flags 0x18 |
| 42 | 41 | TCP | 10.0.0.20 | 10.0.0.10 | 80 → 51041 | 149 / 149 | HTTP durum sınırı 400; TCP flags 0x18 |
| 43 | 42 | TCP | 10.0.0.20 | 10.0.0.10 | 80 → 51042 | 150 / 150 | HTTP durum sınırı 401; TCP flags 0x18 |
| 44 | 43 | TCP | 10.0.0.20 | 10.0.0.10 | 80 → 51043 | 154 / 154 | HTTP durum sınırı 402; TCP flags 0x18 |
| 45 | 44 | TCP | 10.0.0.20 | 10.0.0.10 | 80 → 51044 | 152 / 152 | HTTP durum sınırı 499; TCP flags 0x18 |
| 46 | 45 | TCP | 10.0.0.20 | 10.0.0.10 | 80 → 51045 | 159 / 159 | HTTP durum sınırı 500; TCP flags 0x18 |
| 47 | 46 | TCP | 10.0.0.20 | 10.0.0.10 | 80 → 51046 | 153 / 153 | HTTP durum sınırı 501; TCP flags 0x18 |
| 48 | 47 | arp | 10.0.0.10 | 10.0.0.20 | — | 60 / 60 | ARP host filtresi tanığı |
| 49 | 48 | ICMP | 192.0.2.10 | 198.51.100.10 | — | 60 / 60 | IPv4 ICMP; taşıma portu yok |
| 50 | 49 | TCP | 10.0.0.99 | 10.0.0.20 | — | 36 / 64 | Kasıtlı snaplen kesimi; tam frame 64, yakalanan 36 bayt |

## olay

| Frame | Göreli sn | Protokol | Kaynak | Hedef | Portlar | Yakalanan / hat | Açıklama |
|---:|---:|---|---|---|---|---|---|
| 1 | 0 | UDP | 10.0.0.10 | 10.0.0.53 | 53010 → 53 | 75 / 75 | İstemci portal A sorusu |
| 2 | 1 | UDP | 10.0.0.53 | 10.0.0.10 | 53 → 53010 | 91 / 91 | Portal A yanıtı |
| 3 | 2 | TCP | 10.0.0.10 | 198.51.100.80 | 40100 → 80 | 60 / 60 | Web SYN; TCP flags 0x02 |
| 4 | 3 | TCP | 198.51.100.80 | 10.0.0.10 | 80 → 40100 | 60 / 60 | Web SYN ACK; TCP flags 0x12 |
| 5 | 4 | TCP | 10.0.0.10 | 198.51.100.80 | 40100 → 80 | 60 / 60 | Web ACK; TCP flags 0x10 |
| 6 | 5 | TCP | 10.0.0.10 | 198.51.100.80 | 40101 → 80 | 146 / 146 | HTTP istek portal.lab.test/admin; TCP flags 0x18 |
| 7 | 6 | TCP | 198.51.100.80 | 10.0.0.10 | 80 → 40101 | 150 / 150 | HTTP yanıt 401; TCP flags 0x18 |
| 8 | 7 | TCP | 10.0.0.10 | 198.51.100.80 | 40102 → 80 | 147 / 147 | HTTP istek portal.lab.test/health; TCP flags 0x18 |
| 9 | 8 | TCP | 198.51.100.80 | 10.0.0.10 | 80 → 40102 | 140 / 140 | HTTP yanıt 200; TCP flags 0x18 |
| 10 | 9 | UDP | 10.0.0.11 | 10.0.0.53 | 53011 → 53 | 74 / 74 | Diğer istemci DNS |
| 11 | 10 | UDP | 10.0.0.53 | 10.0.0.11 | 53 → 53011 | 90 / 90 | Diğer DNS yanıtı |
| 12 | 11 | TCP | 10.0.0.11 | 198.51.100.81 | 40103 → 80 | 145 / 145 | HTTP istek other.lab.test/admin; TCP flags 0x18 |
| 13 | 12 | TCP | 198.51.100.81 | 10.0.0.11 | 80 → 40103 | 150 / 150 | HTTP yanıt 401; TCP flags 0x18 |
| 14 | 13 | TCP | 10.0.0.10 | 198.51.100.80 | 40104 → 80 | 146 / 146 | HTTP istek portal.lab.test/login; TCP flags 0x18 |
| 15 | 14 | TCP | 198.51.100.80 | 10.0.0.10 | 80 → 40104 | 159 / 159 | HTTP yanıt 500; TCP flags 0x18 |
| 16 | 15 | TCP | 10.0.0.10 | 198.51.100.80 | 40105 → 443 | 154 / 154 | Portal TLS ClientHello; TCP flags 0x18 |
| 17 | 16 | UDP | 10.0.0.10 | 10.0.0.53 | 53012 → 54 | 75 / 75 | DNS benzeri veri fakat UDP port 54 |
| 18 | 17 | TCP | 2001:db8::10 | 2001:db8::80 | 40106 → 443 | 74 / 74 | IPv6 TCP SYN; TCP flags 0x02 |
| 19 | 18 | arp | 10.0.0.10 | 10.0.0.1 | — | 60 / 60 | ARP ağ geçidi sorusu |
| 20 | 19 | SCTP | 10.0.0.11 | 198.51.100.80 | 50001 → 80 | 66 / 66 | SCTP port 80; TCP değil |
| 21 | 20 | TCP | 10.0.0.10 | 198.51.100.80 | 40107 → 80 | 155 / 155 | HTTP istek portal.lab.test/administration; TCP flags 0x18 |
| 22 | 21 | TCP | 198.51.100.80 | 10.0.0.10 | 80 → 40107 | 154 / 154 | HTTP yanıt 402; TCP flags 0x18 |
| 23 | 22 | TCP | 10.0.0.10 | 198.51.100.80 | 40108 → 80 | 145 / 145 | HTTP istek other.lab.test/admin; TCP flags 0x18 |
| 24 | 23 | TCP | 198.51.100.80 | 10.0.0.10 | 80 → 40108 | 150 / 150 | HTTP yanıt 401; TCP flags 0x18 |
| 25 | 24 | UDP | 10.0.0.99 | 10.0.0.53 | 53013 → 53 | 75 / 75 | Farklı istemci ve harf durumu DNS |

Kayıtlar gerçek motorlarla açılır. Wireshark görüntü filtrelerinin katman çözümlemesi ile BPF'nin byte/offset modeli farklı olabilir; BPF `vlan` sonraki derleme ofsetini değiştirir. `len` özgün hat uzunluğu, erişilebilen byte sınırı ise caplen'dir. BPF için kullanılabilir sözdizimi kurulu libpcap 1.10.6'ya bağlıdır; sayısal adres/port kapsamı derslerde açıklanır.

Kaynaklar: [TShark](https://www.wireshark.org/docs/man-pages/tshark.html), [görüntü filtreleri](https://www.wireshark.org/docs/man-pages/wireshark-filter.html), [pcap-filter](https://npcap.com/guide/wpcap/pcap-filter.html), [pcap_offline_filter](https://npcap.com/guide/wpcap/pcap_offline_filter.html).
