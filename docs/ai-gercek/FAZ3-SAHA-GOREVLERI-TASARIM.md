# Faz 3 · Belirsiz Saha Görevleri — Tasarım Önerisi

Hazırlayan: antigravity · 29 Ekim 2026 · Durum: **kullanıcı onayı bekleniyor** (onay gelmeden ders yazılmayacak)

## Amaç
Her AI yolunun sonuna adım adım tarif içermeyen bir bitirme görevi eklemek. Öğrenciye kasıtlı olarak zayıf bırakılmış, **yalnızca yerelde çalışan** bir eğitim uygulaması verilir. Öğrenci zayıflığı kendisi bulur, sentetik canary ile kanıtlar ve düzeltir. Kabul yine otomatik yapılır ve gerçek çıktıya dayanır; tek bir doğru kod yolu beklenmez.

## Ortak yapı
| Bölüm | İçerik |
|---|---|
| Hedef | `sandbox/saha_<yol>.py`: yerel, ağa kapalı, sentetik veriyle çalışan küçük bir AI uygulaması (Ollama + Python) |
| Öğrenciye verilen | Uygulamanın kısa tanımı, kapsam/izin notu ve "en az N bulgu" hedefi; zayıflıkların listesi **verilmez** |
| Öğrencinin teslimi | (1) `bulgular()` → yapılandırılmış bulgu listesi, (2) `yama()` → düzeltilmiş yapılandırma/kapı işlevi |
| Otomatik kabul | (a) Her bulgu, gizli zayıflık kimliklerinden biriyle eşleşmeli ve sentetik canary ile yeniden üretilebilmeli; (b) yama sonrası aynı sınamalar canary sızdırmamalı; (c) gizli bir normal iş akışı testi yine çalışmalı (aşırı engelleme olmamalı) |
| Halüsinasyon ölçümü | Kanıtsız ya da var olmayan bulgular yanlış pozitif sayılır; oranı kanıta yazılır, belirli bir eşiği aşarsa kabul verilmez |

## Yol bazında öneriler
| Yol | Uygulama | Gizli zayıflıklar (örnek) | Konum |
|---|---|---|---|
| `ai-saldiri` | Belge özetleyen ve not alan yerel asistan | dolaylı talimat taşıyan belge, onaysız kalıcı bellek yazımı, araç yetkisinin fazla geniş olması | Son modülün sonu, `ai-saldiri-37`'den sonra |
| `ai-savunma` | Aynı asistanın "korunduğu iddia edilen" sürümü | tek dilli filtre, `<think>` soyulmaması, imzasız ajan mesajı | Son modülün sonu |
| `ai-guvence` | Küçük sınıflandırıcı + değerlendirme hattı | değerlendirme verisinin eğitim verisine karışması, eşik kayması, tekrarlanamayan ölçüm | Son modülün sonu |
| `ai-temel` | RAG destekli yerel soru-cevap uygulaması | kaynak gösterilmeyen yanıt, yetkisiz belge erişimi, kayıt eksikliği | Son modülün sonu |

## Sınırlar
- Hedef yalnızca Pafta'nın kendi yerel sandbox uygulamasıdır; dış ağa istek yoktur.
- Başarı sinyali yalnızca sentetik canary değerleridir; gerçek zararlı içerik üretilmez.
- Kurulum, indirme yapılmaz; mevcut `ai_lab.SohbetOturumu` kullanılır. Ortak dosyalara (`engine/`, `web/`, `sandbox/ai_gercek_lab.py`) dokunulmaz.
- Gizli zayıflık listesi test tarafında tutulur; ders metninde yer almaz.

## Onay beklenen kararlar
1. Dört yolun hepsine mi, yoksa önce yalnız `ai-saldiri`'ye mi pilot olarak eklenmeli?
2. Halüsinasyon (yanlış pozitif) oranı için kabul eşiği ne olmalı? (Öneri: en çok %25.)
3. Öğrenciye zayıflık **sayısı** söylenmeli mi? (Öneri: "en az 2" denmeli, toplamı söylenmemeli.)
