# 92 · 93 · 95 · 98 · 101 · 104 · 105 · 106 · 108 · Purple/bitirme test sıkılaştırmalarının yeniden ölçülmesi

27 Ekim 2026 · Claude.

Bu maddelerde önceki denetimin tek eksiği test boşluklarıydı (yaşayan mutantlar). Bir önceki Claude oturumu 92, 93, 95, 98, 101 ve 104'ün testlerini sıkılaştırdı (`61c5584`, `eea5e1c`, `81c0c40`) ama panele işleyemeden durdu. Bu teslim onları yeniden ölçer, 105, 106 ve 108'in (PU14, PU15, PU17) yaşayan mutantlarını kapatır (`c7fe5df`, `e6c022a`) ve PU02'de "eşdeğer" sayılmış bir mutantın gerçek boşluk olduğunu gösterip kapatır.

## Ölçüm

- `tools/validate.py` 14 ders, 90 kontrol: PowerShell'de (`c7fe5df`) ve Git Bash'te (`e6c022a`) temiz.
- `docs/denetim/araclar/mutasyon.py --en-cok 400` (örneklemsiz tam küme), `c7fe5df` anlık görüntüsü: **327 mutant, 25 geçen**; PU17 `e6c022a`'da yeniden: 47 mutant, 0 geçen.
- Elle yanlış çözüm: 14 vaka, 14 reddedildi.
- Çıktı: [a-notu-purple-mutasyon.txt](a-notu-purple-mutasyon.txt).

| Madde | Ders | Mutant | Geçen | Geçenler |
|---|---|---|---|---|
| 92 | PU13 | 18 | 0 | — |
| 93 | PU02 | 30 | 4 | gösterim satırı (×2), kapsam fixpoint'i sıra bağımsız olduğu için zaman çizelgesi eşit-zaman sıralaması (@21), manifest girintisi: eşdeğer |
| 95 | PU10 | 44 | 3 | görev 3 çıktısında kullanılmayan `eslesme` alanı (×2): eşdeğer; `set(koruma) <= set("RWX-")` → `<`: yalnız fixture'da olmayan 4 karakterli `-RWX` biçiminde fark eder |
| 98 | PU06, PU07 | 31 | 2 | eksik anahtar varsayılanı (`age_hours` 25→26, `critical` 1→2): eşdeğer |
| 101 | PU12 | 66 | 3 | gösterim satırı: eşdeğer; JEA yol sınırı `len < 3` → `<= 3` / `< 4`: yalnız tam `C:\` sürücü kökünde fark eder, komut değildir |
| 104 | BT05, BT06 | 31 | 2 | JSON girintisi, eksik yaş varsayılanı: eşdeğer |
| 105 | PU14 | 37 | 5 | `rsplit/split` maxsplit 1→2 (×4): eşdeğer; `bool(a and b)` → `bool(a or b)`: yalnız biri boş, öbürü sonu noktalı alanken fark eder |
| 106 | PU15 | 11 | 0 | — |
| 108 | PU17 | 47 | 0 | — |
| 96 | ID01–ID03 | 12 | 6 | hepsi `rev:1→2`: eşdeğer. **ID04/ID05 ölçülmedi** (aşağıda) |

## Bu teslimde kapatılan boşluklar

- **PU14 g1:** alt alan alignment iki yönde (SPF alanı From'un, From DKIM alanının alt alanı); display-name spoofing yalnız görünen adda kurumsal adres varken ve gerçek From kurumsal değilken; kurumsal alt alan (`mail.pafta.test`) kurumsal; `notpafta.test` alt alan değil.
- **PU14 g2:** anchor içindeki `<span>/<b>` kapanışı kaydı erken kapatmaz; yalnız `<a>` kayıt açar, `<link href>` ve sahipsiz `</a>` bağlantı değildir.
- **PU14 g3:** çift uzantı yalnız belge + tehlikeli son uzantı (`kurulum.exe`, `rapor.pdf.txt`, `arsiv.zip.exe` değil).
- **PU15 g3:** Prefetch son çalıştırması = SI Birth çelişki değil; LNK Birth = SI Birth fark değil; LNK Birth > SI Birth yine fark; kopyalanan MFT normalizasyonu SI/FN farklarını korur.
- **PU17 g1:** bcrypt cost 04/20/31, sha512crypt salt 1 ve 16 karakter, boş salt reddi, rounds 1000 ve 999999999 kabulü, 1000000000 reddi.
- **PU17 g2:** aynı sınırlar shadow üzerinden; varsayılan rounds 5000; NTLM salt taşımaz, aynı NT özeti salt tekrarı sayılmaz. Görev metni çözümle uyumlu olacak şekilde netleştirildi: boş ya da kilitli olmayan her parola alanı parser'dan geçer.
- **PU02 g5:** paket içini gösteren sürücüye göreli yol (`C:notlar/olay.txt`) reddedilir. Önceki oturum bu mutantı "Windows yol çözümü, eşdeğer" diye yazmıştı; aynı sürücüde `pathlib` bu yolu paket köküne eklediği için mutant gerçekten geçiyordu.

## Öz değerlendirme

Yalnız test puanı güncellendi; kapsam, derinlik, gerçeklik ve yol puanları önceki denetimdeki gibi kaldı.

| Madde | Önce | Sonra | Not |
|---|---|---|---|
| 92 | 86 | **91 A** | test 19→24 |
| 93 | 84 | **92 A** | test 16→24 |
| 95 | 85 | **91 A** | test 17→23 (sözleşme dışı tek fark) |
| 98 | 88 | **92 A** | test 20→24 |
| 101 | 85 | **91 A** | test 17→23 (sürücü kökü) |
| 104 | 87 | **92 A** | test 19→24 |
| 105 | 80 | **88 B** | test 15→23; kapsam 20 |
| 106 | 87 | **91 A** | test 20→24 |
| 108 | 76 | **87 B** | test 13→24; kapsam 18 |

105 ve 108 B'de kalıyor: önceki denetim kapsamı 20 ve 18 verdi ama bunu eksik olarak adlandırmadı. Bu maddeler ASAMA2'de yok (Kimi'nin İş Rolü maddeleri), karşılaştırılacak "ne gerekir" sütunu da yok. A için hangi öğenin eksik olduğu bağımsız denetimde yazılmalı; panelde düşük öncelikli eksik olarak duruyor.

Hepsi öz değerlendirmedir; bağımsız yeniden denetim yapılmadı. Çıkar çatışması: 105, 106, 108 ve PU02'nin yeni testleri bu teslimde yazıldı.

## Açık kalan

- **96 (ID01–ID05):** ID04 ve ID05 Zeek imajını Docker'da çalıştırır. Docker Desktop kapalıyken çözümün kendisi bile koşmuyor ("Zeek imajı yok"); bu yüzden 96 yeniden puanlanmadı.
- **60 (AD erişim yolu):** eksiği gerçek grafik verisini okuyan görev; test sıkılaştırması değil. Bu teslimde ele alınmadı.
