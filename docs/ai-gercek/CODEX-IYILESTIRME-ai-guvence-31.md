# ai-guvence-31 iyileştirme teslimi

Codex düzeltti; claude-opus denetimi bekleniyor. Puan verilmedi.

Ders markdown ve tracks/ai-guvence/fixtures/ai-guvence-31/{README.md,veri/gommeler.json} değişti. İlk anlatım başına gerçek model/sentetik örnek/kapsam tablosu ve NOT eklendi. Aday havuzundan geri bulma, vec2text ile bilinmeyen serbest metin üretiminden ayrıldı. Üç görev aynı görünür sentetik JSON dosyasını mevcut hazirla/setup ile okur; geçici çalışma kopyasının sonraki çalıştırmada sıfırlandığı açıkça yazılır. Üç gerçekçi kusurlu starter normalize etmeme, bütün tahminleri sayma ve örneği kendi merkezine katma hatalarını taşır. Starterların tamamı reddedilir.

Testler üst boyut/adet sınırları, bozuk vektörler, normalizasyon sıralaması, etiket eşitliği ve dört basamak yuvarlamayla güçlendirildi. Mevcut testler korunur. Merkez sınıflandırmada sözleşmenin izin verdiği karma int/string etiketler artık deterministik sırayla (sayılar sonra stringler) işlenir; anlatımda sıra açıklandı. Gerçek deney modülü değiştirilmedi. Gerçek testin kopya korumasına bütün referans adları/kanit_yaz ve ImportFrom takma ad/yıldız denetimi eklendi; ihlalde stop(). Kabul hâlâ mevcut bütün kontrollerin sonucuna bağlıdır. engine/web davranışı değişmedi.

Dört zorunlu kontrol .ai-venv/Scripts/python.exe -X utf8 ile:
- tools/validate.py ai-guvence-31: TEMİZ, 9 kontrol (1 tahmin, 4 çözüm, 4 başlangıç); gerçek yerel all-minilm:22m gömmeleri dahil. PAFTA_DATA Desktop/pafta-g31-son-kontrol-20261030.
- docs/denetim/araclar/tahmin.py . ai-guvence-31: 1 tahmin, 0 şüpheli.
- kirp_gercek.py Desktop/pafta-mutasyon-g31-v2-20261030 ve kopyadaki mutasyon.py <kopya> --en-cok 1000 ai-guvence-31: 20+21+28=69 mutant, 0 geçen. İlk taramadaki 1 geçen mutant mutasyon-ilk.log dosyasında korunur; bin örneği dışlayan <=/< değişimine karşı geçerli bin örnek testi eklendi ve yeniden tarandı.
- kopya_sonda.py ai-guvence ai-guvence-31 "from sandbox.ai_gercek_ai_guvence_31 import referans_inversion as inversion_raporu": fail, korunuyor. kopya-sonucu.json hedeflenen Kendi inversion guard mesajını ve gerçek kabul kanıtının yokluğunu doğrular.

Gerçek Kontrol kanıtı: Desktop/pafta-g31-son-kontrol-20261030/ai-kanit/guvence-inversion-1793344902389.json. Sekiz kurgusal kayıtta 384 boyut, recovery@1=0.625, recovery@3=0.75, bırak-biri-dışarıda nitelik doğruluğu=1.0. Bunlar bu küçük örneklemin sonuçlarıdır, genel başarı iddiası değildir.

Görünür dosyalar normal runner/setup/Run yolunda üç starter için hatasız okundu; gorunur-dosya-run-1/2/3.json kayıtları vardır. Son gerçek deneyin Run yolu ok, gerçek model çağrısı ve kabul=false (yalnız deneme); gercek-deney-run.json. CLI/runner kontrolü görsel ders ekranı kabulü yerine sayılmadı: Work tarayıcı kontrolü önceki devamda kapalı bildirildiği için bu dersin görsel kabulü YAPILMADI, denetçiye açık eksiktir. Yeni indirme/kurulum, commit/push yok. Yalnız mevcut yerel modeller kullanıldı.
