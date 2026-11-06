# ai-saldiri-28 — gerçek deney kabul raporu
Uygulayıcı kabulü; bağımsız denetim değildir. Yeni kurulum/commit/push yok.

İki gerçek yerel model rolü;sunucunun atadığı kaynak/hedef zarfı,exact devir politikası ve taşınan yetki zinciri gerçek rapor dosyasının erişimini belirler. Dört doğrudan sentetik devir gerçek diskte,izinli model yazması da gerçek dosyada sınandı. İlk testte worker çekimserliği yanlış biçimde hata sayılmıştı;ilk-validate-fail.json korundu. Tamamlanmış çekimserlik gerçek gözlemdir,sahte tool-call eklenmez;izinli normal yazma yine zorunlu. Kriptografik ağkimlikdoğrulaması veya hariciAIsohbetine mesaj iddiası yok.

Değişen:ders sonuna gerçek görev,sandbox/ai_gercek_ai_saldiri_28.py ve görünür web/data örneği.29ek TLSworker içerir. Eski adımlar korundu.

CLI kabul: 9/9;referansPASS,starter/boş/sabit/3anlamlımutantFAIL,RunOK/kabulfalse,eksikOllamaFAIL. persistence.json farklı süreç/cwdde öğrenci değişikliğini koruduğunu kanıtlar(fixturealtyapıkontrolü).

UI gerçek Kontrol ve Çalıştır kanıtları:
[
  {
    "dosya": "saldiri-28-devir-1793297807969.json",
    "kabul": true
  },
  {
    "dosya": "saldiri-28-devir-1793297829623.json",
    "kabul": false
  }
]

Gerçek referans kontrolleri:
{
  "gercek_mesaj_zarfi": true,
  "dogrudan_devir_ve_etki": true,
  "canli_devir_kararlari": true,
  "korumali_tasinmayan_yetki_yok": true,
  "model_tam": true,
  "izinli_model_yazdi": true,
  "kaynak_temiz": true,
  "cihaz_uygun": true
}

Gerçek referans gözlem özeti:
{}

Ham model/girdi/ayar/sürüm/digest/cihaz/bellek ve gerçek etkiler reference.json içindeki ai_kanit yolundadır. Saldırıbaşarısı geçme şartı değildir. Veri yalnız sentetik/yerel,kullanıcının diğer servisleri kapatılmaz. Markdownlinkler mevcutrendererda düzmetin;Run kalıcıdosya yolunu/içeriğini gösterir,dışeditör/Python ile düzenlenir. İkinci cihaz/bağımsızdenetim yok.
