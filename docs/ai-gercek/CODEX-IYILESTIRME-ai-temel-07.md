# ai-temel-07 iyileştirme teslimi

Codex'in kendi kontrolleridir; denetim ve puan claude-opus'a aittir. İş emrindeki dört madde tamamlandı: ilk araç/temsil/sınır tablosu ve NOT; görünür baglam.json+README; setup içinde ai_temel_veri.hazirla; aynı veriyi okuyan ilk üç starter/solution; yaklaşık 912 sözcük anlatım. Eski "model açılmaz" cümlesi ilk üç sentetik göreve daraltıldı, finaldeki gerçek modelle çelişki kaldırıldı.

Yeni veriler tracks/ai-temel/fixtures/ai-temel-07 içindedir. Etiketler, maliyetler ve pozisyonlar elle hazırlanmıştır; gerçek tokenizer/server kaydı değildir. İlk Çalıştır ham JSON'u gösterir. Sonraki iki görev aynı dosyadan konum ve mesajları okur. Her Run/Check geçici veri/ kopyası oluşturur, kalıcılık yoktur. Kaynak haricî editörde veya yüklenen sözlük kod içinde değiştirilebilir; gizli testler ayrıdır. İlk starter en eski tokenları, ikinci çift sinüs, üçüncü aradaki sığmayan mesajı atlayıp daha eski mesajı seçer. Üçü Run çalışır, Check reddeder.

Anlatım token/kelime farkını, sıra ve kopya gereğini, bool/int tuzağını, bütçede kesintisiz son parça politikasını, sinüs/kosinüs ile gerçek model konum mekanizması ayrımını, system mesajının kalmasının güvenlik garantisi olmadığını, logit/olasılık farkını ve kısa bütçenin model kapasitesini temsil etmediğini açıklar. İlk sekiz logit sözlükteki ilk sekiz indekstir; top-8 aday değildir. Yeni testler girdinin değişmemesini ve aralık atlama hatasını ayrıca sınar; eski doğru kontroller çıkarılmadı.

Mevcut gerçek deney korunup güçlendirildi. Yeni sandbox/ai_gercek_ai_temel_07.py gerçek referans ve Run gösterimini içerir. Test kendi bağımsız yerel hesabıyla karşılaştırır. Kopya guard referans/getattr/kanit_yaz ve AST takma ad/yıldız importlarını modelden önce stop ile reddeder. Hook gerçek forward'a verilen token, position_ids, use_cache=False ve no_grad durumunu denetler. Tam 32 tokenın korunacağı 40 tokenlık metin eklenmiştir. Run gerçek çağrı izlerini ve ham raporları kabulfalse ile kaydeder. Kontrol kabul=all(sonuclar) kullanır; model yokluğu PASS değildir. Yeni kurulum/indirme yok.

Zorunlu kontroller (.ai-venv/Scripts/python.exe -X utf8):

- tools/validate.py ai-temel-07, PAFTA_DATA=Desktop/pafta-t07-kabul-20261031: TEMİZ 9; tahmin1,solution4,starter4.
- docs/denetim/araclar/tahmin.py . ai-temel-07: 1 tahmin,0 şüpheli.
- kirp_gercek.py Desktop/pafta-mutasyon-t07-20261031: hedef yokluğu önce doğrulandı; mevcut klasör silinmedi. Kopyadaki mutasyon.py <kopya> --en-cok 1000 ai-temel-07:13+7+24=44 mutant,0 geçen. Gerçek deney bu ayrı mutasyon kopyasından çıkarılmıştır; gerçek model validate/UI ile sınanır.
- kopya_sonda.py ai-temel ai-temel-07 "from sandbox.ai_gercek_ai_temel_07 import referans as gercek_baglam_raporu": fail/korunuyor. Ayrı kopya.json hedef guard reddini doğrular.

Ek sonuçlar outputs/iyilestirme-codex-ai-temel-07 altındadır: bos,sabit,grad-acik,ilk-konum,kopya,eksik-model JSON sonuçları kabul üretmez; ilk üç gorunur-dosya-run JSON sonucu ok. Eksik model yalnız çocuk ortamında olmayan model/revizyon ile local_files_only üzerinden sınandı; indirme yoktur.

Gerçek CLI kanıtı: C:\Users\demo12\Desktop\pafta-t07-kabul-20261031\ai-kanit\temel-07-baglam-1793465992360.json. Model HuggingFaceTB/SmolLM2-135M@93efa2f097d58c2a74874c7e644dbc9b0cee75a2; CPU; config sınırı 8192; beş gerçek girdi; korunan uzunluklar [1, 4, 8, 13, 32], düşen sayılar [11, 8, 8, 0, 8]. Ham metin/kimlik/konum/sonraki aday ve sekiz örnek logit, sürümler, ağırlık SHA256 ve cihaz ortak kanıtta. Tüm sözlük logitleri arşivlenmez; gerçek ileri hesapta hesaplanır ve istenen sekiz örnek saklanır. Bu öğretim deneyi uzun bağlam veya saldırı başarısı kabulü değildir.

Değişen dosyalar: tracks\ai-temel\lessons\ai-temel-07-context-window-ve-konumsal-temsil.md; sandbox/ai_gercek_ai_temel_07.py; tracks/ai-temel/fixtures/ai-temel-07/README.md ve baglam.json; bu rapor ve kuyruk/pano/devir/özet kayıtları. Engine/web, puan dosyaları değişmedi; commit/push yok. Temel16 varsayılan kullanıcı Ollama500 sorunu ve önceki raporların görsel açıkları bu CPU dersiyle kapanmaz.

Gerçek ders ekranı kabulü: girişte tablo/NOT görüldü. İlk üç görev Çalıştır ile aynı JSON'dan çalıştı: ham dosya ve eski pencere, çift sinüs, aralık tuzağında yanlış old,new seçimi ekranda görüldü. Final starter iki kez 8/11 ile reddedildi; kabulfalse. Örnek çözüm Tezgaha alındı ve ders ekranında 11/11 onaylandı: outputs/iyilestirme-codex-20261030/ui-data/ai-kanit/temel-07-baglam-1793466166623.json. Çalıştır gerçek model çıktısını kabulfalse kaydetti: temel-07-baglam-calistir-1793466195404.json; bütçe2/8, düşen10/4, gerçek forward izleri kanıtta. Röntgen/Bytecode gerçek adımda gizli, normal sentetik görevlerde görünür. Ekran görüntüsü dosyası değil, gerçek UI DOM sonuçları gözlendi.

Kendi izole 18800 test sunucusu sonraki dersin kabulü için açık tutuluyor; kullanıcı Ollama/WSL/Docker süreçlerine dokunulmadı. Bu CPU dersinde Ollama başlatılmadı. İşin sonunda yalnız kendi sunucusu kapatılacaktır.

SonrakiTemel11kabulünden sonra aynı kendi18800sunucusu kapatıldı;port dinlemiyor.
