# Kısmen maddeleri · Yerel tamamlama ve dış kabul sınırı · 27.10.2026

## Neden 60 düşüktü?

Önceki 78 puan: test 24/25, kapsam 15/25, derinlik 20/25, gerçeklik 9/15, yol 10/10. Büyük açık, AD13/14'ün yalnız sentetik ACL/elle yazılmış kenarları işlemesi; ASAMA2'nin gerçek grafik verisini okuma isteği karşılanmıyordu. AD15 gerçek DC görevi zaten depoda vardı ama puan kaydının ders eşlemesine alınmamıştı. Laptopta bu canlı laboratuvarın config'i yok.

## Bu teslim

- **60:** Resmi SpecterOps SharpHound örnek veri ZIP'i (165.712 bayt), kaynağı ve SHA-256 manifesti paketlendi. Hiçbir nesne kaydı veya ACL uydurulmadı/değiştirilmedi. Altı users/groups dosyası ham hash ile doğrulanıp görev alanına kopyalanır. Yeni AD14 görevi SID ile üyelik/primary group ve ACL yönlerini ayırır; inherited bilgisi, silinen nesneler, unsupported rights, aynı görünen ad, BFS/DFS farkı ve girdi bütünlüğünü sınar. ZIP ders çalışırken indirilmez, paket kurulmaz, DC'ye bağlanılmaz. Resmi örnekte DU001 → ADMINISTRATORS → DOMAIN ADMINS zinciri `MemberOf`/`WriteDacl` ile bulunur; ters yönde de ayrı bir ACL ilişkisi bulunduğu gerçek veriden doğrulandı.
- **37:** KQ22'ye gerçek portal kabul defteri eklendi: mevcut workspace/veri, query hash'i, 50 çalıştırma Results simulation, entity mapping, Review doğrulaması ayrı ayrı kaydedilir. Create/yayım bu teslimde yok. Yerel gerçek Kusto doğrulaması yeniden geçti ve test için açılan konteyner yeniden kapatıldı.
- **63:** AD22'ye Microsoft yordamıyla ldp.exe Connect/SSL/Bind/Search, izole negatif signing deneyi ve CBT ile karıştırmama bölümü eklendi. ldp GUI adımları artık yalnız araç adı olarak anılmıyor. Gerçek uygulama hâlâ lab gerektiriyor; LDAP yol taşıma testi iki gerçek Windows/WSL vakasında geçti, bu canlı bind kanıtı değildir.

## Puan ve durum

| Madde | Puan | Karar | Bekleyen |
|---|---|---|---|
| 37 | 91 (önceki puan) | Kısmen | Gerçek Sentinel çalışma alanında Test with current data / Review karşılaştırması |
| 60 | **78→91 (Codex yazar önerisi)** | Kısmen | Gerçek CE UI/Cypher karşılaştırması ve bu laptopta AD15 DC kabulü |
| 63 | 92 (önceki puan) | Kısmen | Bu laptopun gerçek DC bağlantısı ve ldp.exe kabul kaydı |

60 önerisinin dağılımı: test 24, kapsam 22, derinlik 23, gerçeklik 12, yol 10. Kaynak biçiminde gerçek export okuma ve sınır/yanlış çözüm testleri puan artışının nedenidir. Bu bağımsız denetim değildir; Claude tekrar ölçmelidir. Kısmenleri sadece puan yükselterek Tam yapmadım. Eski kayıtlar korundu.

## Bu makinede ölçülenler

- AD13–AD14: Windows ve Git Bash **2 ders, 8 kontrol TEMİZ**.
- Yeni grafik görevi: doğru çözüm pass, starter fail; **13 kasıtlı yanlış çözüm reddedildi**.
- AD'nin mevcut çevrimdışı regresyonları temiz; LDAP argv/yol testi **2 test OK**.
- KQ22 yerel Kusto: **TEMİZ**. Bu Sentinel hizmetinin önizlemesi değildir.
- Yönetilen `Pafta/labs/ad/config.json`, standart ldp.exe ve vmrun yolu yok. Azure CLI/profile bulunmadı; bu bulgu Azure hesabı/çalışma alanı olmadığı iddiası değildir. Çalışma alanına erişim doğrulanmadı.
- Ücretli abonelik, Azure kaynağı veya kural oluşturulmadı; AD VM kurulmadı; BloodHound CE sunucusu kurulmuş/çalıştırılmış sayılmadı. Kullanıcı ilerlemesi ve AI-Ek değişmedi. Commit/push yok.

## Kanıtlar

- [Grafik görevi kabulü](../../outputs/laptop-partials-ad60-acceptance.json)
- [Windows](../../outputs/laptop-partials-ad-windows.log) / [Git Bash](../../outputs/laptop-partials-ad-gitbash.log)
- [AD regresyonları](../../outputs/laptop-partials-ad-regression.log)
- [KQ22 yerel tekrar](../../outputs/laptop-partials-kq22-local.log)
- [Önkoşul/erişim tespiti](../../outputs/laptop-partials-prerequisites.json)
- Paket manifesti: `tracks/ad/veri/bloodhound/manifest.json`.

## Resmi kaynaklar

- [SpecterOps örnek veri](https://bloodhound.specterops.io/get-started/quickstart/ce-ingest-sample-data)
- [Ürünün SID/üyelik/ACE dönüştürmesi](https://github.com/SpecterOps/BloodHound/blob/main/packages/go/ein/ad.go)
- [Microsoft Sentinel Results simulation ve Review](https://learn.microsoft.com/en-us/azure/sentinel/detect-threats-custom)
- [Microsoft ldp.exe signing doğrulaması](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/enable-ldap-signing-in-windows-server)
- [LDAP TLS / signing / CBT ayrımı](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/ldap-signing)

## Sonraki gerçek CE kabulü — 27.10.2026

Bu raporun ilk tesliminden sonra SpecterOps BloodHound CE **9.9.0** ayrı yerel Docker laboratuvarına kuruldu. İmajlar digest ile sabitlendi; yalnız `127.0.0.1:18080` yayımlandı. Resmi ZIP ve değişmemiş JSON girişleri gerçek üründe işlendi. Gerçek Cypher yanıtındaki üç SID ve `MemberOf → WriteDacl` kenarları AD14 referans çözümüyle birebir karşılaştırıldı: **PASS**. [Ham ürün yanıtı ve karşılaştırma](../../outputs/audit-20261027/bloodhound-ce/acceptance.json).

Yukarıdaki ilk teslimde geçen “CE sunucusu kurulmadı / CE karşılaştırması bekliyor” ifadesi artık tarihsel kayıttır. Gerçek DC AccessCheck kabulü hâlâ eksik olduğundan #60 Kısmen kalır. CE web arayüzü görsel kabulü iddia edilmez. Bu ek yeni bir kalite puanı üretmez; 91/100 yazar önerisi ve bağımsız denetim bekleme durumu korunur.
