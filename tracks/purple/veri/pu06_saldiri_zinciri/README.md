# PU06 sentetik saldırı zinciri fixture'ı

`lab.json` yalnız `pu06-saldiri-zinciri-analizi.md` dersi için üretilmiş,
tamamen sentetik ve çevrimdışı bir veri kümesidir. Gerçek kullanıcı, parola,
hash, Kerberos bileti, ağ paketi, anahtar veya sistem yapılandırması içermez.

## Bölümler

- `linux`: daha önce kaydedilmiş `id`, `getcap`, `sudo -l`, cron ve PATH
  gözlemlerinin normalize edilmiş hâli. Komutlar bu fixture'dan yeniden
  çalıştırılmaz. Riskli capability, wildcard'lı NOPASSWD kuralı, grupça
  yazılabilir cron dosyası ve güvensiz PATH öğeleri için negatif/positif tanık
  içerir.
- `windows`: sentetik token grup SID'leri ve öznitelikleri, üç DACL nesnesi,
  iki JEA oturum özeti. `deny_only` yönetici grubu, etkin kullanıcı grubu,
  kullanıcıya özel deny ACE ve JEA'da tehlikeli komut/tam yol olmayan dış komut
  tanıkları bulunur.
- `ad_events`: UTC zamanlı sentetik 4624/4625/4768/4769/4771/4776 olayları.
  Parola püskürtme, tek hesaba kaba kuvvet, başarısızdan başarılıya geçiş,
  Logon Type 2/3/10 ve ilgisiz normal trafik örneklerini ayırt ettirir.
  Başarılı 4768/4769 kayıtları kimlik doğrulama bağlamıdır; yatay hareket kenarı
  değildir. 4776 için `0x0` başarı, diğer durumlar başarısızlık olarak modellenir.

## Güvenlik ve kullanım

Veri hiçbir gerçek ortamın dökümü değildir; IP'ler RFC 1918 laboratuvar
adresleri, hesap ve makine adları kurgusaldır. Ders yalnız kayıtlı kanıtı
sınıflandırır. Gerçek ayrıcalık yükseltme, parola/hash/ticket elde etme veya
yeniden kullanma, kırma, uzaktan kod/servis çalıştırma ve yapılandırma değiştirme
kapsam dışıdır.

`sandbox/attack_analysis_lab.py` fixture'ı ders koşucusunun geçici klasörüne
`pu06_lab.json` olarak kopyalar. Yazar kontrolleri:

```powershell
python -X utf8 tools/test_attack_analysis_lab.py
python -X utf8 tools/validate.py pu06
```

`track.json` bu çalışma kapsamında değiştirilmez; dolayısıyla `validate pu06`,
PU06 yol sırasına eklenmeden doğrudan dersi doğrulayamaz. Özel test dersi dosya
adından yükleyerek bütün görevleri çalıştırır.
