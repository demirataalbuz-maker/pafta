# PU17 sentetik/test vektörleri

Bu klasör yalnız biçim ayrıştırma içindir. Gerçek kullanıcı verisi, parola kırma,
wordlist, GPU işi veya çevrimiçi sorgu içermez. Özet metni parola/plaintext değildir.

- NTLM: `password` için MD4(UTF-16LE) sonucu
  `8846f7eaee8fb117ad06bdd830b7586c`; MD4 ayrıca RFC 1320 vektörleriyle sınanır.
- bcrypt `$2a$05$CCCC...` ve `$2y$05$/OK...`: Openwall/John test vektörleri.
  Kaynak: https://github.com/openwall/john/issues/4388
- bcrypt `$2b$12$zQ4...`: yayımlanmış `p@5sw0rd` test vektörü.
- sha512crypt: OpenSSL 3.2.3 `passwd -6 -salt pu17testsalt` ile sentetik
  `PU17-test-vector` girdisinden üretildi.
- yescrypt: Baeldung'un `PASSWORD` / `SALT` örneği.
  Kaynak: https://www.baeldung.com/linux/shadow-passwords

`shadow.txt` içindeki kullanıcı adları ve politika günleri tamamen sentetiktir.
`pu17b` ve `pu17d`, salt tekrarını göstermek için aynı doğrulanabilir sha512crypt
test vektörünü taşır. Hiçbir fixture gerçek parola doğrulaması veya kırma amacıyla
kullanılmaz.

## Ag bicimleri ek ornekleri
`ag_bicimleri.json` elle yazilmis NetNTLMv2/Kerberos/LM bicim verileridir. Gercek kimlik bilgisi, gecerli oturum veya kriptografik test vektoru degildir. Ag yakalama ve parola kirma yapilmaz; yalniz profil ve kaynak baglami incelenir.
