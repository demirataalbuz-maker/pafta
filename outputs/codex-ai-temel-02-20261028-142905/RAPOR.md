# ai-temel-02 · Gerçek embedding deneyi · Codex kendi kabulü

Takip aracıyla yalnız ai-temel-02 alındı. Mevcut dersin sonuna anlatım ve gerçek görev eklendi. Ortak engine/web/laboratuvar dosyaları değiştirilmedi. Kurulum, indirme, commit ve push yapılmadı.

## Gerçek işlem ve sınır

Kurulu SmolLM2-135M modelinin öğrenilmiş giriş embedding katmanı CPU üzerinde kullanıldı. Bağımsız referans gerçek ağırlık tablosundan index_select ile satır seçti. Ham satırlar ve normalize kosinüs matrisi karşılaştırıldı. Transformer ileri hesabı, bağlamsal son katman temsili veya cümle embedding kabulü iddia edilmez.

## Kanıt

- Referans çözüm: PASS, kaynak=gercek ve kabul=true kanıtı.
- Starter, boş kod, sabit cevap, kosinüs yerine nokta çarpımı, ham yerine birim vektör ve ters satır sırası: tümü FAIL ile reddedildi.
- İç testte altı mutant reddedildi; rastgele metin, Türkçe, sıra, yinelenen kimlik, tür doğrulama ve 16-token sınırı sınandı.
- Çalıştır modu: OK.
- Pafta ders ekranında ayrı test ilerleme kaydıyla Kontrol Et: 19/19 geçti; GERÇEK ÇAĞRI / kabul edildi. Ekran: ai-temel-02-ekran.png.
- AI Temel regresyonu: 18 mevcut ders / 132 kontrol; 18 tahmin, 57 referans çözüm ve 57 starter geçti. Altı yazılmamış ders raporda açık bırakıldı.
- Ham kabul JSON dosyaları ve validate-ai-temel.log bu klasörde. Gerçek deneyler HF_HUB_OFFLINE ve TRANSFORMERS_OFFLINE ile yerel önbellekte çalıştırıldı.

Bağımsız denetim değildir. Ders denetime-hazir yapılır; bitti kararı bağımsız denetçiye bırakılır. Mutantlar temel hata örneklerini sınar; keyfi öğrenci koduna karşı tam güvenlik sınırı iddiası yoktur.