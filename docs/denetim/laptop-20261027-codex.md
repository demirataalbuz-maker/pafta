# Laptop aktarımı sonrası Codex düzeltmeleri · 27 Ekim 2026

Bu teslim ders/koşucu düzeltmesidir. Kalite puanlarını yazar yeniden önerdi; bağımsız denetçi Claude'un tekrar ölçümü beklenir. Yalnız validate yeşili, 108 maddenin kapsamının tamamen karşılandığı anlamına gelmez. Önceki 88/108 PASS sonucu, hata listesinde bulunmayan dersleri otomatik eşleyerek elde edilmişti; bağımsız kalite denetimi olarak kullanılmamalı.

## Puan değişiklikleri

| Madde | Önce | Önerilen | Değişiklik |
|---|---:|---:|---|
| 60 · AD nesne ACL/grafik | 78 | 78 | Canlı AD ve gerçek grafik kabulü bu laptopta yok; açık kaldı. AD15 zaten vardı, yeniden yazılmadı. |
| 105 · E-posta analizi | 88 | 91 A | Kapsam 20→23: güven sınırı, sahte doğrulama başlığı, ham EML bütünlüğü, kanıt korelasyonu ve kapsam belirsizliği. |
| 108 · Özet biçimleri | 87 | 92 A | Kapsam 18→23: kaynak/algoritma belirsizliği, politika eşiği ve özeti ifşa etmeyen rapor. |

Diğer puan bileşenleri değiştirilmedi. Eski kayıtlar `puanlar.json/onceki_kabul` içinde korundu. #105/#108 A notları öz değerlendirmedir; bağımsız denetim bekliyor. Panelde `karar=Kısmen` ile `puan<90` farklı kavramlardır (#37 ve #63 90 üzeri olmasına rağmen Kısmen olabilir).

## Çalışma hataları ve kök nedenleri

- **P74:** Native PythonRunner -I ile çalıştığından kullanıcı site-packages/PYTHONPATH görünmüyordu. Projeye kurulmuş .deps artık run/test/trace/dis hazırlığında açıkça ekleniyor. WSL motoru değişmedi. Gerçek BeautifulSoup regresyonu 2 doğru çözüm, 17 yanlış çözüm reddi.
- **BS31:** procps sürümleri zombie comm alanındaki `<defunct>` ekinde farklı. Çözüm Z durumunda eki tam bir kez üretir; sabitlenen anlam korunur.
- **BS33:** WSL varsayılanı root. Sıradan süreç testi artık UID/GID 65534'te ayrı süreç oluşturur; fping eksikti, Kali'ye kuruldu. Namespace beklentisi kernel bounding kümesinden hesaplanır. Host kullanıcısı değiştirilmez.
- **BS35:** Root'un DAC override yeteneği 0555 klasöre yazmayı mümkün kılıyordu; dersin root-sshd alt sürecinde yalnız DAC override/read_search bounding yetenekleri düşürülür. Önceki koşumdan kalan dosyayı yanlış test etmemek için salt-okunur dizine her denemede yeni adla yazılır. Sistem SSH ayarı/servisi değiştirilmez.
- **PS19:** PAFTA_JAVA gibi host ayarları çıktıyı kirletiyordu. Görev yalnız girdide atanan PAFTA_ anahtarlarını raporlar.
- **PS22:** Yeni dosyanın devralınmış DACL'sinde ilk Set-Acl AUTO_INHERITED (AI) kontrol bayrağını ekliyordu. Geçici fixture baseline'ı bir kez normalize edilir; gerçek Deny, okuma reddi, finally geri yükleme, birebir özgün SDDL ve içerik tanıkları korunur. 8 yanlış çözüm reddi.
- **PS24:** Fixture üreticisinin PowerShell alt süreci için process-scope ExecutionPolicy Bypass verilir; makine/kullanıcı ilkesi değiştirilmez. Türkçe kültürde Inventory adını yanlış reddeden ASCII rol adı regex'i `-cnotmatch` ile kültürden bağımsız olur. Native PowerShell modül yolları sürüm 7 üst sürecinden miras alınmaz. 13 yanlış çözüm reddi.
- **PS26:** Türkçe ignore-case regex I/ı dönüşümünde karakter sınıfını yanlış sayıyordu; özel karakter testi `-cmatch` olur. Pester'in doğru çözümü artık geçer.
- **CM23:** Testin SystemRoot'u sahte konuma değiştirmesi CMD/.NET başlangıcını bozuyordu; derlenmiş imzasız EXE bu laptopun App Control ilkesince 4551 ile engelleniyordu. Sorgu aracı için açık PAFTA_WHOAMI override'ı ve CMD test yardımcısı kullanılır; güvenlik ilkesi değiştirilmez. Üç görev hâlâ gerçek whoami CSV'si, eksik araç ve ikinci sorgu hatasını sınar.
- **CM25:** Sigcheck'in Türkçe imza hata mesajı İngilizce sabit metinle karşılaştırılıyordu. Bağımsız gerçek Sigcheck CSV'si BOM'suz UTF-16 dahil çözülür; tam iki bozuk PE adı, gerçek Verified metni, sıra ve toplam korunur. Test başarı için hata mesajını İngilizceye zorlamaz.

## Kanıtlar

- [Purple kabulü](../../outputs/laptop-20261027-purple-acceptance.json): yeni iki görevde doğru çözüm geçer, başlangıç kodu kalır, 20 kasıtlı yanlış çözüm reddedilir; kaynak hash'leri var.
- [Purple mutasyonları](../../outputs/laptop-20261027-purple-mutations.log): 107 mutant; 6 geçen. Beşi ilk görevin maxsplit/domain-normalizasyon eşdeğerleri, biri yeni görevde authserv-id split maxsplit 1→2 (ilk parça aynı). Gerçek kapsam boşluğu olarak gizlenmedi. Boş/sonu noktalı alan hizalama kusuru ayrıca düzeltildi ve sınandı.
- [Purple tahminleri](../../outputs/laptop-20261027-purple-predictions.log): 2 gerçek tahmin, 0 şüpheli.
- [Çalışma kabulü](../../outputs/laptop-20261027-runtime-acceptance.json): ilk başarısız ara koşular dahil tarihçe.
- [Son kabul](../../outputs/laptop-20261027-final-acceptance.json): son Windows/Git Bash hedef taraması, CMD regresyonları, bootstrap ve depo bağlantıları. Ara koşu hataları son kabul sonucu yerine kullanılmamalı.

## Açık kalanlar

#60 için bu laptopun gerçek AD VM/DC konfigürasyonu ve gerçek grafik kabulü gerekir. Paketle gelen masaüstü canlı kanıtı burada tekrar ölçülmüş sayılmadı. AD/Splunk-CIM gibi kurulmamış veya bu teslimde çalıştırılmamış dış motorlara PASS verilmez. AI-Ek değiştirilmedi. Commit/push yapılmadı; kullanıcı ilerlemesi değiştirilmedi.

## Tam yol taramalarının bu laptopta sonucu

| Yol | Ders / kontrol | Sonuç |
|---|---|---|
| Python | 83 / 927 | TEMİZ |
| Bash | 35 / 347 | TEMİZ |
| CMD | 25 / 146 | TEMİZ |
| Purple | 17 / 117 | TEMİZ |
| PowerShell | 29 / 287 | 285 geçti; PS29'un AD VM gerektiren 2 kontrolü engelli. PS19/22/24/26 geçti. |

Bu tablo 108 kalite maddesinin tümünün canlı motorlarda yeniden denetlendiği anlamına gelmez. Test edilmemiş track'ler ve dış lab'lar bu teslimin kabulüne katılmadı.
