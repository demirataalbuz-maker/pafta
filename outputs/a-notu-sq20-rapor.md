# 34 · PostgreSQL JSONB görevleri

27 Ekim 2026 · Codex

SQ20'nin SQLite görevleri korundu; sonuna mevcut Kali WSL kümesinde gerçek PostgreSQL jsonb ile çalışan iki yazma görevi eklendi. Eski “burada çalışmaz” ifadesi yeni native görevleri gösterecek biçimde düzeltildi. Ek paket veya servis kurulmadı.

İlk görev SQL NULL, JSON null, kök nesne/dizi/skaler türü, üst düzey anahtar yokluğu ve boş metin/false/0/nesne/dizi değerini ayrı sınıflandırır. ? operatörünün dizi metni veya skaler metinde de true olabilmesi nedeniyle kök nesne guard'ı test edilir; iç içe başka anahtar ve harf farkı yanlış varlık sayılmaz.

İkinci görev @> ile yapısal olay türü filtresi, LATERAL jsonb_array_elements_text ve WITH ORDINALITY kullanır. Eksik/null/skaler/nesne etiketler fonksiyondan önce CASE ile boş diziye dönüştürülür. Tekrarlı etiketler ve 1 tabanlı özgün konum korunur; büyük harf, ilgisiz tür, iç içe alan ve dizi olmayan kontroller sonucu genişletmez. Süzme sonrası yeniden numaralandırma kabul edilmez.

Kabul: SQ20 **15 kontrol TEMİZ**, tools/test_sql_jsonb.py: **2 referans geçti, 15 yanlış çözüm reddedildi, 0 geçen**. Bazı mutantlar gerçek SQL hata çıktısıyla reddedilir; bunlar bağlantı/yokluk hatası olarak sayılmaz. Yeni görevlerle tam SQL yolu Windows/Git Bash doğrulaması teslimde saklanacak.

Öz değerlendirme: test24/kapsam24/derinlik22/gerçeklik15/yol10 = **95/A**. Önceki bağımsız80 korunmalı; bağımsız yeniden denetim beklenir. Ortak panel dosyasına başka ajanın değişiklikleri nedeniyle dokunulmadı; öneri ayrı dosyadadır.

Kaynaklar kontrol edildi: https://www.postgresql.org/docs/18/functions-json.html ve https://www.postgresql.org/docs/18/datatype-json.html#JSON-CONTAINMENT .
