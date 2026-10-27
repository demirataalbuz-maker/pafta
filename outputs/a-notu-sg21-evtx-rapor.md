# 47 · SG21 Windows'un EVTX/XML'inden Sigma'ya ve gerçek Splunk'a

27 Ekim 2026 · Claude.

Bağımsız denetimin eksikleri: **gerçek EVTX/XML yok, olaylar sentetik JSON** (yüksek) ve **PS21/PS27'deki olay okuma bilgisine köprü yok** (orta). Projede `ps_evtx_fixtures.py` vardı ama Sigma'da kullanılmıyordu.

## Eklenen

- **Kaynak:** [sandbox/sigma_evtx_lab.py](../sandbox/sigma_evtx_lab.py). Altı 4688 kaydı EVT olarak yazılır, Windows'un `wevtutil epl` aracıyla gerçek EVTX'e çevrilir, `wevtutil qe /f:xml` ile Windows'un işlediği XML alınır. Canlı günlük okunmaz.
- **Ders bölümü:** EVT kaynaklı kayıtta `Data` adsızdır (PS27'deki `Properties[n]`). Microsoft 4688 belgesindeki 15 alanlık sıra, boş `CommandLine`'ın denetim ilkesiyle ilişkisi ve kaymaya yol açması, XML kaçışı, `windows-audit` + `splunk_windows` sözleşmesi (`EventCode`, `WinEventLog:Security`) ve `EventID` adı kalırsa kuralın sessiz kalması.
- **Görev 3:** öğrenci `normalle(xml)` yazar. Test 11 kontrol yapar, sonra çıktıyı gerçek Splunk'a yükleyip kuralı gerçek pySigma Splunk backend'iyle çalıştırır: ayse ve zeynep (büyük harfli yol) eşleşir. Mert'in boş komut satırı kör nokta olarak kalır, can'ın üst süreci Explorer'dır.
- **Koşucu:** Sigma yolunda `motor: python` (PythonRunner).

## Kabul

- `tools/test_sigma_evtx.py`: **8 davranış bozan normalleştirici reddedildi, 0 geçen** (boş alan atlama ya da `None`, `EventID` adı, metin `EventCode`, zamanın yanlış yerden alınması, bir kayık alan sırası, ters olay sırası, eksik `Computer`).
- `docs/denetim/araclar/mutasyon.py . sg21`: 5 mutant, 0 geçen.
- `tools/validate.py sg21`: Git Bash ve PowerShell temiz.
- Kanıt: [a-notu-sg21-evtx-kabul.json](a-notu-sg21-evtx-kabul.json).

## Açık kalan

Kayıtlar sentetik içerikli; EVTX ve XML'i Windows üretir. EVT kaynaklı olduğu için olay sürümü 0'dır ve modern `Data Name=...` biçimi bu görevde sınanmaz. Gerçek Sysmon kurulmadı.

## Öz değerlendirme

**90/100 (A)**: test 23, kapsam 22, derinlik 22, gerçeklik 14, yol 9. Sınırda bir A; bağımsız denetim değildir.
