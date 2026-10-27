# 39 · SP23 Authentication ve Endpoint.Processes gerçek CIM modelinde

27 Ekim 2026 · Codex taslağı, Claude tamamladı.

Ders yalnız Web modelini kullanıyordu; ASAMA2 Authentication/Endpoint verisi istiyor. Codex iki görev ve CIM kurulum denetleyicisini yazıp commit etmeden bırakmıştı. Endpoint testinde `\n` kaçışı üretilen kodu bozuyordu (çözüm geçmiyordu), görevde istenen `pid AS process_id` eşlemesi de sınanmıyordu. İkisi düzeltildi.

## İçerik

- **Authentication:** FIELDALIAS (`hesap/kaynak/hedef/uygulama` → `user/src/dest/app`), `EVAL-action` ile `ok/fail` → `success/failure`, bilinmeyen `unknown`; eventtype `tur=auth`, `authentication` etiketi. Kurulu Splunk_SA_CIM 8.5.0'ın kök kısıtı başarılı makine hesabını (`user=*$`) dışarıda bırakır, başarısızını bırakmaz; görev bunu gerçek modelde gösterir. Etiketsiz bir sourcetype'ın aynı alias/EVAL'le modele giremediği ayrıca sınanır.
- **Endpoint.Processes:** model `tag=process tag=report` ister; tek etiket yetmez. Çocuk/ebeveyn süreç alanları, `process_id`, olay türü süzgeci.
- **Kurulum:** `tools/splunk_cim_kur.py` yerel CIM 8.5.0 arşivinin SHA256'sını ve kurulu/etkin sürümü denetler; `--install` yalnız mevcut arşivi Pafta Splunk konteynerine kurar, internetten indirmez. Splunkbase hesabı/koşulları betikle atlanmaz.

## Kabul

- `tools/test_splunk_cim_models.py`: gerçek Splunk Enterprise 10.6.1 + CIM 8.5.0'da **14 davranış bozan mutant reddedildi, 0 geçen** (8 Authentication, 6 Endpoint): yanlış etiket, eksik olay türü süzgeci, normalize edilmemiş/ters/varsayılanı bozuk `action`, eksik alias, hesap adının küçük harfe çevrilmesi, eksik `report`/`process` etiketi, çocuk/ebeveyn ters, eksik `process_id`/`user`.
- `tools/validate.py sp23`: Git Bash ve PowerShell temiz (10 kontrol).
- `python tools/splunk_cim_kur.py`: arşiv SHA256 doğrulandı, CIM 8.5.0 kurulu/etkin, değişiklik yapılmadı.
- Kanıt: [a-notu-sp23-cim-kabul.json](a-notu-sp23-cim-kabul.json).

## Açık kalan

CIM paketi yeni bilgisayarda Splunkbase hesabıyla elle edinilir (lisans koşulları otomatik kabul edilmez). Sonuçlar bu CIM sürümüne bağlıdır; başka sürüme genellenmez.

## Öz değerlendirme

**94/100 (A)**: test 24, kapsam 23, derinlik 23, gerçeklik 15, yol 9. Bağımsız denetim değildir.
