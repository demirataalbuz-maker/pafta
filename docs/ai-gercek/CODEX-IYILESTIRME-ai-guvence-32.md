# ai-guvence-32 iyileştirme teslimi

Codex düzeltti; claude-opus denetimi bekleniyor. Puan verilmedi.

Değişenler: tracks/ai-guvence/lessons/ai-guvence-32-slopsquatting-savunmasi-paket-halusinasyonu.md, tracks/ai-guvence/fixtures/ai-guvence-32/{README.md,veri/paket_onerisi.txt,veri/denetim.json}, sandbox/ai_gercek_ai_guvence_32.py. engine/web davranışı değişmedi. İlk tablo+NOT, üç kusurlu starter ve hazirla/setup ile görünür ham öneri/JSON eklendi. Çalıştır ilk görevde ham dosyayı gösterir; diğer iki görev aynı denetim dosyasını okur. Kopya geçicidir; sonraki çalıştırmada yenilenir, kalıcılık iddia edilmez. Gizli testler ayrı girdilerdir. Dosyalar elle yazılmış sentetik örnek, canlı model kaydı değildir.

Anlatım paket kayıt sistemine dış sorgu yapılmadığını, yerel HTTP model bağlantısını, import/dağıtım adı farkını ve sınırlı çıkarıcının tam pip parser olmadığını açıklar. Allow-list dışı olmak zararlı veya var olmayan paket kanıtı değildir. Hiçbir paket kurulmaz.

Sınır testleri: tek popüler ad, bin popüler ad, üst sınır dışı girdiler, baştaki karakterin silinmesi, tam eşleşmenin dışlanması, alfabetik sonuç, rakam/noktalama/ekstra/bayrak ayrıştırma ve izin listesi boyutları. İlk mutasyonda 35 mutanttan 4'ü geçti: üçü tek-aday ve silme-maliyeti eksiği, biri boş olmayan paket girdilerinde ilk DP satırındaki fazladan kullanılmayan hücre nedeniyle eşdeğerdi. İlk kayıt mutasyon-ilk.log içinde korundu. Tek-aday/silme vakası eklendi; DP ilk satırı aynı önek maliyetlerini doğrudan enumerate indeksleri ve son uzunlukla kurar. Doğru çıktı değişmedi; mevcut testler zayıflatılmadı. Son tarama 1+24+9=34 mutant, 0 geçen.

Gerçek testte referans import takma ad/yıldız koruması ve ihlalde stop eklendi. Üç gerçek çağrının tamamı hatasız olmalı; önceden bir başarılı çağrı yetebiliyordu. Gerçek yanıttaki bütün paket/izin/incele listeleri referans hesapla karşılaştırılır. Kanıt hâlâ bütün kontrollerin all sonucu ile kabul edilir. Deneyin istemi/model ayarları değişmedi; modülde ham yanıt kesilmeden, istem/tohum/sıcaklık/token sınırı/süre ve gerçek kayıtlar kanıta eklendi. Run kanıtı kabul=false olarak kalır.

Dört kontrol .ai-venv/Scripts/python.exe -X utf8 ile:
- tools/validate.py ai-guvence-32: TEMİZ; 9 kontrol, 1 tahmin, 4 çözüm, 4 başlangıç. Gerçek Qwen3 4B Q4_K_M çağrıları dahil, PAFTA_DATA Desktop/pafta-g32-son-kontrol-20261030.
- docs/denetim/araclar/tahmin.py . ai-guvence-32: 1 tahmin, 0 şüpheli.
- kirp_gercek.py Desktop/pafta-mutasyon-g32-v2-20261030; kopyadaki mutasyon.py <kopya> --en-cok 1000 ai-guvence-32: 34 mutant, sıfır geçen.
- kopya_sonda.py ai-guvence ai-guvence-32 "from sandbox.ai_gercek_ai_guvence_32 import referans_denetle as paket_denetle": fail, korunuyor. kopya-sonucu.json hedeflenen guard mesajını ve kabul kanıtı yokluğunu doğrular.

Gerçek kabul kanıtı Desktop/pafta-g32-son-kontrol-20261030/ai-kanit/guvence-slopsquat-1793347981234.json: üç görev, 10 benzersiz öneri; 5'i allow-list içinde, 5'i incelemede (bilmiyorum, csv, jsonschema, python-dateutil, validators). Bu liste gerçek modelin bu koşuldaki önerisidir; kayıt sisteminden varlık/zararlılık doğrulaması değildir.

Üç görünür dosya Run kontrolü ok: outputs/iyilestirme-codex-ai-guvence-32/gorunur-dosya-run-{1,2,3}.json. Mevcut izole test sunucusu 18800 üzerinden normal token/Origin ile Kontrol pass (8 kontrol, gerçek kabul) ve Run ok (gerçek çağrı, kabul=false); http-check.json/http-run.json. Yeni sunucu başlatma port kullanımda olduğundan durdu; mevcut sunucunun kanıt veri yolu outputs/iyilestirme-codex-20261030/ui-data olarak doğrulandı. Mevcut sunucuya kapatma işlemi yapılmadı. Bu sunucu testi görsel UI kabulü değildir. CUA getState bu devamda da 'Local browser use is disabled in Work settings' bildirdi; dersin görsel ekran kabulü YAPILMADI ve denetçiye açık eksiktir.

Yeni indirme/kurulum, commit/push yok. Kullanıcının Ollama sunucusu veya başka süreci kapatılmadı.
