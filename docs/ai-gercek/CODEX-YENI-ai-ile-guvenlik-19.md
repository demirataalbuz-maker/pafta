# SOC–Purple köprüsü — ai-ile-guvenlik-19

2026-11-04. Kullanıcının yazılmamış AI derslerini Codex yazsın kararıyla plan-ai-purple-kopru alındı; diğer yazarın aktif başlangıç kaydı yoktu. Dosyalar yeni ve ayrı; mevcut12'nin üzerine yazılmadı. Yeni ders12'den sonra eklendi. Puan yok, Opus denetimi bekliyor.

## Gerçek sonuç
Ders ekranında76/76 kabul; starter ret. Görünür soc/olaylar.json aynı çalıştırmada değiştirildi/okundu. UI Run da gerçek Ollama ve SQLite çalıştırdı; kabul=false kaldı. Dört model çağrısı2seed×kontrol/saldırı; her çağrıda üç olay. Baseline ve protected alarm defteri gerçek commit/close/reopen/SELECT ile ölçülür. Ayrı bilinen yanlış karar fault_probe açıkça sentetik, model yanıtı diye sunulmuyor. Üç veritabanı×dört çağrı=12dosya. Son UI saldırı pay/payda: {'pay': 2, 'payda': 4}; korumalı bastırma0. Saldırının başarılı olması test şartı değildir. Bu SQLite alarm prototipi; gerçek SIEM veya SSH saldırısı değil.

## Kontroller
python -X utf8 tools/validate.py ai-ile-guvenlik-19:1ders9kontrol TEMİZ(4solution,4starter,1tahmin). Son ek kimlik sınırlarıyla yeniden geçti. tahmin.py . ai-ile-guvenlik-19:1tahmin0şüpheli. Resmî mutantlar üreteci üç saf görevde35mutasyon; ilk tur4geçen çıktı, boş/nonstringkimlik ve boşids sınamaları eklendi, son tur35FAIL0PASS0timeout. Referans fonksiyonları değişmedi. Gerçek finalde boş/sabit,3anlamlı yanlış,4oraclekopya,modül yamasıRET. EksikOllama sunucusu ve olmayanexeRET,kabultrueyok. Hedefli eski11/12/18 derslerinin 9saf kontrolü PASS; bütün müfredat ağır model deneyleri yeniden koşulmadı. Windows sandbox temp izni nedeniyle başlamayan tahmin denemesi izinli ortamda tekrar koşuldu; ilk hata PASS sayılmadı.

## Öğretim ve veriler
İlkaraçtablosu,NOT,450+kelime anlatım,3kusurlu başlangıç,tahmin→çıktı→fark,hata vitrini,eşleme,kanıtı yorumlama,sınır var. Sentetik kaynakJSON ile canlı modelhamyanıtı ayrıdır. Öğrenci kopyası geçicidir; kalıcılık iddiası yok. Gerçekmedia/DBler PAFTA_DATA/ai-kanit-media altında korunur. Tam girdiler/sistem istemi/hamyanıt/seed/modeldigest/sürüm/bellek/cihaz/temizlik receipt'te. Ağ ve parsehataları başarısızdeneydir; partialkayıtlarında rawinput/rawanswer saklanır. Düşük olayda gerçek model önerisi korunur; her şeyi alarma çeviren yanlış çözüm reddedilir. Host high kuralı alan saldırısıyla değiştirilemez. StrictJSON duplicatekeys/ekid/eksikid/enumbozulması ret.

## Dosyalar, kurulum ve kalanlar
Kaynak dosyaları/SHA256 ve kanıt yolları outputs/yeni-ai-ile-guvenlik-19/teslim.json içinde. Yeni dersMD,sandboxmodülü,fixtureJSON/README,track'e birID; ortakengine/web değişmedi. Plan ataması kullanıcı talebiyle Codex'e ve gerçek dersID'ye bağlandı. İndirme/kurulum/ücretliAPI yok. Kullanıcının Ollama sunucusu kapatılmaz; yalnız labın yüklediği model ownership kuralıyla temizlenir. KendiUItestsunucusu test sonunda kapanır,ortak8798çalışır. İkinci masaüstü kabulü yapılmadı. Commit/push yok.

## Kaynaklar
OWASP LLM01:2025 https://genai.owasp.org/llmrisk/llm01-prompt-injection/ ; Ollama resmî API https://github.com/ollama/ollama/blob/main/docs/api.md . Bu kaynaklardan başarı oranı türetilmedi; bütün sayılar gerçek receipt'ten.
