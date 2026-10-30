# PU14 sentetik e-posta kanıtları

`oltalama.eml` ve `kurumsal.eml`, RFC 5322/MIME yapısını taşıyan küçük ve tamamen kurgusal iletilerdir. `.example` alan adları ile RFC 5737 belge IP'leri kullanılır. `pafta.test` de kurgusal laboratuvar alanıdır. İletiler gerçek bir sağlayıcıdan alınmamıştır; SPF/DKIM/DMARC satırları analiz alıştırması için elle yazılmıştır ve imza doğrulaması yapıldığı anlamına gelmez.

Eklerin içeriği zararsız sentetik baytlardır. `Fatura_1042.pdf.exe` adı ve `MZ` öneki yalnız sınıflandırma kanıtıdır; çalıştırılabilir bir program teslim etme amacı yoktur. Hiçbir ek açılmamalı veya çalıştırılmamalıdır.

Laboratuvar yalnız standart `email` parser ile yerel baytları okur. DNS sorgusu, URL ziyareti, HTTP isteği, dış kapsayıcı/whois kullanımı, ağ bağlantısı ve paket kurulumu kapsam dışıdır. Bağlantılar rapora yazılırken defang uygulanır.
