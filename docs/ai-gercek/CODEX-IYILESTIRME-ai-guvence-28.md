# ai-guvence-28 iyileştirme teslimi

Düzelten codex; claude-opus denetimi bekleniyor. Puan verilmedi.

Değişenler: ders markdown, tracks/ai-guvence/fixtures/ai-guvence-28/{README.md,veri/model_kayitlari.json,veri/secim_esikleri.json}, sandbox/ai_gercek_ai_guvence_28.py (yalnız kanıt model başlığının metin türü; model listesi yeni ortam.modeller alanında ve bütün oturum ayrıntılarında korunur). Ortak arayüz listeyi esc() ile çizip hata veriyordu; derse ait kanıt başlığı sözleşmeye uyarlandı. Çağrı, puanlama, izin kapısı ve kaynak temizliği davranışı değişmedi. engine/web değiştirilmedi.

Tablo+NOT, geçici/kalıcı veri ayrımı, görünür dosyaları okuyan üç görev, üç kusurlu çalışan başlangıç, 491 kelime ek anlatım, giriş çelişkisi ve ekranda dört aşamalı belirgin opt-in açıklaması eklendi. İlk görevlerin uzak kullanım acik_onay alanıyla son gerçek görevin yerel opt_in alanı açıkça ayrıldı. Varsayılan web/data/ai-guvence-28-deney.txt opt_in=false kaldı. Yalnız yeni izole test verisinde açık onay kullanıldı; kendi UI test ayarı yedeklenip test sonrası özgün false hâline geri kondu.

Gerçek test plan_ref/score_ref/summary_ref/kanit_yaz için kod_denetimi + ImportFrom takma ad/yıldız kontrolünü kullanır. Kanıt yalnız kabul=all(kontroller.values()).

## Dört kontrol

- validate.py ai-guvence-28: TEMİZ, 9 kontrol (1 tahmin, 4 çözüm, 4 başlangıç). PAFTA_DATA=Desktop/pafta-iyilestirme-28-kanit, açık test opt-in, kurulu Qwen4B ve Qwen8B, koşu başına 8 gerçek yerel çağrı. Kanıt başlığı düzeltmesinden sonra yeniden TEMİZ.
- tahmin.py . ai-guvence-28: 1 tahmin, 0 şüpheli.
- kirp_gercek.py Desktop/pafta-mutasyon-g28-20261030-0920; mutasyon.py <kopya> --en-cok 1000 ai-guvence-28: 22+35+51=108 mutant, 0 geçen. Son değişiklik yalnız gerçek deneyin kanıt metadatasıydı; sentetik görevler aynı.
- kopya_sonda.py ai-guvence ai-guvence-28 "from sandbox.ai_gercek_ai_guvence_28 import plan_ref as karsilastirma_plani, score_ref as karsilastirma_skoru, summary_ref as karsilastirma_ozeti": fail, korunuyor. outputs/iyilestirme-codex-ai-guvence-28/kopya-sonucu.json; model çağrısından önce hedeflenen guard mesajı ve kanıt yokluğu ayrıca doğrulandı.

## Başarısız koşu ve gerçek sonuç

İlk kabul koşusu HTTP 500 ile başarısız oldu ve PASS sayılmadı: Desktop/pafta-iyilestirme-28-kanit/ai-kanit/guvence-28-1793339010399.json. Aynı ayarla yeniden sınama geçti; kök neden çözülmüş veya istikrar kanıtlanmış sayılmaz. Son metadata sonrası geçerli CLI kanıtı guvence-28-1793339396703.json: 8 çağrı, iki modelde kalite/güvenlik 1.0; bu iki aritmetik görev ve canary ölçütüyle sınırlıdır, genel üstünlük iddiası yok.

## Ders ekranı

Kendi 18800 test sunucusunda görev 1 Çalıştır dört görünür JSON kaydını okudu/yazdırdı. Kapalı opt-in Çalıştır model çağrısı olmadan EKSIK/PASS DEGIL verdi; kanıt guvence-28-1793339121654.json. Ortak kanıt bileşeni eksik kaydı FIXTURE diye etiketliyor; eksik/PASS değil hata metni açık, bu ortak renderer sınırlaması değiştirilmedi.

İlk açık UI koşusunda model başlığı liste olduğu için konsolda esc(s.replace) hatası alındı; bu ekran kabulü tamamlanmış sayılmadı. Metadata düzeltmesinden sonra temiz sekmede gerçek görev 9 Kontrol 3/3 geçti, GERÇEK ÇAĞRI/kabul edildi: outputs/codex-guvence-bos-20261029/ui-data/ai-kanit/guvence-28-1793339455514.json. Kaynak temizliği ve cihaz ölçümü geçti. Yeni ilk üç görevin tümü ayrı UI kabulü yapılmadı; CLI validate hepsini sınadı. Kullanıcının Ollama sunucusu kapatılmadı; yeni indirme/kurulum/commit/push yok.
