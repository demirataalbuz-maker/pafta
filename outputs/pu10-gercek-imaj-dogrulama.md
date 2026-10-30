# PU10 · Gerçek Windows bellek imajı doğrulaması

Tarih: 2026-10-26
Dal tabanı: `b14ccc0`
Sonuç: **geçti** — mevcut `sandbox/memory_lab.py` Volatility 3 opt-in yolu değiştirilmeden çalıştı.

## Kaynak ve geri dönüş

- Kaynak: Pafta AD laboratuvarındaki **PF-DC01**, VMware Workstation, 3 GiB RAM.
- Yöntem: `vmrun suspend ... soft`; oluşan `.vmss` ve `.vmem` dosyalarını repo dışındaki kanıt klasörüne kopyalama; ardından aynı VM'yi `start ... nogui` ile sürdürme.
- Son kontrol: PF-DC01 ve PF-APP01 çalışıyor; PF-DC01 konuk IP'si `192.168.247.10` `getGuestIPAddress -wait` ile doğrulandı.
- İmaj ve dışa aktarımlar `%LOCALAPPDATA%\Pafta\evidence\pu10\PF-DC01-20261026-1358` altında kaldı; **3 GiB imaj repoya alınmadı**.
- Bellek içeriği, süreç listesi, kimlik bilgisi veya bellek baytları bu rapora yazılmadı.

## Araç ve imaj kimliği

- Volatility 3 Framework: **2.28.2**; repo dışında `%LOCALAPPDATA%\Pafta\tools\volatility3-2.28.2`.
- `windows.info`: **15.26100**, x64, 2 CPU, `NtProductLanManNt`.
- Çekirdek sembolü: `ntkrnlmp.pdb/B65A1E5D9D57D828E82F8C75F19E9857-1.json.xz`.
- İmaj `SystemTime`: `2026-10-26 11:25:45+00:00`.

| Dosya | Boyut | SHA-256 |
|---|---:|---|
| `PF-DC01-9522e1f6.vmem` | 3.221.225.472 bayt | `2752441468dfc98a3993aaeceda99a229b54d1b53bcae6f0ea2cc9d5f4cc6574` |
| `PF-DC01-9522e1f6.vmss` | 1.323.985 bayt | `0311f3197b29c7edc480c044945f120e0c85008954e9a1b12b45402a3128c08f` |

## Opt-in bağdaştırıcı sonucu

`volatility_topla(..., onay=True)` sonucu `durum=tamam`, `calisti=true`; üç eklenti de geçerli JSON üretti ve mevcut `satirlari_oku` ayrıştırıcısıyla açıldı.

| Eklenti | Satır | JSON SHA-256 |
|---|---:|---|
| `windows.pslist.PsList` | 54 | `5dd8f37b67cb078ad1a3240e7c534e86cddf8bc242e61950e7e112dca2308819` |
| `windows.netscan.NetScan` | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` |
| `windows.malfind.Malfind` | 18 | `392d720ff48db658296749ca9c00cbcb09b5a4bccf1fc63ec36275e3b6ec5caa` |

NetScan'in bu askı anında sıfır kayıt üretmesi araç/ayrıştırıcı hatası olarak sunulmadı; boş sonuç da geçerli JSON'dur. PsList gerçek süreç kanıtı, Malfind ise gerçek aday kayıtları sağladı. Adaylar zararlı hükmü değildir.

## Tekrarlanabilir kabul

Yeni `tools/test_memory_live_pu10.py` varsayılan olarak açıkça atlanır; `PAFTA_MEMORY_LIVE=1`, `PAFTA_VOLATILITY` ve `PAFTA_MEMORY_IMAGE` verilmeden gerçek araç çalıştırmaz.

- İlk canlı test **1/1 geçti** (50,437 saniye); bağımsız tekrar da **1/1 geçti** (54,771 saniye). Üç JSON'un satır sayıları ve özetleri iki çalışmada da yukarıdaki değerlerle aynı.
- Küçük denetim kayıtları: `outputs/pu10-windows-info.txt`, `outputs/pu10-live-test.txt` (54,771 saniyelik tekrar) ve `outputs/pu10-vm-restore.txt`.
- Mevcut sentetik `tools/test_memory_lab.py`: **12/12 geçti**.
- Yeni canlı testin varsayılan çalışması: **1 açık opt-in skip**; araç veya imaj aranmadı.
- PU10 dersi ve `sandbox/memory_lab.py` değiştirilmedi; bağdaştırıcı düzeltmesi gerekmedi.
