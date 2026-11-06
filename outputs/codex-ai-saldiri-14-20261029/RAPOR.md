# ai-saldiri-14 — disk corpus'u ve canlı RAG
Uygulayıcı kabulü; bağımsız denetim değildir.29 Ekim2026.

Değişen: ai-saldiri-14 dersine anlat/gerçek görev index8; sandbox/ai_gercek_ai_saldiri_14.py; web/data/ai-saldiri-14-corpus.txt. Eski adımlar korundu; paket/ortak motor/commit/push yok.

Elle yazılmış sentetik temiz/zehirli corpus görünür, ayrı kalıcı öğrenci JSON kopyası vardır. SQLite belgeler tablosu ve gerçek FTS5 indeksine yazılır, bağlantı kapanıp yeniden açılır. Öğrenci içerik SHA256/kaynak manifestosu üretir; lexical sırası gerçek SQL'den hangi belgelerin yeniden çekilip modele verileceğini belirler. Yerel Qwen'de iki sorgunun temiz/zehirli kollarında dört gerçek çağrı. FTS5 BM25 sırası ayrıca gösterilir; öğrenci token sayımı sıralamasıyla aynı algoritma olduğu iddia edilmez. Embedding/vector DB kullanılmadı.

Model yanıtı sabit metinle karşılaştırılmaz. Retrieval tam-satır canary farkı ve yanıttaki işaret ayrı sinyallerdir; belgenin getirilmesi/işaretin alıntısı/talimata uyma eşit sayılmaz. Saldırı başarısı kabul şartı değildir. Hata/ham mesaj/yanıt/seed/cihaz/bellek/model-digest/DBSHA256 ve manifestolar kanıtta. Çalıştır SQLite dosyasını öğrenci alanında korur; kopya sıfırlanmaz, kullanıcı verisi silinmez. Farklı süreç/dizinlerde kalıcılık persistence.json ile doğrulandı (fixture kontrolü).

Hedef validate1ders/10kontrol TEMİZ. kabul.py/summary.json9/9: referans PASS; starter/boş/sabit + yanlış hash/ters skor/kontrol kollarını birleştirme mutantları FAIL. Test içinde önceki mutantlar ve yeni rastgele sorgu/hash sınamaları var. Çalıştır OK/kabulfalse; eksik Ollama FAIL, kabul yok. Son UI ve grup regresyonu eklenir.

Son UI Kontrol28/28: outputs/codex-kirmizi-seri-20261029/ui-data/ai-kanit/saldiri-14-rag-1793279785999.json. UI Çalıştır saldiri-14-rag-1793279746934.json, bütün kontrollertrue/kabulfalse. İlk UI fetch kesintisi kabul sayılmadı; bağlantı çalışır durumdayken Kontrol yeniden geçirilerek doğrulandı. Son hedef validate10kontrolTEMİZ. Referans bulgu: iki sorguda öğrenci lexical temizde iade/teslimat, zehirli kolda zehir belgesini getirdi; FTS5 aynı iki meşru belgeyi üstte tuttu. Canlı modelde işaret temiz kollarda0/2,zehirli kollarda2/2; bu aktarım sinyalidir ve küçük veri setiyle sınırlıdır.
