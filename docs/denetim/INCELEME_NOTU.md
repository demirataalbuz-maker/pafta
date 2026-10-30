# İnceleme notu (30.10.2026)

Purple tarafını inceleyenler için: puan paneli `docs/denetim/DENETIM_SAYFASI.html`, ham puanlar `docs/denetim/puanlar.json`.
108 maddenin hepsi A aralığında (≥ 90). Aşağıdakiler kesinleşmiş sayılmamalı:

| Madde | Durum |
|---|---|
| 105 · Oltalama e-postası (PU14) | Claude bağımsız denetimi 90. Sonra Claude 5. görevi ekledi (QR kanalı sinyali, kampanya karantinası). Bu ek henüz başka bir denetçi tarafından puanlanmadı. |
| 108 · Parola özeti biçimleri (PU17) | Claude bağımsız denetimi 90. Açık kapsam notu `puanlar.json` içinde. |
| 37 · Sentinel kuralı | Kısmen: gerçek Azure portal kabulü yapılmadı. |
| 60 · AD ACL erişim yolu | Kısmen: kanıt Samba AD DC üzerinde; Windows AccessCheck değil, derse entegre değil. |
| 63 · LDAP TLS / channel binding | Puan 26.10 gerçek DC denetiminden. Sonraki yol düzeltmesi testlerle geçti; kararın Tam'a dönmesi için yeniden denetim gerekir. |

Bilinen ortam sorunu: `pu02` bu makinede validate sırasında 6 saniyelik süre sınırını aşıyor (son commit'in temiz kopyasında da aynı); ders içeriği değil, çalışma süresi sorunu olabilir.

AD derslerinin canlı kontrolleri için `tools/setup_ad_vm.py` ile AD laboratuvarı kurulmalıdır; kurulu değilse AD22/AD23 gibi dersler "laboratuvar kurulmamış" hatası verir.
