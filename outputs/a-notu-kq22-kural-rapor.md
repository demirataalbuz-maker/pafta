# 37 · KQ22 kural kaynağı ve 50 çalıştırmalık benzetim

27 Ekim 2026 · Claude · Codex'in `64c21d4` teslimi üzerine.

Codex'in teslimi zaman pencerelerini ve entity mapping çıktısını gerçek Kusto'da ölçüyordu; kuralın kendisi (eşik, gruplama, bastırma, entity eşlemesi, ürün sınırları) görevde yoktu ve portal önizlemesi abonelik istediği için açık kaldı. Kullanıcı ücretli hizmet istemedi; Bicep CLI indirmesi otomatik izin denetiminden geçmedi ve atlatılmadı. Bu teslim indirme gerektirmez.

## Eklenen

- **Ders bölümü:** kuralın ARM kaynağı (`Microsoft.SecurityInsights/alertRules`, `kind: Scheduled`), REST 2025-09-01 zorunlu alanları ve Microsoft Learn'deki sınırlar: 5 dk–14 gün, sıklık ≤ geriye bakış (tahmin adımındaki 30/15 ayarını Sentinel kaydetmez), 5 dakikalık çalıştırma gecikmesi, eşik her çalıştırmaya ayrı, 150 alarm (149 tekil + 1 özet), bastırma ≤ 24 saat ve kuralı tamamen durdurur, 10 eşleme/3 identifier, 500 entity/64 KB, yerleşik hesap adlarının entity'den düşmesi, Microsoft'un ingestion delay deseni.
- **Görev:** öğrenci doğrulamadan geçmeyen bir Export şablonunu düzeltip parola denemesi kuralını yazar. Koşucu şablonu denetler, sorguyu gerçek Kusto Emulator'da son 50 planlı çalıştırmada koşturur. Test: alarm/bastırma dizisi, her alarmın entity'leri, 8 dk geç gelen kaydın hiçbir pencereye girmemesi, 5 dk gecikme payının kurtardığı kayıt, bastırmanın ikinci saldırıyı gizlemesi, `admin` Account entity'sinin düşmesi, iki ek veri senaryosu.
- **Koşucu:** [sandbox/sentinel_kural_lab.py](../sandbox/sentinel_kural_lab.py), `motor: sentinel-kural` ([engine/runners.py](../engine/runners.py)).

## Kabul

- `tools/test_sentinel_kural.py`: **29 davranış bozan mutant reddedildi, 0 geçen**. Üç eşdeğer ayrı raporlandı: `GreaterThan 0`↔`NotEqual 0` (sonuç sayısı negatif olamaz), `max`↔`min(TimeGenerated)` (benzetim alarm zamanını bu sütundan almaz), `$schema` yılı (laboratuvar şablon şema adresini doğrulamaz). Sınır uçları ayrıca sınandı: PT4M/P14D/P14DT1M, PT24H/PT24H1M, eşik 10000/10001/bool, 10000/10001 karakter, 11 eşleme, 4 identifier.
- Denetçi mutasyon aracı (`docs/denetim/araclar/mutasyon.py . kq22`): yeni görevde 6 mutant, 5 yakalandı; geçen tek mutant `$schema` yılı (eşdeğer). İlk koşuda `apiVersion` 2025→2026 geçiyordu; koşucuya yayımlanmış sürüm listesi eklendi, şimdi reddediliyor.
- `tools/validate.py --yol kql`: Git Bash ve PowerShell, **24 ders, 251 kontrol TEMİZ**. `tools/test_kusto_native.py` temiz.
- Kanıt: [a-notu-kq22-kural-kabul.json](a-notu-kq22-kural-kabul.json).

## Açık kalan

Gerçek Sentinel çalışma alanı yok. Portalın **Test with current data** ve **Review and create** doğrulaması yapılmadı. Takvim, eşik, gruplama, bastırma ve entity çıkarımı belgelere göre yazılmış yerel modeldir; Microsoft pencere uçlarının açık/kapalı olduğunu yazmıyor. Bu kısım yapılmış sayılmaz.

## Öz değerlendirme

**91/100 (A)**: test 24, kapsam 23, derinlik 23, gerçeklik 12, yol 9. Bağımsız denetim değildir; yazar benim, çıkar çatışması var. Gerçeklik 12'de kaldı, çünkü sorgu motoru gerçek ama kural servisi gerçek değil.

Kaynaklar:
- https://learn.microsoft.com/en-us/azure/sentinel/scheduled-rules-overview
- https://learn.microsoft.com/en-us/azure/sentinel/create-analytics-rules
- https://learn.microsoft.com/en-us/azure/sentinel/ingestion-delay
- https://learn.microsoft.com/en-us/azure/sentinel/map-data-fields-to-entities
- https://learn.microsoft.com/en-us/azure/sentinel/entities-reference
- https://learn.microsoft.com/en-us/rest/api/securityinsights/alert-rules/create-or-update?view=rest-securityinsights-2025-09-01
