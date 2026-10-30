# ai-savunma-31 iyileştirme teslimi

Düzelten codex; claude-opus denetimi bekleniyor. Eski tracker Claude orijinal geliştirmesini gösterir; yeni iyileştirme emri Codex tarafından alındı, eski sahiplik değiştirilmedi. Puan verilmedi.

Değişenler: ders markdown, tracks/ai-savunma/fixtures/ai-savunma-31/{README.md,veri/istekler.json,veri/kullanim.json,veri/butce.json}, sandbox/ai_gercek_ai_savunma_31.py (yalnız kanıta ham yanıt, seed ve sıcaklık eklendi). İstekler ve gerçek kabul mantığı aynı. Ortak engine/web veya veri yardımcı modülü değiştirilmedi.

İlk tablo+NOT, geçici veri/örnek fiyat ayrımı, mevcut ai_savunma_veri.hazirla/setup ile dosya okuyan üç görev, kusurlu çalışan başlangıçlar ve 486 kelime ek anlatım eklendi. Kova jetonu/LLM tokenı, simülasyon/dağıtık kota, çıkış tavanı/servis çapı tüketim savunması ayrıldı. Eski ayrı dosya yok açıklaması düzeltildi; genel tüketim tamamen durdu iddiası tek çağrı çıkış tavanına daraltıldı. Gerçek test ImportFrom takma ad/yıldız ve kanit_yaz korumasıyla güçlendirildi; kanıt mevcut kabul=all(sonuclar) kuralında kaldı.

## Mutasyon bulguları ve düzeltme

İlk güçlendirme sonrası 67 mutantta 9 geçen bulundu. Anlamlı açıklar: iç kaydın iki öğeli tuple olması ve 6 yerine 7 basamak yuvarlama yakalanmıyordu. Bu vakalar eklendi. Diğer geçenler yalnız ValueError mesajındaki sayıyı değiştiriyordu; sözleşme/test zayıflatılmadan hata metnindeki sayılar anlamı koruyan yazıya çevrildi. Ayrıca 1000/1001 uzunluk, bir token bütçe, sıfır fiyat, kesirli dolum ve ayrı token türleri sınandı. İlk başarısız mutasyon kopyası Desktop/pafta-mutasyon-s31-20261030-1020 olarak korundu.

## Dört son kontrol

Komutlar .ai-venv/Scripts/python.exe -X utf8 ile: validate.py ai-savunma-31 TEMİZ, 9 kontrol (1 tahmin, 4 çözüm, 4 başlangıç), iki gerçek model çağrısı dahil; tahmin.py . ai-savunma-31 1 tahmin, 0 şüpheli; kirp_gercek.py Desktop/pafta-mutasyon-s31-20261030-v2, mutasyon.py <kopya> --en-cok 1000 ai-savunma-31 26+22+13=61 mutant, 0 geçen. Son hâlde dört kontrol yeniden koşuldu.

Kopya sondası yalnız doğrulamasız referans aliası değildir: geçerli öğrenci çözümünün girdi doğrulaması korunup hesabı referans_butce as yardimci ile yapan sarmalayıcı verildi. kopya_sonda.py ai-savunma ai-savunma-31 <kod> fail, korunuyor; hedeflenen ImportFrom guard mesajı ve kanıt yokluğu ayrıca doğrulandı. Kod/log/tam sonuç: outputs/iyilestirme-codex-ai-savunma-31/{kopya-kodu.py,kopya-sonda.log,kopya-sonucu.json}. PAFTA_DATA=Desktop/pafta-iyilestirme-s31-kanit ve -s31-kopya.

## Ders ekranı

Kendi 18800 sunucusunda görev 1 Çalıştır görünür istek dosyasını okudu; gerçek görev 9 Kontrol 9/9 geçti, GERÇEK ÇAĞRI/kabul edildi. Qwen4B gerçek tüketimi 512→32 token, bütçeli done_reason=length. Sentetik çıkış maliyeti 0.0768→0.0048; ücret ödenmedi. Kanıt outputs/codex-guvence-bos-20261029/ui-data/ai-kanit/savunma-butce-1793340762610.json; iki ham yanıt ve seed=5/sıcaklık=0.1 bulunduğu ayrıca doğrulandı. İlk üç görevin tümü ayrı UI kabulü yapılmadı; CLI validate hepsini sınadı. Yeni indirme/kurulum/commit/push yok; A notunu denetçi verir.
